"""Step 5: GPOS mark attachment (mark, mkmk) and the GDEF glyph classes."""

import math

from fontTools.feaLib.builder import addOpenTypeFeaturesFromString

import pen
from anchors import MARK_CLASSES, anchors, final
from build_state import BuildState
from glyph_table import LETTER_OF
from pen_types import Point

# Stacking (ǘ ǚ, and any second mark): the next mark's lowest ink sits
# STACK_GAP above the ink already there. Measured on the ink, because the
# marks hang differently from their anchors: the downward acute reaches 131
# units below its own, the dieresis barely below. A fixed step left the
# acute on the dots.
STACK_GAP = 90
# GPOS mark class -> the marks in it.
MarkClasses = dict[str, list[str]]
GDEF_BASE, GDEF_MARK = 1, 3
DOTLESS = ("dotlessi", "uni0237")


def _mark_classes(state: BuildState) -> tuple[MarkClasses, list[str]]:
    """Mark class -> its marks, and the markClass statements declaring them."""
    classes: MarkClasses = {}
    lines: list[str] = []
    for gname, (kind, (x, y)) in state.mark_anchors.items():
        cls = dict(MARK_CLASSES)[kind]
        classes.setdefault(cls, []).append(gname)
        lines.append(f"markClass [{gname}] <anchor {round(x)} {round(y)}> @{cls};")
    return classes, lines


def _pos_base(gname: str, a: dict[str, Point], dx: float, classes: MarkClasses) -> str:
    parts = []
    for key, cls in MARK_CLASSES:
        if cls in classes:
            x, y = final(a[key], dx)
            parts.append(f"<anchor {round(x)} {round(y)}> mark @{cls}")
    return f"  pos base {gname} {' '.join(parts)};"


def _stack_depth(state: BuildState) -> float:
    """How far the deepest mark above hangs below its own anchor."""
    above = [
        (g, y) for g, (kind, (x, y)) in state.mark_anchors.items() if kind == "above"
    ]
    return max(y - state.writer.ink[g][1] for g, y in above)


def _stack_y(ink_top: float, depth: float) -> float:
    return ink_top + STACK_GAP + depth


def _letter_bases(state: BuildState, classes: MarkClasses) -> list[str]:
    bases = []
    for gname, dx in state.placed.items():
        if gname not in LETTER_OF and gname not in DOTLESS:
            continue
        bases.append(_pos_base(gname, anchors(state.glyphs[gname], gname), dx, classes))
    return bases


def _composite_bases(
    state: BuildState, classes: MarkClasses, depth: float
) -> list[str]:
    """Precomposed letters as bases: the next mark goes above their ink."""
    bases = []
    for gname, base in state.composite_bases.items():
        a = anchors(state.glyphs[base], base)
        a["above"] = (a["above"][0], _stack_y(state.writer.ink[gname][3], depth))
        bases.append(_pos_base(gname, a, state.placed[base], classes))
    return bases


def _mark_on_mark(state: BuildState, depth: float) -> list[str]:
    """Mark on mark (roadmap D4): every mark above carries a second anchor
    over its own ink, so a second mark sits on the first (ǘ ǚ, Pinyin;
    Vietnamese outside the precomposed stacks) instead of on top of it."""
    tan = math.tan(pen.SLANT)
    lines = []
    for g, (kind, (x, y)) in state.mark_anchors.items():
        if kind != "above":
            continue
        sy = _stack_y(state.writer.ink[g][3], depth)
        lines.append(
            f"  pos mark {g} <anchor {round(x + (sy - y) * tan)} {round(sy)}> mark @TOP;"
        )
    return lines


def set_gdef_classes(state: BuildState) -> None:
    gdef = state.font["GDEF"].table.GlyphClassDef.classDefs
    for gname in state.mark_anchors:
        gdef[gname] = GDEF_MARK  # Radon had these as "component" (4)
    for gname in list(state.placed) + list(state.composite_bases):
        gdef.setdefault(gname, GDEF_BASE)


def position_marks(state: BuildState) -> None:
    classes, lines = _mark_classes(state)
    depth = _stack_depth(state)
    bases = _letter_bases(state, classes) + _composite_bases(state, classes, depth)
    mkmk = _mark_on_mark(state, depth)
    fea = (
        "\n".join(lines)
        + "\nfeature mark {\n"
        + "\n".join(bases)
        + "\n} mark;\n"
        + "feature mkmk {\n"
        + "\n".join(mkmk)
        + "\n} mkmk;\n"
    )
    addOpenTypeFeaturesFromString(state.font, fea, tables=["GPOS"])
