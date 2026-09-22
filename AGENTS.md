# AGENTS.md — working on this repository

Instructions for an agent editing **this pack**. If you are using the pack to
produce a video, read `README.md` and the skill you need instead.

---

## 1. What this repository is

A brand-neutral, English-language, MIT-licensed skill pack for code-generated
video production. A film is written as code: a timeline renders every frame as a
pure function of time, stills are captured from a real browser, ffmpeg encodes,
audio is mixed, and delivery passes a measured gate.

The pack's own prose and skills carry **no client work** — every brand reference in
a skill is a placeholder. The single exception is the bundled `example/` film,
which is branded for **Scaefy**, the project that maintains this pack, and uses
that brand's real logo and on-screen copy. It is a worked example, not client
material, and its brand assets are trademarks of their owner rather than MIT
licensed content (see `THIRD_PARTY_NOTICES.md`).

---

## 2. Hard rules

### 2.1 Language

- **Our own content is English**: skill bodies, docs, tool output, code comments,
  commit messages, fixture strings.
- **Vendored third-party content keeps its upstream language.** Do not translate
  it. `skills/bang-motion/` ships in Indonesian and stays that way.
- No Turkish-specific letters — the dotless i, c-cedilla, g-breve, o-diaeresis,
  s-cedilla, u-diaeresis, and their uppercase forms — anywhere in our own files.
  `tools/verify.sh` enforces this. The letters are spelled out rather than written
  literally here, because listing them would make this very file fail its own gate.
- **One documented exemption:** the bundled `example/` directory is *brand content*,
  not pack prose. Its on-screen copy is Turkish by design, and `example/README.md`
  quotes that copy when it documents the beats. The whole directory is exempt from the
  automated language scan; the banned-string gate still scans it. The convention still
  holds by hand — the README's own prose is written in English.
- **`README.tr.md` is also exempt**, because a translated document is not pack prose
  written in the wrong language. Keep the English `README.md` canonical: change it
  first, then bring the translation across.

### 2.2 No client leakage

This repository is public. It must never contain a client's name, slogan, brand
values, or private vocabulary.

`tools/banned-strings.txt` ships as a **template with every entry commented out**.
Do not add real client terms to it: a public blocklist that names the client is
itself the leak. The real list belongs in the private working copy, which runs
its own pre-publish check.

### 2.3 Zero-cost core

The core pipeline must never require an API key, an account, or network access.
If you add a capability that needs any of those, it goes behind an optional,
clearly labelled layer — never into the default path.

### 2.4 Determinism

Film sources must never use `Math.random`, `Date.now`, or `setInterval`. All
animation is a function of time through a seek contract. Tools may use wall-clock
time for progress reporting; films may not. `tools/verify.sh` enforces this.

### 2.5 Licensing

| Upstream licence | May we vendor? |
|---|---|
| MIT | Yes, with attribution |
| Apache-2.0 | Yes, with the licence text, notices, and a statement of changes |
| AGPL / GPL | **No.** Copyleft would relicense this repository as a whole. |
| No licence | **No.** |

Every vendored item is recorded in `THIRD_PARTY_NOTICES.md` with its licence text
and copyright line. Projects we only *reference* are credited in the README's
related-work section and are never copied.

---

## 3. Skill authoring contract

A skill is a directory `skills/<kebab-name>/` containing `SKILL.md`. The directory
name and the frontmatter `name` must match and be kebab-case.

```markdown
---
name: kebab-case-name
description: One sentence on what it produces, then explicit "Use when..." triggers.
---

# Title

...
```

- The `description` is what makes an agent load the skill. Write concrete
  triggers; cover the situations a user would actually be in, including the ones
  where they never say the skill's name.
- One H1, then H2 sections. Match the structure of the existing skills.
- Reference the other skills by their real names.
- Scripts belong in `skills/<name>/scripts/`; references in
  `skills/<name>/references/`.
- Do not add a licence header or an author name.
- No absolute paths, and no paths into a private project.

---

## 4. Tool conventions

`tools/` holds the **production tooling** the skills and docs reference — frame
capture, frame checks, layout measurement, delivery QC, and the gate runner.
**Release plumbing lives in `ci/`**, because it is never part of making a film and
mixing the two makes `tools/` mean two things at once. `mirror-github.sh` is in
`ci/` for exactly that reason.

| Rule | Why |
|---|---|
| Resolve ffmpeg with `"$(tools/ffmpeg.sh)"` | It tests execution, not existence |
| Never require `ffprobe` | Parse `ffmpeg -i` output instead |
| Measure layout from the DOM | Pixel scans mistake gradients for text |
| Keep helpers inside the project | Capture tools write profiles and temp files locally |
| Target bash 3.2 | macOS ships it; `mapfile` does not exist there |
| Prefix helper function names | `head`, `test`, and `ls` are real commands |

---

## 5. Before you commit

```bash
bash tools/verify.sh
```

Every gate must pass. A gate that reports `WARN` because it has nothing to check
is not a pass — read which gate warned and why.

If your change touches a film source, also capture frames and check them:

```bash
PUPPETEER_CACHE_DIR="$PWD/.puppeteer-cache" TMPDIR="$PWD/.tmp" \
URL="file://$PWD/index.html?clean=1" node tools/shots.mjs shots 1.5 12.0 30.0
python3 tools/check-frames.py shots/*.png
```

---

## 6. What not to do

- Do not add a dependency the core path needs to install in order to watch a film.
- Do not commit a master file; commit a lightweight review copy if one is needed.
- Do not commit secrets. Keys live in `.secrets/` or the environment.
- Do not ship a film that has not passed `qc.py`.
- Do not restate numbers another skill owns — reference it.
