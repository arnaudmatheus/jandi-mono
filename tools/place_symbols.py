"""Step 1b: punctuation, symbols and ligatures with the pen.

Roadmap E1, E2; see tools/punct.py. Drawn glyphs sit on Radon's own centre,
so code columns don't move; restroked ones keep Radon's geometry and advance
exactly.
"""

from shapely import affinity

import punct
from build_state import BuildState
from gsub_features import liga_lookups, lookup_outputs, stylistic_set_lookups

# Radon's italic angle; Talha's is the style's slant. Restroked symbols are
# sheared by the difference.
RADON_ITALIC_ANGLE = 11


def _ligatures(state: BuildState) -> set[str]:
    """Every ligature glyph, on by default or behind a stylistic set."""
    font = state.font
    outputs = lookup_outputs(font, liga_lookups(font) + stylistic_set_lookups(font))
    return outputs - {"emptyAdvanceWidth"} - set(state.glyphs) - set(punct.DRAWN)


def _place_drawn(state: BuildState) -> None:
    w, t = state.nib
    for name in punct.DRAWN:
        if not state.writer.has(name):
            continue
        rx0, _, rx1, _ = state.writer.bounds(name)
        shape = punct.drawn_shape(name, w, t)
        sx0, _, sx1, _ = shape.bounds
        centred = affinity.translate(shape, (rx0 + rx1) / 2 - (sx0 + sx1) / 2, 0)
        state.writer.put(name, centred)
        state.pen_glyphs.append(name)


def _to_restroke(state: BuildState, ligatures: set[str]) -> list[str]:
    def wanted(name: str) -> bool:
        if name in punct.DRAWN or name in state.glyphs:
            return False
        return name.split(".")[0] in punct.RESTROKE_BASES or name in ligatures

    return [name for name in state.font.getGlyphOrder() if wanted(name)]


def _place_restroked(
    state: BuildState, ligatures: set[str], radon_stroke: float
) -> None:
    w, t = state.nib
    radon_angle = RADON_ITALIC_ANGLE if state.opts.italic else 0
    shear = state.opts.slant_deg - radon_angle
    radon = state.font.getGlyphSet()
    for name in _to_restroke(state, ligatures):
        src = punct.outline(radon, name)
        if src.is_empty:
            continue
        shape = punct.restroke(src, w, t, shear, radon_stroke)
        state.writer.put(name, shape, state.font["hmtx"][name][0])
        state.pen_glyphs.append(name)


def place_symbols(state: BuildState) -> None:
    ligatures = _ligatures(state)
    # Measured before anything here is redrawn: Radon's stroke, the weight
    # its symbols are thinned from.
    radon_stroke = punct.stroke_width(state.font.getGlyphSet())
    _place_drawn(state)
    _place_restroked(state, ligatures, radon_stroke)
