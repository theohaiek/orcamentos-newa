# Orçamentos NEWA · v1.0

Aplicativo para **gerar propostas comparativas de seguro auto** a partir dos PDFs de
cotação de várias seguradoras. Você envia os PDFs, o app reconhece e normaliza os
campos automaticamente, confere **de onde veio cada dado** e exporta uma
**Proposta de Seguro** (capa personalizada + comparativo lado a lado), pronta para
enviar ao cliente.

---

## Instalar (Windows)

Baixe **[`Instalar Orcamentos NEWA.exe`](Instalar%20Orcamentos%20NEWA.exe)** aqui de
cima e execute. Instala na pasta do usuário, **sem pedir senha de administrador**, e
cria atalho na Área de Trabalho e no Menu Iniciar.

Na primeira execução o Windows mostra *"O Windows protegeu seu computador"* — é o aviso
padrão para programa sem certificado de assinatura. Clique em **Mais informações** e
**Executar assim mesmo**.

O instalador funciona de três formas, e descobre sozinho em qual está:

| você tem | o que ele faz |
|---|---|
| só o instalador | baixa o programa e o código deste repositório |
| o `.zip` deste repositório extraído, ou um `git clone` | usa os arquivos do disco, sem baixar nada |
| já instalado | atualiza só o que mudou; usuários, configuração e propostas ficam intactos |

Para remover: `Desinstalar.bat`, dentro de `%LOCALAPPDATA%\OrcamentosNEWA`. Seus dados
não são apagados.

### O programa se mantém atualizado sozinho

O executável carrega o Python e as bibliotecas — que mudam raramente. **O motor, a
interface e os perfis das seguradoras ficam numa pasta `repo`, sincronizada com este
repositório**, e é ela que o programa executa. Uma correção publicada aqui chega a
quem usa **no próximo login**, sem reinstalar nada.

A verificação acontece ao abrir o programa e a cada login — então sair e entrar de novo
serve de "procurar atualizações". Sem internet, o programa abre normalmente com o que
já tem em disco.

```
%LOCALAPPDATA%\OrcamentosNEWA\
├─ app\      o programa (Python embutido; só muda em versão nova)
├─ repo\     motor, interface e perfis — é o que se mantém em dia
└─ …         seus usuários, configuração e propostas
```

Se uma sincronização deixar a pasta `repo` num estado que não roda, o programa **não
deixa de abrir**: percebe a falha, tenta sincronizar de novo e, se ainda assim não
subir, usa a cópia que veio no instalador. Publicar código quebrado atrasa a correção;
não deve trancar ninguém para fora do próprio trabalho.

### Quem entra no programa

Por padrão o login é conferido na própria máquina, pelo arquivo de usuários — é o modo
de desenvolvimento. Preenchendo o **endereço de validação** em *Configurações →
Controle de acesso*, quem decide passa a ser o servidor (um webhook), e o arquivo local
deixa de valer: criar usuário na tela de *Usuários* não abre mais porta nenhuma.

Só libera com `200` + JSON + `ok: true`; qualquer outra coisa nega. Falha de rede e erro
5xx são tratados como indisponibilidade, não como negativa — aí vale o **último acesso
confirmado**, que tem prazo definido pelo servidor e exige a mesma senha. Cortar alguém
no servidor tira o acesso em, no máximo, esse prazo. O contrato completo está no
cabeçalho de [`auth.py`](auth.py).

---

