"""The cell: Radon's 1240 units, narrowed (or widened) for Jandí Mono.

Radon's cell is 1240 (0.62 em), wide; with the narrower chancery letters
there was too much space between them. Shrinking the cell in the font itself
tightens everything at once (terminal, bar, menus). What stays Radon's
(symbols, box drawing, braille) is scaled in x with it, so box lines still
meet edge to edge.
"""

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.teePen import TeePen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

from build_options import DEFAULT_CELL, RADON_CELL
from pen_types import GlyphSet

# How close to the cell edge (font units) counts as touching it.
EDGE_SLACK = 5


def rescale_cell(font: TTFont, src: str, cell: int) -> None:
    """Rewrites every glyph of `font` for a `cell`-wide advance.

    >>> rescale_cell(TTFont("MonaspaceRadon-Regular.otf"), "MonaspaceRadon-Regular.otf", 1160)
    """
    if cell == RADON_CELL:
        return
    radon = TTFont(src).getGlyphSet()
    top = font["CFF "].cff.topDictIndex[0]
    for name in font.getGlyphOrder():
        _rescale_glyph(font, radon, name, cell)
    top.Private.defaultWidthX = cell
    top.Private.nominalWidthX = 0


def _x_transform(
    radon: GlyphSet, name: str, width: int, new_width: int, cell: int
) -> tuple[float, float]:
    """(x scale, x offset) for one glyph.

    Wide: the drawing is the same, only the cell grows. What touches both
    edges (box drawing, blocks) stretches so it keeps joining; the rest
    (brackets, braces, punctuation) keeps Jandí Mono's width and is only
    centred. Stretched, [ and { looked more alike ([/{ +0.018 at 12 px).
    """
    r = cell / RADON_CELL
    r_sym = min(r, DEFAULT_CELL / RADON_CELL)
    if r_sym == r:  # the default cell: every glyph scales alike
        return r, 0
    bp = BoundsPen(radon)
    radon[name].draw(bp)
    joins = (
        bp.bounds is not None
        and bp.bounds[0] <= EDGE_SLACK
        and bp.bounds[2] >= width - EDGE_SLACK
    )
    return (r, 0) if joins else (r_sym, (new_width - width * r_sym) / 2)


def _rescale_glyph(font: TTFont, radon: GlyphSet, name: str, cell: int) -> None:
    cff = font["CFF "].cff
    top = cff.topDictIndex[0]
    width = font["hmtx"][name][0]
    # In this order (not width * cell / 1240): the floats must not move.
    new_width = round(width * (cell / RADON_CELL))
    p = T2CharStringPen(None if new_width == cell else new_width, None)
    sx, ox = _x_transform(radon, name, width, new_width, cell)
    # One pass writes the scaled glyph and measures it (the side-bearing
    # is the outline's real left edge, not Radon's stored value).
    nb = BoundsPen(None)
    radon[name].draw(TransformPen(TeePen(p, nb), (sx, 0, 0, 1, ox, 0)))
    charstrings = top.CharStrings
    new = p.getCharString(private=top.Private, globalSubrs=cff.GlobalSubrs)
    charstrings.charStringsIndex[charstrings.charStrings[name]] = new
    lsb = round(nb.bounds[0]) if nb.bounds else 0
    font["hmtx"][name] = (new_width, lsb)
