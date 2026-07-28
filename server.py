# -*- coding: utf-8 -*-
"""
Servidor da aplicação — Orçamentos NEWA
http.server (stdlib), sem dependência de framework. Abre o navegador sozinho.

Rode:  python server.py          (ou, da pasta-pai, python server.py)
Abre:  http://localhost:8080/

Dados de execução ficam FORA do repositório, na pasta-pai:
  ../.devdata/   usuários, config (inclusive a chave da OpenAI), uploads

API:
  POST /api/login  /api/logout            GET /api/me
  GET/POST /api/config                    GET/POST /api/insurers
  GET/POST /api/users  PUT/DELETE /api/users/<u>
  POST /api/extract   (multipart PDF -> perfil + genérico + IA -> campos)
"""
import os, sys, json, io, re, hmac, hashlib, secrets, threading, webbrowser, mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, unquote, parse_qs

import updater

PORT = 8080
REPO = os.path.dirname(os.path.abspath(__file__))   # o motor mora no repositório
HERE = os.path.dirname(REPO)                        # pasta-pai: .env e .devdata
ASSETS = os.path.join(REPO, "orcamentos-newa", "assets")
DATA = os.path.join(REPO, "data")
# Onde ficam usuários, configuração e uploads. Em desenvolvimento, na pasta-pai;
# instalado, na pasta do usuário — a instalação em si pode estar em `Program Files`,
# onde o processo não tem permissão de escrita.
if getattr(sys, "frozen", False):
    DEV = os.path.join(os.environ.get("LOCALAPPDATA") or os.path.expanduser("~"),
                       "OrcamentosNEWA")
else:
    DEV = os.path.join(HERE, ".devdata")
os.makedirs(DEV, exist_ok=True)
UPLOADS = os.path.join(DEV, "uploads")          # PDFs enviados + páginas rasterizadas
os.makedirs(UPLOADS, exist_ok=True)

# A chave da OpenAI tem UMA fonte: o campo em Configurações, digitado na máquina de
# quem usa e guardado em `config.json`, fora do repositório. Não vem de `.env`, não
# vem de variável de ambiente, não tem padrão embutido.
#
# Isso existe porque a chave anterior vazou: as rotas /assets e /data eram servidas
# antes do login e sem contenção de caminho, então `/assets/../../../.env` entregava
# o arquivo inteiro. O buraco do caminho já foi fechado, mas enquanto houvesse uma
# chave em disco fora do controle de quem usa, um erro parecido voltaria a expor a
# chave de outra pessoa. Sem cópia no ambiente de desenvolvimento não há o que vazar
# daqui, e a cota é sempre da conta do cliente.

# =============================== persistência ===============================
def jread(path, default):
    # utf-8-sig, e não utf-8: o Bloco de Notas, o PowerShell e boa parte das
    # ferramentas do Windows gravam um BOM no começo do arquivo. Com `utf-8` puro esse
    # BOM vira erro de parsing, e como a falha aqui é silenciosa o app voltava a TODOS
    # os padrões sem avisar — os dados da corretora sumiam da proposta e ninguém sabia
    # por quê. `utf-8-sig` lê com BOM e sem BOM.
    try:
        return json.load(open(path, encoding="utf-8-sig"))
    except Exception:
        return default

def jwrite(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

# Modelo padrão da camada de fallback (IA).
#
# Já foi `gpt-5-nano`, escolhido por uma comparação enviesada: ela media precisão
# apenas sobre os campos que o modelo preencheu, o que premia quem deixa em branco.
# Medido de novo por COBERTURA CORRETA sobre os 31 campos, o nano faz 44% e o
# `gpt-4o-mini`, 69,4% — dois terços de diferença que a métrica antiga escondia.
#
# O custo por chamada do 4o-mini é maior, e pesa pouco: os perfis determinísticos já
# entregam ~80% sozinhos, então a IA roda sobre um punhado de campos por documento.
DEFAULT_MODEL = "gpt-4o-mini"

# Só vale para modelos de raciocínio (ver `_is_reasoning`). O 4o-mini não é um deles:
# recebe `temperature=0` no lugar. Fica configurável porque a escolha do modelo é.
DEFAULT_EFFORT = "low"

# Config gravada antes desta mudança continua pedindo o nano — trocar o padrão não
# alcança quem já tem o app instalado. A migração roda uma vez e respeita quem
# escolher o nano de propósito depois dela.
MIGRACAO_MODELO = ("gpt-5-nano", DEFAULT_MODEL, "migrado_modelo_2026_07")

# Perfis baixados pela atualização automática. Ficam FORA da instalação porque
# em `Program Files` o processo não tem escrita; sobrepõem os de `data/profiles`
# por nome de arquivo (ver extract_engine.load_profiles).
PROFILES_LOCAL = os.path.join(DEV, "profiles")

USERS_F = os.path.join(DEV, "users.json")
CONFIG_F = os.path.join(DEV, "config.json")
INS_F = os.path.join(DEV, "insurers.json")
TPL_F = os.path.join(DEV, "template.json")

def hash_pw(pw, salt=None):
    salt = salt or secrets.token_hex(8)
    h = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 120000).hex()
    return f"{salt}${h}"

def check_pw(pw, stored):
    try:
        salt, h = stored.split("$", 1)
        return hmac.compare_digest(hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 120000).hex(), h)
    except Exception:
        return False

def seed():
    if not os.path.exists(USERS_F):
        jwrite(USERS_F, {"users": [{"username": "Madu", "name": "Madu", "role": "admin", "pw": hash_pw("123")}]})
    if not os.path.exists(CONFIG_F):
        jwrite(CONFIG_F, {
            "model": DEFAULT_MODEL,
            "reasoning_effort": DEFAULT_EFFORT,
            "openai_key": "",          # preenchido só pela tela de Configurações
            # URL base da atualização automática dos perfis. Vazia = desligada.
            # Aceita tanto o raw de um repositório público quanto um webhook do
            # n8n com o repositório privado atrás — o cliente é o mesmo.
            "update_url": os.environ.get("UPDATE_URL", ""),
            "corretora": {
                "nome": "NEWA Seguros", "email": "newaseguros@newaseguros.com.br",
                "site": "newaseguros.com.br", "telefone": "(11) 4040-3665",
                "whatsapp": "", "endereco": ""
            }
        })
    if not os.path.exists(INS_F):
        jwrite(INS_F, jread(os.path.join(DATA, "insurers.json"), {"insurers": []}))
seed()

def get_users():   return jread(USERS_F, {"users": []})["users"]
def set_users(u):  jwrite(USERS_F, {"users": u})
def get_config():
    c = jread(CONFIG_F, {})
    de, para, marca = MIGRACAO_MODELO
    # `c` vazio significa "não consegui ler" tanto quanto "não existe" — jread engole a
    # exceção. Gravar por cima nesse estado apaga a configuração de quem tem o arquivo
    # ilegível por um motivo bobo (um BOM, uma vírgula sobrando). Migração só mexe em
    # config que foi lida de verdade.
    if c and not c.get(marca):
        c[marca] = True
        if c.get("model") == de:
            c["model"] = para
        set_config(c)
    return c

