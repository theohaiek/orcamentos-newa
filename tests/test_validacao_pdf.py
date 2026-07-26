# -*- coding: utf-8 -*-
"""A pipeline avisa em todos os casos em que deve avisar.

Regra do produto: nunca entregar documento incompleto ou mal mapeado em silêncio.
Cada situação abaixo tem que produzir um aviso explícito, não uma tela verde.
"""
import sys
import _base

_base.exige_motor(); _base.exige_amostras()
import fitz
import server as S

S._ai_extract = lambda *a, **k: {}          # isola a validação da camada de IA


def rasterizar(nome, paginas=None):
    """PDF com as páginas indicadas trocadas por imagem (simula escaneado)."""
    import os
    doc = fitz.open(os.path.join(_base.INPUTS, nome))
    out = fitz.open()
    for i in range(doc.page_count):
        if paginas is None or (i + 1) in paginas:
            pix = doc[i].get_pixmap(matrix=fitz.Matrix(2, 2))
            np_ = out.new_page(width=doc[i].rect.width, height=doc[i].rect.height)
            np_.insert_image(np_.rect, pixmap=pix)
        else:
            out.insert_pdf(doc, from_page=i, to_page=i)
    return out.tobytes()


def roda(titulo, data, fname):
    try:
        r = S.extract_pdf(data, fname)
        print(f"\n### {titulo}")
        n = sum(1 for v in r["fields"].values() if v)
        print(f"    campos={n}/31")
        for a in r["avisos"]:
            print(f"      [{a['nivel']:<8}] {a['codigo']:<20} {a['mensagem'][:84]}")
        return r, None
    except Exception as e:
        print(f"\n### {titulo}\n    RECUSADO: {e}")
        return None, str(e)


falhas = []

r, _ = roda("PDF nativo íntegro", _base.ler("mapfre.pdf"), "mapfre.pdf")
if r and [a for a in r["avisos"] if a["nivel"] == "erro"]:
    falhas.append("PDF íntegro gerou aviso de erro")

_, err = roda("PDF 100% escaneado", rasterizar("mapfre.pdf"), "scan.pdf")
if not err or "imagem" not in err:
    falhas.append("escaneado total não foi recusado com mensagem clara")

r, _ = roda("PDF híbrido (págs 2-3 em imagem)", rasterizar("mapfre.pdf", {2, 3}), "hibrido.pdf")
if not (r and any(a["codigo"] == "paginas_sem_texto" for a in r["avisos"])):
    falhas.append("híbrido não avisou páginas ilegíveis")

r, _ = roda("PDF multi-oferta", _base.ler("allianz.pdf"), "allianz.pdf")
if not (r and any(a["codigo"] == "multi_oferta" for a in r["avisos"])):
    falhas.append("multi-oferta não foi sinalizada")


def explode(*a, **k):
    raise RuntimeError("quota estourada (simulado)")


S._ai_extract = explode
_cfg = S.get_config
S.get_config = lambda: dict(_cfg(), openai_key="x-teste")
r, _ = roda("Falha da camada de IA", _base.ler("zurich.pdf"), "zurich.pdf")
if not (r and any(a["codigo"] == "falha_ia" for a in r["avisos"])):
    falhas.append("falha da IA não gerou aviso")
S.get_config = _cfg

print("\n" + "=" * 70)
print("RESULTADO:", "OK" if not falhas else "FALHAS: " + "; ".join(falhas))
sys.exit(1 if falhas else 0)
