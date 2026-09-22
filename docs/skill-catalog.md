# Skill catalog

Ten skills. An agent loads one when the work matches its `description`, so the
descriptions are written as routing triggers rather than feature lists.

---

## Routing table

| You want to | Load |
|---|---|
| Plan a new video, write a brief, beat sheet or storyboard, build an animatic, or get approval before full production | `video-brief-and-storyboard` |
| Turn a logo, palette, font or handle into verified tokens; check contrast; compute type scale or safe areas | `brand-asset-intake` |
| Build kinetic typography, counters, data bars, name cards, a logo reveal or an end card | `video-motion-graphics` |
| Generate photoreal or stylised footage; keep a character consistent; animate an approved still | `ai-cinematic-broll` |
| Time narration to frames; design a music bed; duck music under speech; hit a loudness target | `voiceover-and-audio-mix` |
| Add captions or subtitles; make a film readable with the sound off; localise it | `kinetic-captions-and-subtitles` |
| Cut a vertical, square or short version; adapt one film across platforms | `multiformat-recomposition` |
| Encode, normalise, QC or derive delivery versions | `video-post-delivery` |
| Write a one-shot opener in HTML + GSAP with cinematic motion | `bang-motion` (vendored) |
| Build a data-fed, repeatedly rendered composition in React | `remotion-marketing-video` (vendored) |

---

## The chain

```
video-brief-and-storyboard
        │
        ├─► brand-asset-intake ────────────────┐
        │                                       │
        ├─► ai-cinematic-broll ───┐             │
        │                         │             │
        ├─► video-motion-graphics ┤             │
        │                         ▼             ▼
        ├─► voiceover-and-audio-mix ──► edit ──► multiformat-recomposition
        │                                             │
        └─► kinetic-captions-and-subtitles ───────────┤
                                                      ▼
                                            video-post-delivery
```

`bang-motion` and `remotion-marketing-video` sit underneath
`video-motion-graphics`: it decides *what* the graphics layer contains and *which*
engine builds it.

---

## Ownership boundaries

Several skills touch the same subjects. Each number has exactly one owner, and the
others reference it rather than restating it — duplicated thresholds drift apart.

| Subject | Owner | Others |
|---|---|---|
| Type scale, safe areas, contrast thresholds | `brand-asset-intake` | Reference it |
| Frame-accurate voiceover cues | `voiceover-and-audio-mix` | `kinetic-captions-and-subtitles` reuses the same cue table |
| Caption readability limits (characters per line, CPS) | `kinetic-captions-and-subtitles` | Declared per language |
| Loudness and true-peak targets | `video-post-delivery` | Every other skill hands off to it |
| Delivery specs and QC specs | `video-post-delivery` | `multiformat-recomposition` maps formats to them |
| Beat boundaries and the approval gate | `video-brief-and-storyboard` | Every downstream skill consumes them |
| Look bible and identity anchoring | `ai-cinematic-broll` | — |

---

## Engine choice

`video-motion-graphics` owns this decision. A film uses **one** engine; mixing them
inside a single film is not supported.

| Situation | Engine |
|---|---|
| One-shot opener, fast iteration, kinetic type | HTML + GSAP (`bang-motion`) |
| Data-fed template that gets re-rendered | Remotion (`remotion-marketing-video`) |
| Photoreal footage, characters, scenes | AI generation (`ai-cinematic-broll`) |
| Minimal, no-dependency film | Plain HTML + a `render(t)` function — see `example/` |

The bundled `example/` film uses the last option deliberately: it proves the engine
contract without a third-party runtime and keeps the repository free of a non-MIT
animation library.

---

## Adding a skill

See `AGENTS.md` §3 for the authoring contract. In short: a kebab-case directory
whose name matches the frontmatter `name`, a `description` that leads with a tight
purpose clause and then explicit "Use when" triggers, one H1, and references to
sibling skills by their real names. `tools/verify.sh` enforces all of it, including
that no skill references a skill that does not exist.
