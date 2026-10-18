"""The curve fitter (tools/fitcurves.py) keeps the shape it is given."""

import math
import random

from shapely.geometry import Polygon

import fitcurves
from fitcurves import _bez, _bez_d1, _bez_d2, _dot, _mul, _sub


def sample(start, segs, steps: int = 24) -> list[tuple[float, float]]:
    """The fitted outline flattened back to points, to compare as a polygon."""
    pts, cur = [start], start
    for seg in segs:
        if seg[0] == "L":
            cur = seg[1]
            pts.append(cur)
            continue
        ctrl = (cur, seg[1], seg[2], seg[3])
        pts += [_bez(ctrl, i / steps) for i in range(1, steps + 1)]
        cur = seg[3]
    return pts


def fitted_area_error(ring: list[tuple[float, float]]) -> float:
    """Area between the ring and its fitted curves, as a share of the ring's area."""
    start, segs = fitcurves.fit_ring(ring)
    original, fitted = Polygon(ring), Polygon(sample(start, segs))
    return original.symmetric_difference(fitted).area / original.area


def teardrop(tip: float = 140, n: int = 60) -> list[tuple[float, float]]:
    """An arc closed by one sharp tip: a ring with exactly one corner."""
    arc = [
        (100 * math.cos(a), 100 * math.sin(a))
        for a in (math.radians(30 + 300 * i / n) for i in range(n + 1))
    ]
    return [(tip, 0), *arc]


def test_single_corner_ring_keeps_its_shape():
    # Regression: a ring with one corner ran from that corner back to itself,
    # and the fit filled the counters of round letters (see FONTLOG 0.7.0).
    ring = teardrop()
    turns = [
        fitcurves._turn(ring[i - 1], ring[i], ring[(i + 1) % len(ring)])
        for i in range(len(ring))
    ]
    assert sum(t > fitcurves.CORNER for t in turns) == 1
    assert fitted_area_error(ring) < 0.01


def test_long_straight_edges_do_not_bulge():
    # Regression: between two far-apart vertices the fit was only checked at
    # the vertices, so long edges bowed outward; _densify checks between them.
    left = [
        (-300 + 100 * math.cos(a), 100 * math.sin(a))
        for a in (math.radians(90 + 180 * i / 20) for i in range(21))
    ]
    right = [
        (300 + 100 * math.cos(a), 100 * math.sin(a))
        for a in (math.radians(-90 + 180 * i / 20) for i in range(21))
    ]
    assert fitted_area_error(right + left) < 0.01


def test_smooth_loop_without_corners_is_fitted():
    circle = [
        (200 * math.cos(2 * math.pi * i / 80), 200 * math.sin(2 * math.pi * i / 80))
        for i in range(80)
    ]
    start, segs = fitcurves.fit_ring(circle)
    assert all(seg[0] == "C" for seg in segs)
    assert fitted_area_error(circle) < 0.005


def test_square_stays_four_lines():
    start, segs = fitcurves.fit_ring([(0, 0), (500, 0), (500, 500), (0, 500)])
    assert [s[0] for s in segs] == ["L"] * 4
    assert segs[-1][1] == start


# The hot functions are written out inline for speed. They must give the
# same floats, bit for bit, as the helpers they replace: a last-digit change
# fitted round letters differently and, once hinted, O read closer to 0
# (0/O +0.046 at 12 px). These compare against the helper versions.


def _random_case(seed: int):
    rng = random.Random(seed)
    pts = [(rng.uniform(-500, 500), rng.uniform(-500, 500)) for _ in range(30)]
    u = sorted(rng.random() for _ in range(30))
    ctrl = tuple((rng.uniform(-500, 500), rng.uniform(-500, 500)) for _ in range(4))
    return pts, u, ctrl


def _max_error_by_helpers(pts, ctrl, u):
    worst, idx = 0.0, len(pts) // 2
    for i, (p, t) in enumerate(zip(pts, u)):
        d = math.dist(_bez(ctrl, t), p)
        if d > worst:
            worst, idx = d, i
    return worst, idx


def _reparam_by_helpers(pts, ctrl, u):
    out = []
    for p, t in zip(pts, u):
        d = _sub(_bez(ctrl, t), p)
        d1, d2 = _bez_d1(ctrl, t), _bez_d2(ctrl, t)
        den = _dot(d1, d1) + _dot(d, d2)
        out.append(min(1.0, max(0.0, t - _dot(d, d1) / den)) if den else t)
    return out


def _generate_by_helpers(pts, u, t1, t2):
    p0, p3 = pts[0], pts[-1]
    c00 = c01 = c11 = x0 = x1 = 0.0
    for p, t in zip(pts, u):
        a1, a2 = _mul(t1, 3 * (1 - t) ** 2 * t), _mul(t2, 3 * (1 - t) * t * t)
        c00, c01, c11 = c00 + _dot(a1, a1), c01 + _dot(a1, a2), c11 + _dot(a2, a2)
        tmp = _sub(p, _bez((p0, p0, p3, p3), t))
        x0, x1 = x0 + _dot(a1, tmp), x1 + _dot(a2, tmp)
    det = c00 * c11 - c01 * c01
    al, ar = (x0 * c11 - x1 * c01) / det, (c00 * x1 - c01 * x0) / det
    return al, ar


def test_inlined_max_error_is_bit_identical():
    for seed in range(20):
        pts, u, ctrl = _random_case(seed)
        assert fitcurves._max_error(pts, ctrl, u) == _max_error_by_helpers(pts, ctrl, u)


def test_inlined_reparam_is_bit_identical():
    for seed in range(20):
        pts, u, ctrl = _random_case(seed)
        assert fitcurves._reparam(pts, ctrl, u) == _reparam_by_helpers(pts, ctrl, u)


def test_inlined_generate_is_bit_identical():
    t1, t2 = (0.6, 0.8), (-0.8, 0.6)
    for seed in range(20):
        pts, u, _ = _random_case(seed)
        _, c1, c2, _ = fitcurves._generate(pts, u, t1, t2)
        al, ar = _generate_by_helpers(pts, u, t1, t2)
        if min(al, ar) < 1e-6 * math.dist(pts[0], pts[-1]):
            continue  # the degenerate fallback, not the arithmetic under test
        assert c1 == (pts[0][0] + t1[0] * al, pts[0][1] + t1[1] * al)
        assert c2 == (pts[-1][0] + t2[0] * ar, pts[-1][1] + t2[1] * ar)
