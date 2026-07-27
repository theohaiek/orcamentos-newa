# -*- coding: utf-8 -*-
"""Instalador do Orçamentos NEWA.

Um executável só, que serve a três situações e descobre sozinho em qual está:

1. **Junto do pacote completo** — o instalador está numa pasta que já tem o
   programa (veio no `.zip`, ou de um `git clone` com o build ao lado). Copia do
   disco, não baixa nada, e não duplica: o que já está igual é deixado como está.
2. **Sozinho** — só o instalador. Baixa o pacote do repositório público no GitHub.
3. **Reinstalando por cima** — já existe instalação. Atualiza o que mudou e
   preserva usuários, configuração e propostas, que moram em outra pasta.

Onde instala: `%LOCALAPPDATA%\\OrcamentosNEWA`. É pasta do usuário, então **não
pede senha de administrador** — e é gravável, o que importa porque o programa se
atualiza sozinho depois.

O que fica em disco:

    %LOCALAPPDATA%\\OrcamentosNEWA\\
    ├─ app\\           o programa (Python embutido; só muda em versão nova)
    ├─ repo\\          o codigo e os perfis (é o que a atualização automática sincroniza)
    └─ (dados do usuário ficam na raiz: usuários, configuração, propostas)

Atalhos: Área de Trabalho e Menu Iniciar.

    python instalador.py [--silencioso] [--destino PASTA]
"""
import os, shutil, sys, tempfile, zipfile

AQUI = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, "frozen", False) else __file__))
NOME = "Orçamentos NEWA"
EXE = "Orcamentos NEWA.exe"
PASTA_APP = "Orcamentos NEWA"          # nome da pasta gerada pelo build

REPO_ZIP = "https://codeload.github.com/theohaiek/orcamentos-newa/zip/refs/heads/main"
RELEASE = "https://github.com/theohaiek/orcamentos-newa/releases/latest/download/orcamentos-newa-app.zip"

# Arquivos e pastas do repositório que o programa precisa em disco para rodar e
# para se manter atualizado. O resto (testes, documentação, build) não vai junto.
DO_REPO = ["app.py", "server.py", "extract_engine.py", "updater.py", "index.html",
           "data", "orcamentos-newa"]


def diga(msg=""):
    print(msg, flush=True)


# --------------------------------------------------------------- localizar origem
def achar_local(nomes, raiz=None):
    """Procura uma pasta/arquivo ao lado do instalador, e um nível acima."""
    for base in ([raiz] if raiz else [AQUI, os.path.dirname(AQUI)]):
        for n in nomes:
            p = os.path.join(base, n)
            if os.path.exists(p):
                return p
    return None


def origem_do_app():
    """A pasta do programa já está aqui? Devolve o caminho, ou None."""
    for cand in (achar_local([PASTA_APP, os.path.join("app", PASTA_APP), "app"]),):
        if cand and os.path.exists(os.path.join(cand, EXE)):
            return cand
    return None


def origem_do_repo():
    """O código-fonte já está aqui? Devolve a raiz do repositório, ou None."""
    for base in (AQUI, os.path.dirname(AQUI), os.path.join(AQUI, "repo")):
        if all(os.path.exists(os.path.join(base, n)) for n in ("server.py", "extract_engine.py", "data")):
            return base
    return None


def baixar(url, destino, rotulo):
    import urllib.request
    diga(f"  baixando {rotulo}…")
    req = urllib.request.Request(url, headers={"User-Agent": "OrcamentosNEWA-instalador"})
    with urllib.request.urlopen(req, timeout=120) as r, open(destino, "wb") as f:
        total = int(r.headers.get("Content-Length") or 0)
        lido = 0
        while True:
            b = r.read(262144)
            if not b:
                break
            f.write(b); lido += len(b)
            if total:
                print(f"\r    {100 * lido // total}%", end="", flush=True)
    diga("\r    concluído")
    return destino


