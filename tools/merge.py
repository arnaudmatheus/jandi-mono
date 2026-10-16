#!/usr/bin/env python3
"""Merge the pen-drawn lowercase into upstream Monaspace Radon and rename it.

python merge.py <upstream.otf> <out.otf> [--style Regular|Bold|Italic|"Bold Italic"]

Everything not redrawn here (symbols, box drawing, braille, punctuation,
figures, capitals, features) is Radon's, untouched. Replaced: a–z, dotless
i/j, the texture-healing variants, every precomposed accented lowercase, and
the combining marks, which also gain real mark positioning (GPOS) and the
GDEF "mark" class Radon lacks."""
import math, re, sys, unicodedata as ud
from fontTools.ttLib import TTFont
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from shapely.geometry import MultiPolygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from shapely import affinity
import pen
from marks import MARKS, CARON_APOSTROPHE

# One skeleton set, four styles. Subtle contrast (decision, proof 01) is kept in
# every style by scaling nib width and hairline together.
STYLES = {
    'Regular':     dict(nib=(138, 106), slant=7),
    'Bold':        dict(nib=(196, 150), slant=7),    # Radon Bold stems ≈250 vs 172: ×1.42
    'Italic':      dict(nib=(138, 106), slant=13),   # Regular already leans 7°: Italic must read apart
    'Bold Italic': dict(nib=(196, 150), slant=13),
}
FAMILY, PS = "Jandi Mono", "JandiMono"
VERSION = "0.2.0"

args = sys.argv[1:]
style = 'Regular'
if '--style' in args:
    i = args.index('--style'); style = args[i + 1]; del args[i:i + 2]
CELL = 1160                           # decision 2026-10-16: 1240 left too much air between chancery letters
if '--cell' in args:
    i = args.index('--cell'); CELL = int(args[i + 1]); del args[i:i + 2]
src, out = args[0], args[1]
W, T = STYLES[style]['nib']
pen.SLANT = math.radians(STYLES[style]['slant'])
TAN = math.tan(pen.SLANT)
font = TTFont(src)
cmap = font.getBestCmap()
cff = font['CFF '].cff
td = cff.topDictIndex[0]

# A célula. Radon tem 1240 (0,62 em), larga; com as letras chancelarescas mais
# estreitas o espaço entre elas sobrava. Encolher a célula na própria fonte
# aperta tudo de uma vez (terminal, barra, menus). O que continua sendo do
# Radon (símbolos, box drawing, braille) é escalado em x junto, então linhas
# de caixa seguem encostando de borda a borda.
if CELL != 1240:                      # Radon upstream is 1240
    from fontTools.pens.transformPen import TransformPen
    srcgs = TTFont(src).getGlyphSet()
    r = CELL / 1240
    cs = td.CharStrings
    for g in font.getGlyphOrder():
        w = font['hmtx'][g][0]
        nw = round(w * r)
        p = T2CharStringPen(None if nw == CELL else nw, None)
        srcgs[g].draw(TransformPen(p, (r, 0, 0, 1, 0, 0)))
        new = p.getCharString(private=td.Private, globalSubrs=cff.GlobalSubrs)
        cs.charStringsIndex[cs.charStrings[g]] = new
        font['hmtx'][g] = (nw, round(font['hmtx'][g][1] * r))
    td.Private.defaultWidthX = CELL
    td.Private.nominalWidthX = 0
pen.ADV = CELL
gs = font.getGlyphSet()

import caps

# Every redrawn glyph: Radon name -> (upright strokes, kind).
# kind decides the centring band and where the marks sit.
GLYPHS = {}
for c in 'abcdefghijklmnopqrstuvwxyz':
    GLYPHS[c] = (pen.LETTERS[c], 'lower')
GLYPHS['dotlessi'] = (pen.LETTERS['dotlessi'], 'lower')
GLYPHS['uni0237'] = (pen.LETTERS['dotlessj'], 'lower')
for c, fn in caps.CAPS.items():
    GLYPHS[c] = (fn, 'cap')
for n, fn in caps.FIGURES.items():
    GLYPHS[n] = (fn, 'cap')
for n, fn in caps.EXTRAS_LOWER.items():
    GLYPHS[n] = (fn, 'lower')
for n, fn in caps.EXTRAS_UPPER.items():
    GLYPHS[n] = (fn, 'cap')
GLYPHS = {g: v for g, v in GLYPHS.items() if g in td.CharStrings}
LETTER_OF = {**{c: c for c in 'abcdefghijklmnopqrstuvwxyz'}, **{c: c for c in caps.CAPS}}
ASCENDERS = set('bdfhkl')
CAP_TOP = 1460

def band_top(kind):
    return pen.XH if kind == 'lower' else CAP_TOP

def strokes_for(gname):
    return GLYPHS[gname][0]()

