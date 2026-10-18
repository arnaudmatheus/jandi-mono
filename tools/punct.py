"""Punctuation, symbols and ligatures with the pen (roadmap E1, E2).

Two ways in:
- DRAWN: the punctuation that carries the pen's character is drawn from
  skeletons like the letters. Its unit is the drop (gota): the teardrop a
  broad nib leaves when it turns on the spot, the same drop as the Baroque
  ball terminals. Period, comma, colon, semicolon, quotes, ! and ? are drops
  and strokes; braces are the carved C-scroll, an S-curve with a pointed
  middle.
- RESTROKED: code symbols and every ligature keep Radon's geometry, which is
  what makes == -> |> join across cells, but lose Radon's marker stroke: the
  outline is thinned to its core and our nib is swept over it (a Minkowski
  sum with the nib rectangle), so thick and thin come from the same 35° pen.
  Round dots inside them become drops.

Both are sheared from Radon's angle (Regular 0°, Italic 11°) to Jandí's
(7°, 13°) around the math axis, so a bar across two cells stays one bar."""

import math
import numpy as np
import shapely
from shapely.geometry import MultiPoint, Point, MultiLineString
from shapely.geometry.base import BaseGeometry
from shapely.ops import voronoi_diagram, linemerge
from pen_types import Stroke, Point as XY
from fontTools.pens.basePen import BasePen
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import affinity
import pen
from pen import path

AXIS = 646  # Radon's math axis: the middle of = and -

# --------------------------------------------------------------- the drop
DROP_R = 112  # body radius of the drop: Radon-sized code punctuation


def DROP(x, y, r=DROP_R):
    """A teardrop: a small loop swept by the nib and filled, its point up and
    to the right along the pen angle. r sets the size of the round body."""
    tip = (x + 0.75 * r, y + 1.15 * r)
    return [
        ("M", tip),
        ("C", (x + 0.2 * r, y + 1.5 * r), (x - r, y + 0.7 * r), (x - r, y)),
        ("C", (x - r, y - 0.75 * r), (x - 0.4 * r, y - r), (x + 0.15 * r, y - r)),
        (
            "C",
            (x + 0.8 * r, y - r),
            (x + 1.05 * r, y - 0.35 * r),
            (x + 0.9 * r, y + 0.35 * r),
        ),
        ("C", (x + 0.85 * r, y + 0.75 * r), tip, tip),
    ]


def drop_shape(x, y, w, t, r=DROP_R):
    """The drop as ink: the swept loop plus its filled body."""
    pts = pen.slant(path(*DROP(x, y, r)))
    return unary_union([pen.sweep(pts, w, t), Polygon(pts).buffer(0)])


# --------------------------------------------------------------- drawn
# Upright skeletons around x = 0; merge places them on Radon's centre.
BASE = 140  # centre of a drop resting on the baseline (ink bottom ≈ -35, like Radon)
XDOT = 930  # centre of the upper dot of : and ;

PAREN_W, PAREN_BOW = 260, 420  # deep bows: (/[ 0.878 -> 0.802 at 12 px
BRACE_POINT = 450  # the carved scroll's point: [/{ 0.914 -> 0.885 at 12 px
COMMA_HEAD = 0.75  # the comma's head is a smaller drop than the period
COLON_R = 0.85  # : and ; dots, a little under the period's drop


def _comma_tail(y, r=DROP_R):
    # Out of the head's lower right, straight down while the nib is at full
    # width, turning left only at the end, where it thins to a hairline. The
    # tail is what tells , from . and ; from :, so it is long, like Radon's.
    # Measured (12/15/20 px): a tail that turned left at once vanished at
    # 12 px (; read as :, 0.947); this one keeps both pairs within 0.01 of
    # 0.5.0 and stays inside the 500-unit descent.
    return path(
        ("M", (0.55 * r, y - 0.2 * r)),
        (
            "C",
            (0.75 * r, y - 2.55 * r),
            (0.5 * r, y - 4.1 * r),
            (-0.3 * r, y - 4.9 * r),
        ),
    )


