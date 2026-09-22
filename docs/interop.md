# Interop

This pack is designed to sit *inside* whatever tooling you already use rather than
replace it. This page covers the case people ask about most: running alongside a
larger production framework.

---

## Using this pack with OpenMontage

[OpenMontage](https://github.com/calesthio/OpenMontage) is a batteries-included
agentic video production framework: a Python orchestrator, a large tool registry,
many provider integrations, and its own skills. It is licensed **AGPLv3**.

This pack is **MIT**. The two licences do not mix, and they do not need to.

### Why nothing is shared

Under AGPL section 5(c), a work that incorporates AGPL code must be licensed as a
whole under the AGPL. Copying any part of OpenMontage into this repository would
relicense the entire repository. So:

- **No OpenMontage code, skill text, or asset is included here.**
- OpenMontage is credited in `README.md` as related work.
- Ideas are not copyrightable; the expression is, and none of it is reproduced.

### How to run them together

OpenMontage's architecture is three-layered, and its third layer is explicitly
**`.agents/skills/` — external technology knowledge packs**. This pack is exactly
that shape. Installing both means placing this pack's `skills/` where
OpenMontage's agent can read them:

```bash
# Install OpenMontage separately, following its own instructions.
# Then make this pack's skills visible to it:
cp -R skills/* /path/to/OpenMontage/.agents/skills/
```

The licences stay separate because the two remain **separate works**. This pack's
files are still MIT; OpenMontage's files are still AGPL. Neither absorbs the
other.

If you redistribute a combined tree, keep the licences distinguishable: this
pack's `LICENSE` and `THIRD_PARTY_NOTICES.md` alongside OpenMontage's own.

### Which to reach for

| Situation | Use |
|---|---|
| A focused film, inside an existing coding agent, no framework install | This pack |
| You need a tool registry, dozens of providers, and a pipeline engine | OpenMontage |
| You need permissive licensing for commercial redistribution | This pack |
| You want the broadest provider catalogue | OpenMontage |

They are complements, not competitors. If you only need code-generated graphics,
captions, and a measured delivery gate, this pack is the smaller dependency.

---

## Using this pack with other agent hosts

The skills follow the [Agent Skills](https://agentskills.io) standard, so the same
`skills/` directory works across hosts:

| Host | How |
|---|---|
| DSH | Install this directory as a preset under `~/.dsh/.agent-presets/` |
| Claude Code | Copy into `.claude/skills/` or use `npx skills add <repo>` |
| Cursor, Codex, OpenClaw, and similar | Copy into the host's skills directory |

Nothing in a skill depends on a specific host. The tools are plain shell, Python,
and Node, and the film itself is a single HTML file.

---

## Using this pack with an existing film pipeline

The delivery gate is deliberately usable on its own. If you already have an edit
and only want the measured checks:

```bash
"$(tools/ffmpeg.sh)" -version >/dev/null && echo "ffmpeg OK"
python3 skills/video-post-delivery/scripts/qc.py your-master.mp4 \
  --spec landscape-1080 --expect-duration 60
```

`qc.py` exits non-zero on any failure, so it drops into an existing CI step
without adaptation. The same applies to `tools/check-frames.py` for frame-level
checks and `tools/probe-layout.mjs` for layout measurement.
