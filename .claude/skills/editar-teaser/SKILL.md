---
name: editar-teaser
description: Fluxo mestre para editar um teaser ou trailer a partir de um vídeo bruto de talking head (uma pessoa falando para a câmera), em 16:9 e em 9:16 com legenda palavra a palavra. Transcreve, propõe roteiros AIDA em texto (portão 1), monta a timeline no Remotion e abre o Studio, renderiza um preview 480p (portão 2) e só então exporta. Use quando o usuário disser "vamos editar", "edita esse vídeo", "faz um teaser/trailer/reel desse bruto", jogar um .mp4/.mov de alguém falando, ou pedir uma versão nova de um teaser já montado.
---

# Editar teaser (fluxo mestre)

Você é o primeiro editor. O dono do vídeo (quem pediu) revisa e aprova; **só ele declara que está pronto**. Gate
verde, render sem erro ou "ficou bom" de passagem não são aprovação.

Os dois portões não se pulam:

1. **Portão 1, texto:** roteiro AIDA em texto, aprovado antes de qualquer render.
2. **Portão 2, preview:** preview 480p dos proxies, aprovado antes de qualquer export.

Exportar sem preview já custou uma hora de render jogada fora por causa de uma legenda ruim. Qualquer mudança depois
de um preview aprovado volta para um preview novo.

## Regras da casa

- O bruto **nunca** é alterado. Tudo sai em `trabalho/<projeto>/` (fora do git). Nada pesado entra no git.
- Versão nova nunca sobrescreve: cada roteiro montado vira `vN` novo; export existente nunca é regravado.
- Uma pergunta por vez, curta. Ajuste de ofício (corte meio quadro antes, rosto mais centrado) você decide; mudança de
  conteúdo (qual fala entra, ordem, CTA, música) é do dono.
- Antes de mostrar qualquer coisa, olhe você mesmo (extraia quadros com `ffmpeg -ss` e leia as imagens).

## Passo a passo

### 0. Máquina
`bash scripts/setup.sh` na primeira vez (confere ffmpeg, uv, node; instala o Remotion). Se faltar algo, diga o comando
de instalação e pare.

### 1. Abrir o projeto e transcrever
```bash
python3 scripts/preparar.py <projeto> "<caminho do bruto>"          # proxy 1080p, voz −16 LUFS
uv run --no-project --with faster-whisper --with nvidia-cublas-cu12 --with "nvidia-cudnn-cu12==9.*" \
  python scripts/transcrever.py <projeto>                            # palavras.json + transcricao.md
```
`<projeto>` é um nome curto sem espaço (ex.: `horta-varanda`). Segunda câmera, se houver:
`uv run --no-project --with numpy python scripts/sincronizar.py <projeto> "<camera-b>"`.
Pergunte pela trilha (arquivo) e pelo texto da cartela final (data, chamada, CTA) enquanto transcreve; a trilha entra
com `python3 scripts/preparar.py <projeto> --musica "<trilha>"`. Sem trilha não há corte "épico": avise o dono.

### 2. Roteiros (portão 1)
Leia `trabalho/<projeto>/transcricao.md` **inteira**. Siga a skill `roteiro-aida`: 2–3 roteiros em texto em
`trabalho/<projeto>/roteiros.md`, com minutagem, frase-chave, imagem e música por bloco. Mostre um resumo no chat e
**espere** a escolha. Ajustes do dono entram no texto, não no vídeo.

### 3. Montar a versão
Converta o roteiro aprovado em `trabalho/<projeto>/roteiro-vN.json` (formato em `exemplos/roteiro-exemplo.json`) e:
```bash
uv run --no-project --with numpy python scripts/musica-picos.py trabalho/<projeto>/musica.mp3   # se houver trilha: escolha o hit
bash scripts/montar.sh <projeto> trabalho/<projeto>/roteiro-vN.json
```
Isso cria as composições `Teaser16x9-<projeto>-vN` e `Teaser9x16-<projeto>-vN`, alinha a legenda palavra a palavra
(skill `legenda-vertical`) e mede rosto e luz por plano (skill `cor-e-pele`). Leia a lista de pedaços da legenda e o
`vN/relatorio.md` antes de seguir: fala cortada no meio, frase de 2 s solta ou zoom estranho se corrigem aqui.

### 4. Studio
`bash scripts/studio.sh` em segundo plano (porta 3123; outra com `PORTA=…`). Passe ao dono a URL e diga onde mexer:
aba **Props** à direita; `segmentos[].de/ate` (corte no bruto), `camera`, `zoom`, `push`, `legendas[].texto`,
`musica.*`, `cta.*`; o botão de salvar grava em `remotion/src/Composicoes.tsx`. Você também pode editar uma timeline com
`node scripts/props.mjs get|set <id>`. Derrube o Studio quando não for mais usado.

### 5. Preview (portão 2)
```bash
bash scripts/preview.sh <projeto> vN          # preview-16x9-480p.mp4 e preview-9x16-480p.mp4 em trabalho/<projeto>/vN/
```
O script confere quadros repetidos. Extraia 2–3 quadros de cada formato e olhe: no 9:16, legenda no pescoço, no máximo
2 palavras, minúscula, sem faixa preta na lateral; no 16:9, rosto sem corte; a cartela legível. Entregue os caminhos e
**espere o ok**.

### 6. Export
Com o ok literal do dono, grave `trabalho/<projeto>/vN/APROVADO` (data + a frase dele) e:
```bash
bash scripts/export.sh <projeto> vN 1080       # ou 2k / 4k, se pedido e se o bruto tiver resolução para isso
```
Feche com um relatório curto: duração, planos, o que saiu do roteiro, o que foi decidido no olho, onde estão os
arquivos. Trilha comercial: lembre que publicar exige licença.

## Vetos já pagos (não repetir)

- **Colcha de frases de 2 s** tiradas de pontos diferentes do bruto: sem continuidade, ninguém acompanha. Blocos longos.
- **Zoom pulando 100 → 170 %** a cada corte: parece rotação, cansa. Só 100 / 107,5 / 115 % (skill `ritmo-e-corte`).
- **Legenda com animação de entrada** (pop, subida, escala): reprovada. Entra e sai seca.
- **Legenda grande na frente da boca**: 100 px, peso 600, topo a 55 % foi reprovado; 86 / 550 / 60 % aprovado.
- **Export sem preview**: uma hora de render perdida. Sempre preview 480p antes.
- **Tempo do Whisper na legenda**: atrasa e "trava". Alinhamento forçado sempre.
- **Render com a máquina carregada** repete quadros; o script avisa, e aí `CONCORRENCIA=3`.

## Adaptações para Mac
Sem GPU NVIDIA o `transcrever.py` cai sozinho para a CPU (int8) e os proxies saem em VideoToolbox; o comando do
Whisper é só `uv run --no-project --with faster-whisper python scripts/transcrever.py <projeto>`. Detalhes e tempos no
README ("Adaptações para Mac"). Não testado em Mac.
