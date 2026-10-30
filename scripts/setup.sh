#!/usr/bin/env bash
# Prepara a máquina para editar: confere as ferramentas, instala o Remotion e cria o arquivo das timelines.
#   bash scripts/setup.sh            (rápido)
#   bash scripts/setup.sh --aquecer  (também baixa os modelos: Whisper large-v3 ~3 GB e o alinhador ~1,2 GB)
set -euo pipefail
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
falta=0
for f in ffmpeg ffprobe node npm uv; do
  if command -v "$f" >/dev/null; then echo "ok  $f"; else echo "FALTA $f"; falta=1; fi
done
if [ "$falta" = 1 ]; then
  if [ "$(uname)" = Darwin ] && command -v brew >/dev/null; then
    echo "instalando pelo brew: ffmpeg uv node git"; brew install ffmpeg uv node git
  else
    echo "Instale o que falta (Mac: o instalador .pkg do Homebrew e depois brew install ffmpeg uv node git;"
    echo "Linux: pacman/apt, ou mise para node e uv)."; exit 1
  fi
fi
node -e 'const v=+process.versions.node.split(".")[0]; if (v<18) { console.error("Node >= 18"); process.exit(1) }'
if command -v nvidia-smi >/dev/null && nvidia-smi -L >/dev/null 2>&1; then
  echo "GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader | head -1) (Whisper em CUDA, proxies em NVENC)"
else
  echo "GPU NVIDIA: não (Whisper na CPU; proxies em VideoToolbox no Mac ou x264)"
fi
(cd "$RAIZ/remotion" && npm ci --no-audit --no-fund)
[ -f "$RAIZ/remotion/src/Composicoes.tsx" ] || cp "$RAIZ/remotion/src/Composicoes.vazio.tsx" "$RAIZ/remotion/src/Composicoes.tsx"
mkdir -p "$RAIZ/trabalho" "$RAIZ/remotion/public"
if [ "${1:-}" = "--aquecer" ]; then
  if [ "$(uname)" = Darwin ]; then
    uv run --no-project --with mlx-whisper python -c \
      'from huggingface_hub import snapshot_download; print(snapshot_download("mlx-community/whisper-large-v3-mlx"))'
    uv run --no-project --with torch --with torchaudio python -c \
      'import torchaudio; torchaudio.pipelines.MMS_FA.get_model(); print("alinhador ok")'
  else
    uv run --no-project --with faster-whisper python -c 'from faster_whisper import download_model; print(download_model("large-v3"))'
    uv run --no-project --index https://download.pytorch.org/whl/cpu --with torch --with torchaudio python -c \
      'import torchaudio; torchaudio.pipelines.MMS_FA.get_model(); print("alinhador ok")'
  fi
fi
echo "pronto. No Claude: vamos editar <caminho do bruto> (e mande o roteiro aprovado junto)"
