# -*- coding: utf-8 -*-
"""Roda toda a suíte. Sai com código != 0 se qualquer teste reprovar.

    python tests/run_all.py

Nenhum teste chama a OpenAI: a camada de IA é substituída por um duplo em todos
eles, então a suíte roda de graça e sem rede.
"""
import os, subprocess, sys

TESTS = os.path.dirname(os.path.abspath(__file__))
ORDEM = ["test_traversal.py", "test_cobertura.py", "test_multioferta.py",
         "test_verificacao_ia.py", "test_validacao_pdf.py", "test_updater.py"]

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

res = []
for t in ORDEM:
    p = os.path.join(TESTS, t)
    if not os.path.exists(p):
        continue
    print("\n" + "=" * 74)
    print(">>", t)
    print("=" * 74)
    r = subprocess.run([sys.executable, p], cwd=TESTS)
    res.append((t, r.returncode))

print("\n" + "=" * 74)
print("RESUMO")
print("=" * 74)
for t, rc in res:
    print(f"  {'PASSOU' if rc == 0 else 'FALHOU'}  {t}")
falhas = sum(1 for _, rc in res if rc != 0)
print(f"\n{len(res) - falhas}/{len(res)} testes passaram")
sys.exit(1 if falhas else 0)
