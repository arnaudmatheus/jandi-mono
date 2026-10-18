# Jandí Mono — roadmap 0.4 → 1.0: Barroco e Rococó

**The base inspiration is the Luso-Brazilian Baroque and the *rococó
mineiro*.** The letters come from the pen of Manuel de Andrade de Figueiredo,
the ornament from the carving and painting of Minas Gerais. Rebuilt on
2026-10-17 from the earlier roadmap, which came from two study rounds:
designers' articles on code fonts and peer-reviewed reading research. Every
open item from those rounds is still here, re-sequenced around the new base.

The rule that hasn't changed: **every phase ends with a measured check**
(`tools/measure.py`) against the previous release. A change that doesn't
hold its number doesn't ship, however Baroque it is.

## The base: where each part of the font comes from

| Part of the font | Source | Where it lives | Default? |
|---|---|---|---|
| **Regular / Bold** | Figueiredo, *Nova Escola* (1722), plate nº 9: hooked ascenders, ball terminals | Every letter | Yes |
| **Italic / Bold Italic** | Figueiredo, plate nº 7, the *cursiva*: loops, entries, *rasgos* (his shapes, drawn with the Regular's broad nib) | Comments, emphasis | Yes |
| **Capitals' feet** | Lapidary inscriptions on the *portadas* and church plaques of Minas | Capitals with free stems | Yes |
| **Ball terminals** | The pen's *gota* (drop), as in Figueiredo's plates and the carved scroll ends | Regular `c f j r y`, `C G J S`, figures | Yes, where measured safe |
| **Capitulares** (`titl`) | Aleijadinho's carved scroll capitals: the stone medallions and *portadas* (São Francisco de Assis, Ouro Preto) | Headings, lock screen | No, opt-in |
| **Flourished capitals** (`swsh`) | Figueiredo's four models of ornamented capitals, copied in the Minas *Compromissos* | Headings, Days | No, opt-in |
| **Florões** | *Rocalha* C- and S-scrolls, shells and crests from the carving | `❦ ❧ ☙`, U+1F650–1F67F | Only by code point |
| **Cartelas** (frames) | The painted cartouches of Manuel da Costa Ataíde's ceilings | Ornamental brackets `❨❩❪❫❴❵` U+2768–2775 | Only by code point |
| **Filactérios** (banners) | The ribbon scrolls that carry inscriptions in the carving and ceilings | Banner ends, Ornamental Dingbats block | Only by code point |
| **Palette bridge** | Azulejo cobalt ≈ jenipapo, Ataíde's red ≈ urucum, gilded *talha* ≈ Casulla gold | Specimen, README, themes | n/a, not glyphs |

**Ornament lives at the terminals and in opt-in places, structure in the
stems.** A Baroque church is a regular plan under a carved surface. A
monospace is the same: the cell and the stems stay regular, and the ornament
goes where reading doesn't depend on it.

## Principles

- **Legibility first.** "Disfluent" fonts don't help memory: Diemand-Yauman
  2011 failed to replicate (Meyer et al. 2015), and so did Sans Forgetica
  (Taylor et al. 2020, Geller et al. 2020). Ornament never costs reading.
- **Ornament in default text must pass the harness.** A ball, foot or hook
  ships only if no confusable pair gets more than 0.01 worse.
- **Everything else is opt-in**, by feature (`titl`, `swsh`) or by code point
  (florões, cartelas, filactérios). Box drawing stays plain, because TUIs need
  its corners to join.
- **Distinct `1 l I` and `0 O` stay.**
- *"A letra deveria ser um corpo com proporção, perfeito, igual nas alturas e
  nas distâncias"* — Figueiredo, 1722. In English: a letter should be a body
  in proportion, equal in its heights and its distances. It reads as the 1722
  brief for a monospace.

## Decisions still in force (2026-10-16)

| Question | Decision | Note |
|---|---|---|
| Upright Regular | **No. Regular stays slanted 7°** | The user doesn't need the dyslexia accommodation. The italic slowdown (Tinker; Slattery & Rayner) is a modest cost, accepted knowingly |
| Chancery `f`, signature `g` | **Keep, in every style** | Familiarity grows with exposure (Beier & Larson 2013) |
| Wide accessibility build | **Yes, cell 1320** | Closer to Zorzi et al. 2012's spacing |
| Text weight (≈450) | **Yes** | Five styles |
| Code ligatures | **On by default** (against Butterick, by choice) | In `liga`, not `calt`, so `-liga` turns them off and keeps texture healing |

---

## Done

### 0.3.0: measurement and skeleton ✅

- **A. Harness.** `tools/measure.py` measures confusability, spacing CV,
  roman/italic similarity, visual angle and sharpness. The baseline is in
  `docs/metrics-0.2.0.md`.
- **B2. x-height 1027 → 1080.** 0.216° at 12 pt on the LG. The laptop is at
  0.160°, so read at ≥ 15 pt there.
- **B3. Distinctiveness.** Mean confusability went from 0.908 to 0.894 at
  12 px. `l/I` dropped from 0.969 to 0.903 and `i/l` from 0.936 to 0.865.

### 0.4.0: Barroco na letra ✅

**Regular after plate nº 9**
- Larger hooked ascenders on `b d h k`, each closed by a ball. `l` keeps its
  plain entry: the hook made `l/I` worse.
- Drops on `c f j r y`. The drops on `c` and `r` are small (radius 18), and
  the `r` arm is pulled back. At full size they closed `c` toward `o` and
  pulled `r` toward `n`.
- Lapidary feet on `F H K M N P R T`, and drops on `C G J S` and on `2 3 5 6 9`.

**Italic: the *corsiva* after plate nº 7**
- His shapes, drawn with the Regular's broad nib.
- Looped `h k`, and an `l` whose loop sits wholly above the x-height. Lower,
  it crossed the stem where `t` has its bar.
- A left curl on `d`, a straight `b`, and a *rasgo* on `p`.
- `n` and `u` differ at both ends. `n` has the long lead-in and a short exit;
  `u` enters straight and leaves long.
- A short-armed `r` with no drop, and a `c` with no drop.

| Measure (12 / 15 / 20 px) | 0.3.0 | 0.4.0 |
|---|---|---|
| Regular confusability (mean) | 0.894 / 0.874 / 0.850 | **0.892 / 0.872 / 0.848** |
| Italic confusability (mean) | 0.894 / 0.876 / 0.852 | **0.884 / 0.859 / 0.829** |
| Roman/italic similarity (15 px; lower is better) | 0.976 | **0.968** (Radon 0.956) |
| Spacing CV | 0.283 | 0.283 |
| Pairs more than 0.01 worse, either style, any size | n/a | **none** |

In the Italic, `i/l` went from 0.916 to 0.806 (12 px) and `l/t` from 0.837 to 0.750
(20 px).

**Rejected by the numbers:**
- **Figueiredo's pressure quill for the Italic.** It filled the counters:
  eight pairs got worse, with `c/o` +0.044 and `n/u` +0.036, even lightened
  to (165, 120). The same quill on the Regular made five pairs worse.
- **Drops on the italic `c` and `r`.**
- **A looped italic `b`**, read as `h`.
- **An inward-curling `h`**, read as `b` (0.994).
- **The corsiva's long exit on `t`**, which matched the `l` tail.
- **The `ASC` hook on the Regular `l`.**

### 0.5.0: spacing, the regular plan under the carving ✅

**D1. Optical centring, on `r` and `k` only.** They now centre on their ink's
centre of mass instead of their bounding box. Each letter was tested alone:
- `r` alone took spacing CV from 0.283 to 0.265.
- Applied to every letter, it made `i/l`, `l/I` and `t/f` worse: narrow
  letters lined up alike in the cell.
- `c e s b h` each traded one pair for another.

**D2. Texture healing re-derived.** Radon's healing makes narrow letters step
aside and wide letters grow into the room. Jandí's `m` and `w` already fill the
cell, so growing them made the healed pairs the tightest in the font: `mt` and
`wt` at 7.5 px against a 13.8 px mean, at 40 px. I searched a grid of
strengths, scoring both bigrams and three-letter contexts (the `i–n` in `min`).
The winner: wide lowercase doesn't grow, and narrow letters keep Radon's step.
- CV over everything: 0.266 → 0.247 (Regular), 0.290 → 0.264 (Italic).
- Tightest healed pair: 7.5 → 10.0 px.
- Healing can't touch narrow beside narrow (`li ti fi`, the loosest) or wide
  beside wide (`mm ww`, the tightest). Only redrawing can: noted for F1.

**D3. Jandi Mono Wide, cell 1320** (and Wide NF).
- Same letters. Only glyphs whose ink touches both cell edges stretch (box
  drawing, blocks), so lines still join.
- Brackets and punctuation keep the default width, centred. Stretched, `[`
  and `{` grew alike (`[/{` +0.018 at 12 px).

**D4. Mark on mark.**
- A `mkmk` feature, plus mark anchors on every precomposed accented letter.
  HarfBuzz recomposes `u + ¨` into `ü` before positioning, so `ǘ`'s acute
  needs an anchor on `ü`.
- The stack height is measured on the ink: the downward acute hangs 131 units
  below its own anchor, so a fixed step left it on the dieresis.
- Known limit: Pinyin capitals (`Ǘ`) reach 2158 units, above the 1890 ascent,
  so a terminal may clip the top accent.

| Measure | 0.4.0 | 0.5.0 | 0.5.0 Wide |
|---|---|---|---|
| Spacing CV, Regular (Radon 0.267) | 0.283 | **0.253** | **0.208** |
| Spacing CV, Italic | 0.302 | **0.271** | **0.222** |
| Regular confusability, 12 / 15 / 20 px | 0.892 / 0.872 / 0.848 | 0.892 / 0.872 / 0.845 | 0.895 / 0.874 / 0.846 |
| Italic confusability, 12 / 15 / 20 px | 0.884 / 0.859 / 0.829 | 0.884 / 0.859 / 0.827 | 0.884 / 0.858 / 0.827 |
| Pairs more than 0.01 worse | n/a | **none** | `v/y` +0.011 at 12 px |

Wide's one exception is not a shape change. The outlines are the default's;
the 1320 cell puts each letter at a different pixel phase at 12 px. Nudging
the letters off-centre to match would show at large sizes, so it stays.

### 0.6.0: pen punctuation and ligatures ✅

**E1. Punctuation with the pen** (`tools/punct.py`).
- **Drawn from skeletons:** `. , : ; ' " ! ? ( ) [ ] { }`. Their unit is the
  *gota*, a teardrop the nib leaves turning on the spot. It rests on the
  baseline like Radon's dot.
- **The comma:** a smaller drop whose tail falls straight while the nib is
  at full width and turns left only at the end. Every drawn glyph sits on
  Radon's own centre, so code columns don't move.
- **The carved C-scroll:** braces whose two curves meet in a deep point.
  Parentheses are deep bows, and brackets have long square arms.
- **Re-stroked from Radon:** `- _ / \ * + = < > | @ # & ~ ^`, their
  texture-healing and contextual variants, and all ~85 ligature glyphs. The
  nib is swept along the medial axis of Radon's outline (Voronoi edges of the
  outline, with loose ends pushed back out to it). Radon's geometry and
  cross-cell joins stay, and the weight comes from our nib alone: hyphen 163,
  `|` 175, against the `l` stem's 175 (Radon's were 178 and 182).
  - Round dots inside ligatures (`...`, `!=`, `::`) become drops.
  - Solid shapes (the triangle of `|>`) stay solid, leaned to our angle.
  - Everything is sheared from Radon's angle (0°, 11° italic) to ours (7°,
    13°) around the math axis.

