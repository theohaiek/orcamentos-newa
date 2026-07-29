# -*- coding: utf-8 -*-
"""Cotação com várias ofertas lado a lado tem que ser detectada.

Escolher a coluna da esquerda em silêncio publicou uma Allianz como
"Colisão/Incêndio/Roubo 100% FIPE" quando aquele plano é "Roubo e Furto" e o
próprio PDF diz que não vale para colisão.

O detector também não pode disparar no que NÃO é multi-oferta:
  - aliro/yelum repetem o MESMO total em 4 formas de pagamento;
  - darwin/bradesco trazem decomposição de prêmio (líquido, IOF, desconto).
"""
import sys
import _base

_base.exige_motor(); _base.exige_amostras()
import extract_engine as EE
import server as S

ESPERADO = {"allianz.pdf": 3, "hdi.pdf": 2}     # conferido à mão nos documentos

falhas = 0
print(f"{'arquivo':<15}{'esperado':>9}{'detectado':>11}  trecho")
print("-" * 92)
for f in _base.pdfs():
    pages = EE.tokenize(_base.ler(f))
    off = S.detect_offers(pages)
    got = off["n"] if off else 0
    exp = ESPERADO.get(f, 0)
    ok = got == exp
    falhas += 0 if ok else 1
    print(f"{f:<15}{exp:>9}{got:>11}  {'[OK]' if ok else '[FALHA]'} "
          f"{(off or {}).get('trecho', '')[:54]}")

print("-" * 92)

# ---------------------------------------------------------- escolha da oferta
# A escolha de plano existe para trocar o valor exibido, e a regra que a torna
# segura é esta: a coluna 1 tem que ser EXATAMENTE o que a extração já entregava.
# Se um dia isso deixar de valer, escolher o plano 1 mudaria valores sem que
# ninguém tivesse pedido — e aí a funcionalidade estaria piorando a extração.
print("\n>> escolher a oferta não altera o que a extração já entregava")


def ok(cond, msg):
    global falhas
    print(f"    [{'OK ' if cond else 'FALHA'}] {msg}", flush=True)
    if not cond:
        falhas += 1


import json

for arq in ("allianz.pdf", "hdi.pdf", "porto.pdf"):
    if arq not in _base.pdfs():
        continue
    r = S.extract_pdf(_base.ler(arq), arq)
    of = r.get("ofertas")
    if not ESPERADO.get(arq):
        ok(not of, f"{arq}: sem multi-oferta, sem seletor de plano")
        continue
    por_campo = (of or {}).get("por_campo") or {}
    ok(bool(por_campo), f"{arq}: {len(por_campo)} campo(s) com valor por coluna")
    iguais = all(por_campo[k][0] == r["fields"][k] for k in por_campo)
    ok(iguais, f"{arq}: a coluna 1 é idêntica ao valor já extraído")
    ok(all(len(v) == of["n"] for v in por_campo.values()),
       f"{arq}: cada campo traz um valor por oferta ({of['n']})")
    ok(all(r["provenance"][k]["confidence"] == "baixa" for k in por_campo),
       f"{arq}: os campos seguem exigindo confirmação")
    try:
        json.dumps(r); serializa = True
    except Exception:
        serializa = False
    ok(serializa, f"{arq}: o payload continua serializável")

print("\nRESULTADO:", "OK" if falhas == 0 else f"{falhas} DIVERGÊNCIA(S)")
sys.exit(1 if falhas else 0)
