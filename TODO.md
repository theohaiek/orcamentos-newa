# TODO — Orçamentos NEWA

Backlog de melhorias e correções. Marque `[x]` ao concluir.

## Extração — cobertura e correção (v0.2 → v0.3) — CONCLUÍDO

- [x] **Causa raiz da baixa cobertura encontrada.** O motor lia "o valor à direita do
      rótulo" na **linha visual**, que num formulário multi-coluna junta pares de colunas
      diferentes (`Veículo: Valor de Mercado Referenciado Dias Paralisação: 0,00 D.M.:
      100.000,00`). Resultado: ou não capturava, ou capturava o valor do rótulo vizinho.
      Passou a usar **segmentos** (bloco/linha do próprio PDF), que já separam rótulo e
      valor por coluna.
- [x] **Bug de "mesma linha".** O teste era sobreposição de caixas; como as caixas de
      fonte de linhas vizinhas quase se tocam, capturava a linha **de cima** — `parc_4x`
      devolvia o valor de 3x e `validade` devolvia a data do cálculo. Agora compara
      **centros verticais**.
- [x] **Motor v2:** estratégias `kv` / `row` / `under`; recorte por `section`;
      **guardas** (`min_value`, `max_value`, `not_regex`, `reject`, `max_words`);
      **normalização** (`currency`, `date_iso`, `cep`, `simnao`, `strip_code`, `replace`);
      **specs alternativas** por campo; `priority` e `match_not` na seleção de perfil.
- [x] **15 perfis dedicados** (aliro, allianz, azul, bradesco, darwin, hdi, itau, justos,
      mapfre, mitsui, porto, suhai, tokio, yelum, zurich), cada um validado campo a campo
      contra o PDF de origem.
- [x] **Camada genérica reconstruída**: derivada dos perfis dedicados, filtrada por
      *leave-one-out* (regra validada num layout que nunca viu) e por um portão que
      descarta regra divergente do perfil dedicado. 33 generalizações inseguras foram
      barradas — entre elas `reparo_para_choque` devolvendo R$ 15.000,00 (uma LMI) e
      `franquia_veiculo` devolvendo um prêmio. Sozinha entrega 11,5/31 nos layouts
      conhecidos e ~6,7/31 num layout inédito.
      *Corrigido:* o "sem erro" que constava aqui é falso — a própria execução do
      `loo_generic.py` imprime 14 valores errados e 86% de precisão. Além disso a
      seleção dos campos "seguros" olhou todas as dobras (circular; refeita de forma
      aninhada aparecem 3 erros) e 41% das regras embarcadas nunca passaram pelo
      leave-one-out.
- [x] **Cobertura determinística: 33% → 81%** (10,3 → 25,1 campos de 31 por arquivo);
      24,9/31 sob critério de plausibilidade por tipo. Verificado de forma independente
      na auditoria de 2026-07-26, que também confirmou que nenhum dos 376 valores
      determinísticos está numericamente errado nesta amostra.
      *Corrigido:* o "0% de campos a confirmar" que constava aqui era artefato de uma
      verificação que aceitava qualquer string presente no documento — hoje são 4%, e
      são reais. E os 33% de referência vêm do motor NOVO rodando sobre os perfis
      antigos: o par motor-antigo + perfis-antigos não é reproduzível.
- [x] **Verdes errados que existiam foram corrigidos** — `farois`/`lanternas` devolviam
      a LMI da cobertura de vidros (R$ 25.000,00) em vez da franquia; `para_brisas`
      devolvia o vidro traseiro; `km_reboque` do HDI dizia "100 km" onde o PDF diz
      "Guincho Sem Limite de KM".
- [x] **Seguradora da coluna:** detecção passou a priorizar o campo extraído. Cotações
      Porto/Itaú/Azul/Mitsui saem do mesmo sistema e trazem "Seguradora: Allianz Seguros"
      (a **congênere** da renovação) — as quatro colunas ganhavam a marca errada.
      Seguradora identificada mas não cadastrada agora cai em marca neutra, nunca em
      outra marca citada de passagem.
