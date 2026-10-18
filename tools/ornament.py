"""Ornament, all opt-in (roadmap 0.8.0): nothing here reaches default text.

- Florões (I1): the rocalha leaf, the vine leaf, the bud and the hedera, at
  Unicode's ornament code points (U+2619, U+2766-2767, U+1F650-1F667). The
  C- and S-scroll of Aleijadinho's carving is in every stem.
- Cartelas (I2): frame halves after the painted cartouches of Manuel da
  Costa Ataíde's nave ceiling (São Francisco de Assis, Ouro Preto,
  1801-1812), at the bracket ornaments U+2768-276B, U+2772-2775.
- Filactérios (I3): ribbon ends after the inscribed scrolls of Aleijadinho's
  Twelve Prophets at Congonhas. Unicode has no banner code points, so they
  live at the heavy angle bracket ornaments ❰ ❱ (U+2770-2771).
- Capitulares (I4): titl, carved inline capitals after lettering cut in
  stone; swsh, capitals with Figueiredo's pen flourish (rasgo). Both are
  OpenType features, off by default.

Every motif is one skeleton. Mirrored and turned forms are made on the
skeleton before the nib sweeps it, so the 35° contrast never flips. The
ornaments stay upright: they are drawn, not written."""

import math
from shapely.geometry import Polygon
from shapely.ops import unary_union
import pen
from letters import GOTA
from pen import path

CELL = 1160  # merge.py sets the real cell (1320 in Wide)
CY = 640  # bullets sit on the math axis


def CX():
    return CELL / 2


FLORAL_SCALE = 1.12  # motifs are drawn in ±430 and stay inside the cell


def _xf(pts, mx=1, my=1, swap=False, cx=None, cy=CY, k=FLORAL_SCALE):
    cx = CX() if cx is None else cx
    out = []
    for x, y in pts:
        if swap:
            x, y = y, x
        out.append((cx + k * mx * x, cy + k * my * y))
    return out


def spiral(cx, cy, r_out, r_in, a0, turns=1.15, cw=True, n=48):
    """An open scroll: an Archimedean spiral from r_out to r_in, starting at
    angle a0 (degrees). Every curl in the ornament is one of these, sized so
    the nib (≈140 units) never fills it in: a volute narrower than about 2.5
    nib widths turns into a blot."""
    pts = []
    for i in range(n + 1):
        u = i / n
        a = math.radians(a0) + (-1 if cw else 1) * u * turns * 2 * math.pi
        r = r_out + (r_in - r_out) * u
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


FINE = 0.55  # engraved line: curls, veins, tendrils


def volute(cx, cy, r_out, a0, cw=True, turns=1.15):
    """A scroll with the drop at its eye, drawn with the fine line."""
    pts = spiral(cx, cy, r_out, r_out * 0.5, a0, turns, cw)
    ex, ey = pts[-1]
    return [(pts, FINE), (GOTA(ex, ey, max(30, r_out * 0.2)), FINE)]


def fine(pts):
    return (pts, FINE)


def _map(s, fn):
    """Apply a point transform to a stroke, keeping its nib weight."""
    return (fn(s[0]), s[1]) if isinstance(s, tuple) else fn(s)


def render(strokes, fills, w, t):
    """strokes: point lists (the full nib) or (points, k) for a lighter nib."""
    parts = [
        (
            pen.sweep_broad(s[0], w * s[1], t * s[1])
            if isinstance(s, tuple)
            else pen.sweep_broad(s, w, t)
        )
        for s in strokes
    ]
    parts += [Polygon(f).buffer(0) for f in fills]
    return unary_union(parts)


# ---------------------------------------------------------------- florões
def leaf_ne(heavy=False):
    """Rocalha leaf pointing north-east: a pointed blade with its vein, and a
    C-scroll volute where the stem turns under."""
    upper = path(("M", (-250, -250)), ("C", (-300, 90), (-20, 360), (340, 340)))
    lower = path(("M", (-250, -250)), ("C", (90, -300), (360, -20), (340, 340)))
    vein = path(("M", (-250, -250)), ("C", (0, 20), (150, 160), (270, 270)))
    stem = path(("M", (-250, -250)), ("C", (-290, -290), (-330, -330), (-380, -330)))
    curl = volute(-380, -170, 160, -90, cw=False)
    strokes = (
        [(upper, 0.75), (lower, 0.75), fine(stem)]
        + curl
        + ([] if heavy else [fine(vein)])
    )
    fills = [upper + list(reversed(lower))] if heavy else []
    return strokes, fills


