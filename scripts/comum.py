"""Coisas que todos os scripts usam: pastas do projeto, projeto.json, tempo mm:ss, encoder de vídeo e as timelines
(defaultProps) em remotion/src/Composicoes.tsx (via scripts/props.mjs).

Layout de um projeto (tudo fora do git):
  trabalho/<projeto>/projeto.json         fontes, fps, offset da câmera B
  trabalho/<projeto>/proxy-a.mp4 ...      proxies (o bruto nunca é tocado)
  trabalho/<projeto>/voz.m4a              voz tratada (−16 LUFS)
  trabalho/<projeto>/palavras.json        transcrição por palavra (Whisper)
  trabalho/<projeto>/transcricao.md       a mesma, legível, com minutagem
  trabalho/<projeto>/vN/                  roteiro, frases, legendas, previews e exports da versão N
  remotion/public/<projeto>/              links (hardlink) para o que o Remotion lê
"""
import json, os, pathlib, re, shutil, subprocess, sys

RAIZ = pathlib.Path(__file__).resolve().parents[1]
TRABALHO = RAIZ / "trabalho"
PUBLIC = RAIZ / "remotion/public"
PROPS = RAIZ / "scripts/props.mjs"


def slug(nome):
    s = re.sub(r"[^a-z0-9-]+", "-", nome.lower()).strip("-")
    if not s: sys.exit("nome de projeto vazio")
    return s


def pasta(projeto):
    return TRABALHO / slug(projeto)


def ler_projeto(projeto):
    p = pasta(projeto) / "projeto.json"
    if not p.exists(): sys.exit(f"projeto {projeto} não existe: rode scripts/preparar.py primeiro")
    return json.loads(p.read_text())


def gravar_projeto(projeto, dados):
    (pasta(projeto) / "projeto.json").write_text(json.dumps(dados, ensure_ascii=False, indent=1))


def seg(t):
    """'mm:ss.s', 'hh:mm:ss.s' ou número → segundos"""
    if isinstance(t, (int, float)): return float(t)
    partes = [float(x) for x in str(t).replace(",", ".").split(":")]
    s = 0.0
    for x in partes: s = s * 60 + x
    return s


def mmss(s):
    m, r = divmod(max(0.0, s), 60)
    return f"{int(m):02d}:{r:04.1f}"


def ffprobe(arq):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate:format=duration",
                        "-of", "json", str(arq)], capture_output=True, text=True, check=True)
    d = json.loads(r.stdout)
    v = next((s for s in d["streams"] if s["codec_type"] == "video"), None)
    a = any(s["codec_type"] == "audio" for s in d["streams"])
    fps = None
    if v:
        n, dd = v["r_frame_rate"].split("/"); fps = float(n) / float(dd)
    return {"duracao": float(d["format"]["duration"]), "largura": v and v["width"], "altura": v and v["height"],
            "fps": fps, "audio": a}


_enc = None


def encoder():
    """O encoder de vídeo da máquina: NVENC (NVIDIA), VideoToolbox (Mac) ou x264 (CPU). Testa de verdade: o ffmpeg
    pode listar NVENC sem GPU."""
    global _enc
    if _enc: return _enc
    if os.environ.get("ENCODER") == "x264":
        _enc = ["-c:v", "libx264", "-preset", "fast", "-crf", "17"]; return _enc
    lista = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True).stdout
    for nome, args in (("h264_nvenc", ["-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "18", "-b:v", "0"]),
                       ("h264_videotoolbox", ["-c:v", "h264_videotoolbox", "-q:v", "70"])):
        if nome in lista:
            ok = subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "color=s=256x256:d=0.2", *args, "-f", "null", "-"],
                                capture_output=True).returncode == 0
            if ok:
                _enc = args; return _enc
    _enc = ["-c:v", "libx264", "-preset", "fast", "-crf", "17"]
    return _enc


def publicar(projeto, origem, nome):
    """põe um arquivo em remotion/public/<projeto>/ (hardlink: link simbólico some no bundle do render)"""
    dest = PUBLIC / slug(projeto) / nome
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() or dest.is_symlink(): dest.unlink()
    try:
        os.link(origem, dest)
    except OSError:
        shutil.copy2(origem, dest)  # outro disco: cópia
    return f"{slug(projeto)}/{nome}"


def props_get(comp):
    r = subprocess.run(["node", str(PROPS), "get", comp], capture_output=True, text=True)
    if r.returncode: sys.exit(r.stderr.strip())
    return json.loads(r.stdout)


def props_grava(comp, dados, novo=False):
    tmp = TRABALHO / ".props-tmp.json"
    tmp.parent.mkdir(exist_ok=True)
    tmp.write_text(json.dumps(dados, ensure_ascii=False))
    r = subprocess.run(["node", str(PROPS), "add" if novo else "set", comp, str(tmp)], capture_output=True, text=True)
    tmp.unlink()
    if r.returncode: sys.exit(r.stderr.strip())


def composicoes(projeto, versao):
    return [f"Teaser16x9-{slug(projeto)}-v{versao}", f"Teaser9x16-{slug(projeto)}-v{versao}"]


def versao_arg(v):
    return int(str(v).lstrip("vV"))
