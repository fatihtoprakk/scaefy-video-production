---
name: multiformat-recomposition
description: Owns the multi-format problem for a film — deciding per shot whether a new aspect ratio is recomposed or safely derived, then laying out and verifying landscape, vertical, square and ultra-wide cuts. Use when producing vertical, square or short cuts from a landscape film; when deciding to recompose a scene or derive a crop; when adapting one film for several platforms; when planning per-format safe areas, type scale or stacking; or when one composition renders several aspect ratios.
---

# Multiformat Recomposition

A 16:9 master is **one composition**, not a source to be re-framed. The same film usually
has to exist as landscape, vertical, square and sometimes ultra-wide, and the temptation
is to scale and crop one master into the others. That is the failure this skill exists to
prevent.

**Recomposition is not cropping.** A crop keeps a rectangle of a picture that was
composed for a different frame. Recomposition lays the scene out again for the target
frame: the type scale, the line breaks, the stacking, the position of the logo and the
amount of headroom are decisions, not leftovers. Only two outcomes are legitimate:

1. **Recompose** the scene for the target aspect ratio — the default.
2. **Derive** a cut from the master — only for a shot whose composition genuinely
   survives the crop, and only after stating what the crop removes.

## The governing test

Before a crop is accepted, write down what it removes: which text blocks, which graphic
module, how much of the subject, which edge of the frame. **If you cannot state what the
crop removes, you have not checked it, and the answer is recompose.**

The arithmetic alone is the warning. Covering a 9:16 target from a 16:9 frame keeps the
full original height and roughly **32% of the width**; a 1:1 target keeps about **56%**.
A centre crop is a decision about most of the picture, not a resize.

| Crop of a 16:9 1920×1080 master | Kept | Removed |
|---|---|---|
| 1:1 1080×1080 | 56% of the width, full height | 44% of the width |
| 9:16 1080×1920 | 32% of the width, full height | 68% of the width |
| 2.39:1 ultra-wide | full width, about 76% of the height | the top and bottom bands, where heads and lower thirds live |

```bash
# Audit what a 9:16 centre crop of the landscape master actually keeps, before it is
# accepted as a derived cut. Judge this preview; do not ship it.
"$(tools/ffmpeg.sh)" -hide_banner -i out/master-60s-1080p.mp4 -t 6 \
  -vf "crop=608:1080:656:0,scale=540:960" -an out/audit/crop-9x16-preview.mp4
```

## Format matrix

| Target | Resolution | Aspect | Typical use | `qc.py` spec |
|---|---|---|---|---|
| Landscape 1080p | 1920×1080 | 16:9 | Event screen, web hero, primary master | `landscape-1080` |
| Landscape 4K | 3840×2160 | 16:9 | Large venue, archival master, re-crop source | `landscape-4k` |
| Vertical | 1080×1920 | 9:16 | Short-form vertical feeds, stories | `vertical-1080` |
| Square | 1080×1080 | 1:1 | Feed posts, carousels, thumbnails | `square-1080` |
| Cinematic ultra-wide | project-defined (e.g. 1920×804) | 2.39:1 or 2.0:1 | Hero banner, title sequence, a deliberate letterbox | `any` plus an explicit `--resolution` |

Cinematic ultra-wide is a creative ratio, not a platform ratio: it is reached by cropping
height from a taller frame, so it removes headroom and lower thirds. Protect those bands
while shooting, or keep ultra-wide to graphic-led scenes. It has no dedicated `qc.py`
spec, so it is checked with `--spec any` and an explicit `--resolution` (and `--fps 25`).

Keep a 4K landscape master when the film is expected to travel: it is the only source
that can be recomposed into the other formats without upscaling.

## Recompose versus derive

The decision is keyed on **what the shot is**, not on how tight the deadline is.

