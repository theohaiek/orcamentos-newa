# Orçamentos NEWA · v0.3

Aplicativo para **gerar propostas comparativas de seguro auto** a partir dos PDFs de
cotação de várias seguradoras. Você envia os PDFs, o app reconhece e normaliza os
campos automaticamente, confere **de onde veio cada dado** e exporta uma
**Proposta de Seguro** de 2 páginas (capa personalizada + comparativo lado a lado),
pronta para enviar ao cliente.

Hoje roda localmente para desenvolvimento/edição ao vivo do visual. A forma de
distribuição — **plugin WordPress** ou **aplicativo desktop instalável** — está em
aberto; as duas são tecnicamente viáveis.

> **Sobre a distribuição (2026-07-26):** uma medição anterior concluiu que o motor não
> poderia ser portado para PHP e descartou o WordPress. **Aquela medição estava errada**
> — o defeito era do script de teste, não da biblioteca. Refeita: o motor roda em PHP
> com **93% da cobertura** que tem em Python, com os perfis intocados. Números e o custo
> real do port em [`docs/avaliacao-smalot.md`](docs/avaliacao-smalot.md). O desenho do
> app desktop continua válido como alternativa:
> [`docs/superpowers/specs/2026-07-25-app-desktop-design.md`](docs/superpowers/specs/2026-07-25-app-desktop-design.md).

> **Status:** v0.3 — funcional ponta a ponta em desenvolvimento local (servidor Python
> de live-edit). **80% dos campos** saem da extração determinística (auditável, sem IA)
> nas 15 seguradoras de amostra. O empacotamento como app desktop está no
> [`TODO.md`](TODO.md).

---

## Principais recursos

- **Extração híbrida (determinística + IA):** um **perfil por layout** extrai os campos
  por posição/rótulo (rápido, gratuito, auditável); a **IA (OpenAI)** entra apenas como
  *fallback* para o que o perfil não resolver, com o valor **verificado no texto do PDF**.
- **Proveniência de cada dado:** todo campo carrega sua origem (página, posição, trecho,
  rótulo-âncora). Na revisão, um ponto colorido indica o método (Perfil / IA verificada /
  Não consta no PDF / Confirmar).
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
│       ├── aliro.json  allianz.json  azul.json  bradesco.json  darwin.json
│       ├── hdi.json    itau.json     justos.json  mapfre.json  mitsui.json
│       ├── porto.json  suhai.json    tokio.json   yelum.json   zurich.json
│       ├── tradicional.json    # família: sistema Porto/Itaú/Azul/Mitsui
│       ├── autoperfil.json     # família: sistema Aliro/Yelum/HDI
│       └── _generic.json       # dicionário de rótulos (roda em qualquer layout)
├── docs/
│   ├── spec.md                 # especificação, arquitetura e decisões
│   └── avaliacao-mineru.md     # MinerU x PyMuPDF: medição e decisão
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

1. **Tokenização posicional** (PyMuPDF), em três níveis. O nível que importa são os
   **segmentos** — tokens agrupados pelo *bloco/linha do próprio PDF*, que é o que separa
   `Veículo:` de `Valor de Mercado Referenciado` e de `Dias Paralisação:` numa mesma linha
   visual de formulário multi-coluna. Ler "o valor à direita do rótulo" pela linha visual
   invadia a coluna vizinha — era a causa raiz da baixa cobertura e dos valores errados.
2. **Camada 1 — perfil determinístico** (`data/profiles/*.json`): âncora por rótulo +
   captura posicional (`kv`/`row`/`under`/`right`/`below`/`table_cell`/`text_regex`),
   recorte por **seção**, **guardas** (`min_value`, `not_regex`, `reject`) e
   **normalização** (moeda BR, data ISO, CEP, Sim/Não). Um campo pode ter várias specs
   alternativas. Gera a proveniência exata. **Um perfil dedicado por seguradora**
   (15 autorados) e perfis de família para layouts do mesmo emissor.
3. **Camada 1b — genérico** (`_generic.json`): dicionário de rótulos que roda em
   **qualquer** layout, só para os campos que sobraram — é o que dá cobertura numa
   seguradora ainda sem perfil próprio. Ele é **derivado dos perfis dedicados** e passa
   por dois filtros: um teste *leave-one-out* (a regra é validada num layout que ela
   nunca viu) e um portão que descarta qualquer regra cujo valor divirja do perfil
   dedicado. Campos que erram em layout novo **ficam de fora** e vão para a IA — é
   preferível um campo âmbar revisado a um campo verde errado.
