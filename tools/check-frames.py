#!/usr/bin/env python3
"""
check-frames.py — automated pre-review for captured frames.

Why this exists: the capture tool produces screenshots but never answers "is
this frame correct?". This script measures what is measurable in every frame and
leaves taste and composition to a human. It measures:

  • size and frame integrity (blank or flat frame = FAIL)
  • ink (text) coverage, and accent-colour coverage when configured
  • whether text is present inside the windows where it is required
  • content touching the frame edge (clipped glyphs)
  • safe-area violations (default 8% margin)
  • dominant colours, to check the palette really comes from the tokens

Themes:
  --theme light   dark ink on a light ground (default)
  --theme dark    light ink on a dark ground

Accent detection is OFF unless you pass --accent-hue. This keeps the tool
brand-neutral: the accent colour is a property of the project's tokens, not of
this script.

Usage:
  python3 tools/check-frames.py shots/*.png
  python3 tools/check-frames.py shots/*.png --theme light --text-windows 0-12,23-30,57-60
  python3 tools/check-frames.py shots/*.png --accent-hue 348
  python3 tools/check-frames.py shots/*.png --json
"""
from __future__ import annotations
import argparse, colorsys, glob, json, math, os, re, sys
from PIL import Image

W, H = 1920, 1080
SAFE_X, SAFE_Y = 0.08, 0.08          # safe area: 8% margin
EDGE_PX = 5                          # band counted as "touching the edge"

# Per-theme ink thresholds. Tune these to the project's tokens: "ink" is
# whatever the design uses for text, "ground" is the background.
THEMES = {
    "light": {"ink_max_lum": 120, "ink_max_sat": 1.01},
    "dark":  {"ink_min_lum": 195, "ink_max_sat": 0.22},
}


def lum(r, g, b):
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def accent_ranges(hue_deg, tol_deg):
    """Hue ranges (0..1) for the accent colour, wrapping around the circle."""
    if hue_deg is None:
        return None
    h = (hue_deg % 360) / 360.0
    t = tol_deg / 360.0
    lo, hi = h - t, h + t
    if lo < 0:
        return ((0.0, hi), (lo + 1.0, 1.0))
    if hi > 1:
        return ((lo, 1.0), (0.0, hi - 1.0))
    return ((lo, hi),)


def classify(px, theme, acc_ranges, acc_sat, acc_lum):
    """Classify one pixel (0-255 RGB) into the measurement classes."""
    r, g, b = px
    L = lum(r, g, b)
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    t = THEMES[theme]
    if theme == "light":
        ink = L < t["ink_max_lum"]
    else:
        ink = L > t["ink_min_lum"] and s < t["ink_max_sat"]
    accent = bool(acc_ranges) and any(lo <= h < hi for lo, hi in acc_ranges) \
        and s > acc_sat and L > acc_lum
    return L, ink, accent


