---
name: som-e-musica
description: Som de teaser de talking head — voz em −16 LUFS, ducking da trilha sob a fala, rampas sem degrau, hit da música na frase-chave, build contínuo, stopdown/turn line, fades de corte e licença da trilha — e como isso vira campo no Remotion (musica.*). Use ao escolher onde a música entra, quando a trilha briga com a voz, quando pedirem "a música tem que bater na frase", "deixa a frase sozinha", ou ao preparar a voz.
---

# Som e música

A música manda no ritmo de um teaser: sem trilha não existe corte "épico" para aprovar. A voz manda no conteúdo:
nunca pode ficar abaixo da trilha.

## Voz
- **−16 LUFS integrado**, pico real ≤ −1,5 dBTP: `preparar.py` faz com `loudnorm`. É o nível usual de plataforma
  social/web para voz.
- Ruído de ar-condicionado ou sala: `preparar.py --tirar-ar` passa um redutor leve (`afftdn`). Mais que isso deixa a
  voz "aquática"; prefira não tratar a tratar demais.
- **Fade de 1 quadro em todo corte de áudio** (evita o clique) e, se o silêncio entre falas "furar", um laço do som da
  sala por baixo ([Sound On Sound](https://www.soundonsound.com/techniques/using-fades-crossfades),
  [guia de room tone](https://larryjordan.com/?p=141196)).

## Trilha
| regra | no motor |
|---|---|
| **Ducking:** trilha bem abaixo da fala (~−14 dB) e cheia quando não há voz ([Storyblocks](https://www.storyblocks.com/resources/tutorials/how-to-balance-audio-premiere-pro)) | `musica.volumeSobFala` (0,2 ≈ −14 dB) e `volumeCheio` (0,6–0,75) depois da última fala |
| **Rampas sem degrau:** toda subida e descida com rampa de 0,8–2 s e easing | `musica.ajustes[].rampa`; a transição fala → cartela já tem rampa |
| **Build contínuo, hit exatamente na frase-chave** ([Film Editing Pro](https://www.filmeditingpro.com/quick-tips-for-cutting-music-cues/)) | `roteiro.musica.hitNaFaixa` (s na trilha) cai no começo da frase-chave de `hitEm` |
| **Cortar música só em frase musical** (fim de compasso, respiro da faixa), nunca no meio de uma nota | o template usa a faixa contínua; se precisar encurtar, escolha a emenda ouvindo |
| **Stopdown / turn line:** a música cai (ou para) para uma frase soar sozinha, e volta ([Rareform Audio](https://www.rareformaudio.com/blog/trailer-music-drop-vs-stopdown)) | `roteiro.musica.ajustes: [{"fala": "…", "ganho": 0.3, "dur": 2, "rampa": 0.8}]` |
| **Sem efeito sonoro literal** (whoosh em todo corte, "ding"); riser só se a trilha pedir | nada de SFX no template |

## Achar o hit
`uv run --no-project --with numpy python scripts/musica-picos.py <trilha>` lista as maiores subidas de energia (entrada
de percussão, acorde cheio) e as quedas (stopdown). Escolha ouvindo; o número é só o atalho. Num caso real: o crescendo
da faixa caiu na frase do Desejo, o hit 1 s depois da revelação e a descida no bloco da Ação.

## Licença
Trilha comercial precisa de licença para anúncio ou página pública. Corte de aprovação interna pode usar a faixa de
referência; antes do export final, pergunte ao dono se há licença (ou proponha uma de biblioteca licenciada no mesmo
clima) e registre a resposta no relatório.
