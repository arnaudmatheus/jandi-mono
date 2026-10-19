"""What one merge.py run builds: style, cell, family, and the nib for them."""

import math
from dataclasses import dataclass
from typing import NamedTuple

import pen


class Style(NamedTuple):
    nib: tuple[int, int]  # nib width and hairline (W, T)
    slant: int  # degrees


# One skeleton set, four styles. Subtle contrast (decision, proof 01) is kept in
# every style by scaling nib width and hairline together.
STYLES: dict[str, Style] = {
    "Regular": Style(nib=(138, 106), slant=7),
    "Bold": Style(nib=(196, 150), slant=7),  # Radon Bold stems ≈250 vs 172: ×1.42
    # The Italic is the corsiva after Figueiredo (tools/corsiva.py): his shapes
    # (loops, rasgos, entries) with the same broad nib as the Regular. His
    # pressure quill was tried and measured: even lightened to (165, 120) it
    # filled the counters, and eight pairs got worse than 0.3.0 (c/o +0.044,
    # n/u +0.036). Comments differ from code by shape; the stroke stays legible.
    "Italic": Style(nib=(138, 106), slant=13),
    "Bold Italic": Style(nib=(196, 150), slant=13),
}
RADON_CELL = 1240  # Radon upstream's advance
# Decision 2026-10-16: 1240 left too much air between chancery letters.
DEFAULT_CELL = 1160
# Talha Mono Wide (roadmap D3): the same letters in a 1320 cell, its own
# family so it installs beside the default. Extra-large letter spacing made
# dyslexic children read faster with fewer errors (Zorzi et al. 2012); the
# default stays 1160 because extra spacing slows typical readers
# (Slattery & Rayner 2013).
WIDE_CELL = 1320
# Talha Mono Text (roadmap G): the same letters with the nib 8% wider, for
# light backgrounds and low-density screens, where thin strokes fade (Commit
# Mono recommends 450 against 400 there). Its own family, weight class 450.
TEXT_NIB = 1.08
TEXT_WEIGHT = 450


@dataclass(frozen=True)
class BuildOptions:
    """One font to build.

    >>> parse_args(["in.otf", "out.otf", "--style", "Italic", "--wide"]).cell
    1320
    """

    src: str
    out: str
    style: str
    cell: int
    family: str
    ps_family: str
    text: bool

    @property
    def italic(self) -> bool:
        return "Italic" in self.style

    @property
    def bold(self) -> bool:
        return "Bold" in self.style

    @property
    def slant_deg(self) -> float:
        return STYLES[self.style].slant

    @property
    def nib(self) -> tuple[float, float]:
        """Nib width and thickness (W, T) for this style and family."""
        w, t = STYLES[self.style].nib
        return (w * TEXT_NIB, t * TEXT_NIB) if self.text else (w, t)


def _take_value(args: list[str], flag: str, default: str) -> str:
    """Removes `flag value` from args and returns value (or the default)."""
    if flag not in args:
        return default
    i = args.index(flag)
    value = args[i + 1]
    del args[i : i + 2]
    return value


def _take_switch(args: list[str], flag: str) -> bool:
    if flag not in args:
        return False
    args.remove(flag)
    return True


def parse_args(argv: list[str]) -> BuildOptions:
    """merge.py <upstream.otf> <out.otf> [--style S] [--cell N] [--wide] [--text]"""
    args = list(argv)
    style = _take_value(args, "--style", "Regular")
    if style not in STYLES:
        raise SystemExit(f"unknown --style {style!r} (expected one of {list(STYLES)})")
    cell = int(_take_value(args, "--cell", str(DEFAULT_CELL)))
    family, ps = "Talha Mono", "TalhaMono"
    if _take_switch(args, "--wide"):
        cell, family, ps = WIDE_CELL, "Talha Mono Wide", "TalhaMonoWide"
    text = _take_switch(args, "--text")
    if text:
        family, ps = family + " Text", ps + "Text"
    if len(args) != 2:
        raise SystemExit(f"expected <upstream.otf> <out.otf>, got {args}")
    return BuildOptions(args[0], args[1], style, cell, family, ps, text)


def configure_pen(opts: BuildOptions) -> None:
    """Sets the pen module's slant and nib angle for this style."""
    pen.SLANT = math.radians(opts.slant_deg)
    pen.PEN = math.radians(35)
