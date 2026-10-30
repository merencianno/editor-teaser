import type { Timeline } from "../schema";

// o que todo estilo de legenda recebe: o pedaço da vez, o bloco `legenda` das props e a fonte já carregada
export type PropsLegenda = { texto: string; estilo: Timeline["legenda"]; fonte: string };
