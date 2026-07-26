# App desktop (Windows + macOS) com backend n8n — design

Data: 2026-07-25 · Substitui o plano de distribuição como plugin WordPress.

## Por que mudou

> **A premissa deste documento caiu (2026-07-26).** Ele foi escrito partindo de que o
> motor não podia ser portado para PHP. Aquela medição estava errada — o defeito era do
> script de teste, não da biblioteca. Refeita: o motor roda em PHP entregando **93% da
> cobertura**, com os perfis intocados. Ver [`avaliacao-smalot.md`](../../avaliacao-smalot.md).
>
> O desenho abaixo continua válido como **uma** das opções de distribuição, e a
> arquitetura (acesso revogável, chave fora do executável, atualização de perfis a
> quente) segue desejável. O que não vale mais é o argumento de que ela era a única
> saída técnica. A escolha entre plugin WordPress e app desktop voltou a ser uma
> decisão de produto.

O produto seria um plugin WordPress, o que obrigava a reescrever o motor de extração
em PHP — trabalho real, mas viável. A alternativa aqui desenhada mantém o motor em
Python e muda o invólucro: de plugin WordPress para **aplicativo desktop instalável**,
com um backend mínimo em n8n para acesso e chave de API.

## Objetivo

Um aplicativo que a equipe instala e usa como qualquer outro programa: ícone próprio,
janela própria, sem navegador à vista. A extração continua local e instantânea. O
acesso é controlado centralmente e pode ser cortado a qualquer momento. A chave da
OpenAI nunca sai do servidor.

## Arquitetura

Três lugares, e só três.

```
MÁQUINA DO USUÁRIO              VPS (n8n)                   GITHUB
┌──────────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│ Orçamentos NEWA      │      │ /auth            │      │ código (privado) │
│  janela nativa       │◄────►│ /ia   (proxy)    │      │ Actions → build  │
│  servidor local      │      │ /versao          │      │ Releases         │
│   └ PyMuPDF + perfis │      │                  │      │  .exe .dmg       │
│  dados locais        │      │ chave OpenAI ────┼──► OpenAI               │
└──────────────────────┘◄────────── atualizações ───────┘                  │
```

### Máquina do usuário

O que hoje é `server.py` + `extract_engine.py`, embrulhado. O servidor HTTP continua
existindo, mas escuta em **porta efêmera em `127.0.0.1`** — não é alcançável pela rede.
A janela é nativa; o usuário não vê navegador nem URL.

Ficam locais: PyMuPDF, os perfis, a interface, os hashes de senha, a configuração e os
PDFs enviados.

> **Correção (2026-07-26).** Este documento afirmava que "nenhum PDF sai da máquina —
> apenas os poucos campos que precisam de IA". **Isso é falso na implementação atual.**
> O parâmetro `only_keys` restringe apenas o *esquema de saída* pedido ao modelo; o que
> é enviado é o **texto integral do documento**, com nome, CPF, CEP, placa e chassi. Só
> os campos que o perfil não resolveu deixam de sair porque não são pedidos — mas o
> texto todo trafega. Enquanto não houver redação dos dados pessoais antes do envio, o
> desenho tem que assumir que o conteúdo do PDF vai para a OpenAI e, no caminho com
> proxy, também para o servidor n8n.

### VPS (n8n)

Três webhooks. Não armazena PDF nem dado de cliente; é porteiro e intermediário.

| Endpoint | Papel |
|---|---|
| `POST /auth` | Recebe um username. Responde se está ativo na whitelist e devolve um token de sessão de curta duração. |
| `POST /ia` | Recebe token + trecho de texto + esquema dos campos pendentes. Valida o token, chama a OpenAI com a credencial armazenada no n8n e devolve o JSON. |
| `GET /versao` | Devolve a versão vigente do app e a versão mínima aceita. |

A whitelist é uma lista de usernames com estado ativo/revogado, editável só pelo dono
do n8n. Usernames são imutáveis.

### GitHub

Código-fonte privado. GitHub Actions constrói os instaladores e publica Releases com
os binários e os arquivos que o app atualiza sozinho.

## Fluxo de uso

1. **Abertura** — o app chama `/auth` com o username. Resposta negativa, versão vencida
   ou ausência de resposta → o app não abre e mostra qual dos três ocorreu.
2. **Senha** — conferida localmente contra o hash guardado na máquina.
3. **Atualização** — perfis e interface novos são baixados e aplicados.
4. **Extração** — os PDFs são processados na máquina. Os ~81% determinísticos saem
   offline e instantâneos.
5. **IA** — só os campos restantes vão a `/ia`.
6. **Conferência, geração e exportação** — tudo local.

## Acesso e revogação

- Whitelist central no n8n; usernames imutáveis, criados só pelo dono.
- Senha inicial `123`, trocável pelo usuário, com hash guardado **na máquina**. O n8n
  autoriza *quem*; a máquina confere *a senha*. Uma pessoa numa máquina nova recomeça
  com a senha padrão.
