#!/usr/bin/env bash
# docs/specimen.png, rendered from the fonts in build/ (run ./build.sh first).
# Needs pango-view and ImageMagick. Each font sits in an isolated fontconfig,
# so a system rule that remaps monospace can't swap the face being shown.
# The plate line is Figueiredo's Nova Escola (1722), plate nº 7, from the
# Biblioteca Nacional de Portugal's public-domain scan (purl.pt/107).
set -euo pipefail
J="$(cd "$(dirname "$0")/.." && pwd)"; D="$(mktemp -d)"; trap 'rm -rf "$D"' EXIT
mkdir -p $D/f $D/p
cp $J/build/JandiMono-*.otf $J/build/JandiMonoNF-Regular.otf $J/build/JandiMonoWide-Regular.otf $J/build/JandiMonoText-Regular.otf $D/f/
cat > $D/fc.conf <<X
<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig><dir>$D/f</dir><cachedir>$D/cache</cachedir></fontconfig>
X
export FONTCONFIG_FILE=$D/fc.conf; fc-cache -f >/dev/null 2>&1
BG='#11203A'; FG='#C8D5CC'; URU='#D9773A'; GOLD='#E3B65A'; MUTED='#7F96A6'; W=1600
r() { # r name markup [margin-left]
  printf '%s' "$2" > $D/p/$1.txt
  pango-view -q --markup --background="$BG" --foreground="$FG" --margin=0 --dpi=96 --output=$D/p/$1.raw.png $D/p/$1.txt
  magick $D/p/$1.raw.png -background "$BG" -gravity west -extent ${W}x -bordercolor "$BG" -border 0x0 $D/p/$1.png
}
pad() { magick -size ${W}x$1 xc:"$BG" $D/p/pad$1.png; echo $D/p/pad$1.png; }
r title '<span font="Jandi Mono 92px">Jandí Mono</span>'
r sub "<span font=\"Jandi Mono Italic 34px\" foreground=\"$URU\">written with the pen of the Luso-Brazilian Baroque</span>"
# The plate, tinted into the palette: parchment -> night blue, ink -> light.
magick $J/docs/figueiredo-plate7-line1.jpg -colorspace gray -level 35%,92% -negate +level-colors "$BG","#DCE6DE" -resize 1360x $D/p/plate.raw.png
magick $D/p/plate.raw.png -background "$BG" -gravity west -extent ${W}x $D/p/plate.png
r platecap "<span font=\"Jandi Mono 19px\" foreground=\"$MUTED\">Manuel de Andrade de Figueiredo, Nova Escola, plate nº 7 (Lisbon, 1722) · Biblioteca Nacional de Portugal, purl.pt/107, public domain</span>"
r corsiva "<span font=\"Jandi Mono Italic 82px\" foreground=\"$URU\">abcdefghilmnopqrstuxz</span>"
r corsivacap "<span font=\"Jandi Mono 19px\" foreground=\"$MUTED\">the same letters in Jandí Mono Italic, the corsiva</span>"
r quote "<span font=\"Jandi Mono Italic 25px\" foreground=\"$GOLD\">“a letra deveria ser um corpo com proporção, igual nas alturas e nas distâncias”</span>
<span font=\"Jandi Mono 19px\" foreground=\"$MUTED\">  a letter should be a body in proportion, equal in its heights and distances. Figueiredo, 1722</span>"
r code "<span font=\"Jandi Mono 27px\"><span foreground=\"$MUTED\">Regular      </span>fn carregar(rota: &amp;Path) -&gt; Result&lt;Config, Erro&gt; {
<span foreground=\"$MUTED\">Italic       </span><span font=\"Jandi Mono Italic 27px\" foreground=\"$URU\">// a letra é um corpo com proporção</span>
<span foreground=\"$MUTED\">Bold         </span><span font=\"Jandi Mono Bold 27px\">if a != b &amp;&amp; c &gt;= 1 { x[0] =&gt; y; }</span>
<span foreground=\"$MUTED\">Bold Italic  </span><span font=\"Jandi Mono Bold Italic 27px\" foreground=\"$GOLD\">ABCDEFGHIJKLM nopqrstuvwxyz 0123456789</span></span>"
r feat "<span font=\"Jandi Mono 46px\">bdhk  cfjry  FHKMNPRT  {([])}  -&gt; =&gt; != :: |&gt;</span>"
r featcap "<span font=\"Jandi Mono 19px\" foreground=\"$MUTED\">hooked ascenders · drops (gota) · lapidary feet · the carved C-scroll · ligatures, on by default</span>"
r orn "<span font=\"Jandi Mono 46px\" foreground=\"$GOLD\">❦ ❨ 1722 ❩ 🙘 ❰ SANCTUS ❱ ☙  </span><span font=\"Jandi Mono 46px\" font_features=\"titl\">OURO</span><span font=\"Jandi Mono 46px\">  </span><span font=\"Jandi Mono 46px\" font_features=\"swsh\" foreground=\"$URU\">P</span><span font=\"Jandi Mono 46px\" foreground=\"$URU\">reto</span>"
r orncap "<span font=\"Jandi Mono 19px\" foreground=\"$MUTED\">opt-in ornament: florões, cartelas, ribbon ends; carved capitals (titl) and Figueiredo's flourish (swsh)</span>"
r lang "<span font=\"Jandi Mono 30px\">fogão · ñe'ẽ · g̃ ỹ ĩ · tiếng việt · lǘsè · ďábel · Ąę</span>"
r fam "<span font=\"Jandi Mono 26px\">Jandi Mono</span><span font=\"Jandi Mono 26px\" foreground=\"$MUTED\">   ·   </span><span font=\"Jandi Mono Wide 26px\">Jandi Mono Wide</span><span font=\"Jandi Mono 26px\" foreground=\"$MUTED\">   ·   </span><span font=\"Jandi Mono Text 26px\">Jandi Mono Text</span>"
ICONS=$(printf '\uf1eb  \uf240  \uf293  \uf120  \uf303  \uf07b  \uf418  \ue7c5  \ue0b0\ue0b2  ▁▂▃▄▅▆▇█  ⣿⣶⣤⣀  ┌─┬─┐')
r icons "<span font=\"Jandi Mono NF 30px\" foreground=\"$URU\">$ICONS</span>"
magick $(pad 70) $D/p/title.png $(pad 14) $D/p/sub.png $(pad 56) $D/p/plate.png $(pad 8) $D/p/platecap.png $(pad 18) $D/p/corsiva.png $(pad 6) $D/p/corsivacap.png \
  $(pad 40) $D/p/quote.png $(pad 48) $D/p/code.png $(pad 44) $D/p/feat.png $(pad 8) $D/p/featcap.png $(pad 40) $D/p/orn.png $(pad 8) $D/p/orncap.png $(pad 36) $D/p/lang.png \
  $(pad 28) $D/p/fam.png $(pad 26) $D/p/icons.png $(pad 70) -append $D/p/all.png
magick $D/p/all.png -bordercolor "$BG" -border 1 -fuzz 2% -trim +repage -bordercolor "$BG" -border 64x64 $J/docs/specimen.png
magick identify $J/docs/specimen.png
