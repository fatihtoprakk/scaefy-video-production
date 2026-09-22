---
name: ai-cinematic-broll
description: Produces photoreal or stylised generated footage — b-roll, characters and scenes — via a provider-agnostic pipeline with a look bible and provider-neutral prompts. Use when a brief or storyboard needs generated footage, b-roll, characters or scenes; when one character must stay consistent across shots; when approved stills must become motion; when writing image or video model prompts; when choosing local or cloud generation; or when reviewing generated footage for defects.
---

# AI Cinematic B-Roll

Generated footage is one layer of a film, never the film. It fills the shots that cannot
be captured — a location that does not exist, a scale that cannot be built, a moment that
already passed — and it is judged by the same rule as every other layer: it is accepted by
a measured check, not by "looks good".

## The architectural rule

**Provider-agnostic craft lives in this skill; provider-specific syntax lives in an
adapter under `providers/<provider>/`.**

Everything here — the look bible, the stills-first pipeline, the prompt skeleton, the
camera vocabulary, the defect checklist — must work identically whether the user generates
locally on their own GPU or through a paid cloud API. No model name, sampler, seed syntax,
resolution string or weight-file reference is written by this skill. Those belong to the
adapter. When an adapter for the chosen provider does not exist, ask for the target
provider and read its documentation; never invent parameter syntax.

## The three provider paths

| Path | Cost | Hardware | Examples |
|---|---|---|---|
| Local open source | **Free** | GPU required (roughly 12 GB VRAM and up; more for long or high-resolution clips) | Open-weight families: Wan, Hunyuan Video, LTX-Video, Flux (stills) |
| Free tier | Free, limited (quota, watermark, resolution or length cap) | None | Provider trial credits |
| Paid API | Paid per generation or per second of output | None | Seedance, Veo, Kling — named as examples only, never as a default |

Choose the path from the brief, not from habit:

1. **GPU available and local weights allowed** → local open source. Free, private, slow,
   and only as good as the installed model.
2. **No GPU but a quota exists** → free tier for drafts, paid only for locked final shots.
3. **Neither GPU nor quota** → do not generate.

**Fallback rule.** If a brief needs generated footage and the user has neither a GPU nor a
quota, fall back to code-generated graphics, typography and archival footage — and **say
so**, in plain words, in the delivery notes. Never silently connect to a paid service.
Before spending any quota, state the shot list and the estimated number of generations.

## Look bible

`out/look-bible.md` locks visual consistency before anything is generated. One look bible
per film, not per shot, and it is approved before the first generation. It is the document
every prompt is written against and the reference every generated frame is judged against.

| Field | What it fixes |
|---|---|
| Grade and colour treatment | Contrast curve, highlight and shadow bias, saturation ceiling, delivery in Rec.709 |
| Lens and depth-of-field character | Focal length band, aperture feel, bokeh shape, distortion, whether the look is clean or imperfect |
| Palette | The project's brand tokens as the anchor; generated footage must sit inside that palette, not beside it |
| Texture and grain | Grain amount and size, halation, compression character, how clean the image is allowed to be |
| Lighting logic | Key direction, hardness, colour temperature, practical sources, time of day |
| Motion language | How the camera moves and how fast; the shutter feel; whether motion is smooth or handheld |
| Never do this | The short list of looks, moves and cliches this film does not use |

```markdown
# Look bible — <film>

Grade: <contrast curve, highlight/shadow bias, saturation ceiling, Rec.709 delivery>
Lens: <focal band, aperture feel, bokeh, distortion>
Palette: <brand tokens used as the anchor; the generated footage sits inside them>
Texture: <grain amount and size, halation, compression character>
Lighting: <key direction, hardness, colour temperature, practicals, time of day>
Motion: <camera language, speed band, shutter feel, handheld or locked>
Never: <banned looks, moves, cliches>
```

## Character and subject consistency

Identity drifts because the model has no memory. Every generation re-samples the face from
noise, so a character generated twice from the same words is two different people. The
usual causes: no reference at all, a single reference reused at every angle, references
lit differently from each other, and prompt drift where age, wardrobe or feature words
change between shots.

**Reference sheet.** Build one per recurring subject under
`media/archive/generated/<subject-id>/reference/`:

- 4–6 angles: front, three-quarter left, three-quarter right, profile, and back where a
  shot needs it.
- One lighting setup across the whole sheet.
- Neutral expression, no occlusion — no hand over the face, no sunglasses, no hair across
  the eyes.
- Identical wardrobe and hair in every tile.
- Plain background, no scene detail competing for the model's attention.

**Anchor every shot.** Each prompt names its reference asset and that asset's role. A shot
with no identity anchor is a new character by definition, however carefully the words are
reused.

