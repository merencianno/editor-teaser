// Teaser de talking head, 16:9 e 9:16 a partir da mesma timeline (props, editáveis no painel "Props" do Studio).
// Regras de edição (.claude/skills/ritmo-e-corte): corte seco com a imagem 2–4 quadros depois do áudio; zoom 1 / 1,075
// / 1,15 com push-in lento e easing; o recorte segue o rosto; fades de 1 quadro só onde o som é cortado; música com
// ducking e rampas; legenda de até 2 palavras no tempo da fala (.claude/skills/legenda-vertical).
import { loadFont } from "@remotion/google-fonts/InstrumentSans";
import { createContext, useContext, useMemo } from "react";
import {
  AbsoluteFill, Audio, Easing, Img, OffthreadVideo, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig,
} from "remotion";
import { ESTILOS } from "./legendas";
import type { Timeline } from "./schema";

const { fontFamily: SANS } = loadFont("normal", { weights: ["400", "500", "600", "700"], subsets: ["latin", "latin-ext"] });

type Seg = Timeline["segmentos"][number] & { emTimeline: number; contAntes: boolean; contDepois: boolean };
const suave = Easing.inOut(Easing.sin);
const lim = (x: number, a: number, b: number) => Math.max(a, Math.min(b, x));

function derivar(tl: Timeline) {
  const fps = tl.fps;
  const f = (s: number) => Math.round(s * fps);
  let t = 0;
  const base = tl.segmentos.map((s) => { const r = { ...s, emTimeline: t }; t += Math.max(0, s.ate - s.de); return r; });
  const SEGS: Seg[] = base.map((s, i) => ({
    ...s,
    // mesmo instante do bruto dos dois lados: troca de câmera/zoom sem corte de som (não leva fade)
    contAntes: i > 0 && Math.abs(base[i - 1].ate - s.de) < 0.02,
    contDepois: i < base.length - 1 && Math.abs(base[i + 1].de - s.ate) < 0.02,
  }));
  const FIM_FALA = t;
  const DURACAO = FIM_FALA + tl.cta.duracao;
  // tempo da voz → tempo na timeline (null = trecho que saiu no corte)
  const naTimeline = (b: number) => {
    const s = SEGS.find((x) => x.de - 0.05 <= b && b < x.ate);
    return s ? s.emTimeline + Math.max(0, b - s.de) : null;
  };
  return { tl, fps, f, SEGS, FIM_FALA, DURACAO, naTimeline };
}
export const duracaoEmQuadros = (tl: Timeline) => Math.max(1, Math.round(derivar(tl).DURACAO * tl.fps));

const Ctx = createContext<ReturnType<typeof derivar> | null>(null);
const useTl = () => useContext(Ctx)!;

// ── cor por câmera: ganho R/G/B (casa a pele), arco de temperatura/saturação ao longo do vídeo, contraste no meio ──
const Filtros: React.FC = () => {
  const { tl, fps, DURACAO } = useTl();
  const fr = useCurrentFrame();
  const c = tl.cor.contraste, k = 0.5 - 0.5 * c;
  const a = tl.cor.arco, p = lim(fr / fps / Math.max(1, DURACAO), 0, 1);
  const temp = a.inicio.temperatura + (a.fim.temperatura - a.inicio.temperatura) * suave(p);
  const sat = a.inicio.saturacao + (a.fim.saturacao - a.inicio.saturacao) * suave(p);
  const matriz = (g: number[]) => {
    const R = g[0] * (1 + temp), G = g[1], B = g[2] * (1 - temp);
    const l = [0.2126, 0.7152, 0.0722].map((x) => x * (1 - sat)); // saturação pela luma Rec.709
    const linha = (i: number) => [0, 1, 2].map((j) => ((l[j] + (i === j ? sat : 0)) * [R, G, B][j]).toFixed(4)).join(" ");
    return `${linha(0)} 0 0  ${linha(1)} 0 0  ${linha(2)} 0 0  0 0 0 1 0`;
  };
  return (
    <svg width="0" height="0" style={{ position: "absolute" }}>
      {(["a", "b"] as const).map((id) => {
        const cam = tl.cameras[id];
        if (!cam) return null;
        return (
          <filter key={id} id={`cor-${id}`} colorInterpolationFilters="sRGB">
            <feColorMatrix type="matrix" values={matriz(cam.ganho)} />
            <feComponentTransfer>
              <feFuncR type="linear" slope={c} intercept={k} /><feFuncG type="linear" slope={c} intercept={k} />
              <feFuncB type="linear" slope={c} intercept={k} />
            </feComponentTransfer>
          </filter>
        );
      })}
    </svg>
  );
};