- [x] **"Não consta no PDF"** virou categoria própria (ponto cinza) — coberturas que o
      documento não menciona deixaram de aparecer como alerta vermelho de conferência.
- [x] **Modelo padrão → `gpt-5-nano`** com `reasoning_effort` ajustável em *Configurações*
      (padrão `low`) e degradação automática quando a API recusa o valor do esforço.
      *Ressalva:* o ranking que embasou a comparação media precisão **só sobre os campos
      que o modelo preencheu**, o que favorece quem deixa em branco. Por cobertura
      correta, o nano@low faz **44%** contra 69,4% do `gpt-4o-mini` — ver pendências.
- [x] **MinerU avaliado** (`docs/avaliacao-mineru.md`): sem ganho em PDF nativo, decisivo
      em PDF escaneado.

## Extração — próximos passos

- [ ] **Auto-perfil**: quando nenhum perfil reconhecer o PDF, propor um perfil a partir
      das posições que a IA já ancorou (valor verificado → rótulo mais próximo à esquerda
      /acima) e deixar o usuário confirmar em *Modelos de Entrada*. A partir do segundo
      envio daquela seguradora a extração vira determinística.
- [ ] Editar/gerenciar perfis pela UI (seção *Modelos de Entrada*).
- [ ] `valor_fipe` (0/15) e `condutores_18_26` (9/15) — ver *Próxima sessão*, item 3.
- [ ] Cotações **multi-oferta** — ver *Próxima sessão*, item 2.
- [ ] Suporte real a comparar 3–5 propostas (hoje em beta).

## Auditoria de 2026-07-26 — corrigido

Uma auditoria adversarial (83 agentes, 40 achados confirmados) encontrou defeitos graves
no trabalho da v0.3. O que já foi corrigido:

- [x] **Path traversal sem autenticação.** `/assets/` e `/data/` eram servidas antes do
      login e `serve_file` não tinha contenção de caminho: `/assets/../../../.env`
      entregava a chave da OpenAI e o hash de senha. Corrigido com `realpath` +
      `commonpath`, coberto por [`tests/test_traversal.py`](tests/).
- [x] **"IA verificada" não verificava nada.** O valor era aceito se a string existisse
      em QUALQUER lugar do documento. Num teste de injeção, **85 de 89 alucinações**
      passavam como verificadas. Agora o valor só é aceito quando aparece **junto a um
      rótulo do próprio campo**, e o casamento é por token inteiro (o valor `15` casava
      dentro de `15.000,00`). Injeção agora: **0 de 89**.
- [x] **"Não consta no PDF" era a palavra da IA promovida a fato.** Agora só é aceito
      depois de conferir que nenhum rótulo do campo aparece no documento. `-`, `--`,
      `n/a` e `na` saíram da lista de ausência: são conteúdo legítimo de célula.
- [x] **Multi-oferta escolhida em silêncio.** A Allianz cota 6 planos; o motor lia a
      primeira coluna e publicava `Colisão/Incêndio/Roubo 100% FIPE` para um plano que o
      próprio PDF diz não cobrir colisão. Agora é detectado (15/15 nos PDFs de amostra,
      sem falso positivo), os campos que dependem da oferta vão para conferência e um
      aviso explícito é exibido.
- [x] **PDF parcialmente escaneado passava calado.** O guarda era o tamanho do texto do
      documento inteiro; um PDF com 1 página nativa e 2 em imagem entregava 10/31 campos
      com a mesma tela verde. Agora a validação é **por página** e as ilegíveis são
      listadas.
- [x] **`ai_error` e `drift` eram calculados e nunca exibidos** — falha total da IA era
      indistinguível de "o PDF não tem esse dado". Viraram avisos na interface.
- [x] **Campo não confirmado não bloqueava a geração.** Agora conta como pendência, e
      editar o campo à mão registra proveniência manual (antes a edição não mexia na
      proveniência).
- [x] **Casamento de perfil sensível a espaço.** Um espaço a mais no meio do marcador
      derrubava o documento inteiro para a IA. `match_profile` compara sem espaços.
