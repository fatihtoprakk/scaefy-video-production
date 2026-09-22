# Example film — Scaefy

A complete **30-second, 1920x1080, 25 fps** film, built with this pack. It is a real
film for the agency that maintains the pack, not a placeholder, and it doubles as the
worked example every skill in the repository refers to.

**Zero dependencies.** Open `index.html` in a browser and it plays — no build step, no
`npm install`, no network, no CDN.

```bash
open index.html          # macOS
xdg-open index.html      # Linux
```

---

## Why this film has no dependencies

Every other engine in this pack (GSAP via `bang-motion`, Remotion via
`remotion-marketing-video`) pulls in a runtime. This example deliberately pulls in
nothing, for three reasons:

1. **It proves the engine contract, not a library.** The film exposes the same
   `window.OPENER` surface the capture and export tools expect — `DURATION`, `W`, `H`,
   `ready`, `seek`, `seekAsync`, `FOOTAGE` — and drives every frame from a single
   `render(t)` function. That contract is the pack's actual interface; GSAP is one way
   to satisfy it, not the definition of it.
2. **It keeps the repository MIT-clean.** GSAP ships under the GSAP Standard Licence,
   which is free to use but is not MIT. Vendoring it into an MIT repository would mix
   licences for no benefit here.
3. **It is the strongest form of the offline promise.** A cloner with Node, Python and
   ffmpeg but no network can still watch, capture, measure and encode this film.

If you want GSAP's timeline ergonomics, load the `bang-motion` skill — it is vendored
and ready.

---

## The film

Agency overview, six beats, 750 frames.

| # | Frames | Seconds | Content |
|---|---|---|---|
| 1 | 0–100 | 0.00–4.00 | **Rasyonel Çözümler Üretiyoruz** — word build |
| 2 | 100–250 | 4.00–10.00 | WordPress, Laravel, SEO, E-ticaret |
| 3 | 250–400 | 10.00–16.00 | Yapay Zeka & Bot Çözümleri, API Çözümleri |
| 4 | 400–550 | 16.00–22.00 | **Çeyrek asırlık tecrübe** + the four real client names |
| 5 | 550–675 | 22.00–27.00 | **Projenizi konuşalım** + scaefy.com |
| 6 | 675–750 | 27.00–30.00 | End card — the real logo + scaefy.com |

**Every on-screen claim comes from the brand's own website**: the positioning line, the
service list, the credibility claim, the client names, the address. No statistic appears
in this film that the brand does not already publish. That is the pack's no-fabrication
rule, applied to its own example.

### Language

On-screen copy is **Turkish**, because the brand is Turkish and the film is meant to be
usable on the real site. `captions/en.srt` carries **English** subtitles so the film also
reads for an international audience and demonstrates the caption skill.

All on-screen strings live in one `COPY` object near the top of the `<script>` block.
Translate that object and you have a different-language film.

### URL parameters

| Parameter | Effect |
|---|---|
| *(none)* | Autoplay and loop |
| `?clean=1` | Suppress autoplay and all UI — what the export tools use |
| `?debug=1` | HUD with the current time, frame number, active beat and a scrub slider |
| `?textonly=1` | Hide the decorative layers so only text remains, for safe-area measurement |

---

## Verify it

The film is authored at a fixed 1920x1080 and scaled to fit the window, so every
measurement in the source is in real 1080p pixels.

```bash
# 1. resolve a working ffmpeg
FF="$(tools/ffmpeg.sh)" && echo "ffmpeg OK"

# 2. capture a still from each beat
PUPPETEER_CACHE_DIR="$PWD/.puppeteer-cache" TMPDIR="$PWD/.tmp" \
URL="file://$PWD/example/index.html?clean=1" \
node tools/shots.mjs shots 2 6 12 18 24 28

# 3. check the frames: blank frames, edge bleed, safe-area overflow, ink coverage
python3 tools/check-frames.py shots/*.png --theme light \
  --accent-hue 16 --text-windows 0-30

# 4. measure every text box against the 8% safe area, from the DOM
PUPPETEER_CACHE_DIR="$PWD/.puppeteer-cache" TMPDIR="$PWD/.tmp" \
node tools/probe-layout.mjs --safe 0.08 \
  --url "file://$PWD/example/index.html?clean=1" 2 6 12 18 24 28

# 5. a review sheet, in numeric time order
python3 tools/contact-sheet.py review/sheet.jpg shots/*.png --cols 3
```

Puppeteer is not installed in this repository. Install it in a working copy before
running steps 2 and 4:

```bash
npm install puppeteer
PUPPETEER_CACHE_DIR="$PWD/.puppeteer-cache" npx puppeteer browsers install chrome-headless-shell
```

---

## Encode it

```bash
FF="$(tools/ffmpeg.sh)"

# full frame grid: 750 JPEG frames at 25 fps
PUPPETEER_CACHE_DIR="$PWD/.puppeteer-cache" TMPDIR="$PWD/.tmp" \
URL="file://$PWD/example/index.html?clean=1" \
node tools/export-frames.mjs frames 25 30 --size 1920x1080

# encode. The colour-range flags matter: JPEG frames are full-range, and without
# them the output is yuvj420p, which the delivery gate rejects.
"$FF" -y -framerate 25 -i frames/f_%05d.jpg \
  -vf "scale=in_range=full:out_range=limited" \
  -c:v libx264 -profile:v high -level 4.2 -preset slow -pix_fmt yuv420p \
  -color_range tv -colorspace bt709 -color_primaries bt709 -color_trc bt709 \
  -r 25 -fps_mode cfr -crf 18 out/example-master.mp4

# the pack's own encode path, if you prefer it
bash skills/video-post-delivery/scripts/encode-master.sh out/example-master.mp4 out/example-1080.mp4 --height 1080

# the delivery gate
python3 skills/video-post-delivery/scripts/qc.py out/example-1080.mp4 \
  --spec landscape-1080 --expect-duration 30
```

`qc.py` exits non-zero on any failure, so it drops straight into CI.

---

## Brand tokens

`assets/brand/tokens.json` records every value **and where it came from**. The accent
colour is the brand's own published `#FF6B35`, read from the site.

**A real defect this example caught:** `#FF6B35` on white measures **2.84:1**, which
fails the 4.5:1 threshold for normal text *and* the 3:1 threshold for large text. The
first draft of this film used it for kickers and emphasised words. Running the pack's
own `check-contrast.py` against the film's own palette caught it, and the film now uses
two tones:

| Token | Value | Ratio on white | Use |
|---|---|---|---|
| `accent` | `#FF6B35` | 2.84:1 | **Decoration only** — progress bar, card edge |
| `accentInk` | `#C2410C` | 5.18:1 | **Text** — kickers, emphasised words |

That is the point of measuring rather than eyeballing: the brand's colour is preserved
where it is safe, and a derived ink carries the text.

---

## Adapting this for your own brand

1. Replace `assets/brand/logo/` with your real logo file. **Do not redraw it** — the
   pack's rule, learned the hard way, is that a redrawn logo never matches.
2. Run `brand-asset-intake` to derive tokens from your logo and site, then verify every
   text colour with `check-contrast.py` before it goes on screen.
3. Rewrite the `COPY` object.
4. Update the beat boundaries in `BEATS` — they are frame indices, and the table above
   shows the arithmetic.
5. Re-measure. A layout that passes in one aspect ratio says nothing about another.

The Scaefy name and logo in this directory are trademarks of their owner and are **not**
covered by this repository's MIT licence. Replace them in any fork.
