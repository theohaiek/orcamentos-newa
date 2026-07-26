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
print("RESULTADO:", "OK" if falhas == 0 else f"{falhas} DIVERGÊNCIA(S)")
sys.exit(1 if falhas else 0)
