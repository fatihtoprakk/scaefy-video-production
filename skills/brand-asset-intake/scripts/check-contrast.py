#!/usr/bin/env python3
"""WCAG contrast check (for headline, lower-third and CTA text).

Usage:
    check-contrast.py --fg "#F4F1EA" --bg "#0B1F19" [--large]
    check-contrast.py --matrix "#F4F1EA,#E4572E" --bg "#0B1F19"

Thresholds: normal text ≥ 4.5:1 · large text (≥ 24 px, or ≥ 18.66 px bold) ≥ 3:1.
Lower-third text always counts as normal text (small size, moving background).
Exit code: 1 if anything falls below its threshold.
"""

from __future__ import annotations

import argparse
import sys


def parse_hex(value: str) -> tuple[int, int, int]:
    v = value.strip().lstrip("#")
    if len(v) == 3:
        v = "".join(ch * 2 for ch in v)
    if len(v) != 6:
        raise ValueError(f"invalid hex: {value}")
    return tuple(int(v[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


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


def main() -> int:
    ap = argparse.ArgumentParser(description="WCAG contrast check")
    ap.add_argument("--fg", default=None, help="foreground colour (#hex)")
    ap.add_argument("--matrix", default=None, help="comma-separated foreground colours")
    ap.add_argument("--bg", required=True, help="background colour (#hex)")
    ap.add_argument("--large", action="store_true", help="large-text threshold (3:1)")
    args = ap.parse_args()

    fgs = []
    if args.fg:
        fgs.append(args.fg)
    if args.matrix:
        fgs.extend(x for x in args.matrix.split(",") if x.strip())
    if not fgs:
        sys.exit("ERROR: --fg or --matrix is required")

    try:
        bg = parse_hex(args.bg)
        pairs = [(f, parse_hex(f)) for f in fgs]
    except ValueError as exc:
        sys.exit(f"ERROR: {exc}")

    threshold = 3.0 if args.large else 4.5
    kind = "large text" if args.large else "normal text"

    print(f"Background: {args.bg}   Threshold: {threshold}:1 ({kind})")
    print("-" * 56)
    failed = 0
    for label, rgb in pairs:
        ratio = contrast(rgb, bg)
        ok = ratio >= threshold
        failed += 0 if ok else 1
        print(f" {label:<10} {ratio:>6.2f}:1   {'PASS' if ok else 'FAIL'}")
        if not ok:
            need = "a darker background" if luminance(rgb) > luminance(bg) else "a lighter background"
            print(f"            suggestion: {need}, or add a subtle shadow/semi-transparent panel behind the text")
    print("-" * 56)
    print("Result: " + ("all passed" if not failed else f"{failed} colour(s) below threshold"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
