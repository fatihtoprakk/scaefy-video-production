#!/usr/bin/env bash
# Print the path of a WORKING ffmpeg to stdout.
#
# Why this exists: `which ffmpeg` only proves a binary is present, not that it
# runs. A broken build (missing shared library, ABI mismatch) still resolves on
# PATH and then dies with a loader error at execution time. Every script here
# therefore tests EXECUTION, not existence, and picks the first candidate that
# actually answers `-version`.
#
# Usage:  FF="$(tools/ffmpeg.sh)"
# Order:  $FFMPEG -> repo-local tools/bin -> PATH -> Homebrew -> /usr/local
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
candidates=()

[ -n "${FFMPEG:-}" ] && candidates+=("$FFMPEG")
# A known-good repo-local build outranks PATH: it lets us use the right binary
# without touching (or depending on) whatever the system ships.
candidates+=("$PROJECT_ROOT/tools/bin/ffmpeg")
command -v ffmpeg >/dev/null 2>&1 && candidates+=("$(command -v ffmpeg)")
candidates+=("/opt/homebrew/bin/ffmpeg" "/usr/local/bin/ffmpeg")

shopt -s nullglob
for p in "$PROJECT_ROOT"/tools/bin/ffmpeg-* \
         "$PROJECT_ROOT"/tools/vendor/imageio_ffmpeg/binaries/ffmpeg-*; do
  candidates+=("$p")
done
shopt -u nullglob

for c in "${candidates[@]}"; do
  [ -x "$c" ] || continue
  # The `sh -c` wrapper matters: if a broken candidate dies from a signal
  # (SIGABRT and friends), the inner shell swallows the signal message and the
  # outer shell only sees a normal non-zero exit code.
  if sh -c '"$0" -hide_banner -version >/dev/null 2>&1' "$c" 2>/dev/null; then
    printf '%s\n' "$c"
    exit 0
  fi
done

cat >&2 <<'EOF'
ERROR: no working ffmpeg found.

Install into the repo, without modifying the system:
  python3 -m pip install --target tools/vendor imageio-ffmpeg
  mkdir -p tools/bin
  cp tools/vendor/imageio_ffmpeg/binaries/ffmpeg-* tools/bin/ffmpeg
  chmod +x tools/bin/ffmpeg

Verify:
  tools/ffmpeg.sh && echo OK

Note: ffprobe is not required. Every probe and measurement in this repo parses
`ffmpeg -i` output instead.
EOF
exit 1