**E2. Ligatures on by default.** All ten stylistic sets moved into `liga`,
including `ss06` (`### +++ ___ &&`). Verified with HarfBuzz, which Ghostty and
foot both shape with: `=> -> != === <= |> :: ###` ligate with no feature flag,
`-liga` returns every plain character, and texture healing (`calt`) still
runs.

**Iterations the numbers decided:**
- **Uniform thinning of Radon's outlines** (erode, then sweep the nib)
  failed. After the rescale to our 1160 cell, diagonals are thinner than the
  thinning depth, so `< > /` and the arrows broke apart. The medial axis
  replaced it.
- **The comma:** a tail that turned left at once vanished at 12 px (`:/;`
  0.874 → 0.947). Six tails were scored. The winner falls straight first,
  under a smaller head, and stays inside the 500-unit descent.
- **Colon dots at 0.85 of the period's drop.** At full size, the shared top
  dot made `;` read as `:`.
- **Parentheses and braces:** bow depth and brace point were scored at four
  and three depths.

| Measure | 0.5.0 | 0.6.0 | Radon |
|---|---|---|---|
| `,/.` at 12 px | 0.922 | **0.917** | 0.918 |
| `:/;` at 12 px | 0.874 | **0.876** | 0.899 |
| `(/[` at 12 px | 0.878 | **0.811** | 0.819 |
| `[/{` at 12 px | 0.914 | **0.884** | 0.921 |
| Regular confusability, mean 12 / 15 / 20 px | 0.892 / 0.872 / 0.845 | **0.887 / 0.864 / 0.828** | |
| Italic confusability, mean 12 / 15 / 20 px | 0.884 / 0.859 / 0.827 | **0.879 / 0.849 / 0.808** | |
| Pairs more than 0.01 worse (Regular, Italic, Wide) | n/a | **none** | |
| Sharpness at 12 px, hintslight | 0.143 | 0.136 | 0.158 |

