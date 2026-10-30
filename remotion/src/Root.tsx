// As composições de cada projeto/versão moram em Composicoes.tsx: gerado por scripts/montar-timeline.py, fora do git,
// e regravado pelo botão de salvar do painel "Props" do Studio. Cada versão tem duas composições:
//   Teaser16x9-<projeto>-vN  e  Teaser9x16-<projeto>-vN
// Se Composicoes.tsx não existir, rode scripts/setup.sh (ele copia Composicoes.vazio.tsx).
import { Composicoes } from "./Composicoes";

export const Root = () => <Composicoes />;