def set_config(c): jwrite(CONFIG_F, c)
def get_insurers():return jread(INS_F, {"insurers": []})["insurers"]
def set_insurers(i):jwrite(INS_F, {"insurers": i})
def get_template(): return jread(TPL_F, {})
def set_template(t): jwrite(TPL_F, t)

# =============================== sessões ===============================
SESS = {}  # token -> username
def new_session(username):
    t = secrets.token_hex(24); SESS[t] = username; return t

# =============================== extração IA ===============================
CAMPOS = {
    "seguradora": "Nome da SEGURADORA (companhia que emite a apólice: Allianz, Porto, Itaú, Bradesco, HDI, Suhai, etc.). NUNCA a corretora.",
    "segurado": "Nome completo do segurado",
    "veiculo": "Marca + modelo + versão do veículo em uma linha",
    "ano_modelo": "Ano/Modelo (ex: 2027 ou 2026/2027)",
    "principal_condutor": "Nome do principal condutor",
    "data_proposta": "Data da proposta/cotação (AAAA-MM-DD)",
    "validade": "Validade da proposta",
    "uso_veiculo": "Uso do veículo (ex: PARTICULAR)",
    "valor_fipe": "Valor FIPE do veículo (ex: R$ 270.216,00)",
    "condutores_18_26": "Há condutores entre 18 e 26 anos? (Sim/Não)",
    "cep_circulacao": "CEP de circulação/pernoite",
    "colisao_incendio_roubo": "Cobertura Colisão/Incêndio/Roubo (ex: 100% FIPE, Valor de mercado)",
    "rcf_danos_materiais": "RCF Danos Materiais a Terceiros (LMI, ex: R$ 100.000,00)",
    "rcf_danos_pessoais": "RCF Danos Pessoais/Corporais a Terceiros (LMI)",
    "acidente_pessoal_passageiro": "Acidente Pessoal por Passageiro (APP, LMI)",
    "morte_pessoal_passageiro": "Morte por Passageiro (LMI)",
    "km_reboque": "Quilometragem/KM de Reboque/Guincho (ex: 500 KM, KM Ilimitado)",
    "diarias_carro_reserva": "Diárias de carro reserva (ex: 15 dias, Não Contratado)",
    "franquia_veiculo": "Franquia do veículo / franquia da cobertura compreensiva",
    "para_brisas": "Franquia/cobertura de Para-Brisas ou Vidros",
    "farois": "Franquia/cobertura de Faróis",
    "lanternas": "Franquia/cobertura de Lanternas",
    "retrovisores": "Franquia/cobertura de Retrovisores",
    "reparo_para_choque": "Reparo/Troca de Para-Choque",
    "reparo_amassados": "Reparo de amassados/martelinho de ouro",
    "protecao_pneu_roda_suspensao": "Proteção de Pneu/Roda/Suspensão",
    "assistencia_residencial": "Seguro com Assistência Residencial (Sim/Não)",
    "a_vista": "Prêmio total à vista (ex: R$ 8.690,70)",
    "parc_4x": "Valor de CADA parcela em 4x sem juros",
    "parc_6x": "Valor de CADA parcela em 6x sem juros",
    "parc_10x": "Valor de CADA parcela em 10x sem juros",
}
def schema(keys=None):
    ks = keys if keys else list(CAMPOS)
    props = {k: {"type": ["string", "null"], "description": CAMPOS[k]} for k in ks}
    props["campos_nao_encontrados"] = {"type": "array", "items": {"type": "string"},
        "description": "Chaves dos campos NÃO encontrados no documento (deixados null)."}
    return {"type": "object", "properties": props, "required": list(props.keys()), "additionalProperties": False}

# Campos que descrevem uma COBERTURA/SERVIÇO: se o documento não menciona, a resposta
# certa é "Não Contratado" (a ausência É a informação, e o comparativo precisa dela).
# Os demais são DADOS do risco/proposta: ausência = null, nunca um palpite.
COBERTURAS = {
    "colisao_incendio_roubo", "rcf_danos_materiais", "rcf_danos_pessoais",
    "acidente_pessoal_passageiro", "morte_pessoal_passageiro", "km_reboque",
    "diarias_carro_reserva", "franquia_veiculo", "para_brisas", "farois", "lanternas",
    "retrovisores", "reparo_para_choque", "reparo_amassados",
    "protecao_pneu_roda_suspensao", "assistencia_residencial",
}

SYS = (
    "Você extrai dados de cotações/orçamentos de seguro auto brasileiros e os normaliza num schema fixo "
    "para um comparativo entre seguradoras. Regras: "
    "1) Use EXATAMENTE os valores do documento, em moeda BR (R$ 1.234,56). "
    "2) NUNCA invente valores nem deduza o que o documento não diz. "
    "3) Ausência tem DUAS respostas diferentes, conforme o tipo do campo: "
    "(a) campos de COBERTURA ou SERVIÇO (coberturas, limites, franquias, assistências) — se o documento "
    "não menciona aquela cobertura, ela não está contratada: responda 'Não Contratado', NUNCA null. "
    "Essa informação é essencial no comparativo entre seguradoras. "
    "(b) campos de DADOS do risco ou da proposta (nomes, veículo, datas, CEP, valor FIPE, prêmios, parcelas) — "
    "se o dado não estiver no documento, responda null e liste a chave em campos_nao_encontrados. "
    "4) 'seguradora' é a companhia de seguro, nunca a corretora; cuidado com a seguradora ANTERIOR "
    "citada em renovações ('congênere') e com parceiros citados no rodapé. "
    "5) Corrija acentuação/encoding para português correto (ex: 'Não', não 'N�o'). "
    "6) Em franquias/coberturas com valor monetário, retorne SÓ o valor (ex: 'R$ 850,00'); "
    "adicione uma qualificação curta só se essencial (ex: 'R$ 6.884,90 (Reduzida)'). Seja conciso. "
    "7) Quando houver variantes de um item (farol convencional/xênon/LED), use a CONVENCIONAL."
)

def clean_text(t):
    return t.replace("�", "").strip()

PROFILES_DIR = os.path.join(DATA, "profiles")

def _is_reasoning(model):
    return model.startswith("gpt-5") or model.startswith("o1") or model.startswith("o3") or model.startswith("o4")

