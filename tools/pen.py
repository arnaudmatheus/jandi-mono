#!/usr/bin/env python3
"""Jandí Mono proof: broad-nib pen engine.

Each letter is a centerline skeleton (cubic Béziers, drawn upright). The
skeleton is slanted, then a rectangular nib at ONE fixed angle is swept along
it. Thick and thin are never drawn by hand: they fall out of the pen angle,
the same for every letter. That constancy is the "Renaissance precision".
"""
import math, sys, json
from shapely.geometry import MultiPoint, Polygon, MultiPolygon
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from shapely import affinity

UPM, ADV, XH = 2000, 1240, 1027          # Radon's grid, measured
SLANT = math.radians(7)                  # one slant for the whole alphabet
PEN = math.radians(35)                   # chancery pen angle

# Skeleton vocabulary: stems at 330/905, x-height band 58..972
T, B = 972, 58

def cubic(p0, p1, p2, p3, n=48):
    out = []
    for i in range(1, n + 1):
        s = i / n
        a = (1 - s) ** 3; b = 3 * (1 - s) ** 2 * s; c = 3 * (1 - s) * s ** 2; d = s ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out

def line(p0, p1, step=24):
    n = max(1, int(math.dist(p0, p1) / step))
    return [(p0[0] + (p1[0] - p0[0]) * i / n, p0[1] + (p1[1] - p0[1]) * i / n) for i in range(1, n + 1)]

def path(*cmds):
    """cmds: ('M',p) ('L',p) ('C',c1,c2,p) -> list of points"""
    pts = []
    for c in cmds:
        if c[0] == 'M': pts = [c[1]]
        elif c[0] == 'L': pts += line(pts[-1], c[1])
        elif c[0] == 'C': pts += cubic(pts[-1], c[1], c[2], c[3])
    return pts

def ellipse(cx, cy, rx, ry, n=160, start=math.pi / 2):
    return [(cx + rx * math.cos(start + 2 * math.pi * i / n), cy + ry * math.sin(start + 2 * math.pi * i / n)) for i in range(n + 1)]

# ---------------------------------------------------------------- letters
def strokes_a():
    # B3: bojo mais estreito, entalhe onde encontra a haste e saída longa —
    # a 12 px o a da 0.2.0 era quase o (similaridade 0.979).
    bowl = path(('M', (880, 760)), ('C', (830, 920), (730, T), (640, T)), ('C', (470, T), (390, 760), (390, 520)),
                ('C', (390, 240), (470, B), (600, B)), ('C', (720, B), (840, 170), (905, 330)))
    stem = path(('M', (905, T)), ('L', (905, 170)), ('C', (905, 80), (960, 40), (1080, 100)))
    return [bowl, stem]

def strokes_e():
    return [path(('M', (330, 470)), ('C', (560, 480), (820, 560), (880, 680)), ('C', (940, 820), (820, T), (630, T)),
                 ('C', (430, T), (320, 760), (320, 520)), ('C', (320, 240), (440, B), (620, B)), ('C', (760, B), (860, 130), (925, 230)))]

def strokes_o():
    return [ellipse(615, 515, 325, 457)]

def strokes_n():
    entry = path(('M', (240, 885)), ('L', (330, T)), ('L', (330, 40)))
    arch = path(('M', (330, 760)), ('C', (390, 930), (520, T), (650, T)), ('C', (810, T), (905, 880), (905, 700)),
                ('L', (905, 170)), ('C', (905, 90), (950, 55), (1030, 95)))
    return [entry, arch]

def strokes_u():
    left = path(('M', (240, 885)), ('L', (330, T)), ('L', (330, 300)), ('C', (330, 140), (430, B), (560, B)),
                ('C', (700, B), (830, 150), (905, 320)))
    stem = path(('M', (905, T)), ('L', (905, 170)), ('C', (905, 90), (950, 55), (1030, 95)))
    return [left, stem]

