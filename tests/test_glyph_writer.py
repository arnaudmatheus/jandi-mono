"""Writing pen shapes into a font (tools/glyph_writer.py)."""

import shapely

from conftest import reloaded, square, tiny_font
from glyph_writer import GlyphWriter


def _writer() -> GlyphWriter:
    return GlyphWriter(reloaded(tiny_font({"a": [square(0, 0, 100)]})), cell=1160)


def test_put_replaces_the_outline_and_records_the_ink():
    writer = _writer()
    writer.put("a", shapely.box(200, -10, 900, 1080))
    assert writer.bounds("a") == (200, -10, 900, 1080)
    assert writer.ink["a"] == (200, -10, 900, 1080)
    assert writer.font["hmtx"]["a"] == (1160, 200)


def test_put_keeps_a_given_advance():
    writer = _writer()
    writer.put("a", shapely.box(0, 0, 2000, 500), advance=2320)
    assert writer.font["hmtx"]["a"][0] == 2320


def test_round_shapes_become_curves():
    writer = _writer()
    writer.put("a", shapely.Point(580, 500).buffer(300, quad_segs=32))
    program = writer.font["CFF "].cff.topDictIndex[0].CharStrings["a"].program
    assert "rrcurveto" in program or "hvcurveto" in program or "vhcurveto" in program


def test_added_glyph_joins_the_glyph_order():
    writer = _writer()
    writer.add("A.titl", shapely.box(100, 0, 1000, 1460))
    writer.commit_glyph_order()
    assert writer.font.getGlyphOrder()[-1] == "A.titl"
    assert writer.has("A.titl")
    assert writer.bounds("A.titl") == (100, 0, 1000, 1460)
