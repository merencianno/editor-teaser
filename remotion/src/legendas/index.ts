// Estilos de legenda disponíveis em `legenda.estilo`. A skill nova-referencia acrescenta estilos aqui (um arquivo por
// referência, ex.: Documentario.tsx) sem mexer no Padrao.
import { Padrao } from "./Padrao";
import type { PropsLegenda } from "./tipos";

export const ESTILOS: Record<string, React.FC<PropsLegenda>> = {
  padrao: Padrao,
};