**Approval rule.** An identity anchor is approved **as a still** before it is animated.
Never animate an unapproved face; a face approved only after the clip exists has already
cost the clip.

**Platform restriction.** Many hosted models reject photorealistic human faces in uploaded
reference images, and some reject any uploaded image containing a real-looking person. The
brief must account for this before a batch is paid for, and pick one of three routes:

1. A non-photoreal treatment — stylised, illustrated or animated look — where the
   reference is accepted.
2. Text-only character generation, accepting drift and confining the subject to single
   shots.
3. A local model, where a photographic reference is allowed.

State the chosen route in the look bible. Also state the likeness rule: a generated face
that resembles a real, identifiable person is not used, and consent terms come from the
brief.

## Stills-first pipeline

A still costs a fraction of a video clip — often one to two orders of magnitude in money
and in time. Approve the frame before paying for motion. A rejected still costs one
generation; a rejected clip costs the whole clip.

1. Write the look bible and the shot recipe (below) first.
2. Generate a batch of still candidates per shot. Vary composition, lens and lighting —
   **not** the identity.
3. Build a contact sheet for review:
   ```bash
   python3 tools/contact-sheet.py out/review/<shot-id>-sheet.jpg \
     media/inbox/generated/<shot-id>/stills/*.png --cols 5
   ```
4. Review the sheet with a human. Approve, reject or re-roll. Nothing proceeds without an
   explicit approval line per still.
5. **Lock the approved stills** to `media/archive/generated/<shot-id>/locked/` and record
   the path in the shot recipe. The locked still is the identity anchor for the clip.
6. Animate with image-to-video: the locked still is the first or reference frame. Identity
   comes from the still; motion comes from the prompt.
7. If the model cannot accept an image, approve the still anyway and reuse its description
   word for word in the video prompt.

The locked still is also the QC reference: every generated clip is compared against the
still it came from.

## Shot recipe contract

Fill this table before generating anything. One row per shot, no exceptions.

| Shot id | Subject | Action | Camera move | Duration (s / frames) | Aspect | Reference assets | Audio intent | Acceptance notes |
|---|---|---|---|---|---|---|---|---|

Worked example at 25 fps:

| Shot id | Subject | Action | Camera move | Duration | Aspect | References | Audio intent | Acceptance notes |
|---|---|---|---|---|---|---|---|---|
| B01 | City skyline at dawn | Light shifts; traffic moves far below | Slow push in, locked horizon | 4.0 s / 100 f | 16:9 | none (environment only) | Low drone, distant traffic | No people, no text, horizon level, no flicker |
| B02 | `<SUBJECT-A>`, mid shot | Walks left to right, glances off camera | Track left, same speed as walk | 6.0 s / 150 f | 16:9 | `<SUBJECT-A>` identity anchor + wardrobe still | Footsteps, room tone | Face matches the anchor at 0 s and at 6 s; hands correct; wardrobe unchanged |
| B03 | Hands on a device | Types two keystrokes, settles | Static, shallow focus | 3.0 s / 75 f | 16:9 | Product still | None | No extra fingers; screen content unreadable (real text is overlaid in code) |
| B04 | Valley at golden hour | Clouds move; grass moves in wind | Slow orbit, 30 degrees | 10.0 s / 250 f | 16:9 | none | Wind, no music | No cuts inside the clip; terrain does not morph; split into beats per the timing breakdown |

Frames are always written as seconds x 25. The duration column is the contract with the
edit; a clip delivered at another length is conformed or regenerated, never stretched
silently.

## Prompt structure

Write one prompt per shot from the recipe. The skeleton is provider-neutral; the adapter
maps each field onto that provider's parameter names.

```text
subject and identity : <who or what, wardrobe, distinguishing features, age band>
environment          : <place, time of day, weather, background depth>
action and motion    : <what moves, in which direction, at what speed>
camera behaviour     : <shot size> + <move> + <speed> + <stability>
timing breakdown     : <only for shots over ~8 s, beat by beat>
transitions/effects  : <none, or one named effect>
audio intent         : <ambient, foley, music bed, silence>
style and mood       : <look bible: grade, lens, texture, lighting, motion language>
reference roles      : <asset path = role, one role per asset>
```

**Reference roles are explicit.** Never write "use these images". Each asset gets exactly
one role and the roles never overlap:

```text
reference-1 = identity of <SUBJECT-A>
reference-2 = wardrobe for <SUBJECT-A>
reference-3 = grade, lens and lighting only
```

A vague reference set makes the model average the inputs: the face takes the grade from
the wardrobe shot, the palette from the lighting shot, and identity drifts. One asset, one
role. If the adapter accepts fewer references than the shot needs, keep the identity anchor
and describe the remaining roles in words.

### Camera language

