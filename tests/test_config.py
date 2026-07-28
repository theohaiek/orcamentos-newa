# -*- coding: utf-8 -*-
"""Leitura da configuração — os dois defeitos de 28/07/2026.

1. **BOM derrubava a configuração inteira, em silêncio.** `jread` abria o arquivo
   como `utf-8`; Bloco de Notas, PowerShell e boa parte das ferramentas do Windows
   gravam um BOM no começo. O BOM virava erro de parsing, e como a falha é engolida
   o app voltava a TODOS os padrões sem dizer nada — na proposta gerada, os dados da
   corretora simplesmente sumiam.

2. **A migração de modelo gravava por cima do que não conseguiu ler.** Config
   ilegível vinha como `{}`, indistinguível de "não existe", e a migração escrevia
   `{marca: true}` no lugar: nome, e-mail e telefone da corretora, perdidos. Foi o
   que aconteceu de verdade nesta máquina.

Também fica provado aqui que a chave da OpenAI **não** vem de variável de ambiente.
"""
import json, os, sys, tempfile

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import server

falhas = []
def ok(cond, msg):
    print(f"    [{'OK ' if cond else 'FALHA'}] {msg}", flush=True)
    if not cond:
        falhas.append(msg)


tmp = tempfile.mkdtemp(prefix="cfg-")
server.CONFIG_F = os.path.join(tmp, "config.json")
MARCA = server.MIGRACAO_MODELO[2]

CHEIA = {"model": "gpt-5-nano", "reasoning_effort": "low", "openai_key": "",
         "corretora": {"nome": "NEWA Seguros", "telefone": "(11) 4040-3665"}}


def grava(obj, bom=False, cru=None):
    dados = cru if cru is not None else json.dumps(obj, ensure_ascii=False, indent=2)
    with open(server.CONFIG_F, "wb") as f:
        if bom:
            f.write(b"\xef\xbb\xbf")
        f.write(dados.encode("utf-8"))


print(">> 1. config gravada com BOM continua sendo lida")
grava(CHEIA, bom=True)
c = server.get_config()
ok(c.get("corretora", {}).get("nome") == "NEWA Seguros", "os dados da corretora sobrevivem ao BOM")
ok(c.get("reasoning_effort") == "low", "o resto da configuração também")

print(">> 2. config ilegível NÃO é sobrescrita")
grava(None, cru='{"model": "gpt-5-nano", }')       # vírgula sobrando: JSON inválido
antes = open(server.CONFIG_F, "rb").read()
c = server.get_config()
ok(c == {}, "leitura falha devolve vazio, como antes")
ok(open(server.CONFIG_F, "rb").read() == antes,
   "o arquivo ilegível fica intacto — havia dado a recuperar ali")

print(">> 3. a migração troca o gpt-5-nano uma vez só")
grava(CHEIA)
c = server.get_config()
ok(c["model"] == "gpt-4o-mini", "gpt-5-nano vira gpt-4o-mini")
ok(c["corretora"]["telefone"] == "(11) 4040-3665", "a migração preserva o resto")
ok(json.load(open(server.CONFIG_F, encoding="utf-8-sig")).get(MARCA) is True,
   "a marca de migração fica gravada")

print(">> 4. quem escolher o gpt-5-nano DEPOIS é respeitado")
c = server.get_config(); c["model"] = "gpt-5-nano"; server.set_config(c)
ok(server.get_config()["model"] == "gpt-5-nano", "a migração não roda de novo")

print(">> 5. padrão e origem da chave")
ok(server.DEFAULT_MODEL == "gpt-4o-mini", f"modelo padrão: {server.DEFAULT_MODEL}")
os.environ["OPENAI_API_KEY"] = "sk-nao-deveria-ser-usada"
try:
    grava({"model": "gpt-4o-mini", MARCA: True})
    ok(server.get_config().get("openai_key", "") == "",
       "chave não é herdada de variável de ambiente")
    fonte = open(os.path.join(os.path.dirname(server.__file__), "server.py"),
                 encoding="utf-8").read()
    ok("os.environ.get(\"OPENAI_API_KEY\"" not in fonte,
       "nenhuma leitura de OPENAI_API_KEY sobrou no código")
    ok("def load_env" not in fonte, "o carregador de .env foi removido")
finally:
    os.environ.pop("OPENAI_API_KEY", None)

print(f"\n  RESULTADO: {'OK' if not falhas else 'FALHOU -> ' + '; '.join(falhas)}")
sys.exit(1 if falhas else 0)
