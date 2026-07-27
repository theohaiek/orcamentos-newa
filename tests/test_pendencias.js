/* Pendências do assistente de conferência — o beco sem saída de 27/07/2026.
 *
 * Sintoma relatado: a pessoa preenchia os campos vermelhos, eles continuavam
 * vermelhos, e o aviso insistia em "3 campo(s) ainda vazio(s)" com os campos
 * visivelmente preenchidos. Não havia como gerar o PDF.
 *
 * Eram quatro defeitos somados, e nenhum deles sozinho explica o travamento:
 *   1. editar no assistente gravava o valor mas não confirmava o campo, então a
 *      pendência nunca saía (na tela de Revisão isso já funcionava);
 *   2. `stepHasPending` só olhava campo vazio, então uma pendência de conferência
 *      não pertencia a etapa nenhuma e o assistente não tinha para onde navegar;
 *   3. a mensagem chamava de "vazio" o que estava preenchido e não conferido;
 *   4. o botão "Preencher vazios" contava as duas pendências, anunciava um número
 *      que não conseguia resolver, e o número não baixava ao ser clicado.
 *
 * Rodar:  node tests/test_pendencias.js
 *
 * O app.js é um IIFE que fala com o DOM, então o teste não o carrega inteiro:
 * reimplementa a MESMA lógica das quatro funções e checa o comportamento. Um
 * guarda no fim confere que as funções continuam existindo no arquivo real, para
 * o teste não seguir verde depois de alguém renomeá-las.
 */
const fs = require("fs");
const path = require("path");

const APP = path.join(__dirname, "..", "orcamentos-newa", "assets", "app.js");
const src = fs.readFileSync(APP, "utf8");

let falhas = [];
function ok(cond, msg) {
  console.log(`    [${cond ? "OK " : "FALHA"}] ${msg}`);
  if (!cond) falhas.push(msg);
}

// ---- espelho da lógica sob teste -------------------------------------------
const CHAVES = ["a_vista", "franquia_veiculo", "para_brisas"];

function breakdown(P) {
  const r = { vazios: 0, semConfirmar: 0 };
  P.columns.forEach((col) => CHAVES.forEach((k) => {
    if (!String(col.fields[k] || "").trim()) { r.vazios++; return; }
    if ((col.provenance[k] || {}).confidence === "baixa") r.semConfirmar++;
  }));
  r.total = r.vazios + r.semConfirmar;
  return r;
}

function msg(P) {
  const b = breakdown(P), partes = [];
  if (b.vazios) partes.push(b.vazios + " campo(s) em branco");
  if (b.semConfirmar) partes.push(b.semConfirmar + " campo(s) a conferir");
  return partes.join(". ") + ".";
}

function stepHasPending(P, chaves) {
  return chaves.some((k) => P.columns.some((c) => {
    if (!String(c.fields[k] || "").trim()) return true;
    return ((c.provenance || {})[k] || {}).confidence === "baixa";
  }));
}

/** Blur no campo do assistente, como em wireWizStep. */
function editar(P, ci, k, v) {
  const col = P.columns[ci];
  const mudou = String(col.fields[k] || "") !== v;
  col.fields[k] = v;
  if (v && (mudou || (col.provenance[k] || {}).confidence === "baixa")) {
    const p = col.provenance[k] || {};
    col.provenance[k] = { value: v, method: "manual", page: p.page || null,
                          bbox: p.bbox || null, snippet: v, anchor: null,
                          confidence: "manual" };
  }
}

function fillEmpties(P) {
  P.columns.forEach((col) => CHAVES.forEach((k) => {
    if (!String(col.fields[k] || "").trim()) col.fields[k] = "Não Contratado";
  }));
}

function cenario() {
  return { columns: [{
    fields: { a_vista: "R$ 8.690,70", franquia_veiculo: "R$ 5.000,00", para_brisas: "" },
    provenance: { a_vista: { confidence: "baixa", method: "ai", page: 2 },
                  franquia_veiculo: { confidence: "alta", method: "profile" } },
  }] };
}

console.log(">> o estado em que o app travava");
let P = cenario();
ok(breakdown(P).total === 2, "duas pendências no total");
ok(breakdown(P).vazios === 1, "uma é campo em branco (para_brisas)");
ok(breakdown(P).semConfirmar === 1, "a outra é campo preenchido a conferir (a_vista)");

