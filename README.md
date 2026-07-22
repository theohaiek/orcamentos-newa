# Orçamentos NEWA

Aplicativo para **gerar propostas comparativas de seguro auto** a partir dos PDFs de
cotação de várias seguradoras. Você envia os PDFs, o app reconhece e normaliza os
campos automaticamente (extração de texto + IA), você revisa e exporta uma
**Proposta de Seguro** de 2 páginas (capa personalizada + comparativo lado a lado),
pronta para enviar ao cliente.

Distribuído como **plugin do WordPress** e também executável localmente para
desenvolvimento/edição ao vivo do visual.

---

## Principais recursos

- **Reconhecimento automático de PDFs** de qualquer seguradora (layout livre), com
  extração de texto nativa + normalização por IA (OpenAI) e detecção da seguradora.
- **Comparativo lado a lado** com o cabeçalho de cada coluna na **cor da marca** da
  seguradora correspondente (editável).
- **Revisão editável in-place** antes de exportar. Campos vazios ficam destacados em
  vermelho e **bloqueiam a exportação** — nunca gera um PDF incompleto ou incorreto.
- **Exportação em PDF** (capa + comparativo) com um clique.
- **Login** com usuários próprios do sistema; administradores criam/editam usuários
  pela seção **Usuários**. Primeira conta: `Madu` / `123`.
- **Modelos de Entrada**: registro das seguradoras aceitas (nome, cor da marca,
  palavras-chave de reconhecimento) — adicione novas pela UI.
- Estética **NEWA**: verde-floresta + acento gradiente.

---

## Estrutura do repositório

```
app-orçamentos-newa/
├── data/
│   └── insurers.json          # registro-semente de seguradoras (cores/keywords)
├── docs/
│   └── spec.md                # especificação, decisões e assumptions
├── orcamentos-newa/           # === o plugin WordPress (pasta que vira o .zip) ===
│   ├── orcamentos-newa.php     # (em construção) bootstrap do plugin + shortcode
│   ├── includes/               # (em construção) auth, extração, REST, registro
│   ├── templates/              # (em construção) shell da SPA para o shortcode
│   └── assets/
│       ├── app.css             # design system da UI
│       ├── proposal.css        # layout do documento exportável
│       ├── app.js              # SPA (login, upload, revisão, export, admin)
│       └── vendor/             # jsPDF + html2canvas (self-contained)
└── README.md
```

> O servidor de desenvolvimento (`server.py`) e o shell (`index.html`) ficam **fora**
> deste repositório (na pasta-pai), pois são apenas ferramentas de edição ao vivo.

---

## Desenvolvimento local (edição ao vivo)

Pré-requisito: **Python 3.8+** com `pymupdf` e `openai`
(`pip install pymupdf openai`).

1. Na pasta-pai (que contém `server.py`), crie um `.env` com sua `OPENAI_API_KEY`
   (ou configure depois pela UI em *Configurações*).
2. Rode:

   ```
   python server.py
   ```

3. Abre sozinho em `http://localhost:8080/` — entre com **Madu / 123**.

Edite os arquivos em `orcamentos-newa/assets/` e recarregue a página (F5) para ver as
mudanças. O servidor serve os assets sem cache.

---

## Como funciona a extração

1. O texto nativo do PDF é extraído (PyMuPDF).
2. O texto é enviado a um modelo da OpenAI com um **schema estrito** (JSON Schema),
   que devolve os campos normalizados e a lista de campos não encontrados.
3. A seguradora é detectada pelo conteúdo (e nome do arquivo) e define a cor da coluna.
4. Na revisão, campos ausentes ficam vermelhos e travam a exportação até serem
   preenchidos ou marcados como *Não Contratado*.

Se um PDF não tiver texto (escaneado), a extração falha com aviso claro — o fallback
por visão da IA está previsto na especificação.

---

## Deploy como plugin WordPress

O empacotamento em `.zip` e a instalação via *WP Admin → Plugins → Adicionar novo →
Enviar plugin* estão descritos em [`docs/spec.md`](docs/spec.md). O login usa o
sistema de usuários do próprio WordPress.
