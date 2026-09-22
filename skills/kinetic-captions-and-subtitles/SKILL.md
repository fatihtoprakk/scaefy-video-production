---
name: kinetic-captions-and-subtitles
description: Authors, times and ships captions and subtitles — readability limits (characters per line, CPS), frame-accurate cues, SRT/VTT authoring and validation, burn-in versus sidecar and localisation. Use when adding captions or subtitles; when a video must read with the sound off; when authoring, timing or validating SRT or VTT; when choosing burn-in or sidecar; when styling word-level captions; when localising a film; or when checking caption speed, line length and placement.
---

# Kinetic Captions and Subtitles

A film must read with the sound off. At an event, on a muted social feed, or for a deaf
viewer, the captions are the film — not an accessory added after the grade.

This skill owns the caption **cue table, design and placement**. `video-post-delivery`
owns the delivery gate and the silent-playback variant; its burn-in example is a delivery
shortcut, and the authoring rules here are the source of truth for the text.

## Two families, one decision

The word "subtitle" hides two different jobs. Decide which one the film needs before
writing a single cue.

| | **Subtitles** | **Kinetic captions** |
|---|---|---|
| Job | translate dialogue for a viewer who does not speak the language | carry the film's own words as a design element for a viewer with the sound off |
| Trigger | foreign-language version, festival or archive delivery | muted social feed, event screen, autoplay |
| Timing | cue-level, from the voiceover recording | word-level, from the voiceover recording |
| Placement | bottom-anchored, fixed, player-controlled | composed into the frame, may move |
| Motion | none; a hard cut between cues at most | entry and exit per word or phrase |
| Styling | restrained, one weight, one size | designed, part of the film's type system |
| Language | target language only | the film's own language |
| Failure mode | too fast to read | competes with the film |

A film rarely needs both **in the same shot**. When a cut needs both — a translated
festival version that also plays muted — decide per shot: kinetic captions in the
graphic sections, translated subtitles over dialogue. Never stack two caption layers in
one band, and never run a translated cue and a kinetic cue in the same frames.

## The readability contract

Captions are readable when they satisfy measurable constraints. These are per-language
values, and **the brief must supply them for the target language**. The English column
below is the worked example only; it is not a universal constant.

| Constraint | English (worked example) | `<lang>` (from the brief) |
|---|---|---|
| Maximum characters per line | 42 | must be supplied |
| Maximum lines on screen | 2 | must be supplied |
| Characters per second (CPS) ceiling | 17 | must be supplied |
| Minimum on-screen duration | 1.0 s (25 frames) | must be supplied |
| Maximum on-screen duration | 7 s | must be supplied |
| Minimum gap between cues | 2 frames (80 ms) | must be supplied |

Rules:

- Count characters **including spaces**, and count the whole cue when computing CPS:
  `CPS = characters / duration_in_seconds`.
- Enforce the ceiling on **every cue**, never on the film average. A long cue that
  contains a fast burst averages under the ceiling while the burst flashes.
- A cue under the minimum duration is not readable; a cue over the maximum is a
  paragraph. Split at a phrase boundary instead of shrinking the type.
- For scripts that are not Latin (CJK, Arabic, Devanagari, Thai), the brief must state
  whether a "character" is a code point or a width unit, and whether lines break between
  words or between characters.
- A cue that fits the box but breaks the CPS ceiling is still a defect. Box fit is
  geometry; CPS is time.

## Frame-accurate timing

The film is 25 fps. **One frame is exactly 40 ms**, so every cue boundary must be a
multiple of 40 ms. Cue times come from the voiceover cues produced by
`voiceover-and-audio-mix` — from the actual recording, never from the script's word
count.

Arithmetic:

```text
frame n covers [n / 25, (n + 1) / 25) seconds, i.e. [n x 40 ms, (n + 1) x 40 ms)
snapped start  n_start = floor(t_start x 25)     start = n_start / 25
snapped end    n_end   = ceil(t_end x 25)        end   = n_end / 25        (exclusive)
frames on screen = n_end - n_start
```

Snap **outward**: floor the start and ceil the end, so a boundary never clips the first or
last word. This is the same rule `voiceover-and-audio-mix` uses, which means the caption
cue table is the voiceover cue table with text attached — every caption change lands on a
cue frame. A plain `round` is fine for planning but not for a boundary, and rounding the
two ends toward each other can collapse a cue to zero frames.

Worked timing table (voiceover cues in, snapped cue times out):

