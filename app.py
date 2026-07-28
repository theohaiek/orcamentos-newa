# -*- coding: utf-8 -*-
"""Orçamentos NEWA — casca desktop.

Mesma aplicação de sempre; o que muda é a moldura. Em vez de subir um servidor
numa porta fixa e abrir o navegador, sobe o servidor numa porta livre e mostra o
conteúdo numa janela nativa: com ícone próprio, sem abas e sem barra de endereço.

    python app.py

Três decisões que valem explicação:

*   **Porta livre, não 8080.** Pedir a porta 0 ao sistema devolve uma que está
    disponível. Porta fixa quebra se outro programa a estiver usando, e é o tipo
    de defeito que só aparece na máquina do cliente. O front-end chama `/api/...`
    em caminho relativo, então a porta ser variável não afeta nada.

*   **Espera o servidor responder de verdade.** O `server.py` abria o navegador
    depois de `sleep(0.8)` — um palpite. Numa máquina lenta a janela abriria numa
    página de erro. Aqui a janela só aparece depois que a porta aceita conexão.

*   **Só escuta em 127.0.0.1.** O servidor nunca fica visível na rede local.
"""
import os, sys, socket, threading, time
from http.server import ThreadingHTTPServer

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)


def _desfazer(repo):
    """Apaga todo rastro de uma tentativa de rodar o código de `repo`.

    Duas armadilhas, e as duas já morderam:

    *   `sys.path.remove` tira **uma** ocorrência. O `app.py` do repositório insere
        a própria pasta no `sys.path` na linha 27, então havia duas — e a que
        sobrava fazia o "código embutido" continuar importando do repositório
        quebrado. Era a rede de proteção pegando o mesmo buraco.

    *   Import que falha no meio deixa módulos no `sys.modules`. Sem limpá-los, o
        retry importa o cadáver em vez do arquivo bom.
    """
    alvo = os.path.abspath(repo)
    sys.path[:] = [p for p in sys.path if os.path.abspath(p) != alvo]
    for nome, mod in list(sys.modules.items()):
        f = getattr(mod, "__file__", None)
        if f and os.path.abspath(f).startswith(alvo + os.sep):
            sys.modules.pop(nome, None)


def _rodar_repo(repo):
    """Tenta rodar o `app.py` de `repo`. Devolve (rodou, erro)."""
    import runpy
    try:
        os.environ["NEWA_DELEGADO"] = "1"
        sys.path.insert(0, repo)
        runpy.run_path(os.path.join(repo, "app.py"), run_name="__main__")
        return True, None
    except SystemExit:
        return True, None
    except Exception as e:
        os.environ.pop("NEWA_DELEGADO", None)
        _desfazer(repo)
        return False, e


def _reparar_repo(repo):
    """Ressincroniza `repo` usando o updater EMBUTIDO, que é o desta versão.

    O motivo de existir: a sincronização de uma versão anterior pode ter deixado o
    repositório incompleto — foi o que aconteceu quando o `auth.py` entrou. O
    updater instalado não conhecia o arquivo novo, baixou o `server.py` que passou
    a importá-lo e parou aí. A partir daqui o programa conserta isso sozinho, em
    vez de depender de alguém reinstalar.
    """
    try:
        import updater as _u
        r = _u.sincronizar_repo(repo)
        return bool(r.get("atualizados"))
    except Exception:
        return False


def _delegar_ao_repo():
    """Instalado, o programa roda o código da pasta `repo`, não o que veio embutido.

    É o que faz a atualização automática valer para o programa inteiro, e não só
    para os perfis: o executável carrega Python e as bibliotecas — que mudam raro —
    enquanto motor, interface e perfis vivem em `repo`, sincronizados com o
    repositório. Uma correção publicada hoje chega ao usuário no próximo login,
    sem reinstalar nada.

    Só acontece no executável empacotado e uma vez só, pela variável de ambiente:
    o código do repositório é este mesmo arquivo, e sem a trava ele se chamaria em
    laço.

    Se o repositório estiver quebrado, tenta consertá-lo antes de desistir; e se
    ainda assim não rodar, cai para a cópia embutida, que veio testada no
    instalador. Repositório quebrado nunca pode impedir o programa de abrir.
    """
    if not getattr(sys, "frozen", False) or os.environ.get("NEWA_DELEGADO") == "1":
        return False
    repo = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(sys.executable))), "repo")
    if not (os.path.isfile(os.path.join(repo, "app.py"))
            and os.path.isfile(os.path.join(repo, "server.py"))):
        return False

    rodou, erro = _rodar_repo(repo)
    if rodou:
        return True
    sys.stderr.write(f"[aviso] o código de 'repo' não subiu ({erro}); tentando atualizar\n")

    if _reparar_repo(repo):
        rodou, erro = _rodar_repo(repo)
        if rodou:
            return True
        sys.stderr.write(f"[aviso] mesmo atualizado, não subiu ({erro})\n")

    sys.stderr.write("[aviso] usando o código embutido no programa\n")
    return False


