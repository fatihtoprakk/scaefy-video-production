---
name: brand-asset-intake
description: Turns logo, brand colours, fonts and handles into verified machine-readable tokens — palette extraction, contrast checks, type scale and safe-area maths. Use when a video or graphics job needs real brand assets before rendering; when extracting a palette from a logo or reference frame; when checking lower-third or headline contrast; when computing safe areas and type sizes for 16:9 or 9:16; or when deciding whether a film is a brand film or only a concept film.
---

# Brand Asset Intake

Graphics production starts with brand files. This skill turns scattered assets into
**verified tokens** and refuses to silently proceed with missing assets.
A wrong logo, an invented colour or an unreadable headline ruins good editing too.

## When to use

- When a video/graphics job needs the real logo, colours, fonts and handles before it starts
- When extracting a palette from a logo or a reference frame
- When verifying lower-third / headline / CTA contrast
- When computing type sizes, safe areas and hierarchy for 16:9 and 9:16
- When deciding whether a film counts as a "brand film" or a "concept film"

## Asset tree contract

The following directories are expected at the project root (create them if missing):

```text
assets/brand/logo/      # logo: SVG > EPS/PDF > transparent PNG (min 2000 px wide)
assets/brand/fonts/     # licensed font files (.ttf/.otf/.woff2) + licence note
assets/brand/colors.json# brand colours (schema below)
assets/brand/tokens.json# generated tokens (written by this skill, never hand-edited)
assets/brand/tokens.css # the same tokens for the web/HTML engine
media/archive/          # real footage/photo archive (interviews, office, team, summit)
media/inbox/            # newly arrived footage, not yet triaged
audio/vo/               # voice-over recordings
audio/music/            # music and jingles
out/                    # delivery outputs (including versions)
```

`colors.json` schema:

```json
{
  "source": "logo.svg + brand guide p.4",
  "brand": {
    "primary": "#0F2A22",
    "accent":  "#E4572E",
    "ink":     "#F4F1EA",
    "bg":      "#0B1F19"
  },
  "notes": "primary from the logo, accent from the guide"
}
```

Rule: every colour records its **source**. A colour whose source cannot be shown is marked
`"derived: <reason>"`. That way the later question "where did we get this colour" is never
left unanswered.

## Workflow

1. **Collect the assets.** If something is missing, state the list plainly; do not invent it.
   No final card is produced before the logo file arrives.
2. **Validate the logo.** `logo-inspect` steps: is it vector (SVG/EPS/PDF), is it transparent,
   does it read at the smallest use, is clear space defined, is there a dark/light background
   variant. If only raster exists, check resolution and the alpha channel.
3. **Extract the palette.**
   ```bash
   python3 skills/brand-asset-intake/scripts/extract-palette.py \
     assets/brand/logo/*.svg assets/brand/logo/*.png --colors 6 --json out/palette.json
   ```
   If brand colours exist in `colors.json`, **they win**; extraction is for verification/suggestion only.
4. **Verify contrast.** For headline and lower-third text:
   ```bash
   python3 skills/brand-asset-intake/scripts/check-contrast.py \
     --fg "#F4F1EA" --bg "#0B1F19" --large
   ```
   Thresholds: normal text ≥ 4.5:1, large headline (≥ 24 px bold) ≥ 3:1. Lower-third text
   always counts as normal text.
5. **Generate tokens.**
   ```bash
   python3 skills/brand-asset-intake/scripts/make-tokens.py \
     --colors assets/brand/colors.json --out assets/brand/tokens.json
   ```
   If real colours are not available yet, **provisional** tokens may be generated; in that case
   the output is marked `"provisional": true` and the film counts as a "concept film".
6. **Hand off.** Graphics production runs in `video-motion-graphics`; audio/encode/QC in the
   `video-post-delivery` skill.

## Typography and safe area

The scale is derived from a 1080p reference; apply ×2 for 4K and ×0.85 for 9:16 (1080×1920)
(because the vertical frame is narrower, headline line length is preserved).

| Role | 1080p (16:9) | 2160p (16:9) | 1080×1920 (9:16) |
|---|---|---|---|
| Headline | 64–82 px | 128–164 px | 54–70 px |
| Emphasis (short) | 92–112 px | 184–224 px | 78–95 px |
| Supporting text | 34–42 px | 68–84 px | 29–36 px |
| Lower third | 38–48 px | 76–96 px | 34–42 px |

- Safe area: at least **8%** from the edges (86 px at 1080p; 154 px in a vertical frame).
- A headline is at most two lines; line length should not exceed ~28 characters at 1080p.
- For silent viewing on an event screen, every key idea stays readable on screen for **at least 1.5 s**
  (38 frames at 25 fps).
- Text animation: 6–10 frames of opacity + 12–20 px of vertical movement.
- Use `font-variant-numeric: tabular-nums` for number counters; otherwise the width
  changes and the composition jitters.

## Publication gate (publish decision)

If the following assets are missing, the production is labelled a **concept film** and is not
published as a brand film:

1. The real logo (vector or transparent high-resolution PNG)
2. Brand colour codes (with their source)
3. The brand font or its usage guide
4. A verified website address and Instagram handle
5. Written confirmation of music and voice-over usage rights
6. Publication permission for the footage used

This item closes the "we don't have it but it looks good" trap: a concept film
can be shown, but it cannot be published as a brand film.

## Pitfalls

- **Redrawing the logo in code.** A freely drawn logo is always wrong; use only the real
  file (copy the SVG path).
- **Flattening a transparent PNG onto a background.** Transparent pixels are not counted when
  extracting a palette; otherwise the background colour is mistaken for a "brand colour"
  (the script masks this).
- **Sampling colour from a screenshot.** Video compression shifts colour; take the palette
  from the logo/guide.
- **Using 16:9 type sizes in 9:16.** The same size overflows in a vertical frame; drop the scale.
- **Treating a provisional token as final.** If `tokens.json` contains `provisional: true`,
  it must be updated with the real assets before delivery.
