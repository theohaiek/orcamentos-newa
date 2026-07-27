# -*- coding: utf-8 -*-
"""Empacota o app num executável Windows.

    python build.py [pasta-de-saida]

Sem argumento, sai em `dist/` aqui do lado.

Gera uma PASTA, não um arquivo único. Arquivo único parece mais limpo mas é pior
na prática: ele se descompacta num diretório temporário a cada abertura, o que
soma segundos de espera toda vez e é o padrão que mais dispara falso positivo de
antivírus. Como quem recebe vê só o instalador, a pasta não aparece para ninguém.

O que entra junto do código: os assets da interface, os perfis de extração, o
`index.html` e o ícone. O que NÃO entra: `.env`, `.devdata`, PDFs de amostra —
nada disso é do programa, é da máquina de quem desenvolve.
"""
import os, shutil, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
NOME = "Orcamentos NEWA"
ICONE = os.path.join(AQUI, "orcamentos-newa", "assets", "app.ico")
_livres = [a for a in sys.argv[1:] if not a.startswith("--")]
SAIDA = os.path.abspath(_livres[0]) if _livres else os.path.join(AQUI, "dist")
TRABALHO = os.path.join(AQUI, "build")

EXCLUIR = [
    "torch", "torchvision", "torchaudio", "llvmlite", "numba", "onnxruntime",
    "scipy", "pandas", "matplotlib", "sklearn", "cv2", "av", "imageio",
    "imageio_ffmpeg", "transformers", "tokenizers", "datasets", "sympy",
    "networkx", "IPython", "jupyter", "notebook", "nbformat", "nbconvert",
    "pytest", "PyQt5", "PyQt6", "PySide2", "PySide6", "tkinter", "test",
    "sqlite3", "lib2to3", "pydoc_data", "setuptools", "pip", "wheel",
    "numpy", "PIL", "lxml", "cryptography", "pytz", "dateutil", "yaml",
]

# origem (relativa ao repo) -> destino dentro do pacote
DADOS = [
    ("orcamentos-newa/assets", "orcamentos-newa/assets"),
    ("data", "data"),
    ("index.html", "."),
]


def build_instalador(saida):
    """O instalador é um executável à parte, e de propósito pequeno.

    Ele não embute PyMuPDF nem o resto: só precisa de `zipfile` e `urllib`, ambos
    da biblioteca padrão. Assim ele cabe no repositório sem inchar o histórico, e
    quem baixa só o instalador baixa poucos megabytes.
    """
    cmd = [sys.executable, "-m", "PyInstaller", "instalador.py",
           "--name", "Instalar Orcamentos NEWA",
           "--noconfirm", "--clean", "--onefile", "--console",
           "--icon", ICONE,
           "--distpath", saida,
           "--workpath", os.path.join(TRABALHO, "inst"),
           "--specpath", os.path.join(TRABALHO, "inst")]
    for m in EXCLUIR + ["pymupdf", "fitz", "openai", "webview", "pydantic", "httpx"]:
        cmd += ["--exclude-module", m]
    print("\n  empacotando o instalador\n")
    return subprocess.run(cmd, cwd=AQUI).returncode


def main():
    if "--instalador" in sys.argv:
        return build_instalador(SAIDA)
    if not os.path.exists(ICONE):
        print(f"!! ícone não encontrado: {ICONE}")
        return 1
    for origem, _ in DADOS:
        if not os.path.exists(os.path.join(AQUI, origem)):
            print(f"!! faltando: {origem}")
            return 1

    cmd = [sys.executable, "-m", "PyInstaller", "app.py",
           "--name", NOME,
           "--noconfirm", "--clean", "--windowed",     # sem janela de console
           "--icon", ICONE,
           "--distpath", SAIDA,
           "--workpath", TRABALHO,
           "--specpath", TRABALHO]
    for origem, destino in DADOS:
        cmd += ["--add-data", f"{os.path.join(AQUI, origem)}{os.pathsep}{destino}"]
    # O pywebview escolhe o backend em tempo de execução, então o PyInstaller não
    # enxerga esses imports percorrendo o código.
    for m in ("webview.platforms.winforms", "clr_loader", "pythonnet"):
        cmd += ["--hidden-import", m]
    # Sem isto o pacote sai com 942 MB. O PyInstaller segue imports opcionais das
    # bibliotecas e acaba arrastando o que estiver instalado no Python da máquina —
    # aqui vieram torch (365 MB), llvmlite, ffmpeg, scipy, onnxruntime, pandas...
    # O app usa PyMuPDF, o cliente da OpenAI e o pywebview. Nada disso entra.
    for m in EXCLUIR:
        cmd += ["--exclude-module", m]

    print(f"  empacotando em {SAIDA}\n")
    r = subprocess.run(cmd, cwd=AQUI)
    if r.returncode != 0:
        return r.returncode

    exe = os.path.join(SAIDA, NOME, NOME + ".exe")
    if not os.path.exists(exe):
        print(f"\n!! o executável não apareceu em {exe}")
        return 1
    tam = sum(os.path.getsize(os.path.join(r_, f))
              for r_, _, fs in os.walk(os.path.join(SAIDA, NOME)) for f in fs)
    print(f"\n  {exe}\n  {tam / 1024 / 1024:.0f} MB na pasta")
    shutil.rmtree(TRABALHO, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
