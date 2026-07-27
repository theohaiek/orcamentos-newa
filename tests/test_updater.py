# -*- coding: utf-8 -*-
"""Atualização automática de perfis — sem rede real.

Sobe um servidor HTTP na própria máquina fazendo o papel do repositório (ou do
n8n) e exercita o cliente contra ele. O que precisa ficar provado:

  1. perfil novo é baixado e passa a valer sobre o que veio no instalador;
  2. perfil já idêntico não é rebaixado (sem tráfego à toa);
  3. hash divergente é DESCARTADO — é a defesa contra arquivo adulterado;
  4. nome de arquivo com travessia (`../`) é ignorado;
  5. conteúdo que não é perfil (HTML de erro, JSON truncado) é ignorado;
  6. servidor fora do ar não quebra nada e o app segue com o que tem;
  7. versão nova do app é anunciada, versão igual ou menor não.
"""
import os, sys, json, hashlib, shutil, tempfile, threading
from http.server import BaseHTTPRequestHandler, HTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import updater
import extract_engine as EE

falhas = []
def ok(cond, msg):
    print(f"    [{'OK ' if cond else 'FALHA'}] {msg}")
    if not cond:
        falhas.append(msg)


def perfil(pid, anchor="Prêmio Total"):
    return json.dumps({"id": pid, "label": pid, "match": [pid],
                       "fields": {"a_vista": {"anchor": anchor, "pick": "kv"}}},
                      ensure_ascii=False).encode("utf-8")


def sha(b):
    return hashlib.sha256(b).hexdigest()


# --------------------------------------------------------- servidor de mentira
ARQUIVOS = {}          # caminho -> bytes

class Mao(BaseHTTPRequestHandler):
    def do_GET(self):
        dados = ARQUIVOS.get(self.path)
        if dados is None:
            self.send_response(404); self.end_headers(); return
        self.send_response(200)
        self.send_header("Content-Length", str(len(dados)))
        self.end_headers(); self.wfile.write(dados)
    def log_message(self, *a): pass


srv = HTTPServer(("127.0.0.1", 0), Mao)
BASE = f"http://127.0.0.1:{srv.server_port}"
threading.Thread(target=srv.serve_forever, daemon=True).start()

tmp = tempfile.mkdtemp(prefix="upd-")
BASEDIR = os.path.join(tmp, "instalado")     # perfis que vieram no instalador
LOCAL = os.path.join(tmp, "baixados")        # perfis atualizados
os.makedirs(BASEDIR); os.makedirs(LOCAL)

# perfil que veio no instalador
antigo = perfil("porto", "Prêmio Total")
open(os.path.join(BASEDIR, "porto.json"), "wb").write(antigo)

novo = perfil("porto", "Valor Total do Seguro")
outro = perfil("zurich")

def manifesto(app="0.4.0", perfis=None, instalador=None):
    m = {"app": app, "perfis": perfis or {}}
    if instalador:
        m["instalador"] = instalador
    return json.dumps(m).encode("utf-8")


print(">> 1. perfil novo é baixado e se sobrepõe ao instalado")
ARQUIVOS["/versao.json"] = manifesto(perfis={"porto.json": sha(novo), "zurich.json": sha(outro)})
ARQUIVOS["/perfis/porto.json"] = novo
ARQUIVOS["/perfis/zurich.json"] = outro
r = updater.verificar(BASE, LOCAL, BASEDIR)
ok(r["ok"] and r["verificado"], "manifesto lido")
ok(sorted(r["perfis_atualizados"]) == ["porto.json", "zurich.json"], "os dois perfis baixados")
carregados = {p["id"]: p for p in EE.load_profiles(BASEDIR, LOCAL)}
ok(carregados["porto"]["fields"]["a_vista"]["anchor"] == "Valor Total do Seguro",
   "o perfil baixado tem precedência sobre o instalado")
ok(len(carregados) == 2, "o perfil só instalado continua disponível")

print(">> 2. nada a fazer quando já está igual")
r = updater.verificar(BASE, LOCAL, BASEDIR)
ok(r["perfis_atualizados"] == [], "segunda verificação não rebaixa nada")

print(">> 3. hash divergente é descartado")
adulterado = perfil("porto", "ANCORA MALICIOSA")
ARQUIVOS["/perfis/porto.json"] = adulterado          # conteúdo trocado, hash do manifesto não
r = updater.verificar(BASE, LOCAL, BASEDIR)
ok(r["perfis_atualizados"] == [], "arquivo com hash errado não é gravado")
atual = json.load(open(os.path.join(LOCAL, "porto.json"), encoding="utf-8"))
ok(atual["fields"]["a_vista"]["anchor"] == "Valor Total do Seguro", "o perfil em disco não foi tocado")
ARQUIVOS["/perfis/porto.json"] = novo

print(">> 4. nome de arquivo com travessia é ignorado")
mau = perfil("mau")
ARQUIVOS["/versao.json"] = manifesto(perfis={"../../server.py": sha(mau), "..\\evil.json": sha(mau)})
ARQUIVOS["/perfis/../../server.py"] = mau
r = updater.verificar(BASE, LOCAL, BASEDIR)
ok(r["perfis_atualizados"] == [], "nome fora do padrão não é baixado")
ok(not os.path.exists(os.path.join(tmp, "server.py")), "nada escrito fora da pasta de perfis")

print(">> 5. conteúdo que não é perfil é ignorado")
lixo = b"<html><body>404 Not Found</body></html>"
ARQUIVOS["/versao.json"] = manifesto(perfis={"lixo.json": sha(lixo)})
ARQUIVOS["/perfis/lixo.json"] = lixo
r = updater.verificar(BASE, LOCAL, BASEDIR)
ok(r["perfis_atualizados"] == [], "HTML com hash correto ainda assim é recusado")
ok(not os.path.exists(os.path.join(LOCAL, "lixo.json")), "não foi gravado")

print(">> 6. servidor fora do ar não quebra")
r = updater.verificar("https://127.0.0.1:1/", LOCAL, BASEDIR)
ok(r["ok"] is False and r["erro"] == "sem resposta", "falha silenciosa e informada")
r = updater.verificar("", LOCAL, BASEDIR)
ok(r["erro"] == "desligado", "URL vazia desliga a verificação")
ok(len(EE.load_profiles(BASEDIR, LOCAL)) == 2, "os perfis em disco continuam carregando")

print(">> 7. versão do app")
ARQUIVOS["/versao.json"] = manifesto(app="0.5.0", instalador="https://exemplo/inst.exe")
r = updater.verificar(BASE, LOCAL, BASEDIR)
ok(r["app_novo"] == "0.5.0" and r["instalador"] == "https://exemplo/inst.exe", "versão maior é anunciada")
ARQUIVOS["/versao.json"] = manifesto(app=updater.VERSION)
ok(updater.verificar(BASE, LOCAL, BASEDIR)["app_novo"] is None, "versão igual não é anunciada")
ARQUIVOS["/versao.json"] = manifesto(app="0.1.0")
ok(updater.verificar(BASE, LOCAL, BASEDIR)["app_novo"] is None, "versão menor nunca é oferecida")
ARQUIVOS["/versao.json"] = manifesto(app="0.9.0", instalador="http://exemplo/inst.exe")
ok(updater.verificar(BASE, LOCAL, BASEDIR)["instalador"] is None, "instalador fora de HTTPS é recusado")

srv.shutdown(); shutil.rmtree(tmp, ignore_errors=True)
print(f"\n  RESULTADO: {'OK' if not falhas else 'FALHOU -> ' + '; '.join(falhas)}")
sys.exit(1 if falhas else 0)
