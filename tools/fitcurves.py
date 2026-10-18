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

CORNER = 32          # degrees: a sharper turn is a corner of the nib
ERROR = 2.5          # font units (2000 per em): far below a pixel at any size

def _sub(a, b): return (a[0] - b[0], a[1] - b[1])
def _add(a, b): return (a[0] + b[0], a[1] + b[1])
def _mul(a, s): return (a[0] * s, a[1] * s)
def _dot(a, b): return a[0] * b[0] + a[1] * b[1]
def _norm(a):
    n = math.hypot(*a)
    return (a[0] / n, a[1] / n) if n else (0.0, 0.0)

def _bez(ctrl, t):
    u = 1 - t
    return _add(_add(_mul(ctrl[0], u ** 3), _mul(ctrl[1], 3 * u * u * t)),
                _add(_mul(ctrl[2], 3 * u * t * t), _mul(ctrl[3], t ** 3)))

def _bez_d1(ctrl, t):
    u = 1 - t
    return _add(_add(_mul(_sub(ctrl[1], ctrl[0]), 3 * u * u), _mul(_sub(ctrl[2], ctrl[1]), 6 * u * t)),
                _mul(_sub(ctrl[3], ctrl[2]), 3 * t * t))

def _bez_d2(ctrl, t):
    return _add(_mul(_add(_sub(ctrl[2], _mul(ctrl[1], 2)), ctrl[0]), 6 * (1 - t)),
                _mul(_add(_sub(ctrl[3], _mul(ctrl[2], 2)), ctrl[1]), 6 * t))

def _chord_params(pts):
    u = [0.0]
    for a, b in zip(pts, pts[1:]):
        u.append(u[-1] + math.dist(a, b))
    total = u[-1] or 1.0
    return [x / total for x in u]

def _generate(pts, u, t1, t2):
    """Least-squares cubic through pts with end tangents t1, t2."""
    p0, p3 = pts[0], pts[-1]
    C = [[0.0, 0.0], [0.0, 0.0]]; X = [0.0, 0.0]
    for p, t in zip(pts, u):
        a1 = _mul(t1, 3 * (1 - t) ** 2 * t)
        a2 = _mul(t2, 3 * (1 - t) * t * t)
        C[0][0] += _dot(a1, a1); C[0][1] += _dot(a1, a2); C[1][1] += _dot(a2, a2)
        tmp = _sub(p, _bez((p0, p0, p3, p3), t))
        X[0] += _dot(a1, tmp); X[1] += _dot(a2, tmp)
    C[1][0] = C[0][1]
    det = C[0][0] * C[1][1] - C[0][1] * C[1][0]
    seg = math.dist(p0, p3)
    if abs(det) > 1e-12:
        al = (X[0] * C[1][1] - X[1] * C[0][1]) / det
        ar = (C[0][0] * X[1] - C[1][0] * X[0]) / det
    else:
        al = ar = seg / 3
    eps = 1e-6 * seg
    if al < eps or ar < eps:                       # degenerate: Wu/Barsky heuristic
        al = ar = seg / 3
    return (p0, _add(p0, _mul(t1, al)), _add(p3, _mul(t2, ar)), p3)

def _max_error(pts, ctrl, u):
    worst, idx = 0.0, len(pts) // 2
    for i, (p, t) in enumerate(zip(pts, u)):
        d = math.dist(_bez(ctrl, t), p)
        if d > worst:
            worst, idx = d, i
    return worst, idx

def _reparam(pts, ctrl, u):
    out = []
    for p, t in zip(pts, u):
        d = _sub(_bez(ctrl, t), p)
        d1, d2 = _bez_d1(ctrl, t), _bez_d2(ctrl, t)
        den = _dot(d1, d1) + _dot(d, d2)
        out.append(min(1.0, max(0.0, t - _dot(d, d1) / den)) if den else t)
    return out

def _fit(pts, t1, t2, err, depth=0):
    if len(pts) == 2:
        d = math.dist(pts[0], pts[1]) / 3
        return [(pts[0], _add(pts[0], _mul(t1, d)), _add(pts[1], _mul(t2, d)), pts[1])]
    u = _chord_params(pts)
    ctrl = _generate(pts, u, t1, t2)
    e, split = _max_error(pts, ctrl, u)
    if e < err:
        return [ctrl]
    if e < err * 4:
        for _ in range(6):
            u = _reparam(pts, ctrl, u)
            ctrl = _generate(pts, u, t1, t2)
            e, split = _max_error(pts, ctrl, u)
            if e < err:
                return [ctrl]
    if depth > 12:
        return [ctrl]
    split = min(max(split, 1), len(pts) - 2)
    tc = _norm(_sub(pts[split - 1], pts[split + 1]))
    return _fit(pts[:split + 1], t1, tc, err, depth + 1) + \
           _fit(pts[split:], _mul(tc, -1), t2, err, depth + 1)

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
    return all(abs((b[0] - a[0]) * (a[1] - p[1]) - (a[0] - p[0]) * (b[1] - a[1])) / L <= err for p in run)

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

def fit_ring(ring, err=ERROR, corner=CORNER):
    """ring: closed list of (x, y) without the repeated last point.
    Returns segments: ('L', p1) or ('C', c1, c2, p3); the first point is ring[k]
    returned separately as the start."""
    n = len(ring)
    if n < 3:
        return ring[0], [('L', p) for p in ring[1:]]
    turns = [_turn(ring[i - 1], ring[i], ring[(i + 1) % n]) for i in range(n)]
    corners = {i for i in range(n) if turns[i] > corner}
    # A corner the polygon split across two close vertices (two 30° turns
    # for one 60° corner) is still a corner: keep the sharper of the pair.
    for i in range(n):
        j = (i + 1) % n
        if (math.dist(ring[i], ring[j]) < 25 and turns[i] > 8 and turns[j] > 8
                and turns[i] + turns[j] > corner and i not in corners and j not in corners):
            corners.add(i if turns[i] >= turns[j] else j)
    corners = sorted(corners)
    smooth = set()
    if not corners:                                   # a smooth closed loop: split at two far points
        corners = [0, n // 2]; smooth = {0, n // 2}
    elif len(corners) == 1:                           # one corner: add a smooth split opposite it, or
        k = (corners[0] + n // 2) % n                 # the run would start and end on the same point
        corners = sorted([corners[0], k]); smooth = {k}
    def centred(k):                                   # tangent through a smooth split point
        return _norm(_sub(ring[(k + 1) % n], ring[k - 1]))
    start = ring[corners[0]]
    segs = []
    for ci, i in enumerate(corners):
        j = corners[(ci + 1) % len(corners)]
        run = [ring[k % n] for k in range(i, (j if j > i else j + n) + 1)]
        if len(run) < 2:
            continue
        run = _densify(run)
        if len(run) == 2 or _straight(run, err):
            segs.append(('L', run[-1]))
            continue
        t1 = centred(i) if i in smooth else _norm(_sub(run[1], run[0]))
        t2 = _mul(centred(j), -1) if j in smooth else _norm(_sub(run[-2], run[-1]))
        for c in _fit(run, t1, t2, err):
            segs.append(('C', c[1], c[2], c[3]))
    return start, segs