**Not done, carried to 0.7.0:** the letters' dots (`i j ä`) and the ball
terminals still use the small dab, not the punctuation drop. Dot size feeds
`i/l` and `i/j`, so that change needs its own measured pass. Sharpness dipped
with the new curves, which is F2's job (hinting).

### 0.7.0: outline quality and the Text weight ✅

**F1. Smooth curves** (`tools/fitcurves.py`). The pen's polygon outlines are
fitted back into cubic Béziers with Schneider's algorithm (*Graphics Gems*,
1990). Real corners stay sharp: the nib's square ends and joins between
strokes.
- **Faithful:** every outline stays within about 1 unit of the pen shape on
  average (2000 per em).
- **Lighter:** letters went from 55 segments on average to 26 (Radon: 18), so
  `o` 91 → 22 and `a` 79 → 27. That's 2× overall, not the 5× once aimed for.
  What remains is structure, not noise: each stroke's square ends and joins.
  A looser fit only went from 2527 to 2127 segments while doubling the error.
- **Two bugs the area check caught.** A ring with a single corner collapsed
  into a line, which filled the counters of `O` and `g`. Long straight edges
  bulged between the polygon's vertices, so runs are now densified before
  fitting.

**F2. Hinting.** `otfautohint` (AFDKO) runs in `build.sh`.
- **Alignment zones measured per style** from the ink: x-height 1101–1123,
  ascender 1584–1606, descender −455. Radon's zones (x-height 1027, ascender
  1530) no longer matched the pen letters.