DRAWN = {
    "period": lambda: ([], [(0, BASE)]),
    "comma": lambda: ([_comma_tail(BASE)], [(0, BASE)]),
    "colon": lambda: ([], [(0, BASE), (0, XDOT)]),
    "semicolon": lambda: ([_comma_tail(BASE)], [(0, BASE), (0, XDOT)]),
    "quotesingle": lambda: ([path(("M", (0, 1500)), ("L", (-10, 850)))], []),
    "quotedbl": lambda: (
        [
            path(("M", (-170, 1500)), ("L", (-180, 850))),
            path(("M", (170, 1500)), ("L", (160, 850))),
        ],
        [],
    ),
    # The stroke ends well above the drop: with 430, Bold closed the gap.
    "exclam": lambda: ([path(("M", (10, 1470)), ("L", (0, 540)))], [(0, BASE)]),
    "question": lambda: (
        [
            path(
                ("M", (-250, 1230)),
                ("C", (-250, 1400), (-120, 1478), (20, 1478)),
                ("C", (180, 1478), (270, 1380), (270, 1235)),
                ("C", (270, 1060), (10, 1010), (0, 790)),
                ("L", (0, 540)),
            )
        ],
        [(0, BASE)],
    ),
    # Deep bows, so ( never reads as a leaning [.
    "parenleft": lambda: (
        [
            path(
                ("M", (PAREN_W, 1560)),
                ("C", (-PAREN_BOW, 1160), (-PAREN_BOW, -20), (PAREN_W, -400)),
            )
        ],
        [],
    ),
    "parenright": lambda: (
        [
            path(
                ("M", (-PAREN_W, 1560)),
                ("C", (PAREN_BOW, 1160), (PAREN_BOW, -20), (-PAREN_W, -400)),
            )
        ],
        [],
    ),
    # Long arms: the square corners are what separate [ from ( and {.
    "bracketleft": lambda: (
        [
            path(
                ("M", (290, 1590)),
                ("L", (-170, 1590)),
                ("L", (-170, -400)),
                ("L", (290, -400)),
            )
        ],
        [],
    ),
    "bracketright": lambda: (
        [
            path(
                ("M", (-290, 1590)),
                ("L", (170, 1590)),
                ("L", (170, -400)),
                ("L", (-290, -400)),
            )
        ],
        [],
    ),
    # The carved C-scroll: two curves that meet in a point at the middle.
    "braceleft": lambda: (
        [
            path(
                ("M", (240, 1590)),
                ("C", (60, 1590), (10, 1500), (10, 1300)),
                ("L", (10, 900)),
                ("C", (10, 720), (-60, AXIS + 20), (-BRACE_POINT, AXIS)),
            ),
            path(
                ("M", (-BRACE_POINT, AXIS)),
                ("C", (-60, AXIS - 20), (10, 570), (10, 390)),
                ("L", (10, -10)),
                ("C", (10, -310), (60, -400), (240, -400)),
            ),
        ],
        [],
    ),
    "braceright": lambda: (
        [
            path(
                ("M", (-240, 1590)),
                ("C", (-60, 1590), (-10, 1500), (-10, 1300)),
                ("L", (-10, 900)),
                ("C", (-10, 720), (60, AXIS + 20), (BRACE_POINT, AXIS)),
            ),
            path(
                ("M", (BRACE_POINT, AXIS)),
                ("C", (60, AXIS - 20), (-10, 570), (-10, 390)),
                ("L", (-10, -10)),
                ("C", (-10, -310), (-60, -400), (-240, -400)),
            ),
        ],
        [],
    ),
}


def drawn_shape(name, w, t):
    strokes, drops = DRAWN[name]()
    parts = [pen.sweep(pen.slant(s), w, t) for s in strokes]
    colon_r = COLON_R * DROP_R

    def r_for(y):
        if name == "comma" or (name == "semicolon" and y == BASE):
            return COMMA_HEAD * (colon_r if name == "semicolon" else DROP_R)
        return colon_r if name in ("colon", "semicolon") else DROP_R

    parts += [drop_shape(x, y, w, t, r_for(y)) for x, y in drops]
    return unary_union(parts)


