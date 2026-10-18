#!/usr/bin/env python3
"""Jandí Mono's broad-nib pen engine.

Each letter is a centerline skeleton (cubic Béziers, drawn upright; see
tools/letters.py). The skeleton is slanted, then a rectangular nib at ONE
fixed angle is swept along it. Thick and thin are never drawn by hand: they
fall out of the pen angle, the same for every letter. That constancy is the
"Renaissance precision".

An 18th-century pointed quill with pressure (Figueiredo's own) was tried
for the Italic and measured worse (build_options.py); it lives in git
history before 1.0.0-beta.1.
"""

import math

import numpy as np
import shapely
from shapely import affinity
from shapely.geometry import Polygon
from shapely.ops import unary_union

ADV, XH = 1240, 1027  # Radon's grid, measured; merge.py sets ADV to the cell
SLANT = math.radians(7)  # one slant for the whole alphabet
PEN = math.radians(35)  # chancery pen angle


def cubic(p0, p1, p2, p3, n=48):
    out = []
    for i in range(1, n + 1):
        s = i / n
        a = (1 - s) ** 3
        b = 3 * (1 - s) ** 2 * s
        c = 3 * (1 - s) * s**2
        d = s**3
        out.append(
            (
                a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0],
                a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1],
            )
        )
    return out


def line(p0, p1, step=24):
    n = max(1, int(math.dist(p0, p1) / step))
    return [
        (p0[0] + (p1[0] - p0[0]) * i / n, p0[1] + (p1[1] - p0[1]) * i / n)
        for i in range(1, n + 1)
    ]


def path(*cmds):
    """cmds: ('M',p) ('L',p) ('C',c1,c2,p) -> list of points"""
    pts = []
    for c in cmds:
        if c[0] == "M":
            pts = [c[1]]
        elif c[0] == "L":
            pts += line(pts[-1], c[1])
        elif c[0] == "C":
            pts += cubic(pts[-1], c[1], c[2], c[3])
    return pts


def ellipse(cx, cy, rx, ry, n=160, start=math.pi / 2):
    return [
        (
            cx + rx * math.cos(start + 2 * math.pi * i / n),
            cy + ry * math.sin(start + 2 * math.pi * i / n),
        )
        for i in range(n + 1)
    ]


# ---------------------------------------------------------------- the pen
def slant(pts):
    return [(x + y * math.tan(SLANT), y) for x, y in pts]


def sweep(pts, w, t):
    return sweep_broad(pts, w, t)


def sweep_broad(pts, w, t):
    """The nib (a w×t rectangle at PEN) dragged along pts: for each segment,
    the convex hull of the nib at both ends, all unioned. Vectorised with
    NumPy and Shapely 2's array functions: the same geometry as building one
    hull per segment in Python, a fraction of the time (the sweep was a third
    of every build)."""
    ux, uy = (w / 2) * math.cos(PEN), (w / 2) * math.sin(PEN)
    vx, vy = -(t / 2) * math.sin(PEN), (t / 2) * math.cos(PEN)
    P = np.asarray(pts, dtype=float)
    if len(P) < 2:
        return unary_union([])
    # (x + ux) + vx, in that order, exactly as the one-hull-at-a-time code
    # did: summing ux + vx first moves the last digit, and a last-digit change
    # is enough to fit a round letter differently (and hint it differently).
    U = np.array([[ux, uy], [ux, uy], [-ux, -uy], [-ux, -uy]])
    V = np.array([[vx, vy], [-vx, -vy], [vx, vy], [-vx, -vy]])
    corners = (P[:, None, :] + U[None, :, :]) + V[None, :, :]  # (n, 4, 2)
    seg = np.concatenate([corners[:-1], corners[1:]], axis=1)  # (n-1, 8, 2)
    return shapely.union_all(shapely.convex_hull(shapely.multipoints(seg)))


OPTICAL = 0  # 0 = box centre, 1 = ink centroid; merge.py sets it per letter


def place(upright_strokes, w, t, dx=None, band_top=XH):
    """Slant, sweep and centre a set of upright strokes. Returns (shape, dx).
    Pass dx to reuse a base letter's centring for its accented forms.
    band_top: centre on 0..x-height for lowercase, 0..cap height for capitals
    and figures (otherwise an F or a P would centre on its lone stem)."""
    shape = unary_union([sweep(slant(s), w, t) for s in upright_strokes])
    if dx is None:
        band = shape.intersection(
            Polygon([(-2000, 0), (4000, 0), (4000, band_top), (-2000, band_top)])
        )
        minx, _, maxx, _ = band.bounds
        centre = (1 - OPTICAL) * (minx + maxx) / 2 + OPTICAL * band.centroid.x
        dx = ADV / 2 - centre
    return affinity.translate(shape, dx, 0), dx