- **Stems from the nib:** 174 vertical, 166 horizontal.
- **Some letters stay unhinted.** Hinting everything made narrow pairs more
  alike: snapping lined their heights up (`i/l` +0.014, `f/j` +0.012, `1/l`
  +0.011, `g/q` +0.011). Excluding one letter of a pair only moved the
  problem. So `i l j q 1` stay unhinted with all their accented and healing
  forms (`tools/nohint.py`), and `t f` too in the italics (`l/t` +0.018,
  `t/f` +0.023 otherwise).

**F3. The pairs healing can't reach.** `m` and `w` narrowed: stems at
300/600/900 instead of 250/600/950, in the corsiva too.
- `mm mw ww` were the tightest pairs: 6.5 px at 40 px against a mean of 14.
- Spacing CV 0.252 → 0.232 (Regular) before hinting, with no pair worse.
- **Rejected:** a longer `i` exit (`i/l` +0.012) and a `t` bar reaching
  further left (`t/f` +0.025). Narrow beside narrow stays the loosest.

**F4. One drop: only for the ball terminals.**
- **Ball terminals** on `c f j r y`, `C G J S` and the figures are now the
  punctuation's teardrop (`pen.GOTA`). `i/j` and `f/j` improve by
  0.005–0.008, and nothing gets worse.
