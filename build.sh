#!/usr/bin/env bash
# Constrói as famílias do Jandí Mono (normal, Wide, Text e as NF) a partir do Radon upstream.
#
# Uso: ./build.sh [python]                      tudo
#      FAMILIES="normal wide" STYLES="Regular Italic" ./build.sh python
#                                               só uma parte (a CI divide assim)
# FAMILIES: normal wide text    STYLES: Regular Bold Italic BoldItalic
# (Text só tem Regular e Italic). JOBS: processos ao mesmo tempo (padrão 4).
set -euo pipefail
cd "$(dirname "$0")"
PY="${1:-python3}"
JOBS="${JOBS:-4}"
FAMILIES="${FAMILIES:-normal wide text}"
STYLES="${STYLES:-Regular Bold Italic BoldItalic}"
NF_DIR="${NF_DIR:-/usr/share/fonts/OTF}"
mkdir -p build

# Cada tarefa roda em segundo plano e o status de cada uma é conferido: um
# merge.py que falha derruba o build (um `wait` sem argumentos sempre dá 0).
# O limite de JOBS espera sem recolher os processos, para nenhum status se
# perder. Com tudo em paralelo, a máquina local chegou a ficar sem memória.
pids=()
throttle() { while (( $(jobs -rp | wc -l) >= JOBS )); do sleep 0.2; done; }
run() { throttle; "$@" & pids+=("$!"); }
collect() {
  local failed=0
  for p in "${pids[@]}"; do wait "$p" || failed=1; done
  pids=()
  (( failed == 0 )) || { echo "build: uma tarefa falhou" >&2; exit 1; }
}

style_name() { case "$1" in BoldItalic) echo "Bold Italic" ;; *) echo "$1" ;; esac; }
built=()
for fam in $FAMILIES; do
  case "$fam" in
    normal) prefix=JandiMono;     flag=() ;;
    wide)   prefix=JandiMonoWide; flag=(--wide) ;;   # célula 1320, o build de acessibilidade
    text)   prefix=JandiMonoText; flag=(--text) ;;   # pena 8% mais larga: fundos claros, 97 PPI
    *) echo "família desconhecida: $fam" >&2; exit 2 ;;
  esac
  for file in $STYLES; do
    [[ $fam == text && $file != Regular && $file != Italic ]] && continue
    run "$PY" tools/merge.py "sources/upstream/MonaspaceRadon-$file.otf" "build/$prefix-$file.otf" \
        --style "$(style_name "$file")" "${flag[@]}"
    built+=("build/$prefix-$file.otf")
  done
done
collect

# Hinting (roadmap F2): Adobe's autohinter over the pen outlines, so FreeType's
# hintslight can snap baseline, x-height and stems to the pixel grid. Before
# the NF step, so the letters arrive hinted; the icons stay as Nerd Fonts made them.
AUTOHINT="$(dirname "$PY")/otfautohint"
command -v "$AUTOHINT" >/dev/null || AUTOHINT=otfautohint
if command -v "$AUTOHINT" >/dev/null; then
  for f in "${built[@]}"; do
    # i l j q 1 (e t f nas itálicas) ficam sem hinting (ver tools/nohint.py).
    # -p 2: o otfautohint abre um processo por núcleo; com vários arquivos ao
    # mesmo tempo isso chegou a 30 processos e esgotou a memória.
    run "$AUTOHINT" -p 2 -x "$("$PY" tools/nohint.py "$f")" "$f"
  done
  collect
else
  echo "sem otfautohint (pip install afdko): fontes sem hinting" >&2
fi

# Variante NF: os ícones do Nerd Fonts (barra, starship, nvim) dentro da fonte.
# Vêm do MonaspiceRn Nerd Font do mesmo estilo, já escalado para esta célula.
for f in "${built[@]}"; do
  file="${f##*-}"; file="${file%.otf}"
  src="$NF_DIR/MonaspiceRnNerdFontMono-$file.otf"
  [[ -f $src ]] || { echo "sem $src: pulando a NF de $f" >&2; continue; }
  base="$(basename "$f" .otf)"
  run "$PY" tools/nerd.py "$f" "$src" "build/${base%-*}NF-$file.otf"
done
collect
ls -la build/JandiMono*.otf
