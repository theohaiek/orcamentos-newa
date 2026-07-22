# Especificação — Orçamentos NEWA

## Objetivo
Aplicativo (plugin WordPress + servidor de dev local) que recebe PDFs de cotação de
seguro auto de várias seguradoras e gera uma **Proposta de Seguro** comparativa de 2
páginas (capa personalizada + comparativo lado a lado), pronta para o cliente,
seguindo a estética da marca **NEWA**.

## Fluxo do usuário
Login → **Nova Proposta**: upload de N PDFs → extração (texto + IA) → **revisão
editável** (uma coluna por seguradora, header na cor da marca) → **exportar PDF**.

## Arquitetura (2 fases)
- **Dev (edição ao vivo):** `server.py` (stdlib `http.server`, fora do repo) serve a
  SPA e implementa a API em Python. Espelha exatamente os endpoints que o plugin
  implementará em PHP.
- **Produção:** plugin WordPress instalável (`.zip`). Mesma UI (assets compartilhados
  em `orcamentos-newa/assets/`). Extração de texto via biblioteca PHP (ex.:
  `smalot/pdfparser`) + chamada à OpenAI; login via usuários nativos do WordPress;
  exportação de PDF no cliente (jsPDF + html2canvas, já vendorizados).

### Contrato de API (dev e plugin)
```
POST /api/login {username,password}      -> {user}  (+cookie de sessão)
POST /api/logout
GET  /api/me                              -> {user} | 401
GET/POST /api/config                      -> integração IA + dados da corretora (admin p/ POST)
GET/POST /api/insurers                    -> registro de seguradoras (admin p/ POST)
GET  /api/users                           -> lista (admin)
POST /api/users / PUT|DELETE /api/users/<u>  (admin)
POST /api/extract  (multipart PDF)        -> {fields, missing, insurer_id}
```

## Extração / normalização
1. Texto nativo extraído do PDF (todos os 15 modelos de input são texto nativo — sem OCR).
2. OpenAI (`gpt-4o`, `response_format` = JSON Schema estrito) mapeia o texto para o
   schema fixo e lista `campos_nao_encontrados`. Temperatura 0. Nunca inventa valores.
3. Seguradora detectada por palavras-chave no conteúdo (+ nome do arquivo).
4. **Fallback previsto:** se o PDF não tiver texto (escaneado), enviar as páginas
   como imagem para o modelo de visão. (Ainda não implementado — hoje falha com aviso.)

### Schema normalizado
- **Informações (compartilhadas):** segurado, veiculo, ano_modelo, principal_condutor,
  data_proposta, validade, uso_veiculo, valor_fipe, condutores_18_26, cep_circulacao.
- **Coberturas (por coluna):** colisao_incendio_roubo, rcf_danos_materiais,
  rcf_danos_pessoais, acidente_pessoal_passageiro, morte_pessoal_passageiro,
  km_reboque, diarias_carro_reserva.
- **Franquias e Assistências (por coluna):** franquia_veiculo, para_brisas, farois,
  lanternas, retrovisores, reparo_para_choque, reparo_amassados,
  protecao_pneu_roda_suspensao, assistencia_residencial.
- **Formas de Pagamento (por coluna):** a_vista, parc_4x, parc_6x, parc_10x.
- **Observações:** 5 bullets padrão (editáveis).

## Garantia "nunca entregar incompleto"
Na revisão, todo campo obrigatório vazio vira uma cápsula vermelha e o botão
**Exportar PDF** fica desabilitado enquanto houver pendências. Há atalho para
preencher vazios com "Não Contratado". A seguradora de cada coluna é confirmável
pelo usuário (clique no header), evitando cor/marca errada.

## Autenticação
- **Dev:** store local (`.devdata/users.json`), senha com PBKDF2; sessão por cookie.
- **Produção:** usuários **nativos do WordPress**. O perfil "administrador" do app
  mapeia para uma capability do WP; a seção **Usuários** encapsula
  `wp_create_user`/atualização de role. Primeira conta: `Madu` / `123`.

## Estética
Verde-floresta NEWA (`#12703A`/`#186018`) + acento gradiente
(magenta→laranja→amarelo→verde). Tipografia Poppins/Inter. Princípios de
`make-interfaces-feel-better`: raios concêntricos, sombras em camadas, `tabular-nums`
nos valores, `scale(.96)` no toque, animações escalonadas, hit-areas ≥ 40px.

## Decisões e Assumptions (revisar)
1. **Marca do output = NEWA** (confirmado). O modelo "Fred Seguros" foi usado só como
   estrutura. Logo NEWA reconstruído em SVG; **substituível** pelo logo oficial.
2. **Capa + comparativo** (2 páginas, confirmado).
3. **Seguradora vem do conteúdo do PDF, não do nome do arquivo** — os PDFs-modelo são
   exports do sistema Newa e às vezes nomeiam "Allianz" no conteúdo. Por isso a coluna
   tem seletor de seguradora editável.
4. **Cores de marca das seguradoras são aproximadas** e **editáveis** em *Modelos de
   Entrada*. Devem ser calibradas com as marcas oficiais.
5. **valor_fipe, APP, morte por passageiro e "condutores 18–26"** frequentemente não
   constam nos PDFs das seguradoras — são preenchidos/confirmados pelo corretor na
   revisão (a validação bloqueia o export se ficarem vazios).
6. **Exportação de PDF é rasterizada** (html2canvas → jsPDF) para garantir fidelidade
   visual idêntica em dev e no plugin. Texto não é selecionável no PDF final.
7. **Dados de contato da corretora** (endereço, WhatsApp, telefone) usam valores dos
   PDFs/placeholder e são editáveis em *Configurações*.
8. **Capa sem foto** (o modelo Fred tinha uma foto). Usa watermark da marca; pode
   receber uma foto/hero oficial da NEWA depois.

## Pendências / roadmap
- [ ] Portar a lógica de extração e a API para o plugin PHP (`includes/`), com login
      via usuários do WordPress e persistência em `wp_options`.
- [ ] Empacotador `.zip` do plugin.
- [ ] Fallback de visão para PDFs escaneados.
- [ ] Calibrar cores/logos oficiais das seguradoras.
- [ ] (Opcional) hero/foto oficial na capa; upload de logo por seguradora.
