"""What the build steps share while one font is made."""

from dataclasses import dataclass, field

from fontTools.ttLib import TTFont

from build_options import BuildOptions
from glyph_table import Letter
from glyph_writer import GlyphWriter
from pen_types import Point


@dataclass
class BuildState:
    """One font in the making. Each step in merge.py reads and extends it.

    placed: base glyph -> its x offset in the cell (accented forms reuse it).
    mark_anchors: combining mark -> (kind, its anchor in the final glyph).
    composite_bases: precomposed letter with a mark above -> its base letter.
    """

    opts: BuildOptions
    font: TTFont
    writer: GlyphWriter
    glyphs: dict[str, Letter]
    placed: dict[str, float] = field(default_factory=dict)
    replaced: list[str] = field(default_factory=list)
    pen_glyphs: list[str] = field(default_factory=list)
    mark_anchors: dict[str, tuple[str, Point]] = field(default_factory=dict)
    composite_bases: dict[str, str] = field(default_factory=dict)

    @property
    def nib(self) -> tuple[float, float]:
        return self.opts.nib
