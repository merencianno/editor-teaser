---
name: ritmo-e-corte
description: Regras de corte, enquadramento e zoom para talking head com uma ou duas câmeras — onde cortar, quando trocar câmera ou tamanho, quanto aproximar, atraso da imagem, pausas, fades de áudio, crop de 4K — e como cada regra vira campo no Remotion (segmentos, zoom, push, transicao). Use ao montar ou ajustar a timeline de um teaser, quando o corte "pula", o zoom incomoda, o ritmo está picotado ou arrastado, ou quando pedirem "seja um editor sênior".
---

# Ritmo e corte

As regras abaixo vêm de editores e guias públicos (fontes no fim de cada linha). Onde nenhuma fonte dá número, está
escrito "no olho". O `scripts/montar-timeline.py` já aplica o padrão; aqui está o porquê e o que mexer.

## Corte

| regra | no motor |
|---|---|
| **A emoção decide o corte** e o pensamento termina antes do corte; segure a reação até ele fechar ([regra dos seis, No Film School](https://nofilmschool.com/2016/11/6-rules-good-cutting-according-oscar-winning-editor-walter-murch)) | `respiroDepois` no trecho (0,8–2 s) só nos 3–4 momentos pesados; push de 8 % na reação |
| **Deixar respirar** é escolha, não regra geral ([No Film School](https://nofilmschool.com/2017/12/watch-why-its-important-let-your-edit-breathe)) | pausa > 1,0 s vira 0,6 s; as demais ficam como foram ditas |
| **Borda de palavra:** corte ~0,08 s antes da primeira palavra e ~0,12 s depois da última, nunca pelo volume (no olho, testado) | `ANTES`/`DEPOIS` no `montar-timeline.py` |
| **Imagem 2–4 quadros depois do áudio** que provoca o corte ([Finchley](https://www.finchley.co.uk/finchley-learning/video-engineering-in-a-professional-podcast-post-production-cutting-when-to-cut-and-why)) | `transicao.atrasoImagem = 3` |
| **Corte seco** entre câmeras de entrevista, sem dissolve ([Creative COW](https://creativecow.net/forums/thread/2-camera-interview-2/)) | não existe dissolve no template, de propósito |
| **Fades curtos (5–10 ms) em todo corte de áudio** e room tone por baixo para o silêncio não "furar" ([Sound On Sound](https://www.soundonsound.com/techniques/using-fades-crossfades), [guia de room tone](https://larryjordan.com/?p=141196)) | fade de 1 quadro só onde o som é cortado; troca de câmera no mesmo instante do bruto não leva fade |

## Câmera e tamanho

| regra | no motor |
|---|---|
| **30°:** reenquadre da mesma câmera precisa de salto grande; duas câmeras já cumprem ([30-degree rule](https://en.wikipedia.org/wiki/30-degree_rule)) | com duas câmeras, toda emenda troca de câmera |
| **Em junção de takes, troque câmera ou tamanho** para esconder o jump cut ([PremiumBeat](https://www.premiumbeat.com/blog/5-ways-to-hide-jump-cuts)) | com uma câmera, junção alterna 1,0 / 1,075 |
| **Enquadramento muda em início de frase**: aberto na ideia nova, close na frase de impacto ([Vizard](https://agent.vizard.ai/how-to/stop-the-punch-ins-cycling-too-fast-in-a-talking-head-edit.html), fonte fraca) | plano novo só na fronteira de fala; frase-chave abre plano próprio |
| **Não trocar de ângulo a cada frase;** reenquadrar nas transições de ideia ([MediaStorm](https://www.mediastorm.com/blog/?p=1126)) | um trecho do roteiro = um bloco; cortes só em pausa longa e na chave |
| **Zoom só 100 / 107,5 / 115 %**: cena nova abre a 100 %, jump cut alterna 100/107,5, punch-in de 115 % só na frase-chave. 100 → 170 % a cada corte foi reprovado (parece rotação) | `segmentos[].zoom` = 1 / 1,075 / 1,15 |
| **Push-in lento de 5–10 %** com ease no início e no fim, sem efeito sonoro, nas frases-chave; nada de zoom em todo corte ([PremiumBeat](https://premiumbeat.com/blog/ken-burns-effect-premiere-pro/), [Vashi](https://vashivisuals.com/vashizoom-premiere-pro-preset-effects/)) | `segmentos[].push`: 0,05 na ideia nova e na chave, 0,08 na reação, 0,02 no resto |
| **Dolly zoom precisa de paralaxe** (câmera andando); com câmera parada, só push-in ([Adobe](https://www.adobe.com/creativecloud/video/production/cinematography/camera-shots-and-angles/dolly-zoom-shot.html)) | não usado |

## Resolução e recorte

- Punch-in de 4K num quadro 1080p fica nítido até ~200 %; 110–120 % é seguro ([Adobe Community](https://community.adobe.com/t5/premiere-pro-discussions/using-4k-footage-in-a-1080p-project-for-zooming-purposes-best-way/m-p/8938096)).
  O Studio e o preview usam o proxy 1080p; o export liga `fontes.usarFinal` e lê a fonte cheia (`final-a.mp4`, criada
  pelo `preparar.py` quando o bruto passa de 1080p).
- O 9:16 recorta a câmera 16:9 na altura cheia: sobra ~32 % da largura. Com bruto 1080p o vertical sai ampliado (~2×);
  para vertical final nítido, grave em 4K. `enquadramento.verticalExtra` (1,3) fecha todos os planos do vertical.
- O recorte segue o rosto em todo plano (`segmentos[].rosto`, medido pelo `rostos.py`).

## Sem número em fonte nenhuma (decida no olho e diga que foi no olho)
Velocidade do zoom em %/s, ritmo de cortes de anúncio, quanto esmagar o preto, motion blur.

## Duas câmeras
`scripts/sincronizar.py` mede o atraso pelo áudio (correlação cruzada) e confere a deriva perto do fim. Num caso real a
segunda câmera estava ~52 s à frente e a deriva foi de 3 ms em 20 min (desprezível). O que parecer dessincronia no
Studio confira no render: o player do Studio às vezes engasga onde o render está certo.