- **Dots stay dabs.** As drops, the dots of `i j` and the diacritics made
  `i/l` worse at every size tried (+0.028 to +0.047). A rounder, heavier dot
  fills the room above the stem that tells `i` from `l`.

**G. Jandi Mono Text** (Regular and Italic, plus NF): the nib 8% wider,
weight class 450, for light backgrounds and the 97 PPI monitor. Both checks
pass:
- `l` stem 174 → 188 (+8.0%).
- The thinnest stroke is 0.98 px at 12 px (target ≥ 0.6).
- Its punctuation pairs are at or below Radon's (`(/[` 0.810 vs 0.819,
  `[/{` 0.882 vs 0.921). They sit above 0.7.0's Regular, as a heavier stroke
  closes counters; that's the expected cost of the weight.

| Measure | 0.6.0 | 0.7.0 | Radon |
|---|---|---|---|
| Regular confusability, 12 / 15 / 20 px | 0.887 / 0.864 / 0.828 | **0.866 / 0.840 / 0.815** | 0.869 / 0.844 / 0.801 |
| Italic confusability, 12 / 15 / 20 px | 0.879 / 0.849 / 0.808 | **0.862 / 0.829 / 0.798** | |
| Spacing CV, Regular / Italic / Wide | 0.253 / 0.271 / 0.208 | **0.239 / 0.256 / 0.196** | 0.267 |
| Sharpness at 12 px (hintslight), Regular / Italic | 0.136 / 0.127 | **0.157 / 0.165** | 0.158 |
| Pairs more than 0.01 worse (Regular, Italic, Wide) | n/a | **none** | |

Builds run at most `JOBS` processes at once (default 4): with everything in
parallel the machine ran out of memory.

### 0.8.0: ornament, the carving and the ceiling ✅ (built and measured, not yet released)

Drawn in `tools/ornament.py`, all opt-in. Every motif is one skeleton;
mirrored and turned forms are made before the nib sweeps it, so the 35°
contrast never flips.

