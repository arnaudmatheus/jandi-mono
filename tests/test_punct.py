"""Punctuation and restroked symbols (tools/punct.py)."""

import shapely
from shapely.geometry import Polygon

import punct
from conftest import square, tiny_font

RADON_STROKE = 100


def parallelogram(x0: float, x1: float, width: float = RADON_STROKE) -> Polygon:
    """A slash-like diagonal stroke from (x0, -300) to (x1, 1500)."""
    return Polygon([(x0, -300), (x0 + width, -300), (x1 + width, 1500), (x1, 1500)])


def test_diagonal_stroke_survives_the_restroke():
    # Regression: the first restroke thinned outlines with a mitred negative
    # buffer, and diagonals (/ \ x) vanished. The centreline keeps them.
    slash = parallelogram(100, 900)
    out = punct.restroke(slash, 138, 106, 0, RADON_STROKE)
    assert not out.is_empty
    assert out.bounds[3] - out.bounds[1] > 0.9 * (slash.bounds[3] - slash.bounds[1])


def test_solid_shape_stays_solid():
    # The filled triangle of |> is not a stroke: it is kept, not re-stroked.
    triangle = Polygon([(100, 100), (900, 640), (100, 1180)])
    out = punct.restroke(triangle, 138, 106, 0, RADON_STROKE)
    assert abs(out.area - triangle.area) < 1e-6


def test_round_dot_becomes_a_drop():
    dot = shapely.Point(580, 140).buffer(110)
    out = punct.restroke(dot, 138, 106, 0, RADON_STROKE)
    expected = punct.drop_shape(0, out.centroid.y, 138, 106)
    assert abs(out.area - expected.area) / expected.area < 0.05


def test_overlapping_contours_are_ink_not_holes():
    # Radon draws the bars of # and the stroke through != as overlapping
    # contours; nonzero winding keeps the overlap inked, even-odd punched it.
    font = tiny_font({"numbersign": [square(100, 100, 400), square(300, 300, 400)]})
    shape = punct.outline(font.getGlyphSet(), "numbersign")
    assert abs(shape.area - (2 * 400 * 400 - 200 * 200)) < 1.0
    assert len(shape.interiors) == 0


def test_clockwise_contour_is_a_counter():
    outer = square(0, 0, 600)
    hole = list(reversed(square(200, 200, 200)))
    shape = punct.outline(tiny_font({"o": [outer, hole]}).getGlyphSet(), "o")
    assert abs(shape.area - (600 * 600 - 200 * 200)) < 1.0


def test_centreline_fallback_for_a_shape_smaller_than_clearance() -> None:
    tiny = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    assert punct.centreline(tiny, 100) == [[(0.5, 0.5), (1.5, 1.5)]]


def test_junctions_stay_connected_while_loose_ends_extend() -> None:
    cross = shapely.union_all(
        [shapely.box(0, 400, 1000, 500), shapely.box(450, 0, 550, 900)]
    )
    lines = punct.centreline(cross, 100)
    endpoints = [point for line in lines for point in (line[0], line[-1])]
    assert any(endpoints.count(point) > 1 for point in endpoints)
    assert min(x for x, _ in endpoints) < 40
    assert max(x for x, _ in endpoints) > 960
    assert all(cross.covers(shapely.LineString(line)) for line in lines)


def test_empty_restroke_is_still_empty() -> None:
    empty = Polygon()
    assert punct.restroke(empty, 138, 106, 7, 100).is_empty