console.log(">> 1. editar no assistente confirma o campo");
editar(P, 0, "a_vista", "R$ 8.690,70");          // mesmo valor, só conferindo
ok(P.columns[0].provenance.a_vista.confidence === "manual", "confirmar sem mudar o valor funciona");
ok(breakdown(P).semConfirmar === 0, "a pendência de conferência saiu");
editar(P, 0, "para_brisas", "R$ 200,00");
ok(breakdown(P).total === 0, "preenchido o vazio, não sobra pendência");

console.log(">> apagar o campo devolve a pendência");
editar(P, 0, "para_brisas", "");
ok(breakdown(P).vazios === 1, "campo esvaziado volta a pendurar");
ok(P.columns[0].provenance.para_brisas.confidence === "manual", "valor vazio não vira confirmação nova");

console.log(">> 2. a etapa com pendência de conferência é encontrável");
P = cenario();
ok(stepHasPending(P, ["a_vista"]) === true, "etapa com campo a conferir é apontada");
ok(stepHasPending(P, ["para_brisas"]) === true, "etapa com campo vazio é apontada");
ok(stepHasPending(P, ["franquia_veiculo"]) === false, "etapa resolvida não é apontada");

console.log(">> 3. a mensagem separa em branco de a conferir");
ok(/em branco/.test(msg(P)) && /a conferir/.test(msg(P)), "cita os dois casos");
ok(!/ainda vazio/.test(msg(P)), "não chama de vazio o que está preenchido");
const so = { columns: [{ fields: { a_vista: "R$ 1,00", franquia_veiculo: "x", para_brisas: "y" },
                         provenance: { a_vista: { confidence: "baixa" } } }] };
ok(!/em branco/.test(msg(so)) && /1 campo\(s\) a conferir/.test(msg(so)), "sem vazios, fala só de conferência");

console.log(">> 4. Preencher vazios anuncia só o que resolve");
P = cenario();
const antes = breakdown(P);
fillEmpties(P);
const depois = breakdown(P);
ok(antes.vazios === 1 && depois.vazios === 0, "resolve os vazios");
ok(depois.semConfirmar === 1, "não confirma sozinho o que precisa de conferência humana");
ok(antes.vazios !== antes.total, "por isso o botão nunca deve mostrar o total");

console.log(">> guarda: as funções ainda existem no app.js");
[["pendingBreakdown", /function pendingBreakdown\(/],
 ["pendingMsg", /function pendingMsg\(/],
 ["pending", /function pending\(\)/],
 ["stepHasPending confere 'baixa'", /function stepHasPending[\s\S]{0,700}?confidence === "baixa"/],
 ["wireWizStep confirma ao editar", /dataset\.wk != null[\s\S]{0,1400}?confidence: "manual"/],
 ["botão usa só os vazios", /pendingBreakdown\(\)\.vazios/],
].forEach(([nome, re]) => ok(re.test(src), nome));

/* Exportação: guardas do que já custou caro descobrir. Não dá para medir a
 * qualidade do PDF sem gerar um, mas dá para impedir a volta das três escolhas
 * que produziram um PDF ruim ou inexistente. */
console.log(">> guarda: exportação do PDF");
ok(/compress: true/.test(src), "PDF comprimido — sem isso o jsPDF embute imagem crua");
ok(/toDataURL\("image\/jpeg", q\)/.test(src), "JPEG: o jsPDF embute sem reprocessar; PNG viraria RGB cru");
ok(/blob\.size <= TETO/.test(src), "a qualidade cai até o arquivo caber");
ok(/blob\.size > TETO\)[\s\S]{0,120}?throw/.test(src), "não envia ao servidor algo que será recusado");
ok(/Math\.min\(3,\s*LIM \/ Math\.max/.test(src), "escala adaptativa: 3x de teto, caindo para caber no canvas");
ok(/if \(!canvas\.width \|\| !canvas\.height\) throw/.test(src), "captura vazia vira erro, não PDF em branco");
ok(/fetch\("\/api\/save-pdf"/.test(src), "grava pelo servidor, não pelo download do navegador");
ok(!/pdf\.save\(/.test(src), "nenhuma chamada a pdf.save() — era ela que falhava calada");
ok(/if \(!r\.ok \|\| !res\.ok\) throw/.test(src), "só anuncia sucesso com confirmação do servidor");

console.log(`\n  RESULTADO: ${falhas.length ? "FALHOU -> " + falhas.join("; ") : "OK"}`);
process.exit(falhas.length ? 1 : 0);
