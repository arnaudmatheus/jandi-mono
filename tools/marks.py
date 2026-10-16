"""Pen-drawn diacritics. Each mark is upright strokes around its anchor at (0, 0):
above-marks sit on top of it, below-marks hang from it. They go through the
same slant and the same nib as the letters, so a tilde is a pen wave, not a
pasted shape."""
from pen import path

def _above(*strokes): return ('above', list(strokes))
def _below(*strokes): return ('below', list(strokes))

MARKS = {
    0x300: _above(path(('M', (70, 10)), ('L', (-120, 190)))),                                   # grave
    0x301: _above(path(('M', (-60, 10)), ('L', (130, 190)))),                                   # acute
    0x302: _above(path(('M', (-175, 10)), ('L', (0, 185)), ('L', (175, 10)))),                  # circumflex
    0x303: _above(path(('M', (-270, 0)), ('C', (-190, 115), (-100, 120), (0, 60)),              # tilde: pen wave
                       ('C', (100, 0), (190, 5), (270, 115)))),
    0x304: _above(path(('M', (-210, 80)), ('L', (210, 80)))),                                   # macron
    0x306: _above(path(('M', (-175, 180)), ('C', (-150, 10), (150, 10), (175, 180)))),          # breve
    0x307: _above(path(('M', (-18, 58)), ('L', (18, 94)))),                                    # dot above
    0x308: _above(path(('M', (-178, 58)), ('L', (-142, 94))), path(('M', (142, 58)), ('L', (178, 94)))),  # dieresis
    0x309: _above(path(('M', (-80, 160)), ('C', (-40, 230), (110, 220), (90, 130)),             # hook above
                       ('C', (80, 80), (20, 70), (10, 20)))),
    0x30A: _above(path(('M', (0, 30)), ('C', (90, 30), (110, 210), (0, 210)),                   # ring
                       ('C', (-110, 210), (-90, 30), (0, 30)))),
    0x30B: _above(path(('M', (-170, 10)), ('L', (-20, 190))), path(('M', (50, 10)), ('L', (200, 190)))),  # double acute
    0x30C: _above(path(('M', (-175, 185)), ('L', (0, 10)), ('L', (175, 185)))),                 # caron
    0x31B: ('horn', [path(('M', (0, 0)), ('C', (80, 40), (110, 120), (80, 200)))]),              # horn (ơ ư)
    0x323: _below(path(('M', (-18, -172)), ('L', (18, -136)))),                                 # dot below
    0x326: _below(path(('M', (30, -110)), ('C', (30, -190), (-20, -250), (-60, -275)))),        # comma below
    0x327: _below(path(('M', (0, 40)), ('L', (0, -60)), ('C', (110, -80), (110, -210), (-70, -235)))),  # cedilla
    0x328: ('ogonek', [path(('M', (0, 30)), ('C', (-100, -40), (-120, -210), (40, -235)))]),     # ogonek
}

# ď ľ ť: Czech/Slovak write the caron on a tall letter as an apostrophe beside it.
CARON_APOSTROPHE = [path(('M', (40, 120)), ('C', (40, 40), (10, -40), (-40, -90)))]
