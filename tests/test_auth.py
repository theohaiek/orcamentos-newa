# -*- coding: utf-8 -*-
"""Controle de acesso — validação no n8n, sem rede real.

Sobe um servidor local fazendo o papel do webhook e exercita o cliente contra ele.
O que precisa ficar provado:

  1. só 200 + JSON + `ok: true` libera — HTML, corpo vazio e 4xx negam;
  2. negado e indisponível são tratados diferente: um nega, o outro deixa o crachá
     offline valer, porque trancar todo mundo fora quando a VPS cai é pior que o mal
     que se quer evitar;
  3. o crachá offline tem prazo, exige a mesma senha, e some quando o servidor nega
     — quem foi desligado não continua entrando por inércia;
  4. o crachá guarda hash, nunca a senha;
  5. com `auth_url` configurada, o `users.json` local NÃO vale mais para entrar.
     Era esse o furo: a senha padrão `123` numa máquina deixava entrar quem
     descobrisse um nome de usuário.
"""
import json, os, sys, tempfile, threading, urllib.error, urllib.request
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import auth

falhas = []
def ok(cond, msg):
    print(f"    [{'OK ' if cond else 'FALHA'}] {msg}", flush=True)
    if not cond:
        falhas.append(msg)


# ------------------------------------------------------ webhook de mentira
RESPOSTA = {"status": 200, "corpo": b'{"ok": true}'}
RECEBIDO = []

class Mao(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0) or 0)
        bruto = self.rfile.read(n)
        try:
            RECEBIDO.append(json.loads(bruto.decode("utf-8")))
        except Exception:
            RECEBIDO.append(None)
        corpo = RESPOSTA["corpo"]
        self.send_response(RESPOSTA["status"])
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers(); self.wfile.write(corpo)
    def log_message(self, *a): pass


srv = ThreadingHTTPServer(("127.0.0.1", 0), Mao)
URL = f"http://127.0.0.1:{srv.server_address[1]}/webhook/teste"
threading.Thread(target=srv.serve_forever, daemon=True).start()

tmp = tempfile.mkdtemp(prefix="auth-")
CACHE = os.path.join(tmp, "auth_cache.json")


def responde(obj, status=200, cru=None):
    RESPOSTA["status"] = status
    RESPOSTA["corpo"] = cru if cru is not None else json.dumps(obj).encode("utf-8")


def prazo(dias):
    return (datetime.now(timezone.utc) + timedelta(days=dias)).isoformat()


print(">> 1. acesso liberado pelo servidor")
RECEBIDO.clear()
responde({"ok": True, "usuario": "madu", "nome": "Madu Ferreira",
          "papel": "admin", "expira_em": prazo(7)})
r = auth.autenticar(URL, "madu", "senha-boa", CACHE, "0.4.0")
ok(r["ok"] and r["origem"] == "servidor", "entra pelo servidor")
ok(r["user"] == {"username": "madu", "name": "Madu Ferreira", "role": "admin"},
   f"identidade vem do servidor: {r['user']}")
ok(RECEBIDO and RECEBIDO[0].get("senha") == "senha-boa"
   and RECEBIDO[0].get("app") == "orcamentos-newa", f"corpo enviado: {RECEBIDO[0]}")

print(">> 2. o crachá offline foi gravado, e sem a senha")
guardado = json.load(open(CACHE, encoding="utf-8"))["madu"]
ok(guardado["papel"] == "admin" and guardado["nome"] == "Madu Ferreira", "papel e nome guardados")
ok("senha-boa" not in json.dumps(guardado), "a senha em claro não está no arquivo")
ok(auth.check_pw("senha-boa", guardado["verificador"]), "o verificador confere a senha certa")
ok(not auth.check_pw("outra", guardado["verificador"]), "e recusa a errada")

print(">> 3. servidor fora do ar: o crachá vale, dentro do prazo")
MORTO = "https://127.0.0.1:1/webhook"
r = auth.autenticar(MORTO, "madu", "senha-boa", CACHE, "0.4.0")
ok(r["ok"] and r["origem"] == "offline", "entra offline")
ok("sem conexão" in r["mensagem"], f"e a tela é avisada: {r['mensagem']}")
r = auth.autenticar(MORTO, "madu", "senha-errada", CACHE, "0.4.0")
ok(not r["ok"], "offline não aceita senha errada")
r = auth.autenticar(MORTO, "ninguem", "x", CACHE, "0.4.0")
ok(not r["ok"] and r["origem"] == "sem-servidor", "sem crachá e sem servidor, não entra")

print(">> 4. crachá vencido não entra")
c = json.load(open(CACHE, encoding="utf-8"))
c["madu"]["expira_em"] = prazo(-1)
auth.gravar_cache(CACHE, c)
r = auth.autenticar(MORTO, "madu", "senha-boa", CACHE, "0.4.0")
ok(not r["ok"] and "expirou" in r["mensagem"], f"vencido é vencido: {r['mensagem']}")

print(">> 5. só 200 + JSON + ok:true libera")
for rotulo, kw in (
        ("HTML de erro do proxy", dict(cru=b"<html>502 Bad Gateway</html>")),
        ("corpo vazio", dict(cru=b"")),
        ("JSON sem o campo ok", dict(obj={"usuario": "madu"})),
        ("ok como string", dict(obj={"ok": "true"})),
        ("ok: false", dict(obj={"ok": False, "erro": "usuário desligado"})),
        ("401 do servidor", dict(obj={"ok": True}, status=401)),
        ("403 do servidor", dict(obj={"ok": True}, status=403)),
):
    responde(kw.get("obj"), kw.get("status", 200), kw.get("cru"))
    r = auth.autenticar(URL, "madu", "senha-boa", CACHE, "0.4.0")
    ok(not r["ok"], f"{rotulo} nega")

