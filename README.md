# Scaefy Video Production

**A code-generated video production skill pack — engine-neutral, free at its core, and gated by measurements instead of opinions.**

Your coding agent writes the film as code. A timeline renders every frame as a pure
function of time, stills are captured from a real browser, ffmpeg encodes, audio is
mixed, and the delivery passes a quality gate that fails loudly. No timeline editor,
no keyframe dragging, no "looks good to me".

> **Status: pre-release (v0.1.0 in progress).** Skills, tooling, docs, and CI are in
> place and `tools/verify.sh` passes. The bundled example film is landing. Nothing is
> published yet.

---

## See it work

`example/` holds a complete **30-second, 1920x1080, 25 fps** film — a real one, built
for the agency that maintains this pack. It has **zero dependencies**: open
`example/index.html` in a browser and it plays. No build step, no package install, no
network.

```bash
# watch it
open example/index.html

# capture stills and measure them
PUPPETEER_CACHE_DIR="$PWD/.puppeteer-cache" TMPDIR="$PWD/.tmp" \
URL="file://$PWD/example/index.html?clean=1" \
node tools/shots.mjs shots 2 6 12 18 24 28
python3 tools/check-frames.py shots/*.png --theme light

# measure every text box against the safe area, from the DOM
PUPPETEER_CACHE_DIR="$PWD/.puppeteer-cache" TMPDIR="$PWD/.tmp" \
node tools/probe-layout.mjs --safe 0.08 --url "file://$PWD/example/index.html?clean=1" 2 6 12 18 24 28
```

The film's on-screen copy is Turkish and its English subtitles ship alongside it,
because the brand it was made for is Turkish. The pack's own prose is English.

---

## Why this exists

Most "AI video" tooling ties you to one engine, one provider, or a heavy framework.
This pack makes three commitments instead:

1. **Engine-neutral.** A film is built with one engine — HTML + GSAP for one-shot work
   that needs fast iteration, Remotion for data-fed templates that get re-rendered, or
   AI generation for photoreal footage. The pack teaches all three and never mixes them
   inside a single film.
2. **Free and offline at the core.** The default pipeline needs no API key, no account,
   and no network. AI footage is an optional layer you can add, skip, or run locally.
3. **Gated by measurements.** Loudness, true peak, frame integrity, safe-area overflow,
   and determinism are checked by scripts that return a non-zero exit code — not by a
   paragraph asking you to be careful.

---

## The zero-cost guarantee

| Layer | Cost | Network | What it covers |
|---|---|---|---|
| **A · Code-generated graphics** (core) | **Free** | **None** | Kinetic typography, counters, data bars, name cards, logo reveals, end cards, captions, transitions, full motion-graphics films |
| **B · AI footage** (optional) | Free with a GPU, otherwise paid | Yes | Photoreal b-roll, characters, scenes |

Layer B has three paths, and you choose:

| Path | Cost | Hardware | Examples |
|---|---|---|---|
| Local open source | **Free** | GPU required | Wan 2.1/2.2, Hunyuan Video, LTX Video, Flux |
| Free tier | Free (limited) | None | Provider trial credits |
| Paid API | Paid | None | Seedance 2.0, Veo, Kling |

If a brief needs AI footage and you have neither a GPU nor a quota, the agent falls back
to Layer A and **says so** — it never silently connects to a paid service.

---

## Quick start

Requirements: **Node 18+**, **Python 3.10+**, **ffmpeg**. All local, all free.

```bash
git clone <this-repo>
cd scaefy-video-production

# Resolve a working ffmpeg (tests execution, not existence)
FF="$(tools/ffmpeg.sh)" && echo "ffmpeg OK"

# Run every quality gate
bash tools/verify.sh
```

To install as a DSH agent preset:

```bash
mkdir -p ~/.dsh/.agent-presets
cp -R . ~/.dsh/.agent-presets/scaefy-video-production
```

