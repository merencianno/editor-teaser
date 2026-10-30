"""Abre um projeto a partir do bruto: proxy de edição, voz tratada e (se o bruto for maior que 1080p) a fonte do
export final. O bruto nunca é alterado: tudo sai em trabalho/<projeto>/.

  python3 scripts/preparar.py <projeto> <bruto.mp4> [--musica trilha.mp3] [--tirar-ar] [--forcar]
  python3 scripts/preparar.py <projeto> --musica trilha.mp3      (só acrescenta a trilha a um projeto existente)

- proxy-a.mp4: 1080p, quadro-chave a cada 15 quadros (o Studio e o render andam rápido; GOP longo de câmera deixa o
  render minutos por quadro), encoder da máquina (NVENC, VideoToolbox ou x264).
- final-a.mp4: só quando o bruto tem mais de 1080 de altura; mesma resolução do bruto, GOP 15. Usado no export.
- voz.m4a: o áudio do bruto em −16 LUFS (loudnorm). --tirar-ar passa um redutor de ruído leve (afftdn) antes.
A segunda câmera entra depois, com scripts/sincronizar.py.
"""
import argparse, json, subprocess, sys
from comum import encoder, ffprobe, gravar_projeto, pasta, publicar, slug


def proxy(origem, destino, fps, altura=1080):
    vf = f"scale=-2:{altura}:flags=lanczos,fps={fps}" if altura else f"fps={fps}"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-stats", "-y", "-i", str(origem), "-vf", vf, "-an", *encoder(),
                    "-g", "15", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(destino)], check=True)


def voz(origem, destino, tirar_ar=False):
    af = ("afftdn=nr=10:nf=-40," if tirar_ar else "") + "loudnorm=I=-16:TP=-1.5:LRA=11"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(origem), "-vn", "-ac", "1", "-ar", "48000",
                    "-af", af, "-c:a", "aac", "-b:a", "192k", str(destino)], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("projeto"); ap.add_argument("bruto", nargs="?")
    ap.add_argument("--musica"); ap.add_argument("--tirar-ar", action="store_true"); ap.add_argument("--forcar", action="store_true")
    a = ap.parse_args()
    dir_ = pasta(a.projeto); dir_.mkdir(parents=True, exist_ok=True)
    pj = dir_ / "projeto.json"
    dados = json.loads(pj.read_text()) if pj.exists() else None

    if a.bruto:
        if dados and not a.forcar:
            sys.exit(f"{pj} já existe. Para trocar o bruto use --forcar (as versões já montadas continuam apontando para ele).")
        info = ffprobe(a.bruto)
        if not info["audio"]: sys.exit("o bruto não tem áudio: a voz precisa vir dele (ou da câmera que gravou o som)")
        fps = round(info["fps"] or 30)
        print(f"bruto: {info['largura']}×{info['altura']}, {info['fps']:.3f} fps, {info['duracao']:.1f} s → composição a {fps} fps")
        print("proxy 1080p…"); proxy(a.bruto, dir_ / "proxy-a.mp4", fps)
        final = ""
        if (info["altura"] or 0) > 1080:
            print(f"fonte do export ({info['altura']}p, GOP 15)…"); proxy(a.bruto, dir_ / "final-a.mp4", fps, altura=None)
            final = publicar(a.projeto, dir_ / "final-a.mp4", "final-a.mp4")
        print("voz −16 LUFS…"); voz(a.bruto, dir_ / "voz.m4a", a.tirar_ar)
        dados = {"projeto": slug(a.projeto), "fps": fps, "duracao": info["duracao"],
                 "brutos": {"a": str(pathlib_abs(a.bruto))},
                 "fontes": {"voz": publicar(a.projeto, dir_ / "voz.m4a", "voz.m4a"),
                            "a": {"arquivo": publicar(a.projeto, dir_ / "proxy-a.mp4", "proxy-a.mp4"), "arquivoFinal": final, "offset": 0.0}},
                 "musica": ""}
    if not dados: sys.exit("informe o bruto")
    if a.musica:
        import pathlib, shutil
        ext = pathlib.Path(a.musica).suffix.lower() or ".mp3"
        shutil.copy2(a.musica, dir_ / f"musica{ext}")
        dados["musica"] = publicar(a.projeto, dir_ / f"musica{ext}", f"musica{ext}")
        print(f"trilha: {dados['musica']}")
    gravar_projeto(a.projeto, dados)
    print(f"pronto: {pj}")


def pathlib_abs(p):
    import pathlib
    return pathlib.Path(p).expanduser().resolve()


if __name__ == "__main__":
    main()
