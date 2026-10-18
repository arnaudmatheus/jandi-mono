#!/usr/bin/env python3
"""Merge the pen-drawn lowercase into upstream Monaspace Radon and rename it.

python merge.py <upstream.otf> <out.otf> [--style Regular|Bold|Italic|"Bold Italic"]

Everything not redrawn here (symbols, box drawing, braille, punctuation,
figures, capitals, features) is Radon's, untouched. Replaced: a–z, dotless
i/j, the texture-healing variants, every precomposed accented lowercase, and
the combining marks, which also gain real mark positioning (GPOS) and the
GDEF "mark" class Radon lacks."""
import math, os, re, sys, unicodedata as ud
from fontTools.ttLib import TTFont
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from shapely.geometry import MultiPolygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from shapely import affinity
import pen
import fitcurves
from marks import MARKS, CARON_APOSTROPHE

# One skeleton set, four styles. Subtle contrast (decision, proof 01) is kept in
# every style by scaling nib width and hairline together.
STYLES = {
    'Regular':     dict(nib=(138, 106), slant=7),
    'Bold':        dict(nib=(196, 150), slant=7),    # Radon Bold stems ≈250 vs 172: ×1.42
    # The Italic is the corsiva after Figueiredo (tools/corsiva.py): his shapes
    # (loops, rasgos, entries) with the same broad nib as the Regular. His
    # pressure quill was tried and measured: even lightened to (165, 120) it
    # filled the counters, and eight pairs got worse than 0.3.0 (c/o +0.044,
    # n/u +0.036). Comments differ from code by shape; the stroke stays legible.
    'Italic':      dict(nib=(138, 106), slant=13),
    'Bold Italic': dict(nib=(196, 150), slant=13),
}
FAMILY, PS = "Jandi Mono", "JandiMono"
VERSION = "0.7.0"

args = sys.argv[1:]
style = 'Regular'
if '--style' in args:
    i = args.index('--style'); style = args[i + 1]; del args[i:i + 2]
CELL = 1160                           # decision 2026-10-16: 1240 left too much air between chancery letters
if '--cell' in args:
    i = args.index('--cell'); CELL = int(args[i + 1]); del args[i:i + 2]
# Jandi Mono Wide (roadmap D3): the same letters in a 1320 cell, its own
# family so it installs beside the default. Extra-large letter spacing made
# dyslexic children read faster with fewer errors (Zorzi et al. 2012); the
# default stays 1160 because extra spacing slows typical readers
# (Slattery & Rayner 2013).
if '--wide' in args:
    args.remove('--wide'); CELL = 1320; FAMILY, PS = "Jandi Mono Wide", "JandiMonoWide"
# Jandi Mono Text (roadmap G): the same letters with the nib 8% wider, for
# light backgrounds and low-density screens, where thin strokes fade (Commit
# Mono recommends 450 against 400 there). Its own family, weight class 450.
TEXT = '--text' in args
if TEXT:
    args.remove('--text'); FAMILY, PS = FAMILY + " Text", PS + "Text"
src, out = args[0], args[1]
W, T = STYLES[style]['nib']
if TEXT:
    W, T = W * 1.08, T * 1.08
pen.SLANT = math.radians(STYLES[style]['slant'])
pen.PEN = math.radians(STYLES[style].get('pen', 35))
pen.NIB = STYLES[style].get('model', 'broad')
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
    # Wide: o desenho é o mesmo, só a célula cresce. O que encosta nas duas
    # bordas (box drawing, blocos) estica para continuar emendando; o resto
    # (colchetes, chaves, pontuação) fica com a largura do Jandí Mono e só é
    # centrado. Esticados, [ e { ficavam mais parecidos ([/{ +0.018 a 12 px).
    r_sym = min(r, 1160 / 1240)
    cs = td.CharStrings
    for g in font.getGlyphOrder():
        w = font['hmtx'][g][0]
        nw = round(w * r)
        p = T2CharStringPen(None if nw == CELL else nw, None)
        bp = BoundsPen(srcgs); srcgs[g].draw(bp)
        joins = bp.bounds is not None and bp.bounds[0] <= 5 and bp.bounds[2] >= w - 5
        sx, ox = (r, 0) if (joins or r_sym == r) else (r_sym, (nw - w * r_sym) / 2)
        srcgs[g].draw(TransformPen(p, (sx, 0, 0, 1, ox, 0)))
        new = p.getCharString(private=td.Private, globalSubrs=cff.GlobalSubrs)
        cs.charStringsIndex[cs.charStrings[g]] = new
        lsb = round(bp.bounds[0] * sx + ox) if bp.bounds else 0
        font['hmtx'][g] = (nw, lsb)
    td.Private.defaultWidthX = CELL
    td.Private.nominalWidthX = 0