- [x] **CPF real de terceiro versionado** em `docs/avaliacao-mineru.md`. Removido do
      arquivo. **O histórico do git ainda contém** — ver pendências abaixo.
- [x] **Suíte de testes** ([`tests/`](tests/)): começou com cinco; hoje são **11
      arquivos**, nenhum chamando a OpenAI e nenhum usando rede real.

## Correções de 2026-07-28

- [x] **Recusa com corpo grande derrubava a conexão em vez de responder.** O
      servidor respondia 401/400 **sem ler o corpo** da requisição. Como a conexão é
      HTTP/1.1 com keep-alive, os bytes do PDF ficavam no socket: o handler voltava
      ao laço, lia o começo do PDF como se fosse a requisição seguinte, respondia
      400 e fechava com o resto por ler — e fechar socket com dados não lidos, no
      Windows, manda RST. O RST apaga o que ainda estava no buffer do cliente,
      inclusive a resposta já enviada. Na prática: **sessão expirada + proposta real
      = erro de rede, sempre**, em vez do 401 que a tela sabe explicar. Medido: 2
      falhas em 12 com 500 bytes, **12 em 12 com 2 MB**. Atinge `/api/save-pdf`
      (gravar a proposta), `/api/extract` (enviar a cotação) e todo POST/PUT/DELETE
      recusado por sessão ou permissão. Corrigido drenando o corpo antes de qualquer
      resposta; coberto por `tests/test_export.py`.
      *Foi este defeito que causava a intermitência do `test_export.py`* — que
      passava sozinho e falhava na suíte, e estava registrado como "causa
      desconhecida".

- [x] **BOM zerava a configuração inteira, em silêncio.** `jread` abria os JSON de
      dados como `utf-8` puro. Bloco de Notas, PowerShell e quase toda ferramenta do
      Windows gravam um BOM no começo do arquivo — que virava erro de parsing. Como a
      falha é engolida por design (`except: return default`), o app voltava a **todos**
      os padrões sem avisar: bastava alguém abrir o `config.json` no Bloco de Notas e
      salvar para os dados da corretora sumirem da proposta. Vale para `config.json`,
      `users.json`, `insurers.json` e `template.json`. Corrigido com `utf-8-sig`, que
      lê com e sem BOM. Coberto por `tests/test_config.py`.
- [x] **Migração de configuração não grava mais por cima do que não conseguiu ler.**
      Config ilegível chega como `{}`, indistinguível de "não existe"; a migração
      escrevia por cima e apagava o que dava para recuperar. Aconteceu de verdade nesta
      máquina, com a configuração de desenvolvimento. Agora só migra config lida.

- [x] **A atualização automática podia impedir o app de abrir.** Dois defeitos que
      só apareceram juntos, ao publicar o `auth.py` — e o efeito somado foi a
      instalação desta máquina parar de abrir:
      1. *A lista de arquivos envelhecia junto com o updater instalado.* Ela era uma
         constante no `updater.py`. O updater da versão instalada baixou o
         `server.py` novo (que passou a fazer `import auth`) e **ignorou o `auth.py`**,
         porque a lista dele, antiga, não conhecia o arquivo. Agora a lista viaja
         dentro do pacote baixado (`data/sincronizar.json`), então quem descreve o
         conjunto é sempre a versão que está sendo instalada. As travas de caminho
         (`..`, absoluto, `:`) continuam valendo venha a lista de onde vier.
      2. *A rede de proteção não protegia.* O `app.py` já tinha o "se o repositório
         quebrar, use a cópia embutida", mas fazia `sys.path.remove(repo)` — que tira
         **uma** ocorrência. O `app.py` do repositório insere a própria pasta no
         `sys.path`, então havia duas, e a que sobrava fazia o código "embutido"
         continuar importando do repositório quebrado. Agora remove todas, limpa os
         módulos meio-importados, **tenta ressincronizar** com o updater embutido e
         só então desiste para a cópia embutida.
      Coberto por `tests/test_sincronizacao.py`.

## v1.0 — 29/07

Fechada para a reunião de 30/07. O que entrou nesta versão, e as decisões que eu
tomei sozinho porque o Theo estava dormindo — todas sob a regra que ele deu:
**nunca piorar a extração de nenhuma forma.**

