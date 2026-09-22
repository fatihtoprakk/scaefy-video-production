# Third-party notices

This repository is MIT licensed (see `LICENSE`). It vendors two third-party skills, both
under the MIT licence, reproduced below with their original copyright notices.

Nothing else is vendored. In particular, **no code or text from AGPLv3-licensed projects
is included** — see "Referenced but not included" at the end.

---

## `skills/bang-motion/`

**Origin:** https://github.com/bangtutorial/bang-motion
**Author:** Bang Tutorial
**Licence:** MIT
**Version vendored:** 1.19.0

```
MIT License

Copyright (c) 2026 Bang Tutorial

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

The skill's own `LICENSE` file is preserved at `skills/bang-motion/LICENSE`.

---

## `skills/remotion-marketing-video/`

**Origin:** https://github.com/xsourabhsharma/remotion-marketing-video-skill
**Author:** Sourabh
**Licence:** MIT

```
MIT License

Copyright (c) 2026 Sourabh

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

The skill's own `LICENSE` file is preserved at `skills/remotion-marketing-video/LICENSE`.

---

## Brand assets in the example film

The bundled `example/` film is a worked example for **Scaefy**, the project that
maintains this pack. It uses that brand's own logo
(`example/assets/brand/logo/scaefy-black.png`), name, and on-screen copy.

The MIT licence in `LICENSE` covers the **code and documentation** in this
repository. It does **not** grant any right to the Scaefy name or logo, which
remain trademarks of their owner. If you fork this repository, replace the example
film's brand assets with your own — the skills are brand-neutral and expect you to
supply your own tokens through `brand-asset-intake`.

---

## Referenced but not included

### OpenMontage — AGPLv3

https://github.com/calesthio/OpenMontage

OpenMontage is licensed under the **GNU Affero General Public License v3**. Under AGPL
section 5(c), a work that incorporates AGPL code must be licensed as a whole under the
AGPL. Copying any part of it into this MIT repository would relicense the entire
repository, so **no OpenMontage code, skill text, or asset is included here**.

It is credited in `README.md` as related work because its independently published design
validates several choices this pack makes — an offline free path, engine selection at
proposal time, and measurable post-render review. Ideas are not copyrightable; the
expression is, and none of that expression is reproduced.

Users who want OpenMontage can install it separately. Because the two projects remain
separate works, their licences do not mix.

### seedance2-skill — MIT

https://github.com/dexhunter/seedance2-skill — © 2026 Dex (i@dex.moe)

A prompt-writing guide for Jimeng Seedance 2.0. It is MIT and therefore vendorable, but
it is not included in this release because it targets a paid cloud model. When it is
vendored it will live under `providers/seedance-2/` with a clear label stating that the
skill is free while the model is not.

### Others

`sub-level/marketing-videos` and `pexoai/pexo-skills` are credited in `README.md` as
related work. Neither is vendored and neither is a dependency.