pen.ADV = CELL
gs = font.getGlyphSet()

import caps
import corsiva
if 'Italic' in style:
    pen.LETTERS.update(corsiva.CORSIVA)

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

# x-height +5% (roadmap B2: Legge & Bigelow's critical print size). Only the
# band from baseline to x-height stretches; ascenders keep their top, so the
# space above is compressed proportionally; descenders don't move.
XH_OLD, XH_NEW = 1027, 1080
K = XH_NEW / XH_OLD
T_NEW = pen.T * K
def vmap(y):
    if y <= 0:
        return y
    if y <= pen.T:
        return y * K
    return T_NEW + (y - pen.T) * (pen.A - T_NEW) / (pen.A - pen.T)
def taller(fn):
    return lambda: [[(x, vmap(y)) for x, y in st] for st in fn()]
GLYPHS = {g: ((taller(fn), kind) if kind == 'lower' else (fn, kind)) for g, (fn, kind) in GLYPHS.items()}
GLYPHS = {g: v for g, v in GLYPHS.items() if g in td.CharStrings}
LETTER_OF = {**{c: c for c in 'abcdefghijklmnopqrstuvwxyz'}, **{c: c for c in caps.CAPS}}
ASCENDERS = set('bdfhkl')
CAP_TOP = 1460

def band_top(kind):
    return XH_NEW if kind == 'lower' else CAP_TOP

def strokes_for(gname):
    return GLYPHS[gname][0]()

# ------------------------------------------------------------- write outlines
def to_charstring(shape, width=None):
    p = T2CharStringPen(width, None)           # width None == defaultWidthX (the cell)
    shape = shape.simplify(0.5)
    for g in (shape.geoms if hasattr(shape, 'geoms') else [shape]):
        if g.geom_type != 'Polygon' or g.is_empty:
            continue
        g = orient(g, sign=1.0)                # CFF: outer contours counter-clockwise
        for ring in [g.exterior] + list(g.interiors):
            # Curves, not polylines (roadmap F1): tools/fitcurves.py.
            start, segs = fitcurves.fit_ring(list(ring.coords[:-1]))
            r = lambda q: (round(q[0]), round(q[1]))
            p.moveTo(r(start))
            for s in segs:
                if s[0] == 'L':
                    p.lineTo(r(s[1]))
                else:
                    p.curveTo(r(s[1]), r(s[2]), r(s[3]))
            p.closePath()
    return p.getCharString(private=td.Private, globalSubrs=cff.GlobalSubrs)

INK = {}
def put(name, shape, advance=None):
    """advance None = the cell; ligatures and spacers keep Radon's own."""
    cs = td.CharStrings
    adv = pen.ADV if advance is None else advance
    new = to_charstring(shape, None if adv == CELL else adv)
    if cs.charStringsAreIndexed:
        cs.charStringsIndex[cs.charStrings[name]] = new
    else:
        cs.charStrings[name] = new
    font['hmtx'][name] = (adv, int(shape.bounds[0]))
    INK[name] = shape.bounds

def radon_bounds(name):
    bp = BoundsPen(gs); gs[name].draw(bp); return bp.bounds

# ------------------------------------------------------------- anchors
def anchors(gname):
    """Top / bottom / horn / ogonek anchors in upright space, before slant + dx."""
    s, kind = strokes_for(gname), GLYPHS[gname][1]
    if kind == 'lower':
        xs = [x for st in s for x, y in st if pen.B - 1 <= y <= T_NEW + 1]
        cx, right = (min(xs) + max(xs)) / 2, max(xs)
        top_y = (pen.A + 170) if gname in ASCENDERS else (T_NEW + 190)
        horn_y = T_NEW - 40
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
# Optical centring (roadmap D1): r and k sit on their ink's centre of mass,
# not on their bounding box (their arm and leg reach right, so the box put
# the stem too far left and left a hole before the next letter). Measured one
# letter at a time: r alone took spacing variation 0.283 -> 0.265; applied to
# every letter it made i/l, l/I, t/f worse (narrow letters lined up alike in
# the cell), and c e s b h each traded one pair for another.
OPTICAL = {'r': 1.0, 'k': 1.0}
for gname, (fn, kind) in GLYPHS.items():
    pen.OPTICAL = OPTICAL.get(gname, 0)
    shape, dx = pen.place(fn(), W, T, band_top=band_top(kind))
    put(gname, shape); placed[gname] = dx; done.append(gname)
    pen.OPTICAL = 0
    if gname == 'i' and 'i.loclTRK' in td.CharStrings:
        put('i.loclTRK', shape); done.append('i.loclTRK')

