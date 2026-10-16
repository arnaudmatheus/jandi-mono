# Jandí Mono

A monospaced font for terminals and desktops: **Monaspace Radon's cursive,
rewritten with a Renaissance pen.** Made for the
[Jandí theme for Omarchy](https://github.com/arnaudmatheus/omarchy-jandi-theme).

![Jandí Mono specimen](docs/specimen.png)

## What it is

Radon is Monaspace's handwriting face: warm, slanted, drawn with an even
marker-like stroke. Jandí Mono keeps Radon's grid, metrics, symbols, box
drawing, braille and OpenType features, and redraws its letters the way a
chancery scribe would: every letter is a centreline swept by **one rectangular
nib held at one fixed angle (35°)**. Thick and thin are never drawn by hand;
they fall out of the pen angle, the same for every letter. The hand lifts
between letters (no joins), which is exactly what a monospace grid needs.

- **Subtle contrast** (≈1.6 : 1), so hairlines survive 9 pt on a 96 PPI screen.
- **Chancery `f`** with a descender, and a **`g` whose looped descender closes
  in one sweep**, inspired by Michelangelo's signature.
- **No confusables:** flagged and footed `1`, curved `l`, serifed `I`,
  slashed `0` narrower than `O`.
- **Writes Tupi and Guarani correctly.** Radon has no mark positioning, so
  `g` + U+0303 leaves the tilde floating beside the `g`. Jandí Mono adds GPOS
  mark attachment: `g̃ G̃ ỹ ĩ ũ ẽ` sit right, and so do Vietnamese stacks and
  the Czech/Slovak apostrophe carons (`ď ľ ť Ľ`).
- **Radon's texture healing still works:** its widened and shifted letter
  variants are regenerated from the same skeletons.
- Regular, Bold, Italic, Bold Italic. The Italic leans 13° against the
  Regular's 7°, so italic comments read apart from code.

## Families

| Family | Use |
|---|---|
| `Jandi Mono` | Text only |
| `Jandi Mono NF` | Plus 10,828 Nerd Fonts icons for bars, prompts and editors |

## Install

```sh
git clone https://github.com/arnaudmatheus/jandi-mono
mkdir -p ~/.local/share/fonts/JandiMono
cp jandi-mono/fonts/otf/*.otf ~/.local/share/fonts/JandiMono/
fc-cache -f
```

On Omarchy, make it the system font (terminals, bar, menus):

```sh
omarchy font set "Jandi Mono NF"
```

## Build

```sh
pip install -r requirements.txt
./build.sh            # or: ./build.sh /path/to/python
```

`tools/pen.py` holds the pen engine and the lowercase skeletons,
`tools/caps.py` the capitals, figures and extra letters, `tools/marks.py` the
diacritics. `tools/merge.py` writes them into the upstream Radon fonts in
`sources/upstream/`; `tools/nerd.py` adds the icons from an installed
MonaspiceRn Nerd Font (set `NF_DIR` if it isn't in `/usr/share/fonts/OTF`).
`SPEC.md` records the design decisions.

## Credits

- **Monaspace Radon**, the base: Riley Cran and the Lettermatic team, for
  [GitHub Next](https://github.com/githubnext/monaspace). SIL OFL 1.1.
  Jandí Mono is a derivative and does not use Monaspace's Reserved Font Names.
- **Nerd Fonts** icons in the NF builds: Ryan L McIntyre and
  [contributors](https://github.com/ryanoasis/nerd-fonts). Each icon set keeps
  its own licence; see the Nerd Fonts repository.
- **The Jandí palette and name**: [jandi-colors](https://github.com/franciscotbjr/jandi-colors)
  by Francisco Tarcizo Bomfim Júnior (MIT), from the blue pigment of the
  jenipapo fruit, the ancestral paint of Brazil's indigenous peoples.
- **Michelangelus** (Microsoft with Studiogusto, for the Fabbrica di San
  Pietro): inspiration only, from its makers' published design principles.
  No outlines, measurements or data from it are used; its licence forbids it.
  Jandí Mono is not affiliated with or endorsed by any of the above.

## Licence

SIL Open Font License 1.1, see [OFL.txt](OFL.txt). Changes are logged in
[FONTLOG.txt](FONTLOG.txt).
