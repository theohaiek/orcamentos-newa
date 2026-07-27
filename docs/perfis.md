# Perfis de extração — como autorar e validar

Contrato entre os arquivos `data/profiles/*.json` e o motor de extração
(`extract_engine.py` no dev; a porta em PHP do plugin deve seguir o mesmo contrato).

Um perfil é um JSON em `data/profiles/<id>.json`:

```json
{
  "id": "bradesco",
  "label": "Bradesco Auto/RE — Demonstrativo de Cálculo",
  "match": ["bradesco auto/re"],          // TODOS devem aparecer no texto do PDF
  "fields": {
    "a_vista": { "pick": "kv", "anchor": "TOTAL A PAGAR", "regex": "[\\d.]+,\\d{2}", "format": "currency" },
    "veiculo": [ {spec A}, {spec B} ]      // LISTA = alternativas, a 1ª que casar vence
  }
}
```

## Como o PDF é modelado

- **segments** — tokens agrupados pelo (bloco, linha) do próprio PDF. É o nível que
  separa `Veículo:` de `Valor de Mercado Referenciado` e de `Dias Paralisação:` numa
  mesma linha visual de formulário multi-coluna. **Use `kv`/`row`/`under` sempre que possível.**
- **lines** — tokens reagrupados por faixa de y (linha visual, atravessa colunas).
  Usado por `right`, `below`, `table_cell`, `regex_near`, `text_regex`.

No dump de layout (`layouts/<id>.txt`) você vê as **linhas visuais** com bbox.

## Estratégias (`pick`)

| pick | o que faz | chaves úteis |
|---|---|---|
| `kv` | acha o segmento-rótulo que **contém `:`** e casa `anchor`; pega o valor depois do `:` no mesmo segmento **ou** nos segmentos à direita na mesma faixa de y, parando no próximo rótulo | `anchor`, `regex`, `ytol`, `xmin`, `xmax`, `max_segments`, `exact`, `starts_with` |

> `ytol` (padrão 3.0) é a distância máxima entre os **centros verticais** do rótulo e do
> valor. Não é sobreposição de caixas: as caixas de fonte de linhas vizinhas quase se
> tocam, e um teste de sobreposição capturava a linha de cima (era a origem do
> off-by-one em tabelas de parcelas). `ytol <= 0` significa "mesma baseline, estrito".
| `row` | igual ao `kv` mas **sem exigir `:`** (tabelas rótulo \| valor) | idem |
| `under` | valor nos segmentos **abaixo** da âncora, dentro de janela de x | `at_x`, `xlo`, `xhi`, `dy` |
| `right` | tokens à direita da âncora na mesma **linha visual** | `regex` |
| `below` | linha(s) visuais abaixo, numa janela de x | `at_x`, `xlo`, `xhi`, `dlines` |
| `table_cell` | célula por faixa de coluna x | `col: [x0,x1]` |
| `regex_near` | regex numa janela de linhas a partir da âncora | `span` |
| `text_regex` | regex no texto corrido; devolve **grupo 1** se existir | `regex` |

## Chaves comuns a qualquer spec

- `anchor` — texto do rótulo (comparação sem acento, minúscula, substring).
- `exact: true` — o rótulo (antes do `:`) deve ser **igual** à âncora.
- `starts_with: true` — o rótulo deve **começar** com a âncora.
- `page: N` — restringe a uma página.
- `occurrence: N` — usa a N-ésima ocorrência da âncora (padrão 1).
- `section` / `section_end` — **restringe a busca** ao trecho da página entre dois
  títulos. Essencial quando o mesmo rótulo aparece em seções diferentes
  (ex.: `Veículo:` em `LIMITES MÁXIMOS` vs em `FRANQUIAS` vs em `PRÊMIOS`).
- `regex` — valida/extrai o valor. Se tiver grupo `( )`, devolve o grupo 1.
- **Guardas** (rejeitam o valor): `not_regex`, `reject: ["..."]`, `min_len`,
  `max_words`, `min_value`, `max_value` (numéricos, em número BR).
- `replace: [["pat","rep"], ...]` — regex substituições antes do formato.
- `format` — um ou vários: `currency` (vira `R$ 1.234,56`), `strip_code`
  (`1 - PARTICULAR` → `PARTICULAR`), `upper`, `title`, `sentence`, `simnao`
  (normaliza Sim/Não), `date_iso` (`22/07/2026` → `2026-07-22`), `digits`, `cep`.

