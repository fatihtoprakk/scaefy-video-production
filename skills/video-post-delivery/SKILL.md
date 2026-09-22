---
name: video-post-delivery
description: Encodes, normalises, subtitles and QCs finished masters to delivery specs — -14 LUFS integrated, -1 dBTP, H.264 yuv420p CFR, burned-in subtitles, 60/30/15-second 16:9 and 9:16 cuts. Use when a film must go to an event screen or social platform; when loudness or true-peak compliance is required; when deriving short or vertical cuts from a master; or when a pre-delivery quality gate is needed.
---

# Delivery, Encode and QC

Prepares a master for event screens and social platforms in a **repeatable** way.
Every check here looks at a measurable threshold rather than "it looks fine".

## Why there is no ffprobe

This repository resolves a working `ffmpeg` through `tools/ffmpeg.sh`, with a static
build shipped at `tools/bin/ffmpeg`. The resolver tests **execution, not existence**:
a candidate is skipped unless `ffmpeg -version` actually runs. All measurement and
scanning parses `ffmpeg -i` output, so `ffprobe` is not required.

```bash
FF="$(tools/ffmpeg.sh)"     # full path to a working ffmpeg
```

## Delivery matrix

Durations and frame sizes are parameters of the delivery matrix; the concrete values
below are the worked example for a 60-second brand film. Substitute whatever the
brief supplies.

| Output | Duration | Frame | Codec / settings |
|---|---|---|---|
| Main film | 60 s | 1920×1080 (or 3840×2160) | H.264 High, yuv420p, 25 fps CFR, 20–35 Mbps (1080p) / 45–70 Mbps (4K) |
| Event backup | 60 s | same | H.264 yuv420p + AAC, constant frame rate (second delivery for player compatibility) |
| Silent playback | 60 s | same | Main master + burned-in subtitles |
| Short cut | 30 s | 16:9 | Derived from the main master |
| Teaser | 15 s | 9:16 | Blurred background + centred image (or a vertical composition) |
| Full vertical | 60 s | 1080×1920 | Graphic modules are composed separately for vertical |

Colour space: Rec.709 / Gamma 2.4. Audio: AAC 48 kHz, 320 kbps stereo.
Loudness: **-14 LUFS integrated**, true peak **≤ -1 dBTP**.
Narration target: approximately **-16 LUFS short-term**; music is ducked 8–12 dB under narration.

## Scripts

| Script | Purpose |
|---|---|
| `scripts/loudness.sh <file> [--check]` | EBU R128 measurement; `--check` exits with code 1 when outside target |
| `scripts/normalize-loudness.sh <input> <output>` | Two-pass `loudnorm` (video is copied, audio is re-encoded) |
| `scripts/encode-master.sh <input> <output> [--height 1080\|2160]` | H.264 master with delivery settings |
| `scripts/derive-versions.sh <master> <dir> [--durations 60,30,15] [--vertical]` | Version derivation (faded cut + vertical) |
| `scripts/qc.py <file> [--spec landscape-1080\|landscape-4k\|vertical-1080\|square-1080\|any] [--expect-duration N]` | Pre-delivery gate: duration, resolution, pix_fmt, CFR, codec, audio, loudness, TP, black/frozen frames, subtitles |

Typical flow:

```bash
POST=skills/video-post-delivery/scripts
"$POST/normalize-loudness.sh" out/edit-master.mp4 out/mixed.mp4
"$POST/encode-master.sh" out/mixed.mp4 out/master-60s-1080p.mp4 --height 1080
"$POST/derive-versions.sh" out/master-60s-1080p.mp4 out/delivery --durations 60,30,15 --vertical
python3 "$POST/qc.py" out/delivery/master-60s-16x9.mp4 --expect-duration 60 --fps 25 --resolution 1920x1080
```

`qc.py` returns **exit code 1** when there is at least one FAIL and prints "MUST NOT SHIP".
Warnings do not block delivery but stay in the report.

## Subtitles (silent playback)

Sound is not always on at an event screen; the key ideas must also read silently.
Two options:

```bash
# 1) Embedded (toggleable) subtitle stream
"$FF" -i master.mp4 -i subtitles.srt -c copy -c:s mov_text -metadata:s:s:0 language=<lang> out/master-sub.mp4

# 2) Burned-in subtitle — independent of player support
"$FF" -i master.mp4 -vf "subtitles=subtitles.srt:force_style='FontName=<YourFont>,FontSize=28,Outline=1,Shadow=0,MarginV=96'" \
  -c:v libx264 -profile:v high -pix_fmt yuv420p -r 25 -fps_mode cfr -c:a copy out/master-burn.mp4
```

Subtitle line rules are configurable per language; the brief must supply the values
for the target language. Worked example for English: at most ~42 characters per line,
at most 2 lines, and a ceiling of ~17 characters per second (CPS). Long sentences are
split, never abbreviated.

## Pre-event test playback

- [ ] Delivery file opened in the event player/server
- [ ] Loudness checked on the venue system (in the room, not in the mix)
- [ ] First and last frame checked (no black/broken frames)
- [ ] Subtitles (if any) at the correct size and inside the safe area
- [ ] File on a local copy (not dependent on a network connection)
- [ ] Backup delivery (H.264 yuv420p, constant fps, AAC) alongside
- [ ] Full duration equals the value the broadcast system requires

## Pitfalls (encountered in practice)

- **`set -e` + `pipefail` + `head`**: the `ffmpeg -i ... | head -1` pipeline **silently**
  kills the script because of SIGPIPE (with no output at all). Pipelines are closed with
  `|| true`; this project once saw `derive-versions.sh` fail to run for exactly this reason.
- **Copying a reference mix**: the promo reel examined clips at -7.6 LUFS and +1.5 dBTP.
  Loud is not "professional"; the target is -14 LUFS / -1 dBTP.
- **`-fps_mode cfr` instead of `-vsync`**: this is the correct flag in ffmpeg 7; a
  variable frame rate causes stutter on event players.
- **Generation loss from intermediate copies**: short versions are encoded in a single
  pass with no intermediate file.
- **Vertical cropped only from 16:9**: text gets cut off. Typography and the safe area
  are composed separately for vertical (`brand-asset-intake` scale,
  `video-motion-graphics` composition).
- **Duration tolerance**: because of frame alignment a 60-second film can come out at
  60.04 s; `qc.py` applies a ±0.10 s tolerance, tightened with `--expect-duration` if the
  broadcast system is stricter.

## Verified behaviour

These scripts were run on this machine:
synthetic 12-second source → `normalize-loudness.sh` (-14.0 LUFS / -12.4 dBTP) →
`encode-master.sh` (1080p25, 20 Mbps) → `qc.py` **0 FAIL / 13 passed**;
`derive-versions.sh` produced 8-second, 5-second and vertical 9:16 versions;
on the reference video `qc.py` reported 3 FAIL (loudness, true peak, black opening).
