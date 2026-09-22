---
name: voiceover-and-audio-mix
description: Turns a script into frame-accurate 25 fps narration cues and a three-layer sound design — music bed, impacts, detail — ducks music under speech and hands delivery a mix at -14 LUFS, -1 dBTP. Use when adding, timing or cueing narration; when choosing recorded or synthetic voice; when sourcing or licensing music; when designing a music bed, impacts or interface sounds; when ducking music under speech; when mixing a film's audio; or when hitting a loudness and true-peak target.
---

# Voiceover and Audio Mix

Audio is the half of the film that is not rendered. This skill covers narration timing, the
sound-design stack, and the loudness handoff. Its measurable promise: **the mix arrives at
the delivery gate already compliant**, so `qc.py` does not fail on audio.

Every command resolves ffmpeg through the repo tool and runs from the project root:

```bash
FF="$(tools/ffmpeg.sh)"     # full path to a working ffmpeg
```

There is no `ffprobe`; read duration and stream layout from `ffmpeg -i`:

```bash
"$FF" -hide_banner -nostdin -i audio/vo/vo-en-raw.wav 2>&1 | grep -E "Duration|Stream"
```

Asset tree this skill reads and writes: `audio/vo/` (voiceover recordings),
`audio/music/` (music and beds), `assets/brand/` (tokens, for any on-screen text that
shares a cue boundary).

## Voiceover sources: recorded vs synthesised

| Source | Cost | Control | Consistency across re-records | Prefer when |
|---|---|---|---|---|
| **Recorded voice** (human) | Session time, talent fee, one cost per re-record | Highest: direction, emphasis, pronunciation, breath, warmth | Low. A new session changes mic, room, distance and energy; the same person months later is audibly a different take | The film carries brand voice, proper names, numbers or emotional weight; the VO is the spine |
| **Synthesised voice** (TTS) | Per character, or free when run locally | Pronunciation via SSML or phoneme edits; no breath, no performance | High. Identical output for identical text and voice model | Copy changes late; many length variants (60/30/15 s) must match; no voice is available; a scratch track is needed before the real record |

Rules:

1. **Lock the voice before timing.** A voice change mid-project (different speaker, different
   TTS model, different settings) **invalidates every previously timed cue**. The words
   still match but the pauses do not, so the cue table must be rebuilt from a new
   `silencedetect` pass.
2. Record or render one file per script section, never one file per word. Section files let a
   single line be replaced without re-timing the whole film.
3. Keep the raw takes in `audio/vo/` next to the timed file. The mix reads the raw take; the
   edit reads the cue table.
4. Both sources are mixed identically: the delivery target does not change because the voice
   is synthetic.

## Script to frame-accurate cues

The cue table is the contract between audio and graphics. Build it in this order.

### 1. Estimate duration from word count

Estimate first, but never ship the estimate. Narration rate is a **parameter the brief
supplies per language**; the English worked example is roughly **2.5–3 words per second**, so
a **60-second film carries roughly 150–180 words** (a 12-second section, 30–36 words).

| Film length | Words at 2.5 w/s | Words at 3 w/s |
|---|---|---|
| 15 s | 38 | 45 |
| 30 s | 75 | 90 |
| 60 s | 150 | 180 |

### 2. Detect the real pauses

The estimate says how long the words should take; the recording says where the pauses
actually are. Measure them:

```bash
"$FF" -hide_banner -nostdin -i audio/vo/vo-en-raw.wav \
  -af "silencedetect=noise=-35dB:d=0.35" -f null - 2>&1 | grep silence
```

Reading the output: each pause prints a start and an end with its duration.

```text
[silencedetect @ 0x...] silence_start: 3.214
[silencedetect @ 0x...] silence_end: 3.741 | silence_duration: 0.527
```

- `noise=-35dB` is the starting threshold. Lower it (to `-45dB`) in a quiet room with a low
  noise floor, raise it (to `-30dB`) when room tone hides the pauses.
- `d=0.35` is the shortest gap treated as a break. Below that, a pause is breath inside a
  sentence and must not become a cue boundary.
- A **segment** is the speech between a `silence_end` and the next `silence_start`. The first
  segment starts at the file's first speech; the last ends at the file's last speech.

### 3. Convert seconds to frames at 25 fps

```text
frame  = seconds × 25                 seconds = frames ÷ 25
```

Convert the cue **start with `floor`** and the cue **end with `ceil`**, so a boundary never
clips the first or last word. A plain `round` is fine for planning, but not for a boundary. Add the section's timeline offset to every frame when the VO
file is one section of a longer film.

Worked example, a 12-second section, offsets applied, at 25 fps:

