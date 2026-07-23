/* =========================================================================
   ORÇAMENTOS NEWA — SPA (vanilla JS)
   API base configurável via window.ORCA_API (dev: "/api" | plugin: REST url)
   ========================================================================= */
(function () {
  "use strict";

  const API = (window.ORCA_API || "/api").replace(/\/$/, "");
  const ASSETS = (window.ORCA_ASSETS || "/assets").replace(/\/$/, "");
  const NONCE = window.ORCA_NONCE || "";
  const LOGO = ASSETS + "/logo-newa.png";

  /* ---------------- Ícones (feather-style) ---------------- */
  const I = {
    doc: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2Z"/></svg>',
    upload: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 15V3m0 0 4 4m-4-4L8 7"/><path d="M4 15v4a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-4"/></svg>',
    layers: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="m12 3 9 5-9 5-9-5 9-5Z"/><path d="m3 13 9 5 9-5"/></svg>',
    users: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M16 20v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 20v-2a4 4 0 0 0-3-3.87M16 3.13A4 4 0 0 1 16 11"/></svg>',
    cog: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.6 1.6 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.6 1.6 0 0 0-2.7 1.1V21a2 2 0 1 1-4 0v-.1A1.6 1.6 0 0 0 7 19.4a1.6 1.6 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.6 1.6 0 0 0-1.1-2.7H1a2 2 0 1 1 0-4h.1A1.6 1.6 0 0 0 2.6 7a1.6 1.6 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.6 1.6 0 0 0 1.8.3H7a1.6 1.6 0 0 0 1-1.5V1a2 2 0 1 1 4 0v.1a1.6 1.6 0 0 0 2.7 1.1 1.6 1.6 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.6 1.6 0 0 0-.3 1.8V7a1.6 1.6 0 0 0 1.5 1H23a2 2 0 1 1 0 4h-.1a1.6 1.6 0 0 0-1.5 1Z"/></svg>',
    logout: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><path d="m16 17 5-5-5-5M21 12H9"/></svg>',
    check: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="m20 6-11 11-5-5"/></svg>',
    alert: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9"><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z"/><path d="M12 9v4m0 4h.01"/></svg>',
    x: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18M6 6l12 12"/></svg>',
    trash: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 6h18M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2m3 0v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/></svg>',
    plus: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14M5 12h14"/></svg>',
    edit: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4 12.5-12.5Z"/></svg>',
    dl: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9"><path d="M12 3v12m0 0 4-4m-4 4-4-4"/><path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2"/></svg>',
    back: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9"><path d="M19 12H5m0 0 7 7m-7-7 7-7"/></svg>',
    fwd: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9"><path d="M5 12h14m0 0-7-7m7 7-7 7"/></svg>',
    wand: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="m15 4 1.5 3L20 8.5 16.5 10 15 13l-1.5-3L10 8.5 13.5 7 15 4Z"/><path d="M4 20 14 10"/><path d="M6.5 6.5 5 5m0 3.5L3.5 7"/></svg>',
    zoom: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3M11 8v6M8 11h6"/></svg>',
    phone: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2 4.2 2 2 0 0 1 4 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.2a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2Z"/></svg>',
    mail: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m2 6 10 7 10-7"/></svg>',
    pin: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M21 10c0 6-9 12-9 12s-9-6-9-12a9 9 0 0 1 18 0Z"/><circle cx="12" cy="10" r="3"/></svg>',
    web: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15 15 0 0 1 0 20 15 15 0 0 1 0-20Z"/></svg>',
    grip: '<svg viewBox="0 0 24 24" fill="currentColor"><circle cx="9" cy="6" r="1.6"/><circle cx="15" cy="6" r="1.6"/><circle cx="9" cy="12" r="1.6"/><circle cx="15" cy="12" r="1.6"/><circle cx="9" cy="18" r="1.6"/><circle cx="15" cy="18" r="1.6"/></svg>',
    eye: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>',
    eyeoff: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M10.7 5.1A9.7 9.7 0 0 1 12 5c6.5 0 10 7 10 7a13.6 13.6 0 0 1-2.2 3M6.6 6.6A13.6 13.6 0 0 0 2 12s3.5 7 10 7a9.7 9.7 0 0 0 4.3-1M3 3l18 18M9.9 9.9a3 3 0 0 0 4.2 4.2"/></svg>',
    tune: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 6h11M4 12h7M4 18h14"/><circle cx="18" cy="6" r="2"/><circle cx="14" cy="12" r="2"/><circle cx="20" cy="18" r="2"/></svg>',
  };
  const MARK = '<svg viewBox="0 0 32 32" fill="none"><path d="M4 8 L13 24 L16 18" stroke="#1F9E4A" stroke-width="4.2" stroke-linecap="round" stroke-linejoin="round"/><path d="M16 18 L22 8 L28 20" stroke="#12703A" stroke-width="4.2" stroke-linecap="round" stroke-linejoin="round"/></svg>';

  /* ---------------- Definição de campos ---------------- */
  const INFO = [
    ["segurado", "Segurado", true],
    ["veiculo", "Veículo", true],
    ["ano_modelo", "Ano/Modelo", true],
    ["principal_condutor", "Principal Condutor", true],
    ["data_proposta", "Data da Proposta", true],
    ["validade", "Validade", false],
    ["uso_veiculo", "Uso do Veículo", false],
    ["valor_fipe", "Valor Fipe", false],
    ["condutores_18_26", "Condutores entre 18 a 26 anos?", false],
    ["cep_circulacao", "CEP Circulação", false],
  ];
  const COBERTURAS = [
    ["colisao_incendio_roubo", "Colisão / Incêndio / Roubo"],
    ["rcf_danos_materiais", "RCF Danos Materiais a Terceiros"],
    ["rcf_danos_pessoais", "RCF Danos Pessoais a Terceiros"],
    ["acidente_pessoal_passageiro", "Acidente Pessoal por Passageiro"],
    ["morte_pessoal_passageiro", "Morte Pessoal por Passageiro"],
    ["km_reboque", "Quilometragem do Reboque"],
    ["diarias_carro_reserva", "Diárias carro Reserva"],
  ];
  const FRANQUIAS = [
    ["franquia_veiculo", "Franquia do Veículo"],
    ["para_brisas", "Para-Brisas"],
    ["farois", "Faróis"],
    ["lanternas", "Lanternas"],
    ["retrovisores", "Retrovisores"],
    ["reparo_para_choque", "Reparo Para-Choque"],
    ["reparo_amassados", "Reparo em Amassados"],
    ["protecao_pneu_roda_suspensao", "Proteção de Pneu / Roda / Suspensão"],
    ["assistencia_residencial", "Seguro com Assistência Residencial"],
  ];
  const PAGAMENTO = [
    ["a_vista", "À VISTA"],
    ["parc_4x", "4X VEZES FIXAS"],
    ["parc_6x", "6X VEZES FIXAS"],
    ["parc_10x", "10X VEZES FIXAS"],
  ];
  const COL_KEYS = [...COBERTURAS, ...FRANQUIAS, ...PAGAMENTO].map((r) => r[0]);
  const OBS_DEFAULT = [
    "PAGAMENTO NO VALOR DE À VISTA OU EM ATÉ 10X SEM JUROS NO CARTÃO DE CRÉDITO",
    "SE OS FARÓIS, LANTERNAS E RETROVISORES FOREM DE LED OU XENÔN, A FRANQUIA VAI SER DIFERENTE",
    "NO CASO DE ARRANHÕES E PEQUENOS DANOS, HAVERÁ A ANÁLISE PARA LIBERAÇÃO DOS REPAROS",
    "A COBERTURA DE PROTEÇÃO DE PNEUS SERÁ LIBERADO PARA UM ITEM DURANTE A VIGÊNCIA",
    "O CARRO RESERVA SERA LIBERADO PARA O SEGURADO OU PRINCIPAL CONDUTOR DA APÓLICE APRESENTANDO CNH COM MAIS DE 2 ANOS E CARTÃO DE CRÉDITO",
  ];

  /* ---------------- Modelo do documento (data-driven) ---------------- */
  function DEFAULT_TPL() {
    return {
      title: "PROPOSTA DE SEGURO",
      subtitle: "NEWA · Corretora de Seguros",
      cover: {
        show: true,
        greeting: "Olá, {{primeiro_nome}}",
        paragraphs: [
          "Antes de qualquer coisa, parabéns por esse passo dado junto à NEWA Seguros.",
          "Aqui, o cuidado com o que é seu começa agora, onde preparamos tudo com atenção aos detalhes.",
          "A seguir, você encontrará uma proposta personalizada, com tudo o que você precisa saber para escolher com confiança a melhor proteção.",
        ],
        showMural: true,
        muralLabel: "Trabalhamos com as principais seguradoras do país",
        showContact: true,
      },
      infoTitle: "Informações do Veículo e Condutor",
      info: INFO.map(([key, label, req]) => ({ key, label, show: true, req: !!req })),
      sections: [
        { id: "cob", title: "Coberturas", show: true, rows: COBERTURAS.map(([key, label]) => ({ key, label, show: true })) },
        { id: "fra", title: "Franquias e Assistências", show: true, rows: FRANQUIAS.map(([key, label]) => ({ key, label, show: true })) },
        { id: "pag", title: "Formas de Pagamento", show: true, rows: PAGAMENTO.map(([key, label]) => ({ key, label, show: true })) },
      ],
      obs: { show: true, title: "Observações", items: OBS_DEFAULT.slice() },
    };
  }
  const clone = (o) => JSON.parse(JSON.stringify(o));
  const tpl = () => (S.template && S.template.sections ? S.template : DEFAULT_TPL());
  const visInfo = () => tpl().info.filter((r) => r.show);
  const dataKeys = (inclOptional) => tpl().sections.filter((s) => s.show)
    .flatMap((s) => s.rows.filter((r) => r.show && (inclOptional || !r.optional)).map((r) => r.key));

  /* ---------------- Utils ---------------- */
  const $ = (s, r = document) => r.querySelector(s);
  const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const root = () => document.getElementById("orca-root");

  async function api(path, opts = {}) {
    const o = Object.assign({ credentials: "same-origin", headers: {} }, opts);
    if (NONCE) o.headers["X-WP-Nonce"] = NONCE;
    if (o.body && !(o.body instanceof FormData)) {
      o.headers["Content-Type"] = "application/json";
      o.body = JSON.stringify(o.body);
    }
    const res = await fetch(API + path, o);
    let data = null;
    try { data = await res.json(); } catch (e) {}
    if (!res.ok) throw Object.assign(new Error((data && data.error) || res.statusText), { status: res.status, data });
    return data;
  }

  function toast(msg, kind = "") {
    let host = $(".toasts");
    if (!host) { host = document.createElement("div"); host.className = "toasts"; document.body.appendChild(host); }
    const t = document.createElement("div");
    t.className = "toast " + kind;
    t.innerHTML = (kind === "ok" ? I.check : kind === "err" ? I.alert : "") + "<span>" + esc(msg) + "</span>";
    host.appendChild(t);
    setTimeout(() => { t.style.transition = "opacity .3s, transform .3s"; t.style.opacity = "0"; t.style.transform = "translateY(8px)"; setTimeout(() => t.remove(), 300); }, 3200);
  }

  function modal({ title, bodyHTML, okText = "Salvar", danger = false, onOk }) {
    const ov = document.createElement("div");
    ov.className = "overlay";
    ov.innerHTML =
      '<div class="modal card"><div class="grad-bar"></div><div class="head"><h3>' + esc(title) + "</h3></div>" +
      '<div class="body">' + bodyHTML + "</div>" +
      '<div class="foot"><button class="btn ghost" data-cancel>Cancelar</button>' +
      '<button class="btn ' + (danger ? "danger" : "") + '" data-ok>' + esc(okText) + "</button></div></div>";
    document.body.appendChild(ov);
    const close = () => { ov.style.opacity = "0"; setTimeout(() => ov.remove(), 180); };
    ov.querySelector("[data-cancel]").onclick = close;
    ov.addEventListener("mousedown", (e) => { if (e.target === ov) close(); });
    ov.querySelector("[data-ok]").onclick = async () => {
      const btn = ov.querySelector("[data-ok]"); btn.disabled = true;
      try { const ok = await onOk(ov); if (ok !== false) close(); btn.disabled = false; }
      catch (e) { btn.disabled = false; toast(e.message || "Erro", "err"); }
    };
    return { ov, close };
  }

  /* ---------------- Estado ---------------- */
  const S = { me: null, insurers: [], config: null, view: "nova", proposal: null, provView: "visual" };

  const insurerById = (id) => S.insurers.find((x) => x.id === id) || S.insurers.find((x) => x.id === "generico") || S.insurers[0];
  function detectInsurer(text, filename) {
    const hay = ((text || "") + " " + (filename || "")).toLowerCase();
    for (const ins of S.insurers) {
      for (const d of (ins.detect || [])) if (d && hay.includes(d.toLowerCase())) return ins.id;
    }
    // fallback pelo nome do arquivo
    const fn = (filename || "").toLowerCase();
    for (const ins of S.insurers) if (fn.includes(ins.id)) return ins.id;
    return "generico";
  }

  /* =========================================================================
     BOOT
     ========================================================================= */
  async function boot() {
    try {
      const me = await api("/me");
      S.me = me.user;
      await loadShared();
      renderApp();
    } catch (e) {
      renderLogin();
    }
  }
  async function loadShared() {
    const [ins, cfg] = await Promise.all([api("/insurers"), api("/config")]);
    S.insurers = ins.insurers || ins;
    S.config = cfg;
    try { const tp = await api("/template"); S.template = tp && tp.sections ? tp : null; }
    catch (e) { S.template = null; }
  }

  /* =========================================================================
     LOGIN
     ========================================================================= */
  function renderLogin(msg) {
    document.body.innerHTML = "";
    const wrap = document.createElement("div");
    wrap.className = "login-wrap";
    wrap.innerHTML =
      '<div class="login-card card stagger">' +
      '<div class="grad-bar"></div>' +
      '<div class="top"><img class="logo-img" src="' + LOGO + '" alt="NEWA">' +
      "<h2>Orçamentos NEWA</h2><p>Entre para gerar propostas de seguro</p></div>" +
      '<form autocomplete="on">' +
      (msg ? '<div class="alert err">' + I.alert + "<span>" + esc(msg) + "</span></div>" : "") +
      '<div class="field"><label>Usuário</label><input class="input" name="username" autocomplete="username" required></div>' +
      '<div class="field"><label>Senha</label><input class="input" type="password" name="password" autocomplete="current-password" required></div>' +
      '<button class="btn lg block" type="submit">Entrar</button>' +
      "</form></div>";
    document.body.appendChild(wrap);
    const form = wrap.querySelector("form");
    form.onsubmit = async (e) => {
      e.preventDefault();
      const btn = form.querySelector("button"); btn.disabled = true; btn.innerHTML = '<span class="spin"></span> Entrando…';
      try {
        const fd = new FormData(form);
        const r = await api("/login", { method: "POST", body: { username: fd.get("username"), password: fd.get("password") } });
        S.me = r.user; await loadShared(); renderApp();
      } catch (err) {
        btn.disabled = false; btn.textContent = "Entrar";
        renderLogin(err.status === 401 ? "Usuário ou senha incorretos." : (err.message || "Falha ao entrar."));
      }
    };
    form.querySelector("[name=username]").focus();
  }

  /* =========================================================================
     APP SHELL
     ========================================================================= */
  const NAV = [
    ["nova", "Nova Proposta", I.doc],
    ["modelo", "Editar modelo", I.tune, true],
    ["modelos", "Modelos de Entrada", I.layers],
    ["usuarios", "Usuários", I.users, true],
    ["config", "Configurações", I.cog, true],
  ];
  function renderApp() {
    const admin = S.me.role === "admin";
    document.body.innerHTML = "";
    const app = document.createElement("div");
    app.className = "app";
    app.innerHTML =
      '<aside class="sidebar">' +
      '<div class="brand"><div class="mark"><img src="' + LOGO + '" alt="NEWA"></div><div class="txt"><div class="name">NEWA</div><div class="sub">Orçamentos</div></div></div>' +
      '<nav class="nav">' +
      NAV.filter((n) => !n[3] || admin).map((n) =>
        '<a data-view="' + n[0] + '">' + n[2] + "<span>" + n[1] + "</span></a>").join("") +
      '</nav>' +
      '<div class="foot"><div class="who"><b>' + esc(S.me.name || S.me.username) + "</b><span>" + (admin ? "Administrador" : "Usuário") + '</span></div>' +
      '<button class="btn icon ghost" title="Sair" data-logout style="color:#CFE4D8">' + I.logout + "</button></div>" +
      "</aside>" +
      '<main class="main"><div id="orca-root"></div></main>';
    document.body.appendChild(app);
    app.querySelectorAll(".nav a").forEach((a) => (a.onclick = () => go(a.dataset.view)));
    app.querySelector("[data-logout]").onclick = async () => { try { await api("/logout", { method: "POST" }); } catch (e) {} location.reload(); };
    go(S.view);
  }
  function go(view) {
    S.view = view;
    document.querySelectorAll(".nav a").forEach((a) => a.classList.toggle("active", a.dataset.view === view));
    ({ nova: viewNova, modelo: viewEditarModelo, modelos: viewModelos, usuarios: viewUsuarios, config: viewConfig }[view] || viewNova)();
  }
  function shell(crumb, title, actionsHTML = "") {
    return (
      '<div class="topbar"><div><div class="crumb">' + esc(crumb) + "</div><h1>" + esc(title) + "</h1></div>" +
      '<div style="display:flex;gap:10px">' + actionsHTML + "</div></div>" +
      '<div class="content" id="view-content"></div>'
    );
  }

  /* =========================================================================
     VIEW: NOVA PROPOSTA
     ========================================================================= */
  function viewNova() {
    if (S.proposal) return renderReview();
    if (!S.nova) S.nova = { count: 2, files: [null, null, null, null, null] };
    const N = S.nova;
    root().innerHTML = shell("Nova Proposta", "Enviar cotações");
    const c = $("#view-content");
    c.innerHTML =
      '<div class="stagger" style="max-width:900px">' +
      '<div class="nova-top">' +
      '<div><h3 style="font-size:17px">Quantas propostas comparar?</h3>' +
      '<p class="muted" style="font-size:13px;margin-top:2px">Um PDF por proposta — cada uma vira uma coluna do comparativo. <b>2 é o modo recomendado.</b></p></div>' +
      '<div class="seg" id="seg">' +
      [1, 2, 3, 4, 5].map((n) => '<button data-n="' + n + '"' + (n === N.count ? ' class="active"' : "") + (n !== 2 ? ' data-beta="1"' : "") + ">" + n + "</button>").join("") +
      "</div></div>" +
      '<div id="betawarn"></div>' +
      '<div class="slots" id="slots"></div>' +
      '<div id="startwrap" style="margin-top:22px" class="hidden">' +
      '<button class="btn lg" id="startbtn">' + I.check + " Extrair e comparar</button>" +
      '<span class="muted" id="starthint" style="margin-left:14px;font-size:13px"></span></div>' +
      "</div>";
    const slotsEl = $("#slots");
    const setFile = (i, f) => {
      if (!(f.type === "application/pdf" || f.name.toLowerCase().endsWith(".pdf"))) { toast("Envie um arquivo PDF.", "err"); return; }
      N.files[i] = f; renderSlots(); updateStart();
    };
    const updateStart = () => {
      const chosen = N.files.slice(0, N.count).filter(Boolean).length;
      const ready = chosen === N.count;
      $("#startwrap").classList.toggle("hidden", chosen === 0);
      $("#startbtn").disabled = !ready;
      $("#starthint").textContent = ready ? "" : (N.count - chosen) + " proposta(s) sem PDF";
    };
    const renderSlots = () => {
      let html = "";
      for (let i = 0; i < N.count; i++) {
        const f = N.files[i];
        if (f) {
          html +=
            '<div class="slot filled" data-i="' + i + '"><div class="scap">Proposta ' + (i + 1) + "</div>" +
            '<div class="sfile"><div class="fic">' + I.doc + '</div><div class="meta"><b>' + esc(f.name) +
            "</b><span>" + (f.size / 1024).toFixed(0) + ' KB</span></div><button class="btn icon ghost" data-rm="' + i + '">' + I.x + "</button></div></div>";
        } else {
          html +=
            '<div class="slot" data-i="' + i + '"><div class="scap">Proposta ' + (i + 1) + "</div>" +
            '<div class="sic">' + I.upload + '</div><div class="slabel">Enviar proposta ' + (i + 1) + "</div>" +
            '<div class="shint">clique ou arraste um PDF</div>' +
            '<input type="file" accept="application/pdf" data-fi="' + i + '" hidden></div>';
        }
      }
      slotsEl.innerHTML = html;
      slotsEl.querySelectorAll(".slot:not(.filled)").forEach((sl) => {
        const i = +sl.dataset.i, inp = sl.querySelector("input");
        sl.onclick = () => inp.click();
        inp.onchange = () => { if (inp.files[0]) setFile(i, inp.files[0]); };
        ["dragenter", "dragover"].forEach((e) => sl.addEventListener(e, (ev) => { ev.preventDefault(); sl.classList.add("drag"); }));
        ["dragleave", "drop"].forEach((e) => sl.addEventListener(e, (ev) => { ev.preventDefault(); sl.classList.remove("drag"); }));
        sl.addEventListener("drop", (ev) => { const f = ev.dataTransfer.files[0]; if (f) setFile(i, f); });
      });
      slotsEl.querySelectorAll("[data-rm]").forEach((b) => (b.onclick = (e) => { e.stopPropagation(); N.files[+b.dataset.rm] = null; renderSlots(); updateStart(); }));
    };
    const updateBeta = () => {
      const bw = $("#betawarn");
      bw.innerHTML = N.count === 2 ? "" :
        '<div class="alert warn" style="margin:14px 0 0">' + I.alert +
        "<span><b>Em desenvolvimento — pode apresentar bugs.</b> Comparar <b>" + N.count +
        "</b> proposta(s) ainda não é totalmente estável. O modo recomendado e testado é <b>2 propostas</b>.</span></div>";
    };
    $("#seg").querySelectorAll("button").forEach((b) => (b.onclick = () => {
      N.count = +b.dataset.n;
      $("#seg").querySelectorAll("button").forEach((x) => x.classList.toggle("active", x === b));
      renderSlots(); updateStart(); updateBeta();
    }));
    renderSlots(); updateStart(); updateBeta();
    $("#startbtn").onclick = () => extract(N.files.slice(0, N.count).filter(Boolean));
  }

  async function extract(files) {
    const c = $("#view-content");
    c.innerHTML =
      '<div class="card pad stagger" style="max-width:760px"><h3>Processando cotações…</h3>' +
      '<p class="muted" style="margin-top:4px">Extraindo texto e mapeando os campos com IA. Isso pode levar alguns segundos por arquivo.</p>' +
      '<div class="filelist" id="prog"></div></div>';
    const prog = $("#prog");
    prog.innerHTML = files.map((f, i) =>
      '<div class="filerow" id="p' + i + '"><div class="fic">' + I.doc + '</div><div class="meta"><b>' + esc(f.name) +
      '</b><span>na fila…</span></div><div class="st work" id="s' + i + '"><span class="spin"></span> extraindo</div></div>').join("");
    const columns = [];
    const errors = [];
    for (let i = 0; i < files.length; i++) {
      const row = $("#s" + i), meta = $("#p" + i + " .meta span");
      try {
        const fd = new FormData(); fd.append("file", files[i]);
        const r = await api("/extract", { method: "POST", body: fd });
        const insurer_id = r.insurer_id || detectInsurer(r.raw_text, files[i].name);
        columns.push({
          filename: files[i].name, insurer_id, fields: r.fields, missing: r.missing || [],
          provenance: r.provenance || {}, unmapped: r.unmapped || [], pages: r.pages || [], doc_id: r.doc_id || null,
          profile_used: !!r.profile_used, profile_id: r.profile_id || null, ai_used: !!r.ai_used, drift: !!r.drift,
        });
        row.className = "st done"; row.innerHTML = I.check + " ok";
        const src = r.profile_used ? "perfil " + (r.profile_id || "") : "IA";
        meta.textContent = insurerById(insurer_id).name + " · " + src + " · " + (r.missing || []).length + " a revisar";
      } catch (e) {
        errors.push(files[i].name);
        row.className = "st err"; row.innerHTML = I.alert + " falhou";
        meta.textContent = e.message || "erro na extração";
      }
    }
    if (!columns.length) {
      c.insertAdjacentHTML("beforeend",
        '<div class="alert err" style="margin-top:16px;max-width:760px">' + I.alert +
        "<span>Nenhuma cotação pôde ser lida. Verifique se os PDFs são válidos e tente novamente.</span></div>");
      c.insertAdjacentHTML("beforeend", '<button class="btn secondary" style="margin-top:14px" onclick="location.reload()">Voltar</button>');
      return;
    }
    // monta a proposta: info compartilhada vem da 1ª coluna
    const info = {};
    tpl().info.forEach((r) => (info[r.key] = columns[0].fields[r.key] || ""));
    S.proposal = { info, columns, errors, obs: clone(tpl().obs.items) };
    if (errors.length) toast(errors.length + " arquivo(s) falharam e foram ignorados.", "err");
    renderReview();
    openConfirmWizard();   // assistente de conferência abre automaticamente após extrair
  }

  /* =========================================================================
     REVIEW + DOCUMENTO (edição in-place)
     ========================================================================= */
  function pending() {
    const P = S.proposal; let n = 0;
    tpl().info.forEach((r) => { if (r.show && r.req && !String(P.info[r.key] || "").trim()) n++; });
    const keys = dataKeys(false);
    P.columns.forEach((col) => keys.forEach((k) => { if (!String(col.fields[k] || "").trim()) n++; }));
    return n;
  }

  function renderReview() {
    const P = S.proposal;
    const nUnmapped = P.columns.reduce((a, col) => a + (col.unmapped || []).length, 0);
    root().innerHTML = shell("Nova Proposta", "Revisão da proposta",
      '<div class="provtoggle" id="provtoggle" title="Como mostrar a origem de cada dado">' +
      '<span class="pt-lbl">Origem:</span>' +
      '<button data-pv="visual"' + (S.provView === "visual" ? ' class="on"' : "") + ">Visual</button>" +
      '<button data-pv="texto"' + (S.provView === "texto" ? ' class="on"' : "") + ">Texto</button></div>" +
      '<button class="btn secondary" id="unmapbtn">' + I.layers + " Não mapeado" + (nUnmapped ? " (" + nUnmapped + ")" : "") + "</button>" +
      '<button class="btn secondary" id="backbtn">' + I.back + " Recomeçar</button>" +
      '<button class="btn secondary" id="fillbtn">Preencher vazios</button>' +
      '<button class="btn" id="expbtn">' + I.check + " Conferir e gerar</button>");
    const c = $("#view-content");
    c.innerHTML =
      '<div id="reviewnote"></div>' +
      '<div class="prov-hint muted">Clique no ponto de origem de cada campo para ver <b>de onde veio no PDF</b>. ' +
      '<span class="dotlegend"><span class="prov-dot method-profile"></span>Perfil</span>' +
      '<span class="dotlegend"><span class="prov-dot method-ai"></span>IA verificada</span>' +
      '<span class="dotlegend"><span class="prov-dot method-low"></span>Confirmar</span></div>' +
      '<div class="orca-doc" id="doc">' + buildDoc(P, true) + "</div>";
    $("#provtoggle").querySelectorAll("[data-pv]").forEach((b) => (b.onclick = () => {
      S.provView = b.dataset.pv;
      $("#provtoggle").querySelectorAll("[data-pv]").forEach((x) => x.classList.toggle("on", x === b));
      const open = $(".prov-modal"); if (open) reopenProvenance();
    }));
    $("#unmapbtn").onclick = () => openUnmapped();
    $("#backbtn").onclick = () => { if (confirm("Descartar esta proposta e recomeçar?")) { S.proposal = null; S.nova = null; viewNova(); } };
    $("#fillbtn").onclick = () => { fillEmpties(); };
    $("#expbtn").onclick = () => openConfirmWizard();
    wireDoc();
    updateNote();
  }

  function updateNote() {
    const n = pending();
    const note = $("#reviewnote"); if (!note) return;
    if (n === 0) {
      note.innerHTML = '<div class="alert ok" style="margin-bottom:18px">' + I.check +
        "<span><b>Tudo preenchido.</b> Clique em <b>Conferir e gerar</b> para revisar a origem de cada dado e gerar o PDF.</span></div>";
    } else {
      note.innerHTML = '<div class="alert warn" style="margin-bottom:18px">' + I.alert +
        "<span><b>" + n + " campo(s) pendente(s).</b> Os campos em vermelho estão vazios — preencha aqui ou dentro de <b>Conferir e gerar</b>. O PDF não será gerado enquanto houver pendências.</span></div>";
    }
    const exp = $("#expbtn"); if (exp) exp.disabled = false;  // sempre abre o assistente (resolve pendências lá dentro)
  }

  /* Realça tokens {{...}} para leitura no editor/preview */
  const mark = (txt) => esc(txt).replace(/\{\{([^}]+)\}\}/g, '<span class="ph-token">{{$1}}</span>');

  /* classe do ponto de proveniência a partir do método/confiança */
  function provClass(p) {
    if (!p) return null;
    if (p.method === "profile") return "method-profile";
    if (p.method === "manual") return "method-manual";
    if (p.method === "ai") return p.confidence === "baixa" ? "method-low" : "method-ai";
    return "method-ai";
  }
  const METHOD_LABEL = {
    "method-profile": ["Perfil determinístico", "Extraído por posição/rótulo — origem exata."],
    "method-ai": ["IA verificada", "Interpretado por IA e confirmado no texto do PDF."],
    "method-low": ["IA — confirme", "Valor da IA não localizado literalmente no PDF. Confira."],
    "method-manual": ["Manual", "Atribuído manualmente a partir do painel Não mapeado."],
  };

  /* constrói o HTML do documento (2 páginas).
     editable=true -> cápsulas editáveis (revisão) ; ph=true -> modo placeholder (editor) */
  function buildDoc(P, editable, ph, tOverride) {
    const T = tOverride || tpl();
    const cols = P.columns;
    const ncols = cols.length;
    const cfg = S.config.corretora || {};
    const labelw = ncols >= 3 ? "240px" : "300px";

    const provDot = (key, ci) => {
      const col = P.columns[ci]; if (!col) return "";
      const cls = provClass((col.provenance || {})[key]);
      if (!cls) return "";
      return '<span class="prov-dot ' + cls + '" data-prov="' + esc(key) + '" data-col="' + ci + '" title="Ver origem no PDF"></span>';
    };
    const cap = (val, kk, ci, lbl) => {
      if (ph) return '<div class="cap ph">{{' + esc(lbl) + "}}</div>";
      const empty = !String(val || "").trim();
      const yes = /^sim$/i.test(String(val || "").trim());
      const na = /não contratado|nao contratado/i.test(String(val || ""));
      const cls = "cap" + (empty ? " empty" : yes ? " yes" : na ? " na" : "");
      const attrs = editable ? ' contenteditable="true" data-k="' + kk + '" data-c="' + ci + '" spellcheck="false"' : "";
      const h = '<div class="' + cls + '"' + attrs + ">" + esc(empty ? (editable ? "" : "—") : val) + "</div>";
      return editable ? '<div class="capwrap">' + h + provDot(kk, ci) + "</div>" : h;
    };
    const infoCap = (r) => {
      if (ph) return '<div class="cap ph">{{' + esc(r.label) + "}}</div>";
      const v = P.info[r.key], empty = !String(v || "").trim();
      const attrs = editable ? ' contenteditable="true" data-info="' + r.key + '" spellcheck="false"' : "";
      const h = '<div class="cap' + (empty ? " empty" : "") + '"' + attrs + ">" + esc(empty ? "" : v) + "</div>";
      return editable ? '<div class="capwrap">' + h + provDot(r.key, 0) + "</div>" : h;
    };
    const colHead = (col, i) => {
      if (ph) return '<div class="col-head" style="background:var(--green-700);color:#fff"><span class="badge" style="background:rgba(255,255,255,.28)">' + (i + 1) + '</span><span class="nm">{{Seguradora ' + (i + 1) + "}}</span></div>";
      const ins = insurerById(col.insurer_id);
      const fg = ins.text === "dark" ? "#141414" : "#fff";
      const inner = ins.logo_small
        ? '<span class="logochip"><img src="' + esc(ins.logo_small) + '" alt="' + esc(ins.name) + '"></span>'
        : '<span class="nm">' + esc(ins.name) + "</span>";
      return '<div class="col-head" data-col="' + i + '" style="background:' + ins.color + ";color:" + fg + '">' +
        '<span class="badge" style="background:rgba(' + (ins.text === "dark" ? "0,0,0,.12" : "255,255,255,.28") + ')">' + (i + 1) + "</span>" +
        inner + "</div>";
    };
    const secBar = (title) =>
      '<div class="sec-bar with-cols" style="--ncols:' + ncols + ";--labelw:" + labelw + '">' +
      '<div class="sec-title">' + esc(title) + "</div>" +
      cols.map((col, i) => colHead(col, i)).join("") + "</div>";
    const dataRows = (rows) =>
      '<div class="rows" style="--ncols:' + ncols + ";--labelw:" + labelw + '">' +
      rows.map((r) =>
        '<div class="datarow"><div class="lbl">' + esc(r.label) + "</div>" +
        cols.map((col, i) => cap(col.fields[r.key], r.key, i, r.label)).join("") + "</div>").join("") +
      "</div>";

    /* ---- CAPA (usa override por-proposta, se editado no assistente) ---- */
    const cv = (P && P.coverOverride) ? Object.assign({}, T.cover, P.coverOverride) : T.cover;
    const nome = ph ? "{{primeiro nome}}" : (P.info.segurado || "Cliente").split(" ")[0];
    const nameHTML = ph ? '<span class="ph-token">{{primeiro nome}}</span>' : "<b>" + esc(nome) + "</b>";
    let greeting = esc(cv.greeting || "Olá, {{primeiro_nome}}").replace("{{primeiro_nome}}", nameHTML);
    greeting = greeting.replace(/\{\{([^}]+)\}\}/g, '<span class="ph-token">{{$1}}</span>');
    const strip = S.insurers.filter((x) => x.id !== "generico")
      .map((x) => x.logo
        ? '<div class="ins-logo"><img src="' + esc(x.logo) + '" alt="' + esc(x.name) + '"></div>'
        : '<span class="ins-txt">' + esc(x.name) + "</span>").join("");
    let cover = "";
    if (T.cover.show) {
      cover =
        '<div class="doc-page cover" data-page="1"><div class="topgrad"></div><div class="safe">' +
        '<div class="logo"><img class="logo-img" src="' + LOGO + '" alt="NEWA Seguros"></div>' +
        '<div class="hero-mark">' + MARK + "</div>" +
        '<div class="hello"><h1>' + greeting + "</h1></div>" +
        '<div class="letter">' + cv.paragraphs.map((p) => "<p>" + mark(p) + "</p>").join("") + "</div>" +
        '<div class="spacer"></div>' +
        (cv.showMural ? '<div class="strip-label">' + esc(cv.muralLabel || "") + "</div>" + '<div class="insurers-strip">' + strip + "</div>" : "") +
        (T.cover.showContact
          ? '<div class="contact">' +
            '<div class="blk"><h4>Atendimento</h4>' +
            '<div class="rowc">' + I.web + "<span>" + esc(cfg.site || "newaseguros.com.br") + "</span></div>" +
            '<div class="rowc">' + I.mail + "<span>" + esc(cfg.email || "newaseguros@newaseguros.com.br") + "</span></div>" +
            '<div class="rowc">' + I.pin + "<span>" + esc(cfg.endereco || "—") + "</span></div></div>" +
            '<div class="blk"><h4>Contato</h4>' +
            '<div class="rowc">' + I.phone + "<span>" + esc(cfg.telefone || "(11) 4040-3665") + "</span></div>" +
            (cfg.whatsapp ? '<div class="rowc">' + I.phone + "<span>" + esc(cfg.whatsapp) + "</span></div>" : "") +
            "</div></div>"
          : "") +
        "</div></div>";
    }

    /* ---- COMPARATIVO ---- */
    const inforow = (r) => '<div class="inforow"><div class="lbl">' + esc(r.label) + ":</div>" + infoCap(r) + "</div>";
    const infoRows = T.info.filter((r) => r.show);
    const infoFull = infoRows.slice(0, 4);
    const infoPairs = infoRows.slice(4);
    let pairsHTML = "";
    for (let i = 0; i < infoPairs.length; i += 2)
      pairsHTML += '<div class="infopair">' + inforow(infoPairs[i]) + (infoPairs[i + 1] ? inforow(infoPairs[i + 1]) : "") + "</div>";
    const infoGrid = '<div class="rows infoblock">' + infoFull.map(inforow).join("") + pairsHTML + "</div>";
    const sectionsHTML = T.sections.filter((s) => s.show)
      .map((s) => secBar(s.title) + dataRows(s.rows.filter((r) => r.show))).join("");
    const obsItems = (P && P.obs) ? P.obs : T.obs.items;
    const obs = T.obs.show
      ? '<div class="obs"><div class="obs-t">' + esc(T.obs.title || "Observações") + "</div><ul" + (editable && !ph ? ' contenteditable="true" data-obs="1"' : "") + ">" +
        obsItems.map((o) => "<li>" + mark(o) + "</li>").join("") + "</ul></div>"
      : "";
    // banner: quais seguradoras a proposta compara (logo + nome)
    const cmpIns = cols.map((col, i) => {
      const ins = insurerById(col.insurer_id);
      const logo = ins.logo_small || ins.logo;
      const media = logo
        ? '<span class="cmp-logo"><img src="' + esc(logo) + '" alt="' + esc(ins.name) + '"></span>'
        : '<span class="cmp-dot" style="background:' + ins.color + '">' + esc(ins.abbr || "") + "</span>";
      return '<div class="cmp-ins"><span class="cmp-badge" style="background:' + ins.color + '">' + (i + 1) + "</span>" +
        media + '<span class="cmp-nm">' + esc(ins.name) + "</span></div>";
    }).join('<span class="cmp-x">×</span>');
    const cmpBanner = '<div class="cmp-banner"><div class="cmp-lbl">Comparativo entre seguradoras</div>' +
      '<div class="cmp-insurers">' + cmpIns + "</div></div>";
    const compare =
      '<div class="doc-page compare" data-page="2"><div class="topgrad"></div>' +
      '<div class="head"><img class="logo-img" src="' + LOGO + '" alt="NEWA"><div class="tt"><small>' + esc(T.subtitle || "") + "</small><h1>" + esc(T.title || "") + "</h1></div></div>" +
      cmpBanner +
      '<div class="sec-bar"><div class="sec-title">' + esc(T.infoTitle || "") + "</div></div>" +
      infoGrid +
      sectionsHTML +
      obs +
      '<div class="compare-foot docfoot"><span>NEWA Seguros</span><div class="g"></div><span>' +
      (ph ? "Proposta gerada em {{data}}" : "Proposta gerada em " + new Date().toLocaleDateString("pt-BR")) + "</span></div></div>";

    return cover + compare;
  }

  function wireDoc() {
    const doc = $("#doc");
    // edição das cápsulas
    doc.querySelectorAll("[contenteditable]").forEach((el) => {
      el.addEventListener("blur", () => {
        const v = el.textContent.trim();
        if (el.dataset.info != null) S.proposal.info[el.dataset.info] = v;
        else if (el.dataset.k != null) S.proposal.columns[+el.dataset.c].fields[el.dataset.k] = v;
        else if (el.dataset.obs != null) S.proposal.obs = Array.from(el.querySelectorAll("li")).map((li) => li.textContent.trim()).filter(Boolean);
        refreshCap(el); updateNote();
      });
      el.addEventListener("keydown", (e) => { if (e.key === "Enter" && el.tagName !== "UL") { e.preventDefault(); el.blur(); } });
    });
    // troca de seguradora ao clicar no header da coluna
    doc.querySelectorAll(".col-head").forEach((ch) => (ch.onclick = () => pickInsurer(+ch.dataset.col)));
    // ponto de proveniência -> popup de origem
    doc.querySelectorAll(".prov-dot").forEach((d) => (d.onclick = (e) => { e.stopPropagation(); openProvenance(+d.dataset.col, d.dataset.prov); }));
  }
  function refreshCap(el) {
    if (el.dataset.info != null || el.dataset.k != null) {
      const v = el.textContent.trim();
      el.classList.toggle("empty", !v);
      el.classList.toggle("yes", /^sim$/i.test(v));
      el.classList.toggle("na", /não contratado|nao contratado/i.test(v));
    }
  }
  function fillEmpties() {
    const P = S.proposal; const keys = dataKeys(true);
    P.columns.forEach((col) => keys.forEach((k) => { if (!String(col.fields[k] || "").trim()) col.fields[k] = "Não Contratado"; }));
    renderReview();
    toast("Campos vazios preenchidos com “Não Contratado”.", "ok");
  }
  function pickInsurer(ci) {
    const opts = S.insurers.map((x) =>
      '<option value="' + x.id + '"' + (S.proposal.columns[ci].insurer_id === x.id ? " selected" : "") + ">" + esc(x.name) + "</option>").join("");
    modal({
      title: "Seguradora da coluna " + (ci + 1),
      okText: "Aplicar",
      bodyHTML: '<div class="field"><label>Seguradora (define a cor do cabeçalho)</label><select class="select input" id="pins">' + opts + "</select></div>",
      onOk: (ov) => { S.proposal.columns[ci].insurer_id = ov.querySelector("#pins").value; renderReview(); },
    });
  }

  /* ---------------- Proveniência (de onde veio cada dado) ---------------- */
  function fieldLabel(key) {
    const t = tpl();
    const fi = t.info.find((r) => r.key === key); if (fi) return fi.label;
    for (const s of t.sections) { const r = s.rows.find((x) => x.key === key); if (r) return r.label; }
    return key;
  }
  function syncTopToggle() {
    const tg = $("#provtoggle"); if (!tg) return;
    tg.querySelectorAll("[data-pv]").forEach((x) => x.classList.toggle("on", x.dataset.pv === S.provView));
  }
  function reopenProvenance() { if (S._prov) openProvenance(S._prov.ci, S._prov.key); }

  function openProvenance(ci, key) {
    const col = S.proposal.columns[ci]; if (!col) return;
    const p = (col.provenance || {})[key];
    const value = key in S.proposal.info && ci === 0 ? S.proposal.info[key] : (col.fields || {})[key];
    S._prov = { ci, key };
    const ex = document.querySelector(".prov-overlay"); if (ex) ex.remove();
    const cls = provClass(p) || "method-low";
    const [mlabel, mdesc] = METHOD_LABEL[cls] || ["—", ""];
    let body;
    if (S.provView === "visual") {
      if (p && p.page && p.bbox) {
        const pg = (col.pages || []).find((x) => x.n === p.page);
        body = pg ? provPageHTML(pg, p.bbox) : '<div class="prov-empty">Página indisponível.</div>';
      } else {
        body = '<div class="prov-empty">' + I.alert + " Origem não localizada no PDF — confirme o valor manualmente.</div>";
      }
    } else {
      body = p
        ? '<div class="prov-text">' +
          '<div class="pr"><span>Página</span><b>' + (p.page || "—") + "</b></div>" +
          (p.anchor ? '<div class="pr"><span>Rótulo-âncora</span><b>' + esc(p.anchor) + "</b></div>" : "") +
          '<div class="pr col"><span>Trecho no PDF</span><div class="snip">' + esc(p.snippet || "—") + "</div></div></div>"
        : '<div class="prov-empty">Sem dados de origem para este campo.</div>';
    }
    const ov = document.createElement("div");
    ov.className = "overlay prov-overlay";
    ov.innerHTML =
      '<div class="prov-modal card"><div class="grad-bar"></div>' +
      '<div class="pm-head"><div><div class="pm-field">' + esc(fieldLabel(key)) + " · " + esc(insurerById(col.insurer_id).name) + "</div>" +
      '<div class="pm-value">' + esc(value || "—") + "</div></div>" +
      '<button class="btn icon ghost" data-close>' + I.x + "</button></div>" +
      '<div class="pm-badge ' + cls + '"><span class="prov-dot ' + cls + '"></span><b>' + mlabel + "</b><span class=\"muted\">" + mdesc + "</span></div>" +
      '<div class="provtoggle sm inpop"><span class="pt-lbl">Ver origem:</span>' +
      '<button data-pv="visual"' + (S.provView === "visual" ? ' class="on"' : "") + ">Visual</button>" +
      '<button data-pv="texto"' + (S.provView === "texto" ? ' class="on"' : "") + ">Texto</button></div>" +
      '<div class="pm-body">' + body + "</div></div>";
    document.body.appendChild(ov);
    const close = () => { ov.remove(); S._prov = null; };
    ov.querySelector("[data-close]").onclick = close;
    ov.addEventListener("mousedown", (e) => { if (e.target === ov) close(); });
    ov.querySelectorAll("[data-pv]").forEach((b) => (b.onclick = () => { S.provView = b.dataset.pv; syncTopToggle(); openProvenance(ci, key); }));
    // auto-scroll até o destaque (modo visual)
    const scroll = ov.querySelector(".prov-page-scroll"), hl = ov.querySelector(".pf-hl");
    if (scroll && hl) scroll.scrollTop = Math.max(0, parseFloat(hl.style.top) - 120);
  }

  function provPageHTML(pg, bbox) {
    const W = 470, sc = W / pg.w, H = pg.h * sc;
    const frags = pg.fragments.map((f) => {
      const l = f.bbox[0] * sc, t = f.bbox[1] * sc, h = (f.bbox[3] - f.bbox[1]) * sc;
      return '<div class="pf" style="left:' + l.toFixed(1) + "px;top:" + t.toFixed(1) + "px;font-size:" + Math.max(4, h * 0.92).toFixed(1) + 'px">' + esc(f.text) + "</div>";
    }).join("");
    const hl = '<div class="pf-hl" style="left:' + (bbox[0] * sc).toFixed(1) + "px;top:" + (bbox[1] * sc).toFixed(1) +
      "px;width:" + ((bbox[2] - bbox[0]) * sc).toFixed(1) + "px;height:" + ((bbox[3] - bbox[1]) * sc).toFixed(1) + 'px"></div>';
    return '<div class="prov-page-scroll"><div class="prov-page" style="width:' + W + "px;height:" + H.toFixed(0) + 'px">' + frags + hl + "</div></div>";
  }

  /* ---------------- Painel "Não mapeado" ---------------- */
  function allFieldKeys() {
    const t = tpl(); const out = t.info.map((r) => [r.key, r.label]);
    t.sections.forEach((s) => s.rows.forEach((r) => out.push([r.key, s.title + " · " + r.label])));
    return out;
  }
  function openUnmapped() {
    const P = S.proposal;
    const ex = document.querySelector(".unmap-overlay"); if (ex) ex.remove();
    const opts = allFieldKeys().map(([k, l]) => '<option value="' + esc(k) + '">' + esc(l) + "</option>").join("");
    const cols = P.columns.map((col, ci) => {
      const items = (col.unmapped || []);
      const rows = items.length
        ? items.map((it, ii) =>
            '<div class="um-row" data-ci="' + ci + '" data-ii="' + ii + '"><div class="um-txt"><span class="um-pg">p' + it.page + "</span>" + esc(it.text) + "</div>" +
            '<div class="um-act"><select class="select input um-sel"><option value="">Atribuir a…</option>' + opts + "</select></div></div>").join("")
        : '<div class="prov-empty">Nada fora do mapeamento nesta coluna.</div>';
      return '<div class="um-col"><div class="um-colh"><span class="badge-n">' + (ci + 1) + "</span>" + esc(insurerById(col.insurer_id).name) +
        '<span class="muted"> · ' + items.length + " item(ns)</span></div>" + rows + "</div>";
    }).join("");
    const ov = document.createElement("div");
    ov.className = "overlay unmap-overlay";
    ov.innerHTML =
      '<div class="unmap-modal card"><div class="grad-bar"></div>' +
      '<div class="um-head"><div><h3>Deixado de fora</h3><p class="muted">Valores presentes no PDF que nenhum campo capturou. Atribua a um campo ou ignore.</p></div>' +
      '<button class="btn icon ghost" data-close>' + I.x + "</button></div>" +
      '<div class="um-body">' + cols + "</div></div>";
    document.body.appendChild(ov);
    const close = () => ov.remove();
    ov.querySelector("[data-close]").onclick = close;
    ov.addEventListener("mousedown", (e) => { if (e.target === ov) close(); });
    ov.querySelectorAll(".um-sel").forEach((sel) => (sel.onchange = () => {
      const key = sel.value; if (!key) return;
      const row = sel.closest(".um-row"), ci = +row.dataset.ci, ii = +row.dataset.ii;
      promoteUnmapped(ci, ii, key); close(); renderReview(); openUnmapped();
    }));
  }
  function promoteUnmapped(ci, ii, key) {
    const col = S.proposal.columns[ci];
    const it = (col.unmapped || [])[ii]; if (!it) return;
    const m = it.text.match(/R\$ ?[\d.]+,\d{2}|\d+ ?(dias|km)|\d+[.,]?\d*%|sim|não|nao|km ?ilimitad[oa]?/i);
    const val = m ? m[0] : it.text;
    col.fields[key] = val;
    col.provenance[key] = { value: val, method: "manual", page: it.page, bbox: it.bbox, snippet: it.text, anchor: null };
    if (ci === 0 && key in S.proposal.info) S.proposal.info[key] = val;
    col.unmapped.splice(ii, 1);
    toast("“" + fieldLabel(key) + "” preenchido a partir do PDF.", "ok");
  }

  /* =========================================================================
     EXPORT PDF (html2canvas + jsPDF)
     ========================================================================= */
  async function doExport(btnSel) {
    if (pending() > 0) { toast("Há campos pendentes. Preencha antes de exportar.", "err"); return; }
    if (!window.jspdf || !window.html2canvas) { toast("Bibliotecas de PDF não carregadas.", "err"); return; }
    const btn = document.querySelector(btnSel || "#expbtn"); const old = btn ? btn.innerHTML : "";
    if (btn) { btn.disabled = true; btn.innerHTML = '<span class="spin"></span> Gerando…'; }
    // garante que o documento existe fora do wizard para captura
    const wiz = document.querySelector(".wiz-overlay"); if (wiz) wiz.style.visibility = "hidden";
    if (!$("#doc")) renderReview();
    try {
      // clona o doc sem edição para captura limpa
      const src = $("#doc");
      src.classList.add("exporting");
      src.querySelectorAll("[contenteditable]").forEach((e) => e.setAttribute("contenteditable", "false"));
      const pages = src.querySelectorAll(".doc-page");
      const { jsPDF } = window.jspdf;
      const pdf = new jsPDF({ unit: "pt", format: "a4", orientation: "portrait" });
      const pw = pdf.internal.pageSize.getWidth(), ph = pdf.internal.pageSize.getHeight();
      for (let i = 0; i < pages.length; i++) {
        const canvas = await window.html2canvas(pages[i], { scale: 2, useCORS: true, backgroundColor: "#ffffff" });
        const img = canvas.toDataURL("image/jpeg", 0.94);
        const ratio = canvas.width / canvas.height;
        let w = pw, h = w / ratio;
        if (h > ph) { h = ph; w = h * ratio; }
        const x = (pw - w) / 2, y = 0;
        if (i > 0) pdf.addPage();
        pdf.addImage(img, "JPEG", x, y, w, h);
      }
      const nome = (S.proposal.info.segurado || "cliente").split(" ")[0].toLowerCase();
      pdf.save("proposta-newa-" + nome + ".pdf");
      src.querySelectorAll("[contenteditable]").forEach((e) => e.setAttribute("contenteditable", "true"));
      src.classList.remove("exporting");
      const w = document.querySelector(".wiz-overlay"); if (w) w.remove();
      toast("PDF gerado com sucesso.", "ok");
    } catch (e) {
      const w = document.querySelector(".wiz-overlay"); if (w) w.style.visibility = "visible";
      toast("Falha ao gerar PDF: " + (e.message || e), "err");
    } finally { const d = $("#doc"); if (d) d.classList.remove("exporting"); if (btn) { btn.disabled = false; btn.innerHTML = old; } }
  }

  /* =========================================================================
     ASSISTENTE DE CONFIRMAÇÃO (etapas: fonte à vista + resultado editável)
     ========================================================================= */
  function buildSteps() {
    const T = tpl(); const steps = [];
    if (T.cover.show) steps.push({ type: "cover", title: "Introdução (capa)", rows: [] });
    steps.push({ type: "info", title: T.infoTitle, rows: T.info.filter((r) => r.show) });
    T.sections.filter((s) => s.show).forEach((s) => steps.push({ type: "sec", title: s.title, rows: s.rows.filter((r) => r.show) }));
    if (T.obs.show) steps.push({ type: "obs", title: T.obs.title, rows: [] });
    return steps;
  }

  function openConfirmWizard() {
    S._wiz = { step: 0, mode: "page", steps: buildSteps() };
    const ex = document.querySelector(".wiz-overlay"); if (ex) ex.remove();
    const ov = document.createElement("div");
    ov.className = "overlay wiz-overlay";
    ov.innerHTML =
      '<div class="wiz card">' +
      '<div class="wiz-top"><div class="wiz-ttl"><div class="wiz-eyebrow">Conferência antes de gerar</div><h2 id="wiz-h"></h2></div>' +
      '<div class="wiz-modes" id="wiz-modes"><span class="pt-lbl">Fonte:</span>' +
      '<button data-wm="page" class="on">Destaque na página</button><button data-wm="crop">Recortes</button></div>' +
      '<button class="btn icon ghost" data-wclose>' + I.x + "</button></div>" +
      '<div class="wiz-steps" id="wiz-steps"></div>' +
      '<div class="wiz-body" id="wiz-body"></div>' +
      '<div class="wiz-foot"><div class="wiz-foot-l"><button class="btn secondary" id="wiz-fill">' + I.wand + " Preencher vazios</button>" +
      '<button class="btn ghost" id="wiz-prev">' + I.back + " Anterior</button></div>" +
      '<div class="wiz-count" id="wiz-count"></div>' +
      '<button class="btn" id="wiz-next">Próximo</button></div></div>';
    document.body.appendChild(ov);
    ov.querySelector("[data-wclose]").onclick = () => ov.remove();
    ov.querySelectorAll("[data-wm]").forEach((b) => (b.onclick = () => {
      S._wiz.mode = b.dataset.wm;
      ov.querySelectorAll("[data-wm]").forEach((x) => x.classList.toggle("on", x === b));
      renderWizStep();
    }));
    $("#wiz-fill").onclick = () => {
      const keys = dataKeys(true);
      S.proposal.columns.forEach((col) => keys.forEach((k) => { if (!String(col.fields[k] || "").trim()) col.fields[k] = "Não Contratado"; }));
      renderWizStep(); toast("Campos vazios preenchidos com “Não Contratado”.", "ok");
    };
    $("#wiz-prev").onclick = () => { if (S._wiz.step > 0) { S._wiz.step--; renderWizStep(); } };
    $("#wiz-next").onclick = () => {
      if (S._wiz.step < S._wiz.steps.length - 1) { S._wiz.step++; renderWizStep(); return; }
      // última etapa: gerar (ou apontar a pendência)
      const n = pending();
      if (n > 0) {
        const fp = S._wiz.steps.findIndex(stepHasPending);
        if (fp >= 0) { S._wiz.step = fp; renderWizStep(); }
        toast(n + " campo(s) ainda vazio(s). Preencha os destacados em vermelho ou use “Preencher vazios”.", "err");
        return;
      }
      doExport("#wiz-next");
    };
    renderWizStep();
  }

  function stepHasPending(st) {
    const P = S.proposal;
    if (st.type === "info") return st.rows.some((r) => r.req && !String(P.info[r.key] || "").trim());
    if (st.type === "sec") return st.rows.some((r) => !r.optional && P.columns.some((c) => !String(c.fields[r.key] || "").trim()));
    return false;
  }

  function renderWizStep() {
    const W = S._wiz, P = S.proposal, steps = W.steps, st = steps[W.step];
    $("#wiz-h").textContent = st.title;
    $("#wiz-count").textContent = "Etapa " + (W.step + 1) + " de " + steps.length;
    // stepper (marca etapas com campos pendentes)
    $("#wiz-steps").innerHTML = steps.map((s, i) => {
      const pend = stepHasPending(s);
      return '<button class="wstep' + (i === W.step ? " on" : "") + (pend ? " pend" : i < W.step ? " done" : "") + '" data-si="' + i + '">' +
        '<span class="wnum">' + (pend ? "!" : i < W.step ? I.check : i + 1) + "</span><span class=\"wlbl\">" + esc(s.title) + "</span></button>";
    }).join("");
    $("#wiz-steps").querySelectorAll("[data-si]").forEach((b) => (b.onclick = () => { W.step = +b.dataset.si; renderWizStep(); }));
    // nav labels
    $("#wiz-prev").style.visibility = W.step === 0 ? "hidden" : "visible";
    const last = W.step === steps.length - 1;
    $("#wiz-next").innerHTML = last ? I.dl + " Confirmar e gerar PDF" : "Próximo " + I.fwd;
    // botão "Preencher vazios" ganha destaque quando há pendências
    const n = pending();
    const fill = $("#wiz-fill");
    if (fill) { fill.classList.toggle("hot", n > 0); fill.innerHTML = I.wand + (n > 0 ? " Preencher " + n + " vazio(s)" : " Preencher vazios"); }
    // body
    $("#wiz-body").innerHTML = wizStepBody(st);
    wireWizStep(st);
  }

  function wizStepBody(st) {
    const P = S.proposal, ncols = P.columns.length;
    const center = wizCenter(st);
    if (st.type === "cover" || st.type === "obs") {
      return '<div class="wiz-stage solo">' + center +
        '<div class="wiz-note">' + I.alert + "<span>Este bloco é <b>texto do modelo</b> — não vem dos PDFs. Ajuste o conteúdo padrão em <b>Editar modelo</b>.</span></div></div>";
    }
    // fontes por coluna
    const sources = P.columns.map((col, ci) => wizSource(st, ci)).join("");
    if (ncols === 2) {
      // uma fonte de cada lado, resultado no centro
      const src = P.columns.map((col, ci) => wizSource(st, ci));
      return '<div class="wiz-stage trio"><div class="wiz-src-col">' + src[0] + "</div>" +
        '<div class="wiz-center-col">' + center + "</div>" +
        '<div class="wiz-src-col">' + src[1] + "</div></div>";
    }
    return '<div class="wiz-stage stack"><div class="wiz-center-col">' + center + "</div>" +
      '<div class="wiz-sources-grid">' + sources + "</div></div>";
  }

  // centro: resultado final da etapa, editável
  function wizCenter(st) {
    const P = S.proposal;
    if (st.type === "cover") {
      const cv = coverData();
      const nome = (P.info.segurado || "Cliente").split(" ")[0];
      return '<div class="wiz-card"><div class="wc-h">Resultado — capa</div><div class="wc-body">' +
        '<div class="field"><label>Saudação</label><input class="input" data-cover="greeting" value="' + esc(cv.greeting) + '"></div>' +
        '<div class="wc-note muted">Prévia: <b>' + esc(cv.greeting.replace("{{primeiro_nome}}", nome)) + "</b></div>" +
        cv.paragraphs.map((p, i) => '<div class="field mt"><label>Parágrafo ' + (i + 1) + '</label><textarea class="input" rows="2" data-coverp="' + i + '">' + esc(p) + "</textarea></div>").join("") +
        "</div></div>";
    }
    if (st.type === "obs") {
      return '<div class="wiz-card"><div class="wc-h">Resultado — observações</div><div class="wc-body">' +
        (P.obs || []).map((o, i) => '<div class="field' + (i ? " mt" : "") + '"><textarea class="input" rows="2" data-obs="' + i + '">' + esc(o) + "</textarea></div>").join("") +
        "</div></div>";
    }
    // info / sec: tabela rótulo × colunas
    const P2 = S.proposal, ncols = P2.columns.length;
    const head = '<div class="wt-row wt-head"><div class="wt-lbl"></div>' +
      P2.columns.map((c, i) => '<div class="wt-col" style="color:' + insurerById(c.insurer_id).color + '">' + (i + 1) + " · " + esc(insurerById(c.insurer_id).name) + "</div>").join("") + "</div>";
    const rows = st.rows.map((r) => {
      const req = st.type === "info" ? !!r.req : !r.optional;
      const cells = P2.columns.map((col, ci) => {
        const val = st.type === "info" ? P2.info[r.key] : col.fields[r.key];
        const prov = (col.provenance || {})[r.key];
        const cls = provClass(prov) || "";
        const empty = !String(val || "").trim();
        const attr = st.type === "info"
          ? ' data-winfo="' + esc(r.key) + '"'
          : ' data-wk="' + esc(r.key) + '" data-wc="' + ci + '"';
        return '<div class="wt-cell"><div class="wcap' + (empty && req ? " empty-req" : "") + '" contenteditable="true" spellcheck="false"' + attr +
          ' data-hl="' + esc(r.key) + '_' + ci + '">' + esc(val || "") + "</div>" +
          (cls ? '<span class="prov-dot ' + cls + '"></span>' : "") + "</div>";
      }).join("");
      return '<div class="wt-row"><div class="wt-lbl">' + esc(r.label) + "</div>" + cells + "</div>";
    }).join("");
    return '<div class="wiz-card"><div class="wc-h">Resultado no documento final</div>' +
      '<div class="wtable" style="--wc:' + ncols + '">' + head + rows + "</div></div>";
  }

  // fonte de uma coluna: página real com marca-texto (ou recortes)
  function wizSource(st, ci) {
    const col = S.proposal.columns[ci];
    const ins = insurerById(col.insurer_id);
    const keys = st.rows.map((r) => r.key);
    // reúne destaques desta etapa que têm origem no PDF
    const hs = [];
    keys.forEach((k) => {
      const p = (col.provenance || {})[k];
      if (p && p.page && p.bbox) hs.push({ key: k, page: p.page, bbox: p.bbox, value: (st.type === "info" ? S.proposal.info[k] : col.fields[k]), method: provClass(p) });
    });
    const headh = '<div class="ws-h"><span class="badge-n" style="background:' + ins.color + '">' + (ci + 1) + "</span>" + esc(ins.name) +
      '<span class="muted"> · ' + (col.profile_used ? "perfil" : "IA") + "</span></div>";
    if (!hs.length) return '<div class="wiz-src">' + headh + '<div class="ws-empty">' + I.alert + " Sem origem localizada nesta etapa.</div></div>";
    if (S._wiz.mode === "crop") {
      const crops = hs.map((h) => wizCrop(col, h)).join("");
      return '<div class="wiz-src">' + headh + '<div class="ws-crops">' + crops + "</div></div>";
    }
    // modo página: agrupa por página
    const byPage = {};
    hs.forEach((h) => (byPage[h.page] = byPage[h.page] || []).push(h));
    const pagesHTML = Object.keys(byPage).map((pn) => wizPage(col, +pn, byPage[pn])).join("");
    return '<div class="wiz-src">' + headh + '<div class="ws-pages">' + pagesHTML + "</div></div>";
  }

  function pageMeta(col, pn) { return (col.pages || []).find((x) => x.n === pn); }
  function imgUrl(col, pn) { return col.doc_id ? API + "/page-image?doc=" + encodeURIComponent(col.doc_id) + "&p=" + pn : null; }

  function wizPage(col, pn, hs) {
    const meta = pageMeta(col, pn); if (!meta) return "";
    const W = 340, sc = W / meta.w;
    const url = imgUrl(col, pn);
    const bg = url
      ? '<img class="ws-img" src="' + url + '" alt="p' + pn + '" loading="lazy">'
      : facsimile(meta, sc); // fallback portátil (sem raster)
    const marks = hs.map((h) =>
      '<div class="ws-hl ' + (h.method || "") + '" data-hl="' + esc(h.key) + "_" + hcol(col) + '" style="left:' + (h.bbox[0] * sc).toFixed(1) +
      "px;top:" + (h.bbox[1] * sc).toFixed(1) + "px;width:" + ((h.bbox[2] - h.bbox[0]) * sc).toFixed(1) +
      "px;height:" + ((h.bbox[3] - h.bbox[1]) * sc).toFixed(1) + 'px" title="' + esc(h.value || "") + '"></div>').join("");
    return '<div class="ws-page" style="width:' + W + "px;height:" + (meta.h * sc).toFixed(0) + 'px">' + bg + marks +
      (url ? '<div class="ws-zoom-hint">' + I.zoom + " passe o mouse p/ ampliar</div>" : "") +
      '<div class="ws-pg-tag">p' + pn + "</div></div>";
  }
  function hcol(col) { return S.proposal.columns.indexOf(col); }

  function facsimile(meta, sc) {
    return (meta.fragments || []).map((f) =>
      '<div class="ws-frag" style="left:' + (f.bbox[0] * sc).toFixed(1) + "px;top:" + (f.bbox[1] * sc).toFixed(1) +
      "px;font-size:" + Math.max(4, (f.bbox[3] - f.bbox[1]) * sc * 0.9).toFixed(1) + 'px">' + esc(f.text) + "</div>").join("");
  }

  function cropUrl(col, h) {
    if (!col.doc_id) return null;
    const vw = h.bbox[2] - h.bbox[0], vh = h.bbox[3] - h.bbox[1];
    const padx = Math.max(12, vw * 0.15);
    const padTop = 2.5, padBot = Math.max(4, vh * 0.35); // topo apertado evita o cabeçalho da tabela
    const x0 = (h.bbox[0] - padx).toFixed(1), y0 = (h.bbox[1] - padTop).toFixed(1);
    const x1 = (h.bbox[2] + padx).toFixed(1), y1 = (h.bbox[3] + padBot).toFixed(1);
    return API + "/crop?doc=" + encodeURIComponent(col.doc_id) + "&p=" + h.page +
      "&x0=" + x0 + "&y0=" + y0 + "&x1=" + x1 + "&y1=" + y1;
  }
  function wizCrop(col, h) {
    const label = fieldLabel(h.key);
    const url = cropUrl(col, h);
    const media = url
      ? '<div class="wc-crop"><img class="wc-crop-img" src="' + url + '" alt="' + esc(h.value || "") + '" loading="lazy"></div>'
      : '<div class="wc-crop facs">' + esc(h.value || "") + "</div>";
    return '<div class="ws-crop-item" data-hl="' + esc(h.key) + "_" + hcol(col) + '"><div class="wc-crop-lbl">' + esc(label) +
      '<span class="muted"> · p' + h.page + "</span></div>" + media + "</div>";
  }

  function coverData() {
    if (!S.proposal.coverOverride) S.proposal.coverOverride = clone(tpl().cover);
    return S.proposal.coverOverride;
  }

  function wireWizStep(st) {
    const body = $("#wiz-body");
    // edição do centro
    body.querySelectorAll("[contenteditable]").forEach((el) => {
      el.addEventListener("focus", () => highlightFor(el.dataset.hl, true));
      el.addEventListener("blur", () => {
        const v = el.textContent.trim();
        if (el.dataset.winfo != null) S.proposal.info[el.dataset.winfo] = v;
        else if (el.dataset.wk != null) S.proposal.columns[+el.dataset.wc].fields[el.dataset.wk] = v;
        highlightFor(el.dataset.hl, false);
      });
      el.addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); el.blur(); } });
    });
    body.querySelectorAll("[data-cover]").forEach((el) => (el.oninput = () => { coverData().greeting = el.value; }));
    body.querySelectorAll("[data-coverp]").forEach((el) => (el.oninput = () => { coverData().paragraphs[+el.dataset.coverp] = el.value; }));
    body.querySelectorAll("[data-obs]").forEach((el) => (el.oninput = () => { S.proposal.obs[+el.dataset.obs] = el.value; }));
    // clique num destaque -> foca a célula correspondente
    body.querySelectorAll(".ws-hl, .ws-crop-item").forEach((m) => (m.onclick = () => {
      const cell = body.querySelector('.wcap[data-hl="' + cssEsc(m.dataset.hl) + '"]');
      if (cell) { cell.focus(); document.getSelection().selectAllChildren(cell); }
    }));
    // lupa/zoom nas páginas de origem (modo "Destaque na página")
    body.querySelectorAll(".ws-page").forEach(attachMagnifier);
  }

  function attachMagnifier(pageEl) {
    const img = pageEl.querySelector(".ws-img");
    if (!img || pageEl.dataset.mag) return;
    pageEl.dataset.mag = "1";
    const ZOOM = 2.5, LENS = 168;
    let lens = null;
    const ensure = () => {
      if (lens) return;
      lens = document.createElement("div");
      lens.className = "mag-lens";
      lens.style.width = lens.style.height = LENS + "px";
      lens.style.backgroundImage = "url(" + img.src + ")";
      pageEl.appendChild(lens);
    };
    pageEl.addEventListener("mousemove", (e) => {
      const r = pageEl.getBoundingClientRect();
      const x = e.clientX - r.left, y = e.clientY - r.top;
      if (x < 0 || y < 0 || x > r.width || y > r.height) { if (lens) lens.style.display = "none"; return; }
      ensure(); lens.style.display = "block";
      lens.style.backgroundSize = (r.width * ZOOM).toFixed(0) + "px " + (r.height * ZOOM).toFixed(0) + "px";
      lens.style.backgroundPosition = (-(x * ZOOM - LENS / 2)).toFixed(0) + "px " + (-(y * ZOOM - LENS / 2)).toFixed(0) + "px";
      lens.style.left = (x - LENS / 2).toFixed(0) + "px";
      lens.style.top = (y - LENS / 2).toFixed(0) + "px";
    });
    pageEl.addEventListener("mouseleave", () => { if (lens) { lens.remove(); lens = null; } });
  }
  function cssEsc(s) { return String(s).replace(/"/g, '\\"'); }
  function highlightFor(hl, on) {
    if (!hl) return;
    document.querySelectorAll('.ws-hl[data-hl="' + cssEsc(hl) + '"], .ws-crop-item[data-hl="' + cssEsc(hl) + '"]')
      .forEach((m) => m.classList.toggle("focused", on));
  }

  /* =========================================================================
     VIEW: MODELOS DE ENTRADA (registro de seguradoras)
     ========================================================================= */
  function viewModelos() {
    root().innerHTML = shell("Modelos de Entrada", "Seguradoras aceitas",
      '<button class="btn" id="addins">' + I.plus + " Nova seguradora</button>");
    const c = $("#view-content");
    c.innerHTML =
      '<p class="muted" style="max-width:720px;margin-bottom:18px">Cada seguradora define a <b>cor do cabeçalho</b> da coluna no comparativo e as <b>palavras-chave</b> usadas para reconhecer o PDF automaticamente. O app lê PDFs de qualquer layout via IA — adicione aqui uma seguradora nova para dar a ela a cor e o nome corretos.</p>' +
      '<div class="card" style="overflow:hidden"><table class="table"><thead><tr><th>Cor</th><th>Seguradora</th><th>Palavras-chave</th><th></th></tr></thead><tbody id="itb"></tbody></table></div>';
    renderInsurersTable();
    $("#addins").onclick = () => editInsurer(null);
  }
  function renderInsurersTable() {
    const tb = $("#itb"); if (!tb) return;
    tb.innerHTML = S.insurers.map((x, i) =>
      "<tr><td><span class='swatch' style='background:" + x.color + "'></span></td>" +
      "<td><b>" + esc(x.name) + "</b></td>" +
      "<td class='muted'>" + esc((x.detect || []).join(", ") || "—") + "</td>" +
      "<td style='text-align:right;white-space:nowrap'>" +
      "<button class='btn icon ghost' data-ed='" + i + "'>" + I.edit + "</button>" +
      (x.id === "generico" ? "" : "<button class='btn icon ghost' data-del='" + i + "'>" + I.trash + "</button>") +
      "</td></tr>").join("");
    tb.querySelectorAll("[data-ed]").forEach((b) => (b.onclick = () => editInsurer(+b.dataset.ed)));
    tb.querySelectorAll("[data-del]").forEach((b) => (b.onclick = () => delInsurer(+b.dataset.del)));
  }
  function editInsurer(idx) {
    const x = idx == null ? { id: "", name: "", color: "#12703A", color2: "#1F9E4A", text: "light", abbr: "", detect: [], logo: "", logo_small: "" } : S.insurers[idx];
    modal({
      title: idx == null ? "Nova seguradora" : "Editar seguradora",
      bodyHTML:
        '<div class="field"><label>Nome</label><input class="input" id="mn" value="' + esc(x.name) + '"></div>' +
        '<div class="field"><label>ID (sem espaços, minúsculo)</label><input class="input" id="mid" value="' + esc(x.id) + '"' + (idx != null ? " disabled" : "") + "></div>" +
        '<div style="display:flex;gap:12px"><div class="field" style="flex:1"><label>Cor da marca</label><input class="input" type="color" id="mc" value="' + esc(x.color) + '" style="height:44px;padding:4px"></div>' +
        '<div class="field" style="flex:1"><label>Texto do cabeçalho</label><select class="select input" id="mt"><option value="light"' + (x.text !== "dark" ? " selected" : "") + '>Claro</option><option value="dark"' + (x.text === "dark" ? " selected" : "") + ">Escuro</option></select></div></div>" +
        '<div class="field"><label>Palavras-chave (separe por vírgula)</label><input class="input" id="md" value="' + esc((x.detect || []).join(", ")) + '"></div>' +
        '<div class="field"><label>Logo grande — com texto (URL, usado na capa)</label><input class="input" id="mlg" value="' + esc(x.logo || "") + '" placeholder="https://..."></div>' +
        '<div class="field"><label>Logo pequeno — sem texto (URL, usado no cabeçalho da coluna)</label><input class="input" id="mls" value="' + esc(x.logo_small || "") + '" placeholder="https://..."></div>',
      onOk: async (ov) => {
        const g = (s) => ov.querySelector(s).value.trim();
        const obj = { id: g("#mid") || g("#mn").toLowerCase().replace(/\s+/g, ""), name: g("#mn"), color: g("#mc"), color2: x.color2 || g("#mc"), text: g("#mt"), abbr: (x.abbr || g("#mn").slice(0, 2).toUpperCase()), detect: g("#md").split(",").map((s) => s.trim()).filter(Boolean), logo: g("#mlg"), logo_small: g("#mls") };
        if (!obj.name) { toast("Informe o nome.", "err"); return false; }
        if (idx == null) S.insurers.splice(S.insurers.length - 1, 0, obj); else S.insurers[idx] = obj;
        await saveInsurers(); renderInsurersTable();
      },
    });
  }
  function delInsurer(idx) {
    const x = S.insurers[idx];
    modal({
      title: "Remover seguradora", danger: true, okText: "Remover",
      bodyHTML: "<p>Remover <b>" + esc(x.name) + "</b> da lista de modelos de entrada?</p>",
      onOk: async () => { S.insurers.splice(idx, 1); await saveInsurers(); renderInsurersTable(); toast("Seguradora removida.", "ok"); },
    });
  }
  async function saveInsurers() { await api("/insurers", { method: "POST", body: { insurers: S.insurers } }); }

  /* =========================================================================
     VIEW: USUÁRIOS (admin)
     ========================================================================= */
  async function viewUsuarios() {
    root().innerHTML = shell("Administração", "Usuários",
      '<button class="btn" id="adduser">' + I.plus + " Novo usuário</button>");
    const c = $("#view-content");
    c.innerHTML = '<div class="card" style="overflow:hidden"><table class="table"><thead><tr><th>Nome</th><th>Usuário</th><th>Perfil</th><th></th></tr></thead><tbody id="utb"><tr><td colspan="4"><div class="sk" style="height:20px;width:60%"></div></td></tr></tbody></table></div>';
    $("#adduser").onclick = () => editUser(null);
    await refreshUsers();
  }
  async function refreshUsers() {
    const r = await api("/users");
    const tb = $("#utb"); if (!tb) return;
    tb.innerHTML = (r.users || []).map((u) =>
      "<tr><td><b>" + esc(u.name || u.username) + "</b></td><td class='muted'>" + esc(u.username) + "</td>" +
      "<td><span class='chip " + (u.role === "admin" ? "admin" : "user") + "'>" + (u.role === "admin" ? "Administrador" : "Usuário") + "</span></td>" +
      "<td style='text-align:right;white-space:nowrap'><button class='btn icon ghost' data-eu='" + esc(u.username) + "'>" + I.edit + "</button>" +
      (u.username === S.me.username ? "" : "<button class='btn icon ghost' data-du='" + esc(u.username) + "'>" + I.trash + "</button>") + "</td></tr>").join("");
    tb.querySelectorAll("[data-eu]").forEach((b) => (b.onclick = () => editUser((r.users || []).find((u) => u.username === b.dataset.eu))));
    tb.querySelectorAll("[data-du]").forEach((b) => (b.onclick = () => delUser(b.dataset.du)));
  }
  function editUser(u) {
    const isNew = !u;
    modal({
      title: isNew ? "Novo usuário" : "Editar " + (u.name || u.username),
      bodyHTML:
        '<div class="field"><label>Nome completo</label><input class="input" id="un" value="' + esc(u ? u.name : "") + '"></div>' +
        '<div class="field"><label>Usuário (login)</label><input class="input" id="uu" value="' + esc(u ? u.username : "") + '"' + (isNew ? "" : " disabled") + "></div>" +
        '<div class="field"><label>Senha' + (isNew ? "" : " (deixe vazio para manter)") + '</label><input class="input" type="password" id="up"></div>' +
        '<div class="field"><label>Perfil</label><select class="select input" id="ur"><option value="user"' + (u && u.role === "admin" ? "" : " selected") + '>Usuário</option><option value="admin"' + (u && u.role === "admin" ? " selected" : "") + ">Administrador</option></select></div>",
      onOk: async (ov) => {
        const g = (s) => ov.querySelector(s).value.trim();
        const body = { name: g("#un"), role: g("#ur") };
        const pw = ov.querySelector("#up").value;
        if (isNew) {
          body.username = g("#uu"); body.password = pw;
          if (!body.username || !pw) { toast("Usuário e senha são obrigatórios.", "err"); return false; }
          await api("/users", { method: "POST", body });
        } else {
          if (pw) body.password = pw;
          await api("/users/" + encodeURIComponent(u.username), { method: "PUT", body });
        }
        await refreshUsers(); toast("Usuário salvo.", "ok");
      },
    });
  }
  function delUser(username) {
    modal({
      title: "Remover usuário", danger: true, okText: "Remover",
      bodyHTML: "<p>Remover o acesso de <b>" + esc(username) + "</b>?</p>",
      onOk: async () => { await api("/users/" + encodeURIComponent(username), { method: "DELETE" }); await refreshUsers(); toast("Usuário removido.", "ok"); },
    });
  }

  /* =========================================================================
     VIEW: EDITAR MODELO (editor do documento — admin)
     ========================================================================= */
  let E = null; // cópia de trabalho do modelo

  function viewEditarModelo() {
    E = clone(tpl());
    root().innerHTML = shell("Editar modelo", "Editar modelo do PDF",
      '<button class="btn ghost" id="tplreset">Restaurar padrão</button>' +
      '<button class="btn" id="tplsave">' + I.check + " Salvar modelo</button>");
    const c = $("#view-content");
    c.innerHTML =
      '<p class="muted" style="max-width:900px;margin-bottom:16px">Arraste pelo <b>⋮⋮</b> para reordenar, clique no olho para mostrar/ocultar, edite os textos e adicione novos campos. Os valores aparecem como <span class="ph-token">{{placeholder}}</span> — na proposta real eles são preenchidos automaticamente.</p>' +
      '<div class="editor"><div class="editor-controls" id="ectrl"></div>' +
      '<div class="editor-preview"><div class="ep-head">Pré-visualização</div><div class="ep-scroll" id="eprev"></div></div></div>';
    $("#tplsave").onclick = saveTemplate;
    $("#tplreset").onclick = () => modal({
      title: "Restaurar modelo padrão", danger: true, okText: "Restaurar",
      bodyHTML: "<p>Isto descarta suas personalizações e volta ao modelo original. Continuar?</p>",
      onOk: async () => { E = DEFAULT_TPL(); rc(); rp(); toast("Modelo restaurado (lembre de salvar).", "ok"); },
    });
    rc(); rp();
  }

  function rp() { // render preview
    const prev = $("#eprev"); if (!prev) return;
    const fakeP = { info: {}, columns: [{ insurer_id: "generico", fields: {} }, { insurer_id: "generico", fields: {} }] };
    prev.innerHTML = '<div class="orca-doc">' + buildDoc(fakeP, false, true, E) + "</div>";
  }

  /* ---- construtores de UI do editor ---- */
  function ec_toggle(on, attrs) { return '<button class="etog' + (on ? " on" : "") + '" ' + attrs + ' title="Mostrar/ocultar">' + (on ? I.eye : I.eyeoff) + "</button>"; }
  const grip = '<span class="grip" title="Arraste para reordenar">' + I.grip + "</span>";

  function rc() { // render controls
    const ctrl = $("#ectrl"); if (!ctrl) return;
    const card = (title, inner, extra) => '<div class="ecard"><div class="ecard-h"><h3>' + esc(title) + "</h3>" + (extra || "") + "</div>" + inner + "</div>";

    // CAPA
    const paras = E.cover.paragraphs.map((p, i) =>
      '<div class="erow" data-idx="' + i + '" data-list="para">' + grip +
      '<textarea class="input erow-in" data-bind="para" data-i="' + i + '" rows="2">' + esc(p) + "</textarea>" +
      '<button class="btn icon ghost edel" data-del="para" data-i="' + i + '">' + I.trash + "</button></div>").join("");
    const capa = card("Capa",
      '<label class="echk"><input type="checkbox" data-bind="cover.show"' + (E.cover.show ? " checked" : "") + "> Mostrar capa</label>" +
      '<div class="field mt"><label>Saudação <span class="muted">(use {{primeiro_nome}})</span></label><input class="input" data-bind="cover.greeting" value="' + esc(E.cover.greeting) + '"></div>' +
      '<div class="elabel mt">Parágrafos</div><div class="elist" data-listwrap="para">' + paras + "</div>" +
      '<button class="btn secondary sm" data-add="para">' + I.plus + " Adicionar parágrafo</button>" +
      '<label class="echk mt"><input type="checkbox" data-bind="cover.showMural"' + (E.cover.showMural ? " checked" : "") + "> Mostrar mural de seguradoras</label>" +
      '<div class="field mt"><label>Texto acima do mural</label><input class="input" data-bind="cover.muralLabel" value="' + esc(E.cover.muralLabel) + '"></div>' +
      '<label class="echk mt"><input type="checkbox" data-bind="cover.showContact"' + (E.cover.showContact ? " checked" : "") + "> Mostrar bloco de contato</label>");

    // TÍTULO
    const titulo = card("Cabeçalho da 2ª página",
      '<div class="field"><label>Subtítulo</label><input class="input" data-bind="subtitle" value="' + esc(E.subtitle) + '"></div>' +
      '<div class="field mt"><label>Título</label><input class="input" data-bind="title" value="' + esc(E.title) + '"></div>');

    // INFORMAÇÕES
    const inforows = E.info.map((r, i) =>
      '<div class="erow" data-idx="' + i + '" data-list="info">' + grip +
      '<input class="input erow-in" data-bind="info.label" data-i="' + i + '" value="' + esc(r.label) + '">' +
      ec_toggle(r.show, 'data-tog="info" data-i="' + i + '"') +
      (r.custom ? '<button class="btn icon ghost edel" data-del="info" data-i="' + i + '">' + I.trash + "</button>" : "") + "</div>").join("");
    const info = card("Informações do veículo e condutor",
      '<div class="field"><label>Título da faixa</label><input class="input" data-bind="infoTitle" value="' + esc(E.infoTitle) + '"></div>' +
      '<div class="elist mt" data-listwrap="info">' + inforows + "</div>" +
      '<button class="btn secondary sm" data-add="info">' + I.plus + " Adicionar campo</button>");

    // SEÇÕES (dados)
    const secs = E.sections.map((s, si) => {
      const rows = s.rows.map((r, ri) =>
        '<div class="erow" data-idx="' + ri + '" data-list="secrow" data-s="' + si + '">' + grip +
        '<input class="input erow-in" data-bind="secrow.label" data-s="' + si + '" data-i="' + ri + '" value="' + esc(r.label) + '">' +
        ec_toggle(r.show, 'data-tog="secrow" data-s="' + si + '" data-i="' + ri + '"') +
        '<button class="btn icon ghost edel" data-del="secrow" data-s="' + si + '" data-i="' + ri + '">' + I.trash + "</button></div>").join("");
      return '<div class="esec" data-idx="' + si + '" data-list="sec"><div class="esec-h">' + grip +
        '<input class="input erow-in strong" data-bind="sec.title" data-s="' + si + '" value="' + esc(s.title) + '">' +
        ec_toggle(s.show, 'data-tog="sec" data-s="' + si + '"') +
        '<button class="btn icon ghost edel" data-del="sec" data-s="' + si + '">' + I.trash + "</button></div>" +
        '<div class="elist" data-listwrap="secrow" data-s="' + si + '">' + rows + "</div>" +
        '<button class="btn secondary sm" data-add="secrow" data-s="' + si + '">' + I.plus + " Adicionar linha</button></div>";
    }).join("");
    const sections = card("Seções comparativas",
      '<div class="elist" data-listwrap="sec">' + secs + "</div>" +
      '<button class="btn secondary sm" data-add="sec">' + I.plus + " Adicionar seção</button>");

    // OBSERVAÇÕES
    const obsrows = E.obs.items.map((o, i) =>
      '<div class="erow" data-idx="' + i + '" data-list="obs">' + grip +
      '<textarea class="input erow-in" data-bind="obs" data-i="' + i + '" rows="2">' + esc(o) + "</textarea>" +
      '<button class="btn icon ghost edel" data-del="obs" data-i="' + i + '">' + I.trash + "</button></div>").join("");
    const obs = card("Observações",
      '<label class="echk"><input type="checkbox" data-bind="obs.show"' + (E.obs.show ? " checked" : "") + "> Mostrar observações</label>" +
      '<div class="field mt"><label>Título</label><input class="input" data-bind="obs.title" value="' + esc(E.obs.title) + '"></div>' +
      '<div class="elist mt" data-listwrap="obs">' + obsrows + "</div>" +
      '<button class="btn secondary sm" data-add="obs">' + I.plus + " Adicionar observação</button>");

    ctrl.innerHTML = capa + titulo + info + sections + obs;
    wireControls();
  }

  function wireControls() {
    const ctrl = $("#ectrl");
    // inputs de texto (atualizam E + preview, sem re-render dos controles)
    ctrl.querySelectorAll("[data-bind]").forEach((el) => {
      const bind = el.dataset.bind;
      const handler = () => {
        const v = el.type === "checkbox" ? el.checked : el.value;
        applyBind(bind, el, v);
        if (el.type === "checkbox") { rc(); rp(); } else { rp(); }
      };
      el.addEventListener(el.type === "checkbox" ? "change" : "input", handler);
    });
    // toggles de visibilidade
    ctrl.querySelectorAll("[data-tog]").forEach((b) => (b.onclick = () => {
      const t = b.dataset.tog, i = +b.dataset.i, s = +b.dataset.s;
      if (t === "info") E.info[i].show = !E.info[i].show;
      else if (t === "sec") E.sections[s].show = !E.sections[s].show;
      else if (t === "secrow") E.sections[s].rows[i].show = !E.sections[s].rows[i].show;
      rc(); rp();
    }));
    // deletar
    ctrl.querySelectorAll("[data-del]").forEach((b) => (b.onclick = () => {
      const t = b.dataset.del, i = +b.dataset.i, s = +b.dataset.s;
      if (t === "para") E.cover.paragraphs.splice(i, 1);
      else if (t === "info") E.info.splice(i, 1);
      else if (t === "obs") E.obs.items.splice(i, 1);
      else if (t === "sec") E.sections.splice(s, 1);
      else if (t === "secrow") E.sections[s].rows.splice(i, 1);
      rc(); rp();
    }));
    // adicionar
    ctrl.querySelectorAll("[data-add]").forEach((b) => (b.onclick = () => {
      const t = b.dataset.add, s = +b.dataset.s;
      if (t === "para") E.cover.paragraphs.push("Novo parágrafo.");
      else if (t === "info") E.info.push({ key: "custom_" + Date.now(), label: "Novo campo", show: true, req: false, custom: true, optional: true });
      else if (t === "obs") E.obs.items.push("Nova observação.");
      else if (t === "sec") E.sections.push({ id: "sec_" + Date.now(), title: "Nova seção", show: true, rows: [{ key: "custom_" + Date.now(), label: "Nova linha", show: true, custom: true, optional: true }] });
      else if (t === "secrow") E.sections[s].rows.push({ key: "custom_" + Date.now(), label: "Nova linha", show: true, custom: true, optional: true });
      rc(); rp();
    }));
    // sortables
    ctrl.querySelectorAll('[data-listwrap="para"]').forEach((el) => makeSortable(el, E.cover.paragraphs, () => { rc(); rp(); }));
    ctrl.querySelectorAll('[data-listwrap="info"]').forEach((el) => makeSortable(el, E.info, () => { rc(); rp(); }));
    ctrl.querySelectorAll('[data-listwrap="obs"]').forEach((el) => makeSortable(el, E.obs.items, () => { rc(); rp(); }));
    ctrl.querySelectorAll('[data-listwrap="sec"]').forEach((el) => makeSortable(el, E.sections, () => { rc(); rp(); }));
    ctrl.querySelectorAll('[data-listwrap="secrow"]').forEach((el) => makeSortable(el, E.sections[+el.dataset.s].rows, () => { rc(); rp(); }));
  }

  function applyBind(bind, el, v) {
    const i = +el.dataset.i, s = +el.dataset.s;
    switch (bind) {
      case "title": E.title = v; break;
      case "subtitle": E.subtitle = v; break;
      case "infoTitle": E.infoTitle = v; break;
      case "cover.show": E.cover.show = v; break;
      case "cover.greeting": E.cover.greeting = v; break;
      case "cover.showMural": E.cover.showMural = v; break;
      case "cover.muralLabel": E.cover.muralLabel = v; break;
      case "cover.showContact": E.cover.showContact = v; break;
      case "para": E.cover.paragraphs[i] = v; break;
      case "info.label": E.info[i].label = v; break;
      case "obs.show": E.obs.show = v; break;
      case "obs.title": E.obs.title = v; break;
      case "obs": E.obs.items[i] = v; break;
      case "sec.title": E.sections[s].title = v; break;
      case "secrow.label": E.sections[s].rows[i].label = v; break;
    }
  }

  function makeSortable(listEl, arr, done) {
    let from = null;
    listEl.querySelectorAll(":scope > [data-idx]").forEach((row) => {
      const h = row.querySelector(":scope > .grip") || row.querySelector(".esec-h > .grip") || row.querySelector(".grip");
      if (h) {
        h.setAttribute("draggable", "true");
        h.addEventListener("dragstart", (e) => { e.stopPropagation(); from = +row.dataset.idx; row.classList.add("dragging"); e.dataTransfer.effectAllowed = "move"; e.dataTransfer.setData("text", ""); });
        h.addEventListener("dragend", () => { row.classList.remove("dragging"); listEl.querySelectorAll(".dragover").forEach((x) => x.classList.remove("dragover")); });
      }
      row.addEventListener("dragover", (e) => { e.preventDefault(); e.stopPropagation(); row.classList.add("dragover"); });
      row.addEventListener("dragleave", () => row.classList.remove("dragover"));
      row.addEventListener("drop", (e) => {
        e.preventDefault(); e.stopPropagation(); row.classList.remove("dragover");
        const to = +row.dataset.idx;
        if (from != null && from !== to) { const m = arr.splice(from, 1)[0]; arr.splice(to, 0, m); done(); }
        from = null;
      });
    });
  }

  async function saveTemplate() {
    const btn = $("#tplsave"); btn.disabled = true; btn.innerHTML = '<span class="spin"></span> Salvando…';
    try {
      await api("/template", { method: "POST", body: { template: E } });
      S.template = clone(E);
      toast("Modelo salvo. As próximas propostas usarão este layout.", "ok");
    } catch (e) { toast("Falha ao salvar: " + (e.message || e), "err"); }
    finally { btn.disabled = false; btn.innerHTML = I.check + " Salvar modelo"; }
  }

  /* =========================================================================
     VIEW: CONFIGURAÇÕES (admin)
     ========================================================================= */
  function viewConfig() {
    const cfg = S.config || {}; const co = cfg.corretora || {};
    root().innerHTML = shell("Configurações", "Configurações");
    const c = $("#view-content");
    c.innerHTML =
      '<div class="stagger" style="max-width:640px;display:flex;flex-direction:column;gap:20px">' +
      '<div class="card pad"><h3 style="margin-bottom:14px">Integração de IA (OpenAI)</h3>' +
      '<div class="field"><label>Chave da API' + (cfg.has_openai_key ? " (configurada — deixe vazio para manter)" : "") + '</label><input class="input" id="cok" type="password" placeholder="sk-..."></div>' +
      '<div class="field" style="margin-top:12px"><label>Modelo</label><input class="input" id="cmodel" value="' + esc(cfg.model || "gpt-5-mini") + '"></div>' +
      '<button class="btn" id="savecfg" style="margin-top:16px">Salvar integração</button></div>' +
      '<div class="card pad"><h3 style="margin-bottom:14px">Dados da corretora (usados na capa da proposta)</h3>' +
      field("cnome", "Nome", co.nome || "NEWA Seguros") +
      field("cemail", "E-mail", co.email || "newaseguros@newaseguros.com.br") +
      field("csite", "Site", co.site || "newaseguros.com.br") +
      field("ctel", "Telefone", co.telefone || "(11) 4040-3665") +
      field("cwpp", "WhatsApp", co.whatsapp || "") +
      field("cend", "Endereço", co.endereco || "") +
      '<button class="btn" id="savecor" style="margin-top:16px">Salvar dados da corretora</button></div></div>';
    $("#savecfg").onclick = async () => {
      const body = { model: $("#cmodel").value.trim() };
      const k = $("#cok").value.trim(); if (k) body.openai_key = k;
      await api("/config", { method: "POST", body }); toast("Integração salva.", "ok"); $("#cok").value = ""; await loadShared();
    };
    $("#savecor").onclick = async () => {
      const corretora = { nome: $("#cnome").value.trim(), email: $("#cemail").value.trim(), site: $("#csite").value.trim(), telefone: $("#ctel").value.trim(), whatsapp: $("#cwpp").value.trim(), endereco: $("#cend").value.trim() };
      await api("/config", { method: "POST", body: { corretora } }); toast("Dados da corretora salvos.", "ok"); await loadShared();
    };
  }
  function field(id, label, val) {
    return '<div class="field" style="margin-top:12px"><label>' + esc(label) + '</label><input class="input" id="' + id + '" value="' + esc(val) + '"></div>';
  }

  window.addEventListener("DOMContentLoaded", boot);
})();