Para desenvolvimento e edição ao vivo do visual, veja
[Desenvolvimento local](#desenvolvimento-local-edição-ao-vivo).

> **Status: v1.0** — app desktop empacotado, instalável e se atualizando sozinho.
> **80% dos campos** saem da extração determinística (auditável, sem IA) nas 15
> seguradoras de amostra. O que ainda **não** é verdade está em [`TODO.md`](TODO.md)
> e em [Distribuição](#distribuição--decidido-app-desktop-windows) — leia antes de
> distribuir para alguém.

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
- **Cotação com vários planos lado a lado** (a Allianz cota 3, a HDI 2) é detectada, e
  o assistente traz um **seletor de plano** no cabeçalho. Escolher troca os campos que
  o servidor conseguiu separar por coluna com duas regras independentes concordando;
  os demais ficam como estavam. Em qualquer caso os campos seguem exigindo confirmação
  — a escolha nunca deixa a extração pior do que ela já era.
- **Editor de modelo:** edite o layout do documento gerado (seções, campos, textos,
  ordem) com pré-visualização em placeholders.
- **Exportação em PDF** (capa + comparativo) com um clique, salva em
  `Documentos\Propostas NEWA` — **pelo servidor, não pelo download do navegador**, e
  nunca sobrescrevendo uma proposta anterior. A tela só anuncia sucesso depois que o
  arquivo existe em disco com o tamanho certo: numa corretora, achar que mandou a
  proposta e não ter mandado é o pior modo de falha possível.
- **Login** conferido na própria máquina por padrão (primeira conta: `Madu` / `123`),
  ou **validado num servidor** quando o endereço é preenchido em *Configurações* — aí
  o arquivo local de usuários deixa de valer e o acesso se corta de um lugar só.
- **Modelos de Entrada:** registro das seguradoras (nome, cor, logos, palavras-chave).
- Estética **NEWA**: verde-floresta + acento gradiente.

---

## Estrutura do repositório

```
app-orçamentos-newa/
├── Instalar Orcamentos NEWA.exe  # o que a pessoa baixa (vive aqui para ficar em dia)
│
│   ── o programa ─────────────────────────────────────────────────────────────
├── app.py                      # casca desktop: janela nativa, porta livre, DPI
├── server.py                   # servidor e API (http.server, sem framework)
├── extract_engine.py           # motor de extração por âncora
├── auth.py                     # quem entra: validação no n8n + crachá offline
├── updater.py                  # atualização de perfis e do programa inteiro
├── index.html                  # casca da SPA
│
│   ── empacotamento ──────────────────────────────────────────────────────────
├── build.py                    # gera o executável e o instalador (PyInstaller)
├── instalador.py               # instala, cria atalhos, resolve o WebView2
│
├── data/
│   ├── insurers.json           # registro de seguradoras (cores, logos, keywords)
│   ├── sincronizar.json        # que arquivos formam o programa na máquina do usuário
│   └── profiles/               # perfis de extração determinística por layout
│       ├── aliro.json  allianz.json  azul.json  bradesco.json  darwin.json
│       ├── hdi.json    itau.json     justos.json  mapfre.json  mitsui.json
│       ├── porto.json  suhai.json    tokio.json   yelum.json   zurich.json
│       ├── tradicional.json    # família: sistema Porto/Itaú/Azul/Mitsui
│       ├── autoperfil.json     # família: sistema Aliro/Yelum/HDI
│       └── _generic.json       # dicionário de rótulos (roda em qualquer layout)
├── docs/
│   ├── spec.md                 # especificação, arquitetura e decisões
│   ├── perfis.md               # como autorar o perfil de uma seguradora nova
│   ├── avaliacao-mineru.md     # MinerU x PyMuPDF: medição e decisão
│   └── avaliacao-smalot.md     # o port PHP que foi medido e descartado
├── orcamentos-newa/            # a interface (assets servidos ao navegador)
│   └── assets/
│       ├── app.css             # design system da UI
│       ├── proposal.css        # layout do documento exportável
│       ├── app.js              # SPA (login, upload, extração, conferência, export, admin)
│       ├── logo-newa.png, logos/  # logo NEWA + logos das seguradoras
│       └── vendor/             # jsPDF + html2canvas (self-contained)
├── tests/                      # 11 arquivos; nenhum chama a OpenAI nem usa rede
├── README.md
└── TODO.md
```

`data/sincronizar.json` é a lista do que vai para a máquina de quem usa. Ela existe
como **dado, não como constante no código**: o atualizador lê essa lista de dentro do
pacote que acabou de baixar, então uma versão que acrescenta um arquivo consegue
descrevê-lo mesmo rodando sob um atualizador antigo. Sem isso, um arquivo novo
referenciado por outro chega pela metade — e foi exatamente o que quebrou uma
instalação em 28/07.

> **A chave da OpenAI não mora em lugar nenhum deste repositório**, e nem na máquina de
> quem desenvolve: não há `.env`, não há variável de ambiente, não há padrão embutido.
> Ela é digitada em *Configurações* na máquina de quem usa e fica em `config.json`, fora
> do repositório. A cota é da conta do cliente, e não há chave a vazar daqui.
>
> Não é zelo abstrato: a chave anterior **vazou**, servida por `/assets/../../../.env`
> numa época em que essa rota respondia antes do login. O buraco do caminho foi fechado
> e tem teste, mas enquanto houvesse chave em disco fora do controle de quem usa, um
> erro parecido exporia a chave de outra pessoa.

---

## Desenvolvimento local (edição ao vivo)

Pré-requisito: **Python 3.8+** com `pymupdf` e `openai` (`pip install pymupdf openai`).

1. Rode:

   ```
   python server.py
   ```

2. Abre sozinho em `http://localhost:8080/` — entre com **Madu / 123**.

3. A chave da OpenAI, se quiser exercitar a camada de IA, vai em *Configurações* — é a
   única fonte, aqui como na máquina de quem usa. Sem ela, o determinístico roda normal
   e entrega os ~80%; só o *fallback* de IA fica desligado.

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
   Modelo padrão: **`gpt-4o-mini`** — 69,4% de cobertura correta contra 44% do
   `gpt-5-nano`, que ocupava esse lugar por uma medição que só olhava os campos
   preenchidos. O modelo é editável em *Configurações*.

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

**11 arquivos de teste. Nenhum chama a OpenAI e nenhum usa rede real** — os serviços
externos são substituídos por servidores locais de mentira, então a suíte roda de graça,
offline e em segundos.

| teste | o que protege |
|---|---|
| `test_traversal.py` | contenção de caminho nas rotas servidas antes do login |
| `test_cobertura.py` | não-regressão da cobertura determinística (piso: 24/31) |
| `test_multioferta.py` | detecção de cotação com vários planos lado a lado |
| `test_verificacao_ia.py` | rejeição de valor inventado pela IA (injeção: 0 de 89 passa) |
| `test_validacao_pdf.py` | avisos da pipeline: página sem texto, falha da IA, drift |
| `test_config.py` | configuração sobrevive a BOM; migração não apaga o que não leu |
| `test_auth.py` | login no servidor, falha fechado, crachá offline com prazo |
| `test_updater.py` | atualização de perfis: hash, travessia, cache, versão |
| `test_sincronizacao.py` | atualização do programa; recuo quando o repo quebra |
| `test_export.py` | gravação do PDF, e recusa que chega como resposta e não como queda |
| `test_pendencias.js` | assistente de conferência e montagem do PDF (roda no Node) |

Sem o Node instalado, o teste de interface é marcado **PULADO** de forma visível — para
ninguém ler a suíte verde como cobertura completa.

PDFs escaneados (sem camada de texto) ainda não são suportados — o MinerU foi avaliado e
é a recomendação para esse caso: ver [`docs/avaliacao-mineru.md`](docs/avaliacao-mineru.md).

---

## Distribuição — decidido: app desktop Windows

O WordPress ficou de fora. O motor continua em Python sem reescrita, o app é um
executável Windows com janela própria, e o servidor externo (n8n) entra **só para
validar acesso** — nunca para processar PDF.

A via descartada foi medida antes de descartar: o motor **porta** para PHP
(`smalot/pdfparser`, sem binário externo, roda em hospedagem compartilhada) entregando
23,3 de 31 campos contra 25,1 do PyMuPDF — 93%. O que pesou contra não foi a cobertura,
foram **duas implementações do mesmo motor para manter em paridade**. Números em
[`docs/avaliacao-smalot.md`](docs/avaliacao-smalot.md); desenho do desktop em
[`docs/superpowers/specs/2026-07-25-app-desktop-design.md`](docs/superpowers/specs/2026-07-25-app-desktop-design.md).

**macOS está fora do escopo** até haver um Mac para testar — há três incógnitas reais
(exportação do PDF, persistência do cookie em `127.0.0.1` no WKWebView, e a tabela do
comparativo, que usa `var()` dentro de `repeat()` no grid), e prometer sem testar seria
inventar. Windows 32 bits também não roda: o build é x64.

### O que ainda não é verdade

Vale ler antes de distribuir para alguém:

- **O texto integral do PDF vai para a OpenAI** — nome, CPF, CEP, placa, chassi —
  quando a camada de IA é acionada. A spec do app desktop afirma o contrário. Ou o
  código muda, ou a spec está mentindo; está em decisão (ver [`TODO.md`](TODO.md)).
  Sem chave configurada, a camada de IA não roda e nada sai da máquina.
- **A senha padrão ainda vale.** A validação no servidor está implementada e testada,
  mas publicada desligada, porque o fluxo do lado do n8n ainda não existe. Até ligar,
  quem tem o app instalado entra com `Madu`/`123`.
- **O instalador nunca rodou em outra máquina.** Em particular, o trecho que instala o
  WebView2 sozinho nunca foi exercitado: a máquina de desenvolvimento já tem o
  componente. É código escrito e não testado.
- **Não há assinatura de código**, por decisão: a Microsoft declara que o certificado EV
  não evita mais o SmartScreen e a reputação zera a cada versão. O aviso da primeira
  execução é aceito conscientemente — mas num Windows 11 com *Smart App Control* ligado
  o binário pode ser **bloqueado**, não só avisado.
