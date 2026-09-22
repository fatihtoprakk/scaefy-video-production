# Free and offline

This pack is built so that the **core pipeline costs nothing and needs no
network**. Everything else is optional and clearly labelled.

---

## The two layers

| Layer | Cost | Network | Covers |
|---|---|---|---|
| **A — Code-generated graphics** (core) | **Free** | **None** | Kinetic typography, counters, data bars, name cards, logo reveals, end cards, captions, transitions, complete motion-graphics films |
| **B — AI footage** (optional) | Free with a GPU, otherwise paid | Yes | Photoreal b-roll, characters, scenes |

**The guarantee:** the default pipeline depends on no paid service and requires no
network access. `bash tools/verify.sh` passes offline. CI scans the core path for
network calls and credential references.

**The fallback rule:** if a brief needs generated footage and you have neither a
GPU nor a quota, the agent falls back to Layer A — graphics, typography, and
archival footage — and **says so explicitly**. It never silently connects to a
paid service.

---

## What you need

| Requirement | Why | Cost |
|---|---|---|
| Node 18+ | Capture and export tools | Free |
| Python 3.10+ | QC, measurement, and palette tools | Free |
| ffmpeg | Encoding and measurement | Free |
| A modern browser | Rendering the film | Free |

No account, no API key, no subscription.

Resolve a working ffmpeg first — the resolver tests execution, not existence:

```bash
FF="$(tools/ffmpeg.sh)" && echo "ffmpeg OK"
```

If it reports nothing, install a static build into the repo without touching the
system:

```bash
python3 -m pip install --target tools/vendor imageio-ffmpeg
mkdir -p tools/bin
cp tools/vendor/imageio_ffmpeg/binaries/ffmpeg-* tools/bin/ffmpeg
chmod +x tools/bin/ffmpeg
```

---

## Layer B: the three provider paths

| Path | Cost | Hardware | Notes |
|---|---|---|---|
| **Local open source** | **Free** | GPU required | Open-weight video and image models run on your own machine. Quality and speed depend on VRAM; expect long render times on modest hardware. |
| **Free tier** | Free, limited | None | Provider trial credits. Good for evaluating, not for production volume. |
| **Paid API** | Paid | None | No hardware requirement, highest quality, per-generation cost. |

Adapters for specific providers live under `providers/<provider>/`. Each adapter
begins with a cost and hardware label, so you can see what you are opting into
before you use it. The craft that is common to all of them lives in the
`ai-cinematic-broll` skill.

### Local generation, honestly

Local generation is genuinely free and genuinely hardware-bound. Before choosing
it, be clear about the trade:

- A capable discrete GPU makes it practical.
- Unified-memory laptops can run smaller models, slowly.
- A machine without a usable GPU should use Layer A instead — not a cloud API it
  was not asked to pay for.

The pack does not pretend local generation is free of cost. It is free of money
and expensive in time.

---

## Free asset sources

Layer A still needs footage sometimes. These sources are free and open, and each
carries its own licence terms:

| Source | Content | Licence |
|---|---|---|
| Archive.org | Archival film and audio | Varies per item — check each |
| NASA | Space and earth imagery | Generally public domain |
| Wikimedia Commons | Images and video | Varies — check each |
| Pexels, Pixabay, Unsplash | Stock photo and video | Free licence with terms; a free developer key is required |

**Rule:** every asset's source and licence is recorded alongside it. "Royalty
free" still has terms, and a licence you cannot produce on request is not a
licence. See the `footage-sourcing-and-licensing` skill.

---

## What costs money, and only if you choose it

- Paid image or video generation APIs
- Premium text-to-speech voices
- Commercial music licensing
- Cloud render farms

None of these is required to produce a finished, QC-passing film.
