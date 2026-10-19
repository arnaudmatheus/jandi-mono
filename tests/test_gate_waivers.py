"""Waivers let the gate accept a deliberate trade, and only for its version."""

import json
from pathlib import Path

import pytest

import check
import gate_waivers
from gate_waivers import Waiver, build_version, find_waiver, load_waivers

DECISIONS = [
    {
        "version": "1.0.0-beta.2",
        "decided": "2026-10-18",
        "reason": "t gets a crossing bar.",
        "allow": [
            {"family": "Test", "pair": "t/1", "px": "20", "max_delta": 0.11},
        ],
    },
    {
        "version": "1.0.0-beta.1",
        "decided": "2026-10-01",
        "reason": "an older decision.",
        "allow": [
            {"family": "Test", "pair": "t/r", "px": "12", "max_delta": 0.5},
        ],
    },
]


@pytest.fixture
def waivers_file(tmp_path: Path) -> Path:
    path = tmp_path / "gate_waivers.json"
    path.write_text(json.dumps(DECISIONS))
    return path


def test_build_version_reads_merge_py(tmp_path: Path) -> None:
    merge_py = tmp_path / "merge.py"
    merge_py.write_text('import sys\n\nVERSION = "2.0.0-beta.3"\n')
    assert build_version(merge_py) == "2.0.0-beta.3"


def test_build_version_names_the_file_when_missing(tmp_path: Path) -> None:
    merge_py = tmp_path / "merge.py"
    merge_py.write_text("VERSION = 2\n")
    with pytest.raises(ValueError, match="merge.py"):
        build_version(merge_py)


def test_only_this_versions_waivers_load(waivers_file: Path) -> None:
    loaded = load_waivers(waivers_file, "1.0.0-beta.2")
    assert loaded == [Waiver("Test", "t/1", "20", 0.11, "t gets a crossing bar.")]
    assert load_waivers(waivers_file, "1.0.0") == []


def test_missing_file_means_no_waivers(tmp_path: Path) -> None:
    assert load_waivers(tmp_path / "none.json", "1.0.0") == []


def test_unexpected_keys_are_rejected(tmp_path: Path) -> None:
    bad = [dict(DECISIONS[0], allow=[{"family": "Test", "pair": "t/1"}])]
    path = tmp_path / "gate_waivers.json"
    path.write_text(json.dumps(bad))
    with pytest.raises(ValueError, match="expected exactly the keys"):
        load_waivers(path, "1.0.0-beta.2")


@pytest.mark.parametrize("delta, covered", [(0.05, True), (0.11, True), (0.12, False)])
def test_waiver_covers_up_to_its_bound(delta: float, covered: bool) -> None:
    w = [Waiver("Test", "t/1", "20", 0.11, "why")]
    assert (find_waiver(w, "Test", 20, "t/1", delta) is not None) is covered
    assert find_waiver(w, "Other", 20, "t/1", delta) is None
    assert find_waiver(w, "Test", 15, "t/1", delta) is None


def metrics(t1_at_20: float) -> dict:
    conf = {px: {"t/r": 0.9, "t/1": 0.7} for px in ("12", "15", "20")}
    conf["20"]["t/1"] = t1_at_20
    return {
        "confusability": conf,
        "spacing": {"cv": 0.2},
        "sharpness": {"hintslight": 0.16},
    }


def test_gate_passes_a_waived_regression_and_reports_it() -> None:
    res = {"before": metrics(0.7), "after": metrics(0.8)}
    w = [Waiver("Test", "t/1", "20", 0.11, "t gets a crossing bar.")]
    report, failed = check.regression_report(
        res, [("Test", "before", "after")], 0.01, w
    )
    assert not failed
    assert "Accepted on purpose" in report and "Why: t gets a crossing bar." in report


def test_gate_still_fails_past_the_waivers_bound() -> None:
    res = {"before": metrics(0.7), "after": metrics(0.85)}
    w = [Waiver("Test", "t/1", "20", 0.11, "t gets a crossing bar.")]
    _, failed = check.regression_report(res, [("Test", "before", "after")], 0.01, w)
    assert failed


def test_repository_waivers_parse() -> None:
    decisions = json.loads(gate_waivers.WAIVERS_PATH.read_text())
    for decision in decisions:
        assert load_waivers(gate_waivers.WAIVERS_PATH, decision["version"])