# ------------------------------------------------------------- write outlines
def to_charstring(shape):
    p = T2CharStringPen(None, None)            # width None == defaultWidthX (the cell)
    shape = shape.simplify(1.5)
    for g in (shape.geoms if isinstance(shape, MultiPolygon) else [shape]):
        g = orient(g, sign=1.0)                # CFF: outer contours counter-clockwise
        for ring in [g.exterior] + list(g.interiors):
            pts = [(round(x), round(y)) for x, y in ring.coords[:-1]]
            p.moveTo(pts[0]); [p.lineTo(q) for q in pts[1:]]; p.closePath()
    return p.getCharString(private=td.Private, globalSubrs=cff.GlobalSubrs)

def put(name, shape):
    cs = td.CharStrings
    new = to_charstring(shape)
    if cs.charStringsAreIndexed:
        cs.charStringsIndex[cs.charStrings[name]] = new
    else:
        cs.charStrings[name] = new
    font['hmtx'][name] = (pen.ADV, int(shape.bounds[0]))

def radon_bounds(name):
    bp = BoundsPen(gs); gs[name].draw(bp); return bp.bounds

# ------------------------------------------------------------- anchors
def anchors(gname):
    """Top / bottom / horn / ogonek anchors in upright space, before slant + dx."""
    s, kind = strokes_for(gname), GLYPHS[gname][1]
    if kind == 'lower':
        cx, right = pen.band_x(s)
        top_y = (pen.A + 170) if gname in ASCENDERS else (pen.T + 190)
        horn_y = pen.T - 40
    else:
        xs = [x for st in s for x, y in st if caps.FB - 20 <= y <= caps.CT + 20]
        cx, right = (min(xs) + max(xs)) / 2, max(xs)
        top_y, horn_y = caps.CT + 150, caps.CT - 40
    return {'above': (cx, top_y), 'below': (cx, 0), 'horn': (right - 40, horn_y),
            'ogonek': (right - 20, 0), 'caronapos': (max(x for st in s for x, y in st) + 70, pen.A - 60)}

def final(pt, dx):
    x, y = pt
    return (x + y * TAN + dx, y)

def shifted(strokes, ox, oy):
    return [[(x + ox, y + oy) for x, y in st] for st in strokes]

done = []
placed = {}
# 1. base glyphs
for gname, (fn, kind) in GLYPHS.items():
    shape, dx = pen.place(fn(), W, T, band_top=band_top(kind))
    put(gname, shape); placed[gname] = dx; done.append(gname)
    if gname == 'i' and 'i.loclTRK' in td.CharStrings:
        put('i.loclTRK', shape); done.append('i.loclTRK')

# 2. texture-healing variants: same skeleton, mapped to Radon's measured extents
for g in font.getGlyphOrder():
    m = re.match(r'^([A-Za-z]+)\.(left|right|both)$', g)
    if not m or m.group(1) not in GLYPHS:
        continue
    base = m.group(1)
    bx0, _, bx1, _ = radon_bounds(base)
    vx0, _, vx1, _ = radon_bounds(g)
    r = (vx1 - vx0) / (bx1 - bx0)
    shift = (vx0 + vx1) / 2 - (bx0 + bx1) / 2
    dx = placed[base]
    c = pen.ADV / 2
    # Skeleton slanted and centred; widen/shift it to Radon's variant, then
    # sweep. The nib angle stays 35° because only the path moves.
    strokes = [[(c + (x + dx - c) * r + shift, y) for x, y in pen.slant(st)] for st in strokes_for(base)]
    shape = unary_union([pen.sweep(st, W, T) for st in strokes])
    put(g, shape); done.append(g)

# 3. precomposed accented letters, lower and upper
def compose(gname, marks_cps):
    s, kind = strokes_for(gname), GLYPHS[gname][1]
    dx = placed[gname]
    a = anchors(gname)
    extra, stack = [], 0
    for cp in marks_cps:
        kind_m, strokes = MARKS[cp]
        if cp == 0x30C and gname in ('d', 'l', 't', 'L'):
            ax, ay = {'t': (a['caronapos'][0], 1200), 'L': (560, caps.CT - 40)}.get(gname, a['caronapos'])
            extra += shifted(CARON_APOSTROPHE, ax, ay); continue
        if kind_m == 'above':
            ax, ay = a['above']; extra += shifted(strokes, ax, ay + stack); stack += 230 if kind == 'lower' else 200
        elif kind_m == 'below':
            ax, ay = a['below']; extra += shifted(strokes, ax, ay)
        else:
            ax, ay = a[kind_m]; extra += shifted(strokes, ax, ay)
    shape, _ = pen.place(s + extra, W, T, dx=dx)
    return shape

for cp, gname in sorted(cmap.items()):
    d = ud.normalize('NFD', chr(cp))
    if len(d) < 2 or d[0] not in LETTER_OF or gname in GLYPHS:
        continue
    if not all(ord(m) in MARKS for m in d[1:]):
        continue
    base = d[0]
    if base in 'ij' and any(MARKS[ord(m)][0] == 'above' for m in d[1:]):
        base = 'dotlessi' if base == 'i' else 'uni0237'
    put(gname, compose(base, [ord(m) for m in d[1:]])); done.append(gname)

