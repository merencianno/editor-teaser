# Tutorial: editar um teaser com o Claude no Mac

Passo a passo para quem nunca usou o editor. **Você não vai abrir o Terminal:** tudo é conversa com o Claude, e ele
roda e abre o que for preciso.

**Este editor não escreve a copy nem cria os assets; ele edita.** Você chega com três coisas:

1. o **vídeo bruto** (a gravação da pessoa falando);
2. o **roteiro ou a copy aprovada**, vinda da skill de copy/roteiro ou do time (texto, .md ou .docx);
3. os **assets**: B-roll, fotos, logo, telas e trilha, exportados da skill de design, do design system da sua marca
   ou entregues pelo time.

O editor acha cada fala do roteiro no melhor take do bruto, corta, enquadra, legenda, encaixa os assets e entrega um
**teaser 16:9** e um **vertical 9:16**.

Você vai precisar de um Mac com Apple Silicon (M1 ou mais novo), uns 15 GB livres e um plano do Claude que inclua o
**Claude Code** (Pro ou Max).

> **O chat do site claude.ai não serve.** Ele não acessa os arquivos nem roda programas no seu Mac. Use o **app
> Claude para Mac, na aba Code**. O vídeo não sai do seu Mac: você só diz ao Claude onde ele está.

> **Primeira vez no Mac:** o editor foi feito e testado em Linux. No Mac ele deve funcionar (os scripts trocam
> sozinhos o que muda), mas você é o primeiro a usar. Se algo travar, diga ao Claude "deu isso, resolve".

---

## Parte 1 · Instalar (uma vez só, ~30 min)

### 1. O app do Claude