| Cue | Script line (placeholder) | Speech start | Speech end | Start frame | End frame | Length |
|---|---|---|---|---|---|---|
| VO-1 | `Opening line goes here` | 0.47 s | 3.21 s | 11 | 81 | 70 |
| VO-2 | `Second line goes here` | 3.74 s | 6.06 s | 93 | 152 | 59 |
| VO-3 | `Third line goes here` | 6.62 s | 9.26 s | 165 | 232 | 67 |
| VO-4 | `Closing line goes here` | 9.82 s | 11.94 s | 245 | 299 | 54 |

Reverse check: frame 232 ÷ 25 = 9.28 s, the cue out-point just after the speech ends at
9.26 s. The 11.94 s of speech in 32 words is 2.7 words/second — inside the English band.

### 4. On-screen text changes land on cue boundaries

**A text change, a graphic change and a caption change happen on a cue frame, never at an
arbitrary time.** If a headline should appear "around 6 seconds", it appears on frame 152
(the end of VO-2), not frame 150. This is what makes the film feel written rather than
assembled, and it is what lets the cue table be handed to the graphics and caption skills
unchanged.

## Three-layer sound design

Three layers, each with one job. Every layer is authored against the cue table and the edit's
cut list, not against a stopwatch. Levels are stated **relative to the mixed dialogue**, taken
as the 0 dB reference.

| Layer | Purpose | Typical level vs dialogue | When to omit |
|---|---|---|---|
| **1 · Music bed** | Emotional floor and pace across the whole film | −18 to −24 dB, then ducked a further 8–12 dB while speech is present | The spine is interview audio with real room tone; narration is continuous and a bed would only add density |
| **2 · Transition impacts / whooshes** | Mark structural cuts, section changes and reveals | −12 to −18 dB; transient peak may touch −6 dB | On cuts inside a continuous scene; on every cut (that is the trailer failure) |
| **3 · Tactile / interface detail** | Sell the motion of counters, bars, cards and reveals | −20 to −28 dB; felt rather than heard | On a static frame; where the graphic already reads its own motion |

### Layer 1 is a frame-keyed curve, not a flat level

A single music level for the whole film either buries the voice or disappears. Key the bed
to frames:

| Keyframe | Frames (25 fps) | Gain (× bed level) | Shape |
|---|---|---|---|
| Music in | 0 → 25 | 0.00 → 1.00 | Linear rise over 1 s; never a hard downbeat |
| Duck under VO-1 | 11 → 81 | 1.00 → 0.25, hold, → 1.00 | 6-frame attack (240 ms), 10-frame release (400 ms) |
| Gap | 81 → 93 | 1.00 | Music returns in the pause; never mute it |
| Duck under VO-2 | 93 → 152 | 1.00 → 0.25, hold, → 1.00 | Same shape as VO-1 |
| Music out | 1487 → 1500 | 1.00 → 0.00 | Linear fall over 13 frames (0.5 s) to the last frame |

### Layers 2 and 3 are placed on cuts

- Place an impact on the **cut frame itself**, not near it. A 2-frame offset is audible as
  sloppiness even when it is invisible.
- One impact per structural transition. A whoosh on a graphics module entry, an impact on the
  reveal, silence everywhere else.
- Detail sounds are triggered by a graphic's own animation frames (the first frame of a
  counter, the frame a bar reaches its target), so sound and motion share one clock.

## Music sourcing and the bed

### Licensing is a first-class concern

Every track needs a **recorded licence and source**, logged alongside the asset. Put a note
next to the file and one row in a manifest:

```text
audio/music/track-source.wav
audio/music/track-source.LICENSE.txt      # licensee, title, composer, source URL, licence type, date, proof file
audio/music/music-log.csv                 # one row per track: file,title,composer,source,licence,territory,term,notes
```

- **"Royalty-free" still has terms.** It usually means no per-play fee, not "no conditions".
  Check attribution, monetisation, broadcast, paid event screening, territory and term.
- A track cleared for an online video is **not automatically cleared** for a paid event
  screening. Record what the licence does **not** allow, in the same note.
- An asset with no recorded source is not usable, regardless of where it came from. This is
  the same gate as the brand-asset publication decision: no licence, no publish.

### Building a bed longer than the source track

`acrossfade` and `adelay` chains are **unreliable** for this. The crossfade arithmetic belongs
in a Python script that computes sample offsets and overlap lengths explicitly. The reasons:

- `acrossfade=d=2` on two 32 s inputs produces **62 s, not 64 s** — the overlap is consumed.
  Chaining a third input consumes another overlap, and every junction is forced to the same
  `d`, so the overlap cannot vary.
- `adelay` + `amix` does **not trim the tail**. The output is longer than the film and the
  extra tail is silent; that silent tail enters the loudness gating window, drags the
  integrated value down, and makes the file length disagree with the edit.
- `amix` **normalises by default** (`normalize=1`), so each added copy lowers the level —
  four copies are 12 dB down. `normalize=0` fixes the level, but then the overlapping copies
  sum (+6 dB at each junction) unless the fades are exactly complementary.