- Revalidação de hora em hora enquanto o app está aberto.
- **Falha fechado**: sem confirmação do n8n, o app não funciona.

> **Consequência aceita:** o n8n é dependência dura. Se ele cair, ninguém trabalha —
> nem nas extrações que não usam IA. É o preço da revogação forte, escolhido
> deliberadamente. Se um dia o custo operacional pesar, a mitigação é uma tolerância
> de poucos dias usando a última confirmação bem-sucedida.

## Chave de API

O executável **nunca contém a chave**. Ela vive numa credencial do n8n, referenciada
por nome no workflow. Ganhos: chave inextraível do binário, consumo visível por
pessoa, e rotação sem redistribuir o app.

## Atualização automática

Duas velocidades:

- **Perfis e interface** (`data/profiles/*.json`, `assets/app.js`, `assets/app.css`) —
  baixados e aplicados na abertura. Seguradora nova entra em produção sem ninguém
  reinstalar. É o caminho da maior parte da evolução do produto.
- **Motor Python** — exige binário novo. O app avisa, baixa e instala.

`/versao` declara a versão mínima aceita, o que permite **forçar** a atualização:
versões abaixo do mínimo param de autenticar.

## Empacotamento

- **Casca:** `pywebview` — janela nativa usando o motor do sistema (WebView2/Chromium
  no Windows, WKWebView/WebKit no macOS). Escolhido em vez do Electron para manter a
  pilha inteira em Python: um build, um `PyInstaller`, sem Node.
- **Build:** GitHub Actions em matriz `windows-latest` + `macos-latest`, porque
  `PyInstaller` não compila para macOS a partir do Windows e não há Mac disponível
  no ambiente de desenvolvimento.
- **Saída:** `.exe` (Inno Setup) e `.dmg`, publicados como Release a cada tag.
- **Sem assinatura digital**, por decisão de custo. Consequência: aviso do SmartScreen
  na primeira execução no Windows, e abrir pelo botão direito → Abrir na primeira vez
  no macOS. Uma vez por máquina.

### Risco declarado

A exportação do documento final usa `html2canvas` + `jsPDF`. No macOS o motor é WebKit,
não Chromium. Se a exportação divergir ou quebrar lá, a saída é trocar a casca por
Electron, que embute o Chromium — o núcleo não muda em nenhum dos casos. **Isto é o
que o portão de validação abaixo existe para descobrir, antes de qualquer outro
trabalho.**

## Portão de validação (primeiro entregável)

Antes de desenvolver o resto, um protótipo mínimo precisa provar que:

1. A interface atual roda dentro de uma janela `pywebview`, sem navegador.
2. O app aparece na barra de tarefas (Windows) e no Dock (macOS) com ícone e nome próprios.
3. O fluxo completo funciona: login, upload dos PDFs, extração, conferência.
4. **A exportação do PDF final funciona nos dois sistemas.**
5. `PyInstaller` produz um executável que roda numa máquina sem Python instalado.

O item 4 é o que decide entre `pywebview` e Electron. Reprovando, o design muda só na
seção de empacotamento.

## Reorganização do repositório

Hoje o repositório é o plugin WordPress e o motor vive fora dele, por não pertencer ao
plugin. Isso inverte:

- `server.py` e `extract_engine.py` **entram** no repositório — viraram o produto.
- `orcamentos-newa/` deixa de ser "o plugin" e passa a ser a interface do app. Os
  arquivos não mudam.
- Entram a casca desktop, o workflow do GitHub Actions e as definições dos workflows
  n8n exportadas (versionadas, para não viverem só dentro do painel).
- Saem do escopo: port para PHP, empacotador `.zip` de plugin, `smalot`.
- `.env` continua fora do versionamento; `.env.example` acompanha.

## Erros

Toda falha de abertura mostra qual é a causa, não um erro genérico:

| Situação | Mensagem |
|---|---|
| Sem internet | Não foi possível confirmar seu acesso. Verifique a conexão. |
| Usuário revogado | Seu acesso foi encerrado. Procure o administrador. |
| Versão vencida | Há uma versão obrigatória. Atualizar agora. |
| n8n fora do ar | O servidor de autenticação não respondeu. Tente novamente em instantes. |
| Falha na IA | O campo fica pendente e destacado, como já acontece hoje — nunca gera documento incompleto em silêncio. |

## Testes

- A bateria atual (cobertura determinística nos 15 PDFs) roda no Actions a cada commit
  e continua sendo o critério de não-regressão do motor.
- Teste de fumaça nos dois sistemas: abre a janela, autentica contra um n8n de teste,
  extrai um PDF e exporta o documento.
- Teste de revogação: usuário marcado como revogado no n8n não consegue abrir.

## Fora de escopo

- PDFs escaneados (MinerU segue avaliado e não implementado).
- Assinatura digital dos instaladores.
- Sincronização de orçamentos entre máquinas.
- Qualquer distribuição via WordPress.