4. **Camada 2 — validação:** documento é conferido **página a página** (página sem texto
   é sinalizada, não ignorada), cotações **multi-oferta** são detectadas, e falha da IA
   vira aviso explícito — nunca campo vazio silencioso.
5. **Camada 3 — IA (fallback):** só para os campos restantes (schema reduzido → rápido).
   O valor devolvido só é aceito como **verificado** quando é encontrado no PDF **junto
   a um rótulo daquele campo** — encontrar a string em qualquer lugar do documento não
   é verificação. Sem isso, o campo vai para conferência. Coberturas que o documento não
   menciona viram "Não consta no PDF" (cinza) — e só depois de conferir que nenhum
   rótulo do campo aparece no documento.
   Modelo padrão: **`gpt-5-nano`**, com esforço de raciocínio ajustável em *Configurações*.

### Cobertura medida (15 PDFs de amostra, 31 campos)

| | determinístico | IA verificada / não consta | a confirmar | vazio |
|---|---|---|---|---|
| antes (v0.2) | 33% | 65% | | |
| **agora** | **81%** | 6% | 4% | 9% |

Sob critério de plausibilidade por tipo de campo (moeda tem que parecer moeda, data tem
que parecer data), o determinístico fica em **24,9/31 = 80%**. É o número que o
[`tests/test_cobertura.py`](tests/) protege contra regressão.

> A faixa "a confirmar" era 0% e passou a 4% porque a verificação da IA deixou de ser
> um `contém` no documento inteiro. Os 11% de "IA verificada" da medição anterior
> incluíam valores que o sistema não tinha como confirmar — hoje eles aparecem como o
> que são.

**Seguradora ainda sem perfil próprio:** medido em *leave-one-out* (cada layout avaliado
por um dicionário genérico construído sem ele), a camada genérica sozinha entrega ~6,7 de
31 campos, com **86% de precisão** — ou seja, ela erra. Para uma seguradora nova, o
caminho é **autorar o perfil dela**, descrito em [`docs/perfis.md`](docs/perfis.md).

> Ressalva de método, para não repetir a afirmação errada anterior: os campos
> considerados "seguros" para a camada genérica foram escolhidos olhando o resultado de
> todas as dobras do leave-one-out, o que torna o "zero erro" circular. Refeita a
> seleção de forma aninhada, aparecem 3 erros. Além disso, 41% das regras embarcadas
> vieram de uma fonte autorada com acesso aos 15 layouts e **nunca** passaram pelo
> leave-one-out. Trate ~6,7/31 como um teto otimista.

### Testes

```
python tests/run_all.py
```

Cinco testes, nenhum deles chama a OpenAI: contenção de caminho nas rotas públicas,
não-regressão da cobertura determinística, detecção de multi-oferta, rejeição de valor
inventado pela IA e os avisos da pipeline de validação.

PDFs escaneados (sem camada de texto) ainda não são suportados — o MinerU foi avaliado e
é a recomendação para esse caso: ver [`docs/avaliacao-mineru.md`](docs/avaliacao-mineru.md).

---

## Distribuição — decisão em aberto

Duas vias, ambas medidas e viáveis:

**Plugin WordPress.** O motor porta para PHP (`smalot/pdfparser`, sem binário externo,
roda em hospedagem compartilhada) entregando **23,3 de 31 campos** contra 25,1 do
PyMuPDF — 93%. Custo: 3 valores divergentes em 350 que precisam de correção nos perfis
antes de produção, e duas implementações do mesmo motor para manter. Medição em
[`docs/avaliacao-smalot.md`](docs/avaliacao-smalot.md).

**App desktop (Windows/macOS).** Mantém o motor em Python sem reescrita nenhuma; janela
nativa, extração inteira na máquina. Exige um backend mínimo (whitelist, ponte para a
OpenAI, versão vigente) e um instalador por sistema. Desenho em
[`docs/superpowers/specs/2026-07-25-app-desktop-design.md`](docs/superpowers/specs/2026-07-25-app-desktop-design.md).

Em ambas, perfis novos de seguradora chegam sem reinstalar.

> **Atenção ao que trafega.** Hoje a camada de IA envia o **texto integral** do PDF à
> OpenAI — inclusive nome, CPF e CEP do segurado. Qualquer das duas vias herda isso
> enquanto não houver redação dos dados pessoais antes do envio (ver `TODO.md`).
