"""Type names shared by the build modules."""

from collections.abc import Callable
from typing import Literal

from fontTools.ttLib.ttGlyphSet import _TTGlyphSet

Point = tuple[float, float]
Stroke = list[Point]
# A letter's drawing: called each time, it returns its upright strokes.
StrokesFn = Callable[[], list[Stroke]]
# Bounds as shapely gives them: (min x, min y, max x, max y).
Bounds = tuple[float, float, float, float]
# What TTFont.getGlyphSet() returns: glyph name -> a glyph that draws itself.
GlyphSet = _TTGlyphSet

# A fitted outline segment: a line to a point, or a cubic to its end point.
Cubic = tuple[Point, Point, Point, Point]
Segment = tuple[Literal["L"], Point] | tuple[Literal["C"], Point, Point, Point]
# A skeleton drawing command for pen.path(): move, line, or cubic Bézier.
PathCmd = tuple[Literal["M", "L"], Point] | tuple[Literal["C"], Point, Point, Point]
