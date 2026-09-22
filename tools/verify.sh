#!/usr/bin/env bash
# verify.sh — run every quality gate in one command.
#
# Gates:
#   1. banned strings   no blocklisted term appears outside the blocklist itself
#   2. language         no Turkish-specific characters anywhere in shipped text
#   3. determinism      no Math.random / Date.now / setInterval in film sources
#   4. syntax           shell, Python, and Node files parse
#   5. delivery         qc.py gate on a rendered master (only with --video)
#
# Usage:
#   tools/verify.sh
#   tools/verify.sh --video out/master.mp4
#
# Exit code is 0 only when every gate passes.
#
# Portable to bash 3.2 (the macOS default): no `mapfile`, no associative arrays.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

VIDEO=""
while [ $# -gt 0 ]; do
  case "$1" in
    --video) VIDEO="${2:-}"; shift 2 ;;
    -h|--help) sed -n '2,16p' "$0"; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

FAILED=0
pass()    { printf '  \033[32mPASS\033[0m  %s\n' "$1"; }
fail()    { printf '  \033[31mFAIL\033[0m  %s\n' "$1"; FAILED=1; }
warn()    { printf '  \033[33mWARN\033[0m  %s\n' "$1"; }
section() { printf '\n\033[1m%s\033[0m\n' "$1"; }

# The blocklist ships as a TEMPLATE with every entry commented out: this repo is
# public, and naming a client here would leak the very strings the list exists
# to block. The real list lives in the private project that owns this pack,
# which runs its own pre-publish check. Comment marker is `;` so hex colour
# values stay matchable.
BLOCKLIST="tools/banned-strings.txt"

section "1. banned strings"
if [ ! -f "$BLOCKLIST" ]; then
  fail "$BLOCKLIST is missing"
else
  set +e
  BLOCK_OUT="$(python3 - "$BLOCKLIST" <<'PY'
import pathlib, sys
block = pathlib.Path(sys.argv[1])
terms = [l.strip() for l in block.read_text(encoding='utf-8').splitlines()
         if l.strip() and not l.lstrip().startswith(';')]
if not terms:
    print("    every entry is commented out")
    sys.exit(2)
skip_dirs = {'.git', 'node_modules', '__pycache__', '.puppeteer-cache', '.tmp', 'out', 'vendor'}
hits = []
for p in pathlib.Path('.').rglob('*'):
    if not p.is_file() or any(part in skip_dirs for part in p.parts):
        continue
    if p.resolve() == block.resolve():
        continue
    try:
        text = p.read_text(encoding='utf-8')
    except (UnicodeDecodeError, OSError):
        continue
    low = text.lower()
    for t in terms:
        if t.lower() in low:
            hits.append(f"{p}: {t}")
if hits:
    print('\n'.join('    ' + h for h in hits[:40]))
    print(f"    ({len(hits)} hit(s) across {len(terms)} patterns)")
    sys.exit(1)
print(f"    {len(terms)} patterns checked")
PY
)"
  BLOCK_CODE=$?
  set -e
  [ -n "$BLOCK_OUT" ] && printf '%s\n' "$BLOCK_OUT"
  case "$BLOCK_CODE" in
    0) pass "no blocklisted term found" ;;
    2) warn "no active patterns — mechanism installed, nothing enforced yet" ;;
    *) fail "blocklisted term present (see above)" ;;
  esac
fi

section "2. language (no Turkish-specific characters)"
# This gate checks for Turkish-specific letters, NOT for English. Vendored
# third-party skills keep their upstream language (bang-motion ships in
# Indonesian) and must pass this gate untouched.
# The Turkish letter class is written as \u escapes on purpose: a literal class
# would make this very file fail its own gate.
if python3 - <<'PY'
import pathlib, re, sys
turkish = re.compile('[\u00e7\u011f\u0131\u00f6\u015f\u00fc\u00c7\u011e\u0130\u00d6\u015e\u00dc]')
skip_dirs = {'.git', 'node_modules', '__pycache__', '.puppeteer-cache', '.tmp', 'out', 'vendor'}
# The bundled example film is BRAND CONTENT, not pack prose: its on-screen copy is
# Turkish by design, and example/README.md quotes that copy when it documents the
# beats. The directory is exempt from the LANGUAGE scan only — the banned-string
# gate above still scans it, and the convention that the README's own prose is
# English is kept by hand rather than enforced here.
skip_dirs.add('example')
# A blocklist must contain the terms it blocks.
skip_files = {'tools/banned-strings.txt'}
hits = []
for p in pathlib.Path('.').rglob('*'):
    if not p.is_file() or any(part in skip_dirs for part in p.parts):
        continue
    if str(p) in skip_files:
        continue
    try:
        text = p.read_text(encoding='utf-8')
    except (UnicodeDecodeError, OSError):
        continue
    found = turkish.findall(text)
    if found:
        line = text[:text.index(found[0])].count('\n') + 1
        hits.append(f"{p}: {len(found)} char(s), first at line {line}")
if hits:
    print('\n'.join('    ' + h for h in hits[:40]))
    print(f"    ({len(hits)} file(s))")
    sys.exit(1)
PY
then pass "no Turkish-specific characters"; else fail "Turkish-specific characters present (see above)"; fi