## Campos a preencher (31)

seguradora, segurado, veiculo, ano_modelo, principal_condutor, data_proposta,
validade, uso_veiculo, valor_fipe, condutores_18_26, cep_circulacao,
colisao_incendio_roubo, rcf_danos_materiais, rcf_danos_pessoais,
acidente_pessoal_passageiro, morte_pessoal_passageiro, km_reboque,
diarias_carro_reserva, franquia_veiculo, para_brisas, farois, lanternas,
retrovisores, reparo_para_choque, reparo_amassados, protecao_pneu_roda_suspensao,
assistencia_residencial, a_vista, parc_4x, parc_6x, parc_10x

Semântica (o documento final é um COMPARATIVO entre seguradoras — os valores têm
que ser comparáveis entre elas):

- `seguradora` — a companhia (Bradesco, Porto…), **nunca** a corretora (NEWA).
- `segurado` / `principal_condutor` — nomes completos.
- `veiculo` — marca + modelo + versão numa linha (sem código FIPE/chassi).
- `ano_modelo` — `2025` ou `2024/2025`.
- `data_proposta` — data da cotação (formato ISO `AAAA-MM-DD`).
- `validade` — até quando vale (data ou "7 dias").
- `uso_veiculo` — PARTICULAR / COMERCIAL.
- `valor_fipe` — valor de mercado do veículo em R$ (não a LMI de terceiros).
- `condutores_18_26` — Sim/Não (cobertura p/ condutor jovem).
- `cep_circulacao` — CEP de pernoite (`00000-000`).
- `colisao_incendio_roubo` — a **modalidade da cobertura de casco**
  (`100% FIPE`, `Valor de Mercado Referenciado`, `95% FIPE`…), **não** o prêmio.
- `rcf_danos_materiais` / `rcf_danos_pessoais` — **LMI** (limite máximo de
  indenização) de danos materiais / corporais a terceiros. É um valor ALTO
  (tipicamente ≥ R$ 50.000). **NUNCA o prêmio** dessa cobertura (valor baixo).
- `acidente_pessoal_passageiro` / `morte_pessoal_passageiro` — LMI de APP
  (invalidez / morte por passageiro). Pode ser `R$ 0,00` (não contratado).
- `km_reboque` — `KM Ilimitado`, `500 KM`, `250 km`.
- `diarias_carro_reserva` — `15 dias`, `7 dias`, `Não Contratado`.
- `franquia_veiculo` — franquia da cobertura compreensiva/casco.
- `para_brisas`, `farois`, `lanternas`, `retrovisores` — franquia/condição desses
  itens. **Um valor conciso** (`R$ 850,00`); se o PDF tiver vários subtipos,
  prefira o **convencional/básico**.
- `reparo_para_choque`, `reparo_amassados` (martelinho), `protecao_pneu_roda_suspensao`
  — franquia ou `Não Contratado`.
- `assistencia_residencial` — Sim/Não.
- `a_vista` — prêmio TOTAL à vista (não o líquido, não o de uma cobertura).
- `parc_4x` / `parc_6x` / `parc_10x` — valor de **CADA parcela** em 4x/6x/10x
  (preferir a opção **sem juros**; se só houver com juros, use essa).

## REGRA DE OURO

**Preencher errado é MUITO pior que deixar vazio.** O app entrega um documento a um
cliente final. Todo valor capturado por perfil vira "verde/confiável" e não é
revisado pela IA. Se você não consegue capturar o valor com segurança, **não
declare o campo** — a IA cuida dele depois e o usuário confere.

Sempre confira o valor extraído contra o dump `layouts/<id>.txt`.

## Seleção do perfil

`match` (todos os marcadores devem aparecer no texto) + `match_not` (nenhum pode aparecer)
+ `priority`. Perfil dedicado da seguradora usa `priority: 10`; perfil de família/sistema
usa `0`. O `match_not` é necessário quando várias seguradoras usam o mesmo emissor e
compartilham rodapé — sem ele o desempate viraria ordem alfabética do nome do arquivo.

## Como validar

Rode a extração determinística de um arquivo e **confira cada valor contra o PDF**:
o que um perfil captura vira "verde/confiável" e não passa por revisão da IA.
Vale a pena conferir também com o conjunto todo instalado, para detectar colisão de
`match` entre perfis.
