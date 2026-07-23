# Orçamentos NEWA · v0.2

Aplicativo para **gerar propostas comparativas de seguro auto** a partir dos PDFs de
cotação de várias seguradoras. Você envia os PDFs, o app reconhece e normaliza os
campos automaticamente, confere **de onde veio cada dado** e exporta uma
**Proposta de Seguro** de 2 páginas (capa personalizada + comparativo lado a lado),
pronta para enviar ao cliente.

Distribuído como **plugin do WordPress** e também executável localmente para
desenvolvimento/edição ao vivo do visual.

> **Status:** v0.2 — funcional ponta a ponta em desenvolvimento local (servidor Python
> de live-edit). Portabilidade para o plugin WordPress e mais perfis de seguradora estão
> no [`TODO.md`](TODO.md).

---

## Principais recursos

- **Extração híbrida (determinística + IA):** um **perfil por layout** extrai os campos
  por posição/rótulo (rápido, gratuito, auditável); a **IA (OpenAI)** entra apenas como
  *fallback* para o que o perfil não resolver, com o valor **verificado no texto do PDF**.
- **Proveniência de cada dado:** todo campo carrega sua origem (página, posição, trecho,
  rótulo-âncora). Na revisão, um ponto colorido indica o método (Perfil / IA verificada /
  Confirmar).
- **Assistente de conferência por etapas** (abre automaticamente antes de gerar): mostra,
  seção por seção, o **resultado final no centro** e os **PDFs de origem de cada lado**,
  com a região de cada valor **marcada em marca-texto** (modo *Destaque na página*, com
  **lupa** ao passar o mouse) ou **recortada** da imagem real (modo *Recortes*, recorte
  gerado no servidor). Tudo **editável** ali mesmo; campos pendentes destacados e o botão
  *Preencher vazios* resolve todos de uma vez.
- **Banner de comparação:** o documento final abre indicando **quais seguradoras** estão
  sendo comparadas (logo + nome de cada uma).
- **Painel "Deixado de fora":** valores em R$ presentes no PDF que nenhum campo capturou,
  promovíveis a um campo.
- **Comparativo lado a lado** com o cabeçalho de cada coluna na cor/logo da marca da
  seguradora (editável).
- **Nunca gera incompleto:** campos obrigatórios vazios bloqueiam a geração e são
  destacados; erros de extração aparecem com o motivo.
- **Editor de modelo:** edite o layout do documento gerado (seções, campos, textos,
  ordem) com pré-visualização em placeholders.
- **Exportação em PDF** (capa + comparativo) com um clique.
- **Login** com usuários próprios; administradores gerenciam contas em **Usuários**.
  Primeira conta: `Madu` / `123`.
- **Modelos de Entrada:** registro das seguradoras (nome, cor, logos, palavras-chave).
- Estética **NEWA**: verde-floresta + acento gradiente.

---

## Estrutura do repositório

```
app-orçamentos-newa/
├── data/
│   ├── insurers.json           # registro de seguradoras (cores, logos, keywords)
│   └── profiles/               # perfis de extração determinística por layout
│       ├── tradicional.json    # Porto / Itaú / Azul / Mitsui
│       ├── autoperfil.json     # Aliro / Yelum
│       ├── suhai.json
│       └── _generic.json       # campos de rótulo inequívoco (qualquer layout)
├── docs/
│   └── spec.md                 # especificação, arquitetura e decisões
├── orcamentos-newa/            # === o plugin WordPress (pasta que vira o .zip) ===
│   └── assets/
│       ├── app.css             # design system da UI
│       ├── proposal.css        # layout do documento exportável
│       ├── app.js              # SPA (login, upload, extração, conferência, export, admin)
│       ├── logo-newa.png, logos/  # logo NEWA + logos das seguradoras
│       └── vendor/             # jsPDF + html2canvas (self-contained)
├── README.md
└── TODO.md
```

> O servidor de desenvolvimento (`server.py`, `extract_engine.py`) e o shell
> (`index.html`) ficam **fora** deste repositório (na pasta-pai) — são ferramentas de
> edição ao vivo e trazem a chave de API em `.env` (nunca versionada).

---

## Desenvolvimento local (edição ao vivo)

Pré-requisito: **Python 3.8+** com `pymupdf` e `openai` (`pip install pymupdf openai`).

1. Na pasta-pai (que contém `server.py`), crie um `.env` a partir de
   [`.env.example`](.env.example) com sua `OPENAI_API_KEY` (ou configure depois pela UI
   em *Configurações*).
2. Rode:

   ```
   python server.py
   ```

3. Abre sozinho em `http://localhost:8080/` — entre com **Madu / 123**.

Edite os arquivos em `orcamentos-newa/assets/` e recarregue a página (F5) — o servidor
injeta *cache-busting*, então um F5 normal já pega a versão nova.

---

## Como funciona a extração (pipeline em camadas)

1. **Tokenização posicional** (PyMuPDF): cada palavra do PDF com sua página e posição.
2. **Camada 1 — perfil determinístico** (`data/profiles/*.json`): âncora por rótulo +
   captura posicional (`right`/`below`/`table_cell`/`text_regex`) + validação por regex.
   Gera a proveniência exata. Perfis por família de layout: `tradicional`
   (Porto/Itaú/Azul/Mitsui), `autoperfil` (Aliro/Yelum), `suhai`.
3. **Camada 1b — genérico** (`_generic.json`): preenche campos de **rótulo inequívoco**
   (RCF, CEP, vidros, faróis, lanternas, retrovisores, reboque, carro reserva) em
   **qualquer** layout, com guardas contra valor errado.
4. **Camada 2 — validação/drift:** campo sem âncora/regex cai para a IA; muitos campos
   falhando sinalizam "layout pode ter mudado".
5. **Camada 3 — IA (fallback):** só para os campos restantes (schema reduzido → rápido);
   o valor é localizado no texto do PDF (string-match). Sem match → confiança baixa e o
   campo fica pendente. Modelo padrão: **`gpt-5-mini`** (`reasoning_effort=minimal`).

PDFs escaneados (sem texto) ainda não são suportados — fallback de visão previsto no
[`TODO.md`](TODO.md).

---

## Deploy como plugin WordPress

O empacotamento em `.zip` e a instalação via *WP Admin → Plugins → Adicionar novo →
Enviar plugin* estão descritos em [`docs/spec.md`](docs/spec.md). O login usará o
sistema de usuários do próprio WordPress. (Em desenvolvimento — ver `TODO.md`.)
