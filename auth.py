# -*- coding: utf-8 -*-
"""Quem entra no app.

Com `auth_url` configurada, quem decide é o webhook do n8n: um POST com usuário e
senha, e a resposta manda. Sem ela, o app cai no `users.json` local — que é o modo
de desenvolvimento, e o único em que a senha padrão `123` ainda abre alguma porta.

O contrato, do lado do n8n:

    POST <auth_url>
    {"usuario": "madu", "senha": "...", "app": "orcamentos-newa", "versao": "0.4.0"}

    liberado  -> 200 {"ok": true, "usuario": "madu", "nome": "Madu",
                      "papel": "admin", "expira_em": "2026-08-04T12:00:00Z"}
    negado    -> 200 {"ok": false, "erro": "usuário ou senha inválidos"}

Negado responde 200 de propósito. O n8n, em caminho de erro, devolve HTML dele —
e aí o app não distingue "senha errada" de "servidor caiu", que são situações
opostas: uma nega, a outra precisa deixar quem já trabalhava continuar.

Regras, e o porquê de cada uma:

* **Falha fechado.** Só libera com 200 + JSON válido + `ok: true`. Página de erro
  de proxy, HTML, corpo vazio, 4xx — tudo negado.

* **Negado e indisponível não são a mesma coisa.** 4xx e resposta fora do contrato
  negam. Falha de rede e 5xx marcam indisponibilidade: o servidor é que está com
  problema, e trancar todo mundo fora por causa disso seria pior que o remédio.

* **Crachá offline com prazo.** Todo acesso concedido pelo servidor grava usuário,
  papel, prazo (`expira_em` — quem escolhe é o servidor) e um verificador da senha.
  Sem rede, entra quem apresentar a mesma senha e estiver dentro do prazo. Cortar
  alguém no banco tira o acesso em, no máximo, esse prazo.

* **O verificador é hash, não senha.** pbkdf2-sha256, o mesmo esquema do
  `users.json`. Quem abrir o cache não encontra senha de ninguém.
"""
import hashlib, hmac, json, os, re, secrets, tempfile, urllib.error, urllib.request
from datetime import datetime, timedelta, timezone

TIMEOUT = 8.0
PRAZO_PADRAO = timedelta(days=7)      # usado só quando o servidor não manda expira_em
ITERACOES = 120000


# --------------------------------------------------------------------- senhas
def hash_pw(pw, salt=None):
    salt = salt or secrets.token_hex(8)
    h = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), ITERACOES).hex()
    return f"{salt}${h}"


def check_pw(pw, stored):
    try:
        salt, h = stored.split("$", 1)
        return hmac.compare_digest(
            hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), ITERACOES).hex(), h)
    except Exception:
        return False


# ---------------------------------------------------------------------- prazo
def _agora():
    return datetime.now(timezone.utc)


def _ler_prazo(valor):
    """ISO 8601 -> datetime com fuso. Devolve None se não der para entender."""
    if not isinstance(valor, str) or not valor.strip():
        return None
    try:
        d = datetime.fromisoformat(valor.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def _dentro_do_prazo(valor):
    d = _ler_prazo(valor)
    return bool(d and d > _agora())


# ---------------------------------------------------------------- crachá local
def ler_cache(caminho):
    try:
        with open(caminho, encoding="utf-8-sig") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}