# 4. combining marks: drawn for an x-height letter at the cell centre
mark_anchor = {}
for cp, (kind, strokes) in MARKS.items():
    gname = cmap.get(cp)
    if not gname:
        continue
    a = anchors('n')
    ax, ay = a['above'] if kind == 'above' else (a['below'] if kind == 'below' else a[kind])
    dx = placed['n']
    shape = unary_union([pen.sweep(pen.slant(st), W, T) for st in shifted(strokes, ax, ay)])
    shape = affinity.translate(shape, dx, 0)
    put(gname, shape); done.append(gname)
    mark_anchor[gname] = (kind, final((ax, ay), dx))

# 4b. Radon's ccmp swaps marks after capitals for `.case` copies, and uses
# ready-made stacks for Vietnamese (uni03020301 = circumflex + acute). Without
# pen outlines and anchors those stayed Radon's and never attached (G̃ broke).
name_cp = {cmap[cp]: cp for cp in MARKS if cp in cmap}
for g in font.getGlyphOrder():
    stem_name = g.split('.')[0]
    combo = re.match(r'^uni(0302|0306)(030[0-9A-F])$', stem_name)
    if g.endswith('.case') and stem_name in name_cp:
        cps = [name_cp[stem_name]]
    elif combo and (g == stem_name or g.endswith('.case')):
        cps = [int(combo.group(1), 16), int(combo.group(2), 16)]
    else:
        continue
    if any(c not in MARKS or MARKS[c][0] != 'above' for c in cps):
        continue
    a = anchors('n'); ax, ay = a['above']; dx = placed['n']
    strokes = []
    for i, c in enumerate(cps):
        strokes += shifted(MARKS[c][1], ax + (70 if i else 0), ay + 220 * i)
    shape = affinity.translate(unary_union([pen.sweep(pen.slant(st), W, T) for st in strokes]), dx, 0)
    put(g, shape); done.append(g)
    mark_anchor[g] = ('above', final((ax, ay), dx))

# 5. GPOS mark attachment + GDEF classes
classes = {}
lines = []
for gname, (kind, (x, y)) in mark_anchor.items():
    cls = {'above': 'TOP', 'below': 'BOTTOM', 'horn': 'HORN', 'ogonek': 'OGONEK'}[kind]
    classes.setdefault(cls, []).append(gname)
    lines.append(f"markClass [{gname}] <anchor {round(x)} {round(y)}> @{cls};")
bases = []
for gname, dx in placed.items():
    if gname not in LETTER_OF and gname not in ('dotlessi', 'uni0237'):
        continue
    a = anchors(gname)
    parts = []
    for key, cls in (('above', 'TOP'), ('below', 'BOTTOM'), ('horn', 'HORN'), ('ogonek', 'OGONEK')):
        if cls in classes:
            x, y = final(a[key], dx)
            parts.append(f"<anchor {round(x)} {round(y)}> mark @{cls}")
    bases.append(f"  pos base {gname} {' '.join(parts)};")
fea = "\n".join(lines) + "\nfeature mark {\n" + "\n".join(bases) + "\n} mark;\n"
addOpenTypeFeaturesFromString(font, fea, tables=['GPOS'])

gdef = font['GDEF'].table.GlyphClassDef.classDefs
for gname in mark_anchor:
    gdef[gname] = 3                      # Radon had these as "component" (4)
for gname in placed:
    gdef.setdefault(gname, 1)

# 6. names: OFL Reserved Font Names may not survive in a derivative
name = font['name']
for rec in list(name.names):
    if rec.nameID in (1, 2, 3, 4, 5, 6, 16, 17, 18, 19, 21, 22, 25):
        name.removeNames(nameID=rec.nameID)
PSSTYLE = style.replace(' ', '')
for nid, val in {1: FAMILY, 2: style, 3: f"{VERSION};{PS}-{PSSTYLE}", 4: f"{FAMILY} {style}", 6: f"{PS}-{PSSTYLE}", 18: f"{FAMILY} {style}", 19: "fogão · ñe'ẽ · yandï'pawa"}.items():
    name.setName(val, nid, 3, 1, 0x409)
    if val.isascii():                     # Mac Roman can't hold ẽ / ï
        name.setName(val, nid, 1, 0, 0)
old = name.getDebugName(0) or ""
name.setName((old + " " if old else "") + "Jandí Mono lowercase and marks: Copyright (c) 2026 arnaudmatheus.", 0, 3, 1, 0x409)
name.setName(f"Version {VERSION}; derived from Monaspace Radon 1.400", 5, 3, 1, 0x409)
name.setName("Monaspace Radon's cursive rewritten with a fixed-angle Renaissance broad nib, for the Jandí theme.", 10, 3, 1, 0x409)
cff.fontNames = [f"{PS}-{PSSTYLE}"]
td.FullName = f"{FAMILY} {style}"; td.FamilyName = FAMILY
if 'Italic' in style:
    font['post'].italicAngle = -float(STYLES[style]['slant'])
font['OS/2'].fsType = 0
font['OS/2'].xAvgCharWidth = CELL
font.save(out)
print(f"{out}: replaced {len(done)} glyphs ({len(placed)} base, {len(mark_anchor)} marks)")
