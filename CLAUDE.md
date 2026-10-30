# editor-teaser

Repositório-ferramenta: transforma um vídeo bruto de talking head (uma pessoa falando para a câmera) num teaser 16:9 e
num vertical 9:16 com legenda palavra a palavra. Você (Claude) é o primeiro editor; o dono do vídeo revisa e aprova.

## Quando aparecer um bruto

Se o usuário disser "vamos editar", mandar um caminho de .mp4/.mov, ou pedir teaser/trailer/reel de um vídeo, siga a
skill **`editar-teaser`** (`.claude/skills/editar-teaser/SKILL.md`) do começo. Ela chama as outras na hora certa:
`roteiro-aida`, `ritmo-e-corte`, `som-e-musica`, `cor-e-pele`, `legenda-vertical`, `design-da-peca`. Se ele mandar uma
referência nova (reel, vídeo, link) como modelo, use **`nova-referencia`**: ela cria uma skill irmã e nunca altera a
padrão.

## Portões (não se pulam)

1. **Roteiro em texto** aprovado antes de montar.
2. **Preview 480p** aprovado antes de exportar (`scripts/export.sh` recusa sem `trabalho/<projeto>/vN/APROVADO`).
Quem aprova é o dono do vídeo, com palavra dele. Gate verde, render sem erro ou elogio de passagem não são aprovação.

## Regras

- **O bruto nunca é alterado.** Tudo é derivado em `trabalho/<projeto>/`.
- **Versão nova nunca sobrescreve:** roteiro novo = `vN` novo; export existente não é regravado.
- **Nada pesado no git:** `trabalho/`, `out/`, `remotion/public/` e toda mídia (`*.mp4 *.mov *.wav *.m4a *.mp3…`) estão
  no `.gitignore`. `remotion/src/Composicoes.tsx` (as timelines dos projetos) também fica fora.
- **A pasta de trabalho é local:** não comite nada dela, não cole conteúdo dela em arquivo versionado (transcrição,
  roteiro real, nomes). Exemplos no repositório só fictícios (`exemplos/`).
- Uma pergunta por vez. Ajuste de ofício você decide e conta; conteúdo (falas, ordem, CTA, música) é do dono.
- Olhe antes de mostrar: extraia quadros (`ffmpeg -ss <t> -i <video> -frames:v 1 q.png`) e leia as imagens.
- Um servidor por vez: o Studio sobe com `bash scripts/studio.sh` (porta 3123, ou `PORTA=…`); derrube quando acabar.
  Nunca rode `preview.sh` com o Studio aberto numa máquina fraca (o render repete quadros).
- Trilha comercial precisa de licença para publicar: pergunte antes do export final.

## Mapa

```
scripts/preparar.py        bruto → proxy 1080p (GOP 15) + voz −16 LUFS (+ fonte cheia se > 1080p); --musica
scripts/transcrever.py     faster-whisper large-v3 por palavra → palavras.json + transcricao.md
scripts/falas.py           acha uma fala (minutagem aproximada + começo do texto) → início/fim exatos
scripts/sincronizar.py     segunda câmera: atraso pelo áudio + proxy
scripts/montar.sh          roteiro.json → versão nova (montar-timeline → legendas → rostos)
scripts/props.mjs          lê/grava a timeline de uma composição (o que o painel Props edita)
scripts/studio.sh          Remotion Studio
scripts/preview.sh         preview 480p dos dois formatos + conferência de quadros
scripts/export.sh          export final (só com APROVADO)
scripts/musica-picos.py    candidatos a hit/stopdown numa trilha
remotion/src/Teaser.tsx    o template (16:9 e 9:16 da mesma timeline); schema.ts = campos do painel
remotion/src/legendas/     estilos de legenda (padrao + irmãos)
```

## Mac
O fluxo foi feito e testado em Linux com GPU NVIDIA. No Mac os scripts trocam sozinhos o encoder (VideoToolbox) e o
Whisper cai para a CPU; os comandos que mudam estão no README, seção "Adaptações para Mac". Essa parte não foi testada.
