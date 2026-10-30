#!/usr/bin/env bash
# Preview 480p das duas composições de uma versão (dos proxies), para o dono aprovar ANTES do export.
#   bash scripts/preview.sh <projeto> <vN> [16x9|9x16|ambos]
# Sai em trabalho/<projeto>/vN/preview-16x9-480p.mp4 e preview-9x16-480p.mp4.
set -euo pipefail
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"; cd "$RAIZ"
proj="$1"; v="${2#v}"; v="${v#V}"; quais="${3:-ambos}"
dir="$RAIZ/trabalho/$proj/v$v"; [ -d "$dir" ] || { echo "versão não existe: $dir"; exit 1; }
mkdir -p "$RAIZ/trabalho/tmp"; export TMPDIR="$RAIZ/trabalho/tmp"   # /tmp pequeno derruba o render
CONC="${CONCORRENCIA:-$(( $(getconf _NPROCESSORS_ONLN) / 2 ))}"
for fmt in 16x9 9x16; do
  [ "$quais" = ambos ] || [ "$quais" = "$fmt" ] || continue
  id="Teaser$fmt-$proj-v$v"
  [ "$fmt" = 16x9 ] && tam=854:480 || tam=480:854
  t0=$(date +%s)
  (cd remotion && npx remotion render src/index.ts "$id" "$dir/.preview-$fmt-540.mp4" --scale=0.5 --crf=20 \
     --concurrency="$CONC" --log=error)
  ffmpeg -nostdin -v error -y -i "$dir/.preview-$fmt-540.mp4" -vf "scale=$tam:flags=lanczos,setsar=1" \
    -c:v libx264 -preset fast -crf 21 -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart "$dir/preview-$fmt-480p.mp4"
  rm -f "$dir/.preview-$fmt-540.mp4"
  echo "preview $fmt: $dir/preview-$fmt-480p.mp4 ($(( $(date +%s) - t0 )) s)"
  python3 scripts/conferir-quadros.py "$dir/preview-$fmt-480p.mp4" || echo "AVISO: quadros repetidos; rode de novo com CONCORRENCIA=3"
done
# abre os previews no player do sistema (ABRIR=0 desliga)
if [ "${ABRIR:-1}" = 1 ]; then for f in "$dir"/preview-*-480p.mp4; do bash scripts/abrir.sh "$f"; done; fi
echo "Mostre ao dono e espere o ok. Só depois: bash scripts/export.sh $proj v$v"