def strokes_y():
    left = path(('M', (240, 885)), ('L', (330, T)), ('L', (330, 300)), ('C', (330, 140), (430, B), (560, B)),
                ('C', (700, B), (830, 150), (905, 320)))
    stem = path(('M', (905, T)), ('L', (905, -150)), ('C', (905, -290), (800, -368), (650, -368)),
                ('C', (520, -368), (420, -320), (360, -240)))
    return [left, stem]

def strokes_g():
    # Inspirado (não copiado) na assinatura de Michelangelo: o descendente faz
    # uma laçada e fecha num só gesto, cruzando de volta pela haste.
    bowl = path(('M', (905, 880)), ('C', (840, 955), (720, T), (620, T)), ('C', (420, T), (320, 760), (320, 560)),
                ('C', (320, 300), (430, 160), (590, 160)), ('C', (730, 160), (850, 260), (905, 400)))
    stem = path(('M', (905, T)), ('L', (905, -120)), ('C', (905, -300), (780, -368), (620, -368)),
                ('C', (430, -368), (300, -300), (300, -200)), ('C', (300, -110), (430, -62), (600, -62)),
                ('C', (780, -62), (900, -100), (1010, -170)))
    return [bowl, stem]

def strokes_f():
    # B3: barra larga, gancho de cima maior e gancho de baixo CURTO — o j
    # fica com o gancho grande; a 12 px os dois eram quase iguais (0.887).
    hook = path(('M', (1010, 1330)), ('C', (960, 1450), (850, 1482), (750, 1482)), ('C', (620, 1482), (560, 1400), (560, 1250)),
                ('L', (560, -170)), ('C', (560, -290), (510, -350), (430, -355)))
    bar = path(('M', (280, T - 10)), ('L', (900, T - 10)))
    return [hook, bar]

def strokes_dotlessi():
    return [path(('M', (400, 865)), ('L', (560, T)), ('L', (560, 170)), ('C', (560, 80), (630, 40), (760, 100)))]

def strokes_idot():
    return strokes_dotlessi() + [path(('M', (557, 1267)), ('L', (593, 1303)))]

def strokes_tilde(cx=620, y=1190):
    # Onda de pena: fina-grossa-fina sai do ângulo da pena, não de desenho.
    return [path(('M', (cx - 270, y)), ('C', (cx - 190, y + 115), (cx - 100, y + 120), (cx, y + 60)),
                 ('C', (cx + 100, y), (cx + 190, y + 5), (cx + 270, y + 115)))]

# Ascender/descender skeleton limits (outline lands ≈ at Radon's 1550 / −426).
A, D = 1482, -360
ENTRY = lambda x, top: [('M', (x - 90, top - 85)), ('L', (x, top))]      # the chancery lead-in
EXIT = lambda x: [('L', (x, 170)), ('C', (x, 90), (x + 45, 55), (x + 125, 95))]  # hairline exit flick
BOWL_R = [('C', (400, 880), (510, T), (640, T)), ('C', (820, T), (910, 800), (910, 520)),
          ('C', (910, 250), (780, B), (600, B)), ('C', (470, B), (380, 100), (330, 170))]
ARCH = [('C', (400, 900), (520, T), (640, T)), ('C', (800, T), (905, 880), (905, 700))]

def strokes_b():
    return [path(*ENTRY(330, A), ('L', (330, 70)), ('C', (330, 30), (290, 10), (230, 20))), path(('M', (330, 620)), *BOWL_R)]

def strokes_c():
    return [path(('M', (900, 830)), ('C', (840, 940), (740, T), (630, T)), ('C', (430, T), (320, 760), (320, 520)),
                 ('C', (320, 240), (440, B), (620, B)), ('C', (760, B), (860, 130), (925, 230)))]

def strokes_d():
    return [strokes_a()[0], path(*ENTRY(905, A), *EXIT(905))]

def strokes_h():
    return [path(*ENTRY(330, A), ('L', (330, 40))),
            path(('M', (330, 640)), *ARCH, ('L', (905, 170)), ('C', (905, 80), (960, 40), (1080, 100)))]

def strokes_dotlessj():
    return [path(('M', (430, 880)), ('L', (560, T)), ('L', (560, -150)), ('C', (560, -300), (440, D), (330, D)),
                 ('C', (240, D), (190, -310), (185, -250)))]

