#!/usr/bin/env bash
# Export final de uma versão. Só roda depois de o dono aprovar o preview (portão 2): o Claude grava o ok dele em
# trabalho/<projeto>/vN/APROVADO (data + frase literal). Nunca sobrescreve um export já feito.
#   bash scripts/export.sh <projeto> <vN> [1080|2k|4k] [16x9|9x16|ambos]
set -euo pipefail
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"; cd "$RAIZ"
proj="$1"; v="${2#v}"; v="${v#V}"; res="${3:-1080}"; quais="${4:-ambos}"
dir="$RAIZ/trabalho/$proj/v$v"
[ -f "$dir/APROVADO" ] || { echo "PARADO: sem $dir/APROVADO. Mostre o preview (scripts/preview.sh) e espere o ok do dono."; exit 1; }
case "$res" in 1080) esc=1;; 2k) esc=1.3333333333;; 4k) esc=2;; *) echo "resolução: 1080, 2k ou 4k"; exit 1;; esac
mkdir -p "$RAIZ/trabalho/tmp"; export TMPDIR="$RAIZ/trabalho/tmp"
CONC="${CONCORRENCIA:-$(( $(getconf _NPROCESSORS_ONLN) / 2 ))}"
for fmt in 16x9 9x16; do
  [ "$quais" = ambos ] || [ "$quais" = "$fmt" ] || continue
  id="Teaser$fmt-$proj-v$v"; saida="$dir/final-$fmt-$res.mp4"
  [ -e "$saida" ] && { echo "já existe, não sobrescrevo: $saida"; continue; }
  node scripts/props.mjs get "$id" | node -e 'let s="";process.stdin.on("data",d=>s+=d).on("end",()=>{const p=JSON.parse(s);
    p.fontes.usarFinal=true; const sem=Object.entries(p.cameras).filter(([,c])=>!c.arquivoFinal).map(([k])=>k);
    if (sem.length && process.argv[1]!=="1") console.error("aviso: câmera "+sem.join(",")+" sem fonte maior que 1080p; o "+process.argv[2]+" sai ampliado do proxy");
    process.stdout.write(JSON.stringify(p))})' "$esc" "$res" > "$dir/.props-export-$fmt.json"
  t0=$(date +%s)
  (cd remotion && npx remotion render src/index.ts "$id" "$saida" --props="$dir/.props-export-$fmt.json" --scale="$esc" \
     --crf=16 --concurrency="$CONC" --log=error)
  echo "final $fmt $res: $saida ($(( $(date +%s) - t0 )) s)"
  python3 scripts/conferir-quadros.py "$saida" || echo "AVISO: quadros repetidos; rode de novo com CONCORRENCIA=3 (apague o arquivo antes)"
done
