---
name: cor-e-pele
description: Cor de talking head — correção primária, casar duas câmeras pela pele, pele entre 45 e 70 IRE, exposição igual entre takes, arco de grade do frio ao quente — medida pelo scripts/rostos.py e ajustada nos campos cor.* e cameras.*.ganho do Remotion. Use quando o vídeo estiver escuro, as câmeras não casarem, a pele estiver vermelha ou cinza, a luz pular entre takes, ou pedirem "corrige a cor", "deixa mais quente", "casa as câmeras".
---

# Cor e pele

Ordem de quem faz cor para entrevista: **primária** no plano de referência → **casar a outra câmera pela pele** →
**look** por cima ([PremiumBeat](https://www.premiumbeat.com/blog/tips-for-coloring-talking-head-interviews-in-davinci-resolve/)).
A pele é a referência porque é o que o olho julga primeiro.

## Medir antes de mexer
`scripts/rostos.py` (rodado pelo `montar.sh`) acha o rosto em 3 quadros de cada plano e mede a pele:
- **IRE da pele** (mediana): o alvo é **45–70 IRE**, com as sombras do rosto acima de 10–20 IRE
  ([wolfcrow](https://wolfcrow.com/a-quick-look-at-understanding-ire-values/)). Fora disso o script ajusta `cor.luz`
  até a borda mais próxima (no máximo 1,5×) e imprime.
- **Exposição por plano:** cada take vai à luz típica da sua câmera (`segmentos[].exposicao`, 0,85–1,35): a luz não
  pula quando a pessoa se mexe ou a nuvem passa.
- **Câmera B casada na A** pela média RGB da pele: `cameras.b.ganho`. Num caso real a câmera lateral saiu ~15 % mais
  clara e menos vermelha; o ganho por canal ficou perto de [1,11 1,04 1,07] na B contra [1,2 1,2 1,2] na A. Esses
  números são daquele set; os seus o script mede.
Confira no vectorscope mental: a pele cai na "linha da pele" (entre vermelho e amarelo)
([Frame.io](https://blog.frame.io/?p=26488)). Pele vermelha demais: baixe o R da câmera; cinza: suba a saturação do arco.

## Look
- `cor.contraste` 1,03–1,06 (em torno do meio). Não esmague o preto: cabelo e roupa escura perdem forma.
- **Arco frio → quente**, quase imperceptível: `cor.arco.inicio` (temperatura −0,03, saturação 0,9) até `fim`
  (+0,03, 1,0). O vídeo começa contido (a dor) e termina quente (a promessa). Mais que ±0,05 vira filtro.
- Preto e branco, filtro de época, LUT pronta: só se o dono pedir.

## No painel do Studio
`cor.luz`, `cor.contraste`, `cor.arco`, `cameras.a.ganho`, `cameras.b.ganho`, `segmentos[].exposicao`. Mude um por vez
e compare no mesmo quadro (o Studio deixa fixar o quadro); depois um preview novo.
