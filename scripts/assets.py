"""Inventário dos assets fornecidos (B-roll, fotos, logos, telas, cartela, trilha) de um projeto. O editor não gera
asset: ele usa o que está em trabalho/<projeto>/assets/ (exportado da skill de design, do design system da marca ou
entregue pelo time).

  python3 scripts/assets.py <projeto>

Lê trabalho/<projeto>/assets/, grava trabalho/<projeto>/assets.json (tipo, dimensão, duração, transparência) e põe
cada arquivo em remotion/public/<projeto>/assets/ (hardlink). Rodado também pelo preparar.py e pelo montar-timeline.py.
"""
import json, subprocess, sys
from comum import pasta, publicar, slug

IMAGEM = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".avif"}
VIDEO = {".mp4", ".mov", ".m4v", ".webm", ".mkv"}
AUDIO = {".mp3", ".m4a", ".wav", ".aac", ".flac", ".ogg"}


def sonda(arq):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,pix_fmt:format=duration",
                        "-of", "json", str(arq)], capture_output=True, text=True)
    if r.returncode: return None
    return json.loads(r.stdout)


def inventariar(projeto, silencioso=False):
    dir_ = pasta(projeto) / "assets"
    dir_.mkdir(parents=True, exist_ok=True)
    itens = {}
    for arq in sorted(p for p in dir_.rglob("*") if p.is_file() and not p.name.startswith(".")):
        ext = arq.suffix.lower()
        tipo = "imagem" if ext in IMAGEM else "video" if ext in VIDEO else "audio" if ext in AUDIO else None
        if not tipo: continue
        d = sonda(arq)
        if not d: print(f"não li: {arq.name}", file=sys.stderr); continue
        v = next((s for s in d["streams"] if s["codec_type"] == "video"), {})
        dur = float(d.get("format", {}).get("duration") or 0) if tipo != "imagem" else 0.0
        pix = v.get("pix_fmt", "")
        alfa = any(x in pix for x in ("rgba", "yuva", "argb", "bgra", "ya8", "ya16", "gbrap")) or (pix == "pal8" and ext == ".png")
        nome = str(arq.relative_to(dir_))
        itens[nome] = {"tipo": tipo, "arquivo": publicar(projeto, arq, f"assets/{nome}"), "largura": v.get("width"),
                       "altura": v.get("height"), "duracao": round(dur, 2), "alfa": alfa}
    (pasta(projeto) / "assets.json").write_text(json.dumps(itens, ensure_ascii=False, indent=1))
    if not silencioso:
        if not itens: print(f"nenhum asset em {dir_}")
        for n, i in itens.items():
            dim = f"{i['largura']}×{i['altura']}" if i["largura"] else "—"
            print(f"  {n:32} {i['tipo']:6} {dim:>10} {i['duracao']:6.1f} s {'transparente' if i['alfa'] else ''}")
    return itens


if __name__ == "__main__":
    inventariar(sys.argv[1])
