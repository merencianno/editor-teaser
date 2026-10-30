"""Transcrição por palavra da voz do projeto (faster-whisper large-v3). Base para o roteiro: o Claude lê a
transcrição, acha as falas e propõe os roteiros. O tempo de palavra do Whisper é aproximado (±0,2 s): serve para
achar e cortar trechos; a legenda usa alinhamento forçado (skill legenda-vertical).

  uv run --no-project --with faster-whisper --with nvidia-cublas-cu12 --with "nvidia-cudnn-cu12==9.*" \
    python scripts/transcrever.py <projeto> [--idioma pt] [--cpu] [--modelo large-v3]

GPU NVIDIA: CUDA com int8_float16 (≈ 1 min para 20 min de fala numa placa de 8 GB). Sem GPU (ou com --cpu): int8 na
CPU, bem mais lento (veja "Adaptações para Mac" no README).
Grava trabalho/<projeto>/palavras.json e transcricao.md.
"""
import argparse, glob, json, os, subprocess, sys

# as bibliotecas CUDA vêm dos pacotes nvidia-* do próprio ambiente do uv; o carregador só as acha se estiverem no
# LD_LIBRARY_PATH antes do processo começar, então o script se reinicia uma vez com ele ajustado
_libs = [d for p in sys.path for d in glob.glob(os.path.join(p, "nvidia", "*", "lib"))]
if _libs and os.environ.get("_EDITOR_TEASER_LD") != "1" and sys.platform.startswith("linux"):
    os.environ["LD_LIBRARY_PATH"] = ":".join(_libs + [os.environ.get("LD_LIBRARY_PATH", "")])
    os.environ["_EDITOR_TEASER_LD"] = "1"
    os.execv(sys.executable, [sys.executable] + sys.argv)

import numpy as np
from comum import mmss, pasta, ler_projeto, RAIZ

SR = 16000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("projeto"); ap.add_argument("--idioma", default="pt"); ap.add_argument("--cpu", action="store_true")
    ap.add_argument("--modelo", default="large-v3")
    a = ap.parse_args()
    dados = ler_projeto(a.projeto)
    voz = RAIZ / "remotion/public" / dados["fontes"]["voz"]
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(voz), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    audio = np.frombuffer(pcm, np.float32).copy()

    from faster_whisper import WhisperModel
    modelo = None
    if not a.cpu:
        try:
            modelo = WhisperModel(a.modelo, device="cuda", compute_type="int8_float16"); print("whisper: CUDA int8_float16")
        except Exception as e:
            print(f"CUDA indisponível ({str(e).splitlines()[0][:120]}); indo de CPU", file=sys.stderr)
    if modelo is None:
        modelo = WhisperModel(a.modelo, device="cpu", compute_type="int8"); print("whisper: CPU int8")

    segs, _ = modelo.transcribe(audio, language=a.idioma, word_timestamps=True, vad_filter=False, beam_size=2)
    out, linhas = [], []
    for s in segs:
        ws = [{"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2)} for w in (s.words or []) if w.word.strip()]
        out.append({"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip(), "words": ws})
        linhas.append(f"[{mmss(s.start)}–{mmss(s.end)}] {s.text.strip()}")
        print(linhas[-1], flush=True)
    d = pasta(a.projeto)
    (d / "palavras.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    (d / "transcricao.md").write_text("# Transcrição (Whisper, conferir no áudio toda fala citada)\n\n" + "\n".join(linhas) + "\n")
    print(f"{sum(len(x['words']) for x in out)} palavras → {d / 'palavras.json'}")


if __name__ == "__main__":
    main()
