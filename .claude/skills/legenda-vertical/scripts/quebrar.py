"""Palavras alinhadas → pedaços de legenda no padrão vertical (no máximo 2 palavras, no tempo da fala).

  python3 quebrar.py palavras.json legendas.json [--nomes "Marta,Lisboa"] [--marcas "Horta Fácil"] [--max-palavras 2]
Saída: [{"texto": "um momento", "ini": 12.17, "fim": 12.51}, ...]  (segundos no arquivo de áudio)
"""
import argparse, json, re, unicodedata

ANTES = 0.04   # aparece 1 quadro antes do som: o olho lê junto com o ouvido
SEGURA = 0.35  # pausa menor: o pedaço fica até o próximo; maior: sai 0,15 s depois da palavra (tela sem legenda)
JUNTA = 0.25   # duas palavras só formam par se o intervalo entre elas for até isso
# palavras de ligação (português); troque para outro idioma
COLA = set("a o as os um uma de do da dos das no na nos nas em e eu me se que pra pro com por tão como meu minha seu sua ao mais muito".split())
norm = lambda x: re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFD", x.lower()).encode("ascii", "ignore").decode())
pont = lambda w: bool(re.search(r"[.,!?;:…]$", w))


def junta_marcas(ws, marcas):
    """nome de várias palavras vira um pedaço só, nunca quebrado (exceção à regra das 2 palavras)"""
    out, i = [], 0
    while i < len(ws):
        for m in marcas:
            n = len(m.split())
            if [norm(x["w"]) for x in ws[i:i + n]] == [norm(x) for x in m.split()]:
                p = re.search(r"[.,!?;:…]+$", ws[i + n - 1]["w"])
                out.append({"w": m + (p.group(0) if p else ""), "s": ws[i]["s"], "e": ws[i + n - 1]["e"], "marca": True}); i += n; break
        else:
            out.append(ws[i]); i += 1
    return out


def pedacos(ws, n=2):
    """grupos de até n palavras (padrão 2) ditas em sequência; palavra de ligação nunca pisca sozinha ("a / sua
    casa") nem fecha o grupo quando a seguinte vem colada ("medo do / meu" → "medo / do meu")"""
    out, i = [], 0
    while i < len(ws):
        g = [ws[i]]
        while len(g) < n and i + len(g) < len(ws):
            nx, ult = ws[i + len(g)], g[-1]
            if ult.get("marca") or nx.get("marca") or pont(ult["w"]) or nx["s"] - ult["e"] > JUNTA: break
            g.append(nx)
        while len(g) > 1 and norm(g[-1]["w"]) in COLA and norm(g[-2]["w"]) not in COLA and not pont(g[-1]["w"]):
            nn = ws[i + len(g)] if i + len(g) < len(ws) else None
            if nn is None or nn["s"] - g[-1]["e"] > JUNTA: break
            g.pop()
        out.append(g); i += len(g)
    return out


def limpa(w, nomes, marca=False):
    """1–2 palavras não são frase: sem pontuação e sem maiúscula de começo de frase; nome e marca mantêm a maiúscula"""
    w = re.sub(r"[.,!?;:…\"“”«»()]+", "", w).strip("-")
    if marca or norm(w) in nomes or (len(w) > 1 and w.isupper()): return w
    return w.lower()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("entrada"); ap.add_argument("saida")
    ap.add_argument("--nomes", default=""); ap.add_argument("--marcas", default="")
    ap.add_argument("--max-palavras", type=int, default=2, help="2 no padrão; outro número só num estilo irmão")
    a = ap.parse_args()
    frases = json.load(open(a.entrada))
    marcas = [m.strip() for m in a.marcas.split(",") if m.strip()]
    nomes = {norm(n) for n in a.nomes.split(",") if n.strip()}
    for f in frases:  # maiúscula no meio da frase = nome próprio
        ps = [x["w"] for x in f["palavras"]]
        for i, w in enumerate(ps):
            if i and not pont(ps[i - 1]) and w[:1].isupper() and norm(w) != "eu": nomes.add(norm(w))
    todos = [p for f in frases for p in pedacos(junta_marcas(f["palavras"], marcas), a.max_palavras)]
    out = []
    for k, p in enumerate(todos):
        ini = p[0]["s"] - ANTES
        if out and 0 < out[-1]["fim"] - ini < 1: ini = out[-1]["fim"]  # nunca por cima do anterior
        prox = todos[k + 1][0]["s"] - ANTES if k + 1 < len(todos) else None
        fim = prox if prox is not None and 0 <= prox - p[-1]["e"] < SEGURA else p[-1]["e"] + 0.15
        if prox is not None and ini < prox < fim: fim = prox
        texto = " ".join(limpa(w["w"], nomes, w.get("marca")) for w in p)
        out.append({"texto": texto, "ini": round(ini, 3), "fim": round(max(fim, ini + 0.12), 3)})
    json.dump(out, open(a.saida, "w"), ensure_ascii=False, indent=1)
    print(len(out), "pedaços:", " | ".join(x["texto"] for x in out))


if __name__ == "__main__":
    main()