| Voiceover cue | Cue time (s) | Frames | Snapped (s) | SRT timestamp |
|---|---|---|---|---|
| V1 start "the whole picture" | 3.42 | floor(85.5) = 85 | 3.400 | `00:00:03,400` |
| V1 end | 5.87 | ceil(146.75) = 147 | 5.880 | `00:00:05,880` |
| V2 start "roles, expectations" | 6.05 | floor(151.25) = 151 | 6.040 | `00:00:06,040` |
| V2 end | 8.94 | ceil(223.5) = 224 | 8.960 | `00:00:08,960` |

Cue 1 runs 3.400–5.880 s (2.48 s, 62 frames) and holds 17 characters, so CPS ≈ 6.9 —
inside the contract. The gap to cue 2 is 0.160 s (4 frames), above the 2-frame minimum.

**Word-level timing is worth the extra effort for kinetic captions, and not for
translated subtitles.** A kinetic caption lands each word as it is spoken, so the eye is
led by the voice and the caption feels part of the film. A translation does not preserve
word boundaries, word order or word count, so word-level animation would assert a
correspondence that does not exist — and it adds motion to text the viewer is already
reading at speed.

## Authoring SRT and VTT

Both formats are plain UTF-8 text. Write them by hand or generate them, but keep one cue
table per language (`captions.en.srt`, `captions.<lang>.srt`) so the timing is authored
once and translated into it.

SRT — comma decimal separator, a sequence number, one blank line between cues:

```text
1
00:00:03,400 --> 00:00:05,880
the whole picture

2
00:00:06,040 --> 00:00:08,960
roles, expectations
```

VTT — a `WEBVTT` header, dot decimal separator, cue settings after the timestamps:

```text
WEBVTT

NOTE English captions, 25 fps, safe area 8%

00:00:03.400 --> 00:00:05.880 line:-3 position:50% size:80% align:center
the whole picture

00:00:06.040 --> 00:00:08.960 line:-3 position:50% size:80% align:center
roles, expectations
```

The VTT cue settings that matter for placement:

| Setting | Values | Use |
|---|---|---|
| `line` | `-3` (lines from the bottom) or `88%` | lift the cue out of the bottom edge and out of platform UI chrome |
| `position` | `50%` (horizontal) with an optional `,line-left` anchor | horizontal anchor for the cue box |
| `size` | `80%` | cap the cue box width so lines break where the contract wants |
| `align` | `center`, `start`, `end` | text alignment inside the box; `start` follows reading direction |
| `vertical` | `rl`, `lr` | vertical writing, for scripts composed vertically |
| `region` | a named `REGION` block | reuse one placement across a whole film |

Rules:

- **UTF-8 without a BOM.** A BOM makes some parsers read the first cue number as text and
  drop the first cue. Check with `file -I captions.en.srt` — it must report `charset=utf-8`.
- SRT has **no styling**, and VTT styling is limited (cue settings, plus `b`/`i`/`u` and a
  `STYLE` block that most players ignore). Anything beyond position and basic emphasis —
  a brand font, a scrim, word-level motion — belongs in the burn-in or in the composition
  itself, not in the sidecar.
- Keep line breaks at phrase boundaries. Never break after an article or a preposition,
  and never hyphenate to make a line fit.

Validate every cue before it reaches an encode. This reads the file as UTF-8, so a bad
encoding fails loudly, and it enforces the contract for the values you pass in:

```bash
python3 - captions.en.srt <<'PY'
import pathlib, re, sys
MAX_CHARS, MAX_LINES, MAX_CPS, MIN_DUR, MAX_DUR, FPS = 42, 2, 17.0, 1.0, 7.0, 25
text = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")   # a BOM or bad encoding fails here
cues = re.findall(
    r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3}) --> (\d{2}):(\d{2}):(\d{2})[,.](\d{3})\n(.*?)(?=\n\n|\Z)",
    text, re.S)
bad = 0
for h1, m1, s1, ms1, h2, m2, s2, ms2, body in cues:
    start = int(h1)*3600 + int(m1)*60 + int(s1) + int(ms1)/1000
    end   = int(h2)*3600 + int(m2)*60 + int(s2) + int(ms2)/1000
    lines = [l for l in body.strip().splitlines() if l.strip()]
    chars, dur = sum(len(l) for l in lines), end - start
    cps = chars / dur if dur > 0 else float("inf")
    fail = []
    if any(len(l) > MAX_CHARS for l in lines): fail.append("line over %d chars" % MAX_CHARS)
    if len(lines) > MAX_LINES: fail.append("more than %d lines" % MAX_LINES)
    if cps > MAX_CPS: fail.append("CPS %.1f > %.1f" % (cps, MAX_CPS))
    if dur < MIN_DUR: fail.append("duration %.2fs < %.2fs" % (dur, MIN_DUR))
    if dur > MAX_DUR: fail.append("duration %.2fs > %.2fs" % (dur, MAX_DUR))
    for t in (start, end):
        if abs(t * FPS - round(t * FPS)) > 1e-3: fail.append("off frame boundary at %.3fs" % t)
    if fail:
        bad += 1
        print("  FAIL %s:%s:%s,%s  %s" % (h1, m1, s1, ms1, "; ".join(fail)))
print("%d cues, %d FAIL" % (len(cues), bad))
sys.exit(1 if bad else 0)
PY
```

