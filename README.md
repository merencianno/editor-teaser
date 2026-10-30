# editor-teaser

Um repositório para o Claude Code editar teasers de **talking head** (uma pessoa falando para a câmera). Você clona,
joga o vídeo bruto e diz **"vamos editar"**. O Claude transcreve, propõe roteiros em texto, monta a timeline num
projeto [Remotion](https://www.remotion.dev/) que você ajusta num painel, mostra um preview leve e só então exporta:

- **teaser 16:9** (site, YouTube, apresentação);
- **vertical 9:16** (Reels, TikTok, Shorts) com legenda palavra a palavra no padrão aprovado.

Você revisa e decide; ele corta, alinha, mede e renderiza.

## Por que é assim

Cada regra abaixo veio de um corte reprovado ou de uma fonte de editor (as fontes estão nas skills).

- **Roteiro AIDA antes de tudo** (atenção, interesse, desejo, ação), com **gancho nos primeiros 5 s falando com quem
  assiste**. Um trailer reordena falas de um bruto longo para caber num arco de 1–2 min; sem estrutura vira uma lista
  de frases bonitas que ninguém acompanha.
- **Blocos longos, de 8 a 20 s**, com o pensamento inteiro. A primeira tentativa, uma colcha de frases de 2 s tiradas de
  pontos diferentes, foi reprovada: a voz pula de tom e a fala perde continuidade. Poucos cortes, escondidos.
- **Zoom 100 / 107,5 % e punch-in de 115 % só na frase-chave.** Pular de 100 para 170 % a cada corte parecia rotação e
  cansava. Cena nova abre a 100 %; jump cut alterna 100/107,5.
- **Push-in lento de 5–10 % com easing**, nas aberturas de ideia e na frase-chave; o resto quase parado.
- **Respiro só nos 3–4 momentos pesados** (revelação, sorriso, pausa emocionada). Nos outros, a pausa natural da fala.
- **A música manda no ritmo** e o **hit cai na frase-chave**; trilha baixa sob a voz (ducking), rampas sem degrau, a
  música cai para uma frase soar sozinha (turn line). Sem trilha não há corte "épico" para aprovar.
- **Legenda de no máximo 2 palavras**, no tempo exato da fala (alinhamento forçado, não o tempo do Whisper), sem
  animação, minúscula e sem pontuação, na altura do pescoço. Legenda grande tapando a boca e animação de entrada foram
  reprovadas.
- **Três portões: texto → preview → export.** O roteiro é aprovado em texto; o vídeo, num preview 480p dos proxies
  (minutos); o export final só depois. Exportar sem preview já custou uma hora de render.
- **O bruto nunca é alterado; versão nova nunca sobrescreve; nada pesado no git.**

## Instalação

Feito e testado em **Linux com GPU NVIDIA** (Whisper em CUDA, proxies em NVENC). Mac: veja o fim deste arquivo.

1. Ferramentas: `ffmpeg`, `node` ≥ 18 (com `npm`), [`uv`](https://docs.astral.sh/uv/) e o Claude Code.
   Driver NVIDIA instalado para usar a GPU (as bibliotecas CUDA do Whisper vêm pelo próprio `uv`).
2. ```bash
   git clone <este repositório> editor-teaser && cd editor-teaser
   bash scripts/setup.sh            # confere as ferramentas, instala o Remotion
   bash scripts/setup.sh --aquecer  # opcional: já baixa o Whisper large-v3 (~3 GB) e o alinhador (~1,2 GB)
   ```

## Primeiro uso

```bash
claude
> vamos editar ~/Videos/bruto-entrevista.mp4
```

O que acontece (skill `editar-teaser`):

1. **Preparar:** proxy 1080p com quadro-chave a cada 15 quadros, voz em −16 LUFS, tudo em `trabalho/<projeto>/`.
2. **Transcrever** por palavra (faster-whisper large-v3). Ele pergunta pela trilha e pelo texto da cartela final.
3. **Portão 1:** 2–3 roteiros AIDA em texto, com minutagem de cada fala, frase-chave, imagem e música por bloco.
   Você escolhe e ajusta no texto.
4. **Montar:** a versão `v1` vira duas composições, `Teaser16x9-<projeto>-v1` e `Teaser9x16-<projeto>-v1`, com
   legenda alinhada e o recorte vertical seguindo o rosto.
5. **Studio:** ele abre o Remotion Studio (`http://localhost:3123`). Aba **Props** à direita: cada plano (`de`/`ate` no
   bruto, câmera, zoom, push), cada pedaço de legenda, volumes da música e textos da cartela são campos; o vídeo muda
   na hora; o botão de salvar grava.
6. **Portão 2:** preview 480p dos dois formatos em `trabalho/<projeto>/v1/`. Você assiste e diz "pode exportar" (ou o
   que mudar).
7. **Export:** 1080p (ou 2K/4K, se o bruto tiver resolução) em `trabalho/<projeto>/v1/final-*.mp4`.

Referência nova de estilo ("quero a legenda desse reel"): mande o vídeo ou o link; a skill `nova-referencia` mede o que
ele faz e cria uma skill irmã (ex.: `legenda-documentario`) sem mexer na padrão, e pede o seu ok antes de usar.

### Comandos, se quiser rodar à mão

```bash
python3 scripts/preparar.py meu-teaser ~/Videos/bruto.mp4 --musica ~/Musicas/trilha.mp3
uv run --no-project --with faster-whisper --with nvidia-cublas-cu12 --with "nvidia-cudnn-cu12==9.*" \
  python scripts/transcrever.py meu-teaser
# escreva trabalho/meu-teaser/roteiro.json (modelo: exemplos/roteiro-exemplo.json)
bash scripts/montar.sh meu-teaser trabalho/meu-teaser/roteiro.json
bash scripts/studio.sh
bash scripts/preview.sh meu-teaser v1
echo "2026-01-01 · 'pode exportar'" > trabalho/meu-teaser/v1/APROVADO
bash scripts/export.sh meu-teaser v1 1080
```

Segunda câmera: `uv run --no-project --with numpy python scripts/sincronizar.py meu-teaser ~/Videos/camera-b.mp4`
antes de montar; as versões seguintes alternam as câmeras em toda emenda.

### Tempos medidos (Linux, Ryzen 7 1800X + RTX 3060 Ti, bruto 1080p de 75 s, teaser de 35 s)

| etapa | tempo |
|---|---|
| `setup.sh` (com cache do npm) | 5 s |
| `preparar.py` (proxy NVENC + voz) | 17 s |
| `transcrever.py` (large-v3, CUDA int8, modelo já baixado) | 15 s |
| `montar.sh` (timeline + alinhamento da legenda na CPU + rostos) | 18–24 s |
| Studio no ar | ~3 s + 3 s de build |
| `preview.sh`, os dois formatos em 480p | 2 min 34 s (~75 s cada) |
| `export.sh` 1080p, um formato | 79 s |

Primeira vez soma o download dos modelos (Whisper ~3 GB, alinhador ~1,2 GB) e dos pacotes do `uv`. O render escala
com a duração: um teaser de 2 min leva ~4–5 min de preview por formato e ~5 min de export 1080p por formato nessa
máquina; 4K, bem mais.

## Estrutura

```
README.md · CLAUDE.md · LICENSE (MIT)
.claude/skills/
  editar-teaser/     fluxo mestre com os portões
  roteiro-aida/      gancho, blocos longos, ordem do roteiro, fala conferida, 2–3 roteiros em texto
  ritmo-e-corte/     corte, câmera, tamanho, zoom, atraso da imagem, crop de 4K (com fontes)
  som-e-musica/      voz −16 LUFS, ducking, rampas, hit, turn line, licença
  cor-e-pele/        primária, casar câmeras pela pele, 45–70 IRE, arco frio → quente
  legenda-vertical/  o padrão aprovado (scripts alinhar/quebrar + componente de referência)
  nova-referencia/   referência → skill irmã medida, com ok antes de usar
  design-da-peca/    tipografia por formato, um destaque, sem enfeite de IA, áreas seguras, cartela < 3 s
remotion/            template: Teaser.tsx (16:9 e 9:16 da mesma timeline), schema.ts (painel Props), legendas/
                     public/ e src/Composicoes.tsx são gerados e ficam fora do git
scripts/             preparar, transcrever, falas, sincronizar, montar-timeline, legendas, rostos, montar.sh,
                     props.mjs, studio.sh, preview.sh, export.sh, musica-picos, conferir-quadros
exemplos/            roteiro em texto, roteiro.json e frases fictícios (curso de horta em apartamento)
trabalho/            (fora do git) um diretório por projeto: proxies, voz, transcrição, versões, previews, exports
```

## Créditos

A lógica de "o Claude como primeiro editor" (decidir o que fica pela transcrição, palavra por palavra; bordas de corte
ajustadas à pausa; alternância de zoom em jump cut; envelope de música; relatório curto no fim) foi inspirada no
pacote [appariciojunior/video-editor-skills](https://github.com/appariciojunior/video-editor-skills), que ensina o
Claude Code a editar no DaVinci Resolve. Ele é licenciado em **CC BY-NC 4.0**; nada do texto nem do código dele foi
copiado para cá: as regras foram reescritas com outras palavras, trocando o motor por ffmpeg + Remotion. Vale a
leitura.

As regras de corte, som e cor citam as fontes públicas nas próprias skills (No Film School,
PremiumBeat, Sound On Sound, Creative COW, wolfcrow, entre outras).

Licença deste repositório: MIT.

## Adaptações para Mac (Apple Silicon)

> **Não testado.** Tudo acima foi feito e medido em Linux com GPU NVIDIA. O que segue é o que muda no Mac, pelo que as
> ferramentas documentam; confira no primeiro uso e corrija aqui.

- **Instalação:** `brew install ffmpeg uv node`. O `setup.sh` é o mesmo.
- **Encoder dos proxies:** `scripts/comum.py` testa NVENC, depois **`h264_videotoolbox`** e por fim x264; no Mac fica
  VideoToolbox sozinho. Para a fonte do export de um bruto 4K, `hevc_videotoolbox` gera arquivos menores
  (troque em `encoder()` se o disco apertar). `ENCODER=x264` força a CPU se o VideoToolbox der problema.
- **Whisper:** sem CUDA. Duas opções:
  - CPU int8 (o padrão sem GPU): `uv run --no-project --with faster-whisper python scripts/transcrever.py <projeto> --cpu`.
    Large-v3 na CPU de um M1/M2 deve levar da ordem do tempo real (20 min de fala ≈ 15–30 min). Para ir mais rápido,
    `--modelo large-v3-turbo` ou `--modelo medium` (perde um pouco em nome próprio).
  - **mlx-whisper** na GPU do Mac: `uv run --no-project --with mlx-whisper python scripts/transcrever.py <projeto> --motor mlx`
    (bem mais rápido que a CPU; mesmo formato de saída).
  - Não use os pacotes `nvidia-*` no comando: eles não existem para Mac e o `uv` falha.
- **Alinhamento da legenda (torch):** roda na CPU, que basta (~10–20 s por minuto de fala). No Mac o `legendas.py` não
  usa o índice CPU do PyTorch (o torch do PyPI já é CPU/MPS). `device="mps"` no `alinhar.py` é possível, mas não foi
  necessário nem testado.
- **Render (Remotion):** igual; o Chrome headless baixa a versão arm64. O render usa CPU; num M-series de 8–10 núcleos
  espere algo parecido com os tempos acima (preview em minutos, export 1080p de 1 min em ~5–15 min). Ajuste
  `CONCORRENCIA` (padrão: metade dos núcleos) se o Mac esquentar ou o conferidor acusar quadros repetidos. O Remotion tem
  `--hardware-acceleration=if-possible` (VideoToolbox) para o encode final no Mac; não está ligado no `export.sh`
  porque não foi testado com `--crf`.
- **Disco:** `trabalho/` cresce rápido (proxy 1080p ≈ 1 GB por 15 min; fonte 4K ≈ 5–7 GB por 20 min). Hardlinks
  funcionam no APFS; em disco externo o script copia.
