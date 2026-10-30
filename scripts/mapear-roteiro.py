"""Roteiro no bruto (portão 1): pega o roteiro ou a copy aprovada e acha cada fala nos takes do bruto.

  python3 scripts/mapear-roteiro.py <projeto> <roteiro.md|.txt|.docx>

Formato do roteiro (o que vier da skill de copy serve; o mínimo é um parágrafo por fala):
  # / ## título        → bloco (ex.: "## Gancho", "## Virada", "## Convite")
  parágrafo de texto   → uma fala a achar no bruto (aspas e marcação são ignoradas)
  **trecho em negrito** → frase-chave daquele bloco (punch-in e, no bloco do pico, o hit da música)
  [colchetes] ou "rótulo: …" (B-roll:, Asset:, Imagem:, Música:, Cartela:, CTA:, Nota:) → direção, não é fala

Para cada fala: todos os takes parecidos no bruto, o melhor (texto mais fiel, Whisper mais seguro, menos tropeço),
minutagem, duração, pausas que viram corte, e o que a copy pede e o bruto não tem. Grava:
  trabalho/<projeto>/mapa.md                 o mapa para o dono ler (portão 1)
  trabalho/<projeto>/mapa/fala-NN.m4a        o take escolhido de cada fala, para ouvir antes de aprovar
  trabalho/<projeto>/roteiro-rascunho.json   ponto de partida do roteiro.json (o Claude completa e o dono aprova)
"""
import difflib, json, re, subprocess, sys, zipfile
from comum import RAIZ, ler_projeto, mmss, pasta
from falas import Falas, canon, norm

ROTULOS = ("b-roll", "broll", "asset", "imagem", "musica", "música", "trilha", "cartela", "cta", "nota", "obs", "direcao", "direção", "tela", "logo", "corte")
MULETAS = {"e", "ahn", "ah", "hum", "tipo", "ne", "entao", "assim", "ok"}
MIN_FIEL, BOM = 0.55, 0.85


def ler_texto(arq):
    if arq.lower().endswith(".docx"):
        xml = zipfile.ZipFile(arq).read("word/document.xml").decode("utf8")
        pars = []
        for p in re.findall(r"<w:p[ >].*?</w:p>", xml, re.S):
            estilo = re.search(r'<w:pStyle w:val="([^"]+)"', p)
            # negrito do Word vira **…** (frase-chave)
            runs = []
            for r in re.findall(r"<w:r[ >].*?</w:r>", p, re.S):
                txt = "".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", r, re.S))
                runs.append(f"**{txt}**" if txt.strip() and re.search(r"<w:b/>|<w:b w:val=\"(1|true)\"/>", r) else txt)
            linha = "".join(runs).replace("****", "")
            if estilo and re.match(r"(Heading|Ttulo|Titulo|Título)", estilo.group(1)): linha = "## " + linha
            pars.append(linha)
        return "\n\n".join(pars)
    return open(arq, encoding="utf8").read()


def estruturar(texto):
    blocos, cur, cta, titulo = [], None, [], []
    for par in re.split(r"\n\s*\n|\n(?=#)", texto):
        par = par.strip()
        if not par: continue
        if re.match(r"^#\s", par) and not blocos and re.search(r"^##\s", texto, re.M):
            titulo.append(par.lstrip("#").strip()); continue  # "# Título" com "## blocos" abaixo: é o título
        if par.startswith("#"):
            cur = {"nome": par.lstrip("#").strip(), "falas": [], "direcao": []}; blocos.append(cur); continue
        if cur is None:
            cur = {"nome": "bloco 1", "falas": [], "direcao": []}; blocos.append(cur)
        fala = []
        for linha in par.split("\n"):
            l = linha.strip()
            rot = re.match(r"^[-*>\s]*([A-Za-zçãéíóú\- ]{2,14}):\s*(.+)$", l)
            if l.startswith(("[", "(")) or (rot and rot.group(1).strip().lower() in ROTULOS):
                cur["direcao"].append(l)
                if rot and rot.group(1).strip().lower() in ("cartela", "cta"): cta.append(rot.group(2).strip())
            elif l:
                fala.append(l)
        if fala:
            l = " ".join(fala)
            chave = re.findall(r"\*\*(.+?)\*\*", l)
            limpo = re.sub(r"\s+", " ", re.sub(r"[*_\"“”]|^[->\s]+", "", l)).strip()
            if len(limpo.split()) >= 2: cur["falas"].append({"texto": limpo, "chave": chave[0] if chave else None})
    return blocos, cta, (titulo[0] if titulo else None)


