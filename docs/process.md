# Process

The end-to-end playbook: from a request to a published film. Each stage produces
an artifact that the next stage consumes, and two of them are approval gates.

---

## The pipeline

```
brief ──► intake ──► beats ──► storyboard ──► animatic ──► [APPROVE]
                                                     │
                          footage / graphics ◄───────┘
                                   │
                              sound ──► edit ──► grade
                                   │
                        [APPROVE] ──► delivery ──► screen test
```

Two gates exist because two decisions are expensive to reverse: the **animatic**
(before generation and render spend) and the **master** (before versions are cut).

---

## Stage by stage

| # | Stage | Owner skill | Artifact |
|---|---|---|---|
| 1 | Brief | `video-brief-and-storyboard` | `brief.md` with goal, audience, platform, duration, aspect, CTA, asset inventory |
| 2 | Asset intake | `brand-asset-intake` | `assets/brand/tokens.json`, verified palette, type scale, safe areas |
| 3 | Beats | `video-brief-and-storyboard` | Beat sheet with frame-accurate boundaries |
| 4 | Storyboard | `video-brief-and-storyboard` | Panels per scene, plus a contact sheet |
| 5 | Animatic | `video-brief-and-storyboard` | Timed preview at real durations with temp audio |
| — | **Gate: approve the animatic** | — | Pacing, beat boundaries, on-screen copy, scene count |
| 6 | Footage | `ai-cinematic-broll` or archival | Approved stills, then clips |
| 7 | Graphics | `video-motion-graphics` | Modules: kinetic type, counters, cards, reveal, end card |
| 8 | Sound | `voiceover-and-audio-mix` | VO cues, music bed, mix at target loudness |
| 9 | Captions | `kinetic-captions-and-subtitles` | Frame-timed captions, SRT/VTT |
| 10 | Edit and grade | `video-motion-graphics` | Assembled master |
| — | **Gate: approve the master** | — | Then versions are cut |
| 11 | Formats | `multiformat-recomposition` | 16:9 / 9:16 / 1:1 as the brief requires |
| 12 | Delivery | `video-post-delivery` | Encoded masters, versions, QC report |
| 13 | Screen test | — | Playback on the real target device |

---

## Commands

```bash
# 1. Resolve a working ffmpeg once
FF="$(tools/ffmpeg.sh)" && echo "ffmpeg OK"

# 2. Capture stills at chosen times for review
PUPPETEER_CACHE_DIR="$PWD/.puppeteer-cache" TMPDIR="$PWD/.tmp" \
URL="file://$PWD/index.html?clean=1" \
node tools/shots.mjs shots 1.5 12.0 30.0

# 3. Measure the frames
python3 tools/check-frames.py shots/*.png --theme light

# 4. Build a review sheet
python3 tools/contact-sheet.py review/sheet.jpg shots/*.png --cols 4

# 5. Measure text placement from the DOM (never by eye)
PUPPETEER_CACHE_DIR="$PWD/.puppeteer-cache" TMPDIR="$PWD/.tmp" \
node tools/probe-layout.mjs --safe 0.08 1.5 12.0 30.0

# 6. Export the full frame sequence for encoding
PUPPETEER_CACHE_DIR="$PWD/.puppeteer-cache" TMPDIR="$PWD/.tmp" \
URL="file://$PWD/index.html?clean=1" \
node tools/export-frames.mjs frames 25 60 --size 1920x1080

# 7. Gate the delivery
python3 skills/video-post-delivery/scripts/qc.py out/master.mp4 \
  --spec landscape-1080 --expect-duration 60

# 8. Or run every gate at once
bash tools/verify.sh --video out/master.mp4
```

---

## Working rules

**Approve the cheap thing.** A still costs a fraction of a clip; an animatic
costs a fraction of a render. Approve in that order.

**One main idea per scene.** If a scene needs two sentences to explain, it is two
scenes.

**On-screen copy is final copy.** Placeholder text that survives into an approved
animatic has a habit of surviving into the master. If a line is not approved, mark
it as a placeholder and say so.

**Measure, do not estimate.** Type size, safe-area overflow, loudness, and true
peak are all measurable. Guess only where measurement is impossible.

**Nothing ships past a failing gate.** `qc.py` returning a failure means the file
is not delivered. That is the whole point of having it.

---

## Autonomy

When the user says "decide for me", the preference gates are skipped — but the
agent still records what it decided and which gate it skipped. Autonomy changes
who decides, not whether the decision is written down.

Safety and integrity gates are never skipped, in any mode:

- an unverified statistic does not go in the film
- a missing brand asset is reported, not invented
- a failing `qc.py` blocks delivery
