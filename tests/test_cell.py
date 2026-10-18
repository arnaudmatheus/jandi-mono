"""The cell rescale (tools/cell.py)."""

from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont

from build_options import DEFAULT_CELL, RADON_CELL, WIDE_CELL
from cell import rescale_cell
from conftest import square, tiny_font

# A box-drawing bar that touches both cell edges, and a bracket that doesn't.
GLYPHS = {
    "boxbar": [[(0, 600), (RADON_CELL, 600), (RADON_CELL, 700), (0, 700)]],
    "bracket": [square(420, 0, 400)],
}


def _radon(tmp_path) -> tuple[TTFont, str]:
    path = tmp_path / "radon.otf"
    tiny_font(GLYPHS, cell=RADON_CELL).save(path)
    return TTFont(path), str(path)


def _bounds(font: TTFont, name: str):
    glyphs = font.getGlyphSet()
    bp = BoundsPen(glyphs)
    glyphs[name].draw(bp)
    return bp.bounds


def test_default_cell_scales_everything_alike(tmp_path):
    font, src = _radon(tmp_path)
    rescale_cell(font, src, DEFAULT_CELL)
    assert font["hmtx"]["boxbar"][0] == DEFAULT_CELL
    assert _bounds(font, "boxbar")[2] == DEFAULT_CELL
    assert _bounds(font, "bracket")[2] - _bounds(font, "bracket")[0] < 400


def test_wide_stretches_only_what_joins_both_edges(tmp_path):
    # Stretched, [ and { looked more alike; box lines must still join.
    font, src = _radon(tmp_path)
    rescale_cell(font, src, WIDE_CELL)
    assert _bounds(font, "boxbar")[2] == WIDE_CELL
    x0, _, x1, _ = _bounds(font, "bracket")
    assert round(x1 - x0) == round(400 * DEFAULT_CELL / RADON_CELL)
    assert abs((x0 + x1) / 2 - WIDE_CELL / 2) <= 1


def test_side_bearing_is_the_real_left_edge(tmp_path):
    font, src = _radon(tmp_path)
    rescale_cell(font, src, DEFAULT_CELL)
    assert font["hmtx"]["bracket"][1] == round(_bounds(font, "bracket")[0])


def test_radon_cell_is_left_alone(tmp_path):
    font, src = _radon(tmp_path)
    rescale_cell(font, src, RADON_CELL)
    assert font["hmtx"]["boxbar"] == (RADON_CELL, 0)
