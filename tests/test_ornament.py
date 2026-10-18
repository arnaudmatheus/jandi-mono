"""A capital's rasgo stays anchored to its ink bounds."""

import pytest
from shapely import affinity
from shapely.geometry import box

import ornament


def test_flourish_follows_the_capital_translation() -> None:
    capital = box(100, -20, 900, 1460)
    original = ornament.flourish(capital)
    moved = ornament.flourish(affinity.translate(capital, 37, -51))
    assert len(original) == len(moved) == 4
    for (points, weight), (shifted, shifted_weight) in zip(original, moved):
        assert weight == shifted_weight == ornament.FINE
        for (x, y), (sx, sy) in zip(points, shifted):
            assert sx == pytest.approx(x + 37)
            assert sy == pytest.approx(y - 51)