- [x] **Escolha do plano em cotação multi-oferta.** A detecção já existia; o que
      faltava era escolher. Medi antes de construir, e a medição derrubou duas
      hipóteses minhas: cada oferta ocupa **duas** sub-colunas nas linhas de cobertura
      (limite e prêmio) e **uma só** na linha de total, e a primeira sonda que escrevi
      reprovava linhas corretas por exigir um valor por coluna.
      Duas regras independentes separam as colunas: fronteira de x tirada do total, e
      divisão por contagem. **Allianz: concordam em 23 de 23 linhas. HDI: 17 de 24**,
      porque lá a fronteira do total cai em cima de valores de cobertura.
      *Decisão:* com dois documentos multi-oferta na amostra não dá para eleger uma
      regra, então o valor **só é oferecido quando as duas concordam**. Onde discordam,
      o campo fica exatamente como está hoje. Resultado: 5 campos na Allianz, 1 na HDI.
      *Decisão:* a extração roda igual e primeiro; isto é uma segunda passada que
      apenas oferece o valor das outras colunas. E os campos continuam exigindo
      confirmação depois da escolha, como já exigiam. **O pior caso desta
      funcionalidade é o comportamento anterior**, e há teste que trava isso: a coluna
      1 tem que ser idêntica ao valor que a extração já entregava.
      *Limite conhecido:* só vale para campos cujo valor é moeda. Sim/Não,
      "100% FIPE" e "400 KM" não são separáveis por coluna monetária e seguem como
      antes.
- [x] **Cabeçalho do assistente** mostra o logo grande de cada seguradora comparada,
      e o seletor de plano quando houver.
- [x] **Banner do comparativo** passou a usar o logo com o nome da seguradora. Antes
      usava o símbolo isolado, que aparecia sem identificação.
- [x] **Mural da capa** ganhou seletor individual das 23 marcas, recolhido, com
      marcar/desmarcar todas. Lista vazia continua significando "todas".
- [x] **Ícone de Configurações** tinha o caminho dos dentes corrompido. Refeito.
- [x] **Marca d'água da capa** repete o desenho do logo da NEWA (duas hastes em
      verdes diferentes e o X cruzando) e ganhou uma grade concêntrica verde saindo
      do centro, mais fraca que a própria marca. O esmaecido é gradiente branco por
      cima, não `mask`: o html2canvas que gera o PDF não aplica máscara, e a grade
      sairia como um quadrado sólido.

## Próxima sessão — decidido com o Theo em 28/07

### 1. Instalar numa máquina que não seja a de desenvolvimento

O instalador nunca rodou em outro computador, e o trecho que instala o WebView2
sozinho **nunca foi exercitado** — esta máquina já tem o componente, então ele sempre
entrou pelo caminho "já instalado". É código escrito e não testado.

Roteiro, de preferência num Windows 11 e num Windows 10 desatualizado:

1. Copiar a pasta `DEMONSTRAÇÃO INSTALAÇAO` inteira, ou só o
   `Instalar Orcamentos NEWA.exe` (para exercitar o modo que baixa do GitHub).
2. Executar. Anotar: apareceu o SmartScreen? Deu para passar com "Mais informações →
   Executar assim mesmo", ou o Windows **bloqueou de vez**? (Smart App Control ligado
   recusa binário sem assinatura, e não é o mesmo que o aviso.)
3. Ver se o antivírus da máquina reclama do executável — PyInstaller sem assinatura
   dá falso positivo com alguma frequência.
4. Conferir a linha `componente de tela (WebView2)` na saída: se disser "não
   encontrado, instalando", é a primeira vez que esse caminho roda de verdade.
5. Abrir pelo atalho da Área de Trabalho e fazer um orçamento inteiro, até o PDF.

Só x64. Windows 32 bits não roda, e não está previsto.

### 2. Multi-oferta: a pré-visualização da área lida ainda não existe

