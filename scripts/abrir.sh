#!/usr/bin/env bash
# Abre um arquivo, pasta ou URL no app padrão (Mac: open; Linux: xdg-open). O usuário não usa terminal: o Claude
# abre o Studio, os previews e o mapa do roteiro por aqui.
#   bash scripts/abrir.sh <arquivo|pasta|url>
set -euo pipefail
if command -v open >/dev/null && [ "$(uname)" = Darwin ]; then open "$1"
elif command -v xdg-open >/dev/null; then xdg-open "$1" >/dev/null 2>&1 &
else echo "abra à mão: $1"; fi