section "3. determinism"
DET_HITS=0
DET_FOUND=0
while IFS= read -r f; do
  [ -n "$f" ] || continue
  DET_FOUND=1
  if grep -nE 'Math\.random|Date\.now|setInterval' "$f"; then DET_HITS=1; fi
done < <(find . -path ./node_modules -prune -o \
  \( -name 'index.html' -o -name '*.film.js' \) -print 2>/dev/null | grep -v node_modules || true)

if [ "$DET_FOUND" = 0 ]; then
  warn "no film sources found yet (example/ not built) — gate skipped"
elif [ "$DET_HITS" = 0 ]; then
  pass "film sources are deterministic"
else
  fail "non-deterministic call in film source (animation must be a function of time)"
fi

section "4. syntax"
SYNTAX_OK=1
while IFS= read -r f; do
  [ -n "$f" ] || continue
  bash -n "$f" || SYNTAX_OK=0
done < <(find tools skills -name '*.sh' -type f 2>/dev/null)
while IFS= read -r f; do
  [ -n "$f" ] || continue
  python3 -m py_compile "$f" || SYNTAX_OK=0
done < <(find tools skills -name '*.py' -type f 2>/dev/null)
while IFS= read -r f; do
  [ -n "$f" ] || continue
  node --check "$f" >/dev/null || SYNTAX_OK=0
done < <(find tools skills -name '*.mjs' -type f 2>/dev/null)
find . -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
[ "$SYNTAX_OK" = 1 ] && pass "shell, Python, and Node files parse" || fail "syntax error (see above)"

section "5. skill contract"
if python3 - <<'PY'
import pathlib, re, sys
root = pathlib.Path('skills')
if not root.is_dir():
    print("    no skills/ directory")
    sys.exit(1)
kebab = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
bad, checked, vendored = [], 0, 0
for d in sorted(p for p in root.iterdir() if p.is_dir()):
    f = d / 'SKILL.md'
    if not f.exists():
        bad.append(f"{d.name}: missing SKILL.md")
        continue
    text = f.read_text(encoding='utf-8')
    if not text.startswith('---'):
        bad.append(f"{d.name}: no YAML frontmatter")
        continue
    fm = text.split('---', 2)[1]
    m = re.search(r'^name:\s*(\S+)', fm, re.M)
    desc = re.search(r'^description:\s*(.+)', fm, re.M)
    if not m:
        bad.append(f"{d.name}: frontmatter has no name")
        continue
    if m.group(1) != d.name:
        bad.append(f"{d.name}: frontmatter name '{m.group(1)}' does not match the directory")
    if not kebab.match(m.group(1)):
        bad.append(f"{d.name}: name '{m.group(1)}' is not kebab-case")

    # Vendored third-party skills carry their own LICENSE. They keep their
    # upstream language and structure, so only the name checks apply to them.
    if (d / 'LICENSE').exists():
        vendored += 1
        checked += 1
        continue

    if not desc or 'use when' not in desc.group(1).lower():
        bad.append(f"{d.name}: description has no 'Use when' routing trigger")
    infence, h1 = False, 0
    for line in text.splitlines():
        if line.strip().startswith('```'):
            infence = not infence
            continue
        if not infence and re.match(r'^# ', line):
            h1 += 1
    if h1 != 1:
        bad.append(f"{d.name}: {h1} top-level headings outside code fences (expected 1)")
    checked += 1

# Cross-references: a backticked kebab-case token that looks like a skill name
# must resolve to a skill that actually exists. Renaming a skill without updating
# its siblings is the usual way a pack rots.
names = {p.name for p in root.iterdir() if p.is_dir()}
prefixes = ('video-', 'brand-', 'ai-', 'kinetic-', 'multiformat-', 'voiceover-',
            'footage-', 'render-')
ref = re.compile(r'`([a-z][a-z0-9]*(?:-[a-z0-9]+){1,4})`')
for d in sorted(p for p in root.iterdir() if p.is_dir()):
    f = d / 'SKILL.md'
    if not f.exists():
        continue
    text = f.read_text(encoding='utf-8')
    for token in sorted(set(ref.findall(text))):
        if token not in names and token.startswith(prefixes):
            bad.append(f"{d.name}: references skill '{token}' which does not exist")

if bad:
    print('\n'.join('    ' + b for b in bad))
    print(f"    ({len(bad)} problem(s))")
    sys.exit(1)
print(f"    {checked} skills checked ({vendored} vendored, exempt from style checks)")
PY
then pass "every skill satisfies the authoring contract"; else fail "skill contract violation (see above)"; fi

section "6. delivery QC"
if [ -z "$VIDEO" ]; then
  warn "no --video given — delivery gate skipped"
elif [ ! -f "$VIDEO" ]; then
  fail "video not found: $VIDEO"
elif python3 skills/video-post-delivery/scripts/qc.py "$VIDEO"; then
  pass "delivery QC returned 0 FAIL"
else
  fail "delivery QC reported FAIL — do not ship"
fi

printf '\n'
if [ "$FAILED" = 0 ]; then
  printf '\033[32mAll gates passed.\033[0m\n'
else
  printf '\033[31mOne or more gates failed.\033[0m\n'
fi
exit "$FAILED"
