"""Type names shared by the build modules."""

from collections.abc import Callable

from fontTools.ttLib.ttGlyphSet import _TTGlyphSet

Point = tuple[float, float]
Stroke = list[Point]
# A letter's drawing: called each time, it returns its upright strokes.
StrokesFn = Callable[[], list[Stroke]]
# Bounds as shapely gives them: (min x, min y, max x, max y).
Bounds = tuple[float, float, float, float]
# What TTFont.getGlyphSet() returns: glyph name -> a glyph that draws itself.
GlyphSet = _TTGlyphSet
