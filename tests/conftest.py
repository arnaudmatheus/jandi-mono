"""Shared test helpers: tiny fonts built in memory, and polygon geometry.

The build tools work on real OpenType fonts, so the tests make small ones
with fontTools' FontBuilder instead of reading the 2 MB upstream files:
fast, and every glyph's shape is known.
"""

import io
from pathlib import Path

import pytest
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.ttLib import TTFont

REPO = Path(__file__).resolve().parent.parent

Point = tuple[float, float]
Contour = list[Point]


def charstring(contours: list[Contour], width: int = 1160):
    """A CFF charstring drawing each contour as a closed polygon."""
    pen = T2CharStringPen(width, None)
    for contour in contours:
        pen.moveTo(contour[0])
        for point in contour[1:]:
            pen.lineTo(point)
        pen.closePath()
    return pen.getCharString()


def tiny_font(glyphs: dict[str, list[Contour]], cell: int = 1160) -> TTFont:
    """An in-memory CFF font: .notdef plus the given glyphs, all one cell wide.

    >>> tiny_font({"a": [[(100, 0), (500, 0), (500, 500), (100, 500)]]})
    """
    order = [".notdef", *glyphs]
    fb = FontBuilder(2000, isTTF=False)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap({ord(n): n for n in glyphs if len(n) == 1})
    strings = {".notdef": charstring([], cell)}
    strings.update({name: charstring(c, cell) for name, c in glyphs.items()})
    fb.setupCFF("TestFont-Regular", {"FullName": "Test Font"}, strings, {})
    fb.setupHorizontalMetrics({name: (cell, 0) for name in order})
    fb.setupHorizontalHeader(ascent=1600, descent=-400)
    fb.setupNameTable({"familyName": "Test Font", "styleName": "Regular"})
    fb.setupOS2(
        sTypoAscender=1600, sTypoDescender=-400, usWinAscent=1600, usWinDescent=400
    )
    fb.setupPost()
    return fb.font


def reloaded(font: TTFont) -> TTFont:
    """The font saved and opened again, as the build opens Radon from disk
    (a loaded CFF keeps its charstrings indexed; a built one doesn't)."""
    buf = io.BytesIO()
    font.save(buf)
    buf.seek(0)
    return TTFont(buf)


def square(x: float, y: float, size: float) -> Contour:
    """A counter-clockwise square (CFF ink), lower-left corner at (x, y)."""
    return [(x, y), (x + size, y), (x + size, y + size), (x, y + size)]


@pytest.fixture
def saved_font(tmp_path: Path):
    """Saves a tiny font to tmp_path under a name; returns its path."""

    def save(name: str, glyphs: dict[str, list[Contour]]) -> Path:
        path = tmp_path / name
        tiny_font(glyphs).save(path)
        return path

    return save