# --------------------------------------------------------------- restroked
class _Flatten(BasePen):
    """CFF outline -> list of point rings (cubics flattened)."""

    def __init__(self, gs):
        super().__init__(gs)
        self.rings = []
        self.cur = []

    def _moveTo(self, p):
        self.cur = [p]

    def _lineTo(self, p):
        self.cur.append(p)

    def _curveToOne(self, a, b, c):
        p0 = self.cur[-1]
        for i in range(1, 13):
            s = i / 12
            u = 1 - s
            self.cur.append(
                (
                    u**3 * p0[0]
                    + 3 * u * u * s * a[0]
                    + 3 * u * s * s * b[0]
                    + s**3 * c[0],
                    u**3 * p0[1]
                    + 3 * u * u * s * a[1]
                    + 3 * u * s * s * b[1]
                    + s**3 * c[1],
                )
            )

    def _closePath(self):
        if len(self.cur) > 2:
            self.rings.append(self.cur)
        self.cur = []

    _endPath = _closePath


def outline(gs, name):
    """Nonzero winding, as the font is drawn: counter-clockwise contours are
    ink, clockwise ones are holes. Radon overlaps its contours (the bars of #
    and *, the stroke through !=), which even-odd would punch out."""
    f = _Flatten(gs)
    gs[name].draw(f)
    ink, holes = [], []
    for ring in f.rings:
        poly = Polygon(ring)
        if len(ring) < 3 or poly.area == 0:
            continue
        (ink if poly.exterior.is_ccw else holes).append(Polygon(ring).buffer(0))
    if not ink:
        return Polygon()
    if not holes:
        return unary_union(ink)
    cut = unary_union(holes)
    islands = [p for p in ink if cut.contains(p)]  # e.g. a bowl inside a counter
    return unary_union([unary_union(ink).difference(cut)] + islands)


def _polygons(geom):
    """Every polygon inside any shapely geometry (thinning can leave lines too)."""
    if geom.geom_type == "Polygon":
        return [] if geom.is_empty else [geom]
    return [p for g in getattr(geom, "geoms", []) for p in _polygons(g)]


def _is_dot(g):
    minx, miny, maxx, maxy = g.bounds
    w, h = maxx - minx, maxy - miny
    return (
        max(w, h) < 460
        and max(w, h) / max(min(w, h), 1) < 1.45
        and g.area > 0.6 * w * h
    )


def _inscribed(g):
    lo, hi = 0.0, 400.0
    for _ in range(14):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if not g.buffer(-mid).is_empty else (lo, mid)
    return lo


def stroke_width(gs, name="hyphen"):
    """Radon is monoline: its hyphen's thickness is the stroke of every symbol."""
    s = outline(gs, name)
    minx, miny, maxx, maxy = s.bounds
    from shapely.geometry import LineString

    return s.intersection(
        LineString([((minx + maxx) / 2, miny - 10), ((minx + maxx) / 2, maxy + 10)])
    ).length


def _voronoi_segments(poly: Polygon) -> np.ndarray:
    dense = shapely.segmentize(poly, 10)
    pts = [
        q for ring in [dense.exterior] + list(dense.interiors) for q in ring.coords[:-1]
    ]
    edges = voronoi_diagram(MultiPoint(pts), edges=True)
    # Every Voronoi edge as a two-point segment, built and tested as arrays
    # (Shapely 2): one call each instead of one Python object per edge.
    lines = shapely.get_parts(shapely.get_parts(edges))
    coords, idx = shapely.get_coordinates(lines, return_index=True)
    same = idx[1:] == idx[:-1]
    segs_xy = np.stack([coords[:-1][same], coords[1:][same]], axis=1)  # (m, 2, 2)
    return shapely.linestrings(segs_xy)


def _interior_lines(poly: Polygon, stroke: float) -> list[Stroke]:
    cand = _voronoi_segments(poly)
    shapely.prepare(poly)
    bnd = poly.boundary
    clear = 0.28 * stroke
    ok = shapely.contains(poly, cand) & (shapely.distance(cand, bnd) >= clear)
    keep = list(cand[ok])
    if not keep:
        return []
    merged = linemerge(MultiLineString(keep))
    return [list(line.coords) for line in getattr(merged, "geoms", [merged])]


def _endpoint_key(point: XY) -> XY:
    return round(point[0], 1), round(point[1], 1)


def _endpoint_degrees(lines: list[Stroke]) -> dict[XY, int]:
    degree = {}
    for line in lines:
        for point in (line[0], line[-1]):
            key = _endpoint_key(point)
            degree[key] = degree.get(key, 0) + 1
    return degree


