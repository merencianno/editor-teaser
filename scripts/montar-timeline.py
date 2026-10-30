"""Roteiro aprovado (texto → roteiro.json) → timeline da versão nova nas duas composições do Remotion.

  python3 scripts/montar-timeline.py <projeto> <roteiro.json> [--versao N]

Cria trabalho/<projeto>/vN/ (roteiro.json, frases.json, relatorio.md) e as composições
Teaser16x9-<projeto>-vN e Teaser9x16-<projeto>-vN em remotion/src/Composicoes.tsx. Versão nova nunca sobrescreve uma
existente: sem --versao, pega a próxima livre.

Regras aplicadas (skills ritmo-e-corte e som-e-musica):
- o roteiro manda na ordem; cada trecho é um bloco de fala corrida (o corte cai dentro dele só em pausa longa);
- pausa > 1,0 s vira 0,6 s; borda de palavra −0,08 s / +0,12 s; respiro pedido depois do trecho;
- zoom: cena nova abre a 1,0 com push de 5 %; jump cut alterna 1,0 / 1,075; frase-chave em 1,15 (punch-in) com push
  de 5 %; reação (respiro ≥ 0,8 s) com push de 8 %; o resto quase parado (2 %);
- com duas câmeras, toda emenda troca de câmera (esconde o jump cut, cumpre os 30°);
- música: o ponto `hitNaFaixa` da trilha cai no começo da frase-chave escolhida; ajustes (turn line) por fala.
"""
import argparse, json, re, shutil, sys
from comum import composicoes, ler_projeto, mmss, pasta, props_grava, slug
from falas import Falas, canon, norm

MAX_PAUSA, PAUSA_FICA = 1.0, 0.6
ANTES, DEPOIS = 0.08, 0.12
Z_ABERTO, Z_JUMP, Z_CHAVE = 1.0, 1.075, 1.15


def acha_seq(ws, texto):
    """índice (em ws) da primeira palavra da sequência `texto`"""
    alvo = [canon(x) for x in texto.split() if norm(x)]
    for i in range(len(ws) - len(alvo) + 1):
        if all(canon(ws[i + j]["w"]) == a for j, a in enumerate(alvo)): return i, i + len(alvo) - 1
    # tolera uma palavra diferente (o Whisper erra uma grafia)
    for i in range(len(ws) - len(alvo) + 1):
        if sum(canon(ws[i + j]["w"]) == a for j, a in enumerate(alvo)) >= len(alvo) - 1: return i, i + len(alvo) - 1
    return None


