"""Where marks attach to a letter, in upright skeleton space."""

import math

import caps
import letters
import pen
from glyph_table import ASCENDERS, T_NEW, Letter
from pen_types import Point, Stroke

# Mark kind -> GPOS mark class.
MARK_CLASSES = (
    ("above", "TOP"),
    ("below", "BOTTOM"),
    ("horn", "HORN"),
    ("ogonek", "OGONEK"),
)


def _band_xs(strokes: list[Stroke], kind: str) -> list[float]:
    """The x of every skeleton point inside the letter's main band."""
    if kind == "lower":
        return [x for st in strokes for x, y in st if letters.B - 1 <= y <= T_NEW + 1]
    return [x for st in strokes for x, y in st if caps.FB - 20 <= y <= caps.CT + 20]


def anchors(letter: Letter, gname: str) -> dict[str, Point]:
    """Top / bottom / horn / ogonek anchors, before slant and centring.

    >>> anchors(glyphs["n"], "n")["below"]
    (617.5, 0)
    """
    s = letter.strokes()
    xs = _band_xs(s, letter.kind)
    cx, right = (min(xs) + max(xs)) / 2, max(xs)
    if letter.kind == "lower":
        top_y = (letters.A + 170) if gname in ASCENDERS else (T_NEW + 190)
        horn_y = T_NEW - 40
    else:
        top_y, horn_y = caps.CT + 150, caps.CT - 40
    return {
        "above": (cx, top_y),
        "below": (cx, 0),
        "horn": (right - 40, horn_y),
        "ogonek": (right - 20, 0),
        "caronapos": (max(x for st in s for x, y in st) + 70, letters.A - 60),
    }


def final(pt: Point, dx: float) -> Point:
    """An upright anchor -> its place in the slanted, centred glyph."""
    x, y = pt
    return (x + y * math.tan(pen.SLANT) + dx, y)


def shifted(strokes: list[Stroke], ox: float, oy: float) -> list[Stroke]:
    return [[(x + ox, y + oy) for x, y in st] for st in strokes]
