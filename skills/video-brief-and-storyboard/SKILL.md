---
name: video-brief-and-storyboard
description: Turns a vague request into a decision-complete brief, beat sheet, storyboard and timed animatic, with an approval gate before any render spend. Use when starting a new video; when turning a brief or a liked reference video into a plan; when writing a beat sheet or storyboard; when building an animatic; when deciding scene count or pacing; or when approval is needed before full production.
---

# Video Brief and Storyboard

Nothing is rendered before the edit is decided. **Changing an edit decision is cheap;
re-rendering is expensive.** This skill converts a vague request into a brief, the brief
into beats, the beats into a storyboard, and the storyboard into a **timed animatic** that
a human approves. Full production starts only after that approval.

The output is a decision-complete plan: every scene has an id, an in/out frame, on-screen
text, an audio cue and a stated source for every claim.

## Brief contract

A brief is a contract, not a mood board. Before any planning, these fields are pinned
down. An empty field is a question for the human, not a gap to fill by guessing.

| Field | What it pins down | Bad | Good |
|---|---|---|---|
| **Goal** | What changes after watching | "promote the brand" | "a first-time visitor books a demo" |
| **Audience** | Who, and what they already know | "everyone" | "technical buyers who know the category" |
| **Platform / aspect** | Where it plays, how it is framed | "social" | "event screen 16:9, plus a 9:16 cut" |
| **Duration** | Target seconds + tolerance | "short" | "30 s, ±1 s" |
| **Call to action** | Exact action + destination | "learn more" | "go to `<URL>`, one action only" |
| **Assets** | Available vs missing, with rights | "we have footage" | the two tables below, filled |
| **Tone** | 3 adjectives, and what it must not feel like | "modern" | "plain, technical, calm; never hyped" |
| **Hard constraints** | Deadline, legal, mandatory copy, forbidden claims | unstated | "no pricing on screen; legal line mandatory" |

**Rule: a missing asset is reported, never invented.** If the logo file, a colour, a
statistic or a rights confirmation is absent, it appears in the *Missing* table and the
production states its fallback. A film built on an invented asset is a concept film, not a
brand film (see the `brand-asset-intake` publication gate).

Copy-pasteable template — write it to `brief.md` at the project root:

```markdown
# Brief — <project>

- **Goal:** <one sentence: what changes after watching>
- **Audience:** <who, what they already know>
- **Platform / aspect:** <event screen | web | Reels | TikTok> / <16:9 | 9:16 | 1:1>
- **Duration:** <seconds> (tolerance ±<seconds>)
- **Call to action:** <exact action + destination>
- **Tone:** <three adjectives>; must not feel like <anti-tone>
- **Hard constraints:** <deadline, legal, mandatory copy, forbidden claims>
- **Spoken / caption language:** <language, language>

## Assets

### Available
| Asset | Path | Rights | Notes |
|---|---|---|---|
| <what> | media/archive/<file> | cleared | <origin, resolution> |

### Missing (reported, never invented)
| Missing asset | Blocks | Fallback |
|---|---|---|
| <what> | <scene id> | <what is shown instead, or hold the scene> |

## Sources for on-screen claims
| Claim | Source | Verified by |
|---|---|---|
| <the exact number or sentence> | <document, page or URL> | <who confirmed it> |

## Agent decisions (autonomous mode only)
| Decision | Gate skipped | Default used | How to reverse |
|---|---|---|---|
```

Once approved, a change to any field **re-opens the gate**: the affected beats are
re-timed, and if the change touches copy, scene count or duration, the animatic is
re-approved before production resumes.

## Structure rules

1. **One main idea per scene.** If a scene needs "and", it is two scenes.
2. **Scene changes every 2–5 seconds** (50–125 frames at 25 fps), unless the brief
   explicitly asks for slow or cinematic pacing. No scene runs past 5 s without a visual
   change: a cut, a camera move, or a typographic change.
3. **The hook lands in the first 1–2 seconds** (frames 0–50). The first frame already
   carries the premise; there is no logo-only intro unless the brief asks for one.
4. **Every claim on screen is traceable to a source.** No source, no number, no
   superlative. This is the same rule as `brand-asset-intake` and the `qc.py` gate, applied
   before the render instead of after it.
5. **Text obeys the limits another skill owns.** Type scale, line length and safe area come
   from `brand-asset-intake`; on-screen copy is planned to read with the sound off, so a
   key idea is never on screen for less than the silent-viewing minimum. Planning the
   minimum here is cheaper than discovering an unreadable beat in the animatic.

Default narrative arc: **hook → reveal → mechanism → proof → CTA**. Beat count follows
from the arc and the duration, not the other way around.

Deviate deliberately, and say so in the brief:

| Situation | Deviation |
|---|---|
| Single-message social cut (≤ 15 s) | hook → proof → CTA; drop the mechanism |
| Demo or tutorial | mechanism first; the hook is the problem the mechanism solves |
| Testimonial-led | proof leads; the hook is the customer's own sentence |
| Brand film, no hard sell | CTA may be a soft end card; proof is atmospheric |
| Looping social asset | the last beat visually matches the first frame |

