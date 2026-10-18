#!/usr/bin/env bash
# Constrói as famílias do Jandí Mono (normal, Wide, Text e as NF) a partir do Radon upstream.
# Uso: ./build.sh [python]   (python com fonttools + shapely)
set -euo pipefail
cd "$(dirname "$0")"
PY="${1:-python3}"
mkdir -p build
# No máximo JOBS processos ao mesmo tempo: cada merge.py segura a fonte inteira
# e a geometria em memória; com tudo em paralelo o sistema ficou sem memória.
JOBS="${JOBS:-4}"
throttle() { while (( $(jobs -rp | wc -l) >= JOBS )); do wait -n; done; }
# Jandi Mono (célula 1160) e Jandi Mono Wide (1320, o build de acessibilidade).
for style in Regular Bold Italic "Bold Italic"; do
  file="${style// /}"
  throttle; "$PY" tools/merge.py "sources/upstream/MonaspaceRadon-$file.otf" "build/JandiMono-$file.otf" --style "$style" &
  throttle; "$PY" tools/merge.py "sources/upstream/MonaspaceRadon-$file.otf" "build/JandiMonoWide-$file.otf" --style "$style" --wide &
done
# Jandi Mono Text: Regular e Italic, pena 8% mais larga (fundos claros, 97 PPI).
for style in Regular Italic; do
  throttle; "$PY" tools/merge.py "sources/upstream/MonaspaceRadon-$style.otf" "build/JandiMonoText-$style.otf" --style "$style" --text &
done
wait
# Hinting (roadmap F2): Adobe's autohinter over the pen outlines, so FreeType's
# hintslight can snap baseline, x-height and stems to the pixel grid. Before
# the NF step, so the letters arrive hinted; the icons stay as Nerd Fonts made them.
AUTOHINT="$(dirname "$PY")/otfautohint"
command -v "$AUTOHINT" >/dev/null || AUTOHINT=otfautohint
if command -v "$AUTOHINT" >/dev/null; then
  # i l j q 1 e famílias ficam sem hinting: hintados, os pares estreitos
  # ficavam mais parecidos (ver tools/nohint.py).
  for f in build/JandiMono-*.otf build/JandiMonoWide-*.otf build/JandiMonoText-*.otf; do
    # -p 2: o otfautohint abre um processo por núcleo; com dois arquivos ao
    # mesmo tempo isso chegou a 30 processos e esgotou a memória.
    throttle; "$AUTOHINT" -p 2 -x "$("$PY" tools/nohint.py "$f")" "$f" &
  done
  wait
else
  echo "sem otfautohint (pip install afdko): fontes sem hinting" >&2
fi
# Variante NF: os ícones do Nerd Fonts (barra, starship, nvim) dentro da fonte.
# Vêm do MonaspiceRn Nerd Font do mesmo estilo, já escalado para esta célula.
NF_DIR="${NF_DIR:-/usr/share/fonts/OTF}"
for file in Regular Bold Italic BoldItalic; do
  src="$NF_DIR/MonaspiceRnNerdFontMono-$file.otf"
  [[ -f $src ]] || { echo "sem $src: pulando NF-$file" >&2; continue; }
  throttle; "$PY" tools/nerd.py "build/JandiMono-$file.otf" "$src" "build/JandiMonoNF-$file.otf" &
  throttle; "$PY" tools/nerd.py "build/JandiMonoWide-$file.otf" "$src" "build/JandiMonoWideNF-$file.otf" &
  if [[ -f build/JandiMonoText-$file.otf ]]; then
    throttle; "$PY" tools/nerd.py "build/JandiMonoText-$file.otf" "$src" "build/JandiMonoTextNF-$file.otf" &
  fi
done
wait
ls -la build/JandiMono*.otf
