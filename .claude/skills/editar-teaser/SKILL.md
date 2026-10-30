---
name: editar-teaser
description: Fluxo mestre para editar um teaser ou trailer a partir de um vídeo bruto de talking head e de um roteiro/copy já aprovado, em 16:9 e em 9:16 com legenda palavra a palavra. Acha o roteiro no bruto (portão 1), encaixa os assets fornecidos, monta no Remotion e abre o Studio, renderiza um preview 480p (portão 2) e só então exporta. O Claude executa e abre tudo; o usuário só conversa. Use quando o usuário disser "vamos editar", "edita esse vídeo", "faz um teaser/trailer/reel desse bruto", mandar um .mp4/.mov de alguém falando, ou pedir uma versão nova de um teaser já montado.
---

# Editar teaser (fluxo mestre)

**Este editor não escreve a copy nem cria os assets; ele edita.** O roteiro vem pronto (skill de copy/roteiro ou
time); B-roll, fotos, logos, telas e trilha vêm da skill de design, do design system da marca ou do time. O trabalho
aqui é fazer um bom roteiro funcionar na tela: escolher os takes, cortar, enquadrar, legendar, encaixar os assets,
mixar e entregar.

**O usuário não usa terminal.** Ele conversa; você roda cada comando, abre o Studio, os previews e as pastas
(`bash scripts/abrir.sh <arquivo|pasta|url>`, que usa `open` no Mac e `xdg-open` no Linux). Nunca diga "rode isto no
terminal". Se algo precisar de senha de administrador, explique o que é e peça que ele faça pela janela do sistema
(no Mac, o instalador .pkg do Homebrew); você não digita senha.

O dono do vídeo (quem pediu) revisa e aprova; **só ele declara que está pronto**. Os dois portões não se pulam:

1. **Portão 1 · roteiro no bruto:** o mapa fala → take → minutagem, aprovado antes de montar.
2. **Portão 2 · preview:** preview 480p dos proxies, aprovado antes de qualquer export.

Exportar sem preview já custou uma hora de render jogada fora. Qualquer mudança depois de um preview aprovado volta
para um preview novo.

## Regras da casa
- O bruto **nunca** é alterado. Tudo sai em `trabalho/<projeto>/` (fora do git). Nada pesado entra no git.
- Versão nova nunca sobrescreve: cada montagem vira `vN` novo; export existente nunca é regravado.
- Uma pergunta por vez, curta. Ajuste de ofício (corte meio quadro antes, rosto mais centrado) você decide e conta;
  conteúdo (qual fala, ordem, CTA, música, asset) é do dono.
- Olhe antes de mostrar: extraia quadros (`ffmpeg -ss <t> -i <vídeo> -frames:v 1 q.png`) e leia as imagens.

## Passo a passo

### 0. Máquina
Primeira vez: `bash scripts/setup.sh` (confere ffmpeg, uv, node, git; no Mac instala pelo `brew` o que faltar;
instala o Remotion). Sem Homebrew no Mac, peça ao usuário o instalador .pkg (README, "Adaptações para Mac").

### 1. Abrir o projeto
Peça (de uma vez): o caminho do bruto, o **roteiro/copy aprovado**, a pasta ou os arquivos de **assets**, a **trilha**
e o texto da **cartela final**. Faltando roteiro, siga o plano B da `roteiro-no-bruto`, avisando que o ideal é o
roteiro vir da skill de copy.
```bash
python3 scripts/preparar.py <projeto> "<bruto>" [--musica "<trilha>"]   # proxy, voz −16 LUFS, inventário de assets
bash scripts/transcrever.sh <projeto>                                   # motor certo para a máquina
```
`<projeto>` é um nome curto sem espaço. Assets: copie para `trabalho/<projeto>/assets/` (skill `assets-e-broll`).
Segunda câmera: `uv run --no-project --with numpy python scripts/sincronizar.py <projeto> "<camera-b>"`.

### 2. Roteiro no bruto (portão 1)
Skill `roteiro-no-bruto`: `python3 scripts/mapear-roteiro.py <projeto> <roteiro>`, abra a pasta dos takes para ele
ouvir, mostre o mapa resumido e o que falta (falas ❌, assets que o roteiro pede e não chegaram). **Espere o ok.**

### 3. Montar a versão
Complete `trabalho/<projeto>/roteiro.json` a partir do `roteiro-rascunho.json` (frase-chave, respiros, inserções de
asset, música; modelo em `exemplos/roteiro-exemplo.json`) e:
```bash
uv run --no-project --with numpy python scripts/musica-picos.py trabalho/<projeto>/musica.mp3   # se houver trilha
bash scripts/montar.sh <projeto> trabalho/<projeto>/roteiro.json
```
Cria `Teaser16x9-<projeto>-vN` e `Teaser9x16-<projeto>-vN`, alinha a legenda (`legenda-vertical`), mede rosto, luz e
foco dos B-rolls (`cor-e-pele`, `assets-e-broll`). Leia a lista da legenda, os avisos de inserção e `vN/relatorio.md`.
Se surgir `assets-pedido.md`, abra-o para o dono: é a lista do que pedir à skill de design ou ao time.

### 4. Studio
`bash scripts/studio.sh` em segundo plano: ele sobe na porta 3123 (outra com `PORTA=…`) e abre o navegador sozinho.
Diga onde mexer: aba **Props** à direita (`segmentos`, `insercoes`, `legendas`, `musica`, `cta`). Pedidos falados
("legenda adiantada nos 0:12", "logo menor") você mesmo aplica com `node scripts/props.mjs get|set <id>`. Derrube o
Studio quando não for mais usado.

### 5. Preview (portão 2)
`bash scripts/preview.sh <projeto> vN`: renderiza os dois formatos em 480p, confere quadros repetidos e abre os
arquivos no player. Antes de entregar, extraia 2–3 quadros de cada formato, inclusive dos B-rolls: no 9:16, legenda no
pescoço, no máximo 2 palavras, minúscula, sem faixa preta, nada tapando o rosto. **Espere o ok.**

### 6. Export
Com o ok literal, grave `trabalho/<projeto>/vN/APROVADO` (data + a frase dele) e `bash scripts/export.sh <projeto> vN
1080` (ou `2k`/`4k`, se pedido e se o bruto tiver resolução). Abra a pasta do resultado
(`bash scripts/abrir.sh trabalho/<projeto>/vN`). Feche com um relatório curto: duração, planos, inserções, o que saiu
do roteiro, o que foi decidido no olho. Trilha comercial: lembre que publicar exige licença.

## Vetos já pagos (não repetir)
- **Colcha de frases de 2 s** tiradas de pontos diferentes do bruto. Blocos longos.
- **Zoom pulando 100 → 170 %** a cada corte. Só 100 / 107,5 / 115 % (`ritmo-e-corte`).
- **Legenda com animação de entrada** ou **grande na frente da boca** (100 px / 600 / 55 % reprovado; 86 / 550 / 60 %).
- **Export sem preview**: uma hora de render perdida.
- **Tempo do Whisper na legenda**: alinhamento forçado sempre.
- **Render com a máquina carregada** repete quadros; o script avisa, e aí `CONCORRENCIA=3`.
- **Inventar** fala que o bruto não tem ou gerar asset que não foi entregue.

## Mac
`transcrever.sh` usa o mlx-whisper (GPU do Mac) sozinho; os proxies saem em VideoToolbox. Não testado em Mac; detalhes
no README ("Adaptações para Mac").