## Beat sheet

A beat sheet is a table with one row per scene. Column set: `#`, start, end, duration in
**frames and seconds**, scene id, on-screen text, audio/VO cue. Times are seconds with two
decimals; frames are integers. The frame column is the one the renderer consumes.

Worked example — a 30-second film at 25 fps, 7 beats, 7 scenes:

| # | Scene | Start (s) | End (s) | Dur (s) | Dur (frames) | On-screen text | Audio / VO cue |
|---|---|---|---|---|---|---|---|
| 1 | S1 | 0.00 | 2.00 | 2.00 | 50 | `40 HOURS OF EDITING` | VO line 1 in at 0.30 |
| 2 | S2 | 2.00 | 7.00 | 5.00 | 125 | `THERE IS A FASTER WAY` | music enters at 2.00 |
| 3 | S3 | 7.00 | 12.00 | 5.00 | 125 | `WRITE THE FILM AS CODE` | VO line 2 |
| 4 | S4 | 12.00 | 17.00 | 5.00 | 125 | `EVERY FRAME IS A FUNCTION OF TIME` | VO line 3 |
| 5 | S5 | 17.00 | 22.00 | 5.00 | 125 | `SAME INPUT, SAME FRAME` | VO line 4; counter beat |
| 6 | S6 | 22.00 | 26.00 | 4.00 | 100 | `START YOUR FIRST FILM` | VO line 5; music builds |
| 7 | S7 | 26.00 | 30.00 | 4.00 | 100 | `<BRAND>` + `<URL>` | music resolves; VO out |

Arc mapping: hook S1 · reveal S2 · mechanism S3–S4 · proof S5 · CTA S6–S7. Every scene
runs 2–5 s; the hook is inside the first 2 s.

The arithmetic that must close:

```text
frames = seconds × 25          (25 fps, constant)

S1  2.00 × 25 =  50     0 →  50
S2  5.00 × 25 = 125    50 → 175
S3  5.00 × 25 = 125   175 → 300
S4  5.00 × 25 = 125   300 → 425
S5  5.00 × 25 = 125   425 → 550
S6  4.00 × 25 = 100   550 → 650
S7  4.00 × 25 = 100   650 → 750

sum of durations: 50+125+125+125+125+100+100 = 750 frames
750 ÷ 25 = 30.00 s  → equals the brief's target
```

If the sum does not equal the target, adjust the middle beats, never the hook or the CTA.
A frame-rate mismatch is the most common arithmetic error: a reference video at 30 fps
copied frame-for-frame runs ~20% fast at 25 fps — convert its durations to seconds first,
then to frames.

## Storyboard

The beat sheet says *when*; the storyboard says *what is in frame*. One panel per scene is
the minimum; add a panel at every beat boundary and at every camera move. As a rule of
thumb, **one panel per 2–4 seconds of screen time**: a 30-second film gets 8–12 panels,
not 30. More panels than that is an edit already, and it is reviewed as an animatic.

Each panel must capture, in text:

| Panel field | Content |
|---|---|
| Panel id | `P03` (unique, stable, referenced by the beat sheet) |
| Scene id + time range | `S4`, 12.00–17.00 s (frames 300–425) |
| Framing | shot size and angle (`medium close`, `wide`, `top-down`) |
| Subject / action | what is in frame and what it does |
| Camera move | `static`, `slow push`, `pan left`, `type build` |
| On-screen text | the exact copy, marked `[PLACEHOLDER]` if not final |
| Duration | seconds and frames |
| Audio cue | VO line, music change, silence |
| Notes | crop safety for 9:16, generated-footage need, asset dependency |

Review panels before the animatic: check that the story reads without audio, that no scene
carries two ideas, and that every panel's duration is legal (2–5 s). Assemble the panels
into one sheet so rhythm and composition are judged at a glance rather than one file at a
time — see the animatic gate below, which uses the same tool on captured frames.

## Animatic gate

An animatic is the whole film at real durations with placeholder visuals and temp audio.
It is not a mood board and not a slideshow of final frames: it is the **edit**, cheaply.

Build it as a single HTML timeline with the same contract the capture tools expect:
`window.OPENER.ready` true when the timeline is loaded, and `window.OPENER.seek(t)` or
`window.OPENER.seekAsync(t)` setting the frame for a given time. Placeholder visuals are
flat blocks or labelled rectangles in the project's tokens; temp audio is a scratch VO or
a royalty-free bed — never the final music.

```bash
# 1. Capture the frame at every beat boundary (outDir first, then seconds)
PUPPETEER_CACHE_DIR="$PWD/.puppeteer-cache" TMPDIR="$PWD/.tmp" \
URL="file://$PWD/animatic/index.html?clean=1" \
node tools/shots.mjs review/animatic-shots 0.0 2.0 7.0 12.0 17.0 22.0 26.0 29.9

# 2. Measure every text box against the safe area (real glyph boxes, not block boxes)
PUPPETEER_CACHE_DIR="$PWD/.puppeteer-cache" TMPDIR="$PWD/.tmp" \
node tools/probe-layout.mjs --selector .hero 2.0 7.0 12.0 17.0 22.0 26.0

# 3. Check the frames: text present in its window, nothing clipped, nothing blank
python3 tools/check-frames.py review/animatic-shots/*.png --theme dark \
  --text-windows 2-7,7-12,12-17,17-22,22-26,26-30

# 4. Assemble the review sheet (tiles are stamped with capture time, numeric order)
python3 tools/contact-sheet.py review/animatic-sheet.jpg \
  review/animatic-shots/*.png --cols 4 --title "30 s animatic — beat boundaries"
```

