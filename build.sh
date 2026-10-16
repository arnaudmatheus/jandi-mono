#!/usr/bin/env bash
# Constrói as quatro variantes do Jandí Mono a partir do Radon upstream.
# Uso: ./build.sh [python]   (python com fonttools + shapely)
set -euo pipefail
cd "$(dirname "$0")"
PY="${1:-python3}"
mkdir -p build
for style in Regular Bold Italic "Bold Italic"; do
  file="${style// /}"
  "$PY" tools/merge.py "sources/upstream/MonaspaceRadon-$file.otf" "build/JandiMono-$file.otf" --style "$style" &
done
wait
# Variante NF: os ícones do Nerd Fonts (barra, starship, nvim) dentro da fonte.
# Vêm do MonaspiceRn Nerd Font do mesmo estilo, já escalado para esta célula.
NF_DIR="${NF_DIR:-/usr/share/fonts/OTF}"
for file in Regular Bold Italic BoldItalic; do
  src="$NF_DIR/MonaspiceRnNerdFontMono-$file.otf"
  [[ -f $src ]] || { echo "sem $src: pulando NF-$file" >&2; continue; }
  "$PY" tools/nerd.py "build/JandiMono-$file.otf" "$src" "build/JandiMonoNF-$file.otf" &
done
wait
ls -la build/JandiMono*.otf
