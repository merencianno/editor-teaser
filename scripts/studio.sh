#!/usr/bin/env bash
# Abre o Remotion Studio (painel Props à direita). Porta: PORTA=3123 por padrão.
set -euo pipefail
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
[ -f "$RAIZ/remotion/src/Composicoes.tsx" ] || cp "$RAIZ/remotion/src/Composicoes.vazio.tsx" "$RAIZ/remotion/src/Composicoes.tsx"
export PORTA="${PORTA:-3123}"
echo "Studio em http://localhost:$PORTA"
cd "$RAIZ/remotion" && exec npm run studio
