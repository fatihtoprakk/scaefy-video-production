#!/usr/bin/env bash
# EBU R128 loudness measurement and target check.
#
# Usage:
#   loudness.sh <file> [--check] [--target -14.0] [--tp -1.0] [--window 0.5]
#
# --check: exits with code 1 when the measurement is outside target (acts as a pre-delivery gate).
# Output: Integrated LUFS, LRA, True Peak (dBTP) plus a PASS/FAIL/WARN line.
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
ROOT="$(find_root "$self")" || { echo "ERROR: project root not found (tools/ffmpeg.sh missing)" >&2; exit 1; }
FF="$("$ROOT/tools/ffmpeg.sh")"

input="${1:?usage: loudness.sh <file> [--check] [--target -14.0] [--tp -1.0] [--window 0.5]}"
shift || true

check=0; target_i="-14.0"; target_tp="-1.0"; window="0.5"
while [ $# -gt 0 ]; do
  case "$1" in
    --check) check=1 ;;
    --target) target_i="$2"; shift ;;
    --tp)     target_tp="$2"; shift ;;
    --window) window="$2"; shift ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
  shift
done

[ -f "$input" ] || { echo "ERROR: file not found: $input" >&2; exit 1; }

raw="$("$FF" -hide_banner -nostdin -i "$input" -map 0:a:0? -af ebur128=peak=true -f null - 2>&1 || true)"

if ! printf '%s' "$raw" | grep -q "Integrated loudness"; then
  echo "ERROR: no audio stream found or measurement failed: $input" >&2
  exit 1
fi

# Parse the summary block (everything after "Integrated loudness:") so progress
# lines ("t: ... I: -7.6 LUFS ...") cannot be confused with the summary values.
summary="$(printf '%s' "$raw" | sed -n '/Integrated loudness:/,$p')"
pick() { printf '%s' "$summary" | grep -oE "^ +$1: +-?[0-9]+(\.[0-9]+)?" | grep -oE '\-?[0-9]+(\.[0-9]+)?' | head -1; }

# `|| true`: when `head -1` closes early, grep receives SIGPIPE; under
# set -e + pipefail that would silently kill this script.
I="$(pick I || true)"
LRA="$(pick LRA || true)"
TP="$(pick Peak || true)"

[ -n "$I" ] || I="NaN"
[ -n "$LRA" ] || LRA="NaN"
[ -n "$TP" ] || TP="NaN"

printf 'File            : %s\n' "$(basename "$input")"
printf 'Integrated      : %s LUFS   (target %s)\n' "$I" "$target_i"
printf 'Loudness range  : %s LU\n' "$LRA"
printf 'True peak       : %s dBTP   (target ≤ %s)\n' "$TP" "$target_tp"

if [ "$check" -eq 1 ]; then
  if ! [[ "$I" =~ ^-?[0-9]+(\.[0-9]+)?$ ]] || ! [[ "$TP" =~ ^-?[0-9]+(\.[0-9]+)?$ ]]; then
    echo "RESULT          : FAIL (measurement unreadable)"
    exit 1
  fi

  # Every problem is reported in one pass (no early exit on the first error).
  report="$(awk -v i="$I" -v ti="$target_i" -v tp="$TP" -v ttp="$target_tp" -v w="$window" 'BEGIN{
    fail = 0;
    di = i - ti; if (di < 0) di = -di;
    if (di > w) { printf "  • Integrated outside target: %+.2f LU deviation (tolerance ±%.2f LU)\n", i - ti, w; fail = 1 }
    if (tp > ttp) { printf "  • True peak exceeds target: %+.2f dB (clipping risk)\n", tp - ttp; fail = 1 }
    else if (tp > ttp - 0.2) { printf "  • WARNING: true peak is very close to the limit (%.2f dBTP)\n", tp }
    exit fail
  }')" || true

  if [ -n "$report" ]; then
    printf '%s\n' "$report" | grep -v '^  • WARNING' || true
    printf '%s\n' "$report" | grep '^  • WARNING' || true
    if printf '%s\n' "$report" | grep -qv '^  • WARNING'; then
      echo "RESULT          : FAIL"
      exit 1
    fi
    echo "RESULT          : PASS (with warnings)"
    exit 0
  fi
  echo "RESULT          : PASS"
fi
