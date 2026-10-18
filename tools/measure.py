#!/usr/bin/env python3
"""Jandí Mono measurement harness (roadmap phase A).

python measure.py --font LABEL=PATH[:ITALIC_PATH] ... [--out docs/metrics]

Renders through Pango/FreeType with fixed, explicit settings — each font in an
isolated fontconfig (so the desktop's own font rules can't substitute it),
hintslight, grayscale antialiasing — and reports:

  confusability   similarity of easily confused characters (Beier & Larson 2010)
  spacing         evenness of the gaps between neighbouring letters (texture healing,
                  Commit Mono smart kerning); lower variation = more even
  roman/italic    how alike each letter is in Regular and Italic (lower = comments
                  read apart from code)
  visual angle    x-height in degrees at the user's real screens (Legge & Bigelow 2011)
  sharpness       share of fully dark ink pixels at 12 px, hinted vs unhinted

Similarity = best normalised correlation over ±1–2 px shifts, after a slight
blur (the eye never sees a single pixel); 1.0 means identical images.
"""

import argparse
import html
import json
import math
import os
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pathlib import Path

import numpy as np
from fontTools.ttLib import TTFont
from PIL import Image

from metric_types import FontMetrics, RomanItalic, Spacing, VisualAngle
from metrics_report import metrics_markdown

CONFUSABLE = [
    ("e", "c"),
    ("a", "o"),
    ("n", "u"),
    ("s", "e"),
    ("c", "o"),
    ("i", "j"),
    ("i", "l"),
    ("l", "t"),
    ("t", "f"),
    ("f", "j"),
    ("1", "l"),
    ("l", "I"),
    ("1", "I"),
    ("0", "O"),
    (",", "."),
    (":", ";"),
    ("(", "["),
    ("[", "{"),
    ("r", "n"),
    ("h", "b"),
    ("g", "q"),
    ("v", "y"),
    # Added 2026-10-18 from the reading test: the reader found t and r
    # hard to tell apart in Jandi Mono (0.936 at 12 px, Radon 0.790).
    ("t", "r"),
    # Added the same day: the first redrawn t (crossbar reaching left)
    # read like the 1's flag in the README image (t/1 +0.10 at 20 px).
    ("t", "1"),
]
SIZES = [12, 15, 20]
BIGRAMS = sorted(set("""
de os es ra ar en nt do te co er re as ad ta da or ca ri ma em se an ue qu st to on ia io ac ec al ic in ne no ve el pa ro um
th he in er an re on at en nd ti es or te of ed is it al ar st to nt ng se ha as ou io le ve co me de hi ri ro ic ne ea ra ce li ch
ll be ma si om ur fn rs py js go if lf ok tx id
il li mi im wi iw lm ml ll mm ww fi ft tl lt ij ji mw wm rn nr
""".split()))
SETUPS = [
    ("LG 25UM58G, 97 PPI, 60 cm", 97, 1.0, 600),
    ("Laptop BOE, 197 PPI, ×1.25, 50 cm", 197, 1.25, 500),
]


