# -*- coding: utf-8 -*-
"""Gravação do PDF da proposta — o defeito de 27/07/2026.

Sintoma: a pessoa clicava em gerar, a tela dizia "PDF gerado com sucesso" e
arquivo nenhum era criado. Numa corretora esse é o pior modo de falha possível:
achar que mandou a proposta e não ter mandado.

Causa: o PDF era entregue pelo download do navegador (`jsPDF.save()`), que numa
janela de aplicativo depende do delegate da casca — e o pywebview vem com
`ALLOW_DOWNLOADS: False`. O download morria em silêncio e a interface anunciava
sucesso do mesmo jeito, porque o aviso vinha logo depois da chamada, sem
verificar nada.

Correção: o PDF é enviado ao servidor local, que grava e devolve o caminho. O
sucesso passa a ser verificável — e o mesmo caminho vale em Windows e macOS.

O que fica provado aqui:
  1. sem sessão não grava;
  2. grava e o arquivo existe em disco, com o tamanho exato;
  3. o que não é PDF é recusado;
  4. nome com travessia de caminho não escapa da pasta;
  5. envio repetido não sobrescreve a proposta anterior.
"""
import json, os, sys, threading, urllib.error, urllib.request
from http.server import ThreadingHTTPServer

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import server
import fitz

falhas = []
def ok(cond, msg):
    # sem flush, uma queda mais adiante leva junto o que já foi impresso e o teste
    # aparece no relatório sem uma linha sequer explicando onde parou
    print(f"    [{'OK ' if cond else 'FALHA'}] {msg}", flush=True)
    if not cond:
        falhas.append(msg)

httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.H)
U = f"http://127.0.0.1:{httpd.server_address[1]}"
threading.Thread(target=httpd.serve_forever, daemon=True).start()

criados = []

def enviar(dados, nome="teste-export.pdf", cookie=None):
    h = {"Content-Type": "application/pdf", "X-Nome-Arquivo": nome}
    if cookie:
        h["Cookie"] = cookie
    r = urllib.request.Request(U + "/api/save-pdf", dados, h)
    try:
        with urllib.request.urlopen(r, timeout=8) as x:
            return x.status, json.loads(x.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


def pdf_de_verdade(altura=1400):
    d = fitz.open(); d.new_page(width=595, height=altura)
    b = d.tobytes(); d.close(); return b


print(">> 1. sem sessão não grava")
ok(enviar(pdf_de_verdade())[0] == 401, "responde 401 sem login")

# Falhar aqui com AttributeError deixava o teste sem nenhuma saída, e o relatório
# só dizia FALHOU — sem pista do motivo. Erro de login é uma condição própria.
try:
    r = urllib.request.Request(U + "/api/login",
                               json.dumps({"username": "Madu", "password": "123"}).encode(),
                               {"Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=15) as x:
        CK = (x.headers.get("Set-Cookie") or "").split(";")[0]
    if not CK:
        raise RuntimeError("o login não devolveu cookie de sessão")
except Exception as e:
    print(f"\n  RESULTADO: FALHOU -> não consegui autenticar para testar: {e}", flush=True)
    httpd.shutdown()
    sys.exit(1)

print(">> 2. grava de verdade, e o sucesso é verificável")
dados = pdf_de_verdade()
st, res = enviar(dados, cookie=CK)
criados.append(res.get("path"))
ok(st == 200 and res.get("ok"), "responde 200")
ok(res.get("path") and os.path.exists(res["path"]), "o arquivo existe em disco")
ok(os.path.getsize(res["path"]) == len(dados), "gravado por inteiro, byte a byte")
ok(res.get("bytes") == len(dados), "o tamanho informado bate com o enviado")

print(">> 3. o que não é PDF é recusado")
ok(enviar(b"<html>pagina de erro</html>", cookie=CK)[0] == 400, "HTML recusado")
ok(enviar(b"", cookie=CK)[0] == 400, "corpo vazio recusado")

print(">> 4. nome de arquivo não escapa da pasta")
st, res = enviar(dados, nome="../../evil.pdf", cookie=CK)
criados.append(res.get("path"))
ok(os.path.dirname(res.get("path", "")) == res.get("pasta"), "gravado dentro da pasta de propostas")
ok(".." not in os.path.basename(res.get("nome", "..")), "os pontos-pontos saíram do nome")
st, res = enviar(dados, nome="C:\\Windows\\System32\\x.pdf", cookie=CK)
criados.append(res.get("path"))
ok(os.path.dirname(res.get("path", "")) == res.get("pasta"), "caminho absoluto também é contido")

print(">> 5. não sobrescreve proposta anterior")
st, a = enviar(dados, nome="repetido.pdf", cookie=CK); criados.append(a.get("path"))
st, b = enviar(dados, nome="repetido.pdf", cookie=CK); criados.append(b.get("path"))
ok(a["path"] != b["path"], "o segundo ganha nome próprio")
ok(os.path.exists(a["path"]) and os.path.exists(b["path"]), "os dois seguem em disco")
ok(b["nome"].endswith(").pdf"), f"sufixo numerado: {b['nome']}")

for p in criados:
    try: os.remove(p)
    except Exception: pass
httpd.shutdown()
print(f"\n  RESULTADO: {'OK' if not falhas else 'FALHOU -> ' + '; '.join(falhas)}")
sys.exit(1 if falhas else 0)