| The shot is | Decision | Why |
|---|---|---|
| Full-bleed footage, centred subject, no burned-in text | Derive (crop) is usually safe | The crop removes context only, and the subject stays inside the new frame |
| Full-bleed footage with an off-centre subject, or text inside the picture | Recompose | The crop removes the subject's balance or the text itself |
| Lower third, name card, subtitle burn-in | Recompose | Type laid out for 1920 px of width overflows or clips in a 1080 px frame |
| Graphic modules: kinetic typography, counters, data bars, logo reveal, end card | Always recompose | These are layouts, and a layout does not survive an arbitrary rectangle |
| Split-screen, multi-column or side-by-side layouts | Always recompose | The columns collapse; the composition was the content |
| Screen recording, UI capture, document or slide | Recompose, or re-shoot at the target ratio | Cropping a UI removes controls and labels the viewer needs |
| Archive still or portrait | Recompose the crop point per image | A centre crop decapitates an off-centre portrait |

**Deriving is the exception; recomposing is the default.** The rule that keeps projects
honest: recompose the master and every hero format; derive only the low-stakes incidental
cuts — a preview, an internal review, a platform backfill of a centred talking head. Even
then the derived file is a crop and is labelled as one.

## One source, several compositions

Three architectural options, from most control to least:

| Option | How it works | Control | Cost | Use for |
|---|---|---|---|---|
| **Per-format render pass** | The same scene tree is rendered once per format, each pass with its own layout | Highest | Highest render time, one pass per format | The master and every hero format |
| **Shared composition with an aspect flag** | One scene tree reads the format and lays out conditionally | Good | One render per format, one code path | Projects with two or three formats and a stable layout vocabulary |
| **Post-hoc derivation** | `derive-versions.sh` scales, blurs or crops the finished master | Lowest | Nearly free | Low-stakes cuts of shots whose composition survives |

The shared composition is the usual middle ground, and it has one hard limit: **it must
not become a pile of conditionals.** Branch once, at the layout level, and let each format
supply layout tokens. Per-element aspect checks scattered through a scene are how a film
ends up with no format looking designed.

```js
// One scene tree, one clock. The format changes layout tokens, not the story.
const FORMAT = new URLSearchParams(location.search).get('format') || '16x9';
const LAYOUT = {
  '16x9': { w: 1920, h: 1080, safe: 0.08, type: 1.00, cols: 2 },
  '9x16': { w: 1080, h: 1920, safe: 0.08, type: 0.85, cols: 1 },
  '1x1':  { w: 1080, h: 1080, safe: 0.08, type: 0.92, cols: 1 },
}[FORMAT];
```

Those scale factors are placeholders. The type scale and the safe-area maths are owned by
`brand-asset-intake` (1080p reference, ×2 for 4K, ×0.85 for 9:16); this skill decides
where they are applied, and does not restate the numbers.

Keep the timing source shared. All formats come from the same beat list and the same
audio master, so a cut, a caption cue or a music hit lands on the same frame everywhere.
Formats differ in layout, never in story order — except where a vertical cut is genuinely
re-edited, and that re-edit is authored, not cropped.

## Per-format layout rules

What actually changes between formats:

| Property | 16:9 landscape | 9:16 vertical | 1:1 square |
|---|---|---|---|
| Safe area | 8% margin (see `brand-asset-intake`) | 8% nominal, tighter vertical band for critical text | 8% margin |
| Type scale | 1080p reference | ×0.85 (narrower frame, shorter line) | between the two |
| Line length | up to about 28 characters at 1080p | shorter lines, more of them | compact |
| Stacking | two or three columns are possible | single column, more vertical rhythm, larger gaps | single column, tight |
| Logo | a corner, with clear space | top or bottom, inside the safe band, never in the occluded bands | bottom or a corner |
| Headroom | subject near the upper third | more headroom above the subject; faces sit above the caption zone | centre-weighted |
| Captions | reinforcement | load-bearing, because viewing is muted | load-bearing |

Vertical has one constraint the others do not: **platform UI occludes the top and bottom
bands.** A progress bar, a caption row, an action rail and a handle sit over the picture,
so critical text must live inside a narrower vertical safe band than a naive percentage of
the frame height suggests. Measure that band for the actual target and record it instead
of assuming it: a headline that clears an 8% margin can still sit under the caption row.

