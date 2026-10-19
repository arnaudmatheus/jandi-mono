"""A corsiva for Jandí Mono's Italic, after Manuel de Andrade de Figueiredo.

Model: plate nº 7 of *Nova Escola para aprender a ler, escrever e contar*
(Lisboa Occidental, 1722; Biblioteca Nacional de Portugal, purl.pt/107,
page 91 of the digitised copy). Figueiredo, born in the Captaincy of Espírito
Santo, Brazil, taught this Portuguese cursive at the Lisbon court; by 1725
his models ornamented the brotherhood statute books of Minas Gerais.

What the plate gives, adapted to a monospace cell:
- looped ascenders on h k (and on l, kept above the x-height): a hairline
  rising to the right, turning over the top and coming down as the stem;
- the bastarda d, whose ascender curls back to the left;
- a descender that ends in a sweeping leftward rasgo (p), kept inside the
  cell so neighbours never collide;
- long rising exits and lead-ins: the cursive rhythm, with the hand still
  lifting between letters (no joins — the grid needs that).

Same skeleton grid as tools/letters.py; letters not listed here keep the roman
skeletons and become cursive through the italic's slant and contrast."""

from letters import T, B, A, D, BOWL_R, ARCH
from pen import path
from pen_types import PathCmd, Stroke, StrokesFn
import letters


# Corsiva lead-in and exit: longer, rising hairlines.
def ENTRY_C(x: float, top: float) -> list[PathCmd]:
    return [
        ("M", (x - 170, top - 240)),
        ("C", (x - 110, top - 120), (x - 50, top - 30), (x, top)),
    ]


def EXIT_C(x: float) -> list[PathCmd]:
    return [
        ("L", (x, 190)),
        ("C", (x, 80), (x + 60, 40), (x + 130, 70)),
        ("C", (x + 170, 90), (x + 200, 130), (x + 220, 180)),
    ]


def LOOP_UP(x: float, base_y: float = 380) -> list[PathCmd]:
    """Looped ascender opening to the right of the stem at x (plate 7: h k).
    The hairline starts low, crosses the stem near the x-height and the loop
    takes the whole ascender, so its counter stays open at 12 px."""
    return [
        ("M", (x - 80, base_y)),
        ("C", (x + 80, 700), (x + 360, 1050), (x + 360, 1320)),
        ("C", (x + 360, 1440), (x + 270, A + 20), (x + 170, A + 20)),
        ("C", (x + 70, A + 20), (x, 1440), (x, 1300)),
    ]


def RASGO(x: float) -> list[PathCmd]:
    """Descender ending in a leftward sweep (plate 7: p q f), inside the cell."""
    return [
        ("L", (x, -190)),
        ("C", (x, -320), (x - 80, D), (x - 200, D)),
        ("C", (x - 290, D), (x - 340, -330), (x - 330, -280)),
    ]


def c_b() -> list[Stroke]:
    # b without a loop (as in the first line of plate nº 7): the loop is kept
    # for h k l, and it is exactly what tells h from b; with both looped,
    # h/b measured 0.97.
    return [
        path(*ENTRY_C(330, letters.A), ("L", (330, 110))),
        path(("M", (330, 620)), *BOWL_R),
    ]


def c_d() -> list[Stroke]:
    bowl = letters.strokes_a()[0]
    # The bastarda d: the stem rises and curls back to the left at the top.
    stem = path(
        ("M", (590, 1330)),
        ("C", (600, 1450), (700, A + 30), (800, A + 30)),
        ("C", (880, A + 30), (905, 1440), (905, 1340)),
        *EXIT_C(905)
    )
    return [bowl, stem]


def c_h() -> list[Stroke]:
    return [
        path(*LOOP_UP(330), ("L", (330, 40))),
        path(("M", (330, 640)), *ARCH, *EXIT_C(905)),
    ]


def c_k() -> list[Stroke]:
    stem = path(*LOOP_UP(330), ("L", (330, 40)))
    loop = path(
        ("M", (330, 430)),
        ("C", (480, 650), (760, 990), (870, 885)),
        ("C", (950, 805), (830, 600), (470, 520)),
    )
    leg = path(
        ("M", (600, 545)),
        ("C", (720, 420), (790, 130), (880, 75)),
        ("C", (930, 45), (990, 70), (1050, 140)),
    )
    return [stem, loop, leg]


def c_l() -> list[Stroke]:
    # The loop sits above the x-height only: crossing the stem at the
    # x-height, it put ink where the t has its bar (l/t 0.861 → 0.896).
    loop: list[PathCmd] = [
        ("M", (480, 1190)),
        ("C", (640, 1260), (940, 1280), (940, 1380)),
        ("C", (940, 1460), (830, A + 25), (720, A + 25)),
        ("C", (610, A + 25), (560, 1450), (560, 1340)),
    ]
    # The tail is the roman's (long, to 885): with the corsiva's short exit,
    # the foot of the l matched the t's.
    return [
        path(
            *loop,
            ("L", (560, 260)),
            ("C", (560, 110), (630, 45), (730, 55)),
            ("C", (810, 65), (860, 120), (885, 190))
        )
    ]


