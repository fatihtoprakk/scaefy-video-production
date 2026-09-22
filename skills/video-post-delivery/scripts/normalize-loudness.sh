#!/usr/bin/env bash
# Two-pass EBU R128 loudness normalisation (loudnorm).
#
# Usage:
#   normalize-loudness.sh <input> <output> [--target -14.0] [--tp -1.0] [--lra 11]
#
# If a video stream is present it is copied (-c:v copy); audio is re-encoded (AAC 48 kHz).
# If only an audio file is given, an audio-only output is produced.
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

input="${1:?usage: normalize-loudness.sh <input> <output> [--target -14] [--tp -1] [--lra 11]}"
output="${2:?output path required}"
shift 2

target_i="-14.0"; target_tp="-1.0"; target_lra="11"
while [ $# -gt 0 ]; do
  case "$1" in
    --target) target_i="$2"; shift ;;
    --tp)     target_tp="$2"; shift ;;
    --lra)    target_lra="$2"; shift ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
  shift
done

[ -f "$input" ] || { echo "ERROR: file not found: $input" >&2; exit 1; }

filter="loudnorm=I=${target_i}:TP=${target_tp}:LRA=${target_lra}"

# Pass 1: measurement
measured="$("$FF" -hide_banner -nostdin -i "$input" -map 0:a:0? -af "${filter}:print_format=json" -f null - 2>&1 || true)"
json="$(printf '%s' "$measured" | sed -n '/{/,/}/p' | tail -n +1)"
[ -n "$json" ] || { echo "ERROR: loudnorm measurement failed (the audio stream may be missing)" >&2; exit 1; }

read -r m_i m_tp m_lra m_thresh m_offset <<EOF
$(printf '%s' "$json" | python3 -c '
import json,sys
d=json.load(sys.stdin)
print(d["input_i"], d["input_tp"], d["input_lra"], d["input_thresh"], d["target_offset"])
')
EOF

echo "Measured: I=$m_i TP=$m_tp LRA=$m_lra thresh=$m_thresh offset=$m_offset"

# Pass 2: linear normalisation (video is copied)
#
# `-shortest` is required, not cosmetic. The video stream is copied and keeps the
# source's exact length, but the re-encoded AAC audio gets encoder padding, which
# can run past the last video frame. Without `-shortest` the container duration
# follows the LONGEST stream, so a 60.00 s film comes out at 60.10 s and the
# delivery gate rejects it for duration. Cutting to the shortest stream keeps the
# container exactly as long as the video.
has_video="$("$FF" -hide_banner -nostdin -i "$input" 2>&1 | grep -c "Video:" || true)"
if [ "$has_video" -gt 0 ]; then
  "$FF" -hide_banner -nostdin -loglevel warning -stats -y -i "$input" \
    -map 0:v:0 -map 0:a:0? -c:v copy \
    -af "${filter}:measured_I=${m_i}:measured_TP=${m_tp}:measured_LRA=${m_lra}:measured_thresh=${m_thresh}:offset=${m_offset}:linear=true" \
    -c:a aac -b:a 320k -ar 48000 -ac 2 -shortest "$output"
else
  "$FF" -hide_banner -nostdin -y -i "$input" \
    -af "${filter}:measured_I=${m_i}:measured_TP=${m_tp}:measured_LRA=${m_lra}:measured_thresh=${m_thresh}:offset=${m_offset}:linear=true" \
    -c:a aac -b:a 320k -ar 48000 -ac 2 "$output"
fi

echo "Written: $output"
echo "Verification:"
"$ROOT/skills/video-post-delivery/scripts/loudness.sh" "$output" --check --target "$target_i" --tp "$target_tp" || true
