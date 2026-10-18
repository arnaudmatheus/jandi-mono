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

def mean(d):
    return sum(d.values()) / len(d)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, type=Path)
    ap.add_argument("--new", required=True, type=Path)
    ap.add_argument("--report", type=Path, default=Path("check-report.md"))
    ap.add_argument("--tolerance", type=float, default=0.01)
    a = ap.parse_args()

    specs, pairs = [], []
    for label, roman, italic in FAMILIES:
        new_r, base_r = a.new / roman, a.base / roman
        if not new_r.exists():
            continue
        def spec(d):
            s = str(d / roman)
            if italic and (d / italic).exists():
                s += ":" + str(d / italic)
            return s
        if not base_r.exists():
            pairs.append((label, None, None)); continue
        i = len(pairs)
        specs += ["--font", f"base{i}={spec(a.base)}", "--font", f"new{i}={spec(a.new)}"]
        pairs.append((label, f"base{i}", f"new{i}"))

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "m"
        subprocess.run([sys.executable, str(HERE / "measure.py"), *specs, "--out", str(out)],
                       check=True, stdout=subprocess.DEVNULL)
        res = json.loads(out.with_suffix(".json").read_text())

    lines = ["# Jandí Mono: regression check", "",
             f"Each family against its baseline. Fails if a confusable pair is more than "
             f"{a.tolerance} worse (similarity; lower is easier to tell apart).", "",
             "| Family | Confusability 12 / 15 / 20 px | Spacing CV | Sharpness 12 px | Pairs worse |",
             "|---|---|---|---|---|"]
    failed = []
    for label, b, n in pairs:
        if b is None:
            lines.append(f"| {label} | no baseline (new family) | | | skipped |"); continue
        rb, rn = res[b], res[n]
        worse = [(px, p, rn["confusability"][px][p] - rb["confusability"][px][p])
                 for px in rb["confusability"] for p in rb["confusability"][px]
                 if rn["confusability"][px][p] - rb["confusability"][px][p] > a.tolerance + 1e-9]
        conf = " / ".join(f"{mean(rb['confusability'][px]):.3f} → {mean(rn['confusability'][px]):.3f}"
                          for px in ("12", "15", "20"))
        cv = f"{rb['spacing']['cv']} → {rn['spacing']['cv']}"
        sh = f"{rb['sharpness']['hintslight']} → {rn['sharpness']['hintslight']}"
        top = sorted(worse, key=lambda w: -w[2])
        cell = ", ".join(f"`{p}` {px} px +{d:.3f}" for px, p, d in top[:8]) or "none"
        if len(top) > 8:
            cell += f", and {len(top) - 8} more"
        lines.append(f"| {label} | {conf} | {cv} | {sh} | {cell} |")
        failed += [(label, *w) for w in worse]
    lines += ["", "**Result: " + ("FAIL**, " + f"{len(failed)} pair(s) worse." if failed else "pass.**")]
    report = "\n".join(lines) + "\n"
    a.report.write_text(report)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as f:
            f.write(report)
    print(report)
    sys.exit(1 if failed else 0)

if __name__ == "__main__":
    main()