The same script parses VTT, because the separator class `[,.]` accepts both decimal
styles.

## Burn-in versus sidecar

| | **Burn-in** | **Sidecar** |
|---|---|---|
| Where the text lives | pixels inside the video | a subtitle stream or a `.vtt`/`.srt` file |
| Renders identically everywhere | yes | no — depends on player support |
| Can be turned off | no | yes |
| Translatable after encode | no, it needs a re-render | yes, add a track or swap the file |
| Reachable by assistive technology | no, it is an image | yes, it is real text |
| Styling and motion | full — font, scrim, word-level motion | position and basic emphasis only |
| Cost of a text change | a full re-render | a file swap |
| Use when | event screen, muted social feed, one fixed language, kinetic captions | web player, multiple languages, toggleable subtitles, an accessibility requirement |

The two are not exclusive: burn in for the event master and attach a sidecar to the web
master. Never burn in one text and ship a sidecar that says something different.

Burn in — `subtitles=` with a `force_style` that sets font, size, outline and bottom
margin. `MarginV` is in script pixels, so it must be at least the 8% safe margin (86 px at
1080p); 96 keeps a two-line caption inside the safe area. `<YourFont>` is a placeholder —
substitute the family name from `assets/brand/tokens.json`, not a filename:

```bash
"$(tools/ffmpeg.sh)" -i out/master-60s-1080p.mp4 \
  -vf "subtitles=captions.en.srt:fontsdir=assets/brand/fonts:original_size=1920x1080:force_style='FontName=<YourFont>,FontSize=34,Outline=1,Shadow=0,MarginV=96,Alignment=2'" \
  -c:v libx264 -profile:v high -pix_fmt yuv420p -r 25 -fps_mode cfr \
  -c:a copy out/master-60s-1080p-captioned.mp4
```

The `subtitles` filter needs libass. Confirm the build has it before planning a burn-in:

```bash
"$(tools/ffmpeg.sh)" -hide_banner -filters | grep -w subtitles
```

Sidecar — embed `mov_text` into the MP4 with a language tag. `<lang>` is an ISO 639-2/B
three-letter code:

```bash
"$(tools/ffmpeg.sh)" -i out/master-60s-1080p.mp4 -i captions.<lang>.srt \
  -map 0:v:0 -map 0:a? -map 1:0 \
  -c:v copy -c:a copy -c:s mov_text \
  -metadata:s:s:0 language=<lang> -metadata:s:s:0 title="<lang>" \
  -disposition:s:0 default \
  out/master-60s-1080p-sub.mp4
```

For a track that only translates on-screen foreign dialogue, use
`-disposition:s:0 forced`. `mov_text` supports no styling; for the web, ship the `.vtt`
beside the MP4 and reference it from the page:

```html
<track kind="captions" srclang="<lang>" src="captions.<lang>.vtt" default>
```

## Designing kinetic captions

Kinetic captions are a graphics module, so they are composed like one: every visible
change is a function of time, and the type style comes from the brand tokens.

Primitives:

| Primitive | What it does | Use for |
|---|---|---|
| **Word build** | words gain opacity in sequence, each on its own frame window | a sentence that must be read as a whole |
| **Highlight sweep** | the phrase is already present; colour or weight moves word by word at speech rate | emphasising a spoken line without changing layout |
| **Pop** | one word goes 100% → 106% → 100% scale over 4–6 frames with opacity | a single emphasis, at most once per section |
| **Rail** | a fixed baseline or thin rule the captions sit on; words fade in place or slide along it | a long stretch of footage, where a jumping baseline resets the eye |

Motion rules:

1. **Caption motion must be calmer than the film's headline motion.** Headlines move
   6–10 frames of opacity plus 12–20 px of travel (`brand-asset-intake`,
   `video-motion-graphics`). A caption stays at or below that: opacity-led, at most 8 px
   of movement, no rotation, no scale above 106%, never per-letter animation.
2. **Exit faster than entry.** 4–6 frames, opacity only. A slow exit collides with the
   next cue and the viewer reads two lines at once.
