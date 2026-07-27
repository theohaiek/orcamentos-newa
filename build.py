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
SAIDA = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(AQUI, "dist")
TRABALHO = os.path.join(AQUI, "build")

# origem (relativa ao repo) -> destino dentro do pacote
DADOS = [
    ("orcamentos-newa/assets", "orcamentos-newa/assets"),
    ("data", "data"),
    ("index.html", "."),
]


def main():
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
