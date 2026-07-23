# TODO — Orçamentos NEWA

Backlog de melhorias e correções. Marque `[x]` ao concluir.

## Bugfixes do assistente de conferência — CONCLUÍDOS (v0.1 → v0.2)

- [x] **1. Zoom no modo "Destaque na página"** — lupa (magnifier) ao passar o mouse
      sobre a página de origem, ampliando ~2.5× a região sob o cursor. Hint visual
      "passe o mouse p/ ampliar" no canto da página.
- [x] **2. Formatação do aviso amarelo "texto do modelo"** — o texto virava vários
      itens flex (com `gap` entre cada `<b>`). Corrigido envolvendo tudo num `<span>`;
      agora é uma frase corrida.
- [x] **3. Recortes aparecendo em branco (modo "Recortes")** — substituído o
      `background-image` (frágil, dependente de escala/carregamento) por **recorte
      renderizado no servidor** (`GET /api/crop` via PyMuPDF `clip`): `<img>` nítido e
      confiável em qualquer página. Margem superior apertada evita o cabeçalho da tabela.
- [x] **4. Destaque do botão "Preencher vazios"** — virou botão secundário com ícone;
      quando há pendências, ganha destaque âmbar pulsante e mostra o contador
      ("Preencher N vazio(s)").
- [x] **5. Banner das seguradoras no documento** — faixa "Comparativo entre seguradoras"
      no topo do comparativo, com logo colorido + nome de cada seguradora, deixando
      claro quais duas propostas estão sendo comparadas.
- [x] **6. "Quantas propostas comparar?"** — 2 é o padrão absoluto; 1/3/4/5 marcadas
      com badge **beta** e aviso "Em desenvolvimento — pode apresentar bugs".

## Extração — perfis e cobertura

- [x] **Modelo padrão → `gpt-5-mini`** com `reasoning_effort=minimal` + schema só dos
      campos que faltam (extração de 65s → ~8s por arquivo).
- [x] **Motor**: estratégia `text_regex` (campos em texto corrido) + tolerância x
      assimétrica (`xlo`/`xhi`) para evitar coluna anterior.
- [x] **Perfil "autoperfil"** (Aliro/Yelum) e **"suhai"** autorados; **camada genérica**
      (`_generic.json`) que preenche campos de rótulo inequívoco (RCF, CEP, vidros,
      faróis, lanternas, retrovisores, reboque, carro reserva) em QUALQUER layout, com
      guardas contra valor errado (RCF exige LMI ≥ 10.000). Verde/arquivo: ~3.7 → ~9.7
      (de ~30); nenhum valor verde incorreto (auditado).
- [ ] Perfis dedicados para os singletons ainda majoritariamente na IA:
      **bradesco, zurich, hdi, mapfre, tokio, darwin, allianz(nativo multi-oferta),
      justos** — cada um tem layout próprio; hoje o genérico pega 3–9 campos e a IA
      (verificada) completa o resto.
- [ ] Editar/gerenciar perfis pela UI (seção *Modelos de Entrada*).
- [ ] Suporte real a comparar 3–5 propostas (hoje em beta).

## Produção (WordPress)

- [ ] Portar motor de extração + perfis para PHP (`smalot/pdfparser`) — incluindo as
      estratégias `table_cell`/`text_regex`/`below(xlo,xhi)` e a camada `_generic`.
- [ ] Login via usuários nativos do WordPress; persistência em `wp_options`.
- [ ] Empacotador `.zip` do plugin instalável.
- [ ] Modo Visual/recortes: usar Imagick quando disponível; senão, o fac-símile de
      fragmentos (o cliente já degrada para o fac-símile quando não há imagem).

## Geral

- [ ] Fallback de visão (IA) para PDFs escaneados (sem texto nativo).
- [ ] Calibrar cores/logos oficiais das seguradoras.