def _extend_endpoint(poly: Polygon, a: XY, b: XY, stroke: float) -> XY:
    # Direction from the inside of the line out through this end.
    dx, dy = a[0] - b[0], a[1] - b[1]
    n = math.hypot(dx, dy) or 1.0
    dx, dy = dx / n, dy / n
    lo, hi = 0.0, 2.0 * stroke
    for _ in range(12):
        m = (lo + hi) / 2
        lo, hi = (
            (m, hi) if poly.contains(Point(a[0] + dx * m, a[1] + dy * m)) else (lo, m)
        )
    reach = max(0.0, lo - 0.30 * stroke)  # the nib adds its own half-width
    return a[0] + dx * reach, a[1] + dy * reach


def _extend_line(
    poly: Polygon, line: Stroke, degree: dict[XY, int], stroke: float
) -> Stroke:
    line = list(line)
    for end in (0, -1):
        if degree[_endpoint_key(line[end])] != 1 or len(line) < 2:
            continue
        line[end] = _extend_endpoint(
            poly, line[end], line[1 if end == 0 else -2], stroke
        )
    return line


def centreline(poly: Polygon, stroke: float) -> list[Stroke]:
    """Find medial-axis polylines, pruning the spurs running into corners.

    Loose ends reach back toward the outline so bars join their neighbours.
    Example: ``lines = centreline(Polygon([(0, 0), (800, 0), (800, 100), (0, 100)]), 100)``.
    """
    lines = _interior_lines(poly, stroke)
    if not lines:
        c = poly.representative_point()
        return [[(c.x, c.y), (c.x + 1, c.y + 1)]]
    degree = _endpoint_degrees(lines)
    return [_extend_line(poly, line, degree, stroke) for line in lines]


def _restroke_polygon(
    g: Polygon, w: float, t: float, shear_deg: float, radon_stroke: float
) -> list[BaseGeometry]:
    # Solid shapes (the filled triangle of |> and <|) aren't strokes: they
    # stay solid, only leaned to Jandí's angle. Where two strokes cross the
    # inscribed circle is at most ≈0.7 of a stroke, so 0.9 can't misfire.
    if _inscribed(g) > 0.9 * radon_stroke:
        return [affinity.skew(g, xs=shear_deg, origin=(0, AXIS))]
    out = []
    for line in centreline(g, radon_stroke):
        line = [
            (x + (y - AXIS) * math.tan(math.radians(shear_deg)), y) for x, y in line
        ]
        out.append(pen.sweep_broad(line, w, t))
    return out


def _restroke_dot(dot: Polygon, w: float, t: float, shear_deg: float) -> BaseGeometry:
    cx, cy = dot.centroid.x, dot.centroid.y
    cx += (cy - AXIS) * math.tan(math.radians(shear_deg))
    # The drop is drawn upright then slanted around y = 0; undo that shift.
    return affinity.translate(drop_shape(0, cy, w, t), cx - cy * math.tan(pen.SLANT), 0)


def restroke(
    shape: BaseGeometry, w: float, t: float, shear_deg: float, radon_stroke: float
) -> BaseGeometry:
    """Write Radon's centreline with Jandí's nib, preserving joins and solids.

    Weight comes from the nib alone, whatever Radon's stroke was.
    Example: ``ink = restroke(outline(gs, "hyphen"), 138, 106, 7, 178)``.
    """
    if shape.is_empty:
        return shape
    geoms = _polygons(shape)
    dots = [g for g in geoms if _is_dot(g)]
    out = []
    for g in geoms:
        if g not in dots:
            out.extend(_restroke_polygon(g, w, t, shear_deg, radon_stroke))
    out.extend(_restroke_dot(d, w, t, shear_deg) for d in dots)
    return unary_union(out)


# Code symbols restroked (plus their texture-healing and contextual variants).
RESTROKE_BASES = {
    "hyphen",
    "underscore",
    "slash",
    "backslash",
    "asterisk",
    "plus",
    "equal",
    "less",
    "greater",
    "bar",
    "at",
    "numbersign",
    "ampersand",
    "asciitilde",
    "asciicircum",
    "underscoredbl",
}
