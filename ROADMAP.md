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

### 0.5.0: spacing, the regular plan under the carving ✅ (built and measured, not yet released)

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

---

## Next

### 0.6.0: pen punctuation and ligatures

**E1. Punctuation as pen drops.** Redraw `. , : ; ' " ! ? ( ) [ ] { } - _ / \ * +
= < > | @ # &` with the pen.
- One drop size is shared by `. : ; i j ä` and the ball terminals, so the
  Baroque *gota* becomes the font's unit of punctuation.
- The comma is a drop with a tail, unmistakable from the period.
- Braces follow the carved C-scroll: an S-curve with a pointed middle, still
  plain enough to read at 12 px.

**E2. Ligatures on by default.** Move all of Radon's ligatures (8 in `liga`,
~59 in ss01–ss10) into `liga`, then redraw each with the pen: they are still
Radon's monoline shapes. Arrows `-> =>` take a pen-cut head. Texture healing
stays alone in `calt`.

*Check:* confusability of `,/.`, `:/;` and `(/[/{` at or below Radon's.
`=> != -> ===` ligate with no feature flags in Ghostty and foot. `-liga`
restores plain characters with texture healing intact.

### 0.7.0: outline quality and the Text weight

**F1. Smooth curves.** Fit cubic Béziers to the pen outlines (55–120 straight
segments per letter today, against Radon's 13–20). The balls and loops are
where facets show first, at the lock-screen clock and when zooming.

**F3. The pairs healing can't reach.** Narrow beside narrow (`li ti fi`) is
the loosest and wide beside wide (`mm mw ww`) the tightest; Radon's healing
doesn't act on either (D2). Redraw while the outlines are open: the lead-ins
of `i l t` and the stems of `m w`. Measured with the three-letter contexts
from D2.

**F2. Hinting.** Run `otfautohint` (afdko) in `build.sh` so hintslight can
snap the x-height and baseline.

**G. Jandi Mono Text (≈450, nib ×1.08).** For the Jandí Light theme and the LG
at 97 PPI, where thin strokes fade. The corsiva's hairlines matter most here.

*Check:* sharpness at 12 px up, outline points down ≥ 5×, spacing CV down. In Text, stems are
8% heavier and hairlines ≥ 0.6 px at 12 px.

### 0.8.0: ornament (opt-in; the carving and the ceiling)

Built after F1 so the ornament is drawn once, in final curves. Nothing in this
phase changes default text.

**I1. Florões.** *Rocalha* C- and S-scrolls, the shell and the crest, drawn
with the pen at `❦ ❧ ☙` and in the Ornamental Dingbats block (U+1F650–1F67F).
They serve as separators in notes, prompts and the lock screen.

**I2. Cartelas.** Frames after Ataíde's cartouches at the ornamental brackets
`❨❩❪❫❴❵` (U+2768–2775). They enclose a word or a number like a painted
cartouche on a ceiling, e.g. `❪ 1722 ❫`.

**I3. Filactérios.** Ribbon-scroll banner ends that turn a line of text into
an inscribed banner. Placed in the Ornamental Dingbats block.

**I4. Capitulares, two sets:**
- `titl`: Aleijadinho's carved scroll capitals, heavy and three-dimensional in
  feeling, for headings and the lock-screen date.
- `swsh`: Figueiredo's flourished pen capitals, light, for Days and titles.
- Both stay inside the line height and are never on in the terminal.

*Check:* with the features off, every metric is identical to 0.7.0. With them
on, glyphs render in Ghostty, Quickshell and Chromium, and nothing clips.

### 1.0.0: validation and release

- **Reading-speed self-test** page: timed passages in Jandí Mono, Wide, Text
  and Radon. The best font differs per reader (Wallace et al. 2022), so
  measure the user's own fit.
- **fontbakery** QA: OFL metadata, names, vertical metrics, monospace checks.
- **Specimen** as a Baroque *folha*: the palette bridge (cobalt, urucum, gold),
  the capitulares and florões in use, and credits to Figueiredo and the Minas
  sources.
- README reading-size guidance: an x-height of at least 0.2° means ≥ 15 pt on
  the laptop for long reading.
- Omarchy: `omarchy font set "Jandi Mono NF"`.

---

## Order and versions

| Version | Phases | Why this order |
|---|---|---|
| 0.3.0 ✅ | A, B2, B3 | Measure first, then the skeleton |
| 0.4.0 ✅ | Barroco na letra (Regular nº 9, corsiva nº 7, feet, balls) | The base inspiration goes into the letters before anything is built on them |
| 0.5.0 ✅ | D1–D4 | Spacing re-derived from the Baroque shapes |
| 0.6.0 | E1, E2 | Punctuation and ligatures need the final drop size and spacing |
| 0.7.0 | F1, F2, G | Curves and hints close the outline pipeline. Text reuses it |
| 0.8.0 | I1–I4 | Ornament drawn once, in final curves, all opt-in |
| 1.0.0 | Validation | The user's own reading decides |

## Sources

- Manuel de Andrade de Figueiredo, *Nova Escola para aprender a ler, escrever
  e contar* (Lisbon, 1722). Public domain, Biblioteca Nacional de Portugal,
  purl.pt/107. Also at the Library of Congress, loc.gov/item/65058981.
- Márcia Almada (2011), on Figueiredo's models in the Minas *Compromissos*.
- The carving of Antônio Francisco Lisboa, "Aleijadinho", and the painting of
  Manuel da Costa Ataíde, studied through Wikimedia Commons photographs. Each
  image's credit is kept beside it in the specimen.
