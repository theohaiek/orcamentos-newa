# smalot/pdfparser × PyMuPDF — medição e decisão

Data: 2026-07-25 · Conclusão: **o port do motor para PHP foi descartado.**

## O que estava em jogo

O produto seria um plugin WordPress, que roda PHP e não roda Python. O motor de
extração usa **PyMuPDF**, uma extensão C de Python, sem equivalente em PHP. O
candidato a substituto era `smalot/pdfparser`: PHP puro, sem binário externo, sem
`exec` — o único perfil que funciona em hospedagem compartilhada.

A pergunta era se ele entrega a informação de que o motor depende.

## Ambiente do teste

PHP 8.2.32 (NTS) + Composer 2.10.2 + `smalot/pdfparser` v2.12.5, contra os 15 PDFs de
amostra. Comparação com a saída do `extract_engine.tokenize()` atual.

**Compatibilidade com WordPress: aprovada.** Requer apenas `php >= 7.1`, `ext-zlib` e
`ext-iconv`, presentes em qualquer hospedagem. Instala por Composer e é vendorizável
no `.zip` do plugin.

**Ressalva de licença:** LGPL-3.0. Compatível com um plugin GPLv3+, incompatível com
GPLv2-only.

## Resultado

| arquivo | chars PyMuPDF | chars smalot | perda | frag. médio | âncoras | localizadas |
|---|---:|---:|---:|---:|---:|---:|
| aliro | 5.643 | **0** | **100%** | — | 23 | **0** |
| allianz | 11.125 | 11.862 | — | 9,3 | 12 | 12 |
| azul | 6.380 | 6.962 | — | 11,1 | 18 | 18 |
| bradesco | 8.267 | 4.839 | **41%** | 18,7 | 27 | 16 |
| darwin | 9.059 | 8.083 | 11% | 40,2 | 26 | 20 |
| hdi | 5.935 | 5.935 | 0% | **1,0** | 15 | **0** |
| itau | 6.832 | 7.473 | — | 11,2 | 23 | 22 |
| justos | 4.321 | 4.367 | — | **1,1** | 24 | **0** |
| mapfre | 6.562 | 7.446 | — | 20,2 | 30 | 30 |
| mitsui | 6.773 | 7.412 | — | 11,3 | 28 | 25 |
| porto | 7.240 | 7.947 | — | 11,7 | 26 | 23 |
| suhai | 4.035 | 4.516 | — | 16,3 | 16 | 16 |
| tokio | 8.684 | 9.761 | — | 20,9 | 29 | 29 |
| yelum | 5.366 | **0** | **100%** | — | 14 | **0** |
| zurich | 4.767 | 5.469 | — | 32,7 | 23 | 23 |
| **total** | **100.989** | **92.072** | **9%** | | **334** | **234 (70%)** |

"Âncoras" são os rótulos que os 15 perfis dedicados realmente usam para localizar cada
campo. Se o rótulo não existe como texto contíguo, não há o que ancorar.

## As quatro falhas

**1. Dois PDFs sem posição alguma.** Em `aliro` e `yelum`, `getText()` devolve o texto
(6.661 e 6.326 caracteres), mas `getDataTM()` devolve **zero** fragmentos. Um motor
posicional não tem o que fazer com isso.

**2. Dois PDFs fragmentados por caractere.** Em `hdi`, 6.839 fragmentos para 7.070
caracteres — cada letra é um fragmento, com a escala da fonte no lugar da largura.
`justos` idem. Nenhum rótulo existe como unidade.

**3. `bradesco` perde 41% do texto.** 8.267 → 4.839 caracteres.

**4. `darwin` corrompe bytes.** Um fragmento sai com UTF-8 inválido; sem
`JSON_INVALID_UTF8_SUBSTITUTE`, `json_encode` devolve `false` silenciosamente.

## A tentativa de recuperação

Um motor PHP real não usaria os fragmentos crus — reconstruiria linhas agrupando por
`y` e concatenando por `x`, inferindo espaços. Implementado com heurística de limiar
pela mediana dos avanços de cada linha (o melhor caso possível, já que o `smalot` não
expõe largura de glifo):

| | âncoras localizadas |
|---|---:|
| fragmentos crus | 70% |
| linhas reconstruídas | **75%** |

`hdi` sobe de 0 para 4 de 15; `justos`, de 0 para 10 de 24. `aliro` e `yelum` seguem em
zero — não há coordenada para reconstruir.

## O problema que decide

Mesmo os 75% recuperados são **linha visual**. A API do `smalot` (`getText`,
`getTextArray`, `getDataTm`, `getTextXY`) expõe posição por operador `Tm` e nada mais:
**não há o nível de bloco**.

E o bloco é exatamente o que produziu o salto de 33% para 81%. Ler "o valor à direita
do rótulo" pela linha visual invade a coluna vizinha num formulário multi-coluna —
`Veículo: Valor de Mercado Referenciado  Dias Paralisação: 0,00  D.M.: 100.000,00`.
Foi a causa raiz corrigida na v0.3, e é o que o `smalot` não permite corrigir.

## Decisão

Port descartado. A estimativa realista era **~50% de cobertura determinística** contra
81%, com 4 dos 15 layouts quebrados — e sem caminho de melhoria, porque a limitação
está na informação que a biblioteca expõe, não no esforço de implementação.

O motor fica em Python. O invólucro deixa de ser um plugin WordPress e passa a ser um
aplicativo desktop: ver [`superpowers/specs/2026-07-25-app-desktop-design.md`](superpowers/specs/2026-07-25-app-desktop-design.md).
