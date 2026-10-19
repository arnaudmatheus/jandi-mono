"""The t/r decision of 1.0.0-beta.2: roman t crosses its stem, corsiva t doesn't."""

import caps
import corsiva
import letters


def bar_ends(strokes: list) -> tuple[float, float]:
    """x of the bar's two ends: the stroke that runs level."""
    for stroke in strokes:
        ys = {round(y) for _, y in stroke}
        if len(ys) == 1:
            xs = [x for x, _ in stroke]
            return min(xs), max(xs)
    raise AssertionError(f"no level stroke in {strokes!r}")


def stem_x(strokes: list) -> float:
    return strokes[0][0][0]


def test_roman_t_bar_crosses_the_stem() -> None:
    strokes = letters.strokes_t()
    left, right = bar_ends(strokes)
    assert (left, right) == (330, 800)
    assert stem_x(strokes) - left >= 200  # reaches well left of the stem at 560


def test_corsiva_keeps_the_t_pulled_right() -> None:
    strokes = corsiva.c_t_pulled_right()
    assert bar_ends(strokes) == (430, 880)
    assert corsiva.CORSIVA["t"] is corsiva.c_t_pulled_right
    # The same stem and exit as the roman t: only the bar differs.
    assert strokes[0] == letters.strokes_t()[0]


def test_one_keeps_its_foot_and_starts_its_flag_further_out() -> None:
    flag_and_stem, foot = caps.FIGURES["one"]()
    assert flag_and_stem[0] == (250, 1010)
    assert bar_ends([foot]) == (430, 850)
