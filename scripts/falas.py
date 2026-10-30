"""Acha uma fala na transcrição: tempo aproximado + começo do texto → início e fim exatos por palavra.

  python3 scripts/falas.py <projeto> "01:12.5" "as primeiras palavras da fala"
Como módulo: Falas(projeto).achar(aprox, texto) → {ini, fim, i, k, texto, antes, depois}
"""
import json, re, sys, unicodedata
from comum import pasta, seg

norm = lambda s: re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode())
# "pra"/"para", "tá"/"está": o Whisper escreve de um jeito, o roteiro de outro
SINONIMOS = {"pra": "para", "pro": "para", "ta": "esta", "to": "estou", "ce": "voce", "vc": "voce"}
canon = lambda s: SINONIMOS.get(norm(s), norm(s))


class Falas:
    def __init__(self, projeto):
        arq = pasta(projeto) / "palavras.json"
        if not arq.exists(): sys.exit("sem transcrição: rode scripts/transcrever.py primeiro")
        self.ws = [w for s in json.loads(arq.read_text()) for w in s["words"]]

    def achar(self, aprox, texto, janela=8.0, depois_de=0):
        """depois_de: índice mínimo da palavra (o fim de um trecho nunca vem antes do começo)"""
        alvo = [canon(x) for x in texto.split() if norm(x)]
        t0 = seg(aprox); ws = self.ws; melhor = None
        for i, w in enumerate(ws):
            if i < depois_de or abs(w["s"] - t0) > janela: continue
            ok = sum(1 for j, a in enumerate(alvo) if i + j < len(ws) and canon(ws[i + j]["w"]) == a)
            nota = ok / len(alvo) - abs(w["s"] - t0) / 100
            if melhor is None or nota > melhor[0]: melhor = (nota, i, i + len(alvo) - 1, ok)
        if melhor is None: raise SystemExit(f"nada perto de {aprox}: confira a minutagem")
        _, i, k, ok = melhor
        k = min(k, len(ws) - 1)
        if ok < len(alvo) * 0.75:
            raise SystemExit(f"fala não achada: {aprox} {texto!r} (casou {ok}/{len(alvo)}: {' '.join(w['w'] for w in ws[i:k + 1])})")
        return {"ini": ws[i]["s"], "fim": ws[k]["e"], "i": i, "k": k, "texto": " ".join(w["w"] for w in ws[i:k + 1]),
                "antes": ws[i - 1]["e"] if i else 0.0, "depois": ws[k + 1]["s"] if k + 1 < len(ws) else ws[k]["e"] + 2}


if __name__ == "__main__":
    print(json.dumps(Falas(sys.argv[1]).achar(sys.argv[2], sys.argv[3]), ensure_ascii=False, indent=1))