// ── um plano: câmera, zoom com push suave, recorte que segue o rosto ──
// `caixa`: tamanho da área onde o plano é desenhado (padrão: o quadro inteiro; no modo "lado" do B-roll, metade dele).
// `desloca`: segundos a mais no bruto (o plano começa no meio do segmento).
const Plano: React.FC<{ s: Seg; atraso: number; dur: number; caixa?: { w: number; h: number }; desloca?: number }> = ({ s, atraso, dur, caixa, desloca = 0 }) => {
  const { tl, f } = useTl();
  const frame = useCurrentFrame();
  const quadro = useVideoConfig();
  const { w: width, h: height } = caixa ?? { w: quadro.width, h: quadro.height };
  const cam = tl.cameras[s.camera] ?? tl.cameras.a;
  const id = tl.cameras[s.camera] ? s.camera : "a";
  // r = quantas larguras do quadro a câmera 16:9 ocupa quando preenche a altura (1 no 16:9; ≈3,16 no 9:16)
  const r = Math.max(1, (16 / 9) / (width / height));
  const vertical = r > 1;
  const push = interpolate(frame, [0, Math.max(1, dur)], [1, 1 + s.push], { easing: suave, extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const z = s.zoom * push * (vertical ? tl.enquadramento.verticalExtra : 1);
  const [px, py] = s.rosto ?? cam.rosto;
  const limY = (z - 1) / 2, limX = (z * r - 1) / 2;
  const tx = lim(-(px - 0.5) * z * r, -limX, limX);
  const ty = lim(tl.enquadramento.alturaRosto - 0.5 - (py - 0.5) * z, -limY, limY);
  const arquivo = tl.fontes.usarFinal && cam.arquivoFinal ? cam.arquivoFinal : cam.arquivo;
  return (
    <AbsoluteFill style={{ backgroundColor: "#000", overflow: "hidden" }}>
      {/* A câmera inteira antes do pan: com width 100 % + cover o navegador já cortaria o 9:16 no centro e o pan até
          um rosto fora do centro mostraria uma faixa preta. Largura r×100 %, centrada; o pan entra como tx / r. */}
      <OffthreadVideo src={staticFile(arquivo)} muted trimBefore={Math.max(0, f(s.de + cam.offset + desloca) + atraso)}
        style={{ position: "absolute", top: 0, left: `${(-(r - 1) / 2) * 100}%`, width: `${r * 100}%`, height: "100%",
          objectFit: "cover", filter: `url(#cor-${id}) brightness(${(s.exposicao ?? 1) * tl.cor.luz})`,
          transform: `translate(${(tx / r) * 100}%, ${ty * 100}%) scale(${z})` }} />
    </AbsoluteFill>
  );
};

// ── voz contínua; fade de 1 quadro só onde há corte de som (evita o clique) ──
const Voz: React.FC<{ s: Seg; d: number }> = ({ s, d }) => {
  const { tl, f } = useTl();
  const a = s.contAntes ? 0 : 1, b = s.contDepois ? 0 : 1;
  return (
    <Audio src={staticFile(tl.fontes.voz)} trimBefore={f(s.de)}
      volume={(fr) => Math.min(a ? Math.min(1, fr / a) : 1, b ? Math.min(1, (d - fr) / b) : 1)} />
  );
};

// ── música: uma faixa contínua; ducking sob a fala, cheia depois; ajustes com rampa (turn line, hit) ──
const Musica: React.FC = () => {
  const { tl, fps, f, FIM_FALA, DURACAO } = useTl();
  const m = tl.musica;
  if (!m.arquivo) return null;
  const corta = Math.max(0, -m.emTimeline);
  const comeca = Math.max(0, m.emTimeline);
  return (
    <Sequence from={f(comeca)} durationInFrames={Math.max(1, f(DURACAO - comeca))}>
      <Audio src={staticFile(m.arquivo)} trimBefore={f(corta)}
        volume={(fr) => {
          const tg = comeca + fr / fps;
          const entra = interpolate(fr / fps, [0, 1.5], [0, 1], { extrapolateRight: "clamp" });
          const nivel = interpolate(tg, [FIM_FALA - 0.3, FIM_FALA + 1.2], [m.volumeSobFala, m.volumeCheio],
            { easing: suave, extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          const sai = interpolate(tg, [DURACAO - 2.5, DURACAO], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          const aj = m.ajustes.reduce((g, a) => g * (1 + (a.ganho - 1) * interpolate(tg,
            [a.emTimeline - a.rampa, a.emTimeline, a.emTimeline + a.dur, a.emTimeline + a.dur + a.rampa], [0, 1, 1, 0],
            { easing: suave, extrapolateLeft: "clamp", extrapolateRight: "clamp" })), 1);
          return Math.min(1, entra * nivel * sai * aj);
        }} />
    </Sequence>
  );
};

// ── abertura: nasce do preto ──
const Abertura: React.FC = () => {
  const { tl, f } = useTl();
  const fr = useCurrentFrame();
  if (!tl.abertura || fr > f(tl.abertura)) return null;
  const o = interpolate(fr, [0, f(tl.abertura)], [1, 0], { easing: Easing.out(Easing.cubic), extrapolateRight: "clamp" });
  return <AbsoluteFill style={{ backgroundColor: "#000", opacity: o }} />;
};

// nome de marca nunca quebra: os espaços dele viram inquebráveis
const inteiro = (txt: string, marcas: string[]) =>
  marcas.filter(Boolean).reduce((t, m) => t.split(m).join(m.replace(/ /g, " ")), txt);

// ── cartela final: fundo preto, um título, uma linha, no máximo um CTA; legível em menos de 3 s ──
const Cta: React.FC = () => {
  const { tl, f, FIM_FALA } = useTl();
  const fr = useCurrentFrame();
  const { durationInFrames, width, height } = useVideoConfig();
  const c = tl.cta;
  if (c.duracao <= 0) return null;
  const ini = f(FIM_FALA) - 4;
  if (fr < ini) return null;
  const vertical = width < height;
  const k = (de: number) => interpolate(fr - ini, [de, de + 14], [0, 1], { easing: suave, extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const sai = interpolate(fr, [durationInFrames - 18, durationInFrames], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const u = Math.min(width, height) / 1080; // escala pelo lado menor
  return (
    <AbsoluteFill style={{ opacity: sai }}>
      <AbsoluteFill style={{ backgroundColor: "#000", opacity: k(0) }} />
      {/* 9:16: o texto fica na faixa segura (UI de Reels/TikTok/Shorts cobre o topo, a base e a direita) */}
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column", textAlign: "center",
        color: "#fff", fontFamily: SANS, padding: vertical ? `${height * 0.14}px ${width * 0.11}px ${height * 0.25}px` : `0 ${width * 0.12}px` }}>
        <h1 style={{ opacity: k(6), margin: 0, fontWeight: 600, fontSize: (vertical ? 78 : 92) * u, lineHeight: 1.05,
          letterSpacing: "-0.02em", textWrap: "balance" }}>{inteiro(c.titulo, c.marcas)}</h1>
        {c.linha && (
          <p style={{ opacity: k(12), margin: `${28 * u}px 0 0`, fontWeight: 400, fontSize: (vertical ? 40 : 34) * u,
            lineHeight: 1.3, letterSpacing: "0", textWrap: "balance", color: "rgb(255 255 255 / 0.86)" }}>
            {inteiro(c.linha, c.marcas)}
          </p>
        )}
        {c.mostrarBotao && c.botao && (
          <span style={{ opacity: k(18), marginTop: 44 * u, display: "inline-flex", alignItems: "center", height: 72 * u,
            padding: `0 ${40 * u}px`, borderRadius: 999, border: `${2 * u}px solid #fff`, fontSize: 26 * u,
            fontWeight: 600, letterSpacing: "0.04em", textTransform: "uppercase" }}>{inteiro(c.botao, c.marcas)}</span>
        )}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ── B-roll e assets fornecidos (o editor manipula, não gera): por cima da fala, que continua por baixo ──
type Ins = Timeline["insercoes"][number];
const Insercao: React.FC<{ x: Ins; ini: number; dur: number }> = ({ x, ini, dur }) => {
  const { tl, f, fps, SEGS } = useTl();
  const fr = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const vertical = width < height;
  const k = x.movimento === "push" ? interpolate(fr, [0, Math.max(1, dur)], [1, 1 + x.push], { easing: suave, extrapolateLeft: "clamp", extrapolateRight: "clamp" }) : 1;
  const midia = (estilo: React.CSSProperties) => x.tipo === "video"
    ? <OffthreadVideo src={staticFile(x.asset)} muted transparent={x.alfa} trimBefore={f(x.inicioClipe)} style={estilo} />
    : <Img src={staticFile(x.asset)} style={estilo} />;
  const cheio = () => midia({ position: "absolute", width: "100%", height: "100%",
    objectFit: x.ajuste === "conter" ? "contain" : "cover", objectPosition: `${x.foco[0] * 100}% ${x.foco[1] * 100}%`,
    transform: `scale(${k})`, transformOrigin: `${x.foco[0] * 100}% ${x.foco[1] * 100}%` });
  // "lado" só existe no 16:9: a pessoa fica na metade dela, o asset na outra. No 9:16 não há lado: vira "cheio".
  if (x.modo === "cheio" || (x.modo === "lado" && vertical)) {
    return <AbsoluteFill style={{ backgroundColor: "#000", overflow: "hidden" }}>{cheio()}</AbsoluteFill>;
  }
  if (x.modo === "lado") {
    const metade = { w: width / 2, h: height };
    const t0 = ini / fps;
    // a fala por baixo continua: desenha, na metade esquerda, o plano de cada segmento que o B-roll atravessa
    const pedacos = SEGS.filter((s) => s.emTimeline < t0 + dur / fps && s.emTimeline + s.ate - s.de > t0);
    return (
      <AbsoluteFill style={{ backgroundColor: "#000" }}>
        <div style={{ position: "absolute", left: 0, top: 0, width: "50%", height: "100%", overflow: "hidden" }}>
          {pedacos.map((s, i) => {
            const de = Math.max(0, f(s.emTimeline) - ini), ate = Math.min(dur, f(s.emTimeline + s.ate - s.de) - ini);
            return (
              <Sequence key={i} from={de} durationInFrames={Math.max(1, ate - de)}>
                <Plano s={{ ...s, push: 0 }} atraso={0} dur={ate - de} caixa={metade} desloca={Math.max(0, t0 - s.emTimeline)} />
              </Sequence>
            );
          })}
        </div>
        <div style={{ position: "absolute", left: "50%", top: 0, width: "50%", height: "100%", overflow: "hidden" }}>{cheio()}</div>
      </AbsoluteFill>
    );
  }
  // sobreposto: PNG transparente (logo, selo, tela) numa posição que não tapa rosto nem legenda
  const p = x.posicao, w = p.largura * width;
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: p.x * width - w / 2, top: p.y * height, width: w, transform: `translateY(-50%) scale(${k})` }}>
        {midia({ width: "100%", height: "auto", display: "block" })}
      </div>
    </AbsoluteFill>
  );
};

export const Teaser: React.FC<Timeline> = (props) => {
  const d = useMemo(() => derivar(props), [props]);
  const { tl, f, SEGS, FIM_FALA, naTimeline } = d;
  const atraso = tl.transicao.atrasoImagem;
  const Legenda = ESTILOS[tl.legenda.estilo] ?? ESTILOS.padrao;
  return (
    <Ctx.Provider value={d}>
      <AbsoluteFill style={{ backgroundColor: "#000" }}>
        <Filtros />
        {SEGS.map((s, i) => {
          // a imagem troca `atraso` quadros depois do áudio que provoca o corte
          const de = f(s.emTimeline) + (i ? atraso : 0);
          const ate = i < SEGS.length - 1 ? f(SEGS[i + 1].emTimeline) + atraso : f(FIM_FALA);
          return (
            <Sequence key={`v${i}`} from={de} durationInFrames={Math.max(1, ate - de)}>
              <Plano s={s} atraso={i ? atraso : 0} dur={ate - de} />
            </Sequence>
          );
        })}
        {SEGS.map((s, i) => {
          const de = f(s.emTimeline), dur = f(s.emTimeline + s.ate - s.de) - de;
          return <Sequence key={`a${i}`} from={de} durationInFrames={Math.max(1, dur)}><Voz s={s} d={dur} /></Sequence>;
        })}
        <Musica />
        {tl.insercoes.map((x, i) => {
          const ini = naTimeline(x.bruto);
          if (ini === null) return null;
          const de = f(ini), dur = Math.max(2, Math.min(f(x.dur), f(FIM_FALA) - de));
          return <Sequence key={`b${i}`} from={de} durationInFrames={dur}><Insercao x={x} ini={de} dur={dur} /></Sequence>;
        })}
        {tl.legenda.mostrar && tl.legendas.map((c, i) => {
          const ini = naTimeline(c.bruto);
          if (ini === null) return null;
          const prox = tl.legendas.slice(i + 1).map((n) => naTimeline(n.bruto)).find((x) => x !== null);
          // duração mínima de 2 quadros e nunca por cima da seguinte
          const dur = Math.max(2, Math.min(f(c.fim - c.bruto), prox != null ? f(prox) - f(ini) : Infinity, f(FIM_FALA) - f(ini)));
          return <Sequence key={`l${i}`} from={f(ini)} durationInFrames={dur}><Legenda texto={c.texto} estilo={tl.legenda} fonte={SANS} /></Sequence>;
        })}
        <Abertura />
        <Cta />
      </AbsoluteFill>
    </Ctx.Provider>
  );
};
