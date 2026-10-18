"""Small rules of the accent and ornament steps."""

import accents
import glyph_table
import letters
from conftest import tiny_font
from place_ornaments import _extend_cmap


def test_i_and_j_lose_their_dot_under_a_mark_above():
    assert accents._base_for("í") == "dotlessi"
    assert accents._base_for("ǰ") == "uni0237"
    assert accents._base_for("į") == "i"  # ogonek hangs below: dot stays


def test_case_marks_and_vietnamese_stacks():
    name_cp = {"acutecomb": 0x301}
    assert accents._case_mark_cps("acutecomb.case", name_cp) == [0x301]
    assert accents._case_mark_cps("uni03020301", name_cp) == [0x302, 0x301]
    assert accents._case_mark_cps("uni03020301.case", name_cp) == [0x302, 0x301]
    assert accents._case_mark_cps("acutecomb", name_cp) == []


def test_x_height_stretches_but_ascenders_keep_their_top():
    assert glyph_table.vmap(-200) == -200
    assert glyph_table.vmap(letters.T) == glyph_table.T_NEW
    assert glyph_table.vmap(letters.A) == letters.A


def test_new_code_points_past_the_bmp_get_a_format_12_subtable():
    font = tiny_font({"a": []})
    _extend_cmap(font, {0x2766: "uni2766", 0x1F650: "u1F650"})
    tables = font["cmap"].tables
    windows_12 = [t for t in tables if t.format == 12 and t.platEncID == 10]
    assert windows_12 and windows_12[0].cmap[0x1F650] == "u1F650"
    assert all(0x1F650 not in t.cmap for t in tables if t.format == 4)
    assert any(t.cmap.get(0x2766) == "uni2766" for t in tables if t.format == 4)