To use the skills with any agent that supports the
[Agent Skills](https://agentskills.io) standard:

```bash
npx skills add <this-repo>
```

---

## Skills

### First-party

| Skill | What it does |
|---|---|
| `brand-asset-intake` | Turns scattered brand assets into verified, machine-readable tokens: palette extraction, WCAG contrast, type scale and safe areas for 16:9/9:16, and a clean asset tree. Refuses to invent a missing logo or colour. |
| `video-motion-graphics` | Builds the graphics layer in code: word-build kinetic typography, portrait mosaics, data and counter bars, name cards, logo reveal, end card — frame-accurate at 25 fps. |
| `video-post-delivery` | Encodes, normalises, subtitles, and QC-checks a master against exact delivery specs, then derives short and vertical versions. Fails loudly rather than shipping a broken file. |

### Vendored (MIT, attributed — see `THIRD_PARTY_NOTICES.md`)

| Skill | Origin |
|---|---|
| `bang-motion` | HTML + CSS + GSAP cinematic motion graphics, by Bang Tutorial |
| `remotion-marketing-video` | Remotion + React marketing video workflow, by Sourabh |

---

## Tooling

| Tool | Purpose |
|---|---|
| `tools/ffmpeg.sh` | Resolves a *working* ffmpeg — tests execution, not existence |
| `tools/shots.mjs` | Captures stills at exact times, awaiting `ready` and `seekAsync` |
| `tools/export-frames.mjs` | Exports a full frame sequence for encoding |
| `tools/check-frames.py` | Black/frozen frames, safe-area overflow, ink coverage, contrast |
| `tools/contact-sheet.py` | Builds a review sheet from frames, in numeric time order |
| `tools/probe-layout.mjs` | Measures real glyph boxes from the DOM — never guess a type size |
| `tools/verify.sh` | Runs every gate in one command |
| `tools/banned-strings.txt` | Blocklist for leakage checks |

The frame tools measure what is measurable and leave taste to a human. The layout probe
reads `Range.getClientRects()` so it reports actual ink bounds regardless of alignment.

---

## Delivery matrix

| Output | Duration | Frame | Codec / settings |
|---|---|---|---|
| Master | 60 s | 1920×1080 or 3840×2160 | H.264 High, yuv420p, 25 fps CFR |
| Event backup | 60 s | same | H.264 yuv420p + AAC, constant frame rate |
| Silent playback | 60 s | same | Master + embedded subtitles |
| Short cut | 30 s | 16:9 | Derived from the master |
| Teaser | 15 s | 9:16 | Recomposed, not cropped |
| Vertical full | 60 s | 1080×1920 | Graphics recomposed for portrait |

Colour space Rec.709 / Gamma 2.4. Audio AAC 48 kHz, 320 kbps stereo.
Loudness target **−14 LUFS integrated**, true peak **≤ −1 dBTP**.

---

## Related work

This pack is deliberately lightweight and permissively licensed. These projects solve
adjacent problems and are worth your attention:

- [**OpenMontage**](https://github.com/calesthio/OpenMontage) — a batteries-included
  agentic video production framework (Python, 100+ tools, 60+ providers), licensed
  **AGPLv3**. Its free path — offline Piper TTS, open archival footage, local GPU
  generation — independently validates the architecture this pack is built on. It is
  *not* a dependency and no code is shared: AGPL and MIT works stay separate.
- [**sub-level/marketing-videos**](https://github.com/sub-level/marketing-videos) — an
  MIT Remotion + AI-footage pipeline with excellent case studies.
- [**pexoai/pexo-skills**](https://github.com/pexoai/pexo-skills) — MIT skills wrapping a
  multi-model cloud generation API.
- [**seedance2-skill**](https://github.com/dexhunter/seedance2-skill) — MIT prompt-writing
  guide for Seedance 2.0, by Dex.

---

## License

MIT — see `LICENSE`. Vendored third-party skills keep their own MIT licences and
attribution; see `THIRD_PARTY_NOTICES.md`.