3. **One move per word.** Never combine scale, travel and colour on the same word.
4. **Keep the baseline fixed across cues in a shot.** A caption that jumps vertically
   between cues costs the viewer a re-fixation on every line.
5. **One caption style for the whole film** — one family, one weight, one size. The
   display face and the brand accent belong to the headline. If a caption borrows the
   headline's scale or face, it becomes the film's most animated element and competes
   with the film instead of describing it.
6. **Emphasis by weight or a single accent colour**, at most one word per cue, never by
   size. Do not carry meaning by colour alone; pair it with weight or a marker.
7. Captions are read while the film continues. Calm is not a style preference here; it is
   what makes the caption readable at reading speed.

## Placement and collision

The default safe area is an **8% margin**; at 1080p that is x 154–1766, y 86–994. The
safe area stops text from being clipped — it does not stop text from colliding with the
film's own text. Reserve bands, one text layer per band:

| Band | 1080p y range | Contents |
|---|---|---|
| Headline | 86–560 | the film's own headlines and titles |
| Lower third | 700–860 | name cards, captions for speakers |
| Caption | 880–994 | one or two lines of captions |
| Clearance | ≥ 40 px between the lower-third and caption bands | never occupied |

If a lower third and a caption would land in the same frames, move the lower third up or
suppress it for that shot. The logo stays out of the caption band: a lower-right logo
must sit above y 860.

Measurement procedure:

```bash
# 1) Captions composed in the film: measure the real glyph boxes at each cue time.
PUPPETEER_CACHE_DIR="$PWD/.puppeteer-cache" TMPDIR="$PWD/.tmp" \
  node tools/probe-layout.mjs --safe 0.08 --selector .caption 3.40 5.88 6.04 8.96

# 2) Capture stills at the cue boundaries.
PUPPETEER_CACHE_DIR="$PWD/.puppeteer-cache" TMPDIR="$PWD/.tmp" \
  URL="file://$PWD/index.html?clean=1" node tools/shots.mjs shots 3.40 5.88 6.04 8.96

# 3) Full composite pass: --text-everywhere silences the out-of-window warning.
python3 tools/check-frames.py 'shots/*.png' --text-everywhere
```

`probe-layout.mjs` reads `Range.getClientRects()`, so it reports ink bounds, not block
boxes — use it whenever the captions exist as DOM text. When they are burned in with
`ffmpeg`, the geometry is set by `FontSize` and `MarginV`, and the stills plus
`check-frames.py` are the measurement.

**The `--theme dark` text-only pass** isolates the captions from the footage. Render the
caption layer over a solid dark ground — the composition's own clean flag, or a black
plate for a burn-in:

```bash
"$(tools/ffmpeg.sh)" -f lavfi -i "color=c=black:s=1920x1080:r=25" \
  -vf "subtitles=captions.en.srt:fontsdir=assets/brand/fonts:original_size=1920x1080:force_style='FontName=<YourFont>,FontSize=34,Outline=1,Shadow=0,MarginV=96,Alignment=2'" \
  -t 12 -c:v libx264 -pix_fmt yuv420p -fps_mode cfr out/caption-plate.mp4

"$(tools/ffmpeg.sh)" -i out/caption-plate.mp4 -ss 3.40 -frames:v 1 out/plate-cue1.png
python3 tools/check-frames.py out/plate-cue1.png --theme dark --text-everywhere
```

Under `--theme dark`, ink is light and low-saturation (luminance > 195, saturation < 0.22),
so the pass counts only the white caption pixels. Running the same frames with the default
`--theme light` over footage would count every bright pixel in the shot as ink and hide a
caption that is out of the band. Use the dark pass to measure the caption's own ink
percentage, bounding box and safe-area violations; use the composite pass to confirm the
caption survives the real background.

## Multi-language and localisation

What changes per language:

| Dimension | What changes | What to do |
|---|---|---|
| CPS ceiling | languages differ in reading speed and word length | take the value from the brief; never reuse the English number |
| Characters per line | a 42-character line is generous in English and cramped in German | take the value from the brief; re-break the lines |
| Text expansion | a translation is often longer than the source, sometimes by a third | budget for it, shorten the source copy or split the cue; never shrink the type to fit |
| Reading direction | right-to-left scripts (Arabic, Hebrew, Farsi, Urdu) reverse alignment and punctuation | set the cue direction and alignment; a left-anchored caption becomes right-anchored |
| Font coverage | a font that covers English does not cover the target script | verify coverage before choosing the font |
| Line breaking | CJK breaks between characters, Thai has no spaces between words | follow the script's rules; do not rely on a Latin word-break heuristic |

