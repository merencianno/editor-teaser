"""Segunda câmera: mede o atraso dela em relação à voz pelo áudio (correlação cruzada) e gera o proxy.

  uv run --no-project --with numpy python scripts/sincronizar.py <projeto> <camera-b.mp4> [--offset 12.345]

Grava fontes.b em trabalho/<projeto>/projeto.json (offset: tempo na câmera B = tempo na voz + offset) e o proxy em
trabalho/<projeto>/proxy-b.mp4. As versões montadas depois disso alternam as duas câmeras. A câmera B precisa ter
algum som (o microfone da própria câmera serve); sem som, meça à mão (palma, claquete) e passe --offset.
"""
import argparse, subprocess, sys
import numpy as np
from comum import ffprobe, gravar_projeto, ler_projeto, pasta, publicar
from preparar import proxy

SR = 4000


def pcm(arq, de, dur):
    r = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", f"{max(0, de):.3f}", "-t", f"{dur:.3f}", "-i", str(arq),
                        "-vn", "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"], capture_output=True, check=True)
    x = np.frombuffer(r.stdout, np.int16).astype(np.float32)
    return (x - x.mean()) / (x.std() + 1e-9)


def atraso(a, b):
    """quanto b está atrasado em relação a a (s) e a confiança (0–1)"""
    n = 1 << int(np.ceil(np.log2(len(a) + len(b))))
    c = np.fft.irfft(np.fft.rfft(b, n) * np.conj(np.fft.rfft(a, n)), n)
    k = int(np.argmax(c)); k = k - n if k > n // 2 else k
    return k / SR, float(c.max() / (np.sqrt((a ** 2).sum() * (b ** 2).sum()) + 1e-9))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("projeto"); ap.add_argument("camera_b"); ap.add_argument("--offset", type=float)
    a = ap.parse_args()
    pj = ler_projeto(a.projeto); dir_ = pasta(a.projeto)
    bruto_a = pj["brutos"]["a"]
    ia, ib = ffprobe(bruto_a), ffprobe(a.camera_b)
    if a.offset is not None:
        off = a.offset; print(f"offset informado: {off:+.3f} s")
    else:
        if not ib["audio"]: sys.exit("a câmera B não tem som: meça o offset à mão e passe --offset")
        a0 = min(60.0, ia["duracao"] / 4); L = min(300.0, ia["duracao"] - a0)
        folga = 120.0  # as câmeras podem ter começado com até 2 min de diferença
        b0 = max(0.0, a0 - folga)
        lag, conf = atraso(pcm(bruto_a, a0, L), pcm(a.camera_b, b0, L + 2 * folga))
        off = b0 + lag - a0
        print(f"offset {off:+.3f} s (correlação {conf:.2f}; abaixo de ~0,3 desconfie e confira no olho)")
        if ia["duracao"] > 600:  # confere a deriva de relógio perto do fim
            t2 = ia["duracao"] - 120
            l2, c2 = atraso(pcm(bruto_a, t2, 60), pcm(a.camera_b, t2 + off - 5, 70))
            print(f"conferência em {t2:.0f} s: deriva {l2 - 5:+.3f} s (correlação {c2:.2f})")
    fps = pj["fps"]
    print("proxy 1080p da câmera B…"); proxy(a.camera_b, dir_ / "proxy-b.mp4", fps)
    final = ""
    if (ib["altura"] or 0) > 1080:
        print("fonte do export da câmera B…"); proxy(a.camera_b, dir_ / "final-b.mp4", fps, altura=None)
        final = publicar(a.projeto, dir_ / "final-b.mp4", "final-b.mp4")
    pj["brutos"]["b"] = str(a.camera_b)
    pj["fontes"]["b"] = {"arquivo": publicar(a.projeto, dir_ / "proxy-b.mp4", "proxy-b.mp4"), "arquivoFinal": final, "offset": round(off, 3)}
    gravar_projeto(a.projeto, pj)
    print("câmera B pronta: as próximas versões alternam as duas câmeras")


if __name__ == "__main__":
    main()
