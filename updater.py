# -*- coding: utf-8 -*-
"""Atualização automática dos perfis de extração, e aviso de versão nova do app.

Por que os perfis se atualizam sozinhos e o app não: um perfil é um JSON de
regras. Quando uma seguradora muda o layout da cotação, o conserto é editar o
perfil — e toda instalação passa a extrair certo sem ninguém reinstalar nada.
Já o motor e a interface mudam junto com o executável, então dependem do
instalador.

De onde vem: uma URL base que serve `versao.json`. Pode ser o
`raw.githubusercontent.com` de um repositório público ou um webhook do n8n com
o repositório privado atrás — o cliente é o mesmo, muda só a URL. Vazia
(o padrão) desliga a verificação.

Formato de `versao.json`:

    {
      "app": "0.4.0",
      "instalador": "https://.../Instalar-OrcamentosNEWA-0.4.0.exe",
      "perfis": { "porto.json": "<sha256 do conteúdo>", ... }
    }

Regras que valem sempre, porque o manifesto vem da rede e rede não é confiável:

* nome de arquivo é validado contra `[a-z0-9_-]+\\.json` — um manifesto
  adulterado não consegue escrever fora da pasta de perfis;
* o sha256 é conferido depois do download e o arquivo é descartado se divergir;
* o conteúdo tem que ser um JSON de perfil válido para ser gravado;
* a gravação é atômica (temporário + replace), então uma queda no meio nunca
  deixa perfil truncado em disco;
* nada aqui levanta exceção para fora nem bloqueia: sem rede, com proxy no
  caminho ou com o servidor fora do ar, o app abre e trabalha com o que já tem.

Os perfis baixados vão para uma pasta gravável do usuário, nunca para dentro da
instalação — em `C:\\Program Files` o processo não teria permissão de escrita.
Os perfis que vieram no instalador continuam lá e servem de piso: o que é
baixado se sobrepõe a eles por nome de arquivo.
"""
import os, re, json, time, hashlib, secrets, tempfile
import urllib.request, urllib.error

VERSION = "0.4.0"

NOME_OK = re.compile(r"^[a-z0-9_][a-z0-9_-]*\.json$")
MAX_PERFIL = 512 * 1024       # um perfil real tem ~7 KB; 512 KB é folga larga
MAX_MANIFESTO = 256 * 1024
TIMEOUT = 6.0                 # curto de propósito: isto nunca pode segurar o app


def _get(url, limite, timeout=TIMEOUT):
    """Baixa `url` com teto de tamanho. Devolve bytes ou None — nunca levanta.

    Cache é o inimigo aqui. Entre nós e o arquivo pode haver a CDN do GitHub (que
    guarda o raw por minutos), um proxy corporativo, ou um antivírus que
    intercepta HTTPS — e qualquer um deles pode devolver a versão de ontem, o que
    faria a atualização simplesmente não acontecer, em silêncio e sem erro.

    Contra isso: cabeçalhos pedindo revalidação E um parâmetro único na URL. Os
    cabeçalhos bastam para caches que respeitam a norma; o parâmetro resolve os
    que não respeitam, porque para eles vira outra URL.
    """
    if not url.lower().startswith(("https://", "http://127.0.0.1", "http://localhost")):
        return None                      # fora de HTTPS só o servidor local
    sep = "&" if "?" in url else "?"
    url = f"{url}{sep}_={int(time.time() * 1000)}-{secrets.token_hex(4)}"
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": f"OrcamentosNEWA/{VERSION}",
            "Cache-Control": "no-cache, no-store, max-age=0",
            "Pragma": "no-cache",
        })
        with urllib.request.urlopen(req, timeout=timeout) as r:
            if r.status != 200:
                return None
            dados = r.read(limite + 1)
            return None if len(dados) > limite else dados
    except Exception:
        return None


def _sha(dados):
    return hashlib.sha256(dados).hexdigest()


def _hashes_locais(pasta):
    out = {}
    if not os.path.isdir(pasta):
        return out
    for nome in os.listdir(pasta):
        if NOME_OK.match(nome):
            try:
                out[nome] = _sha(open(os.path.join(pasta, nome), "rb").read())
            except Exception:
                pass
    return out


def _grava_atomico(destino, dados):
    d = os.path.dirname(destino)
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(dados)
        os.replace(tmp, destino)
        return True
    except Exception:
        try: os.unlink(tmp)
        except Exception: pass
        return False


def _perfil_valido(dados):
    """Um perfil precisa ser objeto JSON com `id` e `fields`. Barra HTML de
    página de erro, JSON truncado e qualquer coisa que não seja perfil."""
    try:
        d = json.loads(dados.decode("utf-8"))
    except Exception:
        return False
    return isinstance(d, dict) and isinstance(d.get("id"), str) and isinstance(d.get("fields"), dict)


