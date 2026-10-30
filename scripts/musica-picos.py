"""Candidatos a "hit" numa trilha: os pontos em que a energia sobe de repente (entrada de percussão, acorde cheio,
drop) e os vales (stopdown). Serve para escolher `musica.hitNaFaixa` no roteiro; confirme sempre ouvindo.

  uv run --no-project --with numpy python scripts/musica-picos.py trilha.mp3 [--n 8]
"""
import argparse, subprocess
import numpy as np

SR, PASSO = 11025, 0.05


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("trilha"); ap.add_argument("--n", type=int, default=8)
    a = ap.parse_args()
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", a.trilha, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32)
    h = int(SR * PASSO)
    rms = np.sqrt(np.add.reduceat(x[: len(x) // h * h] ** 2, np.arange(0, len(x) // h * h, h)) / h)
    db = 20 * np.log10(rms + 1e-6)
    curto = np.convolve(db, np.ones(4) / 4, "same")         # 0,2 s
    longo = np.convolve(db, np.ones(40) / 40, "full")[: len(db)]  # 2 s antes
    sobe = curto - longo
    print(f"duração {len(x) / SR:.1f} s · nível médio {db.mean():.1f} dB")
    def melhores(v, n):
        idx, out = np.argsort(v)[::-1], []
        for i in idx:
            if all(abs(i - j) * PASSO > 2 for j in out): out.append(i)
            if len(out) == n: break
        return sorted(out)
    print("subidas (hit / entrada):")
    for i in melhores(sobe, a.n): print(f"  {i * PASSO:7.2f} s  +{sobe[i]:.1f} dB")
    print("quedas (stopdown / respiro):")
    for i in melhores(-sobe, max(3, a.n // 2)): print(f"  {i * PASSO:7.2f} s  {sobe[i]:.1f} dB")


if __name__ == "__main__":
    main()
