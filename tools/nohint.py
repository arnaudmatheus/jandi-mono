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

BASES = {'i', 'l', 'j', 'q', 'one', 'dotlessi', 'uni0237'}
LETTERS = set('iljq')

font = TTFont(sys.argv[1])
cmap = font.getBestCmap()
skip = set()
# In the italics, hinting t and f too made l/t and t/f worse (+0.018, +0.023
# at 12 px); left out there, nothing is worse and sharpness still rises.
if font['post'].italicAngle:
    BASES |= {'t', 'f', 'tcaron', 'tbar', 'uni021B', 'uni0163'}
    LETTERS |= {'t', 'f'}
for cp, name in cmap.items():
    d = ud.normalize('NFD', chr(cp))
    if d and d[0] in LETTERS and len(d) > 1:
        skip.add(name)
for name in font.getGlyphOrder():
    if name.split('.')[0] in BASES or name.split('.')[0] in skip:
        skip.add(name)
print(','.join(sorted(n for n in skip if re.fullmatch(r'[A-Za-z0-9_.]+', n))))
