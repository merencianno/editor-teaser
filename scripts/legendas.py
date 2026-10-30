"""Legenda palavra a palavra de uma versão: frases.json → alinhamento forçado → pedaços de até 2 palavras → as duas
composições da versão (o 9:16 mostra; o 16:9 guarda os pedaços com `legenda.mostrar` desligado).

  python3 scripts/legendas.py <projeto> <vN> [--nomes "Marta"] [--marcas "Horta Fácil"]

O texto das frases é o da transcrição conferida: corrija grafia em trabalho/<projeto>/vN/frases.json (sem mudar a
ordem nem o tempo) e rode de novo. Nomes e marcas também podem vir do roteiro ("nomes", "marcas").
Usa .claude/skills/legenda-vertical/scripts/{alinhar,quebrar}.py.
"""
import argparse, json, subprocess, sys
from comum import RAIZ, composicoes, ler_projeto, pasta, props_get, props_grava, versao_arg

SKILL = RAIZ / ".claude/skills/legenda-vertical/scripts"
UV_TORCH = ["uv", "run", "--no-project", "--index", "https://download.pytorch.org/whl/cpu",
            "--with", "torch", "--with", "torchaudio", "--with", "soundfile", "--with", "numpy", "python"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("projeto"); ap.add_argument("versao"); ap.add_argument("--nomes", default=""); ap.add_argument("--marcas", default="")
    a = ap.parse_args()
    v = versao_arg(a.versao); pj = ler_projeto(a.projeto); vdir = pasta(a.projeto) / f"v{v}"
    rot = json.loads((vdir / "roteiro.json").read_text())
    nomes = ",".join(filter(None, [a.nomes] + rot.get("nomes", [])))
    marcas = ",".join(filter(None, [a.marcas] + rot.get("marcas", [])))
    voz = RAIZ / "remotion/public" / pj["fontes"]["voz"]
    subprocess.run(UV_TORCH + [str(SKILL / "alinhar.py"), str(voz), str(vdir / "frases.json"), str(vdir / "palavras-alinhadas.json")], check=True)
    subprocess.run([sys.executable, str(SKILL / "quebrar.py"), str(vdir / "palavras-alinhadas.json"), str(vdir / "legendas.json"),
                    "--nomes", nomes, "--marcas", marcas,
                    "--max-palavras", str((rot.get("legenda") or {}).get("maxPalavras", 2))], check=True)
    pedacos = json.loads((vdir / "legendas.json").read_text())
    legendas = [{"bruto": p["ini"], "fim": p["fim"], "texto": p["texto"]} for p in pedacos]
    for comp in composicoes(a.projeto, v):
        d = props_get(comp); d["legendas"] = legendas
        props_grava(comp, d)
    print(f"{len(legendas)} pedaços nas composições da v{v}. Leia a lista acima: nada de pontuação nem maiúscula fora de nome.")


if __name__ == "__main__":
    main()