| Shot size | Reads as | Use for |
|---|---|---|
| Extreme close-up (ECU) | Detail fills the frame | Texture, a held object, tension |
| Close-up (CU) | Face or object | Emotion, a decision |
| Medium close-up (MCU) | Head and shoulders | Speech, reaction |
| Medium shot (MS) | Waist up | Action with context |
| Medium wide (MW) | Full body with surroundings | Movement through a space |
| Wide (WS) | Subject small in the frame | Scale, isolation |
| Establishing wide (EWS) | Place before people | Opening a sequence |

| Move | Meaning | Risk |
|---|---|---|
| Push in | Camera advances toward the subject | Reads as emphasis; overused it becomes a tic |
| Pull back | Camera retreats, revealing context | Reveals generated background errors |
| Pan | Rotates horizontally from a fixed point | Long pans expose unstable geometry |
| Tilt | Rotates vertically from a fixed point | Weak on flat generated backgrounds |
| Track | Moves laterally with or past the subject | Must match subject speed or the subject slips |
| Orbit | Arcs around the subject | Faces drift most under orbit; anchor hard |
| Whip pan | Fast pan used as a transition | Usually a code transition instead |
| Crane | Rises or falls | Generated ground planes often break |
| Dolly zoom | Distance and focal length move in opposition | Rarely reproduced correctly; use sparingly |

**Timing breakdown for shots over ~8 s.** Models lose coherence as a clip lengthens, and
an unplanned long clip invents its own cuts. A 10-second shot is two or three beats:

| Beat | Time | What changes |
|---|---|---|
| 1 | 0.0–4.0 s | Establish the subject and the move; the camera direction is already set |
| 2 | 4.0–7.0 s | The action completes; the camera continues in the same direction |
| 3 | 7.0–10.0 s | The frame settles; the move slows to a stop |

One direction of motion per beat. A static camera and an orbit in the same segment is a
contradiction and the model resolves it by doing neither.

## Acceptance QC

Run this checklist on every generated clip before it enters the edit.

| Defect | What it looks like | Action |
|---|---|---|
| Identity drift | The face changes between shots, or within one shot | Regenerate with a stronger anchor |
| Morphing or warping anatomy | Limbs bend the wrong way, the face reshapes mid-move | Regenerate |
| Extra or missing limbs | A third hand, six fingers, an arm that ends | Regenerate |
| Melting or unstable geometry | Walls, roads or furniture flow into each other | Regenerate, or shorten the shot |
| Unreadable or garbled text | Signs, screens or labels carry invented lettering | Cover or crop; overlay real text in code |
| Flicker and temporal instability | Exposure, colour or grain pulses frame to frame | Regenerate; compare consecutive frames of the full grid |
| Unintended cuts | The clip contains an edit the recipe did not ask for | Regenerate, or use only the clean segment |
| Dead or flat frames | A black, blank or frozen stretch at the head or tail | Regenerate; `tools/check-frames.py` flags blank and flat frames |
| Audio artefacts | Hum, clipped transients, speech-like noise | Discard generated audio; mix separately |

Review procedure:

1. **Extract frames.** A generated clip is a video file, so sample it with the
   resolved ffmpeg — one frame per second for the first pass, the full frame grid
   when flicker or an unintended cut is being examined:
   ```bash
   FF="$(tools/ffmpeg.sh)"
   # first pass: one frame per second
   "$FF" -i media/inbox/generated/<shot-id>/clip.mp4 -vf fps=1 \
     out/review/<shot-id>-frames/t%03d.png
   # full grid, when flicker or an unintended cut is suspected
   "$FF" -i media/inbox/generated/<shot-id>/clip.mp4 \
     out/review/<shot-id>-full/t%04d.png
   ```
   `tools/export-frames.mjs` walks the frame grid of a **code-rendered film**
   through its seek contract; run it on the composition the clip is cut into, so
   the generated layer and the code layer are reviewed on the same grid.
2. **Sample deliberately.** The first frame, the last frame, and one frame per second in
   between — the ends of a clip fail far more often than its middle.
3. **Build a contact sheet** in numeric time order:
   ```bash
   python3 tools/contact-sheet.py out/review/<shot-id>-sheet.jpg \
     out/review/<shot-id>-frames/*.png --cols 5
   ```
4. **Compare against the approved still.** Review the sheet next to
   `media/archive/generated/<shot-id>/locked/` and check face geometry, wardrobe, palette
   and lighting direction tile by tile.
5. **Record a verdict** — PASS or REGENERATE — in the shot recipe. A clip failing identity
   or anatomy checks is **regenerated, not "fixed in the edit"**. Grade, speed, crop and
   duration can be adjusted in the edit; a wrong face, a third hand and melting geometry
   cannot. Change one variable per regeneration — prompt wording, reference role, seed or
   model — or the cause of the improvement is unknown.