**Feito na v1.0:** a escolha do plano, com seletor no cabeçalho do assistente.
**Não feito:** o recorte lado a lado mostrando a região que está sendo lida e a que
está sendo descartada. A infraestrutura existe (`GET /api/crop`, e as ofertas já
carregam a página e as faixas de x), mas não deu tempo de fazer com cuidado antes da
reunião, e meia-implementação de pré-visualização é pior que nenhuma: dá confiança
sem dar prova. Fica para a próxima sessão.

Também segue aberto: os campos não-monetários (Sim/Não, "100% FIPE", "400 KM") não
são separáveis por coluna e continuam pedindo confirmação manual, e a regra de
separação só foi validada em dois documentos.

<details><summary>Descrição original</summary>

Hoje o app detecta que há várias ofertas (15/15 nos PDFs de amostra, sem falso
positivo), lê a primeira coluna e joga os campos que dependem do plano para
conferência — 15 campos, na Allianz. Foi a fricção que travou o uso em 27/07.

O que fazer: ao detectar multi-oferta, abrir uma escolha em *dropdown* com os planos
e seus preços, **mostrando a área do documento que está sendo lida e a que está sendo
descartada**. A infraestrutura para isso já existe: cada campo carrega `page` + `bbox`
na proveniência, e há `GET /api/crop` recortando região da página. Escolhida a oferta,
a extração passa a ler aquela coluna e os campos saem de conferência.

</details>

### 3. `valor_fipe` e `condutores_18_26` — o que exatamente falta

São dois problemas diferentes que estavam na mesma linha, e daí a confusão.

**`valor_fipe` — 0 de 15.** Medido nos PDFs de amostra: os 15 mencionam a FIPE, e
**nenhum traz o valor em reais**. O que existe é o *código* FIPE, que identifica o
modelo (`093017-2`, o mesmo veículo em todas as cotações), não quanto ele vale. Ou
seja: não é o motor que está falhando em achar — o dado **não está no documento**.
Nossas escolhas eram três, e você pediu para detalhar antes de escolher:

- digitar à mão (proveniência manual, ponto azul) — sem dependência externa;
- consultar a tabela FIPE por API a partir do código impresso — preenche sozinho, mas
  depende de rede e de terceiro, e a FIPE do mês pode não ser a que a seguradora usou;
- assumir "não consta no PDF" (cinza) e tirar da proposta.

**`condutores_18_26` — 9 de 15.** Este o motor extrai onde o dado existe. Os 6 que
faltam (azul, itaú, justos, mitsui, porto, suhai) não declaram a informação em lugar
nenhum do documento — não é regra faltando no perfil. Vale conferir um a um antes de
concluir: pode ser que em algum deles a informação exista com outro nome.

## Pendências críticas

- [x] **A chave da OpenAI saiu do código e do disco.** Não há mais `.env`, nem leitura
      de variável de ambiente, nem padrão embutido: a única fonte é o campo em
      *Configurações*, digitado na máquina de quem usa e guardado no `config.json`
      dela. `.env.example` foi removido do repositório porque não havia mais o que
      exemplificar. A cota passa a ser sempre da conta do cliente.
      **Falta você:** a chave antiga esteve exposta e continua válida até ser revogada
      no painel da OpenAI — apagar do disco não revoga nada.
- [x] **Histórico do git limpo.** O CPF foi redigido em todos os commits com
      `git filter-repo` e o histórico reescrito foi publicado; um clone novo do remoto
      não tem mais o dado. Uma varredura junto encontrou e removeu um segundo caso da
      mesma origem — o CEP real de uma amostra usado como exemplo em `docs/perfis.md`.
      **Ressalva:** o GitHub ainda serve os commits antigos por SHA direto até rodar o
      próprio garbage collect; para garantia, abrir chamado no suporte.
- [ ] **Redigir dados pessoais antes de enviar à OpenAI.** Hoje vai o **texto integral**
      do PDF: nome, CPF, CEP, placa, chassi. A spec do app desktop afirma o contrário
      ("nenhum PDF sai da máquina") — ou o código muda, ou a spec está mentindo.
      *Aguardando decisão do Theo (perguntado em 28/07).* O argumento mais forte não é
      LGPD, é que **nenhum desses campos é usado pela extração**: os 31 campos são
      coberturas, franquias, prêmios e parcelamento. Estamos pagando token para enviar
      dado pessoal que o motor descarta — então mascarar não deve custar cobertura, e
      dá para medir antes e depois em vez de afirmar.
