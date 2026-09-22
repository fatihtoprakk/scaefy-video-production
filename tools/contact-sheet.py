#!/usr/bin/env python3
"""
contact-sheet.py — combine frames into a single review sheet, in time order.

Why: comparing rhythm and composition at a glance beats opening frames one by
one. Each tile is stamped with its capture time, and ordering is NUMERIC on the
`t<seconds>` value in the filename rather than lexicographic.

Usage:
  python3 tools/contact-sheet.py review/sheet.jpg shots/*.png --cols 5
"""
from __future__ import annotations
import argparse, glob, math, os, re, sys
from PIL import Image, ImageDraw, ImageFont

# First font that exists wins. Put the project's own label font first if it has
# one; the system fallbacks keep the tool usable with no assets installed.
FONT_CANDIDATES = [
    "assets/brand/fonts/Inter-Regular.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]

def t_of(name: str) -> float:
    m = re.search(r"t(\d+)_(\d+)", os.path.basename(name))
    if m: return float(f"{m.group(1)}.{m.group(2)}")
    m = re.search(r"(\d+(?:\.\d+)?)", os.path.basename(name))
    return float(m.group(1)) if m else 0.0

def load_font(size: int):
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except Exception: pass
    return ImageFont.load_default()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("frames", nargs="+")
    ap.add_argument("--cols", type=int, default=5)
    ap.add_argument("--tile-w", type=int, default=640)
    ap.add_argument("--pad", type=int, default=10)
    ap.add_argument("--quality", type=int, default=88)
    ap.add_argument("--title", default="")
    ap.add_argument("--bg", default="#111111", help="sheet background")
    ap.add_argument("--ink", default="#EEEEEE", help="label text colour")
    ap.add_argument("--title-ink", default="#FFFFFF", help="title text colour")
    ap.add_argument("--border", default="#333333", help="tile border colour")
    a = ap.parse_args()

    files = []
    for f in a.frames:
        files.extend(glob.glob(f) if any(c in f for c in "*?[") else [f])
    if not files:
        print("no frames found", file=sys.stderr); return 1
    files.sort(key=t_of)

    first = Image.open(files[0]); ar = first.height / first.width
    tw = a.tile_w; th = int(tw * ar)
    cols = min(a.cols, len(files)); rows = math.ceil(len(files) / cols)
    label_h = max(22, tw // 22)
    title_h = 46 if a.title else 0

    W = cols * tw + (cols + 1) * a.pad
    H = title_h + rows * (th + label_h) + (rows + 1) * a.pad
    sheet = Image.new("RGB", (W, H), a.bg)
    d = ImageDraw.Draw(sheet)
    f_label = load_font(label_h - 8)
    f_title = load_font(30)

    if a.title:
        d.text((a.pad, 10), a.title, font=f_title, fill=a.title_ink)

    for i, fp in enumerate(files):
        r, c = divmod(i, cols)
        x = a.pad + c * (tw + a.pad)
        y = title_h + a.pad + r * (th + label_h + a.pad)
        im = Image.open(fp).convert("RGB").resize((tw, th), Image.LANCZOS)
        sheet.paste(im, (x, y))
        d.rectangle([x, y, x + tw - 1, y + th - 1], outline=a.border)
        d.text((x + 6, y + th + 2), f"t={t_of(fp):.2f}s", font=f_label, fill=a.ink)

    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    sheet.save(a.out, quality=a.quality, optimize=True)
    print(f"{len(files)} frames -> {a.out} ({W}x{H})")
    return 0

if __name__ == "__main__":
    sys.exit(main())
