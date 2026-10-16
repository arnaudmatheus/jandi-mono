# Jandí Mono — spec

Monaspace Radon's cursive, rewritten with a Renaissance broad-nib pen, for the
Jandí Omarchy theme. A terminal font first: it must hold the grid.

## Base and names

- Base: **Monaspace Radon** (Lettermatic for GitHub Next), OFL 1.1.
  Upstream static Regular in `sources/upstream/`, with its LICENSE.
- Reserved Font Names: "Monaspace", "Argon", "Neon", "Xenon", "Radon",
  "Krypton". None may appear in this font's name. Working name: **Jandí Mono**.
- **Michelangelus is inspiration only.** Its EULA forbids reverse engineering
  and redistribution: no outlines, no measurements traced from it. What we take
  are its stated principles: start from the italic, the hand lifts between
  letters, modular "hidden order", the signature `g`.

## Decisions (proof 01, 2026-10-16)

| Question | Decision |
|---|---|
| Contrast | **Subtle**: nib 138 × 106 units, ≈1.6 : 1 |
| `f` | **Chancery f with descender** (after Michelangelo) |
| `g` | **Signature-inspired loop, default** |
| Width | **Keep the narrower chancery proportions** |
| Cell (2026-10-16) | **1160** (was Radon's 1240): spacing read too airy; Radon glyphs and NF icons scaled to it |

## Pen model (tools/pen.py)

- Every letter is a centreline skeleton drawn upright, slanted **7°**, then a
  rectangular nib at **35°** is swept along it. Thick/thin is never drawn by
  hand.
- Radon's vertical grid is kept: 2000 UPM, advance 1160 (Radon 1240), x-height 1027, cap 1460,
  ascender ≈1550, descender −426, line 1990 / −500.
- Stem weight matches Radon (n stem ≈175 units vs Radon 156–176).

## Omarchy requirements

- Strict monospace; listed by `omarchy font list`; works with
  `omarchy font set`.
- Box drawing, blocks and powerline (tmux) inherited from Radon (scaled to the cell). Braille (btop) is NOT in upstream Radon: only the NF builds have it.
- Nerd Font build for the bar and starship icons.
- Legible at 12 px (9 pt, LG ≈97 PPI), 15 px (bar), 20 px (laptop ≈157 PPI):
  distinct `1 l I`, `0 O`.
- Regular, Bold, Italic, Bold Italic at minimum.

## Jandí requirements

- Correct Portuguese, Tupi and Guarani: `ỹ ĩ ũ ẽ ŷ ï g̃`, with marks anchored to
  each letter's optical centre. Upstream Radon has **no GPOS**, which is why
  `g̃` floats; Jandí Mono adds `mark`/`mkmk` positioning.

## Texture healing (inherited from Radon's `calt`)

Variants `.left` / `.right` / `.both` exist for `f i j l t v` (shifted) and
`m w` (widened past the cell). They are regenerated from the same skeletons,
shifted or widened to Radon's measured extents, so healing keeps working.

## Phases

1. ~~Proof 01: 9 letters, two contrasts~~ — done.
2. ~~Full lowercase + texture-healing variants + marks and anchors, merged into
   upstream Radon Regular, renamed. Proof 02, local install~~ — done
   2026-10-16: `tools/merge.py` → `build/JandiMono-Regular.otf`, 205 glyphs
   replaced, GPOS `mark` added, combining marks reclassified to GDEF class 3.
   `v` given a pointed vertex (round v read as u at 12 px). Still Radon:
   `ß æ ø œ ł đ ħ ĸ ŋ þ ð`, the `i.alt`/`l.alt` stylistic alternates.
   Note: while another font is the Omarchy system font, fontconfig's
   prepend rule returns that font for `Jandi Mono` too — test by making it
   the system font (`omarchy font set "Jandi Mono"`).
3. ~~Figures (`1` flagged, `0` slashed), capitals (inscriptional, sloped)~~ —
   done 2026-10-16: `tools/caps.py`, 478 glyphs replaced. Capitals, figures,
   the 20 extra letters (`ß æ ø œ ł đ ħ ĸ ŋ þ ð Æ Ø Œ Ł Đ Ð Ħ Ŋ Þ`), 137
   accented capitals, texture-healing variants of `E F I L M S T W 1 7`.
   Radon's `ccmp` swaps marks after capitals for `.case` copies and uses
   ready-made Vietnamese stacks (`uni03020301` …): those 29 are pen-drawn and
   anchored too, or `G̃` fails. Dots shortened to square dabs. `Ľ` takes the
   apostrophe caron. Still Radon: punctuation/symbols, `zero.alt01–04`,
   `i.alt`/`l.alt`, `A.italic`/`B.italic`, numr/dnom/sups/sinf figures.
4. ~~Bold / Italic / Bold Italic, Nerd Font patch, preview, OFL repo~~ —
   done 2026-10-16. Bold nib 196×150 (Radon Bold stems ≈250 vs 172, ×1.42,
   same contrast); Italic slant 13° (Regular is already 7°). NF: no FontForge
   here, so `tools/nerd.py` copies the 10,828 icons MonaspiceRn Nerd Font has
   and Jandí Mono lacks (same cell, already scaled), redrawn through a pen.
   Radon has two format-12 cmaps, (0,4) and (3,10): both must get the icons.
   `build.sh` builds all eight; release files in `fonts/otf/`.