class Renderer:
    """One isolated fontconfig per font file."""

    def __init__(self, path: str) -> None:
        self.path = os.path.abspath(path)
        self.dir = tempfile.mkdtemp(prefix="jm-measure-")
        os.symlink(self.path, os.path.join(self.dir, os.path.basename(self.path)))
        t = TTFont(self.path)
        self.family = t["name"].getDebugName(16) or t["name"].getDebugName(1)
        self.style = t["name"].getDebugName(17) or t["name"].getDebugName(2)
        self.xh = t["OS/2"].sxHeight / t["head"].unitsPerEm
        self.conf: dict[str, str] = {}

    def _conf(self, hint: str) -> str:
        if hint not in self.conf:
            p = os.path.join(self.dir, f"fc-{hint}.conf")
            open(p, "w").write(
                f"""<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig><dir>{self.dir}</dir><cachedir>{self.dir}/cache</cachedir>
<match target="font"><edit name="antialias" mode="assign"><bool>true</bool></edit>
<edit name="hinting" mode="assign"><bool>{'true' if hint != 'hintnone' else 'false'}</bool></edit>
<edit name="hintstyle" mode="assign"><const>{hint}</const></edit>
<edit name="rgba" mode="assign"><const>none</const></edit>
<edit name="autohint" mode="assign"><bool>false</bool></edit></match></fontconfig>"""
            )
            self.conf[hint] = p
        return self.conf[hint]

    def _render_command(self, markup_path: str, output: str, px: int) -> list[str]:
        return [
            "pango-view",
            "-q",
            "--markup",
            f"--font={self.family}, {self.style} {px}px",
            "--background=black",
            "--margin=6",
            "--dpi=96",
            f"--output={output}",
            markup_path,
        ]

    def render(self, markup: str, px: int, hint: str = "hintslight") -> np.ndarray:
        """Render markup with this font only; e.g. ``renderer.render("abc", 12)``."""
        with tempfile.TemporaryDirectory() as tmp:
            mk, out = os.path.join(tmp, "t.txt"), os.path.join(tmp, "o.png")
            Path(mk).write_text(markup)
            env = dict(os.environ, FONTCONFIG_FILE=self._conf(hint))
            subprocess.run(
                self._render_command(mk, out, px),
                env=env,
                check=True,
                capture_output=True,
            )
            return np.asarray(Image.open(out).convert("RGB"), dtype=np.float32) / 255.0

    def char(self, ch: str, px: int, hint: str = "hintslight") -> np.ndarray:
        return self.render(
            f'<span foreground="#FFFFFF">{html.escape(ch)}</span>', px, hint
        )[:, :, 0]


def blur(a: np.ndarray) -> np.ndarray:
    k = np.array([1, 2, 1], np.float32) / 4
    a = np.apply_along_axis(lambda r: np.convolve(r, k, "same"), 1, a)
    return np.apply_along_axis(lambda c: np.convolve(c, k, "same"), 0, a)


def _image_correlation(a: np.ndarray, b: np.ndarray) -> float:
    x, y = a - a.mean(), b - b.mean()
    d = math.sqrt((x * x).sum() * (y * y).sum())
    return float((x * y).sum() / d) if d else -1.0


def similarity(a: np.ndarray, b: np.ndarray, shift: int) -> float:
    h, w = max(a.shape[0], b.shape[0]), max(a.shape[1], b.shape[1])
    A = np.zeros((h, w), np.float32)
    A[: a.shape[0], : a.shape[1]] = blur(a)
    Bm = np.zeros((h, w), np.float32)
    Bm[: b.shape[0], : b.shape[1]] = blur(b)
    best = -1.0
    for dy in range(-shift, shift + 1):
        for dx in range(-shift, shift + 1):
            S = np.roll(np.roll(Bm, dy, 0), dx, 1)
            best = max(best, _image_correlation(A, S))
    return best


def confusability(r: Renderer) -> dict[int | str, dict[str, float]]:
    out: dict[int | str, dict[str, float]] = {}
    for px in SIZES:
        chars = sorted({c for p in CONFUSABLE for c in p})
        with ThreadPoolExecutor(8) as ex:
            cache = dict(zip(chars, ex.map(lambda c: r.char(c, px), chars)))
        out[px] = {
            f"{a}/{b}": round(similarity(cache[a], cache[b], 1), 3)
            for a, b in CONFUSABLE
        }
    return out


def _bigram_gap(r: Renderer, px: int, bg: str) -> float | None:
    a, b = (html.escape(c) for c in bg)
    img = r.render(
        f'<span foreground="#FF0000">{a}</span><span foreground="#00FF00">{b}</span>',
        px,
    )
    red, green = img[:, :, 0] > 0.3, img[:, :, 1] > 0.3
    gaps = []
    for y in range(img.shape[0]):
        ra, gb = np.nonzero(red[y])[0], np.nonzero(green[y])[0]
        if len(ra) and len(gb):
            gaps.append(gb.min() - ra.max())
    return float(np.mean(gaps)) if gaps else None


