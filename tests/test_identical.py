"""The refactor safety net (tools/identical.py)."""

from pathlib import Path

import pytest

import identical
from conftest import square, tiny_font

SQUARE = {"a": [square(0, 0, 500)]}


@pytest.fixture
def dirs(tmp_path: Path) -> tuple[Path, Path]:
    before, after = tmp_path / "before", tmp_path / "after"
    before.mkdir()
    after.mkdir()
    return before, after


def test_a_later_build_of_the_same_glyphs_is_identical(dirs):
    before, after = dirs
    tiny_font(SQUARE).save(before / "a.otf")
    later = tiny_font(SQUARE)
    later["head"].modified += 3600  # built an hour later: must not count
    later.recalcTimestamp = False
    later.save(after / "a.otf")
    assert identical.compare_dirs(before, after) == []


def test_a_moved_glyph_is_reported(dirs):
    before, after = dirs
    tiny_font(SQUARE).save(before / "a.otf")
    tiny_font({"a": [square(1, 0, 500)]}).save(after / "a.otf")
    # head too: it holds the font's bounding box, which moved with the glyph.
    assert identical.compare_dirs(before, after) == ["a.otf: head CFF "]


def test_a_missing_font_is_reported(dirs):
    before, after = dirs
    tiny_font(SQUARE).save(before / "a.otf")
    assert identical.compare_dirs(before, after) == [f"a.otf: missing from {after}"]


def test_an_empty_baseline_is_an_error(dirs):
    with pytest.raises(SystemExit, match="no .otf files"):
        identical.compare_dirs(*dirs)