Baixe o **Claude para Mac** em [claude.ai/download](https://claude.ai/download), arraste para Aplicativos, abra e
entre com a sua conta. Vá para a aba **Code**.

### 2. O Homebrew (o instalador de programas), pelo instalador com janela

O Claude instala o resto sozinho, mas o Homebrew pede a **senha do Mac**, e o Claude não digita senha. Por isso este
passo é seu, com o instalador de janela:

1. Abra [github.com/Homebrew/brew/releases/latest](https://github.com/Homebrew/brew/releases/latest).
2. Em **Assets**, baixe o arquivo que termina em **`.pkg`** (algo como `Homebrew-4.x.x.pkg`).
3. Dê **duplo clique** no arquivo baixado e siga o instalador. A senha do Mac é pedida numa janela; é normal.
4. Se o macOS perguntar sobre as **Ferramentas de Linha de Comando** (Command Line Tools), clique em **Instalar** e
   espere terminar.

Já tem Homebrew? Pule este passo.

### 3. Pedir ao Claude para instalar o editor

No app, aba **Code**, abra uma sessão em qualquer pasta (a sua pasta pessoal serve) e mande:

> instala o editor-teaser pra mim: clona https://github.com/merencianno/editor-teaser em ~/editor-teaser, instala o
> que faltar pelo brew e roda o setup com --aquecer

Ele baixa o editor, instala as ferramentas (ffmpeg, uv, node, git), prepara o Remotion e baixa os modelos de
transcrição e de legenda (~4 GB, uma vez só). Pode levar uns 15 minutos. Se ele pedir para você aprovar comandos,
aprove.

### 4. Abrir o editor como projeto

No app, abra a pasta **`~/editor-teaser`** como projeto (a sua pasta pessoal → `editor-teaser`). É dali que você vai
editar sempre.

Pronto. Daqui em diante é só a Parte 2.

---

## Parte 2 · Editar um vídeo

### 1. Pedir a edição

Na sessão do projeto `editor-teaser`, escreva `vamos editar` e **arraste para a janela**: o vídeo bruto, o arquivo do
roteiro aprovado, os assets (ou a pasta deles) e a trilha. Os caminhos aparecem sozinhos. Diga também para que é:

> vamos editar /Users/voce/Movies/gravacao-bruta.mp4
> o roteiro aprovado é /Users/voce/Documents/roteiro-teaser.docx
> os assets estão em /Users/voce/Documents/assets-teaser (B-roll, logo) e a trilha é /Users/voce/Music/trilha.mp3
> quero um teaser de 1 min para o feed e um vertical para Reels; a cartela final diz "Sábado, 10h"

Duas câmeras? Diga qual é a principal e arraste a outra também. Sem roteiro? Ele pode propor um rascunho a partir das
falas, mas avisa: o ideal é o roteiro vir da skill de copy.

### 2. Esperar a preparação

Ele prepara o vídeo, transcreve palavra por palavra (no Mac, na GPU do próprio Mac) e confere a lista de assets.
Uma gravação de 20 min leva alguns minutos.

### 3. Portão 1 · o roteiro no bruto

O Claude devolve o **mapa**: para cada fala do roteiro, o take escolhido no bruto (minutagem e duração), se a fala bate
com a copy (✅ fiel, ⚠ parecida, ❌ o bruto não tem), onde entram corte, respiro e o hit da música. Ele abre uma pasta
com **o áudio de cada take**: ouça, principalmente os ⚠ e os nomes próprios.

Pedidos que funcionam:

- "na fala 3 usa o outro take, o do minuto 12"
- "a fala 5 não existe no bruto: troca por aquela parecida do minuto 8"
- "corta a fala 6, ficou longo"
- "a frase-chave do bloco 2 é 'eu quase desisti'"

Se o roteiro pedir um asset que não veio, ele escreve a **lista de pedidos** (`assets-pedido.md`, aberta para você):
o que pedir, para qual fala, em que formato e duração. Leve à skill de design ou ao time; ele não gera imagem.

Nada é montado antes do seu "pode montar".

### 4. Ajustar no Remotion Studio

Ele monta o vídeo e abre o **Remotion Studio** no navegador.

- À esquerda, escolha a versão: `Teaser16x9-…` ou `Teaser9x16-…`.
- **Play, arrastar a agulha, setas para andar quadro a quadro.**
- A aba **Props**, à direita, é o painel de edição: planos, B-roll e logo (`insercoes`), cada pedaço de legenda, o
  volume da música e o texto da cartela. Mudou, o vídeo atualiza na hora; o ícone de salvar grava.

Não precisa mexer no painel: fale com ele.

> a legenda das 0:12 está adiantada · mais perto no bloco 2 · o B-roll do vaso entra meio segundo depois · logo menor ·
> a música mais baixa sob a voz

### 5. Portão 2 · assistir ao preview

Ele renderiza um **preview leve, em 480p**, dos dois formatos, em alguns minutos, e abre os vídeos para você.
Assista no celular se o destino é o celular. Peça o que mudar, ou diga **"pode exportar"**.

### 6. Export final

Só depois do seu "pode exportar". Ele exporta em 1080p (peça 2K ou 4K se o bruto tiver resolução para isso) e abre a
pasta com os arquivos finais. Cada rodada de ajuste vira uma versão nova (`v2`, `v3`…) e nunca apaga a anterior.

---

## A legenda padrão (vertical)

Ela já vem pronta, sem configurar nada:

- no máximo **2 palavras** por vez;
- aparece **exatamente quando a palavra é falada**;
- **sem animação**, minúscula e sem pontuação (maiúscula só em nome próprio e marca);
- branca, na **altura do pescoço**, logo abaixo da boca, sem tapar o rosto. B-roll e logo nunca a tiram do lugar.

Nome de marca com várias palavras fica inteiro. Se um nome sair em minúscula, diga: "X e Y são nomes".

## Quer outro estilo? Mande uma referência

Baixe o vídeo de referência (o arquivo `.mp4` funciona melhor que o link), arraste para a janela e diga:

> quero a legenda igual à deste vídeo

O Claude mede o que a referência faz (tamanho, posição, palavras por vez, cor, animação) e cria um **estilo irmão**
(por exemplo, `legenda-documentario`), sem mexer no padrão. Ele mostra o que mediu e espera o seu ok antes de usar.
Dali em diante, basta pedir "usa a legenda-documentario".

---

## Se der problema

Tudo se resolve pedindo ao Claude:

- **Qualquer erro:** "deu isso, resolve" (cole a mensagem, ou só descreva).
- **Faltando ferramenta:** "instala o que falta e roda o setup de novo".
- **Transcrição muito lenta:** "usa o modelo turbo".
- **Mac esquentando ou render travando:** "renderiza com menos núcleos".
- **Disco cheio:** "apaga os projetos antigos da pasta trabalho" (o bruto original nunca é tocado).
- **O Studio não abriu:** "abre o Studio de novo".
- **Não achou o arquivo final:** "abre a pasta do export".

Achou um problema do Mac e o Claude resolveu? Peça "anota isso nas Adaptações para Mac do README". Assim o próximo
não paga a mesma rodada.

## Atualizar o editor

> atualiza o editor-teaser

## Resumo de bolso

1. Abrir o projeto `editor-teaser` no app (aba Code).
2. `vamos editar` + arrastar o vídeo, o roteiro aprovado, os assets e a trilha.
3. Aprovar o mapa do roteiro no bruto (ouvir os takes).
4. Ajustar no Studio ou falando.
5. Assistir ao preview e dizer "pode exportar".
6. Pegar os arquivos na pasta que ele abrir.

O racional por trás de cada regra (por que blocos longos, por que esse zoom, por que essa legenda) está no
[README](README.md#por-que-é-assim). Quem prefere o terminal acha os comandos no README, em "Para quem prefere o
terminal".