A font must actually contain the glyphs. A missing glyph renders as a blank box, or the
renderer silently substitutes a fallback font and every metric you measured changes —
line breaks, CPS and placement all shift. **No automated check in this repository catches
this**, because `check-frames.py` measures ink and a blank box is still ink. Verify the
target language visually: render a pangram or the full cue table and read the glyphs, and
have a speaker of the language confirm them. If the brand font lacks the script, the brief
must supply a licensed fallback for that script (`brand-asset-intake`), and the fallback
is stated in the handoff, never silently substituted.

Timecodes are language-independent. Author the cue table once from the voiceover, then
translate the text into it. Retiming per language is allowed only inside the gap between
cues and must still land on frame boundaries.

## Accessibility beyond captions

- **Reading speed is the contract.** A cue over the CPS ceiling is unreadable even when it
  fits the box. Test the fastest passage in the film, not the average.
- **Contrast is against the moving background**, not the average frame. Sample the
  brightest and busiest frame behind the caption band and hold the normal-text threshold
  of 4.5:1 (`brand-asset-intake`). An outline buys a little contrast; over a bright, busy
  shot the real fix is a scrim — a solid or gradient panel at 60–80% opacity, matching the
  lower-third panel rule. In a burn-in, `BorderStyle=3` with a semi-transparent
  `BackColour` draws that panel.
- **Never place captions over faces, over the film's own text, or over a high-detail
  area.** Move the band or add the scrim; do not simply darken the whole frame.
- **Do not carry emphasis by colour alone.** Pair an accent colour with weight or a marker.
- **Keep line breaks at phrase boundaries.** A break after an article or a preposition
  costs a re-read.
- **Captions are not the only carrier of information.** Captions carry sound to a deaf
  viewer; a viewer who cannot see the screen needs the same information in the narration.
  Any content that is only on screen and is needed to understand the film — a number, a
  name card, a URL — must also be spoken in the narration or audio description. Hand that
  requirement to `voiceover-and-audio-mix`; a caption does not satisfy it.
- **No flashing or rapid caption motion.** Fast word motion is a photosensitivity risk;
  keep the caption calmer than the film and honour reduced-motion in a web composition.

## Handoff

- Cue times come from the actual voiceover recording: `voiceover-and-audio-mix` owns the
  recording and its cue table.
- Caption type, accent colour and scrim opacity come from `assets/brand/tokens.json`
  (`brand-asset-intake`); captions are composed as a graphics module
  (`video-motion-graphics`), never as a copy of the headline style.
- The captioned master is encoded, loudness-normalised and gated by
  `video-post-delivery`; that skill owns the silent-playback delivery variant.
- Vertical and short cuts are recomposed in `multiformat-recomposition`. The caption band
  is re-placed for the new frame — a 9:16 frame has 154 px top and bottom margins and
  platform UI chrome at the bottom, so the band moves up. Captions are never inherited by
  cropping.
- Run the repository gates before delivery: `bash tools/verify.sh` (it enforces the
  no-Turkish-characters language gate and the determinism gate on film sources).

## Pitfalls

- **Timing derived from an estimate.** Cues typed from the script's word count or from the
  animatic's planned timings never match the recording — breaths, retakes and a slower read
  all move the words. Author cue times against the actual voiceover, and re-snap every cue
  after a re-record.
- **CPS computed per caption instead of per second of speech.** A long cue that contains a
  fast burst averages under the ceiling while the burst flashes. Check every cue, not the
  film average, and split the cue at a phrase boundary when a passage accelerates.
- **Burning in and then needing a second language.** Burn-in is irreversible; the pixels
  are the film, and a second language means a second master. If more than one language is
  plausible, ship a sidecar, or burn in for the event screen and attach a sidecar to the
  web master.
- **A font without the target language's glyphs.** Blank boxes, or a silent fallback that
  changes the metrics and breaks the line breaks and the CPS you measured. Verify the
  language visually before delivery.
- **Captions inside the safe area but on top of the film's own lower third.** Both are
  inside the safe area and they still collide. Reserve bands and enforce one text layer per
  band.
- **Captions styled so heavily they become the film's most animated element.** The viewer
  watches the caption instead of the film. Caption motion is the calmest text motion in the
  film.
- **A BOM in the SRT.** The first cue number is read as text and the first cue disappears.
  Save as UTF-8 without a BOM and check with `file -I`.
- **Cue ends not snapped to frames.** The last frame flickers or the cue outlives its
  speech. Every boundary is a multiple of 40 ms.
