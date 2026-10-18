"""Fit cubic Béziers to the pen's polygon outlines (roadmap F1).

The nib sweep produces polygons: every curve arrives as dozens of short
straight segments, which facet at large sizes (the lock-screen clock) and
weigh down the file. This turns each ring back into curves:

1. Split the ring at real corners, the turns sharper than CORNER degrees.
   Those are the nib's square ends and the joins between strokes, and they
   stay sharp.
2. Fit each smooth run between corners with as few cubics as stay within
   ERROR font units of every original point. This is Schneider's algorithm,
   "An Algorithm for Automatically Fitting Digitized Curves" (Graphics Gems,
   1990): least-squares control points along fixed end tangents, Newton
   reparameterisation, and a split at the worst point when one cubic isn't
   enough.
3. Runs that are straight within ERROR stay lines.
"""

import math

from pen_types import Point, Stroke, Cubic, Segment

CORNER = 32  # degrees: a sharper turn is a corner of the nib
ERROR = 2.5  # font units (2000 per em): far below a pixel at any size


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def _add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def _mul(a, s):
    return (a[0] * s, a[1] * s)


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def _norm(a):
    n = math.hypot(*a)
    return (a[0] / n, a[1] / n) if n else (0.0, 0.0)


def _bez(ctrl, t):
    u = 1 - t
    return _add(
        _add(_mul(ctrl[0], u**3), _mul(ctrl[1], 3 * u * u * t)),
        _add(_mul(ctrl[2], 3 * u * t * t), _mul(ctrl[3], t**3)),
    )


def _bez_d1(ctrl, t):
    u = 1 - t
    return _add(
        _add(
            _mul(_sub(ctrl[1], ctrl[0]), 3 * u * u),
            _mul(_sub(ctrl[2], ctrl[1]), 6 * u * t),
        ),
        _mul(_sub(ctrl[3], ctrl[2]), 3 * t * t),
    )


def _bez_d2(ctrl, t):
    return _add(
        _mul(_add(_sub(ctrl[2], _mul(ctrl[1], 2)), ctrl[0]), 6 * (1 - t)),
        _mul(_add(_sub(ctrl[3], _mul(ctrl[2], 2)), ctrl[1]), 6 * t),
    )


def _chord_params(pts):
    u = [0.0]
    for a, b in zip(pts, pts[1:]):
        u.append(u[-1] + math.dist(a, b))
    total = u[-1] or 1.0
    return [x / total for x in u]


# The hot curve arithmetic below expands the helpers above (_bez, _bez_d1,
# _bez_d2, _dot, _mul, _add, _sub), operation for operation in the
# same order, so the floats come out bit-identical (the fonts don't change)
# while the 5 million helper calls per font disappear. A NumPy version was
# tried and was faster, but summed in another order: the last digits moved,
# a few round letters split differently, and after hinting O read closer to
# 0 at 12 px (0/O +0.046). So the arithmetic stays exactly as it was.
def _projection(p0: Point, p3: Point, point: Point, t: float) -> Point:
    w = 1 - t
    b0, b1, b2, b3 = w**3, 3 * w * w * t, 3 * w * t * t, t**3
    bx = (p0[0] * b0 + p0[0] * b1) + (p3[0] * b2 + p3[0] * b3)
    by = (p0[1] * b0 + p0[1] * b1) + (p3[1] * b2 + p3[1] * b3)
    return point[0] - bx, point[1] - by


def _normal_equations(
    pts: Stroke, u: list[float], t1: Point, t2: Point
) -> tuple[float, float, float, float, float]:
    c00 = c01 = c11 = x0 = x1 = 0.0
    for point, t in zip(pts, u):
        s1 = 3 * (1 - t) ** 2 * t
        s2 = 3 * (1 - t) * t * t
        a1x, a1y = t1[0] * s1, t1[1] * s1
        a2x, a2y = t2[0] * s2, t2[1] * s2
        c00 += a1x * a1x + a1y * a1y
        c01 += a1x * a2x + a1y * a2y
        c11 += a2x * a2x + a2y * a2y
        tx, ty = _projection(pts[0], pts[-1], point, t)
        x0 += a1x * tx + a1y * ty
        x1 += a2x * tx + a2y * ty
    return c00, c01, c11, x0, x1


