#!/usr/bin/env python3
"""Glyphs left unhinted (roadmap F2): i, l, j, q, one (and t, f in the
italics), and every glyph built on them (accented forms, dotless forms, texture-healing variants).

python nohint.py <font.otf>  ->  comma-separated glyph names

Measured on the Regular (12/15/20 px): hinting everything made the narrow
pairs more alike, since snapping lined their heights up (i/l +0.014,
f/j +0.012, 1/l +0.011, g/q +0.011). Leaving out only one letter of a pair
moved the problem instead of fixing it. With these five letters and their
families unhinted, no pair is worse than unhinted, and sharpness at 12 px
matches Radon's (0.159 against 0.158)."""

import re, sys, unicodedata as ud
from fontTools.ttLib import TTFont

BASES = {"i", "l", "j", "q", "one", "dotlessi", "uni0237"}
LETTERS = set("iljq")


def unhinted_glyphs(font: TTFont) -> list[str]:
    """Names whose hinting harms legibility; e.g. ``unhinted_glyphs(font)``."""
    bases, letters = set(BASES), set(LETTERS)
    # In italics, hinting t and f made l/t and t/f worse (+0.018, +0.023
    # at 12 px); left out there, nothing is worse and sharpness still rises.
    if font["post"].italicAngle:
        bases |= {"t", "f", "tcaron", "tbar", "uni021B", "uni0163"}
        letters |= {"t", "f"}
    skip = _accented_glyphs(font.getBestCmap(), letters)
    for name in font.getGlyphOrder():
        if name.split(".")[0] in bases or name.split(".")[0] in skip:
            skip.add(name)
    return sorted(n for n in skip if re.fullmatch(r"[A-Za-z0-9_.]+", n))


def _accented_glyphs(cmap: dict[int, str], letters: set[str]) -> set[str]:
    skip = set()
    for cp, name in cmap.items():
        decomposed = ud.normalize("NFD", chr(cp))
        if decomposed and decomposed[0] in letters and len(decomposed) > 1:
            skip.add(name)
    return skip


def main(argv: list[str]) -> None:
    """Print the autohinter exclusions; e.g. ``main(["jandi.otf"])``."""
    with TTFont(argv[0]) as font:
        print(",".join(unhinted_glyphs(font)))


if __name__ == "__main__":
    main(sys.argv[1:])
