# -*- coding: utf-8 -*-
"""Roda toda a suíte. Sai com código != 0 se qualquer teste reprovar.

    python tests/run_all.py

Nenhum teste chama a OpenAI: a camada de IA é substituída por um duplo em todos
eles, então a suíte roda de graça e sem rede.
"""
import os, shutil, subprocess, sys

TESTS = os.path.dirname(os.path.abspath(__file__))
ORDEM = ["test_traversal.py", "test_cobertura.py", "test_multioferta.py",
         "test_verificacao_ia.py", "test_validacao_pdf.py", "test_updater.py",
         "test_pendencias.js"]

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
    # os testes de interface rodam no Node; se ele nao existir, sao PULADOS
    # de forma VISIVEL, para ninguem ler a suite verde como cobertura completa.
    if t.endswith(".js"):
        if not shutil.which("node"):
            print("   PULADO: Node.js nao encontrado -- a interface nao foi testada")
            res.append((t, -1)); continue
        r = subprocess.run(["node", p], cwd=TESTS)
    else:
        r = subprocess.run([sys.executable, p], cwd=TESTS)
    res.append((t, r.returncode))

print("\n" + "=" * 74)
print("RESUMO")
print("=" * 74)
for t, rc in res:
    print(f"  {'PASSOU' if rc == 0 else ('PULADO' if rc == -1 else 'FALHOU')}  {t}")
falhas = sum(1 for _, rc in res if rc > 0)
print(f"\n{len(res) - falhas}/{len(res)} testes passaram")
sys.exit(1 if falhas else 0)
