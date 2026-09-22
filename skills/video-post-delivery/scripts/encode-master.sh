#!/usr/bin/env bash
# H.264 master encode for event/web delivery.
#
# Usage:
#   encode-master.sh <input> <output> [--fps 25] [--height 1080|2160] [--bitrate 20M] [--maxrate 24M]
#
# Constant frame rate (CFR), yuv420p, High profile, faststart, Rec.709 tags.
# This is the most compatible combination for event players.
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

input="${1:?usage: encode-master.sh <input> <output> [--fps 25] [--height 1080] [--bitrate 20M]}"
output="${2:?output path required}"
shift 2

fps=25; height=1080; bitrate="20M"; maxrate="24M"; bufsize="40M"
while [ $# -gt 0 ]; do
  case "$1" in
    --fps)     fps="$2"; shift ;;
    --height)  height="$2"; shift ;;
    --bitrate) bitrate="$2"; shift ;;
    --maxrate) maxrate="$2"; shift ;;
    --bufsize) bufsize="$2"; shift ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
  shift
done

if [ "$height" = "2160" ] && [ "$bitrate" = "20M" ]; then bitrate="60M"; maxrate="70M"; bufsize="120M"; fi

[ -f "$input" ] || { echo "ERROR: file not found: $input" >&2; exit 1; }
gop=$(( fps * 2 ))

"$FF" -hide_banner -nostdin -loglevel warning -stats -y -i "$input" \
  -vf "scale=-2:${height}:flags=lanczos" \
  -r "$fps" -fps_mode cfr \
  -c:v libx264 -profile:v high -level 4.2 -preset slow -pix_fmt yuv420p \
  -b:v "$bitrate" -maxrate "$maxrate" -bufsize "$bufsize" -g "$gop" -keyint_min "$fps" -sc_threshold 0 \
  -colorspace bt709 -color_primaries bt709 -color_trc bt709 \
  -c:a aac -b:a 320k -ar 48000 -ac 2 \
  -movflags +faststart \
  "$output"

echo "Written: $output  (${height}p, ${fps} fps, ${bitrate})"