def _ai_extract(texto, filename, cfg, key, only_keys=None):
    """Camada 3: IA. Extrai só os campos pedidos (only_keys) para ser rápida/barata."""
    from openai import OpenAI
    client = OpenAI(api_key=key)
    model = cfg.get("model") or DEFAULT_MODEL
    effort = cfg.get("reasoning_effort", DEFAULT_EFFORT)
    kw = dict(
        model=model,
        messages=[{"role": "system", "content": SYS},
                  {"role": "user", "content": f"Documento (texto extraído do PDF '{filename}'):\n\n{texto}"}],
        response_format={"type": "json_schema", "json_schema": {"name": "cotacao_seguro", "strict": True, "schema": schema(only_keys)}},
    )
    if _is_reasoning(model):
        kw["reasoning_effort"] = effort      # extração é leitura, não raciocínio profundo
    else:
        kw["temperature"] = 0

    def _call(k):
        return client.chat.completions.create(**k)

    try:
        r = _call(kw)
    except Exception as e:
        # famílias novas (gpt-5.1+) recusam 'minimal'; modelos sem raciocínio recusam
        # o parâmetro inteiro. Degrada em vez de falhar a extração toda.
        msg = str(e)
        if "reasoning_effort" in msg and "reasoning_effort" in kw:
            kw2 = dict(kw)
            if kw2["reasoning_effort"] != "low":
                kw2["reasoning_effort"] = "low"
            else:
                kw2.pop("reasoning_effort")
            r = _call(kw2)
        elif "temperature" in msg and "temperature" in kw:
            kw2 = dict(kw); kw2.pop("temperature")
            r = _call(kw2)
        else:
            raise
    d = json.loads(r.choices[0].message.content)
    d.pop("campos_nao_encontrados", None)
    return d

# Termos que identificam o RÓTULO de cada campo no documento. Usados para exigir que
# um valor devolvido pela IA esteja perto do rótulo certo — sem isso, "verificado" só
# significava "esta string existe em algum lugar do PDF", o que aceitava praticamente
# qualquer alucinação (um valor como "R$ 200.000,00" existe em quase toda cotação).
_FIELD_TERMS = {
    "seguradora": ["seguradora", "companhia", "cia de seguros", "seguros s.a", "apolice"],
    "segurado": ["segurado", "proponente", "nome do segurado", "cliente"],
    "veiculo": ["veiculo", "modelo", "marca", "descricao do veiculo", "automovel"],
    "ano_modelo": ["ano modelo", "ano/modelo", "ano fabricacao", "ano do modelo", "ano"],
    "principal_condutor": ["principal condutor", "condutor principal", "condutor"],
    "data_proposta": ["data da proposta", "data da cotacao", "data do calculo",
                      "data de emissao", "emissao", "data"],
    "validade": ["validade", "valida ate", "vigencia", "proposta valida"],
    "uso_veiculo": ["uso do veiculo", "uso", "finalidade", "utilizacao"],
    # NÃO usar "fipe" solto nem "valor de mercado": "100% FIPE" e "Valor de Mercado
    # Referenciado" são o rótulo da COBERTURA de casco, e ficam ao lado do prêmio —
    # era assim que o prêmio do casco entrava aqui carimbado como verificado.
    # "tabela fipe" também sai: aparece descrevendo a BASE da cobertura ("pagamos 100%
    # da Tabela FIPE"), não o valor do veículo.
    "valor_fipe": ["valor fipe", "valor da fipe", "valor do bem",
                   "valor de mercado do veiculo", "valor do veiculo"],
    "condutores_18_26": ["18 e 26", "18 a 26", "condutores entre", "jovem condutor",
                         "condutor de 18"],
    "cep_circulacao": ["cep", "pernoite", "circulacao", "endereco de risco"],
    "colisao_incendio_roubo": ["colisao", "incendio", "roubo", "compreensiva", "casco",
                               "fipe"],
    "rcf_danos_materiais": ["danos materiais", "rcf", "danos a terceiros", "dm",
                            "responsabilidade civil"],
    "rcf_danos_pessoais": ["danos pessoais", "danos corporais", "rcf", "dc",
                           "responsabilidade civil"],
    "acidente_pessoal_passageiro": ["acidente pessoal", "app", "passageiro", "invalidez"],
    "morte_pessoal_passageiro": ["morte", "app", "passageiro"],
    "km_reboque": ["reboque", "guincho", "km", "assistencia", "quilometragem"],
    "diarias_carro_reserva": ["carro reserva", "veiculo reserva", "diarias", "reserva"],
    "franquia_veiculo": ["franquia"],
    "para_brisas": ["para-brisa", "para brisa", "parabrisa", "vidro", "vidros"],
    "farois": ["farol", "farois"],
    "lanternas": ["lanterna", "lanternas"],
    "retrovisores": ["retrovisor", "retrovisores", "espelho"],
    "reparo_para_choque": ["para-choque", "para choque", "parachoque"],
    "reparo_amassados": ["amassado", "martelinho", "funilaria", "reparo rapido"],
    "protecao_pneu_roda_suspensao": ["pneu", "roda", "suspensao"],
    "assistencia_residencial": ["residencial", "assistencia residencia", "casa",
                                "assistencia domiciliar"],
    "a_vista": ["a vista", "premio total", "preco total", "valor total", "total geral",
                "premio liquido"],
    # "parcel" solto casava com qualquer tabela de parcelamento e validava a parcela
    # errada; o marcador tem que ser o número de vezes.
    "parc_4x": ["4x", "4 x", "4 vezes", "4 parcelas", "em 4"],
    "parc_6x": ["6x", "6 x", "6 vezes", "6 parcelas", "em 6"],
    "parc_10x": ["10x", "10 x", "10 vezes", "10 parcelas", "em 10"],
}

_ANCHOR_CACHE = {}

def _field_terms(key):
    """Termos-rótulo do campo: os curados acima + as âncoras reais dos perfis."""
    import extract_engine as EE
    if not _ANCHOR_CACHE:
        for prof in EE.load_profiles(PROFILES_DIR, PROFILES_LOCAL):
            for k, spec in (prof.get("fields") or {}).items():
                for s in (spec if isinstance(spec, list) else [spec]):
                    if isinstance(s, dict) and s.get("anchor"):
                        _ANCHOR_CACHE.setdefault(k, set()).add(EE.norm(s["anchor"]))
        _ANCHOR_CACHE.setdefault("__loaded__", set())
    terms = set(_ANCHOR_CACHE.get(key, set()))
    terms.update(EE.norm(t) for t in _FIELD_TERMS.get(key, []))
    # Termo curto ou puramente numérico não ancora nada: a âncora "10" de um perfil
    # casa dentro de "100% FIPE" e valida a parcela errada.
    return {t for t in terms if len(t) >= 3 and not t.replace(" ", "").isdigit()}


def _value_in(ntext, nv):
    """Contém o valor como TOKEN INTEIRO, não como pedaço de outro número.

    Sem isto, o valor "15" casa dentro de "15.000,00" e o app aponta a proveniência
    para um número que não tem relação com o campo.
    """
    if not nv:
        return False
    i = ntext.find(nv)
    while i >= 0:
        antes = ntext[i - 1] if i > 0 else " "
        depois = ntext[i + len(nv)] if i + len(nv) < len(ntext) else " "
        if not (antes.isdigit() or antes in ".,") and not (depois.isdigit() or depois in ".,"):
            return True
        i = ntext.find(nv, i + 1)
    return False


