---
name: legenda-vertical
description: Padrão aprovado de legenda para teaser/reel vertical de talking head — no máximo 2 palavras por vez, cada pedaço na tela exatamente enquanto é falado (alinhamento forçado, não o tempo do Whisper), sem animação, minúscula e sem pontuação (maiúscula só em nome e marca), branca, na altura do pescoço; e o recorte 9:16 que segue o rosto sem faixa preta. Use para "legenda vertical", "legenda palavra a palavra", "legenda de reel", "versão vertical com legenda", ou ao legendar qualquer talking head 9:16 (Remotion ou ffmpeg).
---

# Legenda vertical (padrão)

Este é o padrão. **Não peça a explicação de novo** e não mude as regras por conta própria: estilo novo nasce como skill
irmã pela skill `nova-referencia`, e esta fica como está.

## Regras fechadas

1. **No máximo 2 palavras na tela.** Nunca frase. Exceção: nome de marca de várias palavras fica inteiro.
2. **Sync palavra a palavra:** o pedaço aparece quando a palavra é dita (1 quadro antes do som: o olho lê junto com o
   ouvido) e troca quando ela termina. Pausa curta (< 0,35 s) segura o pedaço até o próximo; pausa longa deixa a tela
   sem legenda.
3. **Sem animação.** Entra e sai seca. Pop, escala, fade e subida foram reprovados.
4. **Minúscula e sem pontuação.** Dois pedaços não são uma frase: sai a maiúscula de começo de frase e toda vírgula,
   ponto, `?`, `!`, reticências e aspas. **Maiúscula só em nome** (pessoa, lugar, marca): os que aparecem com maiúscula
   no meio da frase são detectados; os demais vão em `--nomes` (ou `"nomes"` no roteiro).
5. **Palavra de ligação nunca pisca sozinha** ("a / sua casa" → "a sua / casa") nem fecha o par ("medo do / meu" →
   "medo / do meu").
6. **Visual (1080×1920):** uma sans (Instrument Sans por padrão), **86 px, peso 550**, branca, tracking −0,015 em,
   sombra suave; centrada, topo a **60 % da altura** = pescoço, logo abaixo da boca. 100 px / peso 600 / topo 55 % foi
   reprovado: grande, tapava a boca.
7. **Texto = fala aprovada.** As palavras vêm das frases do roteiro aprovado (conferidas), nunca da transcrição crua;
   só a quebra, a caixa e a pontuação mudam.

## Fluxo

Neste repositório é um comando só (`python3 scripts/legendas.py <projeto> vN`, chamado pelo `montar.sh`). Por dentro,
ou em outro projeto:

1. **Frases com tempo no áudio** → `frases.json` `[{"texto", "inicio", "fim"}]` (segundos no arquivo de voz, em ordem).
2. **Alinhar** (tempo real de cada palavra, MMS_FA do torchaudio, na CPU):
   ```bash
   uv run --no-project --index https://download.pytorch.org/whl/cpu --with torch --with torchaudio --with soundfile \
     python .claude/skills/legenda-vertical/scripts/alinhar.py voz.m4a frases.json palavras.json
   ```
   Confira no log: palavra com mais de ~0,8 s é pausa engolida (o script já recorta pela energia da voz).
3. **Quebrar:**
   ```bash
   python3 .claude/skills/legenda-vertical/scripts/quebrar.py palavras.json legendas.json --nomes "Marta" --marcas "Horta Fácil"
   ```
   Leia a lista impressa inteira antes de renderizar: nada de vírgula, ponto ou maiúscula fora de nome.
4. **Desenhar:** `remotion/src/legendas/Padrao.tsx` aqui; `referencia/LegendaPalavras.tsx` para levar a outro projeto
   Remotion. Os tempos de `legendas.json` estão no áudio: converta para a timeline do corte (aqui o `Teaser.tsx` faz
   pelo `bruto` de cada pedaço, então a legenda segue o corte quando você mexe nos segmentos). Em ffmpeg puro, gere um
   `.ass` com os mesmos pedaços e o mesmo estilo.
5. **Preview 480p** e esperar o ok; export final uma vez, só depois do ok.

## Vertical a partir de câmera 16:9

- O recorte 9:16 **segue o rosto em todo plano**, inclusive no aberto, e os planos ficam mais fechados que no 16:9
  (`enquadramento.verticalExtra`, 1,3). Com fonte 4K o recorte sai nativo em 1080×1920.
- **O vídeo tem de ser a câmera inteira antes do pan.** Com `width: 100%; object-fit: cover` o navegador já recorta o
  9:16 no centro, e o pan até um rosto fora do centro mostra uma faixa preta na lateral (cortou um ombro num caso real).
  O `<OffthreadVideo>` fica com largura `r × 100 %` (r = (16/9)/(9/16) ≈ 3,16), centrado
  (`left: −(r−1)/2 × 100 %`); o deslocamento em X entra como `tx / r` do elemento; limite do pan `(z·r − 1)/2`.
- Se pedirem "mais perto" e "menos escuro": feche o plano (`verticalExtra`) e suba a luz (`cor.luz`).

## Armadilhas já pagas

- **O tempo de palavra do Whisper não serve para legenda:** uma palavra engole a pausa seguinte e a legenda trava ou
  adianta. Sempre alinhamento forçado + recorte por energia.
- A janela do alinhador não pode invadir a frase vizinha (a última palavra "pega" o som dela). O script limita.
- Pedaço de 1 quadro quebra `interpolate` do Remotion ("inputRange must be strictly monotonically increasing"):
  duração mínima de 2 quadros e nenhum pedaço por cima do anterior.
- **Render com a máquina carregada repete quadros** (a imagem "engasga"). `scripts/conferir-quadros.py` conta; se
  acusar, renderize de novo com `CONCORRENCIA=3`.
- `/tmp` pequeno derruba o Remotion ("Unknown system error -122"): os scripts usam `TMPDIR=trabalho/tmp`.
- Preview 480p exato: renderize com `--scale=0.5` (540×960) e reduza no ffmpeg para 480×854; `--scale` fracionado dá
  altura não inteira e o Remotion recusa.

## Mac
O alinhador roda na CPU em qualquer máquina (o modelo é pequeno; ~10–20 s por minuto de fala). Em Apple Silicon dá para
tentar `device="mps"` no `alinhar.py`, mas não é necessário e não foi testado.
