#!/usr/bin/env python3
"""Add Nerd Font icons to a Jandí Mono build -> "Jandi Mono NF".

python nerd.py <jandi.otf> <monaspice-nerd.otf> <out.otf>

Without FontForge, the official Nerd Fonts patcher can't run here. MonaspiceRn
Nerd Font (Nerd Fonts' patch of the same Radon) already holds every icon
scaled for this exact cell (2000 UPM, 1240 advance), so the icons are copied
from it: every codepoint it has and Jandí Mono lacks. Each icon is redrawn
through a pen, so no CFF subroutine of the source font is carried over."""
import sys
from fontTools.ttLib import TTFont
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.ttLib.tables._c_m_a_p import cmap_format_12

src, icons_src, out = sys.argv[1:4]
font = TTFont(src)
icons = TTFont(icons_src)
cff = font['CFF '].cff; td = cff.topDictIndex[0]
cmap = font.getBestCmap(); icmap = icons.getBestCmap(); igs = icons.getGlyphSet()
order = font.getGlyphOrder()
have = set(order)

added = {}
for cp, gname in sorted(icmap.items()):
    if cp in cmap:
        continue
    name = gname if gname not in have else f"{gname}.nf"
    if name not in added and name not in have:
        width = icons['hmtx'][gname][0]
        p = T2CharStringPen(None if width == 1240 else width, igs)
        igs[gname].draw(p)
        cs = p.getCharString(private=td.Private, globalSubrs=cff.GlobalSubrs)
        idx = td.CharStrings
        idx.charStringsIndex.append(cs)
        idx.charStrings[name] = len(idx.charStringsIndex) - 1
        order.append(name); have.add(name)
        font['hmtx'][name] = (width, icons['hmtx'][gname][1])
        added[name] = []
    added[name].append(cp)

td.charset = order
font.setGlyphOrder(order)

# Plane-15 Material Design icons need a format 12 subtable.
full = dict(cmap)
for name, cps in added.items():
    for cp in cps:
        full[cp] = name
# Radon ships two of them, (0,4) and (3,10), and renderers prefer (3,10):
# every format 12 subtable must get the icons, not just the first one found.
if not any(t.format == 12 and (t.platformID, t.platEncID) == (3, 10) for t in font['cmap'].tables):
    c12 = cmap_format_12(12); c12.platformID, c12.platEncID, c12.language = 3, 10, 0
    font['cmap'].tables.append(c12)
for t in font['cmap'].tables:
    if t.format == 12:
        t.cmap = dict(full)
    elif t.format == 4:
        t.cmap = {cp: g for cp, g in full.items() if cp <= 0xFFFF}

name = font['name']
for rec in list(name.names):
    if rec.nameID in (1, 3, 4, 6, 18):
        s = str(rec)
        if rec.nameID == 6:
            name.setName(s.replace('JandiMono-', 'JandiMonoNF-'), 6, rec.platformID, rec.platEncID, rec.langID)
        elif rec.nameID == 3:
            name.setName(s.replace('JandiMono-', 'JandiMonoNF-'), 3, rec.platformID, rec.platEncID, rec.langID)
        else:
            name.setName(s.replace('Jandi Mono', 'Jandi Mono NF'), rec.nameID, rec.platformID, rec.platEncID, rec.langID)
cff.fontNames = [cff.fontNames[0].replace('JandiMono-', 'JandiMonoNF-')]
td.FullName = td.FullName.replace('Jandi Mono', 'Jandi Mono NF'); td.FamilyName = 'Jandi Mono NF'
font.save(out)
print(f"{out}: +{len(added)} icon glyphs, {sum(len(v) for v in added.values())} codepoints")
