#!/usr/bin/env python3
"""Generate machine-readable design tokens from brand assets.

Usage:
    make-tokens.py --colors assets/brand/colors.json --out assets/brand/tokens.json
    make-tokens.py --colors assets/brand/colors.json --out assets/brand/tokens.json --provisional

Outputs:
    tokens.json  → single source of truth for graphics engines (Remotion / HTML+GSAP)
    tokens.css   → CSS variables for the HTML/GSAP engine (next to tokens.json)

If real brand colours are missing, `--provisional` generates provisional tokens; the output
is marked `provisional: true` and the film does not count as a "brand film".
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Plan §7 recipe: 1080p reference scale. 4K ×2, 9:16 ×0.85.
TYPE_SCALE_1080 = {
    "headline": [64, 82],
    "emphasis": [92, 112],
    "support": [34, 42],
    "lowerThird": [38, 48],
}
SCALE_4K = 2.0
SCALE_VERTICAL = 0.85

SAFE_AREA_PCT = 8.0
FPS = 25
MOTION = {"fadeFrames": [6, 10], "risePx": [12, 20], "minReadFrames": 38}  # 38 frames = 1.5 s @25fps


def scale_range(pair: list[int], factor: float) -> list[int]:
    return [int(round(v * factor)) for v in pair]


def build_type_scale() -> dict:
    out = {}
    for ratio, factor in (("16x9-1080", 1.0), ("16x9-2160", SCALE_4K), ("9x16-1080", SCALE_VERTICAL)):
        out[ratio] = {
            "frame": "1920x1080" if ratio == "16x9-1080" else ("3840x2160" if ratio == "16x9-2160" else "1080x1920"),
            **{k: scale_range(v, factor) for k, v in TYPE_SCALE_1080.items()},
        }
    return out


def safe_area(frame: str) -> dict:
    w, h = (int(x) for x in frame.split("x"))
    return {
        "pct": SAFE_AREA_PCT,
        "marginPx": {"x": int(round(w * SAFE_AREA_PCT / 100)), "y": int(round(h * SAFE_AREA_PCT / 100))},
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate design tokens")
    ap.add_argument("--colors", type=Path, required=True, help="assets/brand/colors.json")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--provisional", action="store_true", help="generate provisional (non-brand) tokens")
    ap.add_argument("--derived", type=Path, default=None, help="extract-palette.py --json output (for provisional mode)")
    args = ap.parse_args()

    if not args.colors.is_file():
        sys.exit(
            f"ERROR: {args.colors} does not exist.\n"
            "Expected schema:\n"
            '  {"source": "...", "brand": {"primary": "#..", "accent": "#..", "ink": "#..", "bg": "#.."}}\n'
            "If real colours are missing: generate provisional tokens with --provisional and mark the film as a 'concept film'."
        )

    data = json.loads(args.colors.read_text(encoding="utf-8"))
    brand = data.get("brand") or {}
    required = ("primary", "accent", "ink", "bg")
    missing = [k for k in required if not brand.get(k)]

    if missing and not args.provisional:
        sys.exit(
            "ERROR: missing brand colour(s): " + ", ".join(missing) + "\n"
            "No final production without the real codes. Use --provisional to move ahead provisionally."
        )

    provisional = bool(missing) or args.provisional
    if provisional and missing and args.derived and args.derived.is_file():
        palette = json.loads(args.derived.read_text(encoding="utf-8")).get("palette", [])
        # Extreme values (nearly black/white) are not assigned to a brand role; otherwise
        # you get nonsense such as picking black as the "accent".
        usable = [p for p in palette if 0.02 <= p.get("luminance", 0) <= 0.85]
        for key, item in zip(missing, usable or palette):
            brand[key] = item["hex"]
    for key in required:
        brand.setdefault(key, None)

    tokens = {
        "provisional": provisional,
        "source": data.get("source", "unknown"),
        "color": {k: brand.get(k) for k in required},
        "type": build_type_scale(),
        "safeArea": {
            "16x9-1080": safe_area("1920x1080"),
            "16x9-2160": safe_area("3840x2160"),
            "9x16-1080": safe_area("1080x1920"),
        },
        "motion": MOTION,
        "film": {
            "fps": FPS,
            "durations": {"master": 60, "short": 30, "teaser": 15},
            "ratios": ["16:9", "9:16"],
            "loudness": {"integratedLufs": -14, "truePeakDbtp": -1},
        },
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(tokens, ensure_ascii=False, indent=2), encoding="utf-8")

    css = args.out.with_suffix(".css")
    css.write_text(
        ":root {\n"
        f"  /* source: {tokens['source']} | provisional: {str(provisional).lower()} */\n"
        f"  --color-primary: {tokens['color']['primary']};\n"
        f"  --color-accent: {tokens['color']['accent']};\n"
        f"  --color-ink: {tokens['color']['ink']};\n"
        f"  --color-bg: {tokens['color']['bg']};\n"
        "  --safe-area-pct: 8%;\n"
        "}\n",
        encoding="utf-8",
    )

    print(f"Wrote: {args.out}")
    print(f"Wrote: {css}")
    if provisional:
        print("WARNING: tokens are PROVISIONAL (provisional: true) — until updated with real brand assets")
        print("       the output must not be published as a 'brand film'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
