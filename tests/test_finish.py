"""Font metadata (tools/finish.py), the fields fontbakery checks."""

import pytest

import finish
from conftest import square, tiny_font


@pytest.mark.parametrize(
    "semver, revision",
    [
        ("1.0.0", "1.000"),
        ("0.8.0", "0.800"),
        ("1.0.0-beta.1", "0.991"),
        ("1.0.0-beta.2", "0.992"),
        ("1.2.0-rc.1", "1.199"),
    ],
)
def test_version_sorts_prereleases_below_the_release(semver, revision):
    font = tiny_font({})
    assert finish.version(font, semver) == revision
    assert font["head"].fontRevision == float(revision)


def test_win_metrics_are_family_constants():
    # Regression: computed per font, each style got its own values and
    # fontbakery failed the family (they must match across it).
    short, tall = tiny_font({"a": [square(0, 0, 500)]}), tiny_font(
        {"a": [square(0, -700, 2900)]}
    )
    for font in (short, tall):
        finish.win_metrics(font)
    assert {f["OS/2"].usWinAscent for f in (short, tall)} == {finish.WIN_ASCENT}
    assert {f["OS/2"].usWinDescent for f in (short, tall)} == {finish.WIN_DESCENT}


def test_glyph_past_the_win_metrics_fails_the_build():
    font = tiny_font({"a": [square(0, 0, finish.WIN_ASCENT + 50)]})
    with pytest.raises(SystemExit, match="past the win metrics"):
        finish.win_metrics(font)


def test_caret_leans_only_in_italics():
    upright, italic = tiny_font({}), tiny_font({})
    finish.caret(upright, 0)
    finish.caret(italic, 13)
    assert upright["hhea"].caretSlopeRun == 0
    assert italic["hhea"].caretSlopeRun == 462


def test_no_mac_names_keeps_windows_records():
    font = tiny_font({})
    font["name"].setName("Mac", 1, 1, 0, 0)
    finish.no_mac_names(font)
    assert {rec.platformID for rec in font["name"].names} == {3}
