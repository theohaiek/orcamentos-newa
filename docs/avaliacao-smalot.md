# smalot/pdfparser × PyMuPDF — quanto pior fica rodando em PHP

Data: 2026-07-26 (revisão) · **Corrige a versão de 2026-07-25, que estava errada.**

> **Retratação.** A primeira medição concluiu que o port para PHP renderia ~50% de
> cobertura e que o `smalot` era incapaz de fornecer a informação que o motor precisa.
> **Isso estava errado, e o erro era do script de teste, não da biblioteca.** Este
> documento traz a medição refeita. A conclusão se inverte: o motor roda em PHP com
> **93% da cobertura** que tem em Python, sem alterar um único perfil.

## O que estava errado na primeira medição

| Defeito no script | Consequência que virou "limitação da biblioteca" |
|---|---|
| `getDataCommands()` não trata o operador `Do`, então todo texto dentro de **Form XObject** ficava invisível | `aliro` e `yelum` apareceram com "zero posição". O stream de página deles tem **47 bytes** — 100% do texto está no Form |
| `/Contents` como **array de streams** não era desembrulhado | `bradesco` aparecia perdendo 41% do texto |
| Foi ligado `setHorizontalOffset('')`, que é **código morto** na 2.12.5, e nunca foi ligado `setDataTmFontInfoHasToBeIncluded(true)`, que é a opção que dá fonte e corpo por fragmento | reconstrução de palavras muito pior do que o possível |

Também foi afirmado que o `smalot` "não tem nível de bloco". **Falso**: `getDataCommands()`
é público e emite `BT`/`ET` (início/fim de bloco de texto), que cobre 88,9% das âncoras.
E o "bloco" do PyMuPDF também não vem do PDF — é sintetizado pelo MuPDF, portanto é
reproduzível em PHP.

Corrigidos os três defeitos (≈30 linhas de PHP):

| | script errado | corrigido |
|---|---:|---:|
| perda de tokens vs PyMuPDF | 16,4% | **0,1%** (11 de 18.381) |
| âncoras dos perfis localizadas (fragmento cru) | 70% | **86,2%** |
| âncoras dos perfis localizadas (reconstruído) | 75% | **96,4%** |

## Compatibilidade com WordPress: aprovada

`smalot/pdfparser` v2.12.5 exige apenas `php >= 7.1`, `ext-zlib` e `ext-iconv` —
presentes em qualquer hospedagem. PHP puro, sem binário externo, sem `exec`, instalável
por Composer e vendorizável no `.zip` do plugin. Testado em PHP 8.2.32.

**Ressalva de licença:** LGPL-3.0 — compatível com um plugin GPLv3+, incompatível com
GPLv2-only.

## O teste que vale: o motor real, sem adaptação

Os fragmentos do `smalot` são convertidos em palavras/segmentos e entregues ao **motor
de extração real** (`run_profile` + `run_generic`), com **os 18 perfis intocados**.

| | PyMuPDF (hoje) | smalot (PHP) | |
|---|---:|---:|---|
| campos por PDF | 25,1/31 | **23,3/31** | **93,1%** |
| valores idênticos | — | 342 de 376 | 91,0% |
| campos que só o PyMuPDF pega | — | 26 | caem para a IA |
| valores divergentes | — | 8 | ver abaixo |
| tempo por PDF | 16 ms | 283 ms | 18× mais lento |

283 ms por PDF é irrelevante para o caso de uso (o usuário envia 2 a 5 cotações e a
chamada de IA sozinha leva segundos).

### As 8 divergências, separadas por gravidade

**Três são valor realmente errado** — este é o custo real do port:

| arquivo | campo | PyMuPDF | PHP |
|---|---|---|---|
| `yelum` | `a_vista` | R$ 4.767,91 | **R$ 4.440,22** |
| `aliro` | `parc_10x` | R$ 346,05 | **R$ 314,60** |
| `yelum` | `veiculo` | TIGGO 7 SPORT 1.5 TURBO 16V AUT. (Flex) | **"Capacidade Categoria Reg. de Tarif..."** |

Os dois primeiros são do mesmo emissor (Autoperfil), cuja linha de total traz o mesmo
valor repetido em 4 colunas de forma de pagamento — a reconstrução PHP pega a coluna
errada. É corrigível no perfil, mas **tem que ser corrigido antes de qualquer uso real**:
um preço errado vai direto para a proposta do cliente.

**Cinco são cosméticas** (mesmo conteúdo, espaço ou emenda):

| arquivo | campo | diferença |
|---|---|---|
| `allianz` | `veiculo` | emendou `4PVersão: 000158/158.` no fim |
| `bradesco` | `colisao_incendio_roubo` | emendou `Dias Paralisação` |
| `hdi` | `veiculo` | `CAOA CHERY- TIGGO` (falta um espaço) |
| `suhai` | `veiculo` | `16 V` em vez de `16V` |
| `suhai` | `ano_modelo` | `2025` em vez de `2025/2025` |

### Sobre `hdi` e `justos`

Estes dois PDFs **realmente** posicionam caractere a caractere: 0,87 e 0,92 caracteres
por operador `Tj`, contra 8,6 a 43,1 nos outros treze. Isso é do arquivo, não da
biblioteca — nenhum parser faz melhor. Com a reconstrução de palavras corrigida, eles
saem de 0 para 24/27 e 21/23 campos.

## Uma correção que veio deste estudo

O casamento de perfil comparava os marcadores **com** espaços. Onde a reconstrução de
palavras insere ou perde um espaço no meio do marcador, o perfil deixava de casar e o
documento inteiro caía na IA. `match_profile` passou a comparar **sem espaços**
(`extract_engine._nospace`). Isso não muda nada no caminho PyMuPDF — os 15 PDFs casam
com os mesmos 15 perfis e a cobertura continua 25,1/31 — e é o que leva a via PHP de
20,3 para 23,3 campos.

## Conclusão

O port para PHP é **viável**, e o WordPress volta a ser uma opção legítima de
distribuição. O custo honesto:

- **–7% de cobertura determinística** (23,3 contra 25,1 campos por PDF); a diferença
  cai para a camada de IA, que já existe.
- **3 valores errados em 350** que precisam ser corrigidos no perfil antes de produção.
- **18× mais lento**, sem impacto prático.
- Duas implementações do mesmo motor para manter em paralelo — este é o custo
  recorrente, e é o argumento mais forte contra.

A escolha entre plugin WordPress e app desktop volta a ser uma decisão de **produto**
(onde o usuário quer usar, que controle de acesso se quer ter), não de capacidade
técnica. O desenho do app desktop está em
[`superpowers/specs/2026-07-25-app-desktop-design.md`](superpowers/specs/2026-07-25-app-desktop-design.md)
e a sua justificativa técnica precisa ser relida à luz destes números.

## Como reproduzir

O ambiente PHP e os scripts de medição ficam fora do repositório (são ferramentas de
avaliação, não do produto). Passos: instalar `smalot/pdfparser` por Composer, extrair
os 15 PDFs com um dumper que trate `Do`, `/Contents` em array e ligue
`setDataTmFontInfoHasToBeIncluded(true)`, converter fragmentos em palavras por métrica
de glifo e alimentar `EE.run_profile`/`EE.run_generic` com o resultado.
