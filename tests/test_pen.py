"""The broad-nib engine (tools/pen.py)."""

import math

import shapely
from shapely.geometry import MultiPoint

import letters
import pen


def sweep_one_hull_at_a_time(pts, w, t):
    """The sweep as it was first written: one convex hull per segment.

    sweep_broad vectorised this; it must still give these exact floats.
    """
    ux, uy = (w / 2) * math.cos(pen.PEN), (w / 2) * math.sin(pen.PEN)
    vx, vy = -(t / 2) * math.sin(pen.PEN), (t / 2) * math.cos(pen.PEN)

    def corners(x, y):
        return [
            ((x + ux) + vx, (y + uy) + vy),
            ((x + ux) - vx, (y + uy) - vy),
            ((x - ux) + vx, (y - uy) + vy),
            ((x - ux) - vx, (y - uy) - vy),
        ]

    hulls = [
        MultiPoint(corners(*a) + corners(*b)).convex_hull for a, b in zip(pts, pts[1:])
    ]
    return shapely.union_all(hulls)


def test_vectorised_sweep_is_bit_identical():
    # Regression: an earlier vectorisation summed ux + vx before adding the
    # point. Only the last digit moved, but that refitted a round letter and,
    # after hinting, O read closer to 0 (0/O +0.046 at 12 px).
    skeleton = pen.path(("M", (330, 640)), *letters.ARCH, ("L", (905, 170)))
    fast = pen.sweep_broad(skeleton, 138, 106)
    slow = sweep_one_hull_at_a_time(skeleton, 138, 106)
    assert shapely.to_wkb(fast) == shapely.to_wkb(slow)


def test_sweep_of_a_single_point_is_empty():
    assert pen.sweep_broad([(100, 100)], 138, 106).is_empty


def test_nib_angle_sets_thick_and_thin():
    # At 35°, a vertical stroke is thicker than a horizontal one: the
    # contrast comes from the pen, never from drawing.
    vertical = pen.sweep_broad(pen.path(("M", (500, 0)), ("L", (500, 1000))), 138, 106)
    horizontal = pen.sweep_broad(
        pen.path(("M", (0, 500)), ("L", (1000, 500))), 138, 106
    )
    v_width = vertical.bounds[2] - vertical.bounds[0]
    h_width = horizontal.bounds[3] - horizontal.bounds[1]
    assert v_width > h_width


def test_place_centres_the_x_height_band_in_the_cell():
    shape, dx = pen.place(letters.LETTERS["o"](), 138, 106)
    band = shape.intersection(shapely.box(-2000, 0, 4000, pen.XH))
    assert abs((band.bounds[0] + band.bounds[2]) / 2 - pen.ADV / 2) < 1e-6


def test_place_reuses_a_given_offset():
    _, dx = pen.place(letters.LETTERS["n"](), 138, 106)
    _, again = pen.place(letters.LETTERS["n"](), 138, 106, dx=dx)
    assert again == dx