Because the band is asymmetric and `tools/probe-layout.mjs --safe` takes one symmetric
fraction, run the probe with the **tighter** of the two bands as a conservative check and
confirm the horizontal margins in the same run. `tools/check-frames.py` derives its
margins from the image size it is given, so a still that is not 1920×1080 reports one
expected size FAIL while its ink, edge and safe-area percentages stay valid.

## Pacing and hook differences

A vertical cut is not the landscape film in a different frame; it is a different rhythm.
Author the vertical edit with its own timing first, then lay it out.

| Dimension | Landscape master | Vertical short |
|---|---|---|
| Hook | lands in the first 3–5 s | lands in the first 1–2 s (25–50 frames); frame one already carries the promise |
| Scene length | 3–6 s per beat | 1.5–3 s per beat, more cuts, every beat self-contained |
| Opening | may establish place before the point | no logo-first or atmosphere-first opener |
| Text on screen | supports the narration | carries the narration, because the film is usually watched muted |
| End card | logo plus CTA over 3–5 s | CTA readable in the last ~2 s at thumb size |

- **Assume muted.** Every spoken line that carries meaning is also on screen. Caption
  splitting, line length, cue timing and burn-in versus sidecar belong to
  `kinetic-captions-and-subtitles`; this skill requires only that captions exist in every
  format and that their cues are re-timed to the vertical cut rather than inherited.
- **Re-edit, do not just re-frame.** If the vertical version changes pacing, the picture
  cut and the music edit change with it. The landscape music edit under a faster vertical
  cut is audible immediately.
- **Re-measure audio per version.** The delivery targets are identical in every format:
  25 fps, H.264 yuv420p, Rec.709, **-14 LUFS integrated**, true peak **≤ -1 dBTP**. A
  shorter cut with a different fade has a different integrated loudness, so each version
  is measured on its own instead of inheriting the master's measurement.

## Verification per format

**A layout that passes in 16:9 says nothing about 9:16.** Every format gets its own
measured pass over the same beat list, and the stills for different formats are captured
at the same times so the passes can be compared frame for frame.

```bash
# 1. Stills per format. The page reads the format flag; shots.mjs uses a fixed
#    1920×1080 viewport, so a non-landscape composition is captured as a
#    format-true stage inside that canvas.
PUPPETEER_CACHE_DIR="$PWD/.puppeteer-cache" TMPDIR="$PWD/.tmp" \
  URL="file://$PWD/index.html?clean=1&format=9x16" \
  node tools/shots.mjs out/shots-9x16 0.5 1.5 6.0 14.0 28.0

# 2. Text geometry in the format's own coordinate space, against the safe band.
PUPPETEER_CACHE_DIR="$PWD/.puppeteer-cache" TMPDIR="$PWD/.tmp" \
  node tools/probe-layout.mjs --url "file://$PWD/index.html?clean=1&format=9x16" \
  --size 1080x1920 --safe 0.08 0.5 1.5 6.0 14.0 28.0

# 3. Frame integrity for that format: blank or flat frames, ink, edge contact.
python3 tools/check-frames.py out/shots-9x16/*.png --theme dark --text-windows 0.5-2,5-8

# 4. Static repository gates (banned strings, language, determinism, syntax).
bash tools/verify.sh
```

- `tools/shots.mjs` — capture. It prints page errors, so a still that shows one is a
  failed capture, not a failed design.
- `tools/probe-layout.mjs --safe` — the authority on text geometry. It reports the
  overflow in pixels per block, which is what turns a per-format type scale into a
  measurement instead of an opinion.
- `tools/check-frames.py` — blank or flat frames, ink coverage inside text windows,
  content touching the frame edge (clipped glyphs), safe-area violations.
- `python3 tools/contact-sheet.py out/sheet-9x16.jpg out/shots-9x16/*.png --cols 5` —
  review one format's rhythm at a glance.
- For a final composition check on the delivered pixels, pull a frame per format and
  compare the two side by side:
  ```bash
  "$(tools/ffmpeg.sh)" -hide_banner -ss 14.0 -i out/master-60s-9x16.mp4 \
    -frames:v 1 out/audit/9x16-t14_00.png
  ```