def _control_distances(
    equations: tuple[float, float, float, float, float], seg: float
) -> tuple[float, float]:
    c00, c01, c11, x0, x1 = equations
    c10 = c01
    det = c00 * c11 - c01 * c10
    if abs(det) > 1e-12:
        al = (x0 * c11 - x1 * c01) / det
        ar = (c00 * x1 - c10 * x0) / det
    else:
        al = ar = seg / 3
    eps = 1e-6 * seg
    if al < eps or ar < eps:  # degenerate: Wu/Barsky heuristic
        al = ar = seg / 3
    return al, ar


def _generate(pts: Stroke, u: list[float], t1: Point, t2: Point) -> Cubic:
    """Least-squares cubic through pts with end tangents t1, t2."""
    p0, p3 = pts[0], pts[-1]
    al, ar = _control_distances(_normal_equations(pts, u, t1, t2), math.dist(p0, p3))
    return (
        p0,
        (p0[0] + t1[0] * al, p0[1] + t1[1] * al),
        (p3[0] + t2[0] * ar, p3[1] + t2[1] * ar),
        p3,
    )


def _max_error(pts, ctrl, u):
    (c0x, c0y), (c1x, c1y), (c2x, c2y), (c3x, c3y) = ctrl
    worst, idx = 0.0, len(pts) // 2
    dist = math.dist
    for i, (p, t) in enumerate(zip(pts, u)):
        w = 1 - t
        b0, b1, b2, b3 = w**3, 3 * w * w * t, 3 * w * t * t, t**3
        d = dist(
            (
                (c0x * b0 + c1x * b1) + (c2x * b2 + c3x * b3),
                (c0y * b0 + c1y * b1) + (c2y * b2 + c3y * b3),
            ),
            p,
        )
        if d > worst:
            worst, idx = d, i
    return worst, idx


def _reparam(pts, ctrl, u):
    (c0x, c0y), (c1x, c1y), (c2x, c2y), (c3x, c3y) = ctrl
    out = []
    for (px, py), t in zip(pts, u):
        w = 1 - t
        b0, b1, b2, b3 = w**3, 3 * w * w * t, 3 * w * t * t, t**3
        dx = ((c0x * b0 + c1x * b1) + (c2x * b2 + c3x * b3)) - px
        dy = ((c0y * b0 + c1y * b1) + (c2y * b2 + c3y * b3)) - py
        e0, e1, e2 = 3 * w * w, 6 * w * t, 3 * t * t
        d1x = ((c1x - c0x) * e0 + (c2x - c1x) * e1) + (c3x - c2x) * e2
        d1y = ((c1y - c0y) * e0 + (c2y - c1y) * e1) + (c3y - c2y) * e2
        f0, f1 = 6 * (1 - t), 6 * t
        d2x = ((c2x - c1x * 2) + c0x) * f0 + ((c3x - c2x * 2) + c1x) * f1
        d2y = ((c2y - c1y * 2) + c0y) * f0 + ((c3y - c2y * 2) + c1y) * f1
        den = (d1x * d1x + d1y * d1y) + (dx * d2x + dy * d2y)
        out.append(min(1.0, max(0.0, t - (dx * d1x + dy * d1y) / den)) if den else t)
    return out


def _refine_fit(
    pts: Stroke, u: list[float], t1: Point, t2: Point, err: float
) -> tuple[Cubic, float, int]:
    ctrl = _generate(pts, u, t1, t2)
    e, split = _max_error(pts, ctrl, u)
    if e < err or not e < err * 4:
        return ctrl, e, split
    for _ in range(6):
        u = _reparam(pts, ctrl, u)
        ctrl = _generate(pts, u, t1, t2)
        e, split = _max_error(pts, ctrl, u)
        if e < err:
            break
    return ctrl, e, split


def _fit(pts: Stroke, t1: Point, t2: Point, err: float, depth: int = 0) -> list[Cubic]:
    if len(pts) == 2:
        d = math.dist(pts[0], pts[1]) / 3
        return [(pts[0], _add(pts[0], _mul(t1, d)), _add(pts[1], _mul(t2, d)), pts[1])]
    ctrl, e, split = _refine_fit(pts, _chord_params(pts), t1, t2, err)
    if e < err or depth > 12:
        return [ctrl]
    split = min(max(split, 1), len(pts) - 2)
    tc = _norm(_sub(pts[split - 1], pts[split + 1]))
    return _fit(pts[: split + 1], t1, tc, err, depth + 1) + _fit(
        pts[split:], _mul(tc, -1), t2, err, depth + 1
    )


