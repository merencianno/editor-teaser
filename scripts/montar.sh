#!/usr/bin/env bash
# Roteiro aprovado → versão nova pronta para o Studio: timeline, legenda palavra a palavra, rosto e luz por plano.
#   bash scripts/montar.sh <projeto> <roteiro.json> [--versao N]
set -euo pipefail
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"; cd "$RAIZ"
proj="$1"; rot="$2"; shift 2
saida=$(python3 scripts/montar-timeline.py "$proj" "$rot" "$@" | tee /dev/stderr)
v=$(printf '%s\n' "$saida" | sed -n 's/^v\([0-9]*\): .*/\1/p' | tail -1)
[ -n "$v" ] || { echo "não achei a versão criada"; exit 1; }
python3 scripts/legendas.py "$proj" "v$v"
uv run --no-project --with "opencv-python-headless<4.11" --with "numpy<2.3" python scripts/rostos.py "$proj" "v$v"
echo "v$v montada. Abra o Studio (bash scripts/studio.sh) e procure Teaser16x9-*-v$v e Teaser9x16-*-v$v."
