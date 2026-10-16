# Jandí Mono — roadmap 0.3 → 1.0

Built from two study rounds (2026-10-16): designers' articles on code fonts
(round 1) and peer-reviewed reading research (round 2). Goal: a font that is
as good for **studying** (long reading, notes) as for code, without losing the
pen. Every phase ends with a **measured** check against the 0.2.0 baseline; a
change that doesn't move its number doesn't ship.

Principles carried from the research:
- Legibility first. "Disfluent" fonts don't help memory (Diemand-Yauman 2011
  failed to replicate, Meyer et al. 2015; Sans Forgetica: Taylor et al. 2020,
  Geller et al. 2020). The pen's character must never cost reading.
- Distinct `1 l I`, `0 O` stay.
- *"A letra deveria ser um corpo com proporção, perfeito, igual nas alturas e
  nas distâncias"* — Manuel de Andrade de Figueiredo, *Nova Escola* (1722).
  The 1722 brief for a monospace: equal heights, equal distances.
- Baroque ornament lives in **opt-in** places (italic, swash capitals,
  ornament code points), never in default text: legibility first.

## Decisions (2026-10-16)

| Question | Decision | Note |
|---|---|---|
| Upright *formata* Regular | **No — Regular stays slanted 7°** (the user doesn't need the dyslexia accommodation) | The italic slowdown was also measured in typical readers (Tinker; Slattery & Rayner): a modest cost, accepted knowingly |
| Chancery `f` and signature `g` | **Keep, in every style** | Familiarity grows with exposure (Beier & Larson 2013) |
| Wide accessibility build | **Yes, cell 1320** | Closer to Zorzi et al. 2012's spacing |
| Text weight (≈450) | **Yes** | Five styles |
| Code ligatures | **On by default** (against Butterick, by choice) | In `liga`, not `calt`: `-liga` turns them off and keeps texture healing |

---

## Phase A — Measurement harness ✅ 0.3.0

Done: `tools/measure.py` (≈4 s per run); baseline in `docs/metrics-0.2.0.md`,
current numbers in `docs/metrics.md`.

### Original plan

Build `tools/measure.py`, rendering through FreeType/Pango with the system's
real settings (hintslight, grayscale AA) at 12 px, 15 px and 20 px.

| Metric | What it measures | Source of the idea |
|---|---|---|
| **Confusability** | Bitmap similarity (normalised correlation after a slight blur) for `e/c a/o n/u s/e i/j/l/t/f 1/l/I 0/O ,/.` | Beier & Larson 2010 |
| **Spacing evenness** | Variance of ink gaps between neighbours over the 200 most frequent bigrams of Portuguese, English and code | Monaspace texture healing; Commit Mono smart kerning |
| **Roman/italic distance** | Similarity of each letter's Regular vs Italic bitmap (lower = easier to tell comments from code) | Operator Mono, JetBrains Mono |
| **Visual angle** | x-height in degrees at the user's real setups (LG 97 PPI @60 cm, laptop 197 PPI @50 cm) | Legge & Bigelow 2011 (critical print size ≈0.2°) |
| **Sharpness** | Edge contrast at 12 px, hinted vs unhinted | FreeType docs |

Deliverable: baseline numbers for Radon and Jandí 0.2.0 in `docs/metrics.md`,
and a proof page that regenerates from the harness.

## Phase B — Foundation: the skeleton changes everything else depends on

~~B1. Upright formata Regular~~ — dropped by decision; Regular stays 7°.

**B2. x-height +5% (1027 → 1080) ✅ 0.3.0.** Result: 0.205° → **0.216°** on the
LG at 12 pt (laptop 0.152° → 0.160°: still below 0.2°, read at ≥ 15 pt there).
No mark clipped; stacked Vietnamese capitals fit. Raises the visual angle at the same point
size (JetBrains Mono maximises x-height for the same reason). Re-check
ascender/descender room, accent clearance, stacked Vietnamese capitals inside
the 1990 ascent.
*Check:* visual angle at 12 pt on the LG ≥ 0.21°; no mark clipped.

**B3. Distinctiveness pass.** Beier & Larson's most-confused groups.
- `i j l t f`: wider feet and hooks (narrow letters gain from widening; the
  cell has room).
- `n/u`: break the mirror (different entry vs exit), `a/o`: clearer stem,
  `e/c`: larger eye, `s`: distinct spine.
*Check (revised after measuring):* mean confusability lower than 0.2.0 at
every size, and no pair more than 0.01 worse than 0.2.0. "≤ Radon for every
pair" proved unrealistic where a decision differs by design: `f/j` is 0.48 in
Radon only because Radon's `f` has no descender, and ours keeps it.

**B3 ✅ 0.3.0**, four measured iterations. Mean confusability 0.908 → **0.894**
(12 px), 0.886 → 0.874 (15 px), 0.864 → 0.850 (20 px); no pair worse than
0.2.0 by > 0.01. Biggest gains: `l/I` 0.969 → 0.903, `i/l` 0.936 → 0.865 (now
below Radon), `h/b` 0.957 → 0.912, `a/o` 0.979 → 0.960. Two ideas were
rejected by the numbers: a lead-in on `u`'s right stem (n/u got worse) and a
tall `t` with a long exit (it started to read as the new `l`). Final forms:
narrower notched `a`, wider `o`, footed `b`, long-exit `h`, short lower hook on
`f` vs big round hook on `j`, wider `i`, sweeping-tail `l`, `t` with a
right-reaching bar, wider `I` bars, longer flag on `1`.

## Phase C — Corsiva Italic, after Figueiredo

Model: the *grifa* and *cursiva* plates of Manuel de Andrade de Figueiredo's
*Nova Escola para aprender a ler, escrever e contar* (Lisbon, 1722). He was
born in the Captaincy of Espírito Santo, Brazil; by 1725 his models were
used for the capitals of the brotherhood statute books (*Compromissos*) of
Minas Gerais — Ouro Preto, Sabará, Caeté, Vila Rica — including brotherhoods
of Black, mixed-race and enslaved people (Almada 2011). Public domain:
digitised at the Biblioteca Nacional de Portugal (purl.pt/107) and the
Library of Congress (loc.gov/item/65058981), so the plates can be studied
and measured directly. His *rasgos* (pen flourishes) inform the entry and exit
strokes; his "interlaced circular strokes" the loops.

Italic and Bold Italic become the *corsiva*: looped ascenders (`b d h k l`),
longer exits, entry hooks, slant ≈13°. With the Regular staying at 7°, the
angle alone separates them by only 6°, so this phase carries the whole
distinction: comments differ from code by **shape**, which also helps
colour-blind readers (Hoefler's reason for Operator Mono's cursive).
*Check:* roman/italic distance clearly above 0.2.0's; italic confusability
still ≤ Radon.

## Phase D — Spacing system

**D1. Optical centring.** Centre each letter on its visual mass (ink
centroid blended with the bounding box), not only the box: `r f j t c L F P 7 1`.

**D2. Texture healing re-derived from Jandí's own widths.** Today's shifts are
copied from Radon's shapes. Recompute giver/taker classes from Jandí's ink
widths (the narrower forms create new givers: `r t f j c s`) and the shift
amounts that equalise gaps, Commit Mono style (it documents 44 units for `o`
between `m` and `i`).

**D3. Jandi Mono Wide (accessibility build), cell 1320.** Same design, wider cell:
extra-large spacing made dyslexic children read 20% faster with half the
errors (Zorzi et al. 2012). Default stays 1160 (Slattery & Rayner 2013:
added letter spacing slows typical readers).
*Check:* spacing-evenness variance below 0.2.0's; Wide builds and installs.

## Phase E — Pen punctuation, symbols and ligatures

**E1.** Redraw `. , : ; ' " ! ? ( ) [ ] { } - _ / \ * + = < > | @ # &` with
the pen. Large and clear in code (Input), comma unmistakable from period
(JetBrains), one consistent dot size shared with `i j ä`.

**E2. Code ligatures on by default.** Radon keeps 8 ligatures in `liga`
(`|| !! ;; // ...`) and ~59 behind opt-in stylistic sets: ss01 `== === =~`,
ss02 `>= <=`, ss03 arrows `-> ~> -->`, ss04 markup `</ /> <>`, ss05 `|> <|`,
ss07 `::`, ss08 `..`, ss09 `=> >> <== >>=`, ss10 `#[ #(`. Move all of them
into `liga` (texture healing stays alone in `calt`, so `-liga` disables
ligatures without losing healing), and redraw every ligature glyph with the
pen: they are still Radon's monoline shapes.
*Check:* confusability of `,/.` `:/;` `(/[/{` ≤ Radon; braces read at 12 px;
`=> != -> ===` form ligatures with no feature flags in Ghostty and foot, and
`-liga` restores plain characters with texture healing intact.

**E4. Mark-to-mark stacking (`mkmk`).** Found while checking B2: `ǘ ǚ`
(Pinyin) aren't precomposed in Radon, so they're built from parts, and the
second mark doesn't stack (no `mkmk`). Present since 0.1.0.

**E3. Florões (ornaments, opt-in by code point).** Pen-drawn fleurons after
Figueiredo's borders and the *rocalha* (rocaille) C- and S-scrolls of the
*rococó mineiro* (Aleijadinho's carving, Ataíde's ceilings at São Francisco
de Assis, Ouro Preto), placed at Unicode's ornament code points: `❦ ❧ ☙` and
the Ornamental Dingbats block (U+1F650–1F67F). Usable as separators in notes,
prompts, the lock screen; no effect on normal text. Box drawing stays plain:
TUIs need its corners to join.

## Phase F — Outline quality and rendering

**F1. Smooth curves.** Fit cubic Béziers to the pen outlines (today 55–120
straight segments per letter vs Radon's 13–20 curves): no facets at the
lock-screen clock or when zooming, lighter files.
**F2. Hinting.** Run Adobe's `otfautohint` (afdko) in `build.sh`: 0.2.0 has
no hints, so with the system's hintslight FreeType can't snap x-height and
baseline to the pixel grid.
*Check:* sharpness at 12 px up vs 0.2.0; outline point count down ≥ 5×.

## Phase G — A "Text" weight for light backgrounds

Thin strokes fade on light grounds; Commit Mono recommends 450 there vs 400
on dark. Add **Jandi Mono Text** (nib ×1.08) for the Jandí Light theme and
the LG at 97 PPI.
*Check:* stem weight +8%, hairline ≥ 0.6 px at 12 px.

## Phase I — Capitulares (swash capitals, opt-in)

Figueiredo gives four models of ornamented capitals, "from the most elaborate
to the simplest"; the Minas *Compromissos* copied them. Draw A–Z swash
capitals in the pen, behind the OpenType `swsh` feature (off by default):
for headings, the lock-screen date, Days. Never on in the terminal.
*Check:* `swsh` off → no change to any metric; on → capitals render and stay
inside the line height.

## Phase H — Validation and release

- **Reading-speed self-test** page (the font is OFL, so it can be embedded):
  timed passages in Jandí Mono (current release), Jandí Mono Wide, Jandí Mono
  Text and Radon. Best fonts differ per reader
  (Wallace et al. 2022) — measure the user's own fit.
- **fontbakery** QA (OFL metadata, names, vertical metrics, monospace checks).
- Reading-size guidance in the README: x-height ≥ 0.2° — on the laptop that
  means ≥ 15 pt for long reading.
- Release 1.0: README, FONTLOG, specimen, Omarchy: `omarchy font set "Jandi Mono NF"`.

---

## Order and versions

| Version | Phases | Why this order |
|---|---|---|
| 0.3.0 | A + B2 + B3 | Measure first; then the skeleton changes everything later builds on |
| 0.4.0 | C + D | Italic and spacing sit on the new skeleton |
| 0.5.0 | E (+ florões) | Punctuation and ligatures need the final dot size and spacing |
| 0.6.0 | F + G | Curves and hints last in the outline pipeline; Text weight reuses it |
| 0.7.0 | I | Capitulares after the outline pipeline is final |
| 1.0.0 | H | Validate with the user's own reading, then release |
