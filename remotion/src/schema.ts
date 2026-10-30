// Schema da timeline. É ele que monta o painel "Props" do Remotion Studio (lado direito): cada campo vira um
// controle, e o botão de salvar grava os valores em src/Composicoes.tsx (a timeline de verdade de cada versão).
import { z } from "zod";

const seg = z.number().min(0);
const rgb = z.tuple([z.number().min(0.5).max(2), z.number().min(0.5).max(2), z.number().min(0.5).max(2)]);
const ponto = z.tuple([z.number().min(0).max(1), z.number().min(0).max(1)]);

export const camera = z.object({
  arquivo: z.string().describe("proxy em public/ (Studio e preview)"),
  arquivoFinal: z.string().describe("fonte em resolução cheia, usada só no export (vazio = o próprio proxy)"),
  offset: z.number().describe("s: tempo nesta câmera = tempo na voz + offset (0 na câmera da voz)"),
  ganho: rgb.describe("ganho R, G, B: casa esta câmera na outra pela pele (medido pelo rostos.py)"),
  rosto: ponto.describe("onde o rosto costuma ficar (x, y de 0 a 1); cada plano pode ter o seu"),
});

export const segmento = z.object({
  bloco: z.string().describe("parte da AIDA (só rótulo)"),
  de: seg.describe("início no bruto (s, tempo da voz)"),
  ate: seg.describe("fim no bruto (s, tempo da voz)"),
  camera: z.enum(["a", "b"]),
  zoom: z.number().min(1).max(1.4).describe("1 = aberto (ideia nova); 1,075 = jump cut; 1,15 = punch-in da frase-chave"),
  push: z.number().min(-0.1).max(0.1).describe("aproximação lenta ao longo do plano (0,05 = entra 5 %; negativo afasta)"),
  chave: z.boolean().describe("frase-chave do bloco (punch-in e hit da música)"),
  rosto: ponto.optional().describe("centro do rosto neste plano (rostos.py)"),
  exposicao: z.number().min(0.6).max(1.6).optional().describe("ganho de luz deste plano (casa a luz entre takes)"),
});

export const pedacoLegenda = z.object({
  bruto: seg.describe("quando aparece, no tempo da voz (s): segue o corte"),
  fim: seg.describe("quando sai, no tempo da voz (s)"),
  texto: z.string().describe("no máximo 2 palavras, minúscula, sem pontuação"),
});

export const insercao = z.object({
  asset: z.string().describe("arquivo em public/<projeto>/assets/ (fornecido: o editor não gera asset)"),
  tipo: z.enum(["imagem", "video"]),
  alfa: z.boolean().describe("asset com transparência (PNG, WebM VP9 ou ProRes 4444)"),
  bruto: seg.describe("entra quando esta fala é dita (tempo da voz, s): segue o corte"),
  dur: z.number().min(0.3).max(30).describe("quanto fica (s): corte rápido 2–4 s, sequência 6–8 s"),
  modo: z.enum(["cheio", "sobreposto", "lado"]).describe("cheio cobre o quadro; sobreposto = PNG por cima; lado = metade (no 9:16 vira cheio)"),
  movimento: z.enum(["parado", "push"]),
  push: z.number().min(0).max(0.15).describe("aproximação ao longo da inserção (0,05–0,10)"),
  inicioClipe: z.number().min(0).describe("de onde o clipe começa (s): corte pela ação do clipe"),
  foco: ponto.describe("ponto de interesse do asset: o recorte (principalmente o 9:16) centra nele"),
  ajuste: z.enum(["cobrir", "conter"]),
  posicao: z.object({ x: z.number().min(0).max(1), y: z.number().min(0).max(1), largura: z.number().min(0.05).max(1) })
    .describe("sobreposto: centro (x, y de 0 a 1) e largura (fração do quadro); fora do rosto e da legenda"),
});

export const timeline = z.object({
  projeto: z.string(),
  formato: z.enum(["16x9", "9x16"]),
  fps: z.number().int(),
  fontes: z.object({
    voz: z.string().describe("voz tratada (−16 LUFS) em public/"),
    usarFinal: z.boolean().describe("liga só no export: troca os proxies pelas fontes em resolução cheia"),
  }),
  cameras: z.object({ a: camera, b: camera.optional() }),
  transicao: z.object({
    atrasoImagem: z.number().int().min(0).max(8).describe("a imagem troca N quadros depois do áudio (2–4)"),
  }),
  enquadramento: z.object({
    verticalExtra: z.number().min(1).max(2).describe("no 9:16 todo plano fica N× mais fechado que no 16:9"),
    alturaRosto: z.number().min(0.25).max(0.6).describe("altura do rosto no quadro quando há folga para centrar (0 = topo)"),
  }),
  cor: z.object({
    contraste: z.number().min(0.8).max(1.3),
    luz: z.number().min(0.7).max(1.8).describe("ganho de luz geral"),
    arco: z.object({
      inicio: z.object({ temperatura: z.number().min(-0.2).max(0.2), saturacao: z.number().min(0.5).max(1.5) }),
      fim: z.object({ temperatura: z.number().min(-0.2).max(0.2), saturacao: z.number().min(0.5).max(1.5) }),
    }).describe("grade ao longo do vídeo: começa frio e contido, termina quente (− azul, + quente)"),
  }),
  abertura: z.number().min(0).max(4).describe("o vídeo nasce do preto em N s (0 = corte seco)"),
  segmentos: z.array(segmento),
  insercoes: z.array(insercao).describe("B-roll e assets fornecidos, ancorados na fala; o áudio da fala segue por baixo"),
  legenda: z.object({
    mostrar: z.boolean(),
    estilo: z.string().describe("padrao ou um estilo criado pela skill nova-referencia (remotion/src/legendas)"),
    tamanho: z.number().min(24).max(140).describe("px na largura de 1080 (86 aprovado no 9:16)"),
    peso: z.number().min(300).max(800),
    topo: z.number().min(0.4).max(0.9).describe("altura do topo da legenda (0,6 = pescoço, logo abaixo da boca)"),
    cor: z.string(),
  }),
  legendas: z.array(pedacoLegenda),
  musica: z.object({
    arquivo: z.string().describe("trilha em public/ (vazio = sem música)"),
    emTimeline: z.number().describe("onde o início da faixa cai na timeline (negativo = a faixa começa antes)"),
    volumeSobFala: z.number().min(0).max(1).describe("trilha sob a voz (ducking)"),
    volumeCheio: z.number().min(0).max(1).describe("trilha sem voz (depois da última fala)"),
    ajustes: z.array(z.object({
      emTimeline: z.number(), dur: z.number().min(0),
      ganho: z.number().min(0).max(4).describe("< 1 cai (turn line), > 1 sobe (hit)"),
      rampa: z.number().min(0.2).max(5).describe("rampa com easing, sem degrau"),
    })),
  }),
  cta: z.object({
    duracao: z.number().min(0).max(12).describe("cartela final depois da última fala (s); 0 = sem cartela"),
    titulo: z.string(), linha: z.string(), botao: z.string(),
    mostrarBotao: z.boolean(),
    marcas: z.array(z.string()).describe("nomes que nunca quebram linha (marca, produto)"),
  }),
});

export type Timeline = z.infer<typeof timeline>;