def _locate_value(pages, value, key=None):
    """Ancora um valor da IA nos tokens reais do PDF.

    Devolve `anchored=True` somente quando o valor foi encontrado E a região onde ele
    está carrega um rótulo do campo (na mesma linha, até 2 linhas acima — cabeçalho de
    coluna — ou 1 abaixo). Encontrar a string em qualquer lugar do documento NÃO é
    verificação: é o que deixava passar valor certo no campo errado.
    """
    import extract_engine as EE
    if not value:
        return None
    termos = _field_terms(key) if key else set()
    variants = [value, value.replace("R$", "").strip(), re.sub(r"[^\d.,%]", "", value)]
    achado_sem_rotulo = None
    for var in variants:
        nv = EE.norm(var)
        if len(nv) < 2:
            continue
        for page in pages:
            linhas = page["lines"]
            for i, line in enumerate(linhas):
                if not _value_in(line["ntext"], nv):
                    continue
                sub = EE._value_tokens(line["tokens"], var) or line["tokens"]
                hit = {"page": page["n"], "bbox": EE._tokens_bbox(sub),
                       "snippet": line["text"], "anchored": False}
                if termos:
                    janela = " | ".join(l["ntext"] for l in linhas[max(0, i - 2): i + 2])
                    if any(t in janela for t in termos):
                        hit["anchored"] = True
                        return hit
                    if achado_sem_rotulo is None:
                        achado_sem_rotulo = hit
                else:
                    return hit
    return achado_sem_rotulo

_ABSENCE = {
    "nao contratado", "nao contratada", "nao contratados", "nao contratadas",
    "nao possui", "nao incluido", "nao incluida", "sem cobertura", "nao aplicavel",
    "nao informado", "nao consta", "nao ha",
}
# "-", "--", "n/a" e "na" foram REMOVIDOS: aparecem como conteúdo legítimo de célula
# nestes PDFs, então tratá-los como "a cobertura não existe" transformava um traço de
# tabela numa afirmação categórica ao cliente.

_NULL_TOKENS = {"null", "none", "nulo", "undefined", "nan", "n\\a"}

def _is_null_token(value):
    """O modelo devolveu a STRING 'null' em vez de JSON null?

    Acontece com a família gpt-5 sob schema estrito. Sem este filtro, o texto
    'null' vira o valor do campo e chega ao documento entregue ao cliente.
    """
    import extract_engine as EE
    return EE.norm(str(value or "")).strip(" .:\"'") in _NULL_TOKENS

def _is_absence(value):
    """O valor afirma que a cobertura NÃO existe no documento?

    Esse tipo de resposta jamais aparece literalmente no PDF (é uma conclusão, não
    uma citação), então a verificação por string-match sempre falharia e o campo
    cairia em "confiança baixa" — poluindo a conferência com alertas falsos.
    """
    import extract_engine as EE
    return EE.norm(str(value or "")).strip(" .:") in _ABSENCE


def _absence_supported(pages, key):
    """O documento realmente NÃO menciona esta cobertura?

    Antes de escrever "não consta no PDF" — uma afirmação categórica que o usuário lê
    como verificada — é preciso conferir. Se um rótulo do campo aparece no documento,
    a cobertura está lá e a resposta da IA precisa de conferência humana, não de um
    selo de verificada.
    """
    termos = _field_terms(key)
    if not termos:
        return False
    blob = " | ".join(l["ntext"] for p in pages for l in p["lines"])
    return not any(t in blob for t in termos)

# --------------------------------------------------------------- multi-oferta
# Rótulos que só aparecem numa linha de TOTAL da cotação.
_TOTAL_TERMS = ["preco total", "premio total", "premio liquido", "total a vista",
                "premio a vista", "valor total", "total geral", "total a pagar"]
_MOEDA_RE = re.compile(r"\b\d{1,3}(?:\.\d{3})*,\d{2}\b")

# Campos cujo valor MUDA conforme a oferta escolhida. Os de identificação
# (segurado, veículo, CEP, datas) são os mesmos em todas as ofertas.
_CAMPOS_POR_OFERTA = {
    "colisao_incendio_roubo", "rcf_danos_materiais", "rcf_danos_pessoais",
    "acidente_pessoal_passageiro", "morte_pessoal_passageiro", "km_reboque",
    "diarias_carro_reserva", "franquia_veiculo", "para_brisas", "farois",
    "lanternas", "retrovisores", "reparo_para_choque", "reparo_amassados",
    "protecao_pneu_roda_suspensao", "assistencia_residencial",
    "a_vista", "parc_4x", "parc_6x", "parc_10x",
}


def _num_br(s):
    try:
        return float(s.replace(".", "").replace(",", "."))
    except ValueError:
        return 0.0


def detect_offers(pages):
    """O documento cota MAIS DE UMA oferta lado a lado?

    Uma cotação multi-oferta (Allianz traz 6 planos, HDI traz 2) não tem "o" valor:
    tem um por plano. Escolher a coluna da esquerda em silêncio já publicou uma
    Allianz como "Colisão/Incêndio/Roubo 100% FIPE" quando o plano daquela coluna é
    "Roubo e Furto" e o próprio PDF diz que não vale para colisão.

    Critérios para não confundir com outras linhas de valores múltiplos:
      - o rótulo de TOTAL tem que estar no INÍCIO da linha (senão pega composição
        de prêmio: "Assist. Funeral: 0,00 TOTAL A PAGAR: 5.848,32");
      - ao menos 2 valores DISTINTOS e não-zero (aliro/yelum repetem o mesmo total
        em 4 colunas de forma de pagamento — não são ofertas diferentes);
      - todos na mesma ordem de grandeza (descarta decomposição prêmio/IOF/desconto,
        como a linha do darwin).
    """
    melhor = None
    for p in pages:
        for l in p["lines"]:
            nt = l["ntext"]
            cabeca = nt[:28]
            if not any(t in cabeca for t in _TOTAL_TERMS):
                continue
            vals = [v for v in _MOEDA_RE.findall(l["text"])]
            nums = sorted({_num_br(v) for v in vals if _num_br(v) > 0})
            if len(nums) < 2:
                continue
            if nums[-1] / nums[0] > 10:
                continue                      # composição de prêmio, não ofertas
            if melhor is None or len(nums) > melhor["n"]:
                melhor = {"n": len(nums), "valores": [f"{x:,.2f}".replace(",", "@")
                                                      .replace(".", ",").replace("@", ".")
                                                      for x in nums],
                          "pagina": p["n"], "trecho": l["text"][:160]}
    return melhor


def save_upload(pdf_bytes):
    """Guarda o PDF para servir imagens de página no assistente de confirmação."""
    did = hashlib.sha1(pdf_bytes).hexdigest()[:16]
    p = os.path.join(UPLOADS, did + ".pdf")
    if not os.path.exists(p):
        open(p, "wb").write(pdf_bytes)
    return did