if _delegar_ao_repo():
    sys.exit(0)

import webview
import server
import updater

TITULO = "Orçamentos NEWA"
APP_ID = "NEWA.Orcamentos"          # identidade no Windows: agrupa e dá ícone na barra
ICONE = os.path.join(AQUI, "orcamentos-newa", "assets", "app.ico")


def ajustar_windows():
    """Nitidez em tela com escala e ícone certo na barra de tarefas.

    Sem o DPI awareness, em monitor a 125% ou 150% o Windows estica a janela por
    bitmap e todo o texto fica borrado. Sem o AppUserModelID, a barra de tarefas
    agrupa a janela sob o ícone genérico do Python em vez do nosso.
    """
    if sys.platform != "win32":
        return
    import ctypes
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)      # por monitor
    except Exception:
        try: ctypes.windll.user32.SetProcessDPIAware()      # sistemas mais antigos
        except Exception: pass
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)
    except Exception:
        pass


def tem_webview2():
    """WebView2 (Chromium) instalado?

    Isto decide se o app funciona ou não. Sem a runtime, o pywebview cai para o
    MSHTML — o motor do Internet Explorer 11 — onde a interface simplesmente não
    roda: o comparativo usa CSS grid e o código usa `fetch` e arrow functions,
    nada disso existe lá. O resultado seria uma janela em branco ou meia página
    torta, sem explicação nenhuma para quem está do outro lado.

    Melhor detectar antes e dizer o que fazer. A presença é publicada pela
    Microsoft no registro, com o GUID fixo da runtime, em três lugares (máquina
    64 e 32 bits, e por usuário) — basta um deles.
    """
    if sys.platform != "win32":
        return True
    import winreg
    GUID = r"{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}"
    locais = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients" "\\" + GUID),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\EdgeUpdate\Clients" "\\" + GUID),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\EdgeUpdate\Clients" "\\" + GUID),
    ]
    for raiz, chave in locais:
        try:
            with winreg.OpenKey(raiz, chave) as k:
                v, _ = winreg.QueryValueEx(k, "pv")
                if v and v != "0.0.0.0":
                    return True
        except OSError:
            pass
    return False


def tamanho_janela(larg=1280, alt=820):
    """Encaixa a janela na tela disponível.

    Notebook de 1366x768 é o que há de mais comum em escritório, e nele uma janela
    de 820 de altura nasce com a base escondida atrás da barra de tarefas — a
    pessoa não vê o botão de gerar. Aqui a janela nunca passa de 92% da área útil.
    """
    if sys.platform != "win32":
        return larg, alt
    try:
        import ctypes
        u = ctypes.windll.user32
        lt, at = u.GetSystemMetrics(0), u.GetSystemMetrics(1)
        return max(900, min(larg, int(lt * 0.92))), max(600, min(alt, int(at * 0.92)))
    except Exception:
        return larg, alt


def subir_servidor():
    """Sobe o servidor numa porta livre e devolve (url, httpd)."""
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.H)
    porta = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{porta}/", httpd


def esperar(porta, limite=15.0):
    """Bloqueia até a porta aceitar conexão. True se subiu, False se estourou."""
    fim = time.time() + limite
    while time.time() < fim:
        try:
            with socket.create_connection(("127.0.0.1", porta), 0.25):
                return True
        except OSError:
            time.sleep(0.05)
    return False


def aviso(titulo, corpo, altura=340):
    webview.create_window(TITULO, html=(
        "<body style='font:15px/1.6 system-ui,sans-serif;padding:36px 40px;color:#22312c'>"
        f"<h2 style='margin:0 0 12px;font-size:20px'>{titulo}</h2>{corpo}</body>"),
        width=580, height=altura)
    webview.start()


