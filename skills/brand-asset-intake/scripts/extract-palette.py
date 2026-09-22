#!/usr/bin/env python3
"""Extract the dominant colour palette from an image (PIL; numpy not required).

Usage:
    extract-palette.py <image...> [--colors 6] [--json output.json] [--alpha-min 200]

Notes:
    • Transparent pixels are NOT included in the palette (otherwise the background colour is mistaken for a brand colour).
    • If brand colours (colors.json) exist, they win; this output is for verification/suggestion only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    sys.exit("ERROR: Pillow is required → python3 -m pip install --target tools/vendor pillow")


def srgb_to_lin(c: float) -> float:
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(rgb: tuple[int, int, int]) -> float:
    r, g, b = (srgb_to_lin(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def hex_of(rgb: tuple[int, int, int]) -> str:
    return "#%02X%02X%02X" % rgb


def _pixels(im: "Image.Image"):
    """Pixel list (without the Pillow 12+ warning)."""
    getter = getattr(im, "get_flattened_data", None)
    return list(getter()) if getter else list(im.getdata())


def opaque_pixels(path: Path, alpha_min: int, max_side: int = 240):
    im = Image.open(path)
    im.load()
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        im = im.convert("RGBA")
        im.thumbnail((max_side, max_side))
        return [(r, g, b) for r, g, b, a in _pixels(im) if a >= alpha_min]
    im = im.convert("RGB")
    im.thumbnail((max_side, max_side))
    return _pixels(im)


def extract(paths: list[Path], n: int, alpha_min: int) -> list[dict]:
    pixels: list[tuple[int, int, int]] = []
    for p in paths:
        pixels.extend(opaque_pixels(p, alpha_min))

    if not pixels:
        sys.exit("ERROR: no countable opaque pixels (file is corrupt or fully transparent)")

    # Turn the pixel list into a 1-row image and use PIL's quantiser.
    flat = Image.new("RGB", (len(pixels), 1))
    flat.putdata(pixels)
    quant = flat.quantize(colors=n, method=Image.MEDIANCUT)
    palette = quant.getpalette() or []
    counts = sorted((quant.getcolors() or []), key=lambda c: -c[0])
    total = sum(c for c, _ in counts) or 1

    out = []
    for count, idx in counts[:n]:
        rgb = tuple(palette[idx * 3 : idx * 3 + 3])
        if len(rgb) != 3:
            continue
        out.append({
            "hex": hex_of(rgb),
            "rgb": list(rgb),
            "share": round(count / total, 4),
            "luminance": round(luminance(rgb), 4),
            "contrast_vs_white": round(contrast(rgb, (255, 255, 255)), 2),
            "contrast_vs_black": round(contrast(rgb, (0, 0, 0)), 2),
        })
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Palette extraction")
    ap.add_argument("images", nargs="+", type=Path)
    ap.add_argument("--colors", type=int, default=6)
    ap.add_argument("--alpha-min", type=int, default=200)
    ap.add_argument("--json", type=Path, default=None)
    args = ap.parse_args()

    for p in args.images:
        if not p.is_file():
            sys.exit(f"ERROR: no such file: {p}")

    palette = extract(args.images, args.colors, args.alpha_min)

    print(f"Palette — {', '.join(p.name for p in args.images)}")
    print("-" * 62)
    print(f"{'HEX':<9}{'SHARE':>7}   {'LUM':>6}   {'vs WHITE':>9} {'vs BLACK':>9}")
    for c in palette:
        print(f"{c['hex']:<9}{c['share']*100:>6.1f}%   {c['luminance']:>6.3f}   "
              f"{c['contrast_vs_white']:>9.2f} {c['contrast_vs_black']:>9.2f}")

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps({
            "source_files": [str(p) for p in args.images],
            "palette": palette,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nWrote: {args.json}")

    print("\nNote: this output is a SUGGESTION. If brand colours exist in assets/brand/colors.json, they win.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