`check-frames.py` measures what is measurable (frame integrity, ink coverage, safe-area
violations, edge clipping) and leaves taste to the human. Its `--theme` follows the
project's tokens — `dark` for light ink on a dark ground, `light` for the reverse. The
contact sheet is the artifact the reviewer reads alongside the timed playback.

**Full production does not start until the animatic is approved.** The reviewer is
approving exactly four things:

| Approved | Meaning |
|---|---|
| **Pacing** | each scene's duration feels right at real speed |
| **Beat boundaries** | every cut is at the agreed frame |
| **On-screen copy** | the exact sentences, and that they are final, not placeholder |
| **Scene count** | no scene is added, merged or dropped after this point |

Approval is recorded in the brief (`## Agent decisions` is not the place for human
sign-off; an approved animatic gets a dated line: `Animatic approved — <date>, rev <n>`).
A later change to copy, scene count or duration invalidates the approval and the animatic
is re-cut. Re-timing inside an approved beat does not.

## Gate taxonomy

Which decisions stop for a human, and which the agent makes alone:

| Human sign-off required (STOP) | Agent decides alone |
|---|---|
| The brief fields: goal, audience, platform/aspect, duration, CTA, tone, hard constraints | Beat internal timing (in/out frames inside an approved beat) |
| Every on-screen claim and its source | Transition type, easing, entry direction |
| Final on-screen copy (locked text) | Placeholder copy for the animatic, clearly marked `[PLACEHOLDER]` |
| Scene count and beat boundaries (the animatic gate) | Panel count and storyboard rendering style |
| Provisional vs final brand tokens (concept film decision) | Temp audio choice (scratch VO or royalty-free bed) |
| Music/VO rights and publication permission | File and folder naming, which tool to run |
| Any spend or render beyond the animatic | Frame-accurate time conversion (seconds → frames) |

Escalate immediately, without deciding: a missing asset; two constraints that cannot both
hold (duration vs scene count); a claim with no source; unclear rights.

**When the user says "decide for me"** (autonomous mode), the agent proceeds — but it
still **records every decision it made and which gate it skipped**. Each row goes into the
`## Agent decisions` table in `brief.md`: the decision, the gate skipped, the default used,
and how to reverse it. The animatic is still built and still reviewed; autonomous mode
skips the human *answer*, not the *gate*. The film carries the mark until the skipped gates
are closed.

## Handoff

The approved brief, beat sheet and storyboard are the input to every downstream skill. Each
consumes a specific slice:

| Downstream skill | What it consumes |
|---|---|
| `brand-asset-intake` | the Available/Missing asset tables, the aspect ratios, and whether provisional tokens are acceptable → `assets/brand/tokens.json`, `tokens.css` |
| `video-motion-graphics` | scene ids, in/out frames, on-screen copy, and which beats carry graphics windows |
| `ai-cinematic-broll` | the shots needing generated footage, their durations and aspect, and the tone/grade intent |
| `voiceover-and-audio-mix` | the audio/VO cue column: line text, in-frame, music changes, duck points |
| `kinetic-captions-and-subtitles` | the locked on-screen copy with per-beat in/out times → caption timing and CPS limits |
| `multiformat-recomposition` | the aspect ratios and per-scene framing notes, and which scenes are crop-safe for 9:16 |
| `video-post-delivery` | final duration and 25 fps, plus the delivery matrix that skill owns (codec, colour space, loudness and true-peak targets) |

## Pitfalls

- **Approving copy that was never final.** Placeholder text approved in the animatic
  becomes the shipped sentence. Mark every placeholder `[PLACEHOLDER]` and re-open the gate
  when the real copy arrives.
- **Planning more scenes than the duration supports.** Eight scenes in 15 seconds means
  under 2 s each: nothing is readable. Scene count is a function of duration and the 2–5 s
  rule, not of how many ideas exist.
- **Treating a reference video's frame counts as portable.** A 30 fps reference copied
  frame-for-frame runs ~20% fast at 25 fps. Convert the reference's durations to seconds,
  then to frames.
- **Letting the animatic use the final music.** A finished score makes weak pacing feel
  intentional and hides dead beats. Temp audio only; the real mix comes after approval.
- **Skipping the brief and discovering a missing asset after the render.** The missing
  logo, colour or rights confirmation surfaces at the end card, when the render is already
  paid for. Report it in the Missing table before planning.
- **Silently guessing a field.** A guessed duration or aspect ratio is discovered only in
  the delivery matrix. An empty brief field is a question, not a default.
