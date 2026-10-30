---
name: roteiro-aida
description: Escrever 2–3 roteiros de teaser/trailer em texto a partir da transcrição de um talking head, na estrutura AIDA (atenção, interesse, desejo, ação), com gancho nos primeiros 5 s, blocos longos de fala corrida, ordem do roteiro (não da gravação), frase-chave por bloco e falas conferidas no áudio. Use no portão 1 do fluxo editar-teaser, ou quando pedirem "roteiro do teaser", "quais falas entram", "propõe uns cortes", "refaz o roteiro".
---

# Roteiro AIDA

O roteiro é aprovado **em texto** antes de qualquer render. Ele decide quais falas entram, em que ordem, onde está a
frase-chave de cada bloco e o que a imagem e a música fazem. Narrativa e fatos vêm do que a pessoa fala no bruto; o
clima vem de quem dirige. Nada de inventar fala.

## Regras

1. **Gancho nos primeiros 5 s, para quem assiste.** A primeira frase fala com o espectador ("você…", uma pergunta, uma
   promessa concreta, uma tensão), não sobre quem fala. Abrir com "eu sou…" ou com contexto perde o público.
2. **AIDA em quatro blocos:**
   - **Atenção:** o gancho e a tese em uma tomada.
   - **Interesse:** a dor ou a situação de quem assiste, nas palavras do bruto.
   - **Desejo:** a virada: o que muda, o que é possível; o pico emocional e o pico da música.
   - **Ação:** o convite concreto (data, lugar, o que fazer) e a cartela.
3. **Blocos longos, de 8 a 20 s,** com o pensamento inteiro. Poucos cortes. Uma colcha de frases de 2 s tiradas de
   pontos diferentes do bruto foi reprovada: perde continuidade, a voz pula de tom e ninguém acompanha.
4. **A ordem é a do roteiro, não a da gravação.** Reordenar é permitido e esperado; dentro de um bloco, prefira falas
   que estavam juntas no bruto (a entonação casa).
5. **Uma frase-chave por bloco** (a que vira o jogo): ela ganha o punch-in de 115 % e, num dos blocos (em geral o
   Desejo), o hit da música.
6. **Respiro só nos 3–4 momentos mais pesados** (depois de uma revelação, um sorriso, uma pausa emocionada): 0,8–2 s
   de silêncio no rosto. Nos outros pontos, a pausa natural da fala.
7. **Fala citada é conferida no áudio.** O Whisper erra palavra e nome. Para cada fala do roteiro:
   `python3 scripts/falas.py <projeto> "mm:ss.s" "começo da fala"` devolve início e fim; ouça o trecho
   (`ffplay -ss <ini> -t <dur> -autoexit trabalho/<projeto>/voz.m4a`) ou, sem ouvir, marque com ⚠ no roteiro.
   Nome próprio e número sempre conferidos.
8. **Tema sensível vira pergunta.** Se a fala mais forte encosta em tema de partido, crença, saúde ou dinheiro prometido,
   proponha e pergunte; quem decide é o dono.
9. **Duração:** teaser 30–60 s; trailer 90–120 s; vertical para feed rende melhor até ~60 s. Fala corrida a ~2,5
   palavras/s: 60 s ≈ 150 palavras de fala.

## Formato da entrega (trabalho/<projeto>/roteiros.md)

Para cada roteiro (2 ou 3, com ângulos diferentes: ex. "a dor primeiro", "a promessa primeiro", "a história"):

```
## Roteiro A · <nome curto> · ~0:58

### 1 · ATENÇÃO (0:00–0:12)
Fala (uma tomada, 01:12,4 → 01:24,0):
> "…texto literal…"
- Frase-chave: "…" → punch-in 115 %
- Imagem: nasce do preto; aberto 100 % com push lento até ~105 %
- Música: piano baixo; respira 1 s depois da frase-chave

### 2 · INTERESSE …
### 3 · DESEJO …   (o hit da música cai na frase-chave daqui)
### 4 · AÇÃO …
Cartela: "<título>" / "<linha>" / CTA "<botão>" (4 s)

Cortes de fala: N (M escondidos por troca de câmera)
```

Feche com **"Para você decidir"**: a escolha do roteiro e no máximo 3 perguntas objetivas (uma fala duvidosa, um tema
sensível, a trilha). Recomende um.

## Do texto aprovado para o roteiro.json

Cada trecho vira `{"de": "mm:ss.s", "inicio": "primeiras palavras", "fim": "últimas palavras"}` com opcionais
`"chave"` (texto da frase-chave, dentro do trecho), `"respiroDepois"` (s), `"camera"` (`"a"`/`"b"`), `"zoom"`,
`"de_fim"` (minutagem aproximada do fim, se o trecho for longo), `"maxPausa"`. Música: `"hitNaFaixa"` (s na trilha, de
`scripts/musica-picos.py`), `"hitEm"` (texto da fala que recebe o hit; padrão = frase-chave do bloco Desejo),
`"ajustes"` (turn line). Modelo completo em `exemplos/roteiro-exemplo.json`.
