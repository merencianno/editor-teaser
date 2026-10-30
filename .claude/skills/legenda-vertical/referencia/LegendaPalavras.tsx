// Legenda padrão em Remotion, autônoma (para levar a outro projeto). Neste repositório o mesmo desenho está em
// remotion/src/legendas/Padrao.tsx. Um <Sequence> por pedaço de quebrar.py, com `ini`/`fim` já convertidos para a
// timeline do vídeo; o componente só desenha. Sem animação: entra e sai seca, junto com a fala.
// Medidas para 1080×1920.
import { AbsoluteFill, Sequence, useVideoConfig } from "remotion";

export const ESTILO = {
  fonte: "Instrument Sans",   // uma sans da marca; na falta, Inter ou Helvetica Neue
  tamanho: 86,                // px na largura de 1080 (100 ficou grande e tapava a boca)
  peso: 550,                  // 600 ficou pesado
  topo: 0.6,                  // fração da altura: pescoço, logo abaixo da boca (0,55 tapava a boca)
  tracking: "-0.015em",
  sombra: "0 2px 6px rgb(0 0 0 / 0.55), 0 0 30px rgb(0 0 0 / 0.35)",
};

export const LegendaPalavras: React.FC<{ texto: string }> = ({ texto }) => {
  const { width } = useVideoConfig();
  return (
    <AbsoluteFill style={{ alignItems: "center" }}>
      <p style={{ position: "absolute", top: `${ESTILO.topo * 100}%`, margin: 0, fontFamily: ESTILO.fonte,
        fontWeight: ESTILO.peso, fontSize: ESTILO.tamanho * (width / 1080), lineHeight: 1.05, letterSpacing: ESTILO.tracking,
        color: "#fff", textAlign: "center", maxWidth: width * 0.86, whiteSpace: "nowrap", textShadow: ESTILO.sombra }}>{texto}</p>
    </AbsoluteFill>
  );
};

// pedaços com ini/fim em segundos NA TIMELINE; duração mínima de 2 quadros (1 quadro quebra interpolações)
export const Legendas: React.FC<{ pedacos: { texto: string; ini: number; fim: number }[]; fps: number }> = ({ pedacos, fps }) => (
  <>
    {pedacos.map((p, i) => {
      const de = Math.round(p.ini * fps);
      const prox = pedacos[i + 1] ? Math.round(pedacos[i + 1].ini * fps) : Infinity;
      const dur = Math.max(2, Math.min(Math.round(p.fim * fps), prox) - de);
      return <Sequence key={i} from={de} durationInFrames={dur}><LegendaPalavras texto={p.texto} /></Sequence>;
    })}
  </>
);