- `afade`'s default `tri` (linear) fade-out plus a linear fade-in sums to 1, so the junction
  holds level. Switching either to `exp` or `qsin` breaks that sum and leaves a dip or a bump.

Compute the plan first, in integers:

```python
SR = 48000
source_s, bed_s, xfade_s = 32.0, 60.0, 2.0
step = source_s - xfade_s                      # 30.0 s: where the next copy starts
starts, t = [], 0.0
while t < bed_s:
    starts.append(t)
    t += step
# -> [0.0, 30.0]: copy 1 covers 0-32 s, copy 2 covers 30-60 s
# (copy start in seconds, copy start in samples, source end_sample for that copy)
plan = [(s, int(round(s * SR)), int(round(min(source_s, bed_s - s) * SR))) for s in starts]
# -> [(0.0, 0, 1536000), (30.0, 1440000, 1440000)]
```

Each copy must be at least `step + xfade` long, or the junction has no overlap to fade
across. With the plan above the two copies already reach 60 s exactly, so the outer `atrim` in
the command below is only a guard against a longer source:

```bash
"$FF" -hide_banner -nostdin -y -i audio/music/track-source.wav \
  -filter_complex "\
[0:a]atrim=start_sample=0:end_sample=1536000,asetpts=N/SR/TB,afade=t=out:st=30:d=2[c0]; \
[0:a]atrim=start_sample=0:end_sample=1440000,asetpts=N/SR/TB,adelay=30000|30000,afade=t=in:st=30:d=2[c1]; \
[c0][c1]amix=inputs=2:duration=longest:normalize=0,atrim=start_sample=0:end_sample=2880000,afade=t=out:st=58:d=2[bed]" \
  -map "[bed]" -ar 48000 -ac 2 audio/music/bed-60s.wav
```

A Python bed builder that writes the finished WAV directly is equally valid and easier to
audit, because the offsets are integers in one place rather than spread across a filter
graph.

## Ducking and mixing

Ducking carves space for narration. Duck the **music**, never the voice, and never mute the
music — a bed that disappears sounds broken. Typical duck depth is **8–12 dB** (linear
0.40–0.25) under speech, with the music returning to bed level in every gap.

### Sidechain-style ducking (reacts to the voice)

```bash
"$FF" -hide_banner -nostdin -y \
  -i audio/music/bed-60s.wav \
  -i audio/vo/vo-en-raw.wav \
  -filter_complex "\
[1:a]aresample=48000,asplit=2[vo][sc]; \
[0:a][sc]sidechaincompress=threshold=0.05:ratio=8:attack=15:release=300:makeup=1[ducked]; \
[ducked][vo]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.891[mix]" \
  -map "[mix]" -ar 48000 -ac 2 out/mix-pre.wav
```

- `threshold=0.05` is linear (about −26 dBFS): the point where the voice starts to push the
  bed down. With `ratio=8`, a bed sitting 12 dB above the threshold is pulled roughly
  10–12 dB — the target range.
- `attack=15` ms is fast enough to catch a consonant onset; slower and the first syllable is
  masked. `release=300` ms is slower than the gap between words, so the bed does not jump
  back up on every breath. **Too fast a release is what pumping is.**
- `makeup=1` means no makeup gain: the point is the duck, not a boost.
- `amix=...:normalize=0` keeps the voice at its recorded level. `alimiter=limit=0.891`
  (≈ −1 dBFS) is a guard against an accidental overshoot, **not** the true-peak compliance
  step — that is measured on the final mix below.

### Explicit volume envelope (reacts to nothing)

The envelope is authored from the cue table, so it is deterministic and frame-exact. Generate
a gain file of the same length and sample rate as the bed — 1.0 outside the cues, 0.25
inside, with linear ramps of 240 ms at every boundary — and multiply:

```bash
"$FF" -hide_banner -nostdin -y \
  -i audio/music/bed-60s.wav \
  -i audio/music/bed-60s-envelope.wav \
  -filter_complex "[0:a]aresample=48000[bed];[1:a]aresample=48000[env];[bed][env]amultiply,alimiter=limit=0.891[m]" \
  -map "[m]" -ar 48000 -ac 2 out/music-ducked.wav
```

Tradeoff: the envelope survives a re-record unchanged, but it cannot respond to an unscripted
loud moment the way the sidechain does. A one-line approximation with the `volume` filter is
`volume=0.25:enable='between(t,0.47,3.21)'` per cue — but a hard gain step clicks, so it must
be ramped before it is usable.

## Loudness and true peak

Delivery target: **−14 LUFS integrated, true peak ≤ −1 dBTP**, AAC 48 kHz stereo 320 kbps.