# 1b. Punctuation, symbols and ligatures with the pen (roadmap E1, E2; see
# tools/punct.py). Drawn glyphs sit on Radon's own centre, so code columns
# don't move; restroked ones keep Radon's geometry and advance exactly.
import punct
RADON_ANGLE = 11 if 'Italic' in style else 0
SHEAR = STYLES[style]['slant'] - RADON_ANGLE
GS = font['GSUB'].table
LIGA_IDX = [i for fr in GS.FeatureList.FeatureRecord if fr.FeatureTag == 'liga' for i in fr.Feature.LookupListIndex]
SS_IDX = [i for fr in GS.FeatureList.FeatureRecord if re.fullmatch(r'ss(0[1-9]|10)', fr.FeatureTag)
          for i in fr.Feature.LookupListIndex]
def lookup_outputs(indices):
    out, seen = set(), set()
    def walk(i):
        if i in seen: return
        seen.add(i); lk = GS.LookupList.Lookup[i]
        for st in lk.SubTable:
            if lk.LookupType == 7: st = st.ExtSubTable
            for v in (getattr(st, 'mapping', None) or {}).values():
                out.update(v if isinstance(v, (list, tuple)) else [v])
            for ls in (getattr(st, 'ligatures', None) or {}).values():
                out.update(l.LigGlyph for l in ls)
            for rec in (getattr(st, 'SubstLookupRecord', None) or []):
                walk(rec.LookupListIndex)
    for i in indices: walk(i)
    return out
LIGATURES = lookup_outputs(LIGA_IDX + SS_IDX) - {'emptyAdvanceWidth'} - set(GLYPHS) - set(punct.DRAWN)
srcgs = font.getGlyphSet()
RADON_STROKE = punct.stroke_width(srcgs)
pen_glyphs = []
for name in punct.DRAWN:
    if name not in td.CharStrings:
        continue
    rx0, _, rx1, _ = radon_bounds(name)
    shape = punct.drawn_shape(name, W, T)
    sx0, _, sx1, _ = shape.bounds
    put(name, affinity.translate(shape, (rx0 + rx1) / 2 - (sx0 + sx1) / 2, 0)); pen_glyphs.append(name)
for name in font.getGlyphOrder():
    if name in punct.DRAWN or name in GLYPHS:
        continue
    if not (name.split('.')[0] in punct.RESTROKE_BASES or name in LIGATURES):
        continue
    src = punct.outline(srcgs, name)
    if src.is_empty:
        continue
    put(name, punct.restroke(src, W, T, SHEAR, RADON_STROKE), font['hmtx'][name][0]); pen_glyphs.append(name)

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
    # Texture healing re-derived (roadmap D2): Radon's narrow letters step
    # aside and its wide ones grow into the room. Jandí's m and w already fill
    # the cell, so growing them made the healed pairs the tightest in the font
    # (mt, wt 7.5 px against a 13.8 mean at 40 px). Measured over a grid of
    # strengths, wide lowercase that doesn't grow is the most even (CV over
    # bigrams and three-letter contexts 0.266 -> 0.247 Regular, 0.290 ->
    # 0.264 Italic); narrow letters keep Radon's step.
    if r > 1 and base.islower():
        r, shift = 1.0, 0.0
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

composite_base = {}
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
    # O acento composto também é base: HarfBuzz recompõe u + ¨ em ü antes de
    # posicionar, e o agudo de ǘ precisa de uma âncora acima do trema.
    n_above = sum(MARKS[ord(m)][0] == 'above' for m in d[1:])
    if n_above:
        composite_base[gname] = base

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
gdef_bases = []
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
# Stacking (ǘ ǚ, and any second mark): the next mark's lowest ink sits STACK_GAP
# above the ink already there. Measured on the ink, because the marks hang
# differently from their anchors: the downward acute reaches 131 units below
# its own, the dieresis barely below. A fixed step left the acute on the dots.
STACK_GAP = 90
DEPTH = max(y - INK[g][1] for g, (kind, (x, y)) in mark_anchor.items() if kind == 'above')
def stack_y(ink_top):
    return ink_top + STACK_GAP + DEPTH
