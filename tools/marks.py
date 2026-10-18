"""Pen-drawn diacritics. Each mark is upright strokes around its anchor at (0, 0):
above-marks sit on top of it, below-marks hang from it. They go through the
same slant and the same nib as the letters, so a tilde is a pen wave, not a
pasted shape."""

from letters import DOT
from pen import path


def _above(*strokes):
    return ("above", list(strokes))


def _below(*strokes):
    return ("below", list(strokes))


MARKS = {
    # grave and acute: drawn downward
    0x300: _above(path(("M", (-120, 190)), ("L", (70, 10)))),
    0x301: _above(path(("M", (130, 190)), ("L", (-60, 10)))),
    # circumflex
    0x302: _above(path(("M", (-175, 10)), ("L", (0, 185)), ("L", (175, 10)))),
    # tilde: a pen wave
    0x303: _above(
        path(
            ("M", (-270, 0)),
            ("C", (-190, 115), (-100, 120), (0, 60)),
            ("C", (100, 0), (190, 5), (270, 115)),
        )
    ),
    # macron
    0x304: _above(path(("M", (-210, 80)), ("L", (210, 80)))),
    # breve
    0x306: _above(path(("M", (-175, 180)), ("C", (-150, 10), (150, 10), (175, 180)))),
    # dot above, dieresis
    0x307: _above(DOT(0, 76)),
    0x308: _above(DOT(-160, 76), DOT(160, 76)),
    # hook above
    0x309: _above(
        path(
            ("M", (-80, 160)),
            ("C", (-40, 230), (110, 220), (90, 130)),
            ("C", (80, 80), (20, 70), (10, 20)),
        )
    ),
    # ring
    0x30A: _above(
        path(
            ("M", (0, 30)),
            ("C", (90, 30), (110, 210), (0, 210)),
            ("C", (-110, 210), (-90, 30), (0, 30)),
        )
    ),
    # double acute
    0x30B: _above(
        path(("M", (-20, 190)), ("L", (-170, 10))),
        path(("M", (200, 190)), ("L", (50, 10))),
    ),
    # caron
    0x30C: _above(path(("M", (-175, 185)), ("L", (0, 10)), ("L", (175, 185)))),
    # horn (ơ ư)
    0x31B: ("horn", [path(("M", (0, 0)), ("C", (80, 40), (110, 120), (80, 200)))]),
    # dot below
    0x323: _below(path(("M", (-18, -172)), ("L", (18, -136)))),
    # comma below
    0x326: _below(path(("M", (30, -110)), ("C", (30, -190), (-20, -250), (-60, -275)))),
    # cedilla
    0x327: _below(
        path(
            ("M", (0, 40)), ("L", (0, -60)), ("C", (110, -80), (110, -210), (-70, -235))
        )
    ),
    # ogonek
    0x328: (
        "ogonek",
        [path(("M", (0, 30)), ("C", (-100, -40), (-120, -210), (40, -235)))],
    ),
}

# ď ľ ť: Czech/Slovak write the caron on a tall letter as an apostrophe beside it.
CARON_APOSTROPHE = [path(("M", (40, 120)), ("C", (40, 40), (10, -40), (-40, -90)))]
