"""Quadros repetidos num render: com a máquina carregada o Remotion às vezes não extrai o quadro a tempo e repete o
anterior e depois pula (a imagem "engasga"). Conta, por segundo, quadros idênticos ao anterior (YDIF < 0,003; fala
parada de verdade fica em 0,02–0,3 mesmo num preview 480p) presos no meio de movimento. Sai com código 1 se algum
segundo tiver mais de 3.

  python3 scripts/conferir-quadros.py video.mp4
"""
import collections, re, subprocess, sys

arq = sys.argv[1]
r = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", arq, "-vf",
                    "signalstats,metadata=print:key=lavfi.signalstats.YDIF:file=-", "-an", "-f", "null", "-"],
                   capture_output=True, text=True)
t, por_seg = None, collections.defaultdict(list)
for linha in r.stdout.splitlines():
    if m := re.search(r"pts_time:([\d.]+)", linha): t = float(m.group(1))
    elif (m := re.search(r"YDIF=([-+\d.eE]+)", linha)) and t is not None: por_seg[int(t)].append(float(m.group(1)))
# engasgo = 1 a 3 quadros quase idênticos ao anterior no meio de movimento: YDIF abaixo de 15 % da média da vizinhança
# (±15 quadros) e abaixo de 0,012 (o encoder deixa ruído num quadro repetido). Parada longa (cartela, preto, fim de
# fade) não conta: lá a imagem está parada de fato.
seq = [(s, d) for s, ds in sorted(por_seg.items()) for d in ds]
ds_ = [d for _, d in seq]
media = [sum(ds_[max(0, i - 15):i + 16]) / len(ds_[max(0, i - 15):i + 16]) for i in range(len(ds_))]
preso = [m > 0.02 and d < min(0.012, max(0.003, 0.15 * m)) for d, m in zip(ds_, media)]
presos = collections.Counter()
i = 0
while i < len(seq):
    if preso[i]:
        j = i
        while j < len(seq) and preso[j]: j += 1
        if j - i <= 3:
            for k in range(i, j): presos[seq[k][0]] += 1
        i = j
    else: i += 1
ruins = [(s, n) for s, n in sorted(presos.items()) if n > 3]
if ruins:
    print("segundos com quadros repetidos:", ", ".join(f"{s}s ({n})" for s, n in ruins)); sys.exit(1)
print(f"quadros ok ({sum(len(x) for x in por_seg.values())} conferidos)")