def strokes_j():
    return strokes_dotlessj() + [path(('M', (557, 1267)), ('L', (593, 1303)))]

def strokes_k():
    stem = path(*ENTRY(330, A), ('L', (330, 40)))
    loop = path(('M', (330, 430)), ('C', (480, 650), (760, 990), (870, 885)), ('C', (950, 805), (830, 600), (470, 520)))
    leg = path(('M', (600, 545)), ('C', (720, 420), (790, 130), (880, 75)), ('C', (930, 45), (980, 60), (1030, 100)))
    return [stem, loop, leg]

def strokes_l():
    # B3: cauda longa que sobe para a direita — nada mais na fonte tem esse
    # desenho, então l deixa de parecer I, 1 ou i a 12 px.
    return [path(*ENTRY(560, A), ('L', (560, 260)), ('C', (560, 110), (630, 45), (730, 55)),
                 ('C', (810, 65), (860, 120), (885, 190)))]

def strokes_m():
    # Três hastes na mesma célula: o m é a única letra que não pode estreitar.
    first = path(*ENTRY(250, T), ('L', (250, 40)))
    arch1 = path(('M', (250, 640)), ('C', (300, 890), (380, T), (450, T)), ('C', (560, T), (600, 880), (600, 700)), ('L', (600, 40)))
    arch2 = path(('M', (600, 640)), ('C', (650, 890), (730, T), (800, T)), ('C', (910, T), (950, 880), (950, 700)), *EXIT(950))
    return [first, arch1, arch2]

def strokes_p():
    return [path(*ENTRY(330, T), ('L', (330, D - 10))), path(('M', (330, 620)), *BOWL_R)]

def strokes_q():
    return [strokes_a()[0], path(('M', (905, T)), ('L', (905, D - 10)))]

def strokes_r():
    return [path(*ENTRY(330, T), ('L', (330, 40))),
            path(('M', (330, 640)), ('C', (400, 880), (520, T), (650, T)), ('C', (750, T), (830, 930), (880, 860)))]

def strokes_s():
    return [path(('M', (860, 880)), ('C', (800, 950), (700, T), (610, T)), ('C', (470, T), (380, 900), (380, 780)),
                 ('C', (380, 640), (520, 600), (620, 560)), ('C', (760, 505), (860, 430), (860, 280)),
                 ('C', (860, 130), (740, B), (590, B)), ('C', (470, B), (370, 100), (310, 190)))]

def strokes_t():
    # B3: haste curta, saída curta e barra puxada para a direita, como nas
    # chancelarescas — três silhuetas distintas: f (barra longa simétrica),
    # l (sem barra, cauda longa), t (barra à direita, cauda curta).
    return [path(('M', (560, 1180)), *EXIT(560)), path(('M', (430, T - 10)), ('L', (880, T - 10)))]

def strokes_v():
    # Vértice agudo na linha de base: com fundo redondo o v virava u a 12 px.
    return [path(*ENTRY(330, T), ('C', (360, 640), (470, 260), (600, 40)),
                 ('C', (700, 260), (860, 560), (900, 800)), ('C', (910, 880), (890, 940), (850, 975)))]

def strokes_w():
    left = path(*ENTRY(250, T), ('L', (250, 400)), ('C', (250, 190), (320, B), (410, B)),
                ('C', (520, B), (600, 180), (600, 420)), ('L', (600, 760)))
    right = path(('M', (600, 420)), ('C', (600, 190), (680, B), (780, B)), ('C', (900, B), (980, 280), (980, 650)),
                 ('C', (980, 820), (960, 900), (920, 960)))
    return [left, right]

def strokes_x():
    return [path(('M', (260, 880)), ('C', (330, 960), (430, T), (500, 860)), ('L', (760, 160)),
                 ('C', (820, 70), (900, 50), (1000, 110))),
            path(('M', (950, 920)), ('L', (280, 60)))]

def strokes_z():
    return [path(('M', (300, 940)), ('C', (400, T), (800, 960), (900, 960)), ('L', (320, 70)),
                 ('C', (500, 90), (800, 60), (930, 60)))]