- `tools/verify.sh` covers the repository gates only; it knows nothing about formats, so
  the per-format checks above run in addition, never instead.

## Delivery

`skills/video-post-delivery/scripts/derive-versions.sh` derives short cuts and a vertical
version from a master, and `skills/video-post-delivery/scripts/encode-master.sh` encodes a
master to the delivery settings. The `video-post-delivery` skill owns the delivery matrix;
this skill owns the composition decisions that precede it.

```bash
POST=skills/video-post-delivery/scripts

# A recomposed vertical master is encoded at its own height. encode-master.sh scales by
# height, so a 1080×1920 master uses --height 1920; --height 1080 would rescale it to
# 608×1080 and silently destroy the format.
"$POST/encode-master.sh" out/mixed-9x16.mp4 out/master-60s-9x16.mp4 --height 1920

# Derivation, for the shots whose composition survives the crop.
"$POST/derive-versions.sh" out/master-60s-1080p.mp4 out/delivery --durations 60,30,15

# Every format is QC'd against its own spec.
python3 "$POST/qc.py" out/master-60s-9x16.mp4 --spec vertical-1080
python3 "$POST/qc.py" out/master-60s-1080p.mp4 --spec landscape-1080 --expect-duration 60
python3 "$POST/qc.py" out/master-60s-1x1.mp4 --spec square-1080
```

- The vertical master is QC'd against **`--spec vertical-1080`**, not against the
  landscape spec. A landscape spec on a vertical file fails on resolution and says
  nothing useful about the composition.
- `derive-versions.sh --vertical-mode crop` is a centre crop: exactly the operation this
  skill exists to prevent, used only for a shot whose composition genuinely survives.
  `--vertical-mode blur` preserves the whole picture over a blurred background, which is
  a safe fallback for footage, but it is a letterbox and not a vertical composition —
  graphic modules are still composed at 9:16.
- A derived cut inherits the master's fade and the master's loudness; re-measure both on
  the derived file.
- `qc.py` reports 0 FAIL or the file is not shipped. That gate applies to every format,
  including the ones derived last.

## Handoff

- How many formats the story actually needs, and the beats for each: `video-brief-and-storyboard`.
- Type scale, safe-area maths, contrast: `brand-asset-intake`.
- Graphic modules and their per-format composition: `video-motion-graphics`.
- Caption cues, line splitting and burn-in: `kinetic-captions-and-subtitles`.
- Encode, loudness, version derivation and the QC gate: `video-post-delivery`.

## Pitfalls

- **Cropping a 16:9 master to 9:16 and calling it a vertical version.** The result reads
  as low effort because it is: the composition was never designed for the frame.
- **Text that was inside the 16:9 safe area but outside the 9:16 one.** Type laid out
  against 1920 px of width overflows a 1080 px frame even when its margin percentage
  looks correct. The type scale is recomputed per format, never inherited.
- **A subject's head clipped by a centre crop.** The retained 32% strip slices a face that
  sits off-centre, and any crop that trims height — ultra-wide, or a crop of a taller
  source — takes the top of the head with it.
- **A composition so full of aspect-ratio conditionals that no single format looks
  designed.** Branch once at the layout level; when every element carries its own format
  check, the design has no owner.
- **Reusing the landscape music edit on a vertical cut with different pacing.** The hits
  land on the wrong frames, and the integrated loudness of the shorter cut has moved.
- **QC'ing only the landscape master and shipping the vertical unchecked.** The vertical
  is the format most likely to be watched and least likely to be measured.
- **Assuming a platform's safe area from memory rather than measuring it.** The occluded
  bands differ by target and change over time; measure the band, record it, and check text
  against the measured value.
- **Encoding a vertical master with `--height 1080`.** `encode-master.sh` scales by height,
  so a 1080×1920 source becomes 608×1080. Use `--height 1920`.
- **Letting a derived cut eat the end card.** The mechanical cut point and the 0.6 s fade
  can remove the CTA; if narrative integrity matters, the cut point is a human decision.
