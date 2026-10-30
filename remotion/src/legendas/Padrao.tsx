// Legenda padrão (skill legenda-vertical): até 2 palavras, sem animação (entra e sai seca, junto com a fala),
// branca, sombra suave, centrada, topo na altura do pescoço. Medidas na largura de 1080 (o 16:9 usa a mesma régua).
import { AbsoluteFill, useVideoConfig } from "remotion";
import type { PropsLegenda } from "./tipos";

export const Padrao: React.FC<PropsLegenda> = ({ texto, estilo, fonte }) => {
  const { width } = useVideoConfig();
  const escala = Math.min(width, 1080) / 1080;
  return (
    <AbsoluteFill style={{ alignItems: "center" }}>
      <p style={{ position: "absolute", top: `${estilo.topo * 100}%`, margin: 0, fontFamily: fonte, fontWeight: estilo.peso,
        fontSize: estilo.tamanho * escala, lineHeight: 1.05, letterSpacing: "-0.015em", color: estilo.cor,
        textAlign: "center", maxWidth: width * 0.86, whiteSpace: "nowrap",
        textShadow: "0 2px 6px rgb(0 0 0 / 0.55), 0 0 30px rgb(0 0 0 / 0.35)" }}>
        {texto}
      </p>
    </AbsoluteFill>
  );
};