def extrair(zip_path, para):
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(para)
    itens = [os.path.join(para, x) for x in os.listdir(para)]
    # zip do GitHub embrulha tudo numa pasta "<repo>-main"
    if len(itens) == 1 and os.path.isdir(itens[0]):
        return itens[0]
    return para


# --------------------------------------------------------------- cópia sem duplicar
def igual(a, b):
    try:
        return os.path.getsize(a) == os.path.getsize(b) and open(a, "rb").read() == open(b, "rb").read()
    except OSError:
        return False


def copiar(origem, destino):
    """Copia só o que mudou. Devolve (copiados, iguais)."""
    copiados = iguais = 0
    if os.path.isfile(origem):
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        if os.path.exists(destino) and igual(origem, destino):
            return 0, 1
        shutil.copy2(origem, destino)
        return 1, 0
    for raiz, dirs, arqs in os.walk(origem):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git")]
        rel = os.path.relpath(raiz, origem)
        alvo = destino if rel == "." else os.path.join(destino, rel)
        os.makedirs(alvo, exist_ok=True)
        for a in arqs:
            if a.endswith(".pyc"):
                continue
            o, d = os.path.join(raiz, a), os.path.join(alvo, a)
            if os.path.exists(d) and igual(o, d):
                iguais += 1
            else:
                shutil.copy2(o, d); copiados += 1
    return copiados, iguais


# --------------------------------------------------------------- atalhos
def criar_atalho(destino_lnk, alvo, dir_trabalho, icone=None, descricao=""):
    """Cria um .lnk pelo próprio Windows, via COM.

    Sem dependência externa: usa o WScript.Shell que existe em toda instalação do
    Windows, chamado por PowerShell. Um `.bat` disfarçado abriria janela preta e
    não aceitaria ícone próprio.
    """
    import subprocess
    ps = (
        f"$s = (New-Object -ComObject WScript.Shell).CreateShortcut('{destino_lnk}');"
        f"$s.TargetPath = '{alvo}';"
        f"$s.WorkingDirectory = '{dir_trabalho}';"
        f"$s.Description = '{descricao}';"
        + (f"$s.IconLocation = '{icone}';" if icone else "")
        + "$s.Save()"
    )
    r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
                       capture_output=True, text=True)
    return r.returncode == 0 and os.path.exists(destino_lnk)


def pasta_especial(nome):
    """Área de Trabalho / Menu Iniciar do usuário, perguntando ao Windows.

    Ler %USERPROFILE%\\Desktop erra em duas situações comuns: OneDrive
    redirecionando a Área de Trabalho, e Windows em inglês.
    """
    import subprocess
    r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command",
                        f"[Environment]::GetFolderPath('{nome}')"],
                       capture_output=True, text=True)
    p = (r.stdout or "").strip()
    return p if p and os.path.isdir(p) else None