def vine_ne(heavy=False):
    """Vine leaf pointing north-east: three lobes and a coiled tendril."""
    edge = path(
        ("M", (-230, -230)),
        ("C", (-330, 0), (-260, 200), (-80, 170)),  # left lobe
        ("C", (-120, 330), (60, 420), (330, 340)),  # tip lobe
        ("C", (420, 60), (330, -120), (170, -80)),  # right lobe
        ("C", (200, -260), (0, -330), (-230, -230)),
    )
    vein = path(("M", (-230, -230)), ("L", (240, 240)))
    tendril = path(("M", (-230, -230)), ("C", (-270, -280), (-320, -330), (-380, -330)))
    curl = volute(-380, -150, 180, -90, cw=False, turns=1.5)
    strokes = [(edge, 0.75), fine(tendril)] + curl + ([] if heavy else [fine(vein)])
    return strokes, ([edge] if heavy else [])


def bud_ne(heavy=False):
    """A closed bud pointing north-east, held by two sepals, on a scrolled stem."""
    body = path(
        ("M", (330, 330)),
        ("C", (180, 330), (-60, 200), (-60, 20)),
        ("C", (-60, -60), (-10, -110), (60, -110)),
        ("C", (220, -110), (330, 160), (330, 330)),
    )
    sepal_a = path(("M", (-150, -150)), ("C", (-170, 0), (-120, 80), (-40, 90)))
    sepal_b = path(("M", (-150, -150)), ("C", (0, -170), (80, -120), (90, -40)))
    stem = path(("M", (-150, -150)), ("C", (-220, -220), (-300, -320), (-380, -320)))
    curl = volute(-380, -150, 170, -90, cw=False)
    strokes = [(body, 0.75), fine(sepal_a), fine(sepal_b), fine(stem)] + curl
    return strokes, ([body] if heavy else [])


def hedera_down():
    """The hedera (floral heart, ❦): a solid heart leaf, point down, its stem
    rising and curling over to the left."""
    heart = path(
        ("M", (0, -400)),
        ("C", (-180, -250), (-370, -70), (-350, 110)),
        ("C", (-330, 270), (-130, 300), (0, 180)),
        ("C", (130, 300), (330, 270), (350, 110)),
        ("C", (370, -70), (180, -250), (0, -400)),
    )
    stem = path(("M", (0, 180)), ("C", (10, 290), (40, 360), (120, 400)))
    curl = volute(-30, 420, 150, 0, cw=False, turns=1.1)
    return [(heart, 0.75), fine(stem)] + curl, [heart]


def _oriented(builder, direction, turned=False, heavy=False):
    """direction: NE, NW, SE, SW. turned: mirrored across the motif's own axis."""
    strokes, fills = builder(heavy)
    mx = -1 if direction in ("NW", "SW") else 1
    my = -1 if direction in ("SE", "SW") else 1
    f = lambda pts: _xf(pts, mx, my, swap=turned)
    return [_map(s, f) for s in strokes], [f(s) for s in fills]


def _hedera(rot):
    strokes, fills = hedera_down()

    def r(pts):
        if rot == "down":
            return _xf(pts)
        k = FLORAL_SCALE
        if rot == "right":  # ❧: rotated, pointing right
            return [(CX() - k * y, CY + k * x) for x, y in pts]
        # ☙: reversed, pointing left
        return [(CX() + k * y, CY - k * x) for x, y in pts]

    return [_map(s, r) for s in strokes], [r(s) for s in fills]


FLOROES = {
    0x2766: lambda: _hedera("down"),
    0x2767: lambda: _hedera("right"),
    0x2619: lambda: _hedera("left"),
}
_DIRS = {0: "NW", 1: "SW", 2: "NE", 3: "SE"}
for k in range(4):
    d = _DIRS[k]
    FLOROES[0x1F650 + k] = lambda d=d: _oriented(leaf_ne, d)
    FLOROES[0x1F654 + k] = lambda d=d: _oriented(leaf_ne, d, turned=True)
    FLOROES[0x1F658 + k] = lambda d=d: _oriented(vine_ne, d)
    FLOROES[0x1F65C + k] = lambda d=d: _oriented(vine_ne, d, heavy=True)
    FLOROES[0x1F660 + k] = lambda d=d: _oriented(bud_ne, d)
    FLOROES[0x1F664 + k] = lambda d=d: _oriented(bud_ne, d, heavy=True)

# ---------------------------------------------------------------- cartelas
TOP, BOT = 1520, -320  # a frame half spans the bracket height
MIDY = (TOP + BOT) / 2


def _volute(x, y, s=1, up=1, r=190):
    """The scrolled end of a cartouche frame at (x, y), curling in toward the
    text (s: +1 = to the right) and down from the top (up=-1) or up from the
    bottom (up=1)."""
    cx, cy = x, y + up * r
    a0 = 90 if up == -1 else -90
    cw = (s == 1) == (up == -1)
    return volute(cx, cy, r, a0, cw=cw)


def cartela_paren():
    # A C-scroll bow with scrolled ends and a drop at its outer middle.
    bow = path(("M", (640, TOP)), ("C", (180, TOP - 420), (180, BOT + 420), (640, BOT)))
    return [bow, GOTA(240, MIDY, 60)] + _volute(640, TOP, 1, -1) + _volute(
        640, BOT, 1, 1
    ), []


