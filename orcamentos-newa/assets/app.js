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
    phone: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2 4.2 2 2 0 0 1 4 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.2a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2Z"/></svg>',
    mail: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m2 6 10 7 10-7"/></svg>',
    pin: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M21 10c0 6-9 12-9 12s-9-6-9-12a9 9 0 0 1 18 0Z"/><circle cx="12" cy="10" r="3"/></svg>',
    web: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15 15 0 0 1 0 20 15 15 0 0 1 0-20Z"/></svg>',
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
  const S = { me: null, insurers: [], config: null, view: "nova", proposal: null };

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
    ({ nova: viewNova, modelos: viewModelos, usuarios: viewUsuarios, config: viewConfig }[view] || viewNova)();
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
      '<p class="muted" style="font-size:13px;margin-top:2px">Um PDF por proposta — cada uma vira uma coluna do comparativo.</p></div>' +
      '<div class="seg" id="seg">' +
      [1, 2, 3, 4, 5].map((n) => '<button data-n="' + n + '"' + (n === N.count ? ' class="active"' : "") + ">" + n + "</button>").join("") +
      "</div></div>" +
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
    $("#seg").querySelectorAll("button").forEach((b) => (b.onclick = () => {
      N.count = +b.dataset.n;
      $("#seg").querySelectorAll("button").forEach((x) => x.classList.toggle("active", x === b));
      renderSlots(); updateStart();
    }));
    renderSlots(); updateStart();
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
        columns.push({ filename: files[i].name, insurer_id, fields: r.fields, missing: r.missing || [] });
        row.className = "st done"; row.innerHTML = I.check + " ok";
        meta.textContent = (insurerById(insurer_id).name) + " · " + (r.missing || []).length + " campo(s) a revisar";
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
    INFO.forEach(([k]) => (info[k] = columns[0].fields[k] || ""));
    S.proposal = { info, columns, obs: OBS_DEFAULT.slice(), errors };
    if (errors.length) toast(errors.length + " arquivo(s) falharam e foram ignorados.", "err");
    renderReview();
  }

  /* =========================================================================
     REVIEW + DOCUMENTO (edição in-place)
     ========================================================================= */
  function pending() {
    const P = S.proposal; let n = 0;
    INFO.forEach(([k, , req]) => { if (req && !String(P.info[k] || "").trim()) n++; });
    P.columns.forEach((col) => COL_KEYS.forEach((k) => { if (!String(col.fields[k] || "").trim()) n++; }));
    return n;
  }

  function renderReview() {
    const P = S.proposal;
    root().innerHTML = shell("Nova Proposta", "Revisão da proposta",
      '<button class="btn secondary" id="backbtn">' + I.back + " Recomeçar</button>" +
      '<button class="btn secondary" id="fillbtn">Preencher vazios: “Não Contratado”</button>' +
      '<button class="btn" id="expbtn">' + I.dl + " Exportar PDF</button>");
    const c = $("#view-content");
    c.innerHTML =
      '<div id="reviewnote"></div>' +
      '<div class="orca-doc" id="doc">' + buildDoc(P, true) + "</div>";
    $("#backbtn").onclick = () => { if (confirm("Descartar esta proposta e recomeçar?")) { S.proposal = null; S.nova = null; viewNova(); } };
    $("#fillbtn").onclick = () => { fillEmpties(); };
    $("#expbtn").onclick = () => doExport();
    wireDoc();
    updateNote();
  }

  function updateNote() {
    const n = pending();
    const note = $("#reviewnote"); if (!note) return;
    if (n === 0) {
      note.innerHTML = '<div class="alert ok" style="margin-bottom:18px">' + I.check +
        "<span><b>Tudo preenchido.</b> Revise os valores e clique em <b>Exportar PDF</b>.</span></div>";
    } else {
      note.innerHTML = '<div class="alert warn" style="margin-bottom:18px">' + I.alert +
        "<span><b>" + n + " campo(s) pendente(s).</b> Os campos em vermelho estão vazios — preencha ou marque como “Não Contratado”. O PDF não será gerado enquanto houver pendências.</span></div>";
    }
    const exp = $("#expbtn"); if (exp) exp.disabled = n > 0;
  }

  /* constrói o HTML do documento (2 páginas). editable=true -> cápsulas editáveis */
  function buildDoc(P, editable) {
    const cols = P.columns;
    const ncols = cols.length;
    const cfg = S.config.corretora || {};
    const labelw = ncols >= 3 ? "240px" : "300px";

    const cap = (val, kk, ci) => {
      const empty = !String(val || "").trim();
      const yes = /^sim$/i.test(String(val || "").trim());
      const na = /não contratado|nao contratado/i.test(String(val || ""));
      const cls = "cap" + (empty ? " empty" : yes ? " yes" : na ? " na" : "");
      const attrs = editable ? ' contenteditable="true" data-k="' + kk + '" data-c="' + ci + '" spellcheck="false"' : "";
      return '<div class="' + cls + '"' + attrs + ">" + esc(empty ? (editable ? "" : "—") : val) + "</div>";
    };
    const infoCap = (k) => {
      const v = P.info[k], empty = !String(v || "").trim();
      const attrs = editable ? ' contenteditable="true" data-info="' + k + '" spellcheck="false"' : "";
      return '<div class="cap' + (empty ? " empty" : "") + '"' + attrs + ">" + esc(empty ? "" : v) + "</div>";
    };
    const colHead = (col, i) => {
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
    const dataRows = (defs) =>
      '<div class="rows" style="--ncols:' + ncols + ";--labelw:" + labelw + '">' +
      defs.map(([k, lbl]) =>
        '<div class="datarow"><div class="lbl">' + esc(lbl) + "</div>" +
        cols.map((col, i) => cap(col.fields[k], k, i)).join("") + "</div>").join("") +
      "</div>";

    /* ---- CAPA ---- */
    const nome = (P.info.segurado || "Cliente").split(" ")[0];
    const strip = S.insurers.filter((x) => x.id !== "generico")
      .map((x) => x.logo
        ? '<div class="ins-logo"><img src="' + esc(x.logo) + '" alt="' + esc(x.name) + '"></div>'
        : '<span class="ins-txt">' + esc(x.name) + "</span>").join("");
    const cover =
      '<div class="doc-page cover" data-page="1"><div class="topgrad"></div><div class="safe">' +
      '<div class="logo"><img class="logo-img" src="' + LOGO + '" alt="NEWA Seguros"></div>' +
      '<div class="hero-mark">' + MARK + "</div>" +
      '<div class="hello"><h1>Olá, <b>' + esc(nome) + "</b></h1></div>" +
      '<div class="letter"><p>Antes de qualquer coisa, parabéns por esse passo dado junto à <b>NEWA Seguros</b>.</p>' +
      "<p>Aqui, o cuidado com o que é seu começa agora, onde preparamos tudo com atenção aos detalhes.</p>" +
      "<p>A seguir, você encontrará uma proposta personalizada, com tudo o que você precisa saber para escolher com confiança a melhor proteção.</p></div>" +
      '<div class="spacer"></div>' +
      '<div class="strip-label">Trabalhamos com as principais seguradoras do país</div>' +
      '<div class="insurers-strip">' + strip + "</div>" +
      '<div class="contact">' +
      '<div class="blk"><h4>Atendimento</h4>' +
      '<div class="rowc">' + I.web + "<span>" + esc(cfg.site || "newaseguros.com.br") + "</span></div>" +
      '<div class="rowc">' + I.mail + "<span>" + esc(cfg.email || "newaseguros@newaseguros.com.br") + "</span></div>" +
      '<div class="rowc">' + I.pin + "<span>" + esc(cfg.endereco || "—") + "</span></div></div>" +
      '<div class="blk"><h4>Contato</h4>' +
      '<div class="rowc">' + I.phone + "<span>" + esc(cfg.telefone || "(11) 4040-3665") + "</span></div>" +
      (cfg.whatsapp ? '<div class="rowc">' + I.phone + "<span>" + esc(cfg.whatsapp) + "</span></div>" : "") +
      "</div></div></div></div>";

    /* ---- COMPARATIVO ---- */
    const inforow = ([k, lbl]) => '<div class="inforow"><div class="lbl">' + esc(lbl) + ":</div>" + infoCap(k) + "</div>";
    const infoFull = INFO.slice(0, 4);   // segurado, veiculo, ano_modelo, principal_condutor
    const infoPairs = INFO.slice(4);     // data, validade, uso, fipe, condutores, cep
    let pairsHTML = "";
    for (let i = 0; i < infoPairs.length; i += 2)
      pairsHTML += '<div class="infopair">' + inforow(infoPairs[i]) + (infoPairs[i + 1] ? inforow(infoPairs[i + 1]) : "") + "</div>";
    const infoGrid = '<div class="rows infoblock">' + infoFull.map(inforow).join("") + pairsHTML + "</div>";
    const obs =
      '<div class="obs"><div class="obs-t">Observações</div><ul' + (editable ? ' contenteditable="true" data-obs="1"' : "") + ">" +
      P.obs.map((o) => "<li>" + esc(o) + "</li>").join("") + "</ul></div>";
    const compare =
      '<div class="doc-page compare" data-page="2"><div class="topgrad"></div>' +
      '<div class="head"><img class="logo-img" src="' + LOGO + '" alt="NEWA"><div class="tt"><small>NEWA · Corretora de Seguros</small><h1>PROPOSTA DE SEGURO</h1></div></div>' +
      '<div class="sec-bar"><div class="sec-title">Informações do Veículo e Condutor</div></div>' +
      infoGrid +
      secBar("Coberturas") + dataRows(COBERTURAS) +
      secBar("Franquias e Assistências") + dataRows(FRANQUIAS) +
      secBar("Formas de Pagamento") + dataRows(PAGAMENTO) +
      obs +
      '<div class="compare-foot docfoot"><span>NEWA Seguros</span><div class="g"></div><span>Proposta gerada em ' +
      new Date().toLocaleDateString("pt-BR") + "</span></div></div>";

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
    const P = S.proposal;
    P.columns.forEach((col) => COL_KEYS.forEach((k) => { if (!String(col.fields[k] || "").trim()) col.fields[k] = "Não Contratado"; }));
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

  /* =========================================================================
     EXPORT PDF (html2canvas + jsPDF)
     ========================================================================= */
  async function doExport() {
    if (pending() > 0) { toast("Há campos pendentes. Preencha antes de exportar.", "err"); return; }
    if (!window.jspdf || !window.html2canvas) { toast("Bibliotecas de PDF não carregadas.", "err"); return; }
    const btn = $("#expbtn"); const old = btn.innerHTML; btn.disabled = true; btn.innerHTML = '<span class="spin"></span> Gerando…';
    try {
      // clona o doc sem edição para captura limpa
      const src = $("#doc");
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
      toast("PDF gerado com sucesso.", "ok");
    } catch (e) {
      toast("Falha ao gerar PDF: " + (e.message || e), "err");
    } finally { btn.disabled = false; btn.innerHTML = old; }
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
      '<div class="field" style="margin-top:12px"><label>Modelo</label><input class="input" id="cmodel" value="' + esc(cfg.model || "gpt-4o") + '"></div>' +
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
