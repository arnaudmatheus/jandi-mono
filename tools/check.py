#!/usr/bin/env python3
"""Regression gate: the rule every release has followed, run by CI.

python check.py --base DIR --new DIR [--report PATH] [--tolerance 0.01]

Measures each family in --new against the font of the same name in --base
(tools/measure.py: Pango/FreeType, 12/15/20 px) and fails if any confusable
pair got more than --tolerance worse. Spacing evenness and sharpness are
reported, not gated: a design change may move them on purpose, and the
roadmap records why. A family with no baseline yet (a new family) is
reported and skipped.

The report is Markdown: written to --report, and to GitHub's job summary
when $GITHUB_STEP_SUMMARY is set."""

import argparse, json, os, subprocess, sys, tempfile
from pathlib import Path
from metric_types import FontMetrics
from typing import cast

HERE = Path(__file__).resolve().parent
# (label, roman file, italic file or None): the roman/italic pair is measured
# together so roman/italic similarity is checked too.
FAMILIES = [
    ("Jandi Mono", "JandiMono-Regular.otf", "JandiMono-Italic.otf"),
    ("Jandi Mono Italic", "JandiMono-Italic.otf", None),
    ("Jandi Mono Bold", "JandiMono-Bold.otf", "JandiMono-BoldItalic.otf"),
    ("Jandi Mono Wide", "JandiMonoWide-Regular.otf", "JandiMonoWide-Italic.otf"),
    ("Jandi Mono Text", "JandiMonoText-Regular.otf", "JandiMonoText-Italic.otf"),
]


FamilyPair = tuple[str, str | None, str | None]
Regression = tuple[int | str, str, float]


def mean(d: dict[str, float]) -> float:
    return sum(d.values()) / len(d)


def _check_args(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, type=Path)
    ap.add_argument("--new", required=True, type=Path)
    ap.add_argument("--report", type=Path, default=Path("check-report.md"))
    ap.add_argument("--tolerance", type=float, default=0.01)
    return ap.parse_args(argv)


def _font_spec(directory: Path, roman: str, italic: str | None) -> str:
    spec = str(directory / roman)
    if italic and (directory / italic).exists():
        spec += ":" + str(directory / italic)
    return spec


def _comparison_specs(base: Path, new: Path) -> tuple[list[str], list[FamilyPair]]:
    specs: list[str] = []
    pairs: list[FamilyPair] = []
    for label, roman, italic in FAMILIES:
        if not (new / roman).exists():
            continue
        if not (base / roman).exists():
            pairs.append((label, None, None))
            continue
        i = len(pairs)
        specs += [
            "--font",
            f"base{i}={_font_spec(base, roman, italic)}",
            "--font",
            f"new{i}={_font_spec(new, roman, italic)}",
        ]
        pairs.append((label, f"base{i}", f"new{i}"))
    return specs, pairs


def _run_measurements(specs: list[str]) -> dict[str, FontMetrics]:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "m"
        subprocess.run(
            [sys.executable, str(HERE / "measure.py"), *specs, "--out", str(out)],
            check=True,
            stdout=subprocess.DEVNULL,
        )
        return cast(
            dict[str, FontMetrics], json.loads(out.with_suffix(".json").read_text())
        )


def _worse_pairs(
    before: FontMetrics, after: FontMetrics, tolerance: float
) -> list[Regression]:
    return [
        (px, pair, after["confusability"][px][pair] - scores[pair])
        for px, scores in before["confusability"].items()
        for pair in scores
        if after["confusability"][px][pair] - scores[pair] > tolerance + 1e-9
    ]


def _regression_cell(worse: list[Regression]) -> str:
    top = sorted(worse, key=lambda w: -w[2])
    cell = ", ".join(f"`{p}` {px} px +{d:.3f}" for px, p, d in top[:8]) or "none"
    if len(top) > 8:
        cell += f", and {len(top) - 8} more"
    return cell


def _comparison_row(
    label: str, rb: FontMetrics, rn: FontMetrics, worse: list[Regression]
) -> str:
    conf = " / ".join(
        f"{mean(rb['confusability'][px]):.3f} → {mean(rn['confusability'][px]):.3f}"
        for px in ("12", "15", "20")
    )
    cv = f"{rb['spacing']['cv']} → {rn['spacing']['cv']}"
    sh = f"{rb['sharpness']['hintslight']} → {rn['sharpness']['hintslight']}"
    return f"| {label} | {conf} | {cv} | {sh} | {_regression_cell(worse)} |"


def _report_heading(tolerance: float) -> list[str]:
    return [
        "# Jandí Mono: regression check",
        "",
        f"Each family against its baseline. Fails if a confusable pair is more than "
        f"{tolerance} worse (similarity; lower is easier to tell apart).",
        "",
        "| Family | Confusability 12 / 15 / 20 px | Spacing CV | Sharpness 12 px | Pairs worse |",
        "|---|---|---|---|---|",
    ]


def regression_report(
    res: dict[str, FontMetrics], pairs: list[FamilyPair], tolerance: float
) -> tuple[str, bool]:
    """Summarize regressions; e.g. ``report, failed = regression_report(results, pairs, 0.01)``."""
    lines = _report_heading(tolerance)
    failed = []
    for label, b, n in pairs:
        if b is None or n is None:
            lines.append(f"| {label} | no baseline (new family) | | | skipped |")
            continue
        rb, rn = res[b], res[n]
        worse = _worse_pairs(rb, rn, tolerance)
        lines.append(_comparison_row(label, rb, rn, worse))
        failed += [(label, *w) for w in worse]
    lines += [
        "",
        "**Result: "
        + ("FAIL**, " + f"{len(failed)} pair(s) worse." if failed else "pass.**"),
    ]
    return "\n".join(lines) + "\n", bool(failed)


def _publish_report(report: str, path: Path) -> None:
    path.write_text(report)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as summary:
            summary.write(report)
    print(report)


def main(argv: list[str] | None = None) -> None:
    """Run the release gate; e.g. ``main(["--base", "fonts/otf", "--new", "build"])``."""
    args = _check_args(argv)
    specs, pairs = _comparison_specs(args.base, args.new)
    report, failed = regression_report(_run_measurements(specs), pairs, args.tolerance)
    _publish_report(report, args.report)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
