#!/usr/bin/env bash
# Abre o Remotion Studio (painel Props à direita). Porta: PORTA=3123 por padrão.
set -euo pipefail
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
[ -f "$RAIZ/remotion/src/Composicoes.tsx" ] || cp "$RAIZ/remotion/src/Composicoes.vazio.tsx" "$RAIZ/remotion/src/Composicoes.tsx"
export PORTA="${PORTA:-3123}"
echo "Studio em http://localhost:$PORTA"
# abre o navegador sozinho assim que o servidor responder (ABRIR=0 desliga)
if [ "${ABRIR:-1}" = 1 ]; then
  ( for _ in $(seq 1 60); do curl -s -o /dev/null "http://localhost:$PORTA" && { bash "$RAIZ/scripts/abrir.sh" "http://localhost:$PORTA"; break; }; sleep 1; done ) &
fi
cd "$RAIZ/remotion" && exec npm run studio
