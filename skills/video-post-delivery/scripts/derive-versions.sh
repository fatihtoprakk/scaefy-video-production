#!/usr/bin/env bash
# Derive delivery versions from a single master: 60/30/15 s (16:9) + vertical 9:16.
#
# Usage:
#   derive-versions.sh <master> <output_dir> [--durations 60,30,15] [--vertical] [--vertical-mode blur|crop]
#
# Notes:
#   • Short versions are cut from the head of the master and faded out over the last
#     0.6 s. If narrative integrity matters, the cut point must be a human decision;
#     this script is for mechanical derivation (teaser/preview).
#   • Every version is encoded in a single pass directly to delivery settings; no
#     intermediate copy is produced (so there is no generation loss).
#   • In the vertical version the source image is centred over a blurred background.
#     Graphic modules (typography, data bars) must ALSO be composed at 9:16 for
#     vertical; the transform here only carries the picture across safely.
set -euo pipefail

self="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
find_root() {
  local d="$1"
  while [ "$d" != "/" ]; do
    [ -x "$d/tools/ffmpeg.sh" ] && { printf '%s\n' "$d"; return 0; }
    d="$(dirname "$d")"
  done
  return 1
}
ROOT="$(find_root "$self")" || { echo "ERROR: project root not found" >&2; exit 1; }
FF="$("$ROOT/tools/ffmpeg.sh")"

master="${1:?usage: derive-versions.sh <master> <output_dir> [--durations 60,30,15] [--vertical]}"
outdir="${2:?output directory required}"
shift 2

durations="60,30,15"; vertical=0; vmode="blur"
while [ $# -gt 0 ]; do
  case "$1" in
    --durations) durations="$2"; shift ;;
    --vertical) vertical=1 ;;
    --vertical-mode) vmode="$2"; shift ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
  shift
done

[ -f "$master" ] || { echo "ERROR: master not found: $master" >&2; exit 1; }
mkdir -p "$outdir"
base="$(basename "${master%.*}")"

# Duration read: `ffmpeg -i` with no output always returns 1, and a pipeline that
# closes early (such as `head`) raises SIGPIPE. Under `set -e` + `pipefail` that
# SILENTLY kills the script, so the pipeline is closed with `|| true` and the
# result is validated.
master_dur="$("$FF" -hide_banner -nostdin -i "$master" 2>&1 \
  | sed -n 's/.*Duration: \([0-9][0-9]*:[0-9][0-9]*:[0-9.]*\).*/\1/p' \
  | awk -F: 'NR==1 { printf "%.2f", $1*3600 + $2*60 + $3 }' || true)"
[ -n "$master_dur" ] || { echo "ERROR: could not read master duration: $master" >&2; exit 1; }
echo "Master: $base (${master_dur}s) → $outdir"

VENC=(-r 25 -fps_mode cfr -c:v libx264 -profile:v high -level 4.2 -preset slow
      -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709
      -c:a aac -b:a 320k -ar 48000 -ac 2 -movflags +faststart)

IFS=',' read -ra secs <<< "$durations"
for n in "${secs[@]}"; do
  out="$outdir/${base}-${n}s-16x9.mp4"
  if awk -v m="$master_dur" -v n="$n" 'BEGIN{exit !(m > n + 0.15)}'; then
    fade_start="$(awk -v n="$n" 'BEGIN{printf "%.2f", n-0.6}')"
    "$FF" -hide_banner -nostdin -loglevel warning -stats -y -i "$master" -t "$n" \
      -vf "fade=t=out:st=${fade_start}:d=0.6" \
      -af "afade=t=out:st=${fade_start}:d=0.6" \
      "${VENC[@]}" -b:v 20M -maxrate 24M -bufsize 40M -g 50 -keyint_min 25 -sc_threshold 0 \
      "$out"
  else
    # The master is already shorter than this duration: only transcode to delivery settings.
    "$FF" -hide_banner -nostdin -loglevel warning -stats -y -i "$master" \
      "${VENC[@]}" -b:v 20M -maxrate 24M -bufsize 40M -g 50 -keyint_min 25 -sc_threshold 0 \
      "$out"
  fi
  echo "  → $out"
done

if [ "$vertical" -eq 1 ]; then
  case "$vmode" in
    blur)
      vf="split=2[bg][fg];[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=40:2,eq=brightness=-0.06[bg2];[fg]scale=1080:-2[fg2];[bg2][fg2]overlay=(W-w)/2:(H-h)/2"
      ;;
    crop)
      vf="scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
      ;;
    *) echo "ERROR: --vertical-mode must be blur|crop" >&2; exit 2 ;;
  esac
  vout="$outdir/${base}-vertical-9x16.mp4"
  "$FF" -hide_banner -nostdin -loglevel warning -stats -y -i "$master" -vf "$vf" \
    "${VENC[@]}" -b:v 16M -maxrate 20M -bufsize 32M -g 50 -keyint_min 25 -sc_threshold 0 \
    "$vout"
  echo "  → $vout (vertical, mode: $vmode)"
fi

echo "Done."