def cartela_flat():
    bow = path(("M", (660, TOP)), ("C", (420, TOP - 380), (420, BOT + 380), (660, BOT)))
    shell = [
        path(("M", (470, MIDY)), ("L", (330 + 40 * k, MIDY + 160 * (k - 1.5) / 1.5)))
        for k in range(4)
    ]
    rim = path(
        ("M", (330, MIDY - 160)),
        ("C", (260, MIDY - 60), (260, MIDY + 60), (330, MIDY + 160)),
    )
    return [bow, fine(rim)] + [fine(s) for s in shell] + _volute(
        660, TOP, 1, -1
    ) + _volute(660, BOT, 1, 1), []


def cartela_shell():
    frame = path(
        ("M", (760, TOP)),
        ("L", (480, TOP - 160)),
        ("L", (480, BOT + 160)),
        ("L", (760, BOT)),
    )
    return [frame, GOTA(790, TOP + 10, 34), GOTA(790, BOT - 10, 34)], []


def cartela_brace():
    top = path(
        ("M", (760, TOP)),
        ("C", (560, TOP), (520, TOP - 120), (520, TOP - 320)),
        ("L", (520, MIDY + 260)),
        ("C", (520, MIDY + 120), (460, MIDY + 30), (300, MIDY)),
    )
    bot = path(
        ("M", (300, MIDY)),
        ("C", (460, MIDY - 30), (520, MIDY - 120), (520, MIDY - 260)),
        ("L", (520, BOT + 320)),
        ("C", (520, BOT + 120), (560, BOT), (760, BOT)),
    )
    curl = volute(300, MIDY - 150, 150, 90, cw=False)
    return [top, bot] + curl + _volute(760, TOP, 1, -1) + _volute(760, BOT, 1, 1), []


def _mirror(builder):
    s, f = builder()
    m = lambda pts: [(CELL - x, y) for x, y in pts]
    return [_map(p, m) for p in s], [m(p) for p in f]


CARTELAS = {
    0x2768: cartela_paren,
    0x2769: lambda: _mirror(cartela_paren),
    0x276A: cartela_flat,
    0x276B: lambda: _mirror(cartela_flat),
    0x2772: cartela_shell,
    0x2773: lambda: _mirror(cartela_shell),
    0x2774: cartela_brace,
    0x2775: lambda: _mirror(cartela_brace),
}

# ---------------------------------------------------------------- filactérios
RT, RB = 1060, 260  # ribbon edges: from x-height down past the baseline


def ribbon_end_left():
    """The end of an inscribed ribbon: the band runs to the cell's right edge
    to meet the words, is creased once, and ends in a swallowtail."""
    mid = (RT + RB) / 2
    edge = CELL - 70  # the nib's half-width: the ink ends exactly at the cell edge
    band = path(
        ("M", (edge, RT)),
        ("L", (200, RT)),
        ("L", (370, mid)),
        ("L", (200, RB)),
        ("L", (edge, RB)),
    )
    return [(band, 0.8)], []


FILACTERIOS = {0x2770: ribbon_end_left, 0x2771: lambda: _mirror(ribbon_end_left)}

ORNAMENTS = {**FLOROES, **CARTELAS, **FILACTERIOS}
HEAVY = set(range(0x1F65C, 0x1F660)) | set(range(0x1F664, 0x1F668))


# ---------------------------------------------------------------- capitulares
def carved(strokes, w, t):
    """titl: the letter cut in stone. A heavier stroke with a fine groove down
    its centre, as in inscriptions carved with a V-cut: the light catches one
    wall and leaves the groove dark."""
    outer = unary_union([pen.sweep_broad(s, w * 1.25, t * 1.35) for s in strokes])
    groove = unary_union([pen.sweep_broad(s, 34, 34) for s in strokes])
    return outer.difference(groove)


def flourish(shape):
    """swsh: Figueiredo's rasgo grows out of the capital. A volute curls over
    its head on the left, and a long swash runs under the baseline from left
    to right, turning up at the end, as on his flourished capitals."""
    minx, miny, maxx, maxy = shape.bounds
    head = [
        fine(
            path(
                ("M", (minx + 160, maxy - 10)),
                (
                    "C",
                    (minx + 100, maxy + 60),
                    (minx, maxy + 80),
                    (minx - 90, maxy + 40),
                ),
            )
        )
    ] + volute(minx - 90, maxy - 140, 180, 90, cw=False)
    tail = path(
        ("M", (minx - 60, miny + 160)),
        (
            "C",
            (minx - 140, miny - 40),
            (minx + 60, miny - 190),
            (minx + 320, miny - 170),
        ),
        (
            "C",
            (maxx - 120, miny - 150),
            (maxx + 120, miny - 110),
            (maxx + 90, miny + 60),
        ),
    )
    return head + [fine(tail)]
