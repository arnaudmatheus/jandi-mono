"""Metadata every built font must get right (fontbakery's universal profile).

Called by merge.py on each style and again by nerd.py, whose icons extend
the glyph bounds."""
import math
from fontTools.pens.boundsPen import BoundsPen


def win_metrics(font):
    """usWinAscent/usWinDescent cover every glyph: Windows clips anything
    outside them (stacked Pinyin capitals, ornaments, icons). Linux line
    spacing comes from hhea and OS/2 typo metrics, which stay as they are."""
    gs = font.getGlyphSet()
    y_min, y_max = 0, 0
    for name in font.getGlyphOrder():
        bp = BoundsPen(gs)
        gs[name].draw(bp)
        if bp.bounds:
            y_min, y_max = min(y_min, bp.bounds[1]), max(y_max, bp.bounds[3])
    os2 = font['OS/2']
    os2.usWinAscent = max(os2.usWinAscent, math.ceil(y_max))
    os2.usWinDescent = max(os2.usWinDescent, math.ceil(-y_min))


def version(font, semver):
    """head.fontRevision and the name table's version string agree: 1.0.0
    is Version 1.000, 0.8.0 is Version 0.800."""
    major, minor, patch = (int(x) for x in semver.split('.'))
    rev = f"{major}.{minor * 100 + patch:03d}"
    font['head'].fontRevision = float(rev)
    return rev


def caret(font, slant_deg):
    """The text cursor leans with the letters (hhea caret slope)."""
    if slant_deg:
        font['hhea'].caretSlopeRise = 2000
        font['hhea'].caretSlopeRun = round(2000 * math.tan(math.radians(slant_deg)))


def stat(font, weight, italic, weight_name):
    """A STAT table: the weight and italic axes, so applications group the
    styles of a family correctly."""
    from fontTools.otlLib.builder import buildStatTable
    # A static font names only its own position on each axis.
    own = dict(value=weight, name=weight_name, **({"flags": 0x2, "linkedValue": 700} if weight == 400 else {}))
    axes = [
        dict(tag="wght", name="Weight", values=[own]),
        # Each static font names only its own italic value: Roman (elidable,
        # linked to Italic) or Italic.
        dict(tag="ital", name="Italic",
             values=[dict(value=1, name="Italic")] if italic
             else [dict(value=0, name="Roman", flags=0x2, linkedValue=1)]),
    ]
    buildStatTable(font, axes, elidedFallbackName=2)


def no_mac_names(font):
    """Only Windows-platform name records: the Mac Roman ones are legacy and
    modern systems never read them."""
    font['name'].names = [n for n in font['name'].names if n.platformID != 1]