def verificar(base_url, pasta_perfis, pasta_base=None, aplicar=True):
    """Consulta o manifesto e sincroniza os perfis.

    `pasta_perfis` é a pasta gravável (o que foi baixado); `pasta_base` é a que
    veio no instalador, usada só para leitura — um perfil idêntico ao instalado
    não precisa ser baixado.

    Devolve sempre um dicionário, nunca levanta:
      {"ok": bool, "erro": str|None, "app": str, "app_novo": str|None,
       "instalador": str|None, "perfis_atualizados": [nomes], "verificado": bool}
    """
    r = {"ok": False, "erro": None, "app": VERSION, "app_novo": None,
         "instalador": None, "perfis_atualizados": [], "verificado": False}
    if not base_url:
        r["erro"] = "desligado"
        return r

    bruto = _get(base_url.rstrip("/") + "/versao.json", MAX_MANIFESTO)
    if bruto is None:
        r["erro"] = "sem resposta"
        return r
    try:
        man = json.loads(bruto.decode("utf-8"))
        if not isinstance(man, dict):
            raise ValueError
    except Exception:
        r["erro"] = "manifesto inválido"
        return r

    r["verificado"] = True
    r["ok"] = True

    app_remoto = man.get("app")
    if isinstance(app_remoto, str) and _maior(app_remoto, VERSION):
        r["app_novo"] = app_remoto
        inst = man.get("instalador")
        if isinstance(inst, str) and inst.lower().startswith("https://"):
            r["instalador"] = inst

    perfis = man.get("perfis")
    if not isinstance(perfis, dict) or not aplicar:
        return r

    locais = _hashes_locais(pasta_perfis)
    if pasta_base:
        for nome, h in _hashes_locais(pasta_base).items():
            locais.setdefault(nome, h)

    for nome, esperado in sorted(perfis.items()):
        if not NOME_OK.match(nome) or not isinstance(esperado, str) or len(esperado) != 64:
            continue                                   # nome ou hash suspeito: ignora
        if locais.get(nome) == esperado:
            continue                                   # já está igual
        dados = _get(base_url.rstrip("/") + "/perfis/" + nome, MAX_PERFIL)
        if dados is None or _sha(dados) != esperado or not _perfil_valido(dados):
            continue                                   # não bate: descarta em silêncio
        if _grava_atomico(os.path.join(pasta_perfis, nome), dados):
            r["perfis_atualizados"].append(nome)
    return r


ZIP_REPO = "https://codeload.github.com/theohaiek/orcamentos-newa/zip/refs/heads/main"
MAX_ZIP = 40 * 1024 * 1024

# O que a sincronização mantém em dia. Testes, documentação e scripts de build não
# vão para a máquina do usuário; e nada fora desta lista é escrito, então um
# repositório adulterado não consegue plantar arquivo em lugar nenhum.
SINCRONIZAR = ("app.py", "server.py", "extract_engine.py", "updater.py", "auth.py",
               "index.html", "data/", "orcamentos-newa/")


def _permitido(rel):
    rel = rel.replace("\\", "/")
    if ".." in rel.split("/") or rel.startswith("/") or ":" in rel:
        return False
    if "/__pycache__/" in rel or rel.endswith(".pyc"):
        return False
    return any(rel == p or (p.endswith("/") and rel.startswith(p)) for p in SINCRONIZAR)


def sincronizar_repo(pasta_repo, url=ZIP_REPO, timeout=60.0):
    """Põe a pasta `repo` da instalação em dia com o repositório.

    Atualizar só os perfis resolvia meia dúvida: um conserto no motor ou na
    interface continuaria preso na máquina de quem desenvolve. Aqui o programa
    inteiro acompanha o repositório — é por isso que o executável carrega apenas
    Python e as bibliotecas, e o código de verdade mora em `repo`.

    Baixa o `.zip` do branch (o repositório todo tem menos de 1 MB, então comparar
    arquivo a arquivo é mais simples e mais confiável que manter um manifesto) e
    grava só o que difere, de forma atômica.

    Nunca levanta e nunca apaga nada: arquivo que sumiu do repositório continua em
    disco. Remover é mais arriscado do que deixar sobrar, e sobrar não quebra —
    o que não é referenciado simplesmente não é lido.
    """
    r = {"ok": False, "erro": None, "atualizados": [], "iguais": 0}
    if not pasta_repo:
        r["erro"] = "sem pasta"; return r
    dados = _get(url, MAX_ZIP, timeout)
    if dados is None:
        r["erro"] = "sem resposta"; return r

    import io, zipfile
    try:
        z = zipfile.ZipFile(io.BytesIO(dados))
    except Exception:
        r["erro"] = "pacote inválido"; return r

    nomes = z.namelist()
    if not nomes:
        r["erro"] = "pacote vazio"; return r
    raiz = nomes[0].split("/")[0] + "/"          # o GitHub embrulha em "<repo>-<branch>/"
    try:
        for n in nomes:
            if n.endswith("/") or not n.startswith(raiz):
                continue
            rel = n[len(raiz):]
            if not _permitido(rel):
                continue
            novo = z.read(n)
            destino = os.path.join(pasta_repo, *rel.split("/"))
            if os.path.exists(destino):
                try:
                    if _sha(open(destino, "rb").read()) == _sha(novo):
                        r["iguais"] += 1
                        continue
                except OSError:
                    pass
            if _grava_atomico(destino, novo):
                r["atualizados"].append(rel)
    except Exception as e:
        r["erro"] = str(e); return r
    r["ok"] = True
    return r


def _maior(a, b):
    """Compara versões `1.2.3`. Não-numérico perde, para nunca oferecer downgrade."""
    def part(v):
        try:
            return [int(x) for x in str(v).strip().split(".")]
        except Exception:
            return []
    pa, pb = part(a), part(b)
    if not pa:
        return False
    n = max(len(pa), len(pb))
    return (pa + [0] * n)[:n] > (pb + [0] * n)[:n]
