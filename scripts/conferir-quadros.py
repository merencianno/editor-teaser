"""Quadros repetidos num render: com a máquina carregada o Remotion às vezes não extrai o quadro a tempo e repete o
anterior (a imagem "engasga"). Conta, por segundo, quadros quase idênticos ao anterior (YDIF < 0,05), ignorando
segundos inteiros parados (cartela, preto). Sai com código 1 se algum segundo tiver mais de 3.

  python3 scripts/conferir-quadros.py video.mp4
"""
import collections, re, subprocess, sys

arq = sys.argv[1]
r = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", arq, "-vf", "signalstats,metadata=print:key=lavfi.signalstats.YDIF",
                    "-an", "-f", "null", "-"], capture_output=True, text=True)
t, por_seg = None, collections.defaultdict(list)
for linha in r.stderr.splitlines():
    if m := re.search(r"pts_time:([\d.]+)", linha): t = float(m.group(1))
    elif (m := re.search(r"YDIF=([\d.]+)", linha)) and t is not None: por_seg[int(t)].append(float(m.group(1)))
ruins = []
for s, ds in sorted(por_seg.items()):
    parados = sum(d < 0.05 for d in ds)
    if parados > 3 and parados < len(ds) - 2: ruins.append((s, parados))
if ruins:
    print("segundos com quadros repetidos:", ", ".join(f"{s}s ({n})" for s, n in ruins)); sys.exit(1)
print(f"quadros ok ({sum(len(x) for x in por_seg.values())} conferidos)")
