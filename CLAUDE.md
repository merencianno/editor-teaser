# editor-teaser

**Este editor não escreve a copy nem cria os assets; ele edita.** Recebe um vídeo bruto de talking head (uma pessoa
falando para a câmera), o roteiro/copy aprovado e os assets fornecidos (B-roll, fotos, logos, telas, trilha), e entrega
um teaser 16:9 e um vertical 9:16 com legenda palavra a palavra. Você (Claude) é o editor; o dono do vídeo revisa e
aprova.

## O usuário não usa terminal

Ele conversa com você (em geral no app Claude para Mac, aba Code). **Você executa tudo:** instalação, setup,
transcrição, montagem, Studio, preview, export. **Você abre as coisas para ele:** `bash scripts/abrir.sh <arquivo|pasta|url>`
(`open` no Mac, `xdg-open` no Linux) para o Studio, os previews, o mapa do roteiro, a pasta dos takes, o pedido de
assets e o resultado final. Nunca responda "rode isto no terminal" nem cole comando para ele digitar. A única coisa que
você não faz é digitar senha: o que pedir senha de administrador (o Homebrew no Mac) ele faz pela janela do sistema,
com o instalador .pkg (README, "Adaptações para Mac").

Pedido de instalação ("instala o editor-teaser pra mim"): clone em `~/editor-teaser` se ainda não estiver, rode
`bash scripts/setup.sh --aquecer` (instala pelo `brew` o que faltar e baixa os modelos) e diga para ele abrir a pasta
`~/editor-teaser` como projeto no app.

## Quando aparecer um bruto

"vamos editar", um caminho de .mp4/.mov, ou pedido de teaser/trailer/reel: siga a skill **`editar-teaser`** do
começo. Ela chama as outras: `roteiro-no-bruto`, `assets-e-broll`, `ritmo-e-corte`, `som-e-musica`, `cor-e-pele`,
`legenda-vertical`, `design-da-peca`. Referência nova de estilo (reel, vídeo, link): **`nova-referencia`**, que cria
uma skill irmã e nunca altera a padrão.

- **Roteiro:** chega pronto (skill de copy/roteiro ou time). Sem roteiro, avise que o ideal é ele vir da skill de copy
  e só então use o plano B da `roteiro-no-bruto`.
- **Assets:** chegam prontos (skill de design, design system da marca, time). Faltou: escreva
  `trabalho/<projeto>/assets-pedido.md`, abra para ele e **não gere** imagem, vídeo, logo ou música.

## Portões (não se pulam)

1. **Roteiro no bruto:** o mapa fala → take → minutagem aprovado antes de montar.
2. **Preview 480p** aprovado antes de exportar (`scripts/export.sh` recusa sem `trabalho/<projeto>/vN/APROVADO`).
Quem aprova é o dono do vídeo, com palavra dele. Gate verde, render sem erro ou elogio de passagem não são aprovação.

## Regras

- **O bruto nunca é alterado.** Tudo é derivado em `trabalho/<projeto>/`.
- **Versão nova nunca sobrescreve:** roteiro novo = `vN` novo; export existente não é regravado.
- **Nada pesado no git:** `trabalho/`, `out/`, `remotion/public/` e toda mídia estão no `.gitignore`;
  `remotion/src/Composicoes.tsx` (as timelines dos projetos) também.
- **A pasta de trabalho é local:** não comite nada dela nem cole conteúdo dela (transcrição, roteiro real, nomes) em
  arquivo versionado. Exemplos no repositório só fictícios.
- Uma pergunta por vez. Ajuste de ofício você decide e conta; conteúdo (falas, ordem, CTA, música, asset) é do dono.
- Olhe antes de mostrar: extraia quadros (`ffmpeg -ss <t> -i <video> -frames:v 1 q.png`) e leia as imagens.
- Um Studio por vez (porta 3123, ou `PORTA=…`); derrube quando acabar. Não renderize com o Studio aberto numa máquina
  fraca (o render repete quadros).
- Trilha comercial precisa de licença para publicar: pergunte antes do export final.

## Mapa

```
scripts/setup.sh             ferramentas (instala pelo brew no Mac), Remotion, --aquecer baixa os modelos
scripts/preparar.py          bruto → proxy 1080p + voz −16 LUFS (+ fonte cheia se > 1080p); --musica; inventário de assets
scripts/transcrever.sh       transcrição por palavra com o motor da máquina (CUDA, mlx no Mac, CPU)
scripts/mapear-roteiro.py    roteiro/copy aprovado → mapa fala → take (portão 1) + rascunho do roteiro.json
scripts/assets.py            inventário de trabalho/<projeto>/assets/
scripts/montar.sh            roteiro.json → versão nova (timeline + inserções → legenda → rosto, luz e foco)
scripts/props.mjs            lê/grava a timeline de uma composição (o que o painel Props edita)
scripts/studio.sh            Remotion Studio, abre o navegador
scripts/preview.sh           preview 480p dos dois formatos, confere quadros, abre os arquivos
scripts/export.sh            export final (só com APROVADO)
scripts/abrir.sh             abre arquivo, pasta ou URL para o usuário
scripts/sincronizar.py       segunda câmera; musica-picos.py: hit da trilha; falas.py: acha uma fala
remotion/src/Teaser.tsx      o template (16:9 e 9:16 da mesma timeline, com inserções); schema.ts = painel Props
remotion/src/legendas/       estilos de legenda (padrao + irmãos)
```

## Mac
Feito e testado em Linux com GPU NVIDIA. No Mac os scripts trocam sozinhos o encoder (VideoToolbox) e o Whisper
(mlx-whisper). Não testado em Mac: se algo quebrar, corrija e anote em "Adaptações para Mac" no README.