def candidatos(ws, fala):
    alvo = [canon(x) for x in fala.split() if norm(x)]
    n = len(alvo); seq = [canon(w["w"]) for w in ws]
    achados = []
    primeiras = set(alvo[:3])
    for i in range(len(ws)):
        if seq[i] not in primeiras: continue
        melhor = None
        for m in range(max(1, int(n * 0.8)), int(n * 1.25) + 2):
            r = difflib.SequenceMatcher(None, alvo, seq[i:i + m], autojunk=False).ratio()
            if melhor is None or r > melhor[0]: melhor = (r, i, i + m - 1)
        if melhor[0] >= MIN_FIEL: achados.append(melhor)
    achados.sort(reverse=True)
    escolhidos = []
    for r, i, k in achados:  # takes que não se sobrepõem
        if all(k < i2 or i > k2 for _, i2, k2 in escolhidos): escolhidos.append((r, i, k))
    return escolhidos[:4]


def qualidade(ws, i, k):
    trecho = ws[i:k + 1]
    p = sum(w.get("p", 1.0) for w in trecho) / len(trecho)
    tropeco = sum(1 for a, b in zip(trecho, trecho[1:]) if canon(a["w"]) == canon(b["w"]) and len(norm(a["w"])) > 1)
    muleta = sum(1 for w in trecho if norm(w["w"]) in MULETAS and w["e"] - w["s"] > 0.35)
    pausas = [(a["e"], b["s"]) for a, b in zip(trecho, trecho[1:]) if b["s"] - a["e"] > 1.0]
    return p, tropeco + muleta, pausas


def diferencas(fala, ws, i, k):
    a = fala.split(); b = [w["w"] for w in ws[i:k + 1]]
    sm = difflib.SequenceMatcher(None, [canon(x) for x in a], [canon(x) for x in b], autojunk=False)
    out = []
    for op, a0, a1, b0, b1 in sm.get_opcodes():
        if op == "replace": out.append(f"copy \"{' '.join(a[a0:a1])}\" → bruto \"{' '.join(b[b0:b1])}\"")
        elif op == "delete": out.append(f"falta no bruto: \"{' '.join(a[a0:a1])}\"")
        elif op == "insert": out.append(f"só no bruto: \"{' '.join(b[b0:b1])}\"")
    return out


