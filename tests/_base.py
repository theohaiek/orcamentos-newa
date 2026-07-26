# -*- coding: utf-8 -*-
"""Base comum dos testes: localiza o motor e os PDFs de amostra.

O motor (`server.py`, `extract_engine.py`) vive na raiz do repositório. Os PDFs de
amostra ficam na pasta-pai, fora do versionamento (contêm dados reais).
"""
import os, sys

TESTS = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(TESTS)                   # raiz do repositório: onde está o motor
HERE = os.path.dirname(REPO)                    # pasta-pai: .env, .devdata, amostras
INPUTS = os.path.join(HERE, "Modelo-Inputs")

if REPO not in sys.path:
    sys.path.insert(0, REPO)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def exige_motor():
    if not os.path.exists(os.path.join(REPO, "server.py")):
        print(f"SKIP: server.py não encontrado em {REPO}")
        sys.exit(0)


def exige_amostras():
    if not os.path.isdir(INPUTS):
        print(f"SKIP: pasta de amostras não encontrada em {INPUTS}")
        sys.exit(0)


def pdfs():
    return [f for f in sorted(os.listdir(INPUTS)) if f.lower().endswith(".pdf")]


def ler(nome):
    return open(os.path.join(INPUTS, nome), "rb").read()