def gravar_cache(caminho, dados):
    """Grava de forma atômica: um desligamento no meio não deixa cache pela metade."""
    try:
        pasta = os.path.dirname(caminho) or "."
        os.makedirs(pasta, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=pasta, prefix=".auth-", suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        os.replace(tmp, caminho)
        return True
    except Exception:
        return False


# ------------------------------------------------------------------ requisição
def _url_aceitavel(url):
    u = (url or "").strip().lower()
    # HTTPS obrigatório: a senha viaja no corpo. As exceções são de teste local.
    return u.startswith("https://") or u.startswith(("http://127.0.0.1", "http://localhost"))


def _pedir(url, corpo, timeout):
    """Devolve (dados, indisponivel).

    `dados` é o JSON da resposta, ou None. `indisponivel` diz se o problema foi do
    servidor (rede, 5xx) e não das credenciais — é o que autoriza o crachá offline.
    """
    req = urllib.request.Request(
        url, json.dumps(corpo, ensure_ascii=False).encode("utf-8"),
        {"Content-Type": "application/json; charset=utf-8",
         "Accept": "application/json",
         "User-Agent": "OrcamentosNEWA"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            bruto = r.read(64 * 1024)
    except urllib.error.HTTPError as e:
        # 5xx é problema do servidor; 4xx é resposta sobre as credenciais.
        return None, e.code >= 500
    except Exception:
        return None, True                     # sem rede, DNS, timeout, TLS
    try:
        d = json.loads(bruto.decode("utf-8", "replace"))
    except Exception:
        return None, False                    # respondeu, mas não o contrato
    return (d if isinstance(d, dict) else None), False


# ---------------------------------------------------------------- autenticação
def _pessoa(d, usuario):
    papel = "admin" if str(d.get("papel", "")).lower() == "admin" else "user"
    nome = str(d.get("nome") or "").strip() or usuario
    return {"username": str(d.get("usuario") or usuario), "name": nome, "role": papel}


def autenticar(url, usuario, senha, cache_path, versao="", timeout=TIMEOUT):
    """Valida no n8n; sem resposta, aceita o crachá offline dentro do prazo.

    Devolve `{"ok": bool, "user": {...}|None, "origem": str, "mensagem": str}`.
    `origem` é 'servidor', 'offline' ou 'negado' — serve para a tela dizer à pessoa
    o que aconteceu, em vez de um "falha no login" que não ajuda ninguém.
    """
    usuario = (usuario or "").strip()
    chave = usuario.lower()
    cache = ler_cache(cache_path)

    if not _url_aceitavel(url):
        return {"ok": False, "user": None, "origem": "config",
                "mensagem": "o endereço de validação de acesso não está configurado "
                            "corretamente (precisa ser https)"}
    if not usuario or not senha:
        return {"ok": False, "user": None, "origem": "negado",
                "mensagem": "informe usuário e senha"}

    d, indisponivel = _pedir(url, {"usuario": usuario, "senha": senha,
                                   "app": "orcamentos-newa", "versao": versao}, timeout)

    if d is not None and d.get("ok") is True:
        pessoa = _pessoa(d, usuario)
        prazo = _ler_prazo(d.get("expira_em")) or (_agora() + PRAZO_PADRAO)
        cache[chave] = {"nome": pessoa["name"], "papel": pessoa["role"],
                        "expira_em": prazo.isoformat(), "verificador": hash_pw(senha)}
        gravar_cache(cache_path, cache)
        return {"ok": True, "user": pessoa, "origem": "servidor", "mensagem": ""}

    if not indisponivel:
        # O servidor respondeu e não liberou. Some o crachá: se a pessoa foi
        # desligada, não faz sentido o app continuar aceitando o crachá antigo.
        if chave in cache:
            cache.pop(chave, None)
            gravar_cache(cache_path, cache)
        msg = ""
        if isinstance(d, dict):
            msg = str(d.get("erro") or "").strip()
        return {"ok": False, "user": None, "origem": "negado",
                "mensagem": msg or "usuário ou senha inválidos"}

    # Daqui para baixo: o servidor não respondeu. Só o crachá vale.
    guardado = cache.get(chave)
    if not guardado:
        return {"ok": False, "user": None, "origem": "sem-servidor",
                "mensagem": "não consegui confirmar seu acesso e não há registro "
                            "recente deste usuário nesta máquina. Verifique a internet."}
    if not _dentro_do_prazo(guardado.get("expira_em")):
        return {"ok": False, "user": None, "origem": "sem-servidor",
                "mensagem": "não consegui confirmar seu acesso e seu último acesso "
                            "válido expirou. Verifique a internet."}
    if not check_pw(senha, guardado.get("verificador", "")):
        return {"ok": False, "user": None, "origem": "negado",
                "mensagem": "usuário ou senha inválidos"}
    return {"ok": True,
            "user": {"username": usuario, "name": guardado.get("nome") or usuario,
                     "role": "admin" if guardado.get("papel") == "admin" else "user"},
            "origem": "offline",
            "mensagem": "sem conexão com o servidor de acesso — entrando com o "
                        "último acesso confirmado"}
