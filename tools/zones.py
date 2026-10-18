"""Step 5b: alignment zones and stems for hinting (roadmap F2).

Measured on this style's own ink. Radon's zones (x-height 1027, ascender
1530) no longer match the pen letters (x-height 1080, the nib's corner above
it), and wrong zones would snap the wrong heights. Each zone is 22 units: the
flat height plus the round letters' overshoot, under the BlueScale limit.
"""

import math
import statistics

import pen
from build_state import BuildState

BOTTOM, TOP = 1, 3  # indices into shapely bounds


def _median(state: BuildState, names: str, idx: int) -> float:
    ink = state.writer.ink
    return statistics.median(ink[g][idx] for g in names if g in ink)


def _zone(top: float) -> list[int]:
    return [round(top) - 4, round(top) + 18]


def set_zones(state: BuildState) -> None:
    """BlueValues, OtherBlues and stem widths in the CFF Private dict."""
    xh = _median(state, "xzvwuamnr", TOP)
    base = _median(state, "xzuamnrlhi", BOTTOM)
    cap = _median(state, "EFHIKLTXZ", TOP)
    asc = _median(state, "bdhkl", TOP)
    desc = _median(state, "gjpqy", BOTTOM)
    priv = state.font["CFF "].cff.topDictIndex[0].Private
    priv.BlueValues = (
        [round(base) - 18, round(base) + 4] + _zone(xh) + _zone(cap) + _zone(asc)
    )
    priv.OtherBlues = [round(desc) - 4, round(desc) + 18]
    priv.BlueScale, priv.BlueShift, priv.BlueFuzz = 0.037, 7, 0
    w, t = state.nib
    # The width of a vertical and of a horizontal stroke of the nib.
    nib_v = round(w * math.cos(pen.PEN) + t * math.sin(pen.PEN))
    nib_h = round(w * math.sin(pen.PEN) + t * math.cos(pen.PEN))
    priv.StdVW, priv.StdHW = nib_v, nib_h
    priv.StemSnapV, priv.StemSnapH = [nib_v], [nib_h]
