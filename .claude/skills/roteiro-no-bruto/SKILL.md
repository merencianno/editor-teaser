---
name: roteiro-no-bruto
description: Portão 1 do editor — recebe o roteiro ou a copy já aprovada (texto, .md, .docx), acha cada fala nos takes do bruto (o melhor take, com o áudio para conferir), mostra o mapa fala → take → minutagem → duração → onde entra corte, respiro e hit, e aponta o que o roteiro pede e o bruto não tem. O AIDA entra só como checagem de estrutura e, sem roteiro nenhum, como plano B. Use quando chegar um roteiro/copy junto com o bruto, quando pedirem "acha essas falas no vídeo", "monta esse roteiro", "qual take é melhor", ou quando não houver roteiro.
---

# Roteiro no bruto

**Este editor não escreve a copy; ele edita.** O roteiro chega pronto, da skill de copy/roteiro ou do time, e o
trabalho aqui é achar no bruto a melhor versão de cada fala e montar com começo, meio e fim. Fala que o roteiro pede e
o bruto não tem não se inventa: aponta-se.

## 1. Receber o roteiro
Aceite o que vier: texto colado, `.md`, `.txt`, `.docx`. Salve em `trabalho/<projeto>/roteiro-aprovado.<ext>`. O
formato que o mapa entende (o mínimo é um parágrafo por fala):

```
# Título do vídeo
## Gancho                       ← bloco
Primeira fala, um parágrafo.    ← fala a achar no bruto
**Frase-chave em negrito.**     ← frase-chave do bloco (punch-in; no bloco do pico, o hit da música)
[B-roll: arquivo.mp4 sobre "trecho da fala"]   ← direção (não é fala)
Cartela: Sábado, 10h            ← rótulos: B-roll, Asset, Imagem, Logo, Tela, Música, Trilha, Cartela, CTA, Nota
```
Se a copy vier noutro formato (tabela, falas numeradas), reescreva nesse molde sem mudar uma palavra das falas.
Modelo: `exemplos/copy-exemplo.md`.

## 2. Mapear
```bash
python3 scripts/mapear-roteiro.py <projeto> trabalho/<projeto>/roteiro-aprovado.md
```
Para cada fala ele procura todos os takes parecidos (a pessoa costuma repetir a frase) e escolhe o melhor:
texto mais fiel à copy, Whisper mais seguro (clareza), menos tropeço (palavra repetida, muleta longa). Grava:
- `trabalho/<projeto>/mapa.md`: fala → ✅ fiel / ⚠ parecida / ❌ não está no bruto → take escolhido (minutagem,
  duração, pausas longas que viram corte), diferenças de texto e outros takes;
- `trabalho/<projeto>/mapa/fala-NN.m4a`: o take escolhido de cada fala, **para ouvir**;
- `trabalho/<projeto>/roteiro-rascunho.json`: o ponto de partida do `roteiro.json`.

## 3. Conferir no áudio e mostrar
- O Whisper erra palavra e nome: toda fala ⚠ e todo nome próprio ou número precisa ser ouvido. Abra a pasta dos
  takes para o dono (`bash scripts/abrir.sh trabalho/<projeto>/mapa`) e diga quais ouvir.
- Mostre o mapa resumido no chat: uma linha por fala (take, duração, status) e, no fim, **o que falta**: falas ❌,
  diferenças relevantes (⚠ "copy X → bruto Y"), duração total contra a pedida.
- Onde entra **corte** (pausa longa, emenda entre takes), **respiro** (0,8–2 s só nos 3–4 momentos pesados) e
  **hit** da música (a frase-chave do bloco do pico). Proponha; o dono decide.
- Para fala que falta: ofereça trocar por outra fala do bruto com o mesmo sentido (cite minutagem), cortar, ou pedir
  regravação. Nunca "aproxime" com pedaços de palavras de lugares diferentes.

**Portão 1:** espere o ok do mapa. Só então complete o `roteiro.json` (rascunho + `chave`, `respiroDepois`,
`insercoes`, `musica`, `cta`; skill `assets-e-broll` para as inserções) e monte.

## 4. Checagem de estrutura (AIDA como régua, não como regra de escrita)
Sem mudar a copy, verifique e aponte:
- **gancho nos primeiros 5 s** falando com quem assiste (se a primeira fala demora a chegar no ponto, sugira começar
  no meio dela, onde o take permitir);
- **uma frase-chave por bloco**, marcada;
- **CTA** claro no fim (cartela com um convite);
- **blocos longos de 8–20 s**, sem colcha de frases de 2 s (foi reprovado: perde continuidade);
- duração: teaser 30–60 s; trailer 90–120 s; vertical de feed rende melhor até ~60 s.

## Plano B · sem roteiro
Se vier só o bruto, avise antes: **"o ideal é o roteiro vir da skill de copy; posso propor um a partir das falas, mas
é um rascunho de editor"**. Com o ok, leia `transcricao.md` inteira e proponha 2–3 roteiros em AIDA no formato de
`exemplos/roteiros-aida-exemplo.md` (gancho para quem assiste, interesse, desejo com a frase-chave, ação), só com falas
que existem no bruto, com minutagem e ⚠ no que não foi ouvido. Tema sensível (partido, crença, saúde, promessa de
dinheiro) vira pergunta. Escolhido um, ele passa pelo mesmo mapa (passos 2 e 3).

## roteiro.json (o que o montador lê)
Cada trecho: `{"de": "mm:ss.s", "inicio": "primeiras palavras", "fim": "últimas palavras"}` com opcionais `"chave"`,
`"respiroDepois"` (s), `"camera"` (`"a"`/`"b"`), `"zoom"`, `"de_fim"` (minutagem do fim, se o trecho for longo),
`"maxPausa"`. Mais `insercoes` (skill `assets-e-broll`), `musica` (`hitNaFaixa`, `hitEm`, `ajustes`; skill
`som-e-musica`), `cta`, `marcas`, `nomes`. Modelo completo em `exemplos/roteiro-exemplo.json`.