def _turn(a, b, c):
    v1, v2 = _sub(b, a), _sub(c, b)
    n1, n2 = math.hypot(*v1), math.hypot(*v2)
    if not n1 or not n2:
        return 0.0
    cos = max(-1.0, min(1.0, _dot(v1, v2) / (n1 * n2)))
    return math.degrees(math.acos(cos))


def _straight(run, err):
    a, b = run[0], run[-1]
    L = math.dist(a, b)
    if L == 0:
        return len(run) <= 2
    return all(
        abs((b[0] - a[0]) * (a[1] - p[1]) - (a[0] - p[0]) * (b[1] - a[1])) / L <= err
        for p in run
    )


def _densify(run, step=12.0):
    """Extra points along long edges, so the fit's error is checked between
    the polygon's vertices too, not only at them."""
    out = [run[0]]
    for a, b in zip(run, run[1:]):
        k = int(math.dist(a, b) // step)
        for s in range(1, k + 1):
            t = s / (k + 1)
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
        out.append(b)
    return out


def _ring_corners(ring: Stroke, corner: float) -> list[int]:
    n = len(ring)
    turns = [_turn(ring[i - 1], ring[i], ring[(i + 1) % n]) for i in range(n)]
    corners = {i for i in range(n) if turns[i] > corner}
    # A corner the polygon split across two close vertices (two 30° turns
    # for one 60° corner) is still a corner: keep the sharper of the pair.
    for i in range(n):
        j = (i + 1) % n
        if (
            math.dist(ring[i], ring[j]) < 25
            and turns[i] > 8
            and turns[j] > 8
            and turns[i] + turns[j] > corner
            and i not in corners
            and j not in corners
        ):
            corners.add(i if turns[i] >= turns[j] else j)
    return sorted(corners)


def _ring_splits(ring: Stroke, corner: float) -> tuple[list[int], set[int]]:
    corners = _ring_corners(ring, corner)
    if not corners:  # a smooth closed loop: split at two far points
        return [0, len(ring) // 2], {0, len(ring) // 2}
    if len(corners) == 1:  # one corner: add a smooth split opposite it, or
        k = (corners[0] + len(ring) // 2) % len(ring)  # the run would close on itself
        return sorted([corners[0], k]), {k}
    return corners, set()


def _centred_tangent(ring: Stroke, k: int) -> Point:
    # Tangent through a smooth split point.
    return _norm(_sub(ring[(k + 1) % len(ring)], ring[k - 1]))


def _fit_run(
    ring: Stroke, i: int, j: int, smooth: set[int], err: float
) -> list[Segment]:
    n = len(ring)
    run = [ring[k % n] for k in range(i, (j if j > i else j + n) + 1)]
    if len(run) < 2:
        return []
    run = _densify(run)
    if len(run) == 2 or _straight(run, err):
        return [("L", run[-1])]
    t1 = _centred_tangent(ring, i) if i in smooth else _norm(_sub(run[1], run[0]))
    t2 = (
        _mul(_centred_tangent(ring, j), -1)
        if j in smooth
        else _norm(_sub(run[-2], run[-1]))
    )
    return [("C", c[1], c[2], c[3]) for c in _fit(run, t1, t2, err)]


def fit_ring(
    ring: Stroke, err: float = ERROR, corner: float = CORNER
) -> tuple[Point, list[Segment]]:
    """Fit a closed ring without its repeated last point, preserving corners.

    Returns a start and ('L', end) / ('C', c1, c2, end) segments.
    Example: ``start, segments = fit_ring([(0, 0), (10, 0), (0, 10)])``.
    """
    if len(ring) < 3:
        return ring[0], [("L", p) for p in ring[1:]]
    corners, smooth = _ring_splits(ring, corner)
    segs = []
    for ci, i in enumerate(corners):
        j = corners[(ci + 1) % len(corners)]
        segs.extend(_fit_run(ring, i, j, smooth, err))
    return ring[corners[0]], segs