def c_f() -> list[Stroke]:
    # A straight descender with a cut to the right: with the rasgo sweeping
    # left, f read as j at 12 px (the j keeps the big hook).
    hook = path(
        ("M", (1000, 1330)),
        ("C", (950, 1450), (850, 1482), (750, 1482)),
        ("C", (620, 1482), (560, 1400), (560, 1250)),
        ("L", (560, -250)),
        ("C", (560, -320), (590, D), (660, -340)),
    )
    bar = path(("M", (300, T - 10)), ("L", (880, T - 10)))
    return [hook, bar]


def c_p() -> list[Stroke]:
    return [path(*ENTRY_C(330, T), *RASGO(330)), path(("M", (330, 620)), *BOWL_R)]


def c_n() -> list[Stroke]:
    entry = path(*ENTRY_C(330, T), ("L", (330, 40)))
    # The arch leaves the stem high, as in the roman. Leaving from the bottom
    # (the way the bastarda hand writes n in one gesture) closed the lower
    # left corner and n read as u: n/u 0.898 → 0.934.
    # The roman's short exit: with the corsiva's long exit, n mirrored the u,
    # which enters straight and leaves long.
    arch = path(
        ("M", (330, 760)),
        ("C", (390, 930), (520, T), (650, T)),
        ("C", (810, T), (905, 880), (905, 700)),
        ("L", (905, 170)),
        ("C", (905, 90), (950, 55), (1030, 95)),
    )
    return [entry, arch]


def c_m() -> list[Stroke]:
    # Stems at 300/600/900, as in the roman (wide-beside-wide pairs, roadmap F3).
    first = path(*ENTRY_C(300, T), ("L", (300, 40)))
    arch1 = path(
        ("M", (300, 640)),
        ("C", (345, 890), (405, T), (465, T)),
        ("C", (562, T), (600, 880), (600, 700)),
        ("L", (600, 40)),
    )
    arch2 = path(
        ("M", (600, 640)),
        ("C", (645, 890), (705, T), (765, T)),
        ("C", (862, T), (900, 880), (900, 700)),
        ("L", (900, 190)),
        ("C", (900, 80), (950, 40), (1010, 70)),
        ("C", (1040, 90), (1060, 130), (1070, 170)),
    )
    return [first, arch1, arch2]


def c_u() -> list[Stroke]:
    # No long lead-in: n and u with the same entry and the same exit become
    # mirrors (n/u 0.898 → 0.94). The u enters straight, as on plate nº 7.
    left = path(
        ("M", (330, T)),
        ("L", (330, 300)),
        ("C", (330, 140), (430, B), (560, B)),
        ("C", (700, B), (830, 150), (905, 320)),
    )
    stem = path(("M", (905, T)), *EXIT_C(905))
    return [left, stem]


def c_a() -> list[Stroke]:
    bowl, _ = letters.strokes_a()
    return [bowl, path(("M", (905, T)), *EXIT_C(905))]


def c_i_dotless() -> list[Stroke]:
    return [path(*ENTRY_C(560, T), *EXIT_C(560))]


def c_i() -> list[Stroke]:
    return c_i_dotless() + [letters.DOT()]


def c_t() -> list[Stroke]:
    return [
        path(("M", (560, 1180)), *EXIT_C(560)),
        path(("M", (430, T - 10)), ("L", (880, T - 10))),
    ]


def c_c() -> list[Stroke]:
    # No drop: with the pressure quill it nearly closed the c (c/o 0.900 → 0.944).
    return [
        path(
            ("M", (890, 870)),
            ("C", (830, 960), (740, T), (630, T)),
            ("C", (430, T), (320, 760), (320, 520)),
            ("C", (320, 240), (440, B), (620, B)),
            ("C", (760, B), (860, 130), (935, 240)),
        )
    ]


def c_r() -> list[Stroke]:
    # A short arm, no drop, leaving the top-right corner open: that is where
    # the n has its shoulder. With the long arm, r/n got worse.
    return [
        path(*ENTRY_C(330, T), ("L", (330, 40))),
        path(
            ("M", (330, 700)),
            ("C", (390, 900), (500, T), (620, T)),
            ("C", (720, T), (790, 950), (815, 905)),
        ),
    ]


def c_t_pulled_right() -> list[Stroke]:
    # The t the Italic has always used: the 0.8.0 roman t, bar pulled right
    # of the stem (c_t above, with the corsiva exit, was never registered).
    # The roman t's crossing bar (1.0.0-beta.2) made t/r worse against this
    # corsiva's short-armed r (+0.015 to +0.024 at 12-20 px), so the Italic
    # keeps this one.
    return [
        path(("M", (560, 1180)), *letters.EXIT(560)),
        path(("M", (430, T - 10)), ("L", (880, T - 10))),
    ]


CORSIVA: dict[str, StrokesFn] = {
    "a": c_a,
    "b": c_b,
    "c": c_c,
    "d": c_d,
    "f": c_f,
    "h": c_h,
    "i": c_i,
    "k": c_k,
    "l": c_l,
    "m": c_m,
    "n": c_n,
    "p": c_p,
    "r": c_r,
    "t": c_t_pulled_right,
    "u": c_u,
    "dotlessi": c_i_dotless,
}