def render_page_png(did, pno, scale=2.0):
    """Rasteriza uma página do PDF guardado (imagem real da fonte). Cacheia."""
    import fitz
    if not re.fullmatch(r"[0-9a-f]{16}", did or ""):
        return None
    src = os.path.join(UPLOADS, did + ".pdf")
    if not os.path.exists(src):
        return None
    cache = os.path.join(UPLOADS, f"{did}-p{pno}-{int(scale*10)}.png")
    if os.path.exists(cache):
        return open(cache, "rb").read()
    doc = fitz.open(src)
    if pno < 1 or pno > doc.page_count:
        return None
    pix = doc[pno - 1].get_pixmap(matrix=fitz.Matrix(scale, scale))
    data = pix.tobytes("png")
    open(cache, "wb").write(data)
    return data

def render_crop_png(did, pno, x0, y0, x1, y1, scale=3.0):
    """Recorta uma região (em pontos do PDF) e devolve PNG nítido. Robusto: sem CSS."""
    import fitz
    if not re.fullmatch(r"[0-9a-f]{16}", did or ""):
        return None
    src = os.path.join(UPLOADS, did + ".pdf")
    if not os.path.exists(src):
        return None
    doc = fitz.open(src)
    if pno < 1 or pno > doc.page_count:
        return None
    page = doc[pno - 1]
    r = page.rect
    clip = fitz.Rect(max(r.x0, x0), max(r.y0, y0), min(r.x1, x1), min(r.y1, y1))
    if clip.width <= 1 or clip.height <= 1:
        return None
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), clip=clip)
    return pix.tobytes("png")

def extract_pdf(pdf_bytes, filename=""):
    import extract_engine as EE
    doc_id = save_upload(pdf_bytes)
    pages = EE.tokenize(pdf_bytes)
    texto = clean_text("\n".join(l["text"] for p in pages for l in p["lines"]))

    # --- Validação de legibilidade, POR PÁGINA ---------------------------------
    # O guarda antigo olhava só o total de caracteres do documento. Um PDF com a
    # primeira página nativa e o resto escaneado passava direto, o perfil casava e o
    # app entregava 10 de 31 campos com a mesma tela verde de um documento completo.
    sem_texto = [p["n"] for p in pages if not p["tokens"]]
    if len(sem_texto) == len(pages):
        raise RuntimeError("Não foi possível ler texto deste PDF: ele é uma imagem "
                           "(documento escaneado). Envie a versão digital da cotação.")
    if len(texto) < 40:
        raise RuntimeError("Não foi possível ler texto do PDF (documento vazio ou escaneado).")

    fields = {k: None for k in CAMPOS}
    provenance = {}
    consumed = []
    profile_used = False
    profile_id = None
    prof_fail = 0
    prof_total = 0

    # --- Camada 1: determinístico por perfil ---
    all_profiles = EE.load_profiles(PROFILES_DIR, PROFILES_LOCAL)
    prof = EE.match_profile(pages, all_profiles)
    if prof:
        profile_used = True
        profile_id = prof["id"]
        res = EE.run_profile(pages, prof)
        prof_total = len(prof.get("fields", {}))
        prof_fail = prof_total - len(res["fields"])
        for k, v in res["fields"].items():
            fields[k] = v
            provenance[k] = res["provenance"][k]
        consumed = list(res["consumed"])

    # --- Camada 1b: genérico (rótulos inequívocos) p/ o que o perfil não pegou ---
    gen = EE.run_generic(pages, all_profiles, set(k for k in CAMPOS if fields.get(k)))
    for k, v in gen["fields"].items():
        fields[k] = v
        provenance[k] = gen["provenance"][k]
    consumed += gen["consumed"]
    if gen["fields"]:
        profile_used = True  # houve extração determinística

    # --- Camada 3: IA só para o que faltou (ou tudo, se não houve perfil) ---
    missing_keys = [k for k in CAMPOS if not fields.get(k)]
    ai_used = False
    ai_error = None
    if missing_keys:
        cfg = get_config()
        key = cfg.get("openai_key", "")
        if key:
            try:
                ai = _ai_extract(texto, filename, cfg, key, only_keys=missing_keys)
                ai_used = True
                for k in missing_keys:
                    v = (ai.get(k) or "").strip() if isinstance(ai.get(k), str) else ai.get(k)
                    if not v or _is_null_token(v):
                        continue     # alguns modelos devolvem a STRING "null" em vez de JSON null
                    fields[k] = v
                    src = _locate_value(pages, v, k)
                    if src and src.get("anchored"):
                        # valor achado no documento E junto de um rótulo do campo
                        provenance[k] = {"value": v, "method": "ai", "anchor": None,
                                         "page": src["page"], "bbox": src["bbox"],
                                         "snippet": src["snippet"], "confidence": "verificada"}
                        consumed.append((src["page"], tuple(round(x) for x in src["bbox"])))
                    elif _is_absence(v) and _absence_supported(pages, k):
                        # "Não Contratado" nunca casa literalmente com o PDF — é a
                        # afirmação de que a cobertura não existe ali. Só aceitamos essa
                        # afirmação depois de conferir que nenhum rótulo do campo aparece
                        # no documento.
                        provenance[k] = {"value": v, "method": "ausente", "anchor": None,
                                         "page": None, "bbox": None,
                                         "snippet": "Nenhuma menção a esta cobertura foi encontrada no documento.",
                                         "confidence": "verificada"}
                    elif src:
                        # a string existe no PDF, mas longe de qualquer rótulo do campo:
                        # provavelmente é o valor de OUTRO campo. Precisa de conferência.
                        provenance[k] = {"value": v, "method": "ai", "anchor": None,
                                         "page": src["page"], "bbox": src["bbox"],
                                         "snippet": src["snippet"], "confidence": "baixa",
                                         "motivo": "valor encontrado no documento, mas não junto ao rótulo deste campo"}
                    else:
                        provenance[k] = {"value": v, "method": "ai", "anchor": None,
                                         "page": None, "bbox": None, "snippet": v,
                                         "confidence": "baixa",
                                         "motivo": "valor não localizado no texto do documento"}
            except Exception as e:
                ai_error = str(e)
        elif not profile_used:
            raise RuntimeError("Chave OpenAI não configurada e nenhum perfil reconheceu este PDF.")

    insurer_id = detect_insurer(fields.get("seguradora"), filename, texto)
    missing = [k for k in CAMPOS if not fields.get(k)]
    drift = bool(profile_used and prof_total and (prof_fail / prof_total) > 0.4)

    # --- Multi-oferta: rebaixar o que depende da oferta escolhida --------------
    ofertas = detect_offers(pages)
    if ofertas:
        for k in _CAMPOS_POR_OFERTA:
            p = provenance.get(k)
            if p and fields.get(k):
                p["confidence"] = "baixa"
                p["motivo"] = (f"o documento cota {ofertas['n']} ofertas lado a lado e "
                               f"este valor foi lido da primeira coluna — confirme se é "
                               f"a oferta correta")

    # --- Avisos: tudo que o usuário PRECISA ver antes de gerar ----------------
    # Regra do produto: nunca entregar documento incompleto ou mal mapeado em
    # silêncio. Cada aviso traz nível, mensagem pronta e o dado que o originou.
    avisos = []
    if sem_texto:
        avisos.append({
            "nivel": "erro", "codigo": "paginas_sem_texto",
            "mensagem": (f"{len(sem_texto)} de {len(pages)} páginas deste PDF são imagem "
                         f"(páginas {', '.join(map(str, sem_texto))}) e não puderam ser "
                         f"lidas. Os campos dessas páginas estão faltando."),
            "paginas": sem_texto})
    if ofertas:
        avisos.append({
            "nivel": "erro", "codigo": "multi_oferta",
            "mensagem": (f"Este documento cota {ofertas['n']} ofertas diferentes lado a "
                         f"lado ({', '.join('R$ ' + v for v in ofertas['valores'])}). Os "
                         f"valores foram lidos da primeira coluna — confirme cada um "
                         f"antes de gerar a proposta."),
            "ofertas": ofertas})
    if ai_error:
        avisos.append({
            "nivel": "erro", "codigo": "falha_ia",
            "mensagem": ("A leitura assistida por IA falhou, então os campos que o perfil "
                         "não resolveu ficaram vazios — eles não estão ausentes do PDF."),
            "detalhe": ai_error})
    if drift:
        avisos.append({
            "nivel": "atencao", "codigo": "layout_mudou",
            "mensagem": (f"O modelo de leitura desta seguradora falhou em {prof_fail} de "
                         f"{prof_total} campos. O layout do documento pode ter mudado — "
                         f"confira os valores com atenção redobrada."),
            "perfil": profile_id})
    if not profile_used:
        avisos.append({
            "nivel": "atencao", "codigo": "sem_perfil",
            "mensagem": ("Nenhum modelo de leitura reconheceu este layout, então todos os "
                         "campos vieram da IA e precisam de conferência.")})
    n_conf = sum(1 for p in provenance.values() if p.get("confidence") == "baixa")
    if n_conf:
        avisos.append({
            "nivel": "atencao", "codigo": "campos_a_confirmar",
            "mensagem": f"{n_conf} campo(s) precisam da sua confirmação antes de gerar.",
            "campos": [k for k, p in provenance.items() if p.get("confidence") == "baixa"]})

    return {
        "insurer_id": insurer_id,
        "doc_id": doc_id,
        "profile_used": profile_used,
        "profile_id": profile_id,
        "ai_used": ai_used,
        "ai_error": ai_error,
        "drift": drift,
        "paginas_sem_texto": sem_texto,
        "ofertas": ofertas,
        "avisos": avisos,
        "fields": fields,
        "provenance": provenance,
        "missing": missing,
        "unmapped": EE.build_unmapped(pages, consumed),
        "pages": EE.page_maps(pages),
    }