- ~~Corrigir os 3 valores divergentes da via PHP~~ (`yelum/a_vista`,
  `aliro/parc_10x`, `yelum/veiculo`). **Sem efeito desde que o WordPress saiu do
  escopo** — não existe port PHP em produção nem previsto. Fica registrado porque
  a divergência é do motor de âncoras, não do parser: se o port voltar à mesa,
  esses três casos são o ponto de partida.
- [ ] **Escolha de oferta pelo usuário** em PDFs multi-oferta — ver *Próxima sessão*,
      item 2.
- [x] **Motor versionado.** `server.py`, `extract_engine.py` e `index.html` entraram no
      repositório.
- [x] **Modelo padrão de volta ao `gpt-4o-mini`.** A métrica que sustentou o
      `gpt-5-nano` só comparava campos que o modelo preencheu — o que premia quem
      deixa em branco — e escondia dois terços da distância: **44%** de cobertura
      correta contra **69,4%**. O custo maior por chamada pesa pouco, porque os
      perfis determinísticos já entregam ~80% e a IA só cobre o resíduo. Config já
      gravada com o nano é migrada uma vez, respeitando quem escolher o nano depois.

## Distribuição (v0.4 → V1) — DECIDIDO: app desktop Windows

O WordPress fica de fora. O motor continua em Python, o app vira executável
Windows com janela própria, e o n8n entra **só para validar acesso** — nunca para
processar PDF. Servidor n8n já disponível, com uptime saudável. Avaliação que sustenta
a escolha: [`docs/avaliacao-smalot.md`](docs/avaliacao-smalot.md) e
[`docs/superpowers/specs/2026-07-25-app-desktop-design.md`](docs/superpowers/specs/2026-07-25-app-desktop-design.md).

**O n8n não guarda a chave da OpenAI** — chegou-se a cogitar isso, e foi descartado em
28/07. A chave é do cliente, digitada em *Configurações* na máquina dele; o Theo a
instala à mão, em call. Assim o n8n fica fora da cadeia de dado pessoal e a cota é da
conta de quem usa.

**O repositório é público**, e a atualização automática puxa direto do zip do branch.
Chegou-se a desenhar o n8n servindo o manifesto com o repositório privado atrás; não
foi preciso. Abrir o repo **não** é "carro sem chave": Python empacotado é
desempacotável e a verificação de acesso, removível. O que o n8n protege de fato é o
corte de acesso a quem usa o build oficial — não os perfis, que são públicos por opção.

- [x] **Atualização automática** ([`updater.py`](updater.py)), em duas frentes:
      *Perfis* — manifesto `versao.json` com sha256 por perfil; baixa só o que mudou,
      confere o hash, recusa o que não for perfil válido, grava de forma atômica em
      pasta gravável do usuário (a instalação em `Program Files` não é gravável) e o
      perfil baixado se sobrepõe ao instalado por nome. Nome de arquivo validado contra
      `[a-z0-9_-]+\.json`, então manifesto adulterado não escreve fora da pasta.
      *Programa inteiro* (`sincronizar_repo`) — baixa o zip do branch e grava só o que
      difere, com a lista de arquivos vinda de dentro do próprio pacote. Sem rede, tudo
      falha em silêncio e o app trabalha com o que tem. Versão nova do app é
      **anunciada**, nunca aplicada sozinha; downgrade nunca é oferecido.
      `GET /api/update` expõe o estado. 24 asserções em
      [`tests/test_updater.py`](tests/test_updater.py) e 16 em
      [`tests/test_sincronizacao.py`](tests/test_sincronizacao.py), sem rede real.
- [x] **Casca `pywebview`** ([`app.py`](app.py)): janela nativa, ícone próprio, porta
      livre em vez de fixa, janela só abre quando o servidor aceita conexão, DPI por
      monitor, e recusa com explicação quando falta a runtime do WebView2 (sem ela o
      pywebview cai no motor do Internet Explorer, onde a interface não roda).
      `--verificar` prova o binário sem abrir janela.
