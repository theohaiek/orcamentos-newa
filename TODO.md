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
- [ ] Campos que nenhum layout entrega hoje: `valor_fipe` (a maioria traz só o código
      FIPE) e `condutores_18_26` em parte dos layouts.
- [ ] Cotações **multi-oferta** (Allianz traz 6 planos lado a lado): hoje o perfil só
      declara o que é idêntico entre as ofertas. Falta o usuário escolher a oferta.
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
- [x] **Suíte de testes** ([`tests/`](tests/)): cinco testes, nenhum chamando a OpenAI.

## Pendências críticas

- [ ] **Trocar a chave da OpenAI.** Ela esteve exposta por path traversal num servidor
      em execução. Trocar e recriar o `.env`.
- [ ] **Decidir sobre o histórico do git.** O CPF saiu do arquivo mas continua nos
      commits anteriores e em `origin/main`. Limpar exige reescrita de histórico
      (`git filter-repo` + `push --force`) — decisão do dono do repositório.
- [ ] **Redigir dados pessoais antes de enviar à OpenAI.** Hoje vai o **texto integral**
      do PDF: nome, CPF, CEP, placa, chassi. A spec do app desktop afirma o contrário
      ("nenhum PDF sai da máquina") e precisa ser corrigida ou o código, ajustado.
- [ ] **Corrigir os 3 valores divergentes da via PHP** (`yelum/a_vista`,
      `aliro/parc_10x`, `yelum/veiculo`) antes de qualquer uso do port em produção.
- [ ] **Escolha de oferta pelo usuário** em PDFs multi-oferta: hoje só avisamos. O certo
      é listar as ofertas e deixar escolher.
- [ ] **Versionar o motor.** `server.py` e `extract_engine.py` produzem todos os números
      publicados e não estão sob controle de versão em lugar nenhum.
- [ ] **Reavaliar o `gpt-5-nano`.** A métrica que sustentou a escolha só comparava
      campos que o modelo preencheu, escondendo dois terços da distância: cobertura
      correta real de **44%** contra 69,4% do `gpt-4o-mini`.

## Distribuição (v0.4 → V1) — decisão em aberto

As duas vias são viáveis; ver [`docs/avaliacao-smalot.md`](docs/avaliacao-smalot.md)
(PHP entrega 93% da cobertura) e
[`docs/superpowers/specs/2026-07-25-app-desktop-design.md`](docs/superpowers/specs/2026-07-25-app-desktop-design.md).

**Se for plugin WordPress:**
- [ ] Portar o motor para PHP sobre `smalot/pdfparser`, tratando `Do` (Form XObject),
      `/Contents` em array e ligando `setDataTmFontInfoHasToBeIncluded(true)`.
- [ ] Reconstrução de palavras por métrica de glifo (é o que recupera `hdi` e `justos`).
- [ ] Login via usuários nativos do WordPress; persistência em `wp_options`.
- [ ] Empacotador `.zip` do plugin.

**Se for app desktop:**
- [ ] **Portão de validação:** protótipo `pywebview` provando janela nativa, ícone na
      taskbar/Dock, fluxo completo e — o que decide — **exportação do PDF no macOS**
      (WebKit, não Chromium). Reprovando, a casca vira Electron.
- [ ] Backend n8n: `/auth` (whitelist, token), `/ia` (proxy da OpenAI) e `/versao`.
- [ ] App consumindo o backend; falha fechado quando não confirma o acesso.
- [ ] Atualização automática: perfis/interface a quente, motor via instalador.
- [ ] Build no GitHub Actions (matriz Windows + macOS) gerando `.exe` e `.dmg`.
- [ ] Rever o furo de acesso: whitelist remota com senha local padrão `123` não impede
      quem descobrir um username de entrar na própria máquina.

**Em qualquer das duas:**
- [ ] PDF escaneado: MinerU como serviço externo (segue fora do escopo por ora).

## Geral

- [ ] Calibrar cores/logos oficiais das seguradoras.
