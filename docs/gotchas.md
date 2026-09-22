# Gotchas

Failures that cost real time, each with the fix. Every entry here was paid for
once; the point of writing them down is not to pay twice.

---

## Capture and rendering

### `<video>` does not play in a headless shell

`chrome-headless-shell` can fail to decode H.264 and VP9 with
`MEDIA_ELEMENT_ERROR: Format error`, and `file://` plus local HTTP may both be
unavailable. **Do not build a film that depends on `<video>` playback.**

**Fix:** play footage as a JPEG frame sequence at the target frame rate, and make
the film's seek contract await image decoding (`seekAsync`) so a captured frame
is never a stale one.

### "Requesting main frame too early"

Some Puppeteer and Chrome version combinations raise this on `page.goto()` right
after `newPage()`.

**Fix:** prefer `chrome-headless-shell` and reuse the blank tab the browser
already opened at launch instead of calling `newPage()` and navigating
immediately. `tools/shots.mjs` and `tools/export-frames.mjs` both do this.

### Full-bleed footage must never scale below 1

Scaling full-bleed footage below 1 leaves a sliver of background at the frame
edge, which reads as a rendering bug.

**Fix:** clamp the scale at 1 and let the footage crop instead.

### Background typography in front of the content

A background layer (giant number, grid) placed after the content layer silently
covers it.

**Fix:** keep the back layer *before* the content in document order, and the
overlay after it. Verify by capturing a frame where both are visible.

---

## Encoding

### JPEG sources encode as `yuvj420p` and get rejected

Intermediate JPEG frames are full-range. Without an explicit conversion the
output is `yuvj420p`, which delivery specs reject.

**Fix:** convert the range explicitly and tag the output:

```
scale=in_range=full:out_range=limited   plus   -color_range tv
```

### `ffprobe` may not be available

Do not assume `ffprobe` exists. Every measurement in this repo parses `ffmpeg -i`
output instead, and `tools/ffmpeg.sh` resolves a binary that actually executes
rather than one that merely exists on `PATH`.

### `set -e` plus `pipefail` plus `head` kills the script

`ffmpeg -i file | head -1` terminates the pipeline early; `head` exits, `ffmpeg`
receives SIGPIPE, and `pipefail` turns that into a silent script death.

**Fix:** append `|| true`, or capture the full output and slice it afterwards.

### `acrossfade` and `adelay` chains are unreliable for music beds

Building a bed longer than the source track by chaining `acrossfade`/`adelay`
has produced a track that silently shortened and a track whose tail was silent.

**Fix:** compute the crossfade arithmetic explicitly in a script — sample offsets
and overlap lengths — rather than trusting the filter graph to do it.

### AAC padding stretches the container past the video

Re-encoding audio while copying video can leave the container longer than the
video stream. AAC adds encoder padding, and the container duration follows the
**longest** stream — so a film whose video is exactly 60.00 s comes out at
60.10 s. A duration gate with a ±0.10 s tolerance then rejects a file that is
correct in every other respect.

This was measured, not theorised: the pack's own `normalize-loudness.sh` produced
a 60.10 s file that its own `qc.py` refused.

**Fix:** pass `-shortest` when the video is copied and the audio is re-encoded, so
the output is cut to the shortest stream. `normalize-loudness.sh` does this. If
you build your own chain, either add `-shortest` or trim the audio explicitly with
`-t <duration>`.

### A gate that does not measure a documented requirement

The delivery matrix documents H.264 High profile, and `encode-master.sh` sets it.
`qc.py` originally checked the codec but never the profile, so a Baseline file
passed a gate that claimed to enforce High.

**Fix:** measure what you document. `qc.py` now parses the profile from
`ffmpeg -i` output and fails when it does not match the spec.

---

## Measurement

### Pixel-based "is the text there" checks mislead

A background gradient registers as ink, so a pixel scan can report text where
there is none.

**Fix:** measure layout from the DOM with `getComputedStyle` and
`Range.getClientRects()`, and use pixel checks only for presence and overflow.
`tools/probe-layout.mjs` reports real glyph boxes, not block boxes.

### A layout that passes in one aspect ratio says nothing about another

Safe areas and type scale change per format.

**Fix:** run a measured pass per aspect ratio, not once for the master.

---

## CSS

### Specificity trap

A later rule with higher specificity silently overrides an earlier one — for
example a two-line heading collapsing to one line because a `.hero .txt` rule
landed after the line-break rule.

**Fix:** keep layout rules for the same element adjacent, and verify the rendered
result rather than reading the stylesheet.

### Losing `position` when converting text to an image

Converting an element from text to an image drops `position: absolute`, so
`left`/`top` stop applying and the element snaps to the origin.

**Fix:** re-declare `position` on the replaced element.

---

## Tooling and repository hygiene

### macOS ships bash 3.2

`mapfile`, associative arrays, and other bash 4+ features are unavailable. Scripts
that work in CI on Linux can fail on a developer's Mac.

**Fix:** use `while read` loops and process substitution. `tools/verify.sh`
targets bash 3.2 deliberately.

### A verify script can fail its own gate

A language or blocklist gate that contains the literal patterns it searches for
will detect itself and report a false failure.

**Fix:** write the pattern with escapes (for example `\u` escapes in a character
class) or exempt the file explicitly and document why.

### Shadowing a common command

Defining a shell function named `head`, `test`, or `ls` silently replaces the
command for the rest of the script.

**Fix:** prefix helper names (`section`, `log`, `die`).

### A blocklist that names the client is itself a leak

Shipping a public blocklist containing a client's real names publishes exactly
the strings it exists to block.

**Fix:** ship the *mechanism* publicly with every entry commented out, keep the
real list in the private working copy, and run the check from there before
publishing.

### A gate that enforces nothing must not report success

A blocklist with no active patterns is not a pass. Reporting `PASS` hides the
fact that nothing is being checked.

**Fix:** report a warning that distinguishes "checked and clean" from
"installed but not enforcing".