def pedacos_do_trecho(F, tr):
    a = F.achar(tr["de"], tr["inicio"])
    b = F.achar(tr.get("de_fim", tr["de"]), tr["fim"], janela=tr.get("janela", 90), depois_de=a["i"])
    ws = F.ws[a["i"]:b["k"] + 1]
    max_p, fica = tr.get("maxPausa", MAX_PAUSA), tr.get("pausaFica", PAUSA_FICA)
    # começa um pouco antes da primeira palavra, sem pegar o fim da palavra anterior do bruto
    out, ini = [], min(ws[0]["s"] - 0.02, max(ws[0]["s"] - ANTES, a["antes"] + 0.02))
    for w1, w2 in zip(ws, ws[1:]):
        if w2["s"] - w1["e"] > max_p:
            out.append([ini, w1["e"] + DEPOIS + fica * 0.4])
            ini = w2["s"] - ANTES - fica * 0.6
    fim = min(ws[-1]["e"] + DEPOIS + tr.get("respiroDepois", 0), b["depois"] - 0.06)
    out.append([ini, max(fim, ws[-1]["e"] + 0.05)])
    return out, ws


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("projeto"); ap.add_argument("roteiro"); ap.add_argument("--versao", type=int)
    a = ap.parse_args()
    pj = ler_projeto(a.projeto); dir_ = pasta(a.projeto)
    rot = json.loads(open(a.roteiro).read())
    F = Falas(a.projeto)
    v = a.versao or 1 + max([int(m.group(1)) for p in dir_.glob("v*") if (m := re.fullmatch(r"v(\d+)", p.name))] or [0])
    vdir = dir_ / f"v{v}"
    if vdir.exists() and any(vdir.iterdir()): sys.exit(f"{vdir} já existe: versão nova nunca sobrescreve (use outra --versao)")
    vdir.mkdir(parents=True, exist_ok=True)
    duas = "b" in pj["fontes"]

    segs, ws_tl, rel, t, cam = [], [], [], 0.0, "a"
    for bloco in rot["blocos"]:
        for tr in bloco["trechos"]:
            pedacos, ws = pedacos_do_trecho(F, tr)
            ch = acha_seq(ws, tr["chave"]) if tr.get("chave") else None
            if tr.get("chave") and ch is None: sys.exit(f"frase-chave não está no trecho: {tr['chave']!r}")
            # parte cada pedaço na frase-chave: ela ganha um plano próprio (punch-in)
            planos = []
            for de, ate in pedacos:
                cortes = [de]
                if ch:
                    w0, w1 = ws[ch[0]], ws[ch[1]]
                    if de < w0["s"] < ate:
                        antes = ws[ch[0] - 1]["e"] if ch[0] else de
                        cortes.append(max(antes, w0["s"] - 0.1))
                    if de < w1["e"] < ate:
                        cortes.append(min(ate, w1["e"] + DEPOIS))
                cortes = sorted(set(round(c, 3) for c in cortes)) + [ate]
                partes = [[x, y] for x, y in zip(cortes, cortes[1:]) if y - x > 0.05]
                # pedaço curto demais vira parte do vizinho (plano de menos de 0,8 s pisca)
                j = 0
                while j < len(partes):
                    if partes[j][1] - partes[j][0] < 0.8 and len(partes) > 1:
                        if j: partes[j - 1][1] = partes[j][1]
                        else: partes[1][0] = partes[0][0]
                        partes.pop(j)
                    else: j += 1
                planos += [(x, y, ch is not None and x - 0.15 <= ws[ch[0]]["s"] < y) for x, y in partes]
            ultimo_zoom = None
            for k, (de, ate, e_chave) in enumerate(planos):
                if segs and duas: cam = "b" if cam == "a" else "a"
                cam = tr.get("camera", cam) if k == 0 else cam
                contiguo = segs and abs(segs[-1]["ate"] - de) < 0.02
                if e_chave: zoom, push = Z_CHAVE, 0.05
                elif k == 0: zoom, push = Z_ABERTO, 0.05
                elif contiguo: zoom, push = (ultimo_zoom or Z_ABERTO), 0.02   # volta da frase-chave sem pular
                else: zoom, push = (Z_JUMP if (ultimo_zoom or Z_ABERTO) == Z_ABERTO else Z_ABERTO), 0.02  # jump cut alterna
                if k == len(planos) - 1 and tr.get("respiroDepois", 0) >= 0.8 and not e_chave: push = 0.08  # reação
                zoom = tr.get("zoom", zoom) if k == 0 else zoom
                # junção sem troca de câmera nem de tamanho é jump cut aparente: alterna o tamanho
                if segs and not contiguo and cam == segs[-1]["camera"] and abs(zoom - segs[-1]["zoom"]) < 0.01:
                    zoom = Z_JUMP if zoom == Z_ABERTO else Z_ABERTO
                if not e_chave: ultimo_zoom = zoom
                segs.append({"bloco": bloco["nome"], "de": round(de, 3), "ate": round(ate, 3), "camera": cam,
                             "zoom": zoom, "push": push, "chave": bool(e_chave)})
                dentro = [w for w in ws if de - 0.1 <= w["s"] < ate and not (k and w["s"] < de)]
                texto = " ".join(w["w"] for w in dentro)
                rel.append(f"| {mmss(t)} | {ate - de:4.1f} s | {bloco['nome']} | {mmss(de)} | {cam} | {zoom:.3f}{' chave' if e_chave else ''} | {texto} |")
                for w in dentro:
                    ws_tl.append({"w": w["w"], "s": t + max(0.0, w["s"] - de), "e": t + min(w["e"], ate) - de, "bruto": w["s"], "bruto_e": w["e"]})
                t += ate - de
    fim_fala = t

    # ── frases (para a legenda): quebra em pontuação final, pausa ≥ 0,6 s ou corte ──
    frases, cur = [], []
    for w in ws_tl:
        if cur and (cur[-1]["w"].endswith((".", "?", "!")) or w["bruto"] - cur[-1]["bruto_e"] >= 0.6
                    or abs((w["s"] - cur[-1]["s"]) - (w["bruto"] - cur[-1]["bruto"])) > 0.05):
            frases.append(cur); cur = []
        cur.append(w)
    if cur: frases.append(cur)
    frases_json = [{"texto": " ".join(x["w"] for x in fr), "inicio": round(fr[0]["bruto"], 3), "fim": round(fr[-1]["bruto_e"], 3)} for fr in frases]
    (vdir / "frases.json").write_text(json.dumps(frases_json, ensure_ascii=False, indent=1))

    # ── música: hit na frase-chave; ajustes por fala ──
    m = rot.get("musica") or {}
    def na_tl(texto):
        alvo = [canon(x) for x in texto.split() if norm(x)]
        for i in range(len(ws_tl) - len(alvo) + 1):
            if all(canon(ws_tl[i + j]["w"]) == a_ for j, a_ in enumerate(alvo)): return ws_tl[i]["s"]
        sys.exit(f"fala da música não está no corte: {texto!r}")
    em_tl = 0.0
    if m.get("hitNaFaixa") is not None:
        chaves = [s for s in segs if s["chave"]]
        alvo = na_tl(m["hitEm"]) if m.get("hitEm") else None
        if alvo is None and chaves:
            s0 = next((s for s in chaves if "desejo" in s["bloco"].lower()), chaves[0])
            alvo = sum(x["ate"] - x["de"] for x in segs[:segs.index(s0)])
        if alvo is not None: em_tl = round(alvo - m["hitNaFaixa"], 3)
    ajustes = [{"emTimeline": round(na_tl(x["fala"]) + x.get("desloca", -0.1), 3), "dur": x.get("dur", 2.0),
                "ganho": x.get("ganho", 0.3), "rampa": x.get("rampa", 0.8)} for x in m.get("ajustes", [])]
    musica = {"arquivo": pj.get("musica", "") if m.get("usar", True) else "", "emTimeline": em_tl,
              "volumeSobFala": m.get("volumeSobFala", 0.22), "volumeCheio": m.get("volumeCheio", 0.7), "ajustes": ajustes}

    cta = rot.get("cta") or {}
    cameras = {"a": {"arquivo": pj["fontes"]["a"]["arquivo"], "arquivoFinal": pj["fontes"]["a"].get("arquivoFinal", ""),
                     "offset": 0.0, "ganho": [1.0, 1.0, 1.0], "rosto": [0.5, 0.4]}}
    if duas:
        b = pj["fontes"]["b"]
        cameras["b"] = {"arquivo": b["arquivo"], "arquivoFinal": b.get("arquivoFinal", ""), "offset": b["offset"],
                        "ganho": [1.0, 1.0, 1.0], "rosto": [0.5, 0.4]}

    def props(formato):
        vert = formato == "9x16"
        return {
            "projeto": slug(a.projeto), "formato": formato, "fps": pj["fps"],
            "fontes": {"voz": pj["fontes"]["voz"], "usarFinal": False},
            "cameras": cameras,
            "transicao": {"atrasoImagem": 3},
            "enquadramento": {"verticalExtra": 1.3, "alturaRosto": 0.4},
            "cor": {"contraste": 1.04, "luz": 1.0,
                    "arco": {"inicio": {"temperatura": -0.03, "saturacao": 0.9}, "fim": {"temperatura": 0.03, "saturacao": 1.0}}},
            "abertura": rot.get("abertura", 1.0),
            "segmentos": segs,
            "legenda": {"mostrar": vert, "estilo": "padrao", "tamanho": 86 if vert else 60, "peso": 550, "topo": 0.6 if vert else 0.64, "cor": "#ffffff"},
            "legendas": [],
            "musica": musica,
            "cta": {"duracao": cta.get("duracao", 4.0), "titulo": cta.get("titulo", ""), "linha": cta.get("linha", ""),
                    "botao": cta.get("botao", ""), "mostrarBotao": bool(cta.get("botao")), "marcas": rot.get("marcas", [])},
        }

    shutil.copy2(a.roteiro, vdir / "roteiro.json")
    for comp, formato in zip(composicoes(a.projeto, v), ("16x9", "9x16")):
        props_grava(comp, props(formato), novo=True)
        print(f"composição: {comp}")
    total = fim_fala + cta.get("duracao", 4.0)
    n_cortes = sum(1 for x, y in zip(segs, segs[1:]) if abs(x["ate"] - y["de"]) > 0.02)
    (vdir / "relatorio.md").write_text(
        f"# {rot.get('titulo', 'teaser')} · v{v}\n\n{total:.1f} s ({fim_fala:.1f} s de fala + {total - fim_fala:.1f} s de cartela) · "
        f"{len(segs)} planos · {n_cortes} cortes de fala · {len(frases_json)} frases"
        + (f" · música entra em {em_tl:+.2f} s" if musica["arquivo"] else " · sem música") + "\n\n"
        "| na timeline | dura | bloco | no bruto | câm. | zoom | fala |\n|---|---|---|---|---|---|---|\n" + "\n".join(rel) + "\n")
    print(f"v{v}: {total:.1f} s, {len(segs)} planos, {n_cortes} cortes de fala, {len(frases_json)} frases → {vdir}")


if __name__ == "__main__":
    main()
