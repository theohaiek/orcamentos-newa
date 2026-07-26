# -*- coding: utf-8 -*-
"""Um valor inventado pela IA não pode ser carimbado como "verificado".

A verificação antiga aceitava o valor se a string existisse em QUALQUER lugar do
documento. Injetando "R$ 200.000,00" (que existe em quase toda cotação como LMI
de RCF) em todos os campos vazios, 85 de 89 alucinações passavam como verificadas.

Meta: zero. Toda alucinação tem que cair em "a confirmar".
"""
import sys
import _base

_base.exige_motor(); _base.exige_amostras()
import server as S

ALVO = "R$ 200.000,00"
S._ai_extract = lambda texto, filename, cfg, key, only_keys=None: {
    k: ALVO for k in (only_keys or [])}
_cfg = S.get_config
S.get_config = lambda: dict(_cfg(), openai_key="x-teste")

print(f"{'arquivo':<15}{'injetados':>10}{'verificados':>13}{'a confirmar':>13}")
print("-" * 51)
tot_inj = tot_ver = tot_bx = 0
vazou = []
for f in _base.pdfs():
    r = S.extract_pdf(_base.ler(f), f)
    prov = r["provenance"]
    inj = [k for k, p in prov.items() if p.get("method") in ("ai", "ausente")]
    ver = [k for k in inj if prov[k].get("method") == "ai"
           and prov[k].get("confidence") == "verificada"]
    bx = [k for k in inj if prov[k].get("confidence") == "baixa"]
    if ver:
        vazou.append((f, ver))
    print(f"{f:<15}{len(inj):>10}{len(ver):>13}{len(bx):>13}")
    tot_inj += len(inj); tot_ver += len(ver); tot_bx += len(bx)

print("-" * 51)
print(f"{'TOTAL':<15}{tot_inj:>10}{tot_ver:>13}{tot_bx:>13}")
if vazou:
    print("\nALUCINAÇÕES ACEITAS COMO VERIFICADAS:")
    for f, ks in vazou:
        print(f"  {f}: {ks}")
print("\nRESULTADO:", "OK" if tot_ver == 0 else f"{tot_ver} FALSO(S)-VERIFICADO(S)")
sys.exit(1 if tot_ver else 0)
