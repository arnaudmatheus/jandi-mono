"""Keep report contents and the CI regression boundary stable through refactors."""

import json
from pathlib import Path

import pytest

import check
import measure
from metrics_report import metrics_markdown

FIXTURES = Path(__file__).parent / "fixtures"


def sample_metrics() -> dict:
    return {
        "font": "Test Regular",
        "x_height_em": 0.54,
        "confusability": {px: {"t/r": 0.936, "t/1": 0.8} for px in (12, 15, 20)},
        "spacing": {
            "mean_gap_px@40": 12.5,
            "cv": 0.2,
            "tightest": ["mm"],
            "loosest": ["ti"],
            "n": 2,
        },
        "visual_angle": {"Screen": {"x_height_mm": 2.1, "degrees": 0.2}},
        "sharpness": {"hintslight": 0.16, "hintnone": 0.14},
    }


def test_metrics_markdown_matches_before_refactor() -> None:
    regular = sample_metrics()
    italic = dict(regular, roman_italic={"mean": 0.9, "per_letter": {"a": 0.9}})
    result = metrics_markdown(
        {"Regular": regular, "Italic": italic},
        [12, 15, 20],
        [("t", "r"), ("t", "1")],
        ["Screen"],
    )
    assert result == (FIXTURES / "metrics-report.md").read_text()


def serialized_metrics() -> dict:
    return json.loads(json.dumps(sample_metrics()))


@pytest.mark.parametrize(
    "delta, fails",
    [(0, False), (0.01, False), (0.0100000005, False), (0.01001, True), (-0.03, False)],
)
def test_gate_preserves_tolerance_boundary(delta: float, fails: bool) -> None:
    before, after = serialized_metrics(), serialized_metrics()
    after["confusability"]["12"]["t/r"] += delta
    report, failed = check.regression_report(
        {"before": before, "after": after}, [("Test", "before", "after")], 0.01
    )
    assert failed is fails
    assert ("**Result: FAIL**" in report) is fails


def test_regression_report_matches_before_refactor() -> None:
    before, after = serialized_metrics(), serialized_metrics()
    after["confusability"]["12"]["t/r"] += 0.025
    report, failed = check.regression_report(
        {"base0": before, "new0": after},
        [("Test", "base0", "new0"), ("New", None, None)],
        0.01,
    )
    assert failed
    assert report == (FIXTURES / "regression-report.md").read_text()


def test_regression_summary_sorts_and_limits_pairs() -> None:
    worse = [("12", f"p{i}", i / 100) for i in range(10)]
    cell = check._regression_cell(worse)
    assert cell.startswith("`p9` 12 px +0.090, `p8`")
    assert "`p1`" not in cell
    assert cell.endswith("and 2 more")


class FakeReportWriter:
    def __init__(self) -> None:
        self.written = {}

    def __call__(self, path: str) -> "FakeReportFile":
        return FakeReportFile(self.written, path)


class FakeReportFile:
    def __init__(self, written: dict[str, str], path: str) -> None:
        self.written, self.path = written, path

    def write_text(self, text: str) -> int:
        self.written[self.path] = text
        return len(text)


def test_write_md_uses_the_established_sizes_and_pairs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    writer = FakeReportWriter()
    monkeypatch.setattr(measure, "Path", writer)
    monkeypatch.setattr(measure, "SIZES", [12, 15, 20])
    monkeypatch.setattr(measure, "CONFUSABLE", [("t", "r"), ("t", "1")])
    monkeypatch.setattr(measure, "SETUPS", [("Screen", 97, 1, 600)])
    regular = sample_metrics()
    italic = dict(regular, roman_italic={"mean": 0.9, "per_letter": {"a": 0.9}})
    measure.write_md({"Regular": regular, "Italic": italic}, "metrics.md")
    assert writer.written["metrics.md"] == (FIXTURES / "metrics-report.md").read_text()
