---
name: video-motion-graphics
description: Produces the graphics layer for a brand film or promo in code — kinetic typography, word-build titles, counters, data bars, name cards, logo reveal and end card at 25 fps in 16:9 and 9:16. Use when a brief or a liked reference video needs kinetic type, counters, data bars, name cards, a logo reveal or an end card; when effects must be rebuilt with real brand assets, not copied skin; or when typography and transitions must be versioned and re-rendered, not hand-animated in After Effects.
---

# Motion Graphics

The **graphics layer** that sits on top of the live-action spine is produced here. The
goal is to take the **rhythm** of a liked reference video and derive the **skin** from
the brand.

## Two engines — which one when

| Engine | When | Where |
|---|---|---|
| **HTML + CSS + GSAP** (the `bang-motion` skill) | Fast iteration as a single `index.html`, instant preview in the browser, kinetic typography / opener / bumper / lower third, 16:9 and 9:16 | The `bang-motion` skill: `assets/starter-opener.html` architecture, `references/techniques.md` recipes, frame-by-frame MP4 via `scripts/export-frames.mjs` |
| **Remotion + React** (the `remotion-marketing-video` skill) | Data-driven, multi-scene templates that are rendered over and over; data bars/counters as React components; versioned output | The `remotion-marketing-video` skill (setup, animation maths, export pipeline) |

Decision rule: **a one-off event opener with fast iteration → GSAP**; **a data-fed
template produced over and over → Remotion**. Do not mix the two in the same film; an
alpha-channel graphics layer is produced in one engine and composited in the edit.

Both engines read `assets/brand/tokens.json` (see the `brand-asset-intake` skill). Brand
colour and font are **never hardcoded** in the code; they come from the tokens.

## Invariant rules

1. **The reference gives rhythm, not skin.** Taken from the reference video: shot
   duration, cutting rhythm, word-break logic, the presence of counters/bars, typographic
   hierarchy. Not taken: palette, font, texture, layout, ornaments, sentences, scene
   order. The palette, fonts, texture and layout come from the project's own brand tokens
   (`assets/brand/tokens.json`), never from the reference video. This is not a preference;
   it is a rule.
2. **Determinism.** Every visible change is a function of time (the frame number). No
   `Date.now()`, no `Math.random()`, no CSS transition/keyframe, no timers. Otherwise the
   frame-by-frame render and the preview will not match.
3. **Frame-accurate timing.** A constant 25 fps. Timecodes are written converted to
   frames.
4. **Measured text animation.** Brief §7: 6–10 frames of opacity + 12–20 px of vertical
   movement. No flashy kinetic typography; word-build is used only in the question section
   and in the finale.
5. **Every key idea stays on screen for at least 1.5 s (38 frames).** There is silent
   viewing at the event.
6. **Graphics budget.** The brief defines its own effect windows. Effects serve the story
   and never bury it: the middle section stays documentary, and graphics never overpower
   the spine.
7. **Safe area.** At least 8% from the edges; extra allowance for the top and bottom bands
   in 9:16.

## Timing table (25 fps) and module placement

| Time | Frames | Graphics module | Typography |
|---|---|---|---|
| 0:00–0:06 | 0–150 | **M1** question 1–2 | Word-build, two questions |
| 0:06–0:12 | 150–300 | **M1** continued | Short headlines |
| 0:12–0:23 | 300–575 | none (documentary) | Lower third only |
| 0:23–0:30 | 575–750 | **M3** data module | `QUESTION ONE` |
| 0:30–0:39 | 750–950 | **M3** number-heavy | `THE WHOLE PICTURE` |
| 0:39–0:46 | 950–1125 | **M4** name cards | Real interview subjects |
| 0:46–0:57 | 1125–1425 | none | `ROLES. EXPECTATIONS. TECHNOLOGY.` |
| 0:57–1:00 | 1425–1500 | **M5** logo reveal + end card | `BEYOND THE FAMILIAR.` + CTA |

The strings in the Typography column are illustrative placeholders that show the shape of
the copy; the brief supplies the final on-screen text.

## Module recipes

**M1 — Word-build typography.** The sentence completes at a shot boundary (on screen
`WHY DO PEOPLE` → cut → `BURN OUT?`). A word group gains opacity over 6–10 frames and
shifts up 12–20 px; no letter-by-letter animation (it distracts). About 28 characters per
line. The emphasis word is in the brand accent colour from the tokens, the rest off-white.

**M2 — Portrait mosaic (conditional).** If real archive photography exists, a 6×4 grid;
the tiles appear in sequence (each tile 4–6 frames apart). If the photo pool is not real,
it is **not used** (stock portraits give the film a "stock feel"). Colour: a single-colour
duotone derived from the brand tokens, plus natural skin tones.

**M3 — Data / counter bars.** 3–4 numbers; each number counts up with `tabular-nums`, a
thin bar grows toward the target beneath it, label 34–42 px. Number 92–112 px. **Only
data whose source can be shown is used**; an unverified statistic is never published.
Instead of the reference's "25 speakers / 35 investors" crowd effect, use a small number
of meaningful measures here.

**M4 — Name card.** Lower third: name (48–56 px) + title (34–38 px), 6–10 frames of
opacity, 16–24 px slide from the left. No date badge, no `SPEAKER` tag, no ornament —
plain, editorial. If a background is needed, a panel at 60% opacity in the brand's dark
tone from the tokens (for contrast: `brand-asset-intake`).

**M5 — Logo reveal + end card.** Instead of a hexagon, an **organically growing line**: a
thin line in the brand colour slowly extending from left to right, a soft light opening at
the centre, the logo coming from a real file (never drawn in code). Then
`BEYOND THE FAMILIAR.` plus a verified web/Instagram CTA. The module's background is
supplied by the brief.

## Alpha layer and handoff to the edit

If the graphics layer is delivered separately (so it can be composited over the live
footage in the edit):

```bash
# Motion graphics on a transparent background, lossless
"$FF" -i graphics.mov -c:v prores_ks -profile:v 4444 -pix_fmt yuva444p10le graphics-alpha.mov

# Overlay onto the edit
"$FF" -i edit.mp4 -i graphics-alpha.mov -filter_complex "[0:v][1:v]overlay=0:0:format=auto" -c:a copy out/edit-with-graphics.mp4
```

In a web/GSAP production, the `bang-motion` skill's `scripts/export-frames.mjs` pipeline
produces frame-by-frame PNGs; the PNG sequence plus alpha is converted to ProRes 4444.
During preview, 6–20 locked seconds are sampled frame by frame and judged **by eye** (text
overflow, collisions, early entry).

## Handoff

- Graphics output is never delivered directly: it passes the `qc.py` gate in the
  `video-post-delivery` skill (duration, frame rate, black frames, audio).
- When the film is finished, the 60/30/15 s and 9:16 versions are derived with
  `derive-versions.sh`; **in the vertical version the typography is recomposed**, not
  cropped.

## Pitfalls

- **Frame-rate confusion.** The reference is 30 fps, our film is 25 fps. If the
  reference's frame counts are copied one-to-one, the rhythm speeds up by 20%; durations
  are converted from seconds to frames.
- **If the font is missing, the browser/renderer silently falls back to a substitute
  font** and the composition breaks. The font file must live under `assets/brand/fonts/`,
  and the preview and the render must see the same font.
- **Getting approval on sample/placeholder text.** If temporary copy is used in the
  animatic, this is stated explicitly; the on-screen copy is the final copy from brief §7.
- **An effect that is beautiful on its own.** A graphics module must be meaningful even
  without the sentence it carries; a module added as ornament makes the film look like a
  "template promo" (that is exactly the reference's trap).
