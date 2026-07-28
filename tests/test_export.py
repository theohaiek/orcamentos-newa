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

print(">> 6. recusa com PDF grande chega como resposta, não como queda de conexão")
# O servidor respondia 401/400 SEM ler o corpo. A conexão é HTTP/1.1 com
# keep-alive, então os bytes do PDF ficavam no socket; o handler voltava ao laço,
# lia o PDF como se fosse a requisição seguinte, respondia 400 e fechava com
# dados ainda por ler. No Windows fechar assim manda RST, e o RST descarta a
# resposta que o cliente ainda não tinha lido -> WinError 10053.
# Com 500 bytes falhava 2 vezes em 12 (era a intermitência desta suíte); com 2 MB,
# 12 em 12 — ou seja, sessão expirada + proposta real = erro de rede sempre, em
# vez do 401 que a tela sabe explicar.
grande = pdf_de_verdade() + b"\n% " + b"x" * 3_000_000

def status(rota, dados, cabecalhos, timeout=30):
    try:
        req = urllib.request.Request(U + rota, dados, cabecalhos)
        with urllib.request.urlopen(req, timeout=timeout) as x:
            x.read(); return x.status
    except urllib.error.HTTPError as e:
        e.read(); return e.code
    except Exception as e:
        return type(e).__name__

r = [status("/api/save-pdf", grande,
            {"Content-Type": "application/pdf", "X-Nome-Arquivo": "grande.pdf"})
     for _ in range(5)]
ok(all(x == 401 for x in r), f"sem sessão, 5 envios de 3 MB: todos 401 -> {r}")

r = [status("/api/extract", grande,
            {"Content-Type": "multipart/form-data", "Cookie": CK})  # sem boundary
     for _ in range(3)]
ok(all(x == 400 for x in r), f"upload malformado de 3 MB: todos 400 -> {r}")

for p in criados:
    try: os.remove(p)
    except Exception: pass
httpd.shutdown()
print(f"\n  RESULTADO: {'OK' if not falhas else 'FALHOU -> ' + '; '.join(falhas)}")
sys.exit(1 if falhas else 0)