**I1. Florões** at `❦ ❧ ☙` and U+1F650–1F667:
- the **hedera** (the printer's floral heart), solid, with a scrolled stem;
- the **rocalha leaf**, in four directions plus the turned forms;
- the **vine leaf** and the **bud**, each light and heavy.

**I2. Cartelas** at `❨❩ ❪❫ ❲❳ ❴❵`: frame halves after Ataíde's ceiling
cartouches.
- `❨❩` are C-scroll bows with scrolled ends and a drop.
- `❪❫` carry a shell.
- `❲❳` have chamfered corners with drops.
- `❴❵` are scroll braces with a volute at the point.

**I3. Filactérios.** Unicode has no banner code points, which the earlier
plan assumed it did. The swallowtail ribbon ends live at `❰ ❱` instead (the
heavy angle bracket ornaments). Their band ends exactly at the cell edge, to
meet the inscription. `❮ ❯` keep Radon's design: `❯` is Starship's default
prompt.

**I4. Capitulares**, two OpenType features, off by default:
- `titl`: carved capitals, a heavier stroke with a fine groove down its
  centre, as in V-cut stone lettering;
- `swsh`: Figueiredo's rasgo, a volute over the capital's head and a swash
  under the baseline. These overhang their cell on purpose; they are for
  headings, not the terminal.

**The lesson the drawings taught.** A curl narrower than about 2.5 nib widths
fills in and becomes a blot. Every scroll is an open Archimedean spiral with
the drop at its eye, and curls, veins and tendrils use a fine engraved line
(0.55 of the nib), as engraved Baroque ornament does. Ornaments wider than
the cell are scaled to fit, so they never paint over a neighbour in a
terminal.

*Check:* with the features off, every metric of Regular, Italic, Wide and
Text is **identical** to 0.7.0 (confusability, spacing, sharpness, visual
angle, roman/italic). With them on, HarfBuzz shapes `titl`/`swsh` and every
ornament maps in the plain and NF builds. Nothing passes the ascent or the
descent.

---

## Next

### Code health (after 1.0.0-beta.1)

`CLAUDE.md` is the repository's code standard from 2026-10-18. The code
predates it. The refactor below is its own step, kept out of any release.
Every step must produce **byte-identical fonts**: same glyphs and tables,
compared against a build of the commit before. The fonts are the product,
and a refactor must not move them.

1. **English everywhere ✅** (done before the beta): about 65 Portuguese
   comment lines and the build's messages were translated, meaning and
   provenance intact.
2. **pytest ✅** 53 tests, under two seconds (`pytest`), on tiny fonts built
   in memory and one named fake (`tests/fakes/failing_python`). Regression
   tests for the bugs already found:
   - the single-corner ring that filled counters in the curve fitter, and
     long edges that bulged;
   - diagonals vanishing in the restroke (the mitred negative buffer), and
     overlapping contours read even-odd;
   - the summation order that moved last digits: the vectorised sweep and
     the inlined fitter are checked bit for bit against the code they
     replaced;
   - a bare `wait` hiding failed builds;
   - Windows metrics per font instead of per family.
3. **Split `merge.py` ✅** The 579-line script is now a 90-line
   orchestrator and one module per step: `cell`, `place_letters`,
   `place_symbols`, `place_ornaments`, `healing`, `accents`,
   `mark_positioning`, `zones`, `naming`, with `build_options`,
   `build_state`, `glyph_table`, `glyph_writer`, `gsub_features` and
   `anchors` under them. `pen.py` is the engine (122 lines); the lowercase
   moved to `letters.py`. Dead code from the proofs went with it: the
   pointed-quill sweep, `glyph_shape`, `skeleton`, the tilde composites.
   `tools/identical.py` checked every step: all ten fonts byte-identical.
4. **Functions of 4–20 lines, at most two levels of indentation ✅**
   Split the remaining curve fitter, punctuation, measurement/reporting,
   regression gate, STAT metadata and flourish functions. `nerd.py` and
   `nohint.py` now have importable functions and guarded `main()` entry points.
   Arithmetic order and report formatting stay unchanged. The suite now has
   82 tests; all ten unhinted fonts, NF output tables and hint exclusions
   match the previous code (only font timestamps/checksums are ignored).
   [Validation notes](docs/code-health-step4.md).
5. **Explicit types** on every function: done for the new modules
   (`pen_types.py`: Point, Stroke, StrokesFn, Bounds, GlyphSet). Left: the
   drawing modules (letters, corsiva, caps, ornament, punct, marks), pen,
   fitcurves, finish, measure, check.
6. **Dependencies injected**: pass the pen settings (nib, slant, cell) as a
   value instead of setting `pen.SLANT`, `pen.ADV` and `pen.OPTICAL` as
   module globals, and stop merging the corsiva into `letters.LETTERS` in
   place.
7. **Formatter and CI ✅** `black` over tools and tests; a `test` job runs
   `black --check` and `pytest` beside the builds, and releases wait for it
   (`requirements-dev.txt`, pinned).

### Build infrastructure

- **Pipeline ✅** (`.github/workflows/build.yml`). Every push and pull
  request builds all families on a GitHub runner. `tools/check.py` fails the
  job if a confusable pair is more than 0.01 worse than the fonts committed
  before. A `v*` tag matching `VERSION` publishes the Release. The NF icons
  come from Nerd Fonts v3.5.1, pinned by SHA-256.
- **Parallel CI ✅.** Five build jobs of two fonts each (with their NF)
  run at once; a final job gathers them, runs the gate and publishes.
  `build.sh` takes `FAMILIES` and `STYLES` to build a part, and now fails if
  any font fails (a bare `wait` had been hiding failed jobs).
- **Faster code ✅, with identical output:** one font builds in about 50 s
  instead of 104 s. Every glyph is byte-identical to the 0.8.0 release,
  checked on Regular, Bold and Wide Italic.
  - The nib sweep is vectorised (NumPy and Shapely 2 array calls).
  - The centreline tests its Voronoi edges as arrays.
  - The curve fitter's hot helpers are written inline.
  - The cell rescale draws each glyph once.
- **Arithmetic order matters, and was kept.** Two tries changed the last
  digit of some coordinates: a NumPy curve fitter (sums in another order),
  and nib corners summed as `x + (ux + vx)` instead of `(x + ux) + vx`. The
  outlines moved by less than a unit, but a few round letters then split
  their curves differently, and after hinting `O` read closer to `0` at
  12 px (`0/O` +0.046). The regression gate caught both, so both were redone
  to keep the exact order.
- **Still open:**
  1. Derive Wide from the normal family instead of drawing it twice.
  2. A per-glyph cache, keyed on skeleton, nib, slant and cell.

### 1.0.0: validation and release (1.0.0-beta.1 released; final after one more reading session)

- **Reading-speed self-test ✅ built**:
  [Jandí Reading Test](https://claude.ai/artifact/XDD6j8zVNS581xVPPGP3Lz).
  - Eight passages in Portuguese, two per font: Jandi Mono, Wide, Text and
    Radon.
  - Fonts shown blind as A–D in a shuffled order, with no font twice in a
    row.
  - A comprehension question after each passage. Speed counts only passages
    answered correctly.
  - Sessions are saved, so results average across days. The best font
    differs per reader (Wallace et al. 2022), so the user's own results
    decide 1.0's default.
  - **Waiting on the user's sessions.**
- **fontbakery ✅** (pinned 1.1.0, CI `qa` job, every family). Fixed:
  - the font revision now agrees with the name table;
  - Windows clipping metrics cover every glyph;
  - a STAT table, with each static font naming only its own weight and
    italic;
  - the italic caret slope;
  - no legacy Mac name records.

  Two checks are excluded, with reasons in the workflow:
  - `case_mapping`: about 15 African-language lowercase letters inherited
    from Radon have no capitals, and Radon fails it too;
  - `opentype/monospace`: it crashes on CFF fonts, a fontbakery bug.
- **Specimen ✅**: a Baroque *folha* (`tools/specimen.sh`) with Figueiredo's
  plate nº 7 and the ornament. Its palette bridge: azulejo cobalt to Jandí
  blue, Ataíde's red to urucum, gilded *talha* to jenipapo pulp. Earlier
  drafts said "Casulla gold", but Casulla is another theme; Jandí's own
  yellow is the right pair.
- **Reading-size guidance ✅** in the README, with a table per screen.
- **Omarchy ✅**: already the system font (`omarchy font set "Jandi Mono
  NF"`) and Ghostty's.

**Reading test, session 1 (2026-10-18), not used for the decision.** On the
LG at 16 px, dark theme, read speeds ran from 67 to 656 words a minute.
Normal silent reading is around 200–350.
- The two slowest passages were the ones where the user stopped to study the
  letters, which turned up the two observations below.
- Speed doubled from the first half of the session to the second, a warm-up.

So the test was revised (v2):
- a practice passage that isn't counted;
- reads below 120 or above 500 wpm are left out, with the reason shown;
- instructions to read for meaning, and a separate box for notes on a font;
- a winner is named only when the gap between fonts beats the spread within
  each font.

Averages use only v2 sessions.

**Session 2 (v2, same day), also not used.** The test reused the same
eight passages, so on the second run the reader knew the texts and the
answers. Five of the eight passages took 2–10 s (700 to 2,900 wpm), and
every question was still answered correctly. The pace check left them out,
which left one counted passage each for three fonts and none for Radon.

So the test was revised again (v3):
- a pool of 29 passages of about 150 words, and each session takes the nine
  the reader has seen least, so no text repeats until the pool runs out;
- four-option questions whose wrong answers come from the passage itself.

Averages use only v3 sessions.

**Session 3 (v3, 2026-10-18), the first valid one.** On the LG at 16 px, in
the dark theme, counted speeds ran from 190 to 329 wpm, a normal reading
range:

| Font | wpm | Passages counted |
|---|---|---|
| Text | 321 | 1 |
| Jandi Mono | 299 | 1 |
| Radon | 296 | 2 |
| Wide | 231 | 2 |

The reader's own passages varied 22–36% within a font, more than any gap
between fonts. So far, no font is measurably faster for this reader, and
Jandi Mono stays the default. One more session on another day would firm
it up.

After this session the test shuffles which letter each font wears every
session (v3.1). The A–D mapping had been fixed and was revealed after
session 1, so the test was no longer blind.

**Reader observations from the test (2026-10-18), to act on later.** Two
narrow letters side by side leave a visible hole in real words:
- *antigo*: `t i` in **Jandi Mono Wide**;
- *Estrada*: `t r` in **Jandi Mono**.

Session 2's notes (written in the test's note box):
- **Wide**: "too much space between a and l", another narrow letter next to
  a round one.
- **Text**: "the t is a little bit harder to differentiate". The heavier nib
  may close `t` toward `f` or `l`. Check `t/f` and `l/t` on Text with
  `tools/measure.py`.

Session 3's notes, both in Jandi Mono:
- *tipiti* "has a different spacing from the rest": nearly all narrow
  letters, the same cluster as *antigo* and *Estrada*.
- `t` and `r` are hard to tell apart. Measured (similarity, 12 / 15 / 20 px):

  | Font | `t/r` |
  |---|---|
  | Jandi Mono | 0.936 / 0.911 / 0.901 |
  | Jandi Mono Text | 0.937 / 0.904 / 0.892 |
  | Monaspace Radon | 0.790 / 0.721 / 0.647 |

  That makes `t/r` one of the most confusable pairs in the font, worse than
  `r/n`. It was never on the harness's list, so the gate couldn't see it.
  `t/f` and `l/t` are also weaker than Radon's, so the short `t` with its
  right-reaching bar is the common factor.

  **Outcome (1.0.0-beta.1 keeps the 0.8.0 `t`).** `t/r`, then `t/1`, became
  measured pairs. Nineteen redrawn `t`s were measured in Regular and Bold,
  hinted, against 0.8.0:
  - weight moved left (stem right, bar reaching back) separated `t` from
    `r` (0.936 → 0.874) but read as `1`. `t/1` got +0.10 at 20 px, and the
    README hero showed *texto* as "1ex1o";
  - a centred bar read as `f`, a longer foot as `l`;
  - a lowered right bar helped `t/r` a little but cost `t/1` and `l/t` at
    20 px.

  The `t` is boxed in by `r`, `1`, `f` and `l`: at this size no `t` alone
  beats all four. **Next:** redraw `t` together with `r` (or with `1`),
  measured on all five pairs.

It shows in both cells, so it's in the shared letters, not one family's
width. It is the same weakness the measurements found in F3/D2 (`ti ri li`
are the loosest pairs, which texture healing can't reach). The likely fix
is in how `t i r` sit in the cell: their side-bearings, or a measured
narrow-beside-narrow kerning of the healing classes. It must be checked
against the three-letter contexts. Not changed yet, at the user's request.

After 1.0: draw the African-language capitals Radon lacks (`Ɓ Ɗ Ɛ Ɔ Ƈ Ƙ`…),
so `case_mapping` can be checked too.

---

## Order and versions

| Version | Phases | Why this order |
|---|---|---|
| 0.3.0 ✅ | A, B2, B3 | Measure first, then the skeleton |
| 0.4.0 ✅ | Barroco na letra (Regular nº 9, corsiva nº 7, feet, balls) | The base inspiration goes into the letters before anything is built on them |
| 0.5.0 ✅ | D1–D4 | Spacing re-derived from the Baroque shapes |
| 0.6.0 ✅ | E1, E2 | Punctuation and ligatures need the final drop size and spacing |
| 0.7.0 ✅ | F1–F4, G | Curves and hints close the outline pipeline. Text reuses it |
| 0.8.0 ✅ | I1–I4 | Ornament drawn once, in final curves, all opt-in |
| 1.0.0 | Validation | The user's own reading decides |

## Sources

- Manuel de Andrade de Figueiredo, *Nova Escola para aprender a ler, escrever
  e contar* (Lisbon, 1722). Public domain, Biblioteca Nacional de Portugal,
  purl.pt/107. Also at the Library of Congress, loc.gov/item/65058981.
- Márcia Almada (2011), on Figueiredo's models in the Minas *Compromissos*.
- The carving of Antônio Francisco Lisboa, "Aleijadinho", and the painting of
  Manuel da Costa Ataíde, studied through Wikimedia Commons photographs. Each
  image's credit is kept beside it in the specimen.