**Conform before the timeline.** Models return 24, 25 or 30 fps, often variable. A clip
entering a 25 fps edit without conforming drifts against the audio and against every code
layer. Resample in time, preserving duration:

```bash
"$FF" -i raw.mp4 -r 25 -fps_mode cfr -c:v libx264 -pix_fmt yuv420p -crf 16 \
  out/conform/<shot-id>-25.mp4
```

`-r 25` duplicates or drops frames to preserve duration. Slowing a 30 fps clip to 25 fps is
a separate, deliberate speed change — never let it happen by accident. Tag Rec.709 on
output; convert if the model returns a different colour space.

**Never trust generated on-screen text.** Cover it, crop it, or overlay real text in code
and measure the result with `tools/probe-layout.mjs`. Captions and subtitles belong to
`kinetic-captions-and-subtitles`.

**Discard generated audio** unless the brief explicitly asks for it. The mix is built in
`voiceover-and-audio-mix` against the delivery target of −14 LUFS integrated and true peak
≤ −1 dBTP.

## Provider adapters

```text
providers/<provider>/
  SKILL.md     # syntax, limits, cost and hardware label
  examples/    # approved prompt and parameter pairs from this project
```

Every adapter begins with a label line stating cost and hardware, before any other content:

```markdown
> Cost: free. Hardware: GPU with 12 GB VRAM or more.
> Cost: free tier, limited quota. Hardware: none.
> Cost: paid per generation. Hardware: none.
```

The adapter holds syntax; this skill holds craft. An adapter never restates the craft — it
maps craft fields onto the provider's parameter names, records reference-image limits, and
states what the model will not accept.

Minimal adapter template:

```markdown
---
name: provider-<provider>
description: Adapter for <provider> — maps the ai-cinematic-broll craft fields onto <provider> prompt syntax, parameters, reference-image handling and cost limits. Use when generating footage through <provider>.
---

# <Provider> Adapter

> Cost: <free | free tier, limited | paid per generation>. Hardware: <none | GPU, N GB VRAM>.

## Craft to parameter mapping

| Craft field (ai-cinematic-broll) | <provider> parameter |
|---|---|
| subject and identity | <prompt field> |
| camera behaviour | <prompt field> |
| reference roles | <reference slot> |
| duration | <length parameter> |
| aspect | <aspect parameter> |

## Reference images

- Maximum references: <N>
- Photoreal human faces accepted: <yes | no>
- Reference roles that overlap: <allowed | rejected>

## Limits

- Maximum clip length: <N> s
- Returned frame rate: <N> fps, <constant | variable>
- Native aspect ratios: <list>

## Cost control

- <how to draft cheaply, when to spend, what to never re-roll>
```

## Handoff

- A clip enters the edit only after the defect checklist and a PASS verdict recorded in the
  shot recipe.
- Storyboard and shot intent come from `video-brief-and-storyboard`; brand palette and
  tokens from `brand-asset-intake`.
- Audio mix, loudness and true peak: `voiceover-and-audio-mix` at −14 LUFS integrated and
  true peak ≤ −1 dBTP.
- Real on-screen text and captions: `kinetic-captions-and-subtitles`, measured with
  `tools/probe-layout.mjs`.
- Version fan-out: `multiformat-recomposition` — a 9:16 cut is recomposed, not cropped.
- Final encode and gate: `video-post-delivery` — 25 fps, H.264 yuv420p, Rec.709 — with
  `tools/verify.sh` run before delivery.

## Pitfalls

- **Generating video before approving stills.** The single most expensive mistake. Every
  rejected clip is a full clip paid for; the same frame as a still costs a fraction.
- **A look bible written after generation started.** The first batch already set the grade,
  the lens and the grain. Consistency is decided before generation, not patched after it.
- **One reference image used for every shot.** The character never turns. A single front
  view repeated becomes a flat mask; build the reference sheet with multiple angles.
- **Prompts that conflict with themselves.** A static camera plus an orbit in the same
  segment, or "slow and calm" plus "fast action", leaves the model averaging both. One
  direction of motion per beat.
- **Asking a 4-second clip to carry a 12-second idea.** The idea is cut across shots or the
  shot is lengthened with a beat plan; it is not compressed into a clip that cannot hold it.
- **Assuming the clip is 25 fps.** The model returns 24 or 30, the edit drifts against the
  audio and the code layers, and the fault surfaces at delivery. Conform every clip.
- **Treating "looks good" as acceptance.** The defect checklist is run on every clip, with
  frames extracted and compared against the approved still. Taste is a human call; identity
  and anatomy are checks.
- **Spending quota before stating the plan.** The shot list and the estimated generation
  count are stated before a paid path is used, and the free fallback is announced when
  neither GPU nor quota exists.
