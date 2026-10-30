#!/usr/bin/env bash
# Transcreve com o motor certo para a máquina: GPU NVIDIA (CUDA), Mac Apple Silicon (mlx-whisper) ou CPU.
#   bash scripts/transcrever.sh <projeto> [opções do transcrever.py]
set -euo pipefail
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"; cd "$RAIZ"
if command -v nvidia-smi >/dev/null && nvidia-smi -L >/dev/null 2>&1; then
  exec uv run --no-project --with faster-whisper --with nvidia-cublas-cu12 --with "nvidia-cudnn-cu12==9.*" \
    python scripts/transcrever.py "$@"
elif [ "$(uname)" = Darwin ] && [ "$(uname -m)" = arm64 ]; then
  exec uv run --no-project --with mlx-whisper python scripts/transcrever.py "$@" --motor mlx    # não testado
else
  exec uv run --no-project --with faster-whisper python scripts/transcrever.py "$@" --cpu
fi
