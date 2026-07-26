# Avaliação do MinerU como camada de leitura de PDF

**Pergunta:** o [MinerU](https://github.com/opendatalab/mineru) (OpenDataLab) melhora a
extração das cotações em relação ao PyMuPDF que o app usa hoje?

**Resposta curta:** **não para os PDFs de cotação que recebemos hoje** (todos com camada
de texto nativa) — ele é ligeiramente pior e ~3.000× mais lento. **Sim, e de forma
decisiva, para PDFs escaneados**, onde o PyMuPDF não extrai absolutamente nada. Fica
recomendado como *fallback* para esse caso, não como caminho principal.

---

## O que é o MinerU

Motor de *document parsing* que converte PDF/DOCX/PPTX/XLSX/imagens em **Markdown/JSON
prontos para LLM**: detecta layout, reconstrói tabelas em HTML, fórmulas em LaTeX e faz
OCR em 109 idiomas. Dois backends: `pipeline` (roda em CPU) e `vlm` (modelo de visão,
precisa de GPU com 8GB+).

**Licença e custo:** *MinerU Open Source License*, baseada na Apache 2.0 com condições
adicionais. **Não há paywall** — é gratuito e o código é aberto. Existe um serviço
hospedado opcional (mineru.net), mas nada do que usamos depende dele.

**Instalação (feita aqui em venv isolado, fora do projeto):**

```
python -m venv mineru-env
mineru-env/Scripts/python -m pip install "mineru[core]"
# Windows: HF_HUB_DISABLE_SYMLINKS=1 é obrigatório — sem isso o download dos
# modelos falha com "WinError 1314: o cliente não tem o privilégio necessário"
# (o cache do HuggingFace usa symlinks, que exigem modo desenvolvedor/admin).
HF_HUB_DISABLE_SYMLINKS=1 mineru -p <pdf-ou-pasta> -o <saida> -b pipeline
```

Requisitos reais: Python 3.10–3.12 no Windows, 16GB+ RAM, ~20GB de disco. A instalação
puxa PyTorch, transformers, OpenCV e ~1,5GB de modelos no primeiro uso.
`-l pt` **não existe** — português usa o modelo latino padrão (as opções de `-l` são
apenas ch/korean/arabic/cyrillic/etc.).

---

## Teste 1 — PDFs nativos (os 15 da amostra)

Mesmo modelo (`gpt-4o-mini`), mesmo prompt, mesmo schema. Muda só de onde vem o texto.

| camada de texto | campos preenchidos | ancoráveis no PDF | concordância | tempo |
|---|---|---|---|---|
| **PyMuPDF** (atual) | **25,5**/31 | **23,4** | **98%** | **0,02 s** |
| MinerU (pipeline) | 24,9/31 | 21,8 | 93% | ~60–90 s |

*"ancoráveis" = o valor devolvido é encontrado literalmente no PDF — é o critério que o
app usa para marcar um campo como "IA verificada" em vez de "confirmar".*

Por que o MinerU perde aqui:

- **Reordena o conteúdo.** A detecção de ordem de leitura embaralha formulários: no
  Bradesco, o bloco "DADOS DO CORRETOR" aparece antes do cabeçalho do documento.
- **Perde valores.** O CPF do segurado virou `CPF/CNPJ:` sem valor; `Sexo: Feminino`
  virou `Sexo:`. Célula fundida na reconstrução da tabela = dado que some.
- **Faz OCR mesmo quando há texto nativo** (backend `pipeline` rasteriza a página), o que
  introduz erros de reconhecimento: no modelo do veículo, um `I` maiúsculo virou `l`
  minúsculo.
- **Coordenadas só por bloco.** O `content_list` traz bbox da *tabela inteira*, não da
  célula. O app precisa de bbox **por valor** para destacar a origem de cada campo no
  assistente de conferência — isso o `get_text("words")` do PyMuPDF dá de graça.
- **Gera mais tokens** (12.661 vs 7.957 caracteres em média), encarecendo a chamada de IA.

## Teste 2 — PDF escaneado (sem camada de texto)

Rasterizamos o `mapfre.pdf` (2×) e regeramos um PDF só de imagens:

| camada de texto | caracteres extraídos |
|---|---|
| PyMuPDF | **0** — o app aborta com "documento vazio ou escaneado" |
| MinerU | **13.528** — contra 13.715 do mesmo PDF nativo (98,6%) |

Aqui não há comparação: o MinerU recupera praticamente todo o documento.

---

## Decisão

1. **Caminho principal continua PyMuPDF.** Mais preciso nos PDFs que recebemos, instantâneo,
   sem dependências pesadas e é o único que entrega bbox por palavra — requisito da
   proveniência e do assistente de conferência.
2. **MinerU entra como fallback de PDF escaneado** (item que já estava no `TODO.md`):
   quando a tokenização devolver texto vazio, passar o PDF pelo MinerU e seguir o
   pipeline com o texto resultante. Nesse caminho não haverá destaque visual por campo
   (só bbox de bloco), então todo campo assim extraído deve entrar como *pendente de
   confirmação*.
3. **Restrição de produção:** o MinerU não roda em hospedagem compartilhada de WordPress
   (PyTorch + ~1,5GB de modelos). Para o plugin, seria um serviço externo acionado sob
   demanda, não código embarcado no `.zip`.

## Teste 3 — representação do texto enviada à IA (hipótese descartada)

Como o motor determinístico ganhou muito ao trocar "linhas visuais" por "segmentos
rótulo→valor", testamos a mesma ideia na camada de IA: enviar `Rótulo: valor ; Rótulo:
valor` em vez do texto por linhas.

| representação | preenchidos | ancoráveis |
|---|---|---|
| linhas (atual) | 25,7/31 | 23,5 |
| segmentos rótulo→valor | 25,3/31 | 22,4 |

Sem ganho — o LLM já lida bem com a linha corrida, e a segmentação quebra o contexto de
tabelas largas. **Mantida a representação por linhas.**
