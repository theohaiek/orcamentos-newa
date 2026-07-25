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
      conhecidos e ~6,7/31 num layout inédito, sem erro.
- [x] **Cobertura determinística: 33% → 81%** (10,3 → 25,1 campos de 31 por arquivo).
      Concordância com o consenso de 18 configurações de modelo: **82% → 97%**, sem
      nenhum valor verde incorreto. Campos "a confirmar" (vermelhos): **de ~2% para 0%**.
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

## Produção (WordPress)

- [ ] Portar motor de extração + perfis para PHP (`smalot/pdfparser`) — incluindo
      segmentos por bloco, `kv`/`row`/`under`, `section`, guardas e normalização.
- [ ] Login via usuários nativos do WordPress; persistência em `wp_options`.
- [ ] Empacotador `.zip` do plugin instalável.
- [ ] Modo Visual/recortes: usar Imagick quando disponível; senão, o fac-símile de
      fragmentos (o cliente já degrada para o fac-símile quando não há imagem).
- [ ] PDF escaneado: MinerU como serviço externo (não roda em hospedagem compartilhada).

## Geral

- [ ] Calibrar cores/logos oficiais das seguradoras.