- [x] **Instalador** ([`instalador.py`](instalador.py)): executável de 8 MB que instala
      em `%LOCALAPPDATA%` sem pedir administrador, cria atalho na Área de Trabalho e no
      Menu Iniciar, escreve um desinstalador que preserva os dados, e prova a instalação
      rodando `--verificar` antes de declarar sucesso. Funciona com o pacote ao lado
      (zip extraído ou `git clone`), sozinho (baixa do GitHub) e por cima de uma
      instalação anterior — comparando arquivo a arquivo, então não duplica nada.
- [x] **O programa acompanha o repositório**: o executável carrega Python e as
      bibliotecas; motor, interface e perfis vivem em `<instalação>/repo` e são
      sincronizados a cada abertura e a cada login. Correção publicada chega ao usuário
      no próximo login, sem reinstalar.
- [x] **Build enxuto**: 942 MB → 82 MB. O PyInstaller arrastava o que estivesse
      instalado no Python da máquina (torch, llvmlite, ffmpeg, scipy, onnxruntime).
- [x] **Cliente do `POST /auth`** ([`auth.py`](auth.py)): com `auth_url` configurada,
      quem decide quem entra é o servidor, e o `users.json` local **não é consultado
      nem como segunda chance** — é o que fecha o furo da senha padrão `123`. Só
      libera com 200 + JSON + `ok: true`: HTML de proxy, corpo vazio e 4xx negam.
      5xx e falha de rede são tratados como indisponibilidade, não como negativa, e
      aí vale o crachá offline: usuário, papel, prazo e um **hash** da senha gravados
      no último acesso confirmado. Servidor negando apaga o crachá, então quem foi
      desligado não segue entrando por inércia. HTTPS obrigatório (a senha trafega).
      25 asserções em [`tests/test_auth.py`](tests/), sem rede real.
      **Falta você:** montar o fluxo no n8n — o contrato está no cabeçalho do
      `auth.py`. Enquanto `auth_url` estiver vazia, o login segue local, que é o modo
      de desenvolvimento. Ligar é colar a URL em *Configurações → Controle de acesso*.
- [x] **A chave da OpenAI é do cliente**, digitada em *Configurações* e guardada no
      `config.json` da máquina dela. Sem proxy `/ia`: o texto do PDF vai direto do app
      para a OpenAI, então o n8n **não** entra na cadeia de dado pessoal, e a cota é do
      cliente, na conta dele.
- [ ] Publicação: rotina que gera `versao.json` com os hashes dos perfis e sobe o
      instalador, para o updater não depender de passo manual.
- [ ] **O furo de acesso está fechado no código, mas ainda não em produção.** O
      caminho existe e é testado: com `auth_url` preenchida, a senha local e o padrão
      `123` deixam de valer. Só que `auth_url` está **vazia** no que foi publicado —
      porque o fluxo no n8n ainda não existe, e ligar antes disso trancaria o Theo fora
      do próprio app. Enquanto isso, quem tiver o app instalado entra com `Madu`/`123`.
      Fecha quando o webhook estiver de pé.
- [ ] Assinatura de código fica **fora** do escopo: a Microsoft declara que EV não evita
      mais o SmartScreen, e a reputação zera a cada versão. O aviso da primeira execução
      é aceito conscientemente.
- [ ] PDF escaneado: MinerU como serviço externo (segue fora do escopo por ora).

**macOS — fora do escopo até haver um Mac para testar.** Três incógnitas impedem
qualquer promessa: a exportação do PDF (`jsPDF.save()` dispara `<a download>` num
`blob:`, e o `pywebview` vem com downloads desligados por padrão), a persistência do
cookie de sessão em `http://127.0.0.1` no WKWebView, e a tabela do comparativo, que usa
`var()` dentro de `repeat()` no grid — se falhar, a página 2 colapsa em vez de degradar.
Some-se US$ 99/ano de Apple Developer Program.

## Geral

- [ ] Calibrar cores/logos oficiais das seguradoras.