def spacing(r: Renderer, px: int = 40) -> Spacing:
    """Measure bigram gap variation; e.g. ``spacing(Renderer("regular.otf"))``."""
    with ThreadPoolExecutor(8) as ex:
        res = dict(zip(BIGRAMS, ex.map(partial(_bigram_gap, r, px), BIGRAMS)))
    vals = np.array([v for v in res.values() if v is not None])
    ordered = sorted((v, k) for k, v in res.items() if v is not None)
    return {
        "mean_gap_px@40": round(float(vals.mean()), 2),
        "cv": round(float(vals.std() / vals.mean()), 3),
        "tightest": [k for _, k in ordered[:6]],
        "loosest": [k for _, k in ordered[-6:]],
        "n": len(vals),
    }


def roman_italic(rr: Renderer, ri: Renderer, px: int = 15) -> RomanItalic:
    letters = "abcdefghijklmnopqrstuvwxyz"
    with ThreadPoolExecutor(8) as ex:
        R = list(ex.map(lambda c: rr.char(c, px), letters))
        I = list(ex.map(lambda c: ri.char(c, px), letters))
    per = {c: round(similarity(a, b, 2), 3) for c, a, b in zip(letters, R, I)}
    return {"mean": round(float(np.mean(list(per.values()))), 3), "per_letter": per}


def visual_angle(r: Renderer, pt: float = 12) -> dict[str, VisualAngle]:
    out: dict[str, VisualAngle] = {}
    for name, ppi, scale, dist in SETUPS:
        px = pt * 96 / 72 * scale
        mm = r.xh * px / ppi * 25.4
        out[name] = {
            "x_height_mm": round(mm, 2),
            "degrees": round(math.degrees(2 * math.atan(mm / 2 / dist)), 3),
        }
    return out


def sharpness(r: Renderer) -> dict[str, float]:
    text = "fn parse(raw: &amp;str) -&gt; Option&lt;Entry&gt; // não é fungo · summary 2026"
    out: dict[str, float] = {}
    for hint in ("hintslight", "hintnone"):
        g = r.render(f'<span foreground="#FFFFFF">{text}</span>', 12, hint)[:, :, 0]
        ink = g[g > 0.1]
        out[hint] = round(float((ink > 0.9).mean()), 3)
    return out


def _measure_spec(spec: str) -> tuple[str, FontMetrics]:
    label, paths = spec.split("=", 1)
    reg, _, ita = paths.partition(":")
    rr = Renderer(reg)
    res: FontMetrics = {
        "font": f"{rr.family} {rr.style}",
        "x_height_em": round(rr.xh, 4),
        "confusability": confusability(rr),
        "spacing": spacing(rr),
        "visual_angle": visual_angle(rr),
        "sharpness": sharpness(rr),
    }
    if ita:
        res["roman_italic"] = roman_italic(rr, Renderer(ita))
    return label, res


def _measure_args(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--font", action="append", required=True, help="LABEL=REGULAR[:ITALIC]"
    )
    ap.add_argument("--out", default="docs/metrics")
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """Measure fonts and save reports; e.g. ``main(["--font", "Jandi=font.otf"])``."""
    a = _measure_args(argv)
    results = {}
    for spec in a.font:
        label, res = _measure_spec(spec)
        results[label] = res
        print(f"measured {label}")
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    Path(a.out + ".json").write_text(json.dumps(results, indent=1, ensure_ascii=False))
    write_md(results, a.out + ".md")
    print(Path(a.out + ".md").read_text())


def write_md(res: dict[str, FontMetrics], path: str) -> None:
    """Write the established metrics tables; e.g. ``write_md(results, "metrics.md")``."""
    markdown = metrics_markdown(res, SIZES, CONFUSABLE, [name for name, *_ in SETUPS])
    Path(path).write_text(markdown)


if __name__ == "__main__":
    main()
