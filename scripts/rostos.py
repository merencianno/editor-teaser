"""Rosto e luz de cada plano de uma versão (OpenCV, 3 quadros por plano) e casamento de cor entre câmeras pela pele.

  uv run --no-project --with "opencv-python-headless<4.11" --with "numpy<2.3" python scripts/rostos.py <projeto> <vN>

Grava nas duas composições da versão:
- segmentos[].rosto: centro do rosto no plano (o recorte, principalmente o 9:16, segue esse ponto);
- segmentos[].exposicao: leva a pele de cada take à luz típica da sua câmera (a luz não pula entre takes);
- cameras.*.rosto: onde o rosto costuma ficar (mediana), usado quando um plano não acha rosto;
- cameras.b.ganho: ganho R/G/B que casa a pele da câmera B na da A (só com duas câmeras);
- cor.luz: só se a pele mediana da câmera A estiver fora de 45–70 IRE (leva à borda mais próxima).
Imprime tudo o que mediu: confira antes de aceitar (num caso real a câmera lateral saiu ~15 % mais clara e menos
vermelha; o ganho por canal corrigiu sem mexer no look).
"""
import json, subprocess, sys
import cv2, numpy as np
from comum import RAIZ, composicoes, props_get, props_grava, versao_arg

W, H = 960, 540
CASC = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")


def quadro(arq, t):
    r = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", f"{max(0, t):.3f}", "-i", str(arq), "-frames:v", "1",
                        "-vf", f"scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True)
    if len(r.stdout) != W * H * 3: return None
    return np.frombuffer(r.stdout, np.uint8).reshape((H, W, 3))


def rosto(img):
    g = cv2.equalizeHist(cv2.cvtColor(img, cv2.COLOR_RGB2GRAY))
    fs = CASC.detectMultiScale(g, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))
    if len(fs) == 0: return None
    x, y, w, h = max(fs, key=lambda r: r[2] * r[3])
    return ((x + w / 2) / W, (y + h / 2) / H, w / W)


def pele(img, cx, cy, larg):
    """pixels de pele numa caixa do tamanho do rosto: (média RGB, luma p50 em IRE aproximado)"""
    x, y, r = int(cx * W), int(cy * H), max(20, int(larg * W * 0.45))
    c = img[max(0, y - r):y + r, max(0, x - r):x + r].reshape(-1, 3).astype(np.float32)
    R, G, B = c[:, 0], c[:, 1], c[:, 2]
    Y = 0.2126 * R + 0.7152 * G + 0.0722 * B
    m = (R > G) & (G > B) & (Y > 25) & (R - B > 10)
    if m.sum() < 150: return None
    # 8 bits de vídeo: 16 = 0 IRE, 235 = 100 IRE (o proxy é limitado)
    return c[m].mean(0), float((np.median(Y[m]) - 16) / 219 * 100)


def main():
    proj, v = sys.argv[1], versao_arg(sys.argv[2])
    comps = composicoes(proj, v)
    tl = props_get(comps[0])
    pub = RAIZ / "remotion/public"
    medidas = []
    for i, s in enumerate(tl["segmentos"]):
        cam = tl["cameras"][s["camera"]]
        arq = pub / cam["arquivo"]
        pts, peles = [], []
        for t in (s["de"] + 0.3, (s["de"] + s["ate"]) / 2, s["ate"] - 0.3):
            img = quadro(arq, t + cam["offset"])
            if img is None: continue
            r = rosto(img)
            if r:
                pts.append(r)
                p = pele(img, *r)
                if p: peles.append(p)
        medidas.append((s, pts, peles))
    # mediana por câmera e descarte de falso positivo (mão, reflexo): longe demais de onde a pessoa costuma estar
    for id_ in tl["cameras"]:
        todos = [p for s, pts, _ in medidas if s["camera"] == id_ for p in pts]
        if not todos: print(f"câmera {id_}: nenhum rosto achado; fica o padrão {tl['cameras'][id_]['rosto']}"); continue
        ref = (float(np.median([p[0] for p in todos])), float(np.median([p[1] for p in todos])))
        tl["cameras"][id_]["rosto"] = [round(ref[0], 3), round(ref[1], 3)]
        print(f"câmera {id_}: rosto típico em {tl['cameras'][id_]['rosto']}")
        for s, pts, _ in medidas:
            if s["camera"] != id_: continue
            bons = [p for p in pts if abs(p[0] - ref[0]) < 0.12 and abs(p[1] - ref[1]) < 0.12]
            s["rosto"] = [round(float(np.median([p[0] for p in bons])), 3), round(float(np.median([p[1] for p in bons])), 3)] if bons \
                else tl["cameras"][id_]["rosto"]
    # exposição por plano: pele de cada take → mediana da câmera (limites para não "corrigir" sombra intencional)
    ire_cam, rgb_cam = {}, {}
    for id_ in tl["cameras"]:
        ires = [np.median([p[1] for p in pl]) for s, _, pl in medidas if s["camera"] == id_ and pl]
        rgbs = [p[0] for s, _, pl in medidas if s["camera"] == id_ for p in pl]
        if not ires: continue
        ire_cam[id_] = float(np.median(ires)); rgb_cam[id_] = np.median(rgbs, axis=0)
        for s, _, pl in medidas:
            if s["camera"] == id_ and pl:
                s["exposicao"] = round(float(np.clip(ire_cam[id_] / max(1.0, np.median([p[1] for p in pl])), 0.85, 1.35)), 3)
    for s, pts, pl in medidas:
        print(f"  {s['de']:8.2f}–{s['ate']:8.2f} {s['camera']} rosto={s.get('rosto')} ({len(pts)}/3) exposição={s.get('exposicao', 1)}")
    if "a" in ire_cam:
        ire = ire_cam["a"]
        print(f"pele da câmera A: ~{ire:.0f} IRE (alvo 45–70)")
        if ire < 45 or ire > 70:
            alvo = 45 if ire < 45 else 70
            tl["cor"]["luz"] = round(float(np.clip(alvo / max(ire, 1), 0.8, 1.6)), 3)
            print(f"  → cor.luz = {tl['cor']['luz']}")
    if "a" in rgb_cam and "b" in rgb_cam:
        g = rgb_cam["a"] / np.maximum(rgb_cam["b"], 1) * np.array(tl["cameras"]["a"]["ganho"])
        tl["cameras"]["b"]["ganho"] = [round(float(x), 3) for x in np.clip(g, 0.6, 1.6)]
        print(f"pele A {np.round(rgb_cam['a'], 1)} × B {np.round(rgb_cam['b'], 1)} → ganho da B {tl['cameras']['b']['ganho']}")
    for comp in comps:
        d = props_get(comp)
        d["segmentos"] = tl["segmentos"]; d["cameras"] = tl["cameras"]; d["cor"]["luz"] = tl["cor"]["luz"]
        props_grava(comp, d)
    print(f"gravado em {', '.join(comps)}")


if __name__ == "__main__":
    main()
