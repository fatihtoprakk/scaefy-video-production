#!/usr/bin/env python3
"""Pre-delivery quality control (QC).

Parses ffmpeg's own output; ffprobe is NOT required (all measurement parses
`ffmpeg -i` output and ffmpeg is resolved through tools/ffmpeg.sh).

Usage:
    qc.py <file> [--spec landscape-1080|landscape-4k|vertical-1080|square-1080|any]
                 [--expect-duration 60] [--fps 25] [--resolution 1920x1080]
                 [--json] [--full-scan]

Checks: duration, resolution, pixel format, video codec and H.264 profile, frame
rate (constant), pixel aspect ratio, audio codec, sample rate, channels,
integrated loudness, true peak, black opening/ending, frozen frames, and the
presence of a subtitle stream.

Exit code: 1 if there is at least one FAIL, otherwise 0. Warnings do not change the exit code.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

PASS, WARN, FAIL = "PASS", "WARN", "FAIL"
ICON = {PASS: "✓", WARN: "!", FAIL: "✗"}

SPECS = {
    # spec: (duration, fps, resolution, pix_fmt, audio Hz, channels, h264 profile)
    "landscape-1080": (60.0, 25.0, "1920x1080", "yuv420p", 48000, "stereo", "High"),
    "landscape-4k": (60.0, 25.0, "3840x2160", "yuv420p", 48000, "stereo", "High"),
    "vertical-1080": (None, 25.0, "1080x1920", "yuv420p", 48000, "stereo", "High"),
    "square-1080": (None, 25.0, "1080x1080", "yuv420p", 48000, "stereo", "High"),
    "any": (None, None, None, None, None, None, None),
}

LOUDNESS_I_TARGET = -14.0
LOUDNESS_I_TOLERANCE = 1.0
LOUDNESS_TP_MAX = -1.0


def find_root(start: Path) -> Path:
    for d in [start, *start.parents]:
        if (d / "tools" / "ffmpeg.sh").is_file():
            return d
    sys.exit("ERROR: project root not found (tools/ffmpeg.sh missing)")


def resolve_ffmpeg(root: Path) -> str:
    out = subprocess.run([str(root / "tools" / "ffmpeg.sh")], capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(out.stderr.strip() or "ERROR: ffmpeg not found")
    return out.stdout.strip()


def ffmpeg_run(ff: str, args: list[str]) -> str:
    p = subprocess.run([ff, "-hide_banner", "-nostdin", *args], capture_output=True, text=True)
    return (p.stderr or "") + (p.stdout or "")


def hms_to_seconds(h: str, m: str, s: str) -> float:
    return int(h) * 3600 + int(m) * 60 + float(s)


def probe(ff: str, path: Path) -> dict:
    out = ffmpeg_run(ff, ["-i", str(path)])
    info: dict = {"raw": out}

    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", out)
    info["duration"] = hms_to_seconds(*m.groups()) if m else None

    vline = next((l for l in out.splitlines() if "Stream #" in l and "Video:" in l), "")
    aline = next((l for l in out.splitlines() if "Stream #" in l and "Audio:" in l), "")
    sline = next((l for l in out.splitlines() if "Stream #" in l and "Subtitle:" in l), "")

    if vline:
        info["v_codec"] = (re.search(r"Video: (\w+)", vline) or [None, None])[1]
        dim = re.search(r"(\d{2,5})x(\d{2,5})", vline)
        info["resolution"] = f"{dim.group(1)}x{dim.group(2)}" if dim else None
        info["pix_fmt"] = (re.search(r",\s*(yuv\w+|rgb\w+|gbr\w+|gray\w*)", vline) or [None, None])[1]
        info["fps"] = float(m.group(1)) if (m := re.search(r"([\d.]+) fps", vline)) else None
        info["tbr"] = float(m.group(1)) if (m := re.search(r"([\d.]+) tbr", vline)) else None
        info["sar"] = (re.search(r"\[SAR (\d+:\d+)", vline) or [None, None])[1]
        # ffmpeg prints the profile in parentheses: "Video: h264 (High) (avc1 ...)".
        info["v_profile"] = (re.search(r"Video: \w+ \(([^)]+)\)", vline) or [None, None])[1]
        info["v_bitrate_kbps"] = int(m.group(1)) if (m := re.search(r"(\d+) kb/s", vline)) else None
    if aline:
        info["a_codec"] = (re.search(r"Audio: (\w+)", aline) or [None, None])[1]
        info["sample_rate"] = int(m.group(1)) if (m := re.search(r"(\d+) Hz", aline)) else None
        info["channels"] = (re.search(r"Hz,\s*([a-z0-9.()]+)", aline) or [None, None])[1]
        info["a_bitrate_kbps"] = int(m.group(1)) if (m := re.search(r"(\d+) kb/s", aline)) else None
    info["has_subtitles"] = bool(sline)
    info["has_audio"] = bool(aline)
    return info


def measure_loudness(ff: str, path: Path) -> dict:
    out = ffmpeg_run(ff, ["-i", str(path), "-map", "0:a:0?", "-af", "ebur128=peak=true", "-f", "null", "-"])
    summary = out.split("Integrated loudness:")[-1] if "Integrated loudness:" in out else ""

    def pick(label: str):
        m = re.search(rf"^\s+{label}:\s+(-?[\d.]+)", summary, re.M)
        return float(m.group(1)) if m else None

    return {"integrated": pick("I"), "lra": pick("LRA"), "true_peak": pick("Peak")}


def scan_edges(ff: str, path: Path, duration: float | None, full: bool) -> dict:
    """Look for black frames, frozen frames and silence in the first/last 5 s.

    If full=True the whole file is scanned (slower, but catches freeze/blackout defects).
    """
    result = {"black": [], "freeze": [], "silence": []}
    windows = (
        [("full", [])]
        if full
        else [("head", ["-t", "5"]), ("tail", ["-sseof", "-5"])]
    )

    for name, seek in windows:
        # Black frames + freeze (video)
        out = ffmpeg_run(
            ff,
            [*seek, "-i", str(path), "-vf", "blackdetect=d=0.04:pix_th=0.10,freezedetect=n=-60dB:d=1.5",
             "-an", "-f", "null", "-"],
        )
        for m in re.finditer(r"black_start:([\d.]+) black_end:([\d.]+)", out):
            result["black"].append((name, float(m.group(1)), float(m.group(2))))
        for m in re.finditer(r"freeze_start: ([\d.]+)", out):
            result["freeze"].append((name, float(m.group(1))))

        # Silence (audio)
        out = ffmpeg_run(
            ff,
            [*seek, "-i", str(path), "-vn", "-af", "silencedetect=n=-50dB:d=0.5", "-f", "null", "-"],
        )
        for m in re.finditer(r"silence_start: (-?[\d.]+)", out):
            result["silence"].append((name, float(m.group(1))))

    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="Pre-delivery QC")
    ap.add_argument("file", type=Path)
    ap.add_argument("--spec", choices=sorted(SPECS), default="landscape-1080")
    ap.add_argument("--expect-duration", type=float, default=None)
    ap.add_argument("--fps", type=float, default=None)
    ap.add_argument("--resolution", default=None)
    ap.add_argument("--loudness", type=float, default=LOUDNESS_I_TARGET)
    ap.add_argument("--tp", type=float, default=LOUDNESS_TP_MAX)
    ap.add_argument("--full-scan", action="store_true", help="scan the whole file for freezes/blackouts")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if not args.file.is_file():
        sys.exit(f"ERROR: file not found: {args.file}")

    root = find_root(Path(__file__).resolve().parent)
    ff = resolve_ffmpeg(root)

    spec_dur, spec_fps, spec_res, spec_pix, spec_hz, spec_ch, spec_profile = SPECS[args.spec]
    exp_dur = args.expect_duration if args.expect_duration is not None else spec_dur
    exp_fps = args.fps if args.fps is not None else spec_fps
    exp_res = args.resolution or spec_res

    info = probe(ff, args.file)
    checks: list[tuple[str, str, str]] = []

    def add(name: str, status: str, detail: str) -> None:
        checks.append((name, status, detail))

    # --- Container / video ---
    dur = info.get("duration")
    if exp_dur is not None:
        if dur is None:
            add("Duration", FAIL, "unreadable")
        elif abs(dur - exp_dur) > 0.10:
            add("Duration", FAIL, f"{dur:.2f} s (expected {exp_dur:.2f} ±0.10)")
        else:
            add("Duration", PASS, f"{dur:.2f} s")
    else:
        add("Duration", PASS, f"{dur:.2f} s" if dur else "unknown (spec: any)")

    if exp_res:
        add("Resolution", PASS if info.get("resolution") == exp_res else FAIL,
            f"{info.get('resolution')} (expected {exp_res})")
    if spec_pix:
        add("Pixel format", PASS if info.get("pix_fmt") == spec_pix else FAIL,
            f"{info.get('pix_fmt')} (expected {spec_pix})")
    add("Video codec", PASS if info.get("v_codec") == "h264" else WARN,
        f"{info.get('v_codec')} ({info.get('v_bitrate_kbps')} kb/s)")
    # The delivery matrix documents H.264 High profile, and encode-master.sh sets
    # it. A gate that does not measure a documented requirement is not a gate, so
    # this is a FAIL rather than a warning.
    if spec_profile:
        actual = info.get("v_profile")
        add("H.264 profile", PASS if (actual or "").lower() == spec_profile.lower() else FAIL,
            f"{actual or 'unknown'} (expected {spec_profile})")

    if exp_fps:
        fps, tbr = info.get("fps"), info.get("tbr")
        if fps is None:
            add("Frame rate", FAIL, "unreadable")
        elif abs(fps - exp_fps) > 0.01:
            add("Frame rate", FAIL, f"{fps} fps (expected {exp_fps})")
        elif tbr is not None and abs(fps - tbr) > 0.01:
            add("Frame rate", FAIL, f"variable frame rate (fps={fps}, tbr={tbr})")
        else:
            add("Frame rate", PASS, f"{fps} fps constant")

    sar = info.get("sar")
    if sar and sar != "1:1":
        add("Pixel aspect", WARN, f"SAR {sar} (not square pixels)")
    elif sar:
        add("Pixel aspect", PASS, "SAR 1:1")

    # --- Audio ---
    if not info.get("has_audio"):
        add("Audio stream", FAIL, "no audio stream")
    else:
        add("Audio codec", PASS if info.get("a_codec") == "aac" else WARN,
            f"{info.get('a_codec')} {info.get('a_bitrate_kbps')} kb/s")
        if spec_hz and info.get("sample_rate") != spec_hz:
            add("Sample rate", FAIL, f"{info.get('sample_rate')} Hz (expected {spec_hz})")
        else:
            add("Sample rate", PASS, f"{info.get('sample_rate')} Hz")
        if spec_ch and info.get("channels") != spec_ch:
            add("Channels", WARN, f"{info.get('channels')} (expected {spec_ch})")

        loud = measure_loudness(ff, args.file)
        i, tp = loud.get("integrated"), loud.get("true_peak")
        if i is None:
            add("Loudness", FAIL, "could not be measured")
        else:
            drift = abs(i - args.loudness)
            add(
                "Loudness",
                PASS if drift <= LOUDNESS_I_TOLERANCE else FAIL,
                f"{i:+.1f} LUFS (target {args.loudness:+.1f} ±{LOUDNESS_I_TOLERANCE})",
            )
        if tp is not None:
            add("True peak", PASS if tp <= args.tp else FAIL, f"{tp:+.2f} dBTP (limit {args.tp:+.1f})")

    # --- Edge scan ---
    edges = scan_edges(ff, args.file, dur, args.full_scan)
    head_black = [b for b in edges["black"] if b[0] in ("head", "full") and b[1] <= 0.10]
    tail_black = [b for b in edges["black"] if b[0] in ("tail", "full") and dur and b[2] >= dur - 0.10]
    if head_black:
        add("First frame", FAIL, f"video starts black ({head_black[0][1]:.2f}s)")
    else:
        add("First frame", PASS, "no black/broken opening")
    if tail_black:
        add("Last frame", FAIL, f"video ends black ({tail_black[0][2]:.2f}s)")
    else:
        add("Last frame", PASS, "no black/broken ending")

    freezes = edges["freeze"]
    add("Frozen frame", WARN if freezes else PASS,
        f"{len(freezes)} freeze(s) detected (first: {freezes[0][1]:.1f}s)" if freezes else "none")

    head_sil = [s for s in edges["silence"] if s[1] <= 0.05]
    if head_sil:
        add("Opening audio", WARN, "first 0.5 s are silent")

    # --- Subtitles ---
    add("Subtitle stream", PASS if info.get("has_subtitles") else WARN,
        "present" if info.get("has_subtitles") else "none (embedded subtitles are recommended for silent playback)")

    fails = [c for c in checks if c[1] == FAIL]
    warns = [c for c in checks if c[1] == WARN]

    if args.json:
        print(json.dumps({
            "file": str(args.file), "spec": args.spec, "info": info,
            "checks": [{"name": n, "status": s, "detail": d} for n, s, d in checks],
            "fail": len(fails), "warn": len(warns),
        }, ensure_ascii=False, indent=2))
    else:
        print(f"QC — {args.file.name}  (spec: {args.spec})")
        print("-" * 68)
        for name, status, detail in checks:
            print(f" {ICON[status]} {name:<18} {detail}")
        print("-" * 68)
        print(f"Result: {len(fails)} FAIL · {len(warns)} warnings · {len(checks) - len(fails) - len(warns)} passed")
        if fails:
            print("MUST NOT SHIP: resolve the FAIL items above first.")

    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
