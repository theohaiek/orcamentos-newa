# -*- coding: utf-8 -*-
"""As rotas públicas não podem servir arquivo fora da sua raiz.

`/assets/` e `/data/` são as únicas rotas servidas antes do login. Sem contenção
de caminho, `/assets/../../../.env` entregava a chave da OpenAI e o hash de senha.

O teste NÃO imprime conteúdo de arquivo — só o status e se o corpo carrega
assinatura de segredo.
"""
import re, socket, sys, threading, time
import _base

_base.exige_motor()
import server as S

PORT = 8197
srv = S.ThreadingHTTPServer(("127.0.0.1", PORT), S.H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
time.sleep(0.4)


def raw(path):
    s = socket.create_connection(("127.0.0.1", PORT), 3)
    s.sendall(("GET " + path + " HTTP/1.0\r\nHost: localhost\r\n\r\n").encode())
    buf = b""
    while True:
        try:
            c = s.recv(65536)
        except Exception:
            break
        if not c:
            break
        buf += c
    s.close()
    txt = buf.decode("utf-8", "replace")
    head, _, body = txt.partition("\r\n\r\n")
    status = head.splitlines()[0] if head else "(sem resposta)"
    vazou = bool(re.search(r"sk-[A-Za-z0-9_-]{16}", body)) or "OPENAI_API_KEY" in body \
        or '"pw"' in body
    return status, len(body), vazou


FUGAS = [
    "/assets/../../../.env",
    "/assets/../../.devdata/users.json",
    "/data/../../.env",
    "/data/../../../.env",
    "/assets/..%2f..%2f..%2f.env",
    "/assets/....//....//....//.env",
    "/data/profiles/../../../.env",
]
LEGITIMOS = ["/assets/app.js", "/assets/app.css", "/data/insurers.json",
             "/data/profiles/porto.json"]

falhas = 0
print("== tentativas de fuga (esperado 404, sem vazamento) ==")
for a in FUGAS:
    st, n, vazou = raw(a)
    ok = ("404" in st) and not vazou
    falhas += 0 if ok else 1
    print(f"  [{'OK ' if ok else 'FALHA'}] {a:<44} {st:<24} vazou={vazou}")

print("\n== arquivos legítimos (esperado 200) ==")
for a in LEGITIMOS:
    st, n, _ = raw(a)
    ok = "200" in st and n > 0
    falhas += 0 if ok else 1
    print(f"  [{'OK ' if ok else 'FALHA'}] {a:<44} {st:<24} {n}B")

srv.shutdown()
print("\nRESULTADO:", "OK" if falhas == 0 else f"{falhas} FALHA(S)")
sys.exit(1 if falhas else 0)