LETTERS = {
    'a': strokes_a, 'b': strokes_b, 'c': strokes_c, 'd': strokes_d, 'e': strokes_e, 'f': strokes_f,
    'g': strokes_g, 'h': strokes_h, 'i': strokes_idot, 'j': strokes_j, 'k': strokes_k, 'l': strokes_l,
    'm': strokes_m, 'n': strokes_n, 'o': strokes_o, 'p': strokes_p, 'q': strokes_q, 'r': strokes_r,
    's': strokes_s, 't': strokes_t, 'u': strokes_u, 'v': strokes_v, 'w': strokes_w, 'x': strokes_x,
    'y': strokes_y, 'z': strokes_z, 'dotlessi': strokes_dotlessi, 'dotlessj': strokes_dotlessj,
}
# Composites: the tilde is anchored over each letter's own optical centre
# (the bowl for g, between the arms for y), not over the cell centre.
COMPOSITES = {
    'atilde': ('a', 615), 'etilde': ('e', 625), 'otilde': ('o', 615), 'ntilde': ('n', 618),
    'utilde': ('u', 618), 'ytilde': ('y', 618), 'itilde': ('dotlessi', 560), 'gtilde': ('g', 612),
}

# ---------------------------------------------------------------- the pen
def slant(pts):
    return [(x + y * math.tan(SLANT), y) for x, y in pts]

def sweep(pts, w, t):
    ux, uy = (w / 2) * math.cos(PEN), (w / 2) * math.sin(PEN)
    vx, vy = -(t / 2) * math.sin(PEN), (t / 2) * math.cos(PEN)
    def corners(p):
        x, y = p
        return [(x + ux + vx, y + uy + vy), (x + ux - vx, y + uy - vy), (x - ux + vx, y - uy + vy), (x - ux - vx, y - uy - vy)]
    hulls = [MultiPoint(corners(a) + corners(b)).convex_hull for a, b in zip(pts, pts[1:])]
    return unary_union(hulls)

def glyph_shape(name, w, t):
    if name in COMPOSITES:
        base, cx = COMPOSITES[name]
        strokes = LETTERS[base]() + strokes_tilde(cx)
    else:
        strokes = LETTERS[name]()
    shape = unary_union([sweep(slant(s), w, t) for s in strokes])
    # Centre on the x-height band, so f/g/y descenders don't drag the letter.
    band = shape.intersection(Polygon([(-2000, 0), (4000, 0), (4000, XH), (-2000, XH)]))
    minx, _, maxx, _ = band.bounds
    return affinity.translate(shape, ADV / 2 - (minx + maxx) / 2, 0)

def polygons(shape):
    shape = shape.simplify(1.5)
    geoms = shape.geoms if isinstance(shape, MultiPolygon) else [shape]
    return [orient(g, sign=-1.0) for g in geoms]   # TrueType: outer contours clockwise

def place(upright_strokes, w, t, dx=None, band_top=XH):
    """Slant, sweep and centre a set of upright strokes. Returns (shape, dx).
    Pass dx to reuse a base letter's centring for its accented forms.
    band_top: centre on 0..x-height for lowercase, 0..cap height for capitals
    and figures (otherwise an F or a P would centre on its lone stem)."""
    shape = unary_union([sweep(slant(s), w, t) for s in upright_strokes])
    if dx is None:
        band = shape.intersection(Polygon([(-2000, 0), (4000, 0), (4000, band_top), (-2000, band_top)]))
        minx, _, maxx, _ = band.bounds
        dx = ADV / 2 - (minx + maxx) / 2
    return affinity.translate(shape, dx, 0), dx

def band_x(upright_strokes):
    """Optical centre and right edge of the x-height band, in upright space."""
    xs = [x for s in upright_strokes for x, y in s if B - 1 <= y <= T + 1]
    return (min(xs) + max(xs)) / 2, max(xs)

def skeleton(name):
    if name in COMPOSITES:
        base, cx = COMPOSITES[name]; strokes = LETTERS[base]() + strokes_tilde(cx)
    else:
        strokes = LETTERS[name]()
    return [slant(s) for s in strokes]
