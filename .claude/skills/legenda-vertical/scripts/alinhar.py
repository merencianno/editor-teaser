"""Tempo real de cada palavra: alinhamento forçado (torchaudio MMS_FA) do texto aprovado com a voz.

Entrada: frases.json = [{"texto": "...", "inicio": s, "fim": s}, ...]  (segundos NO ARQUIVO DE ÁUDIO, em ordem de fala)
         opcionais "janelaInicio"/"janelaFim": limites duros da janela (o corte do vídeo). Sem eles a janela vai até
         0,8 s depois da frase e, se a fala continua no bruto, a última palavra "estica" sobre o que veio depois.
Saída:   palavras.json = [{"inicio": s, "palavras": [{"w": "Hoje", "s": 12.05, "e": 12.31}, ...]}, ...]

  uv run --no-project --index https://download.pytorch.org/whl/cpu --with torch --with torchaudio --with soundfile \
    python alinhar.py voz.m4a frases.json palavras.json

Por que não o tempo do Whisper: ele estica uma palavra sobre a pausa seguinte (uma palavra curta com 2,5 s) e a
legenda fica adiantada ou "travando". O alinhador também estica às vezes; por isso cada palavra é recortada pela
energia da voz no fim. Roda bem na CPU (o modelo é pequeno); na primeira vez baixa o MMS_FA (~1,2 GB).
"""
import json, re, subprocess, sys, unicodedata
import numpy as np, torch, torchaudio

SR = 16000
# número escrito em algarismo vira palavra para o alinhador (que só conhece letras); complete conforme o idioma
NUM = {"1": "um", "2": "dois", "3": "tres", "4": "quatro", "5": "cinco", "10": "dez", "100": "cem", "1000": "mil"}


def romano(w):
    w = NUM.get(re.sub(r"\D", "", w), w) if re.fullmatch(r"\W*\d+\W*", w) else w
    w = unicodedata.normalize("NFD", w.lower()).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z']", "", w) or "a"


def main(voz, entrada, saida):
    frases = json.load(open(entrada))
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", voz, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    audio = torch.from_numpy(np.frombuffer(pcm, np.float32).copy())
    b = torchaudio.pipelines.MMS_FA
    model, tok, alin = b.get_model(with_star=False), b.get_tokenizer(), b.get_aligner()
    res = []
    for i, f in enumerate(frases):
        a0, a1 = max(0, f["inicio"] - 0.4), f["fim"] + 0.8
        # a janela não invade a frase vizinha (senão a última palavra "pega" o som dela)
        if i + 1 < len(frases) and f["inicio"] < frases[i + 1]["inicio"] < a1: a1 = max(f["fim"], frases[i + 1]["inicio"] - 0.05)
        if i and frases[i - 1]["inicio"] < f["inicio"]: a0 = max(a0, min(f["inicio"] - 0.1, frases[i - 1]["fim"]))
        if "janelaInicio" in f: a0 = max(a0, min(f["janelaInicio"], f["inicio"] - 0.02))
        if "janelaFim" in f: a1 = min(a1, max(f["janelaFim"], f["fim"] + 0.02))
        wav = audio[int(a0 * SR):int(a1 * SR)].unsqueeze(0)
        pal = f["texto"].split()
        with torch.inference_mode():
            em, _ = model(wav)
            spans = alin(em[0], tok([romano(w) for w in pal]))
        k = wav.shape[1] / em.shape[1] / SR
        ws = [{"w": w, "s": a0 + sp[0].start * k, "e": a0 + sp[-1].end * k} for w, sp in zip(pal, spans)]
        # recorte pela energia (10 ms): palavra longa demais = pausa engolida
        x = wav[0].numpy(); H = SR // 100
        rms = np.sqrt(np.convolve(x ** 2, np.ones(H) / H, "same"))[::H]
        lim = 0.12 * np.percentile(rms, 95)
        for p in ws:
            i0, i1 = int((p["s"] - a0) * 100), int((p["e"] - a0) * 100)
            voz_ = np.nonzero(rms[i0:i1 + 1] > lim)[0]
            if len(voz_) and p["e"] - p["s"] > 0.6:
                p["s"], p["e"] = a0 + (i0 + voz_[0]) / 100, a0 + (i0 + voz_[-1] + 1) / 100
                if p["e"] - p["s"] > 0.9: p["s"] = max(p["s"], p["e"] - 0.45)
            p["s"], p["e"] = round(p["s"], 3), round(p["e"], 3)
        res.append({"inicio": f["inicio"], "palavras": ws})
        print(f'{f["inicio"]:8.2f} ' + " ".join(f'{x["w"]}[{x["s"]:.2f}-{x["e"]:.2f}]' for x in ws), flush=True)
    json.dump(res, open(saida, "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(*sys.argv[1:4])
