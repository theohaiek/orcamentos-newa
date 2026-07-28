# -*- coding: utf-8 -*-
"""Sincronização do programa — os dois defeitos de 28/07/2026.

Aconteceram juntos, e o efeito somado é o pior possível: **o app não abre mais**.

1. **A lista de arquivos envelhecia junto com o updater instalado.** Ela era uma
   constante no `updater.py`. Quando o `auth.py` entrou e o `server.py` passou a
   importá-lo, o updater da versão instalada baixou o `server.py` novo e ignorou o
   arquivo que ele passou a precisar — porque a lista dele, antiga, não o conhecia.
   A instalação ficou com um repositório que não importa. Agora a lista viaja
   DENTRO do pacote (`data/sincronizar.json`), então quem descreve o conjunto é
   sempre a versão que está sendo instalada.

2. **A rede de proteção não protegia.** O `app.py` já tinha o "se o repositório
   quebrar, use a cópia embutida" — mas fazia `sys.path.remove(repo)`, que tira UMA
   ocorrência. O `app.py` do repositório insere a própria pasta no `sys.path`, então
   havia duas: a que sobrava fazia o código "embutido" continuar importando do
   repositório quebrado, e o programa morria com o mesmo erro. Medido: o executável
   instalado deixou de abrir.
"""
import io, json, os, sys, tempfile, threading, types, zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import updater

falhas = []
def ok(cond, msg):
    print(f"    [{'OK ' if cond else 'FALHA'}] {msg}", flush=True)
    if not cond:
        falhas.append(msg)


# ------------------------------------------------------------- zip de mentira
PACOTE = {"bytes": b""}

class Mao(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    def do_GET(self):
        b = PACOTE["bytes"]
        self.send_response(200)
        self.send_header("Content-Type", "application/zip")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers(); self.wfile.write(b)
    def log_message(self, *a): pass


srv = ThreadingHTTPServer(("127.0.0.1", 0), Mao)
URL = f"http://127.0.0.1:{srv.server_address[1]}/main.zip"
threading.Thread(target=srv.serve_forever, daemon=True).start()


def monta(arquivos, lista=None):
    """Monta um zip no formato do GitHub: tudo dentro de '<repo>-main/'."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for nome, conteudo in arquivos.items():
            z.writestr("orcamentos-newa-main/" + nome, conteudo)
        if lista is not None:
            z.writestr("orcamentos-newa-main/" + updater.LISTA_NO_PACOTE,
                       json.dumps(lista, ensure_ascii=False))
    PACOTE["bytes"] = buf.getvalue()


def pasta():
    return tempfile.mkdtemp(prefix="sinc-")


BASE = {"server.py": "import auth\n", "auth.py": "X = 1\n",
        "app.py": "pass\n", "extract_engine.py": "pass\n",
        "updater.py": "pass\n", "index.html": "<html>"}

print(">> 1. o caso real: arquivo novo citado só pela lista do pacote")
ok("auth.py" not in ("app.py", "server.py"), "cenário: auth.py é o arquivo novo")
d = pasta()
monta({**BASE, "novo_modulo_x.py": "Y = 2\n"},
      lista={"arquivos": ["app.py", "server.py", "auth.py", "novo_modulo_x.py"]})
r = updater.sincronizar_repo(d, URL)
ok(r["ok"] and r.get("lista") == "pacote", f"a lista veio do pacote: {r.get('lista')}")
ok(os.path.exists(os.path.join(d, "auth.py")), "auth.py foi baixado junto do server.py")
ok(os.path.exists(os.path.join(d, "novo_modulo_x.py")),
   "arquivo que a lista EMBUTIDA não conhece também chega")
ok(not os.path.exists(os.path.join(d, "index.html")),
   "e o que a lista do pacote não cita não é escrito")

print(">> 2. sem a lista no pacote, vale a embutida")
d = pasta()
monta(dict(BASE, README_x=".."), lista=None)
r = updater.sincronizar_repo(d, URL)
ok(r.get("lista") == "embutida", f"cai na embutida: {r.get('lista')}")
ok(os.path.exists(os.path.join(d, "server.py")), "o essencial continua chegando")
ok(not os.path.exists(os.path.join(d, "README_x")), "o que não é do programa fica de fora")

print(">> 3. lista inválida não é obedecida")
for rotulo, conteudo in (("não é lista", {"arquivos": "server.py"}),
                         ("lista vazia", {"arquivos": []}),
                         ("sem a chave", {"outra": ["server.py"]}),
                         ("longa demais", {"arquivos": [f"f{i}.py" for i in range(400)]})):
    d = pasta()
    monta(BASE, lista=conteudo)
    r = updater.sincronizar_repo(d, URL)
    ok(r.get("lista") == "embutida", f"{rotulo} -> usa a embutida")

print(">> 4. a lista do pacote NÃO consegue escrever fora da pasta")
d = pasta()
fora = os.path.join(os.path.dirname(d), "ESCAPOU.txt")
monta({"server.py": "ok", "../ESCAPOU.txt": "invasor"},
      lista={"arquivos": ["server.py", "../ESCAPOU.txt", "..\\ESCAPOU.txt", "/etc/passwd"]})
r = updater.sincronizar_repo(d, URL)
ok(not os.path.exists(fora), "travessia continua barrada, venha a lista de onde vier")
ok(os.path.exists(os.path.join(d, "server.py")), "e o arquivo legítimo é gravado")

print(">> 5. a lista sempre inclui a si mesma")
d = pasta()
monta(BASE, lista={"arquivos": ["server.py"]})          # de propósito, sem citar-se
updater.sincronizar_repo(d, URL)
ok(os.path.exists(os.path.join(d, *updater.LISTA_NO_PACOTE.split("/"))),
   "senão a próxima sincronização voltaria a não ter a lista")

print(">> 6. desfazer uma delegação limpa TUDO (era o furo da rede de proteção)")
import app                                              # não roda main(); só define
repo = os.path.abspath(pasta())
sys.path.insert(0, repo)
sys.path.insert(0, repo)                                # duas vezes, como acontecia
falso = types.ModuleType("modulo_do_repo_x")
falso.__file__ = os.path.join(repo, "modulo_do_repo_x.py")
sys.modules["modulo_do_repo_x"] = falso
app._desfazer(repo)
ok(not [p for p in sys.path if os.path.abspath(p) == repo],
   "nenhuma ocorrência do repo sobra no sys.path")
ok("modulo_do_repo_x" not in sys.modules, "módulo meio-importado do repo sai do cache")
ok("os" in sys.modules and "json" in sys.modules, "e nada além do repo é removido")

srv.shutdown()
print(f"\n  RESULTADO: {'OK' if not falhas else 'FALHOU -> ' + '; '.join(falhas)}")
sys.exit(1 if falhas else 0)
