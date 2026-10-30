#!/usr/bin/env node
// Lê e grava as timelines (defaultProps) em remotion/src/Composicoes.tsx — o arquivo que o painel "Props" do Studio
// regrava ao salvar. Lê qualquer formato que o Studio escreva (chave sem aspas, vírgula sobrando), porque avalia o
// objeto em vez de usar JSON.parse.
//
//   node scripts/props.mjs list
//   node scripts/props.mjs get <id>                 → JSON no stdout
//   node scripts/props.mjs add <id> <props.json>    → composição nova (recusa se o id já existe)
//   node scripts/props.mjs set <id> <props.json>    → troca a timeline de uma composição existente
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const RAIZ = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const ARQ = path.join(RAIZ, "remotion/src/Composicoes.tsx");
const VAZIO = path.join(RAIZ, "remotion/src/Composicoes.vazio.tsx");

const ler = () => {
  if (!fs.existsSync(ARQ)) fs.copyFileSync(VAZIO, ARQ);
  return fs.readFileSync(ARQ, "utf8");
};

// fim do objeto que começa em `ini` (posição do "{"), pulando strings e comentários
function fecha(txt, ini) {
  let n = 0;
  for (let i = ini; i < txt.length; i++) {
    const c = txt[i];
    if (c === '"' || c === "'" || c === "`") {
      for (i++; i < txt.length && txt[i] !== c; i++) if (txt[i] === "\\") i++;
    } else if (c === "/" && txt[i + 1] === "/") {
      while (i < txt.length && txt[i] !== "\n") i++;
    } else if (c === "/" && txt[i + 1] === "*") {
      i = txt.indexOf("*/", i + 2) + 1;
    } else if (c === "{") n++;
    else if (c === "}" && --n === 0) return i;
  }
  throw new Error("objeto sem fechamento");
}

function localizar(txt, id) {
  const m = new RegExp(`id=["']${id.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}["']`).exec(txt);
  if (!m) return null;
  const dp = txt.indexOf("defaultProps={", m.index);
  if (dp < 0) throw new Error(`composição ${id} sem defaultProps`);
  const ini = dp + "defaultProps={".length;
  const fim = fecha(txt, ini);
  return { ini, fim };
}

const ids = (txt) => [...txt.matchAll(/<Composition\s+id=["']([^"']+)["']/g)].map((m) => m[1]);

function bloco(id, props) {
  const [w, h] = props.formato === "9x16" ? [1080, 1920] : [1920, 1080];
  return `    {/* <<${id}>> */}
    <Composition id="${id}" component={Teaser} schema={timeline} fps={${props.fps}} width={${w}} height={${h}} durationInFrames={${props.fps * 60}}
      calculateMetadata={({ props }) => ({ durationInFrames: duracaoEmQuadros(props) })}
      defaultProps={${JSON.stringify(props, null, 2)}} />
    {/* <</${id}>> */}
`;
}

const [cmd, id, arq] = process.argv.slice(2);
const txt = ler();
if (cmd === "list") {
  console.log(ids(txt).join("\n"));
} else if (cmd === "get") {
  const p = localizar(txt, id);
  if (!p) { console.error(`composição ${id} não existe`); process.exit(1); }
  const obj = new Function(`return (${txt.slice(p.ini, p.fim + 1)});`)();
  process.stdout.write(JSON.stringify(obj, null, 1) + "\n");
} else if (cmd === "add" || cmd === "set") {
  const props = JSON.parse(fs.readFileSync(arq, "utf8"));
  const p = localizar(txt, id);
  let novo;
  if (cmd === "add") {
    if (p) { console.error(`composição ${id} já existe: versão nova nunca sobrescreve`); process.exit(1); }
    const marca = "    {/* <<COMPOSICOES>> */}\n";
    if (!txt.includes(marca)) { console.error("marcador <<COMPOSICOES>> sumiu de Composicoes.tsx"); process.exit(1); }
    novo = txt.replace(marca, marca + bloco(id, props));
  } else {
    if (!p) { console.error(`composição ${id} não existe`); process.exit(1); }
    novo = txt.slice(0, p.ini) + JSON.stringify(props, null, 2) + txt.slice(p.fim + 1);
  }
  fs.writeFileSync(ARQ, novo);
  console.log(`${cmd === "add" ? "criada" : "atualizada"}: ${id}`);
} else {
  console.error("uso: props.mjs list | get <id> | add <id> <props.json> | set <id> <props.json>");
  process.exit(2);
}