print(">> 5b. o motivo da recusa vem do servidor, mesmo em 4xx")
# Com o n8n respondendo 401 para senha errada, o corpo é a única coisa que
# distingue "senha errada" de "senha alterada". Se ele for descartado, a tela só
# consegue dizer "acesso negado" e a pessoa não sabe o que fazer.
for cod in (401, 403, 422):
    responde({"ok": False, "erro": "sua senha foi alterada"}, status=cod)
    r = auth.autenticar(URL, "madu", "x", CACHE, "1.0.0")
    ok(not r["ok"] and r["mensagem"] == "sua senha foi alterada",
       f"HTTP {cod}: a mensagem do corpo chega à tela")

print(">> 5c. webhook respondendo antes de conferir é erro de configuração, não senha errada")
responde({"message": "Workflow was started"})
r = auth.autenticar(URL, "madu", "x", CACHE, "1.0.0")
ok(not r["ok"], "não libera")
ok(r["origem"] == "config" and "Respond to Webhook" in r["mensagem"],
   f"e diz onde está o problema: {r['mensagem'][:60]}...")

print(">> 6. 5xx é problema do servidor, não das credenciais")
responde({"ok": True}, status=200)
auth.autenticar(URL, "madu", "senha-boa", CACHE, "0.4.0")        # regrava o crachá
responde({"erro": "workflow quebrado"}, status=500)
r = auth.autenticar(URL, "madu", "senha-boa", CACHE, "0.4.0")
ok(r["ok"] and r["origem"] == "offline", "500 deixa o crachá valer")

print(">> 7. negado apaga o crachá")
responde({"ok": False, "erro": "usuário desligado"})
r = auth.autenticar(URL, "madu", "senha-boa", CACHE, "0.4.0")
ok(not r["ok"] and r["mensagem"] == "usuário desligado", "a mensagem do servidor chega à tela")
ok("madu" not in json.load(open(CACHE, encoding="utf-8")),
   "desligado no servidor não continua entrando offline")

print(">> 8. endereço sem https é recusado")
r = auth.autenticar("http://exemplo.com/webhook", "madu", "x", CACHE, "0.4.0")
ok(not r["ok"] and r["origem"] == "config", "http externo não serve — a senha vai no corpo")
ok(auth._url_aceitavel("https://editor.clinicaleger.com.br/webhook/abc"), "https serve")

print(">> 9. papel desconhecido não vira admin")
responde({"ok": True, "papel": "gerente", "expira_em": prazo(1)})
r = auth.autenticar(URL, "outro", "s", CACHE, "0.4.0")
ok(r["ok"] and r["user"]["role"] == "user", f"papel fora do contrato cai para user: {r['user']['role']}")

# ---------------------------------------------------------------- integração
print(">> 10. com auth_url configurada, o users.json local não vale mais")
import server
server.CONFIG_F = os.path.join(tmp, "config.json")
server.USERS_F = os.path.join(tmp, "users.json")
server.AUTH_CACHE = os.path.join(tmp, "cache-srv.json")
server.jwrite(server.USERS_F, {"users": [
    {"username": "Madu", "name": "Madu", "role": "admin", "pw": server.hash_pw("123")}]})
server.jwrite(server.CONFIG_F, {"auth_url": URL, server.MIGRACAO_MODELO[2]: True})

httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.H)
APP = f"http://127.0.0.1:{httpd.server_address[1]}"
threading.Thread(target=httpd.serve_forever, daemon=True).start()

def entrar(u, s):
    req = urllib.request.Request(APP + "/api/login",
                                 json.dumps({"username": u, "password": s}).encode(),
                                 {"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as x:
            return x.status, json.loads(x.read()), (x.headers.get("Set-Cookie") or "")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}"), ""

responde({"ok": False, "erro": "usuário ou senha inválidos"})
st, body, _ = entrar("Madu", "123")
ok(st == 401, f"a senha local 123 não entra mais (HTTP {st})")

responde({"ok": True, "usuario": "madu", "nome": "Madu", "papel": "admin", "expira_em": prazo(7)})
st, body, ck = entrar("madu", "qualquer-uma-que-o-servidor-aceite")
ok(st == 200 and body.get("user", {}).get("role") == "admin", f"quem o servidor libera entra: {st}")
ok("orca_sess=" in ck, "a sessão é criada")

print(">> 11. o usuário do servidor existe para as rotas seguintes")
# Antes, a sessão guardava só o nome e o `user()` procurava no users.json local —
# quem entrou pelo n8n não estava lá, e TODA rota depois do login respondia 401.
req = urllib.request.Request(APP + "/api/me", headers={"Cookie": ck.split(";")[0]})
with urllib.request.urlopen(req, timeout=10) as x:
    me = json.loads(x.read())
ok(me.get("user", {}).get("username") == "madu", f"/api/me reconhece a sessão: {me}")

print(">> 12. sem auth_url, o login local volta a valer (modo de desenvolvimento)")
server.jwrite(server.CONFIG_F, {"auth_url": "", server.MIGRACAO_MODELO[2]: True})
st, body, _ = entrar("Madu", "123")
ok(st == 200, f"users.json volta a decidir quando não há servidor configurado: {st}")

httpd.shutdown(); srv.shutdown()
print(f"\n  RESULTADO: {'OK' if not falhas else 'FALHOU -> ' + '; '.join(falhas)}")
sys.exit(1 if falhas else 0)
