---
name: assets-e-broll
description: B-roll e assets no teaser — o editor manipula, não gera. Inventaria o que foi fornecido (trabalho/<projeto>/assets/), encaixa cada asset ancorado na fala (cheio, sobreposto ou lado; parado ou push), corta pela ação do clipe, respeita rosto e legenda, recorta o 9:16 no assunto, e escreve a lista de pedidos do que falta (assets-pedido.md) em vez de criar. Use quando o roteiro pedir B-roll, foto, logo, tela, cartela ou trilha; quando chegarem arquivos de asset; ou quando pedirem "põe um B-roll aqui", "coloca o logo", "falta imagem".
---

# Assets e B-roll

**O editor não cria asset.** B-roll, fotos, logos, telas, cartelas e trilha são fornecidos: exportados de uma skill
de design, do design system da sua marca ou entregues pelo time. O que for específico se pede (ou se gera fora daqui)
e se entrega. Aqui só se corta, posiciona, recorta e move.

## 1. Inventário
Os arquivos vão para `trabalho/<projeto>/assets/` (o dono arrasta para a pasta, ou você copia do caminho que ele
mandar; abra a pasta para ele com `bash scripts/abrir.sh trabalho/<projeto>/assets`).
```bash
python3 scripts/assets.py <projeto>       # também roda no preparar e em toda montagem
```
Lista tipo, dimensão, duração e transparência e grava `trabalho/<projeto>/assets.json`. Olhe cada asset antes de usar
(extraia 3 quadros de um clipe: começo, meio, fim) para saber onde está a ação.

## 2. Encaixe no roteiro.json
```json
"insercoes": [
  {"asset": "varanda-regando.mp4", "sobre": "a varanda muda", "dur": 3.0, "inicio": 1.5,
   "modo": "cheio", "movimento": "push", "push": 0.06},
  {"asset": "logo.png", "sobre": "turma nova", "ate": "comigo", "modo": "sobreposto"}
]
```
- `sobre`: o trecho da fala em que a inserção **entra** (como a `chave`); segue o corte quando a timeline muda.
- `dur` (s) ou `ate` (texto da fala em que ela sai).
- `modo`: **cheio** (cobre o quadro), **sobreposto** (PNG transparente por cima), **lado** (16:9: pessoa numa metade,
  asset na outra; no 9:16 não existe e vira cheio).
- `movimento`: **parado** ou **push** (5–10 % ao longo da inserção, com easing). Nada de giro, tremida ou zoom rápido.
- opcionais: `inicio` (s dentro do clipe), `foco` [x, y] (ponto de interesse), `ajuste` (`cobrir`/`conter`),
  `posicao` por formato `{"16x9": {"x", "y", "largura"}, "9x16": {...}}`, `descricao` (para o pedido).
- **O áudio da fala continua por baixo.** O som do clipe não entra.
No Studio, tudo isso aparece em `insercoes[]` no painel Props.

## 3. Regras
- **Cortar pela ação do clipe, não por duração fixa:** entre quando a ação começa (`inicio`) e saia antes de ela
  acabar. Corte rápido: **2–4 s**; sequência de imagens: **6–8 s** no total. O montador avisa o que fica fora.
- **Ancore no sentido:** o B-roll ilustra a palavra que está sendo dita, não a frase anterior.
- **Use o B-roll para esconder emenda** (jump cut entre takes): a inserção cobrindo o corte deixa a voz contínua.
- **Não cubra a frase-chave nem o respiro**: ali o rosto é o assunto.
- **Rosto e legenda livres:** sobreposto no 16:9 fica no canto superior oposto ao rosto (padrão x 0,84, y 0,2,
  largura 0,2); no 9:16, abaixo da legenda e acima da faixa da interface (padrão x 0,5, y 0,72, largura 0,36). A
  legenda fica por cima de tudo e não muda de lugar.
- **Recorte 9:16 inteligente:** asset 16:9 em cheio no vertical perde as laterais; o `rostos.py` acha o foco (rosto,
  senão o centro do detalhe) e o recorte centra nele. Se o assunto não couber, peça uma versão 1080×1920.
- **PNG transparente** para logo, selo e tela recortada; vídeo com transparência só em WebM VP9 ou ProRes 4444.
- **Logo:** uma vez, pequeno, no fim ou junto do convite; nunca no gancho. Cartela final é da `design-da-peca`.
- Foto parada em cheio pede `push` (5–8 %); clipe com movimento próprio fica `parado`.

## 4. Quando falta asset: pedido, não geração
Ponha no `roteiro.json` a inserção com o nome que o arquivo terá e uma `descricao`. Ao montar, o que não existir em
`assets/` fica fora do vídeo e vai para **`trabalho/<projeto>/assets-pedido.md`**: o quê, para qual fala, modo,
formato (1920×1080 ou 1080×1920; MP4 H.264 ou PNG transparente; foto com 1920 px no lado maior), tempo na tela e
duração mínima do clipe (com folga para cortar pela ação). Abra o arquivo para o dono e diga: "peça isto à skill de
design ou ao time; quando chegar, salve em assets/ e eu monto de novo". **Não gere imagem, vídeo nem logo.**