def detect_insurer(seguradora, filename, texto):
    """Identifica a seguradora da coluna (define cor/logo do comparativo).

    Prioridade — da evidência mais forte para a mais fraca:
      1. o CAMPO `seguradora` extraído (curto e específico);
      2. o nome do arquivo;
      3. o texto inteiro do PDF — último recurso, porque cotações citam
         parceiros e a seguradora anterior da renovação (ex.: um orçamento
         Azul cita "Allianz Seguros" como congênere e "Porto Seguro" no rodapé).
    Em 3, vence o marcador MAIS LONGO encontrado, não o primeiro da lista.
    """
    ins_list = get_insurers()

    def by_marker(hay):
        best = None
        for ins in ins_list:
            for d in ins.get("detect", []):
                if d and d.lower() in hay and (best is None or len(d) > len(best[1])):
                    best = (ins["id"], d)
        return best[0] if best else None

    got = by_marker((seguradora or "").lower())
    if got:
        return got
    fn = (filename or "").lower()
    for ins in ins_list:
        if ins["id"] != "generico" and ins["id"] in fn:
            return ins["id"]
    if (seguradora or "").strip():
        # A seguradora FOI identificada no documento, mas não está cadastrada em
        # "Modelos de Entrada". Cair no texto inteiro aqui trocaria a marca por outra
        # citada de passagem (uma cotação Mitsui vira "Porto" pelo rodapé). Melhor a
        # marca neutra — o usuário corrige a seguradora da coluna com um clique.
        return "generico"
    return by_marker((texto or "").lower()) or "generico"

# =============================== multipart ===============================
def parse_multipart(body, boundary):
    parts = body.split(b"--" + boundary)
    out = []
    for part in parts:
        if not part or part in (b"--\r\n", b"--"): continue
        if b"\r\n\r\n" not in part: continue
        head, data = part.split(b"\r\n\r\n", 1)
        if data.endswith(b"\r\n"): data = data[:-2]
        head_s = head.decode("utf-8", "ignore")
        m = re.search(r'name="([^"]*)"', head_s)
        fn = re.search(r'filename="([^"]*)"', head_s)
        out.append({"name": m.group(1) if m else "", "filename": fn.group(1) if fn else None, "data": data})
    return out