def main():
    proj, arq = sys.argv[1], sys.argv[2]
    pj = ler_projeto(proj); dir_ = pasta(proj); F = Falas(proj); ws = F.ws
    blocos, cta, titulo = estruturar(ler_texto(arq))
    voz = RAIZ / "remotion/public" / pj["fontes"]["voz"]
    (dir_ / "mapa").mkdir(exist_ok=True)
    md = [f"# Roteiro no bruto · {arq.split('/')[-1]}", "",
          "Cada fala da copy achada nos takes do bruto. ✅ fiel · ⚠ parecida (confira a diferença) · ❌ o bruto não tem.",
          "Ouça os takes escolhidos em `mapa/fala-NN.m4a` antes de aprovar.", ""]
    rascunho = {"titulo": titulo or (blocos[0]["nome"] if blocos else "teaser"), "marcas": [], "nomes": [], "blocos": [], "insercoes": [],
                "cta": {"titulo": cta[0] if cta else "", "linha": cta[1] if len(cta) > 1 else "", "botao": "", "duracao": 4}}
    total, n, faltas = 0.0, 0, []
    for b in blocos:
        md += [f"## {b['nome']}", ""]
        rb = {"nome": b["nome"], "trechos": []}
        for fa in b["falas"]:
            n += 1
            cands = candidatos(ws, fa["texto"])
            if not cands:
                md += [f"**{n:02d}** ❌ \"{fa['texto']}\"", "", "   O bruto não tem esta fala (nem parecida). Regravar, trocar por outra fala ou cortar.", ""]
                faltas.append(fa["texto"]); continue
            notas = []
            for r, i, k in cands:
                p, trop, pausas = qualidade(ws, i, k)
                notas.append((r - 0.04 * trop + 0.1 * p, r, i, k, p, trop, pausas))
            notas.sort(reverse=True)
            _, r, i, k, p, trop, pausas = notas[0]
            dur = ws[k]["e"] - ws[i]["s"]
            enxuto = dur - sum(b_ - a_ - 0.6 for a_, b_ in pausas)
            total += enxuto
            st = "✅" if r >= BOM else "⚠"
            md += [f"**{n:02d}** {st} \"{fa['texto']}\"", "",
                   f"- take: **{mmss(ws[i]['s'])} → {mmss(ws[k]['e'])}** · {dur:.1f} s"
                   + (f" ({enxuto:.1f} s com {len(pausas)} pausa(s) longa(s) virando corte)" if pausas else "")
                   + f" · fidelidade {r:.0%} · clareza {p:.0%}" + (f" · {trop} tropeço(s)" if trop else "")]
            if r < 1.0:
                for d in diferencas(fa["texto"], ws, i, k)[:4]: md.append(f"- {d}")
            if len(notas) > 1:
                md.append("- outros takes: " + "; ".join(f"{mmss(ws[x[2]]['s'])} ({x[1]:.0%}, clareza {x[4]:.0%})" for x in notas[1:]))
            if fa["chave"]: md.append(f"- frase-chave: \"{fa['chave']}\" → punch-in 115 %")
            md.append("")
            subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{max(0, ws[i]['s'] - 0.3):.2f}", "-to", f"{ws[k]['e'] + 0.4:.2f}",
                            "-i", str(voz), "-c:a", "aac", "-b:a", "128k", str(dir_ / "mapa" / f"fala-{n:02d}.m4a")], check=True)
            ini5 = " ".join(w["w"] for w in ws[i:min(i + 5, k + 1)]); fim5 = " ".join(w["w"] for w in ws[max(i, k - 4):k + 1])
            tr = {"de": mmss(ws[i]["s"]), "inicio": ini5, "fim": fim5}
            if dur > 20: tr["de_fim"] = mmss(ws[k]["s"])
            if fa["chave"]: tr["chave"] = fa["chave"]
            rb["trechos"].append(tr)
        if b["direcao"]: md += ["Direção: " + " · ".join(b["direcao"]), ""]
        if rb["trechos"]: rascunho["blocos"].append(rb)
    # checagem de estrutura (AIDA como checagem, não como regra de escrita)
    md += ["## Checagem", "",
           f"- duração estimada da fala: **{total:.0f} s** (+ cartela)",
           f"- {n - len(faltas)} de {n} falas achadas" + (f"; faltam: {', '.join(repr(x[:40]) for x in faltas)}" if faltas else "")]
    primeiro = next((t for b in rascunho["blocos"] for t in b["trechos"]), None)
    if primeiro: md.append("- gancho: confira se a primeira fala prende nos primeiros 5 s e fala com quem assiste")
    sem_chave = [b["nome"] for b in blocos if b["falas"] and not any(f["chave"] for f in b["falas"])]
    if sem_chave: md.append(f"- blocos sem frase-chave marcada (negrito): {', '.join(sem_chave)}")
    md.append("- CTA: " + (f"\"{cta[0]}\"" if cta else "nenhuma cartela/CTA na copy: pergunte ao dono"))
    (dir_ / "mapa.md").write_text("\n".join(md) + "\n")
    (dir_ / "roteiro-rascunho.json").write_text(json.dumps(rascunho, ensure_ascii=False, indent=1))
    print("\n".join(md))
    print(f"\n→ {dir_ / 'mapa.md'} · {dir_ / 'roteiro-rascunho.json'} · takes em {dir_ / 'mapa'}/")


if __name__ == "__main__":
    main()
