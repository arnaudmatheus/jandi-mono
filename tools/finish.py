"""Metadata every built font must get right (fontbakery's universal profile).

Called by merge.py on each style and again by nerd.py, whose icons extend
the glyph bounds."""

import math
from fontTools.pens.boundsPen import BoundsPen

# Windows clipping metrics, the same for every family and style:
# fontbakery wants them equal across a family and covering its tallest and
# deepest glyph, and each font is built on its own (in CI, on separate
# runners), so they are constants. The extremes today are Radon's Vietnamese
# Ể texture-healing variants (2251 in Bold) and an alternate ļ (-770 in
# Bold), the same in every family; the constants leave a small margin.
WIN_ASCENT, WIN_DESCENT = 2300, 800


def win_metrics(font):
    """usWinAscent/usWinDescent from the family constants. Windows clips
    anything outside them, so a glyph that reaches past them fails the
    build instead of clipping in silence (raise the constants then).
    Linux line spacing comes from hhea and OS/2 typo metrics, untouched."""
    gs = font.getGlyphSet()
    worst = []
    for name in font.getGlyphOrder():
        bp = BoundsPen(gs)
        gs[name].draw(bp)
        if bp.bounds and (bp.bounds[3] > WIN_ASCENT or bp.bounds[1] < -WIN_DESCENT):
            worst.append((name, round(bp.bounds[1]), round(bp.bounds[3])))
    if worst:
        raise SystemExit(
            f"glyphs past the win metrics ({WIN_ASCENT}/-{WIN_DESCENT}): {worst[:8]}"
        )
    font["OS/2"].usWinAscent, font["OS/2"].usWinDescent = WIN_ASCENT, WIN_DESCENT


def version(font, semver):
    """head.fontRevision and the name table's version string agree: 1.0.0
    is Version 1.000, 0.8.0 is Version 0.800. A pre-release sorts just
    below its release, so installers replace it with the final one:
    1.0.0-beta.1 is 0.991, beta.2 0.992, and 1.0.0 itself 1.000."""
    core, _, pre = semver.partition("-")
    major, minor, patch = (int(x) for x in core.split("."))
    if pre:
        n = int(pre.rsplit(".", 1)[-1]) if pre[-1].isdigit() else 1
        rev = (
            f"{major - 1}.{990 + n:03d}"
            if minor == 0 and patch == 0
            else f"{major}.{minor * 100 + patch - 1:03d}"
        )
    else:
        rev = f"{major}.{minor * 100 + patch:03d}"
    font["head"].fontRevision = float(rev)
    return rev


def caret(font, slant_deg):
    """The text cursor leans with the letters (hhea caret slope)."""
    if slant_deg:
        font["hhea"].caretSlopeRise = 2000
        font["hhea"].caretSlopeRun = round(2000 * math.tan(math.radians(slant_deg)))


def stat(font, weight, italic, weight_name):
    """A STAT table: the weight and italic axes, so applications group the
    styles of a family correctly."""
    from fontTools.otlLib.builder import buildStatTable

    # A static font names only its own position on each axis.
    own = dict(
        value=weight,
        name=weight_name,
        **({"flags": 0x2, "linkedValue": 700} if weight == 400 else {}),
    )
    axes = [
        dict(tag="wght", name="Weight", values=[own]),
        # Each static font names only its own italic value: Roman (elidable,
        # linked to Italic) or Italic.
        dict(
            tag="ital",
            name="Italic",
            values=(
                [dict(value=1, name="Italic")]
                if italic
                else [dict(value=0, name="Roman", flags=0x2, linkedValue=1)]
            ),
        ),
    ]
    buildStatTable(font, axes, elidedFallbackName=2)


def no_mac_names(font):
    """Only Windows-platform name records: the Mac Roman ones are legacy and
    modern systems never read them."""
    font["name"].names = [n for n in font["name"].names if n.platformID != 1]
