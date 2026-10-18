"""Measurement orchestration, with named fakes for render and process I/O."""

import json
import subprocess
from pathlib import Path

import numpy as np
import pytest

import check
import measure
from test_reports import sample_metrics, serialized_metrics


class FakeBigramRenderer:
    def render(self, markup: str, px: int) -> np.ndarray:
        pixels = np.zeros((3, 10, 3))
        pixels[0, 1:3, 0] = 1
        pixels[0, 6:8, 1] = 1
        pixels[1, 2:4, 0] = 1
        pixels[1, 5:7, 1] = 1
        return pixels


def test_spacing_measures_ink_gaps_and_ignores_empty_rows(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(measure, "BIGRAMS", ["ab", "cd"])
    result = measure.spacing(FakeBigramRenderer())
    assert result["mean_gap_px@40"] == 3.0
    assert result["cv"] == 0
    assert result["n"] == 2


class FakeFontPaths:
    @staticmethod
    def exists(path: Path) -> bool:
        return str(path) in {
            "old/roman.otf",
            "new/roman.otf",
            "new/italic.otf",
            "new/fresh.otf",
        }


def test_comparison_specs_skip_absent_fonts_and_mark_new_families(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    files = FakeFontPaths()
    monkeypatch.setattr(Path, "exists", files.exists)
    monkeypatch.setattr(
        check,
        "FAMILIES",
        [
            ("Old", "roman.otf", "italic.otf"),
            ("New", "fresh.otf", None),
            ("Missing", "missing.otf", None),
        ],
    )
    specs, pairs = check._comparison_specs(Path("old"), Path("new"))
    assert specs == [
        "--font",
        "base0=old/roman.otf",
        "--font",
        "new0=new/roman.otf:new/italic.otf",
    ]
    assert pairs == [("Old", "base0", "new0"), ("New", None, None)]


class FakeMeasurementProcess:
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail
        self.calls = []

    def run(self, command: list[str], **kwargs: object) -> None:
        self.calls.append((command, kwargs))
        if self.fail:
            raise subprocess.CalledProcessError(7, command)

    @staticmethod
    def read(path: Path) -> str:
        return json.dumps({"base0": sample_metrics(), "new0": sample_metrics()})


def test_measurement_process_failure_propagates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    process = FakeMeasurementProcess(fail=True)
    monkeypatch.setattr(check.subprocess, "run", process.run)
    with pytest.raises(subprocess.CalledProcessError):
        check._run_measurements(["--font", "base0=font.otf"])


def test_measurement_process_reads_its_json_report(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    process = FakeMeasurementProcess()
    monkeypatch.setattr(check.subprocess, "run", process.run)
    monkeypatch.setattr(Path, "read_text", process.read)
    result = check._run_measurements(["--font", "base0=font.otf"])
    assert result["base0"] == serialized_metrics()
    assert process.calls[0][0][2:4] == ["--font", "base0=font.otf"]
    assert process.calls[0][1]["check"] is True


class FakeGateEnvironment:
    def __init__(self, delta: float) -> None:
        self.after = serialized_metrics()
        self.after["confusability"]["12"]["t/r"] += delta
        self.published = []

    def specs(self, base: Path, new: Path) -> tuple[list[str], list[check.FamilyPair]]:
        return [], [("Test", "base0", "new0")]

    def measurements(self, specs: list[str]) -> dict:
        return {"base0": serialized_metrics(), "new0": self.after}

    def publish(self, report: str, path: Path) -> None:
        self.published.append((report, path))


@pytest.mark.parametrize("delta, status", [(0, 0), (0.02, 1)])
def test_check_cli_exit_status_tracks_regressions(
    monkeypatch: pytest.MonkeyPatch, delta: float, status: int
) -> None:
    gate = FakeGateEnvironment(delta)
    monkeypatch.setattr(check, "_comparison_specs", gate.specs)
    monkeypatch.setattr(check, "_run_measurements", gate.measurements)
    monkeypatch.setattr(check, "_publish_report", gate.publish)
    with pytest.raises(SystemExit) as error:
        check.main(["--base", "old", "--new", "new", "--report", "gate.md"])
    assert error.value.code == status
    assert gate.published[0][1] == Path("gate.md")


def test_similarity_retains_shift_search_and_empty_image_sentinel() -> None:
    pixels = np.zeros((10, 10), dtype=np.float32)
    pixels[2:7, 3:5] = 1
    moved = np.roll(pixels, 1, axis=1)
    assert measure.similarity(pixels, moved, 1) == pytest.approx(1)
    assert measure.similarity(pixels, moved, 0) < 0.9
    assert measure.similarity(np.zeros_like(pixels), np.zeros_like(pixels), 1) == -1


class FakeCharacterRenderer:
    def char(self, character: str, px: int) -> np.ndarray:
        pixels = np.zeros((px, px), dtype=np.float32)
        pixels[2:8, 3:5] = 1
        return pixels


def test_confusability_keeps_size_and_pair_keys(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(measure, "CONFUSABLE", [("t", "r"), ("t", "1")])
    result = measure.confusability(FakeCharacterRenderer())
    assert result == {px: {"t/r": 1.0, "t/1": 1.0} for px in (12, 15, 20)}
