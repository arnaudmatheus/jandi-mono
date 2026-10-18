"""Step 6: names and metadata.

OFL Reserved Font Names may not survive in a derivative, so every name
record that carries Radon's is rewritten.
"""

from fontTools.ttLib import TTFont

import finish
from build_options import TEXT_WEIGHT, BuildOptions
from glyph_table import XH_NEW

# Name IDs that carry the family's name (or Radon's).
RENAMED_IDS = (1, 2, 3, 4, 5, 6, 16, 17, 18, 19, 21, 22, 25)
WINDOWS_ENGLISH = (3, 1, 0x409)
SAMPLE_TEXT = "fogão · ñe'ẽ · yandï'pawa"
COPYRIGHT = "Jandí Mono lowercase and marks: Copyright (c) 2026 arnaudmatheus."
DESCRIPTION = (
    "Monaspace Radon's cursive rewritten with a fixed-angle Renaissance "
    "broad nib, for the Jandí theme."
)


def _ps_name(opts: BuildOptions) -> str:
    return f"{opts.ps_family}-{opts.style.replace(' ', '')}"


def _set_names(font: TTFont, opts: BuildOptions, version: str) -> None:
    name = font["name"]
    for rec in list(name.names):
        if rec.nameID in RENAMED_IDS:
            name.removeNames(nameID=rec.nameID)
    full = f"{opts.family} {opts.style}"
    records = {
        1: opts.family,
        2: opts.style,
        3: f"{version};{_ps_name(opts)}",
        4: full,
        6: _ps_name(opts),
        18: full,
        19: SAMPLE_TEXT,
    }
    for nid, val in records.items():
        name.setName(val, nid, *WINDOWS_ENGLISH)
    old = name.getDebugName(0) or ""
    name.setName((old + " " if old else "") + COPYRIGHT, 0, *WINDOWS_ENGLISH)


def _weight(opts: BuildOptions) -> tuple[int, str]:
    if opts.text:
        return TEXT_WEIGHT, "Text"
    return (700, "Bold") if opts.bold else (400, "Regular")


def _set_cff_names(font: TTFont, opts: BuildOptions) -> None:
    cff = font["CFF "].cff
    cff.fontNames = [_ps_name(opts)]
    top = cff.topDictIndex[0]
    top.FullName = f"{opts.family} {opts.style}"
    top.FamilyName = opts.family


def name_font(font: TTFont, opts: BuildOptions, version: str) -> None:
    """Names, version, style flags and Windows metrics for a finished font."""
    _set_names(font, opts, version)
    rev = finish.version(font, version)
    longer = f"Version {rev}; Jandi Mono {version}; derived from Monaspace Radon 1.400"
    font["name"].setName(longer, 5, *WINDOWS_ENGLISH)
    font["name"].setName(DESCRIPTION, 10, *WINDOWS_ENGLISH)
    _set_cff_names(font, opts)
    if opts.italic:
        font["post"].italicAngle = -float(opts.slant_deg)
    font["OS/2"].fsType = 0
    finish.caret(font, opts.slant_deg if opts.italic else 0)
    weight, weight_name = _weight(opts)
    finish.stat(font, weight, opts.italic, weight_name)
    if opts.text:
        font["OS/2"].usWeightClass = TEXT_WEIGHT
    font["OS/2"].sxHeight = XH_NEW
    font["OS/2"].xAvgCharWidth = opts.cell
    finish.win_metrics(font)
    finish.no_mac_names(font)
