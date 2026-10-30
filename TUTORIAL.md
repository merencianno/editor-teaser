# Tutorial: editar um teaser com o Claude no Mac

Passo a passo para quem nunca usou o repositório. Você vai precisar de um Mac com Apple Silicon (M1 ou mais novo),
uns 15 GB livres e um plano do Claude que inclua o **Claude Code** (Pro ou Max).

> **Antes de tudo: o chat do site claude.ai não serve.** Ele não acessa os arquivos nem roda programas no seu Mac.
> Use o **Claude Code**: o app Claude para Mac, na aba **Code**, ou o comando `claude` no Terminal. O vídeo não é
> enviado a lugar nenhum: fica no seu Mac, e você só diz ao Claude onde ele está.

> **Primeira vez no Mac:** o fluxo foi feito e testado em Linux. No Mac ele deve funcionar, porque os scripts trocam
> sozinhos o que muda, mas você é o primeiro a rodar. Se algo travar, peça ao próprio Claude para corrigir (veja
> [Se der problema](#se-der-problema)).

---

## Parte 1 · Instalar (uma vez só, ~30 min)

### 1. Abrir o Terminal

`Cmd + Espaço`, digite **Terminal**, Enter. Todos os comandos abaixo você **copia, cola no Terminal e aperta Enter**.

### 2. Instalar o Homebrew (o instalador de programas do Mac)

Pule este passo se `brew --version` já responder alguma coisa.

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Ele pede a **senha do Mac** (ao digitar, nada aparece na tela; é normal). No fim, ele mostra duas linhas em "Next
steps" começando com `echo` e `eval`: copie e rode as duas. Feche e abra o Terminal.

### 3. Instalar as ferramentas

```bash
brew install ffmpeg uv node git
```

### 4. Instalar o Claude Code

Opção A, o app: baixe o **Claude para Mac** em [claude.ai/download](https://claude.ai/download), entre com a sua
conta e use a aba **Code**.

Opção B, o Terminal:

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

Feche e abra o Terminal, rode `claude` uma vez e faça o login quando ele pedir.

### 5. Baixar o editor

```bash
git clone https://github.com/merencianno/editor-teaser.git ~/editor-teaser
cd ~/editor-teaser
bash scripts/setup.sh --aquecer
```

O `setup.sh` confere tudo e escreve `ok` para cada ferramenta. Com `--aquecer`, ele já baixa os modelos de
transcrição e de legenda (~4 GB, uma vez só). Se aparecer `FALTA alguma-coisa`, rode `brew install alguma-coisa` e
repita.

Pronto. Daqui em diante é só a Parte 2.

---

## Parte 2 · Editar um vídeo

### 1. Abrir o Claude na pasta do editor

```bash
cd ~/editor-teaser
claude
```

No app: aba **Code**, escolha a pasta `editor-teaser` como projeto.

### 2. Pedir a edição

Escreva `vamos editar ` e **arraste o arquivo do vídeo do Finder para a janela**: o caminho aparece sozinho. Exemplo:

```
vamos editar /Users/voce/Movies/gravacao-bruta.mp4
```

Ajuda dizer junto o que é o vídeo e para quê:

```
vamos editar /Users/voce/Movies/gravacao-bruta.mp4
é um convite para o evento do dia 12; quero um teaser de 1 min para o feed e um vertical para Reels.
a frase mais forte é a da virada, perto do minuto 14.
```

Duas câmeras? Diga qual é a principal e arraste a outra também. Tem trilha? Arraste o arquivo da música. A pergunta
seguinte do Claude é pela trilha e pelo texto da cartela final.

### 3. Esperar a transcrição

Ele prepara o vídeo e transcreve palavra por palavra. No Mac, diga **"use o mlx"** para transcrever na GPU do Mac
(bem mais rápido que a CPU). Uma gravação de 20 min leva alguns minutos.

### 4. Portão 1 · escolher o roteiro (em texto)

O Claude devolve 2 ou 3 roteiros em **AIDA**:

- **Atenção:** um gancho nos primeiros 5 s, falando com quem assiste;
- **Interesse:** o contexto;
- **Desejo:** a virada, a frase-chave;
- **Ação:** o convite (data, link).

Cada bloco traz a fala literal, de onde ela sai no bruto e quanto dura. **Leia como quem lê um roteiro:** troque
bloco, corte frase, peça outra abertura. Nada é renderizado antes do seu "esse".

Pedidos que funcionam:

- "fica com o B, mas abre com a frase do A"
- "corta o bloco 3, ficou longo"
- "a frase-chave é 'eu quase desisti', não a outra"
- "quero menos de 45 s"

### 5. Ajustar no Remotion Studio

Aprovado o roteiro, ele monta a timeline e abre o **Remotion Studio** no navegador (`http://localhost:3123`).

- À esquerda, escolha a composição: `Teaser16x9-…` ou `Teaser9x16-…`.
- **Play, arrastar a agulha, setas para andar quadro a quadro.**
- A aba **Props**, à direita, é o painel de edição. Cada plano, cada pedaço de legenda, o volume da música e o texto
  da cartela é um campo. Mudou, o vídeo atualiza na hora. O ícone de salvar grava a mudança.

Não precisa mexer no painel: pode só falar com o Claude ("a legenda das 0:12 está adiantada", "mais perto no
bloco 2", "a música mais baixa sob a voz") e ele altera.

### 6. Portão 2 · assistir ao preview

Ele renderiza um **preview leve, em 480p**, dos dois formatos, em alguns minutos, e diz onde está o arquivo. Assista
no celular se o destino é o celular. Peça o que mudar, ou diga **"pode exportar"**.

### 7. Export final

Só depois do seu "pode exportar". O arquivo final sai em `~/editor-teaser/trabalho/<projeto>/v1/final-…mp4`
(1080p; peça 2K ou 4K se o bruto tiver resolução para isso). Cada rodada de ajuste vira uma versão nova (`v2`, `v3`…)
e nunca apaga a anterior.

---

## A legenda padrão (vertical)

Ela já vem pronta, sem configurar nada:

- no máximo **2 palavras** por vez;
- aparece **exatamente quando a palavra é falada**;
- **sem animação**, minúscula e sem pontuação (maiúscula só em nome próprio e marca);
- branca, na **altura do pescoço**, logo abaixo da boca, sem tapar o rosto.

Nome de marca com várias palavras fica inteiro. Se um nome sair em minúscula, diga: "X e Y são nomes".

## Quer outro estilo? Mande uma referência

Baixe o vídeo de referência (o arquivo `.mp4` funciona melhor que o link) e diga:

```
quero a legenda igual à deste vídeo: /Users/voce/Downloads/referencia.mp4
```

O Claude mede o que a referência faz (tamanho, posição, palavras por vez, cor, animação) e cria um **estilo irmão**
(por exemplo, `legenda-documentario`), sem mexer no padrão. Ele mostra o que mediu e espera o seu ok antes de usar.
Dali em diante, basta pedir "usa a legenda-documentario".

---

## Se der problema

- **O primeiro recurso é o próprio Claude.** Cole o erro e diga "deu isso, resolve". Ele conhece os scripts.
- **`FALTA ffmpeg` (ou outra):** `brew install ffmpeg` e rode `bash scripts/setup.sh` de novo.
- **Transcrição muito lenta:** peça "use o mlx" ou "use o modelo turbo".
- **Mac esquentando ou render travando:** peça "renderiza com menos núcleos".
- **Disco cheio:** a pasta `~/editor-teaser/trabalho/` guarda os proxies e as versões. Apague os projetos antigos de
  lá; o bruto original nunca é tocado.
- **O Studio não abre:** peça "abre o Studio de novo", ou rode `bash scripts/studio.sh` e acesse
  `http://localhost:3123`.

Achou um problema do Mac e o Claude resolveu? Peça "anota isso nas Adaptações para Mac do README". Assim o próximo
não paga a mesma rodada.

## Atualizar o editor

```bash
cd ~/editor-teaser && git pull
```

## Resumo de bolso

1. `cd ~/editor-teaser && claude`
2. `vamos editar ` + arrastar o vídeo
3. escolher o roteiro em texto
4. ajustar no Studio ou falando
5. assistir ao preview e dizer "pode exportar"
6. pegar o arquivo em `trabalho/<projeto>/`

O racional por trás de cada regra (por que blocos longos, por que esse zoom, por que essa legenda) está no
[README](README.md#por-que-é-assim).