Why it exists: event screens and social platforms **normalise** playback to their own
reference. An over-loud master is simply turned down and loses the impact the loudness was
meant to buy, and it clips after lossy encoding. An under-loud master is turned up, and its
noise floor comes with it. The target is the level that survives normalisation.

Measure with the delivery script, not by ear. It runs `ebur128=peak=true` over the file and
prints integrated LUFS, loudness range and true peak:

```bash
skills/video-post-delivery/scripts/loudness.sh out/mix-pre.wav --check
```

Fix with the two-pass `loudnorm` script (measure, then linear normalise; video is copied):

```bash
skills/video-post-delivery/scripts/normalize-loudness.sh out/mix-pre.wav out/mix-final.wav
```

Three rules that are easy to get wrong:

1. **Loudness is measured on the final mix, not on stems.** Stem levels do not sum linearly —
   music is ducked under speech and effects sit on cuts — so a compliant VO stem plus a
   compliant music stem can produce a non-compliant mix. Measure the mixed file.
2. **True peak is a separate check from integrated loudness.** Integrated loudness is a gated
   average over the programme; true peak is the maximum inter-sample value, caught by a
   single transient (a whoosh or an impact). A mix can read exactly −14.0 LUFS and still
   exceed −1 dBTP. Passing one says nothing about the other.
3. **Re-measure after encoding.** AAC can move the true peak by a few tenths of a dB. The
   final check runs on the delivered master, not on the pre-encode WAV.

Pass/fail criterion: **PASS when |integrated − (−14.0)| ≤ 0.5 LU and true peak ≤ −1.0 dBTP.**
Anything else is a FAIL: `loudness.sh --check` exits 1, and `qc.py` prints "MUST NOT SHIP".
Leave the target's own headroom in place rather than mastering to the limit, so the encoded
file still passes.

## Silent playback

A film may play with **no sound** at an event. Any narration carrying meaning must also be
readable, which means the caption text is the script text, timed from the same cue table:
caption in/out frames equal cue frames.

Hand off to `kinetic-captions-and-subtitles` for caption styling and the character-per-second
ceiling. For placement, render a text-only variant (captions on, graphics off) and capture one
still at each cue frame, then measure it with the `--theme dark` check (light ink on a dark
ground). The checker reads the capture time from the `t<seconds>_<centiseconds>` filename
convention, so the loop below names each still accordingly:

```bash
# Cue frames 11, 81, 152, 232 at 25 fps -> 0.44, 3.24, 6.08, 9.28 s
for f in 11 81 152 232; do
  "$FF" -hide_banner -nostdin -y -i out/captions-only-1080p.mp4 \
    -vf "select=eq(n\,$f)" -fps_mode passthrough \
    "shots/t$(printf '%d_%02d' $((f / 25)) $(((f * 4) % 100))).png"
done
python3 tools/check-frames.py shots/t*.png --theme dark \
  --text-windows 0-12,23-30,57-60 --text-everywhere
```

This reports ink coverage inside the caption windows, content touching the frame edge (clipped
glyphs) and safe-area violations — the measurable part of caption placement. The judgement
part stays with a human.

## Handoff

| Upstream / downstream | What crosses the boundary |
|---|---|
| `video-brief-and-storyboard` | The script, the language, and the speaking-rate parameter for that language |
| `video-motion-graphics` | The cue table: text and module changes land on cue frames |
| `kinetic-captions-and-subtitles` | The same cue table, for caption in/out frames |
| `video-post-delivery` | The finished mix, for `loudness.sh`, `normalize-loudness.sh` and the `qc.py` gate |

## Pitfalls

- **Timing cues against the estimate and never checking the recording.** The word count says
  12 seconds; the take says 13.4. Cue the real file with `silencedetect` and keep the
  estimate only as a pre-record planning number.
- **Re-recording the VO after the edit is locked.** The pauses move, so every cue, caption
  and text change moves with them. Lock the voice and the cue table before the edit is
  finished; if the VO must change, budget a re-time.
- **A bed built with `acrossfade` that silently shortens the track or leaves the tail
  silent.** The overlap is consumed (62 s, not 64 s) and an untrimmed `amix` leaves silence
  past the last frame. Compute offsets and overlap lengths in Python and pass exact samples.
- **Normalising stems instead of the mix.** Compliant stems are not a compliant mix. The
  measurement is taken on the mixed file.
- **Treating integrated loudness as sufficient and ignoring true peak.** One impact can push
  the true peak over −1 dBTP while the integrated value still reads −14.0 LUFS.
- **Music that masks consonants.** Duck too little, or duck with an attack slower than about
  30 ms, and the words survive but the intelligibility does not.
- **Sound effects on every cut.** An impact on each transition turns a film into a trailer.
  Reserve layer 2 for structural cuts.
- **Assuming "royalty-free" means "no conditions".** Missing attribution or a screening
  restriction is a licensing failure, not a stylistic one.