for gname, base in composite_base.items():
    a = anchors(base); a['above'] = (a['above'][0], stack_y(INK[gname][3]))
    parts = [f"<anchor {round(final(a[k], placed[base])[0])} {round(final(a[k], placed[base])[1])}> mark @{cls}"
             for k, cls in (('above', 'TOP'), ('below', 'BOTTOM'), ('horn', 'HORN'), ('ogonek', 'OGONEK')) if cls in classes]
    bases.append(f"  pos base {gname} {' '.join(parts)};")
    gdef_bases.append(gname)
# Mark on mark (roadmap D4): every mark above carries a second anchor over its
# own ink (stack_y), so a second mark sits on the first (ǘ ǚ, Pinyin;
# Vietnamese outside the precomposed stacks) instead of on top of it.
mk = [f"  pos mark {g} <anchor {round(x + (stack_y(INK[g][3]) - y) * TAN)} {round(stack_y(INK[g][3]))}> mark @TOP;"
      for g, (kind, (x, y)) in mark_anchor.items() if kind == 'above']
fea = ("\n".join(lines) + "\nfeature mark {\n" + "\n".join(bases) + "\n} mark;\n"
       + "feature mkmk {\n" + "\n".join(mk) + "\n} mkmk;\n")
addOpenTypeFeaturesFromString(font, fea, tables=['GPOS'])

# Ligatures on by default (roadmap E2, decision 2026-10-16): Radon keeps most
# of them behind ss01-ss10; they move into liga, so they need no feature flag
# and -liga still turns every one of them off. Texture healing stays in calt.
for fr in GS.FeatureList.FeatureRecord:
    if fr.FeatureTag == 'liga':
        fr.Feature.LookupListIndex = sorted(set(fr.Feature.LookupListIndex) | set(SS_IDX))
        fr.Feature.LookupCount = len(fr.Feature.LookupListIndex)

gdef = font['GDEF'].table.GlyphClassDef.classDefs
for gname in mark_anchor:
    gdef[gname] = 3                      # Radon had these as "component" (4)
for gname in list(placed) + gdef_bases:
    gdef.setdefault(gname, 1)

# 5b. Alignment zones and stems for hinting (roadmap F2), measured on this
# style's own ink. Radon's zones (x-height 1027, ascender 1530) no longer
# match the pen letters (x-height 1080, the nib's corner above it), and wrong
# zones would snap the wrong heights. Each zone is 22 units: the flat height
# plus the round letters' overshoot, under the BlueScale limit.
import statistics
def _median(names, idx):
    return statistics.median(INK[g][idx] for g in names if g in INK)
xh = _median('xzvwuamnr', 3); base = _median('xzuamnrlhi', 1)
cap = _median('EFHIKLTXZ', 3); asc = _median('bdhkl', 3); desc = _median('gjpqy', 1)
z = lambda top: [round(top) - 4, round(top) + 18]
priv = td.Private
priv.BlueValues = [round(base) - 18, round(base) + 4] + z(xh) + z(cap) + z(asc)
priv.OtherBlues = [round(desc) - 4, round(desc) + 18]
priv.BlueScale, priv.BlueShift, priv.BlueFuzz = 0.037, 7, 0
nib_v = round(W * math.cos(pen.PEN) + T * math.sin(pen.PEN))   # a vertical stroke's width
nib_h = round(W * math.sin(pen.PEN) + T * math.cos(pen.PEN))   # a horizontal stroke's width
priv.StdVW, priv.StdHW = nib_v, nib_h
priv.StemSnapV, priv.StemSnapH = [nib_v], [nib_h]

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
if TEXT:
    font['OS/2'].usWeightClass = 450
font['OS/2'].sxHeight = XH_NEW
font['OS/2'].xAvgCharWidth = CELL
font.save(out)
print(f"{out}: replaced {len(done)} glyphs ({len(placed)} base, {len(mark_anchor)} marks), {len(pen_glyphs)} punctuation/symbols/ligatures")
