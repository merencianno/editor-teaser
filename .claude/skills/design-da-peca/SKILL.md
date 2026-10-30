---
name: design-da-peca
description: O know-how de design que vai em todo teaser — uma sans com peso, tracking e tamanho por formato, um destaque por texto, nada de enfeite com cara de IA (glow, pop, emoji, borda colorida), nome de marca inteiro, áreas seguras de Reels/TikTok/Shorts, cartela final legível em menos de 3 s com um CTA, contraste e movimento sutil. Use ao escrever a cartela final, mexer em legenda, texto na tela, cor de texto ou animação, ou antes de mostrar qualquer preview.
---

# Design da peça

O vídeo é da pessoa falando; o texto na tela serve a ela. Tudo o que chama atenção para si (efeito, cor, movimento)
compete com o rosto e perde.

## Tipografia
- **Uma família sans** no vídeo inteiro (Instrument Sans por padrão; a da marca, se houver). Hierarquia por tamanho e
  peso, não por fonte nova.

| uso | 9:16 (1080×1920) | 16:9 (1920×1080) | peso | tracking |
|---|---|---|---|---|
| legenda | 86 px, topo a 60 % | 60 px, topo a 64 % (desligada por padrão) | 550 | −0,015 em |
| título da cartela | 78 px | 92 px | 600 | −0,02 em |
| linha da cartela | 40 px | 34 px | 400 | 0 |
| botão (opcional) | 26 px, caixa alta | 26 px, caixa alta | 600 | +0,04 em |

- Linhas equilibradas: `text-wrap: balance` em título e linha; **nada de palavra órfã** (uma ou duas palavras soltas
  sob uma linha cheia). Quebre à mão num ponto de sentido se preciso.
- **Nome de marca nunca quebra** entre linhas (nem o artigo que faz parte do nome se separa do resto): liste em
  `"marcas"` no roteiro; a cartela troca os espaços dele por inquebráveis e a legenda o mantém num pedaço só.

## Um destaque por texto
Num título, no máximo **um** elemento destacado (uma palavra em cor ou peso, ou o botão). Dois destaques = nenhum.

## Sem cara de IA
Fora: **glow**, neon, sombra colorida; **pop/bounce/escala** na entrada de texto; emoji na legenda; **borda colorida**
em caixa ou botão de enfeite; barra de acento; gradiente decorativo; "circulado" pronto; texto girando ou tremendo.
Destaque vem de tipografia, espaço e de um gesto próprio da peça, usado uma vez.

## Áreas seguras (9:16)
A interface de Reels, TikTok e Shorts cobre partes do vídeo. Medidas conservadoras que servem aos três (os apps mudam a
UI; confira num upload privado):
- **topo ~14 %** (~270 px): nome do perfil, abas;
- **base ~25 %** (~480 px): legenda do post, música, botões;
- **direita ~12 %** (~130 px): curtir, comentar, compartilhar; esquerda ~6 %.
A legenda a 60 % e a cartela (padding 14 % / 25 % / 11 %) já respeitam. Nada de texto importante fora disso.

## Cartela final
- **Legível em menos de 3 s, um CTA** ([Rocketship](https://www.rocketshiphq.com/?p=7229)): título curto (data ou
  promessa), uma linha, no máximo um botão. 4 s na tela.
- Fundo preto (ou o escuro do próprio vídeo), texto branco; contraste de texto pequeno ≥ 4,5:1.
- Sem logo gigante, sem três chamadas, sem QR code se ninguém pediu.

## Movimento
- Texto entra **seco** ou com fade curto (0,3–0,5 s, easing in-out). Legenda: sempre seca.
- Se algo flutuar, só `translateY` de ±4–6 px em 4–6 s, sem rotação.
- Push-in do vídeo: 5–10 % em todo o plano, com easing (skill `ritmo-e-corte`). Nada de zoom em todo corte.

## Antes de mostrar
Extraia 2–3 quadros de cada formato e olhe: texto dentro da área segura, legenda abaixo da boca, sem palavra órfã na
cartela, nome de marca inteiro, nenhum enfeite da lista acima.