# =============================== HTTP handler ===============================
class H(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    def log_message(self, *a): pass

    # -- helpers --
    def user(self):
        c = self.headers.get("Cookie", "")
        m = re.search(r"orca_sess=([a-f0-9]+)", c)
        if not m: return None
        un = SESS.get(m.group(1))
        if not un: return None
        return next((u for u in get_users() if u["username"] == un), None)

    def handle_one_request(self):
        self._corpo_lido = False        # a instância é reaproveitada no keep-alive
        return BaseHTTPRequestHandler.handle_one_request(self)

    # Um corpo de requisição que ninguém leu não some: a conexão é HTTP/1.1 com
    # keep-alive, então os bytes continuam no socket. O handler volta ao laço, lê
    # o começo do PDF como se fosse a requisição seguinte, responde 400 e fecha
    # com o resto por ler — e fechar um socket com dados não lidos, no Windows,
    # manda RST. O RST descarta o que ainda estava no buffer do cliente, inclusive
    # a resposta já enviada. Resultado: quem estava com a sessão expirada e mandou
    # uma proposta recebia erro de rede em vez do 401 que a tela sabe explicar.
    # Medido antes da correção: 2 falhas em 12 com 500 bytes, 12 em 12 com 2 MB.
    LIMITE_DESCARTE = 64 * 1024 * 1024

    def descartar_corpo(self):
        if getattr(self, "_corpo_lido", False):
            return
        self._corpo_lido = True
        try:
            n = int(self.headers.get("Content-Length", 0) or 0)
        except (ValueError, AttributeError):
            return
        if n > self.LIMITE_DESCARTE:
            # cliente fora de qualquer uso real: não vale ler para descartar
            self.close_connection = True
            return
        while n > 0:
            pedaco = self.rfile.read(min(n, 65536))
            if not pedaco:
                break
            n -= len(pedaco)

    def send_json(self, obj, code=200, cookie=None):
        b = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.descartar_corpo()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        if cookie: self.send_header("Set-Cookie", cookie)
        self.end_headers(); self.wfile.write(b)

    def salvar_pdf(self):
        """Grava o PDF montado no navegador e devolve o caminho real em disco.

        O caminho óbvio seria o download do próprio navegador (`pdf.save()`), e era
        o que existia. Só que numa janela de aplicativo o download depende de a
        casca implementar o delegate — o pywebview vem com `ALLOW_DOWNLOADS: False`
        — e o resultado era o pior possível: o arquivo não era criado e a interface
        anunciava sucesso assim mesmo. Numa corretora, isso é a pessoa achar que
        mandou a proposta e não ter mandado.

        Gravando aqui, o sucesso deixa de ser suposição: ou o arquivo existe e o
        caminho volta para a tela, ou volta erro. Também torna o comportamento igual
        em Windows e macOS, onde as regras de download são diferentes.
        """
        dados = self.read_body()
        if not dados or not dados.startswith(b"%PDF"):
            return self.send_json({"error": "conteúdo não é um PDF"}, 400)
        if len(dados) > 60 * 1024 * 1024:
            return self.send_json({"error": "arquivo grande demais"}, 413)

        bruto = unquote(self.headers.get("X-Nome-Arquivo", "") or "proposta")
        # só o que é seguro num nome de arquivo: nada de caminho, nada de reservado
        nome = re.sub(r"[^\w .\-()]+", "-", bruto, flags=re.UNICODE).strip(" .-")[:80] or "proposta"
        if not nome.lower().endswith(".pdf"):
            nome += ".pdf"

        pasta = os.path.join(os.path.expanduser("~"), "Documents", "Propostas NEWA")
        try:
            os.makedirs(pasta, exist_ok=True)
        except OSError:
            pasta = DEV
        destino = os.path.join(pasta, nome)
        base, ext = os.path.splitext(destino)
        n = 2
        while os.path.exists(destino):        # nunca sobrescrever proposta anterior
            destino = f"{base} ({n}){ext}"; n += 1
        try:
            with open(destino, "wb") as f:
                f.write(dados)
        except OSError as e:
            return self.send_json({"error": f"não foi possível gravar: {e}"}, 500)
        if not os.path.exists(destino) or os.path.getsize(destino) != len(dados):
            return self.send_json({"error": "o arquivo não foi gravado por inteiro"}, 500)
        return self.send_json({"ok": True, "path": destino, "pasta": pasta,
                               "nome": os.path.basename(destino), "bytes": len(dados)})

    def read_body(self):
        self._corpo_lido = True
        n = int(self.headers.get("Content-Length", 0) or 0)
        return self.rfile.read(n) if n else b""

    def read_json(self):
        try: return json.loads(self.read_body().decode("utf-8") or "{}")
        except Exception: return {}

    def serve_file(self, path, ctype=None, root=None):
        # Contenção de caminho: `root` é a única árvore que esta rota pode servir.
        # Sem isto, "/assets/../../../.env" sai da raiz e entrega o .env (a chave da
        # OpenAI) e o users.json — as rotas /assets e /data são as únicas servidas
        # antes da checagem de login.
        if root:
            try:
                real = os.path.realpath(path)
                base = os.path.realpath(root)
                if os.path.commonpath([real, base]) != base:
                    return self.send_json({"error": "not found"}, 404)
                path = real
            except (ValueError, OSError):
                return self.send_json({"error": "not found"}, 404)
        if not os.path.exists(path) or not os.path.isfile(path):
            return self.send_json({"error": "not found"}, 404)
        ctype = ctype or (mimetypes.guess_type(path)[0] or "application/octet-stream")
        with open(path, "rb") as f: b = f.read()
        self.send_response(200)
        self.send_header("Content-Type", ctype + ("; charset=utf-8" if ctype.startswith(("text", "application/javascript")) else ""))
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers(); self.wfile.write(b)

    def serve_index(self):
        """Serve o index com cache-bust nos assets locais.

        A marca é `versão do app + mtime do arquivo`. O mtime sozinho basta em
        desenvolvimento, mas não em instalação: um instalador pode preservar a data
        do arquivo, e aí a interface nova ficaria escondida atrás do CSS velho em
        cache. A versão no meio garante que toda release invalide tudo.
        """
        path = os.path.join(REPO, "index.html")
        if not os.path.exists(path): return self.send_json({"error": "not found"}, 404)
        html = open(path, encoding="utf-8").read()
        def ver(name):
            fp = os.path.join(ASSETS, name)
            m = str(int(os.path.getmtime(fp))) if os.path.exists(fp) else "0"
            return f"{updater.VERSION}-{m}"
        html = re.sub(r'(/assets/([\w./-]+\.(?:js|css)))',
                      lambda m: m.group(1) + "?v=" + ver(m.group(2)), html)
        b = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers(); self.wfile.write(b)

    # -- routing --
    def do_GET(self):
        p = urlparse(self.path).path
        if p == "/" or p == "/index.html":
            return self.serve_index()
        if p.startswith("/assets/"):
            return self.serve_file(os.path.join(ASSETS, unquote(p[len("/assets/"):])), root=ASSETS)
        if p.startswith("/data/"):
            return self.serve_file(os.path.join(DATA, unquote(p[len("/data/"):])), root=DATA)
        if p == "/api/page-image":
            if not self.user(): return self.send_json({"error": "unauth"}, 401)
            q = parse_qs(urlparse(self.path).query)
            did = (q.get("doc", [""])[0]); pno = int(q.get("p", ["1"])[0] or 1)
            data = render_page_png(did, pno)
            if not data: return self.send_json({"error": "not found"}, 404)
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "max-age=600")
            self.end_headers(); self.wfile.write(data); return
        if p == "/api/crop":
            if not self.user(): return self.send_json({"error": "unauth"}, 401)
            q = parse_qs(urlparse(self.path).query)
            def qf(k, d=0.0):
                try: return float(q.get(k, [d])[0])
                except Exception: return d
            did = q.get("doc", [""])[0]; pno = int(q.get("p", ["1"])[0] or 1)
            data = render_crop_png(did, pno, qf("x0"), qf("y0"), qf("x1"), qf("y1"))
            if not data: return self.send_json({"error": "not found"}, 404)
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "max-age=600")
            self.end_headers(); self.wfile.write(data); return
        if p == "/api/me":
            u = self.user()
            return self.send_json({"user": pub(u)} if u else {"error": "unauth"}, 200 if u else 401)
        if p == "/api/config":
            if not self.user(): return self.send_json({"error": "unauth"}, 401)
            c = get_config()
            return self.send_json({"model": c.get("model", DEFAULT_MODEL), "reasoning_effort": c.get("reasoning_effort", DEFAULT_EFFORT), "has_openai_key": bool(c.get("openai_key")), "corretora": c.get("corretora", {})})
        if p == "/api/insurers":
            if not self.user(): return self.send_json({"error": "unauth"}, 401)
            return self.send_json({"insurers": get_insurers()})
        if p == "/api/template":
            if not self.user(): return self.send_json({"error": "unauth"}, 401)
            return self.send_json(get_template())
        if p == "/api/update":
            if not self.user(): return self.send_json({"error": "unauth"}, 401)
            if parse_qs(urlparse(self.path).query).get("agora"):
                checar_atualizacao()
            return self.send_json(dict(ATUALIZACAO))
        if p == "/api/users":
            u = self.user()
            if not u or u["role"] != "admin": return self.send_json({"error": "forbidden"}, 403)
            return self.send_json({"users": [pub(x) for x in get_users()]})
        return self.send_json({"error": "not found"}, 404)

    def do_POST(self):
        p = urlparse(self.path).path
        if p == "/api/login":
            d = self.read_json()
            u = next((x for x in get_users() if x["username"].lower() == str(d.get("username", "")).lower()), None)
            if not u or not check_pw(str(d.get("password", "")), u["pw"]):
                return self.send_json({"error": "invalid"}, 401)
            tok = new_session(u["username"])
            # Todo login verifica atualização. É o que dá à usuária um jeito de forçar
            # a busca sem saber que ela existe: sair e entrar de novo resolve.
            threading.Thread(target=checar_atualizacao, daemon=True).start()
            return self.send_json({"user": pub(u)}, cookie=f"orca_sess={tok}; Path=/; HttpOnly; SameSite=Lax")
        if p == "/api/logout":
            return self.send_json({"ok": True}, cookie="orca_sess=; Path=/; Max-Age=0")
        if p == "/api/save-pdf":
            if not self.user(): return self.send_json({"error": "unauth"}, 401)
            return self.salvar_pdf()
        me = self.user()
        if not me: return self.send_json({"error": "unauth"}, 401)
        if p == "/api/extract":
            ct = self.headers.get("Content-Type", "")
            m = re.search(r"boundary=(.+)$", ct)
            if not m: return self.send_json({"error": "no boundary"}, 400)
            parts = parse_multipart(self.read_body(), m.group(1).strip().strip('"').encode())
            fp = next((x for x in parts if x["filename"]), None)
            if not fp: return self.send_json({"error": "sem arquivo"}, 400)
            try:
                return self.send_json(extract_pdf(fp["data"], fp["filename"]))
            except Exception as e:
                return self.send_json({"error": str(e)}, 422)
        # admin-only daqui pra baixo
        if me["role"] != "admin": return self.send_json({"error": "forbidden"}, 403)
        if p == "/api/config":
            d = self.read_json(); c = get_config()
            if "model" in d: c["model"] = d["model"]
            if "reasoning_effort" in d: c["reasoning_effort"] = d["reasoning_effort"]
            if d.get("openai_key"): c["openai_key"] = d["openai_key"]
            if "corretora" in d: c["corretora"] = d["corretora"]
            set_config(c); return self.send_json({"ok": True})
        if p == "/api/insurers":
            d = self.read_json(); set_insurers(d.get("insurers", [])); return self.send_json({"ok": True})
        if p == "/api/template":
            d = self.read_json(); set_template(d.get("template", {})); return self.send_json({"ok": True})
        if p == "/api/users":
            d = self.read_json(); users = get_users()
            if any(x["username"].lower() == str(d.get("username", "")).lower() for x in users):
                return self.send_json({"error": "usuário já existe"}, 409)
            users.append({"username": d["username"], "name": d.get("name", d["username"]),
                          "role": "admin" if d.get("role") == "admin" else "user", "pw": hash_pw(d["password"])})
            set_users(users); return self.send_json({"ok": True})
        return self.send_json({"error": "not found"}, 404)

    def do_PUT(self):
        me = self.user()
        if not me or me["role"] != "admin": return self.send_json({"error": "forbidden"}, 403)
        m = re.match(r"^/api/users/(.+)$", urlparse(self.path).path)
        if not m: return self.send_json({"error": "not found"}, 404)
        un = unquote(m.group(1)); d = self.read_json(); users = get_users()
        u = next((x for x in users if x["username"] == un), None)
        if not u: return self.send_json({"error": "não encontrado"}, 404)
        if "name" in d: u["name"] = d["name"]
        if "role" in d: u["role"] = "admin" if d["role"] == "admin" else "user"
        if d.get("password"): u["pw"] = hash_pw(d["password"])
        set_users(users); return self.send_json({"ok": True})

    def do_DELETE(self):
        me = self.user()
        if not me or me["role"] != "admin": return self.send_json({"error": "forbidden"}, 403)
        m = re.match(r"^/api/users/(.+)$", urlparse(self.path).path)
        if not m: return self.send_json({"error": "not found"}, 404)
        un = unquote(m.group(1))
        if un == me["username"]: return self.send_json({"error": "não pode remover a si mesmo"}, 400)
        set_users([x for x in get_users() if x["username"] != un]); return self.send_json({"ok": True})

