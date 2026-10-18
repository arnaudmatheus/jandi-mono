#!/usr/bin/env bash
# docs/hero.png: the README's opening image, rendered from the fonts in
# build/ (run ./build.sh first). Needs pango-view and ImageMagick.
#
# Left: the name, the line it stands for, the families. Right: the font at
# work, a terminal in the Jandí theme with code whose comments are in the
# corsiva. Below: Figueiredo's plate nº 7 (1722, public domain, Biblioteca
# Nacional de Portugal, purl.pt/107) beside the same letters in the Italic.
set -euo pipefail
J="$(cd "$(dirname "$0")/.." && pwd)"; D="$(mktemp -d)"; trap 'rm -rf "$D"' EXIT
mkdir -p "$D/f"
cp "$J"/build/JandiMono-*.otf "$J"/build/JandiMonoNF-Regular.otf "$D/f/"
cat > "$D/fc.conf" <<X
<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig><dir>$D/f</dir><cachedir>$D/cache</cachedir></fontconfig>
X
export FONTCONFIG_FILE="$D/fc.conf"; fc-cache -f >/dev/null 2>&1

# The Jandí theme (~/.config/omarchy/themes/jandi/colors.toml).
BG='#11203A'; TERM_BG='#0A1424'; EDGE='#1E3452'; FG='#C8D5CC'; MUTED='#8FA7B3'; DIM='#5D7F96'
URU='#D9773A'; GOLD='#D4B26A'; LEAF='#7FA67E'; BLUE='#7097C2'
W=2400; H=1150

# t name markup: render markup to a transparent PNG
NL=$'\n'
t() { printf '%s' "$2" > "$D/$1.txt"; pango-view -q --markup --background=transparent --margin=0 --dpi=96 --output="$D/$1.png" "$D/$1.txt"; }

t eyebrow "<span font=\"Jandi Mono 22px\" foreground=\"$DIM\" letter_spacing=\"3000\">MONOSPACE · OFL 1.1 · 2026</span>"
t title "<span font=\"Jandi Mono 150px\" foreground=\"$FG\">Jandí Mono</span>"
t sub "<span font=\"Jandi Mono Italic 44px\" foreground=\"$URU\">written with the pen of${NL}the Luso-Brazilian Baroque</span>"
t fleuron "<span font=\"Jandi Mono 96px\" foreground=\"$GOLD\">❦</span>"
t families "<span font=\"Jandi Mono 28px\" foreground=\"$MUTED\">Regular · Italic · Bold · Bold Italic${NL}Wide · Text · Nerd Font icons</span>"

k() { printf '<span foreground="%s">%s</span>' "$URU" "$1"; }       # keyword
ty() { printf '<span foreground="%s">%s</span>' "$BLUE" "$1"; }     # type
s() { printf '<span foreground="%s">%s</span>' "$LEAF" "$1"; }      # string
c() { printf '<span font="Jandi Mono Italic 37px" foreground="%s">%s</span>' "$MUTED" "$1"; }  # comment, in the corsiva
CODE="<span font=\"Jandi Mono 37px\" foreground=\"$FG\">$(c '// a letra é um corpo com proporção')
$(k fn) ler(rota: &amp;$(ty Path)) -&gt; $(ty Result)&lt;$(ty Texto), $(ty Erro)&gt; {
    $(k let) texto = fs::read_to_string(rota)?;
    $(k if) texto != $(s '""') &amp;&amp; texto.len() &gt;= 1 {
        $(k return) $(ty Ok)($(ty Texto)::novo(texto));  $(c '// pronto')
    }
    $(ty Err)($(ty Erro)::Vazio)  $(c '// nada a ler')
}</span>"
t code "$CODE"
t tab "<span font=\"Jandi Mono NF 24px\" foreground=\"$DIM\">  ~/projetos/ler   ·   nvim ler.rs</span>"

# The plate line, tinted into the palette, and the same letters in the Italic.
magick "$J/docs/figueiredo-plate7-line1.jpg" -colorspace gray -level 35%,92% -negate \
  +level-colors "$BG","#DCE6DE" -resize x150 "$D/plate.png"
t arrow "<span font=\"Jandi Mono 56px\" foreground=\"$GOLD\">→</span>"
t corsiva "<span font=\"Jandi Mono Italic 74px\" foreground=\"$URU\">abcdefghilmnop</span>"
t credit "<span font=\"Jandi Mono 20px\" foreground=\"$DIM\">Manuel de Andrade de Figueiredo, Nova Escola, plate nº 7, Lisbon 1722  →  Jandí Mono Italic</span>"

# Terminal window: a rounded panel with a thin edge and a tab rule.
TX=1040; TY=150; TW=1250; TH=$(( $(magick identify -format %h "$D/code.png") + 200 ))
magick -size ${W}x${H} xc:"$BG" \
  -fill "$TERM_BG" -stroke "$EDGE" -strokewidth 2 -draw "roundrectangle $TX,$TY $((TX+TW)),$((TY+TH)) 18,18" \
  -stroke "$EDGE" -strokewidth 2 -draw "line $((TX+2)),$((TY+64)) $((TX+TW-2)),$((TY+64))" \
  -stroke "$EDGE" -strokewidth 2 -draw "line 110,850 $((W-110)),850" \
  "$D/canvas.png"
magick "$D/canvas.png" \
  "$D/eyebrow.png" -geometry +116+150 -composite \
  "$D/title.png" -geometry +104+200 -composite \
  "$D/sub.png" -geometry +112+430 -composite \
  "$D/fleuron.png" -geometry +108+580 -composite \
  "$D/families.png" -geometry +112+716 -composite \
  "$D/tab.png" -geometry +$((TX+28))+$((TY+18)) -composite \
  "$D/code.png" -geometry +$((TX+44))+$((TY+110)) -composite \
  "$D/plate.png" -geometry +110+890 -composite \
  "$D/arrow.png" -geometry +$((110 + $(magick identify -format %w "$D/plate.png") + 40))+930 -composite \
  "$D/corsiva.png" -geometry +$((110 + $(magick identify -format %w "$D/plate.png") + 130))+910 -composite \
  "$D/credit.png" -geometry +112+1066 -composite \
  "$J/docs/hero.png"
magick identify "$J/docs/hero.png"