def verificar():
    """Confere o build sem abrir janela:  Orcamentos NEWA.exe --verificar

    Um executável empacotado quebra de um jeito que o código-fonte não quebra —
    biblioteca que ficou de fora, arquivo de dados que não foi junto, DLL nativa
    ausente. Descobrir isso na máquina do cliente é tarde. Aqui o próprio binário
    prova que sobe, serve a interface, enxerga os perfis e consegue ler um PDF.
    """
    import urllib.request
    falhas = []
    def ok(c, m):
        print(f"  [{'OK ' if c else 'FALHA'}] {m}")
        if not c: falhas.append(m)

    print(f"Orçamentos NEWA {updater.VERSION} — verificação do build")
    print(f"  empacotado: {bool(getattr(sys, 'frozen', False))}\n  raiz: {AQUI}")

    import extract_engine as EE
    perfis = EE.load_profiles(server.PROFILES_DIR, server.PROFILES_LOCAL)
    ok(len(perfis) >= 15, f"perfis carregados: {len(perfis)}")
    ok(os.path.exists(os.path.join(AQUI, "orcamentos-newa", "assets", "app.js")), "assets presentes")
    ok(os.path.exists(os.path.join(AQUI, "index.html")), "index.html presente")

    url, httpd = subir_servidor()
    ok(esperar(httpd.server_address[1]), "servidor respondeu")
    for rota, esperado in (("/", 200), ("/api/me", 401)):
        try:
            with urllib.request.urlopen(url.rstrip("/") + rota, timeout=6) as r:
                got = r.status
        except Exception as e:
            got = getattr(e, "code", str(e))
        ok(got == esperado, f"{rota} -> {got}")

    amostras = os.path.join(os.path.dirname(AQUI), "Modelo-Inputs")
    pdfs = sorted(f for f in os.listdir(amostras) if f.lower().endswith(".pdf")) \
        if os.path.isdir(amostras) else []
    if pdfs:
        pages = EE.tokenize(open(os.path.join(amostras, pdfs[0]), "rb").read())
        prof = EE.match_profile(pages, perfis)
        campos = EE.run_profile(pages, prof)["fields"] if prof else {}
        ok(len(campos) >= 15, f"extração real ({pdfs[0]}): {len(campos)} campos por {prof['id'] if prof else '-'}")
    else:
        print("  [nota] sem Modelo-Inputs ao lado: extração não exercitada")

    httpd.shutdown()
    print(f"\n  RESULTADO: {'OK' if not falhas else 'FALHOU -> ' + '; '.join(falhas)}")
    return 1 if falhas else 0


def main():
    if "--verificar" in sys.argv:
        return verificar()
    ajustar_windows()

    if not tem_webview2():
        aviso("Falta um componente do Windows",
              "<p>Este aplicativo usa o <b>Microsoft Edge WebView2</b> para desenhar a tela, "
              "e ele não está instalado nesta máquina.</p>"
              "<p>Baixe o <i>Evergreen Runtime</i> em "
              "<b>developer.microsoft.com/microsoft-edge/webview2</b>, instale, e abra o "
              "aplicativo de novo. É gratuito e leva um minuto.</p>"
              "<p style='color:#5b6b64;font-size:13.5px'>No Windows 11 e no Windows 10 "
              "atualizado ele já vem de fábrica — se está faltando, provavelmente o "
              "sistema está sem atualizar há bastante tempo.</p>", altura=400)
        return 2

    url, httpd = subir_servidor()
    porta = httpd.server_address[1]

    if not esperar(porta):
        # Sem servidor não há o que mostrar. Falhar com uma janela explicando é
        # melhor do que uma janela em branco ou um erro de conexão do navegador.
        aviso("Não foi possível iniciar",
              "<p>O serviço interno do aplicativo não respondeu. Feche e abra de novo.</p>"
              "<p>Se continuar, verifique se algum antivírus está bloqueando o programa.</p>")
        return 1

    # A verificação de atualização roda em paralelo e nunca segura a janela. Ela
    # também roda a cada login (ver server.py), então sair e entrar de novo serve
    # de "procurar atualizações" sem precisar de botão para isso.
    threading.Thread(target=server.checar_atualizacao, daemon=True).start()

    larg, alt = tamanho_janela()
    webview.create_window(
        f"{TITULO} {updater.VERSION}", url,
        width=larg, height=alt, min_size=(900, 600),
        confirm_close=True,          # evita fechar sem querer com trabalho em aberto
    )
    webview.start(icon=ICONE if os.path.exists(ICONE) else None)
    return 0


if __name__ == "__main__":
    sys.exit(main())
