"""merge.py's command line (tools/build_options.py)."""

import pytest

from build_options import DEFAULT_CELL, TEXT_NIB, WIDE_CELL, parse_args


def test_defaults_are_the_regular_in_the_default_cell():
    opts = parse_args(["in.otf", "out.otf"])
    assert (opts.style, opts.cell, opts.family, opts.ps_family) == (
        "Regular",
        DEFAULT_CELL,
        "Jandi Mono",
        "JandiMono",
    )
    assert opts.nib == (138, 106)


def test_wide_is_its_own_family_in_a_wider_cell():
    opts = parse_args(["in.otf", "out.otf", "--wide", "--style", "Bold Italic"])
    assert (opts.cell, opts.family, opts.ps_family) == (
        WIDE_CELL,
        "Jandi Mono Wide",
        "JandiMonoWide",
    )
    assert opts.bold and opts.italic and opts.slant_deg == 13


def test_text_widens_the_nib_and_names_the_family():
    opts = parse_args(["in.otf", "out.otf", "--text"])
    assert opts.family == "Jandi Mono Text"
    assert opts.nib == (138 * TEXT_NIB, 106 * TEXT_NIB)


def test_wide_wins_over_an_explicit_cell():
    assert parse_args(["a", "b", "--cell", "1200", "--wide"]).cell == WIDE_CELL


def test_unknown_style_names_the_valid_ones():
    with pytest.raises(SystemExit, match="unknown --style 'Light'.*Regular"):
        parse_args(["a", "b", "--style", "Light"])


def test_missing_output_path_is_an_error():
    with pytest.raises(SystemExit, match="expected <upstream.otf> <out.otf>"):
        parse_args(["only-one.otf"])
