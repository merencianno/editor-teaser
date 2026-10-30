# editor-teaser

**Este editor não escreve a copy nem cria os assets; ele edita.** É um repositório para o Claude Code editar teasers
de **talking head** (uma pessoa falando para a câmera): você entrega o vídeo bruto, o roteiro ou a copy já aprovada e
os assets (B-roll, fotos, logo, trilha), e diz **"vamos editar"**. O Claude acha cada fala do roteiro no melhor take,
encaixa os assets, monta a timeline num projeto [Remotion](https://www.remotion.dev/) que você ajusta num painel,
mostra um preview leve e só então exporta:

- **teaser 16:9** (site, YouTube, apresentação);
- **vertical 9:16** (Reels, TikTok, Shorts) com legenda palavra a palavra no padrão aprovado.

**Você não precisa de terminal.** O Claude roda tudo e abre o Studio, os previews e as pastas para você; você só
conversa e aprova.

**Primeira vez? Comece pelo [TUTORIAL.md](TUTORIAL.md)** (passo a passo no Mac, da instalação ao export).

## O que vem de fora

| o quê | de onde vem | o editor faz |
|---|---|---|
| roteiro / copy | skill de copy ou roteiro, ou o time (texto, .md, .docx) | acha cada fala nos takes do bruto, monta a ordem, aponta o que falta |
| B-roll, fotos, telas, logo, cartela desenhada | skill de design, design system da sua marca, ou o time | corta pela ação, posiciona, recorta para o 9:16, move com sutileza |
| trilha | biblioteca licenciada ou o time | põe o hit na frase-chave, faz o ducking e as rampas |

Faltou um asset? O Claude escreve `trabalho/<projeto>/assets-pedido.md` (o quê, para qual fala, formato, duração) para
você pedir a quem faz. Ele não gera B-roll, imagem, logo nem música. Sem roteiro, ele pode propor um rascunho em AIDA a
partir das falas, avisando que o ideal é o roteiro vir da skill de copy.

## Por que é assim

Cada regra abaixo veio de um corte reprovado ou de uma fonte de editor (as fontes estão nas skills).

- **Roteiro no bruto antes de tudo.** O roteiro aprovado vira um mapa: cada fala → o melhor take (texto fiel,
  Whisper seguro, sem tropeço) → minutagem e duração, com o áudio de cada take para ouvir, e o que o roteiro pede e o
  bruto não tem. O AIDA (gancho nos primeiros 5 s falando com quem assiste, frase-chave, CTA) vira checagem de
  estrutura.
- **Blocos longos, de 8 a 20 s**, com o pensamento inteiro. Uma colcha de frases de 2 s tiradas de pontos diferentes
  foi reprovada: a voz pula de tom e a fala perde continuidade. Poucos cortes, escondidos (troca de tamanho ou B-roll).
- **Zoom 100 / 107,5 % e punch-in de 115 % só na frase-chave.** Pular de 100 para 170 % a cada corte parecia rotação e
  cansava. Cena nova abre a 100 %; jump cut alterna 100/107,5.
- **Push-in lento de 5–10 % com easing**, nas aberturas de ideia, na frase-chave e nas fotos paradas; o resto quase
  parado.
- **B-roll cortado pela ação do clipe**, não por duração fixa: corte de 2–4 s, sequência de 6–8 s, ancorado na palavra
  que ilustra, sem cobrir a frase-chave nem o respiro, com rosto e legenda livres.
- **Respiro só nos 3–4 momentos pesados** (revelação, sorriso, pausa emocionada).
- **A música manda no ritmo** e o **hit cai na frase-chave**; ducking sob a voz, rampas sem degrau, turn line.
- **Legenda de no máximo 2 palavras**, no tempo exato da fala (alinhamento forçado), sem animação, minúscula e sem
  pontuação, na altura do pescoço. Legenda grande tapando a boca e animação de entrada foram reprovadas.
- **Portões: roteiro no bruto → preview → export.** O vídeo é aprovado num preview 480p dos proxies (minutos); o
  export final só depois. Exportar sem preview já custou uma hora de render.
- **O bruto nunca é alterado; versão nova nunca sobrescreve; nada pesado no git.**

## Como é o uso

Tudo acontece numa conversa com o Claude (o [TUTORIAL.md](TUTORIAL.md) tem as frases para mandar):

1. **Instalar:** "instala o editor-teaser pra mim…" (uma vez). No Mac, antes, o instalador .pkg do Homebrew.
2. **Começar:** "vamos editar" + o vídeo, o roteiro aprovado, os assets e a trilha.
3. **Portão 1 · roteiro no bruto:** ele mostra o mapa (fala → take → minutagem → duração, onde entram corte, respiro e
   hit) e abre a pasta com o áudio de cada take para você ouvir. Você aprova ou troca takes.
4. **Montagem e Studio:** ele monta `Teaser16x9-<projeto>-vN` e `Teaser9x16-<projeto>-vN` e abre o Remotion Studio no
   navegador. Aba **Props** à direita: planos (`segmentos`), B-roll (`insercoes`), legenda, música e cartela são
   campos. Ou só peça: "logo menor", "a legenda das 0:12 está adiantada".
5. **Portão 2 · preview:** ele renderiza os dois formatos em 480p e abre os arquivos. Você assiste e diz "pode
   exportar" (ou o que mudar).
6. **Export:** 1080p (ou 2K/4K, se o bruto tiver resolução), e ele abre a pasta do resultado.

Referência nova de estilo ("quero a legenda desse reel"): a skill `nova-referencia` mede o que ela faz e cria uma
skill irmã (ex.: `legenda-documentario`) sem mexer na padrão, e pede o seu ok antes de usar.

## Para quem prefere o terminal

Nada disso é necessário para usar com o Claude; é o mesmo fluxo à mão.

Ferramentas: `ffmpeg`, `node` ≥ 18 (com `npm`), [`uv`](https://docs.astral.sh/uv/), `git`. GPU NVIDIA opcional (o
Whisper usa CUDA; as bibliotecas vêm pelo próprio `uv`).

```bash
git clone https://github.com/merencianno/editor-teaser.git ~/editor-teaser && cd ~/editor-teaser
bash scripts/setup.sh --aquecer                       # ferramentas, Remotion e modelos (~4 GB, uma vez)

# assets fornecidos em trabalho/meu-teaser/assets/
python3 scripts/preparar.py meu-teaser ~/Videos/bruto.mp4 --musica ~/Musicas/trilha.mp3
bash scripts/transcrever.sh meu-teaser
python3 scripts/mapear-roteiro.py meu-teaser ~/Documentos/roteiro-aprovado.md   # portão 1
# complete trabalho/meu-teaser/roteiro.json a partir do roteiro-rascunho.json (modelo: exemplos/roteiro-exemplo.json)
bash scripts/montar.sh meu-teaser trabalho/meu-teaser/roteiro.json
bash scripts/studio.sh                                # abre http://localhost:3123
bash scripts/preview.sh meu-teaser v1                 # portão 2
echo "2026-01-01 · 'pode exportar'" > trabalho/meu-teaser/v1/APROVADO
bash scripts/export.sh meu-teaser v1 1080
```

Segunda câmera: `uv run --no-project --with numpy python scripts/sincronizar.py meu-teaser ~/Videos/camera-b.mp4`
antes de montar; as versões seguintes alternam as câmeras em toda emenda. `ABRIR=0` nos scripts evita que eles abram
navegador e player.

### Tempos medidos (Linux, Ryzen 7 1800X + RTX 3060 Ti, bruto 1080p de 75 s, teaser de ~30 s com 2 inserções)

| etapa | tempo |
|---|---|
| `setup.sh` (com cache do npm) | 5–7 s |
| `preparar.py` (proxy NVENC + voz + inventário de assets) | 15–17 s |
| `transcrever.sh` (large-v3, CUDA int8, modelo já baixado) | 15–18 s |
| `mapear-roteiro.py` (7 falas, áudio de cada take) | 1 s |
| `montar.sh` (timeline + inserções + alinhamento da legenda na CPU + rosto, luz e foco) | 18–24 s |
| Studio no ar | ~3 s + 3,5 s de build |
| `preview.sh`, os dois formatos em 480p | 2 min 30 s – 2 min 50 s (~80 s cada) |
| `export.sh` 1080p, um formato (teaser de 35 s) | 79 s |

Primeira vez soma o download dos modelos (Whisper ~3 GB, alinhador ~1,2 GB) e dos pacotes do `uv`. O render escala
com a duração: um teaser de 2 min leva ~4–5 min de preview por formato e ~5 min de export 1080p por formato nessa
máquina; 4K, bem mais.

## Estrutura

```
README.md · TUTORIAL.md · CLAUDE.md · LICENSE (MIT)
.claude/skills/
  editar-teaser/     fluxo mestre com os portões
  roteiro-no-bruto/  roteiro/copy aprovado → melhor take de cada fala, mapa, o que falta; AIDA como checagem e plano B
  assets-e-broll/    inventário, inserções ancoradas na fala, regras de B-roll, pedido do que falta (não gera)
  ritmo-e-corte/     corte, câmera, tamanho, zoom, atraso da imagem, crop de 4K (com fontes)
  som-e-musica/      voz −16 LUFS, ducking, rampas, hit, turn line, licença
  cor-e-pele/        primária, casar câmeras pela pele, 45–70 IRE, arco frio → quente
  legenda-vertical/  o padrão aprovado (scripts alinhar/quebrar + componente de referência)
  nova-referencia/   referência → skill irmã medida, com ok antes de usar
  design-da-peca/    tipografia da legenda e da cartela, áreas seguras, sem enfeite de IA (não cria identidade)
remotion/            template: Teaser.tsx (16:9 e 9:16 da mesma timeline), schema.ts (painel Props), legendas/
                     public/ e src/Composicoes.tsx são gerados e ficam fora do git
scripts/             setup, preparar, transcrever(.sh), mapear-roteiro, assets, falas, sincronizar, montar-timeline,
                     legendas, rostos, montar.sh, props.mjs, studio.sh, preview.sh, export.sh, abrir.sh,
                     musica-picos, conferir-quadros
exemplos/            copy de entrada, roteiro.json com inserções, roteiros AIDA (plano B) e frases, todos fictícios
trabalho/            (fora do git) um diretório por projeto: assets/, proxies, voz, transcrição, mapa, versões,
                     previews, exports
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
> ferramentas documentam; confira no primeiro uso e corrija aqui (peça ao Claude: "anota isso nas Adaptações para Mac").

- **Homebrew sem terminal:** o instalador oficial em linha de comando pede a senha de administrador, e o Claude não
  digita senha. Use o **instalador .pkg** em [github.com/Homebrew/brew/releases/latest](https://github.com/Homebrew/brew/releases/latest)
  (baixe o `Homebrew-….pkg`, duplo clique, senha na janela do macOS). Se o macOS pedir as **Ferramentas de Linha de
  Comando**, clique em Instalar. Depois disso o `setup.sh` instala `ffmpeg uv node git` pelo `brew` sozinho (sem senha).
- **Encoder dos proxies:** `scripts/comum.py` testa NVENC, depois **`h264_videotoolbox`** e por fim x264; no Mac fica
  VideoToolbox sozinho. Para a fonte do export de um bruto 4K, `hevc_videotoolbox` gera arquivos menores
  (troque em `encoder()` se o disco apertar). `ENCODER=x264` força a CPU se o VideoToolbox der problema.
- **Whisper:** sem CUDA. O `scripts/transcrever.sh` escolhe sozinho o **mlx-whisper** (GPU do Mac, modelo
  `mlx-community/whisper-large-v3-mlx`, baixado pelo `setup.sh --aquecer`). Alternativa: CPU int8
  (`transcrever.py --cpu`), da ordem do tempo real num M1/M2 (20 min de fala ≈ 15–30 min); `--modelo large-v3-turbo`
  acelera. Os pacotes `nvidia-*` não existem para Mac e não entram no comando.
- **Alinhamento da legenda (torch):** roda na CPU, que basta (~10–20 s por minuto de fala). No Mac o `legendas.py` não
  usa o índice CPU do PyTorch (o torch do PyPI já é CPU/MPS).
- **Abrir coisas:** `scripts/abrir.sh` usa `open` (Studio no navegador padrão, previews no QuickTime, pastas no Finder).
- **Render (Remotion):** igual; o Chrome headless baixa a versão arm64. O render usa CPU; num M-series de 8–10 núcleos
  espere algo parecido com os tempos acima. Ajuste `CONCORRENCIA` (padrão: metade dos núcleos) se o Mac esquentar ou o
  conferidor acusar quadros repetidos. O Remotion tem `--hardware-acceleration=if-possible` (VideoToolbox) para o
  encode final no Mac; não está ligado no `export.sh` porque não foi testado com `--crf`.
- **Disco:** `trabalho/` cresce rápido (proxy 1080p ≈ 1 GB por 15 min; fonte 4K ≈ 5–7 GB por 20 min). Hardlinks
  funcionam no APFS; em disco externo o script copia.
