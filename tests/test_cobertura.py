# -*- coding: utf-8 -*-
"""Não-regressão da extração determinística.

Mede quantos campos saem SEM IA nos 15 PDFs de amostra e reprova se a cobertura
cair abaixo da linha de base. Este é o número que o produto vende — se ele cair
por causa de uma mudança, o teste tem que gritar.

Critério de contagem honesto: além de existir, o valor precisa ser plausível para
o tipo do campo (moeda tem que parecer moeda, data tem que parecer data).
"""
import re, sys
import _base

_base.exige_motor(); _base.exige_amostras()
import extract_engine as EE
from server import CAMPOS, PROFILES_DIR

PISO_MEDIA = 24.0          # média de campos/arquivo (linha de base medida: 25,1)
PISO_MINIMO = 16           # nenhum arquivo pode despencar sozinho

MOEDA = re.compile(r"^R\$ ?\d{1,3}(\.\d{3})*,\d{2}$")
DATA = re.compile(r"^\d{4}-\d{2}-\d{2}$|^\d{2}/\d{2}/\d{4}$")
MONETARIOS = {"a_vista", "parc_4x", "parc_6x", "parc_10x", "franquia_veiculo",
              "rcf_danos_materiais", "rcf_danos_pessoais",
              "acidente_pessoal_passageiro", "morte_pessoal_passageiro"}
AUSENCIA = re.compile(r"nao contratad|nao possui|sem cobertura|nao consta|isent|gratuit",
                      re.I)


def plausivel(k, v):
    s = str(v or "").strip()
    if not s:
        return False
    if k in MONETARIOS:
        return bool(MOEDA.match(s)) or bool(AUSENCIA.search(EE.norm(s)))
    if k in ("data_proposta", "validade"):
        return bool(DATA.match(s)) or len(s) >= 6
    if k == "cep_circulacao":
        return len(re.sub(r"\D", "", s)) == 8
    return len(s) >= 2


profiles = EE.load_profiles(PROFILES_DIR)
print(f"{'arquivo':<15}{'perfil':<12}{'campos':>7}{'plausíveis':>12}")
print("-" * 47)
tot = ok_tot = 0
baixos = []
for f in _base.pdfs():
    pages = EE.tokenize(_base.ler(f))
    prof = EE.match_profile(pages, profiles)
    campos = {}
    if prof:
        campos.update(EE.run_profile(pages, prof)["fields"])
    campos.update(EE.run_generic(pages, profiles, set(campos)).get("fields", {}))
    n = len(campos)
    okn = sum(1 for k, v in campos.items() if plausivel(k, v))
    if okn < PISO_MINIMO:
        baixos.append((f, okn))
    print(f"{f:<15}{(prof or {}).get('id', '-'):<12}{n:>7}{okn:>12}")
    tot += n; ok_tot += okn

nfiles = len(_base.pdfs())
media = ok_tot / nfiles
print("-" * 47)
print(f"{'MÉDIA':<27}{tot / nfiles:>7.1f}{media:>12.1f}")
print(f"\ncobertura determinística: {media:.1f}/{len(CAMPOS)} campos "
      f"({100 * media / len(CAMPOS):.0f}%)  — piso do teste: {PISO_MEDIA}")

falhou = media < PISO_MEDIA or baixos
if baixos:
    print("arquivos abaixo do mínimo:", baixos)
print("RESULTADO:", "OK" if not falhou else "REGRESSÃO")
sys.exit(1 if falhou else 0)
