---
name: nova-referencia
description: Recebe um vídeo ou link de referência (reel, trailer, anúncio) e transforma o que ele faz em regras mensuráveis — legenda (tamanho, posição, caixa, palavras por vez, animação, cor, caixa alta) ou ritmo (duração de plano, zoom, cortes) — escritas numa skill irmã ao lado da padrão (ex. legenda-documentario), sem mexer na padrão, e pede o ok do dono antes de usar. Use quando mandarem "quero a legenda igual a esse reel", "faz no estilo desse vídeo", "olha essa referência", ou um link/arquivo de vídeo como modelo.
---

# Nova referência → skill irmã

A skill padrão (`legenda-vertical`, `ritmo-e-corte`) **não muda** por causa de uma referência. A referência vira uma
skill nova, ao lado, com nome próprio (`legenda-<nome>`, `ritmo-<nome>`), e só passa a valer numa versão depois de o
dono ver um preview curto e aprovar.

## 1. Pegar a referência
- Arquivo: copie para `trabalho/referencias/<nome>/` (fora do git).
- Link: peça o arquivo ao dono ou baixe só para análise (`uvx yt-dlp -o "trabalho/referencias/<nome>/ref.%(ext)s" <link>`),
  se ele tiver direito de usar como referência. **A referência nunca entra no git nem no vídeo.**
- Pergunte o que ele gostou nela (a legenda? o ritmo? a cor?). Meça só isso.

## 2. Medir (números, não adjetivos)
```bash
R=trabalho/referencias/<nome>
ffprobe -v error -show_entries stream=width,height,r_frame_rate -of compact $R/ref.mp4
ffmpeg -v error -i $R/ref.mp4 -vf "fps=2,scale=540:-2" $R/q-%03d.png            # 2 quadros por segundo
ffmpeg -v error -ss <t> -i $R/ref.mp4 -frames:v 12 $R/seq-%02d.png               # 12 quadros seguidos: animação
```
Olhe os quadros (leia as imagens) e anote, para a **legenda**:

| medida | como |
|---|---|
| tamanho | altura da letra minúscula (x-height) ou da linha em % da altura do quadro → px em 1920 |
| posição | topo da legenda em fração da altura (0,6 = pescoço); centrada ou alinhada |
| palavras por vez | conte em 10 pedaços seguidos; média e máximo |
| caixa / fundo | sem fundo, caixa sólida (cor, opacidade, raio, padding), contorno (espessura), sombra |
| caixa alta | minúscula, Título, CAIXA ALTA; pontuação sim/não |
| fonte | sans/serif, peso aproximado (400/550/700/900), largura (condensada?) |
| cor | branca, amarela, palavra de destaque colorida (qual regra decide o destaque?) |
| animação | compare os 12 quadros seguidos: seca, fade (quantos quadros), pop/escala (de quanto), subida |
| tempo | o pedaço entra com a palavra ou antes? (alinhe o áudio da referência com `alinhar.py` se precisar) |

Para **ritmo**: duração média de plano
(`ffmpeg -i ref.mp4 -vf "select='gt(scene,0.3)',showinfo" -f null - 2>&1 | grep pts_time`), presença de zoom (quadros
seguidos crescem?), cortes por frase, onde a música bate.

## 3. Escrever a skill irmã
`.claude/skills/legenda-<nome>/SKILL.md`, no molde da `legenda-vertical`: descrição dizendo de qual referência veio e
quando usar; a tabela medida acima com os números; **o que muda em relação ao padrão** (e só isso); o que continua igual
(sync palavra a palavra, alinhamento forçado, nome de marca inteiro).

No código, sem tocar no padrão:
- Se a diferença couber nos campos (`legenda.tamanho`, `peso`, `topo`, `cor`) e no `--max-palavras` do `quebrar.py`
  (`"legenda": {"maxPalavras": 3}` no roteiro), a skill irmã só registra os valores.
- Se precisar de desenho novo (caixa, contorno, caixa alta, destaque), crie `remotion/src/legendas/<Nome>.tsx` (copie o
  `Padrao.tsx` e mude), registre em `remotion/src/legendas/index.ts` (`<nome>: <Nome>`) e use
  `"legenda": {"estilo": "<nome>"}` no roteiro. Animação, se a referência tiver, entra só no estilo irmão.
- Regras de design continuam valendo (skill `design-da-peca`): nada de glow, sombra pesada ou emoji só porque a
  referência tem; se tiver, pergunte.

## 4. Pedir o ok antes de usar
Monte uma versão curta (10–15 s) com o estilo novo, `bash scripts/preview.sh <projeto> vN 9x16`, mostre ao lado de um
quadro da referência e pergunte. Só depois do ok o estilo entra numa versão de verdade. Registre na skill irmã a data e
a frase do ok (sem nome de pessoa).