def analyse(path, theme, acc_ranges, acc_sat, acc_lum):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    px = im.load()
    n = w * h
    sx, sy = int(w * SAFE_X), int(h * SAFE_Y)
    inks = accents = edge = safe_viol = 0
    dark = bright = 0
    lsum = lsum2 = 0.0
    hist = {}
    step = 2                                        # sample on a 2px grid (speed)
    bx0, by0, bx1, by1 = w, h, -1, -1              # content (ink+accent) bbox
    for y in range(0, h, step):
        for x in range(0, w, step):
            L, is_ink, is_accent = classify(px[x, y], theme, acc_ranges, acc_sat, acc_lum)
            lsum += L; lsum2 += L * L
            if L < 12: dark += 1
            if L > 240: bright += 1
            if is_ink: inks += 1
            if is_accent: accents += 1
            if (is_ink or is_accent):
                if x < bx0: bx0 = x
                if y < by0: by0 = y
                if x > bx1: bx1 = x
                if y > by1: by1 = y
                if x < EDGE_PX or y < EDGE_PX or x >= w - EDGE_PX or y >= h - EDGE_PX:
                    edge += 1
                if x < sx or y < sy or x >= w - sx or y >= h - sy:
                    safe_viol += 1
            if (x % 32 == 0) and (y % 32 == 0):     # coarse histogram for dominant colours
                key = (px[x, y][0] // 16 * 16, px[x, y][1] // 16 * 16, px[x, y][2] // 16 * 16)
                hist[key] = hist.get(key, 0) + 1
    m = max(1, (w // step) * (h // step))
    mean = lsum / m
    var = max(0.0, lsum2 / m - mean * mean)
    dom = sorted(hist.items(), key=lambda kv: -kv[1])[:5]
    return {
        "file": os.path.basename(path), "w": w, "h": h,
        "mean_lum": round(mean, 2), "stdev": round(math.sqrt(var), 2),
        "ink_pct": round(inks / m * 100, 4),
        "accent_pct": round(accents / m * 100, 4),
        "edge_px": edge, "safe_viol_px": safe_viol,
        "bbox": [bx0, by0, bx1, by1] if bx1 >= 0 else None,
        "dark_pct": round(dark / m * 100, 2), "bright_pct": round(bright / m * 100, 3),
        "dominant": ["#%02X%02X%02X" % k for k, _ in dom],
    }


def t_of(name):
    """Recover the capture time from a shots.mjs filename (t12_50 -> 12.50)."""
    m = re.search(r"t(\d+)_(\d+)", name)
    return float(f"{m.group(1)}.{m.group(2)}") if m else None


def parse_windows(s):
    out = []
    for part in (s or "").split(","):
        part = part.strip()
        if not part:
            continue
        a, b = part.split("-")
        out.append((float(a), float(b)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("frames", nargs="+")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--theme", choices=("light", "dark"), default="light",
                    help="light = light ground with dark ink, dark = dark ground with light ink")
    ap.add_argument("--text-windows", default="",
                    help="time windows (seconds) where text is REQUIRED, e.g. 0-12,23-30. "
                         "Empty means no window is enforced.")
    ap.add_argument("--allow-edge-before", type=float, default=1.6,
                    help="before this second, edge bleed is treated as intentional (opening)")
    ap.add_argument("--grace", type=float, default=0.25,
                    help="frames this close to a window boundary get a relaxed text threshold")
    ap.add_argument("--min-ink", type=float, default=0.05,
                    help="minimum ink percentage required inside a text window")
    ap.add_argument("--safe-viol-max", type=int, default=200,
                    help="warning threshold for safe-area violations (sampled pixels)")
    ap.add_argument("--bleed", action="store_true",
                    help="full-bleed footage scenes: skip edge and safe-area checks")
    ap.add_argument("--text-everywhere", action="store_true",
                    help="captions are on for the whole film: silence the out-of-window text warning")
    ap.add_argument("--accent-hue", type=float, default=None,
                    help="accent hue in degrees (0-360); enables accent detection when set")
    ap.add_argument("--accent-hue-tol", type=float, default=20.0,
                    help="hue tolerance in degrees around --accent-hue")
    ap.add_argument("--accent-sat", type=float, default=0.50,
                    help="minimum saturation for a pixel to count as accent")
    ap.add_argument("--accent-lum", type=float, default=70,
                    help="minimum luminance for a pixel to count as accent")
    a = ap.parse_args()

    files = []
    for f in a.frames:
        files.extend(sorted(glob.glob(f)) if any(c in f for c in "*?[") else [f])
    windows = parse_windows(a.text_windows)
    acc_ranges = accent_ranges(a.accent_hue, a.accent_hue_tol)

    rows, fails = [], 0
    for f in files:
        r = analyse(f, a.theme, acc_ranges, a.accent_sat, a.accent_lum)
        t = t_of(r["file"])
        notes = []
        if (r["w"], r["h"]) != (W, H):
            notes.append(f"FAIL size {r['w']}x{r['h']} (expected {W}x{H})")
        if r["stdev"] < 3:
            notes.append("FAIL frame blank or flat (stdev<3)")
        if a.theme == "dark" and r["mean_lum"] < 4:
            notes.append("FAIL frame is fully black")
        if a.theme == "light" and r["mean_lum"] > 250 and r["stdev"] < 6:
            notes.append("FAIL frame is fully white")
        if t is not None:
            in_text = any(x <= t <= y for x, y in windows)
            # Grace period: frames near a beat boundary are mid-transition, so
            # text is not expected to be fully present yet.
            near_edge = any(abs(t - x) <= a.grace or abs(t - y) <= a.grace for x, y in windows)
            if in_text and r["ink_pct"] < a.min_ink and not near_edge:
                notes.append(f"FAIL no ink inside text window (ink={r['ink_pct']}%)")
            elif in_text and r["ink_pct"] < a.min_ink:
                notes.append(f"OK grace period (ink={r['ink_pct']}%)")
            if (not in_text) and r["ink_pct"] > 0 and not a.text_everywhere:
                notes.append(
                    f"WARN text outside its window (ink={r['ink_pct']}%) — caption or overlay?")
            if r["edge_px"] > 0 and t >= a.allow_edge_before and not a.bleed:
                notes.append(f"FAIL content touches the edge ({r['edge_px']} sampled px) — clipped glyph")
            if r["edge_px"] > 0 and t < a.allow_edge_before and not a.bleed:
                notes.append(f"OK intentional opening bleed ({r['edge_px']} px)")
            if r["safe_viol_px"] > a.safe_viol_max and not a.bleed:
                notes.append(f"WARN safe-area violation ({r['safe_viol_px']} px) bbox={r['bbox']}")
        if "FAIL" in " ".join(notes):
            fails += 1
        r["notes"] = notes
        rows.append(r)

    if a.json:
        print(json.dumps({"frames": rows, "fails": fails, "theme": a.theme}, indent=2, ensure_ascii=False))
    else:
        print(f"theme: {a.theme}")
        print(f"{'frame':<14}{'mean L':>8}{'stdev':>8}{'ink%':>9}{'accent%':>9}{'edge':>7}{'safe':>7}  notes")
        for r in rows:
            print(f"{r['file']:<14}{r['mean_lum']:>8.1f}{r['stdev']:>8.1f}"
                  f"{r['ink_pct']:>9.3f}{r['accent_pct']:>9.3f}{r['edge_px']:>7}{r['safe_viol_px']:>7}  "
                  + ("; ".join(r["notes"]) if r["notes"] else "-"))
        print(f"\n{len(rows)} frames · {fails} FAIL")
        if rows:
            print("dominant colours (first frame):", ", ".join(rows[0]["dominant"]))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