# --------------------------------------------------------------- instalação
def instalar(destino=None, silencioso=False):
    destino = destino or os.path.join(
        os.environ.get("LOCALAPPDATA") or os.path.expanduser("~"), "OrcamentosNEWA")
    d_app, d_repo = os.path.join(destino, "app"), os.path.join(destino, "repo")

    diga(f"\n  {NOME} — instalação")
    diga(f"  destino: {destino}\n")

    tmp = tempfile.mkdtemp(prefix="newa-inst-")
    try:
        # ---- 1. o programa -------------------------------------------------
        local = origem_do_app()
        if local:
            diga(f"  programa encontrado aqui: {os.path.basename(local)}")
        else:
            diga("  programa não veio junto — buscando no GitHub")
            z = baixar(RELEASE, os.path.join(tmp, "app.zip"), "o programa (~80 MB)")
            local = extrair(z, os.path.join(tmp, "app"))
            if not os.path.exists(os.path.join(local, EXE)):
                cand = achar_local([PASTA_APP], raiz=local)
                if cand: local = cand
        if not os.path.exists(os.path.join(local, EXE)):
            raise RuntimeError("o executável do programa não foi encontrado no pacote")
        c, i = copiar(local, d_app)
        diga(f"  programa: {c} arquivo(s) atualizado(s), {i} já estavam iguais")

        # ---- 2. o código e os perfis ---------------------------------------
        raiz = origem_do_repo()
        if raiz:
            diga(f"  código-fonte encontrado aqui: {raiz}")
        else:
            diga("  código-fonte não veio junto — buscando no GitHub")
            z = baixar(REPO_ZIP, os.path.join(tmp, "repo.zip"), "o código e os perfis")
            raiz = extrair(z, os.path.join(tmp, "repo"))
        tc = ti = 0
        for n in DO_REPO:
            o = os.path.join(raiz, n)
            if os.path.exists(o):
                a, b = copiar(o, os.path.join(d_repo, n)); tc += a; ti += b
        diga(f"  código e perfis: {tc} arquivo(s) atualizado(s), {ti} já estavam iguais")

        # ---- 3. atalhos ----------------------------------------------------
        alvo = os.path.join(d_app, EXE)
        icone = os.path.join(d_repo, "orcamentos-newa", "assets", "app.ico")
        if not os.path.exists(icone):
            icone = alvo
        feitos = []
        for chave, sub in (("Desktop", None), ("StartMenu", "Programs")):
            base = pasta_especial(chave)
            if not base:
                continue
            if sub:
                base = os.path.join(base, sub)
                os.makedirs(base, exist_ok=True)
            lnk = os.path.join(base, f"{NOME}.lnk")
            if criar_atalho(lnk, alvo, d_app, icone, "Gerador de propostas comparativas de seguro auto"):
                feitos.append(lnk)
        diga(f"  atalhos criados: {len(feitos)}")
        for f in feitos:
            diga(f"    {f}")

        # ---- 4. desinstalador ---------------------------------------------
        with open(os.path.join(destino, "Desinstalar.bat"), "w", encoding="utf-8") as f:
            f.write("@echo off\r\nchcp 65001 >nul\r\n"
                    "echo Removendo o Orcamentos NEWA...\r\n"
                    f'rmdir /s /q "{d_app}" 2>nul\r\n'
                    f'rmdir /s /q "{d_repo}" 2>nul\r\n'
                    'del "%USERPROFILE%\\Desktop\\' + NOME + '.lnk" 2>nul\r\n'
                    'del "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\' + NOME + '.lnk" 2>nul\r\n'
                    "echo.\r\necho Pronto. Seus dados e propostas NAO foram apagados.\r\n"
                    f'echo Eles estao em: {destino}\r\n'
                    "pause\r\n")

        # ---- 5. prova ------------------------------------------------------
        diga("\n  verificando a instalação…")
        import subprocess
        r = subprocess.run([alvo, "--verificar"], capture_output=True, text=True, timeout=180)
        saida = (r.stdout or "") + (r.stderr or "")
        for l in saida.splitlines():
            if l.strip():
                diga("  " + l.rstrip())
        if r.returncode != 0:
            raise RuntimeError("a instalação não passou na própria verificação")

        diga(f"\n  Instalado. Abra pelo atalho “{NOME}” na Área de Trabalho.")
        diga(f"  Para remover: {os.path.join(destino, 'Desinstalar.bat')}")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    silencioso = "--silencioso" in sys.argv
    destino = None
    if "--destino" in sys.argv:
        i = sys.argv.index("--destino")
        if i + 1 < len(sys.argv):
            destino = sys.argv[i + 1]
    try:
        cod = instalar(destino, silencioso)
    except Exception as e:
        diga(f"\n  FALHOU: {e}")
        cod = 1
    if not silencioso:
        diga()
        try:
            input("  Pressione Enter para fechar.")
        except EOFError:
            pass
    return cod


if __name__ == "__main__":
    sys.exit(main())