def pub(u):
    return None if not u else {"username": u["username"], "name": u.get("name", u["username"]), "role": u.get("role", "user")}

# =============================== atualização ===============================
# Estado da última verificação, lido por GET /api/update. A verificação roda numa
# thread ao subir o servidor: sem rede ou com o servidor de atualização fora do ar
# ela falha em silêncio e o app trabalha com os perfis que já tem em disco.
ATUALIZACAO = {"app": updater.VERSION, "verificado": False}

def checar_atualizacao():
    cfg = get_config()
    r = updater.verificar(cfg.get("update_url", ""), PROFILES_LOCAL, PROFILES_DIR)

    # Instalado, o código vive em `<instalação>/repo` e é ele que o programa roda
    # (ver app.py). Sincronizar essa pasta é o que faz uma correção publicada hoje
    # chegar ao usuário no próximo login — sem reinstalar nada. Rodando do
    # código-fonte não há o que sincronizar: a pasta É o repositório de trabalho.
    if REPO.replace("\\", "/").rstrip("/").endswith("/repo"):
        s = updater.sincronizar_repo(REPO, cfg.get("repo_zip_url") or updater.ZIP_REPO)
        r["repo"] = {"ok": s["ok"], "erro": s["erro"],
                     "atualizados": s["atualizados"], "iguais": s["iguais"]}
        if s["atualizados"]:
            print(f"  {len(s['atualizados'])} arquivo(s) do programa atualizados "
                  f"(vale ao reabrir): {', '.join(s['atualizados'][:5])}"
                  f"{'…' if len(s['atualizados']) > 5 else ''}")

    ATUALIZACAO.clear(); ATUALIZACAO.update(r)
    if r.get("perfis_atualizados"):
        print(f"  perfis atualizados: {', '.join(r['perfis_atualizados'])}")

def main():
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), H)
    url = f"http://localhost:{PORT}/"
    print(f"\n  Orçamentos NEWA {updater.VERSION} — dev server\n  {url}\n  (usuário: Madu / senha: 123)\n  Ctrl+C para parar.\n")
    threading.Thread(target=checar_atualizacao, daemon=True).start()
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try: srv.serve_forever()
    except KeyboardInterrupt: print("\n  encerrado.")

if __name__ == "__main__":
    main()
