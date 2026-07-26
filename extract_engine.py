# -*- coding: utf-8 -*-
"""
Motor de extração DETERMINÍSTICA por perfil (dev / live-edit) — v2.

Modelo de dados (3 níveis, do mais fino ao mais grosso):
  tokens   — palavra + bbox (PyMuPDF `get_text("words")`).
  segments — tokens agrupados por (bloco, linha) do PDF. É o nível que separa
             "Veículo:" de "Valor de Mercado Referenciado" e de "Dias Paralisação:"
             numa MESMA linha visual de um formulário multi-coluna. É o que torna
             a captura rótulo→valor segura (sem invadir a coluna vizinha).
  lines    — tokens reagrupados por faixa de y (linha VISUAL, atravessando colunas).
             Útil para regex em texto corrido e para o inventário "não mapeado".

Estratégias de captura (`pick`):
  kv        — rótulo terminado em ":"; valor no mesmo segmento (após o ":") ou nos
              segmentos à direita, na mesma faixa de y, parando no próximo rótulo.
  row       — igual ao kv, mas sem exigir ":" (tabelas rótulo | valor).
  under     — valor nos segmentos ABAIXO da âncora, dentro de uma janela de x.
  right     — tokens à direita da âncora na mesma linha visual (legado).
  below     — linha(s) abaixo da âncora, numa janela de x (legado).
  table_cell— célula por faixa de coluna x (legado).
  regex_near— regex numa janela de linhas ao redor da âncora.
  text_regex— regex no texto corrido (grupo 1 se houver).

Um campo pode declarar UMA spec ou uma LISTA de specs (alternativas, na ordem:
a primeira que devolver valor vence). Isso é o que dá cobertura em layouts
diferentes com o mesmo dicionário de campos.

Espelho conceitual do que o plugin fará em PHP (smalot/pdfparser -> getDataTM).
Os PERFIS (data/profiles/*.json) são o artefato compartilhado e parser-agnóstico.
"""
import re, json, os, glob, unicodedata
from collections import OrderedDict
import fitz


# ---------------------------------------------------------------- normalização
def norm(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower().strip()


def _sq(s):
    """Normaliza e colapsa espaços — para comparar rótulos."""
    return re.sub(r"\s+", " ", norm(s))


def _nospace(s):
    """Remove TODOS os espaços — para casar marcador de perfil sem depender de
    onde o extrator decidiu quebrar palavra."""
    return re.sub(r"\s+", "", s or "")


# ---------------------------------------------------------------- tokenização
def tokenize(pdf_bytes):
    """Devolve páginas com tokens, segmentos (bloco/linha) e linhas visuais."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = []
    for pno in range(doc.page_count):
        page = doc[pno]
        words = page.get_text("words")  # (x0,y0,x1,y1,word,block,line,wordno)
        toks = [{"x0": w[0], "y0": w[1], "x1": w[2], "y1": w[3], "t": w[4],
                 "b": w[5], "l": w[6]} for w in words if w[4].strip()]
        pages.append({"n": pno + 1, "w": page.rect.width, "h": page.rect.height,
                      "tokens": toks,
                      "segments": _build_segments(toks),
                      "lines": _build_lines(toks)})
    return pages


def _bbox(ts):
    return [min(t["x0"] for t in ts), min(t["y0"] for t in ts),
            max(t["x1"] for t in ts), max(t["y1"] for t in ts)]


_tokens_bbox = _bbox   # alias histórico (usado pelo server para ancorar valores da IA)


def _build_segments(toks):
    """Agrupa tokens por (bloco, linha) do PDF — preserva a separação de colunas."""
    g = OrderedDict()
    for t in toks:
        g.setdefault((t["b"], t["l"]), []).append(t)
    segs = []
    for ts in g.values():
        ts = sorted(ts, key=lambda t: t["x0"])
        text = " ".join(t["t"] for t in ts)
        bb = _bbox(ts)
        segs.append({"x0": bb[0], "y0": bb[1], "x1": bb[2], "y1": bb[3],
                     "text": text, "ntext": _sq(text), "tokens": ts})
    segs.sort(key=lambda s: (round(s["y0"] / 3.0), s["x0"]))
    return segs


def _build_lines(toks):
    """Agrupa tokens em LINHAS VISUAIS por proximidade do centro vertical.

    Agrupamento adaptativo (e não bucket fixo de y): tabelas em que o valor é
    impresso 2-3pt acima do rótulo (ex.: MAPFRE) passam a formar UMA linha só.
    """
    if not toks:
        return []
    items = sorted(toks, key=lambda t: (t["y0"] + t["y1"]) / 2.0)
    hs = sorted(t["y1"] - t["y0"] for t in items)
    h = hs[len(hs) // 2] or 8.0
    tol = max(2.0, h * 0.6)
    groups, cur = [], [items[0]]
    cy = (items[0]["y0"] + items[0]["y1"]) / 2.0
    for t in items[1:]:
        c = (t["y0"] + t["y1"]) / 2.0
        if c - cy <= tol:
            cur.append(t)
        else:
            groups.append(cur); cur = [t]
        cy = c
    groups.append(cur)
    lines = []
    for ts in groups:
        ts = sorted(ts, key=lambda t: t["x0"])
        text = " ".join(t["t"] for t in ts)
        bb = _bbox(ts)
        lines.append({"text": text, "ntext": norm(text), "bbox": bb,
                      "tokens": ts, "y": bb[1]})
    lines.sort(key=lambda l: l["y"])
    return lines


# ---------------------------------------------------------------- perfis
def load_profiles(profiles_dir):
    profs = []
    for f in sorted(glob.glob(os.path.join(profiles_dir, "*.json"))):
        try:
            profs.append(json.load(open(f, encoding="utf-8")))
        except Exception:
            pass
    return profs


def match_profile(pages, profiles):
    """Escolhe o perfil cujos marcadores 'match' TODOS aparecem no texto.

    Desempate: maior `priority` (perfil dedicado da seguradora = 10; perfil de
    família/sistema = 0), depois maior número de marcadores. Ignora perfis '_'.
    """
    # O marcador é comparado SEM espaços: onde o PDF posiciona caractere a caractere
    # (HDI, Justos), a reconstrução de palavras pode inserir ou perder um espaço no
    # meio do marcador e o perfil deixava de casar — o documento inteiro caía na IA
    # por causa de um espaço. O conteúdo do marcador continua tendo que estar lá.
    full = _nospace(norm(" ".join(l["text"] for p in pages for l in p["lines"])))
    best, best_rank = None, None
    for prof in profiles:
        if str(prof.get("id", "")).startswith("_"):
            continue
        marks = [_nospace(norm(m)) for m in prof.get("match", [])]
        if not marks or not all(m in full for m in marks):
            continue
        # `match_not`: marcadores que NÃO podem aparecer. Necessário quando várias
        # seguradoras usam o mesmo emissor e compartilham rodapé/cabeçalho — sem isso
        # o desempate viraria ordem alfabética do nome do arquivo de perfil.
        if any(_nospace(norm(m)) in full for m in prof.get("match_not", [])):
            continue
        rank = (int(prof.get("priority", 0)), len(marks))
        if best_rank is None or rank > best_rank:
            best, best_rank = prof, rank
    return best


# ---------------------------------------------------------------- escopo/seção
def _scope(pages, spec):
    """Lista de (page, segments) restrita por `page` e por `section`/`section_end`."""
    want_page = spec.get("page")
    sec = spec.get("section")
    sec_end = spec.get("section_end")
    out = []
    for page in pages:
        if want_page and page["n"] != want_page:
            continue
        segs = page["segments"]
        if sec:
            ns = _sq(sec)
            start = next((s for s in segs if ns in s["ntext"]), None)
            if not start:
                continue
            y0 = start["y0"]
            y1 = page["h"]
            if sec_end:
                ne = _sq(sec_end)
                end = next((s for s in segs if ne in s["ntext"] and s["y0"] > y0 + 1), None)
                if end:
                    y1 = end["y0"]
            segs = [s for s in segs if s["y0"] >= y0 - 0.5 and s["y0"] < y1]
        out.append((page, segs))
    return out


# ---------------------------------------------------------------- valor/formato
def _apply_regex(text, spec):
    rx = spec.get("regex")
    if not rx:
        return text.strip() or None
    m = re.search(rx, text, re.I)
    if not m:
        return None
    return (m.group(1) if m.lastindex else m.group(0)).strip() or None


def _guards(value, spec):
    """Rejeita valores que violem guardas declaradas no perfil."""
    if value is None:
        return None
    v = value.strip()
    if not v:
        return None
    if spec.get("not_regex") and re.search(spec["not_regex"], v, re.I):
        return None
    nv = _sq(v)
    for bad in spec.get("reject", []):
        if nv == _sq(bad):
            return None
    if spec.get("min_len") and len(v) < int(spec["min_len"]):
        return None
    if spec.get("max_words") and len(v.split()) > int(spec["max_words"]):
        return None
    mn, mx = spec.get("min_value"), spec.get("max_value")
    if mn is not None or mx is not None:
        num = _to_number(v)
        if num is None:
            return None
        if mn is not None and num < float(mn):
            return None
        if mx is not None and num > float(mx):
            return None
    return v


def _to_number(v):
    m = re.search(r"(\d[\d.]*(?:,\d+)?)", v.replace(" ", ""))
    if not m:
        return None
    try:
        return float(m.group(1).replace(".", "").replace(",", "."))
    except Exception:
        return None


def _format(value, spec):
    """Normalização declarativa do valor (moeda BR, maiúsculas, código-prefixo…)."""
    v = value
    for pat, rep in spec.get("replace", []):
        v = re.sub(pat, rep, v, flags=re.I)
    f = spec.get("format")
    if not f:
        return v.strip()
    for fmt in (f if isinstance(f, list) else [f]):
        if fmt == "strip_code":                      # "1 - PARTICULAR" -> "PARTICULAR"
            v = re.sub(r"^\s*\d+\s*[-–]\s*", "", v)
        elif fmt == "currency":                      # "1.234,56" -> "R$ 1.234,56"
            v = re.sub(r"\s+", " ", v).strip()
            if re.fullmatch(r"[\d.]+,\d{2}", v):
                v = "R$ " + v
            else:
                v = re.sub(r"R\$\s*", "R$ ", v)
        elif fmt == "upper":
            v = v.upper()
        elif fmt == "title":
            v = v.title()
        elif fmt == "sentence":
            v = v[:1].upper() + v[1:] if v else v
        elif fmt == "simnao":                        # normaliza Sim/Não
            n = _sq(v)
            if n.startswith(("sim", "s -", "s-", "contratad", "incluid")):
                v = "Sim"
            elif n.startswith(("nao", "n -", "n-", "não")):
                v = "Não"
        elif fmt == "date_iso":                       # 22/07/2026 -> 2026-07-22
            m = re.search(r"(\d{2})/(\d{2})/(\d{4})", v)
            if m:
                v = f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
        elif fmt == "digits":
            v = re.sub(r"[^\d]", "", v)
        elif fmt == "cep":
            d = re.sub(r"[^\d]", "", v)
            if len(d) == 8:
                v = d[:5] + "-" + d[5:]
    return re.sub(r"\s+", " ", v).strip()


# ---------------------------------------------------------------- helpers seg
def _same_row(a, b, tol):
    """Dois segmentos estão na MESMA linha visual?

    Compara o CENTRO vertical, não a sobreposição das caixas: as caixas do
    PyMuPDF incluem ascendente/descendente da fonte, então em tabelas densas
    as caixas de linhas vizinhas quase se tocam e um teste de sobreposição
    captura a linha de cima (era a causa do off-by-one em tabelas de parcelas).
    """
    ca = (a["y0"] + a["y1"]) / 2.0
    cb = (b["y0"] + b["y1"]) / 2.0
    return abs(ca - cb) <= tol


_LABEL_END = re.compile(r":\s*$")


def _is_label(seg):
    return bool(_LABEL_END.search(seg["text"]))


def _anchor_hit(seg, spec):
    """A âncora casa no segmento? Considera só a parte ANTES do ':' quando houver."""
    a = _sq(spec["anchor"])
    head = seg["text"].split(":", 1)[0] if ":" in seg["text"] else seg["text"]
    hn = _sq(head)
    if spec.get("exact"):
        return hn == a
    if spec.get("starts_with"):
        return hn.startswith(a)
    return a in hn


# ---------------------------------------------------------------- picks (seg)
def _pick_kv(pages, spec, require_colon=True):
    # ytol = distância máxima entre os CENTROS verticais. Valor <= 0 significa
    # "mesma baseline, estrito" (1pt) — não desliga a busca.
    tol = float(spec.get("ytol", 3.0))
    tol = 1.0 if tol <= 0 else tol
    occ = int(spec.get("occurrence", 1))
    xmin, xmax = spec.get("xmin"), spec.get("xmax")
    seen = 0
    for page, segs in _scope(pages, spec):
        for i, s in enumerate(segs):
            if require_colon and ":" not in s["text"]:
                continue
            if not _anchor_hit(s, spec):
                continue
            seen += 1
            if seen < occ:
                continue
            # (a) valor no MESMO segmento, depois do ':'
            if ":" in s["text"]:
                after = s["text"].split(":", 1)[1].strip()
                val = _guards(_apply_regex(after, spec), spec) if after else None
                if val:
                    src = _value_tokens(s["tokens"], val) or s["tokens"]
                    return _prov(val, page, _bbox(src), s["text"], spec)
            # (b) segmentos à DIREITA na mesma faixa de y, até o próximo rótulo
            cands = [o for o in segs
                     if o is not s and _same_row(s, o, tol) and o["x0"] >= s["x1"] - 1.0
                     and (xmin is None or o["x0"] >= xmin)
                     and (xmax is None or o["x0"] <= xmax)]
            cands.sort(key=lambda o: o["x0"])
            acc, acc_toks = [], []
            for o in cands:
                if _is_label(o) and acc:
                    break
                if _is_label(o) and not acc:
                    break                       # rótulo colado: não há valor
                acc.append(o["text"]); acc_toks += o["tokens"]
                val = _guards(_apply_regex(" ".join(acc), spec), spec)
                if val:
                    src = _value_tokens(acc_toks, val) or acc_toks
                    return _prov(val, page, _bbox(src), " ".join(acc), spec)
                if len(acc) >= int(spec.get("max_segments", 3)):
                    break
            if seen >= occ and not spec.get("scan_all"):
                continue
    return None


def _pick_under(pages, spec):
    """Valor nos segmentos ABAIXO da âncora, dentro de uma janela de x."""
    dy = float(spec.get("dy", 40.0))
    occ = int(spec.get("occurrence", 1))
    seen = 0
    for page, segs in _scope(pages, spec):
        for s in segs:
            if not _anchor_hit(s, spec):
                continue
            seen += 1
            if seen < occ:
                continue
            ax = spec.get("at_x", s["x0"])
            xlo = float(spec.get("xlo", 12.0)); xhi = float(spec.get("xhi", 120.0))
            cs = (s["y0"] + s["y1"]) / 2.0
            # "abaixo" = centro abaixo do centro da âncora (não basta y0 > y1 da
            # âncora: as caixas de fonte de linhas vizinhas quase se tocam).
            # A janela `dy` continua medida a partir da BASE da âncora.
            below = [o for o in segs
                     if (o["y0"] + o["y1"]) / 2.0 > cs + 2.0
                     and o["y0"] <= s["y1"] + dy
                     and o["x0"] >= ax - xlo and o["x0"] <= ax + xhi]
            below.sort(key=lambda o: (o["y0"], o["x0"]))
            for o in below:
                val = _guards(_apply_regex(o["text"], spec), spec)
                if val:
                    src = _value_tokens(o["tokens"], val) or o["tokens"]
                    return _prov(val, page, _bbox(src), o["text"], spec)
    return None


def _prov(value, page, bbox, snippet, spec):
    return {"value": _format(value, spec), "page": page["n"], "bbox": list(bbox),
            "snippet": snippet, "anchor": spec.get("anchor", ""), "method": "profile"}


# ---------------------------------------------------------------- picks (linha)
def _find_anchor(pages, spec):
    """Localiza a linha-âncora (linha visual). Retorna (page, line_idx, bbox)."""
    a = norm(spec["anchor"])
    occ = spec.get("occurrence", 1)
    want_page = spec.get("page")
    seen = 0
    for page in pages:
        if want_page and page["n"] != want_page:
            continue
        for li, line in enumerate(page["lines"]):
            if a in line["ntext"]:
                seen += 1
                if seen == occ:
                    return page, li, line["bbox"]
    return None


def extract_field(pages, spec):
    """Executa UMA spec de campo. Devolve dict de proveniência ou None."""
    pick = spec.get("pick", "right")

    if pick == "kv":
        return _pick_kv(pages, spec, require_colon=True)
    if pick == "row":
        return _pick_kv(pages, spec, require_colon=False)
    if pick == "under":
        return _pick_under(pages, spec)

    if pick == "text_regex":
        rx = re.compile(spec["regex"], re.I)
        for page, segs in _scope(pages, spec):
            ymin = min((s["y0"] for s in segs), default=None)
            ymax = max((s["y1"] for s in segs), default=None)
            for line in page["lines"]:
                if ymin is not None and not (ymin - 1 <= line["bbox"][1] <= ymax + 1):
                    continue
                m = rx.search(line["text"])
                if not m:
                    continue
                val = _guards((m.group(1) if m.lastindex else m.group(0)).strip(), spec)
                if val:
                    src = _value_tokens(line["tokens"], val) or line["tokens"]
                    return {"value": _format(val, spec), "page": page["n"],
                            "bbox": _bbox(src), "snippet": line["text"],
                            "anchor": spec.get("anchor", ""), "method": "profile"}
        return None

    found = _find_anchor(pages, spec)
    if not found:
        return None
    page, li, abbox = found
    line = page["lines"][li]
    anchor_norm = norm(spec["anchor"])

    def result(value, src_tokens):
        value = _guards(value, spec)
        if value is None:
            return None
        return {"value": _format(value, spec), "page": page["n"],
                "bbox": _bbox(src_tokens) if src_tokens else list(abbox),
                "snippet": line["text"] if pick == "right" else " ".join(t["t"] for t in src_tokens),
                "anchor": spec["anchor"], "method": "profile"}

    if pick == "right":
        joined, end_x = "", line["bbox"][0]
        for t in line["tokens"]:
            joined = norm((joined + " " + t["t"]).strip())
            if anchor_norm in joined:
                end_x = t["x1"]; break
        right = [t for t in line["tokens"] if t["x0"] >= end_x - 1]
        val = _apply_regex(" ".join(t["t"] for t in right), spec)
        return result(val, _value_tokens(right, val) or right)

    if pick == "below":
        ax = spec.get("at_x", abbox[0])
        xtol = spec.get("xtol", 140)
        xlo = spec.get("xlo", 18); xhi = spec.get("xhi", xtol)
        for lj in range(li + 1, min(li + int(spec.get("dlines", 4)), len(page["lines"]))):
            nxt = page["lines"][lj]
            band = [t for t in nxt["tokens"] if ax - xlo <= t["x0"] <= ax + xhi]
            val = _apply_regex(" ".join(t["t"] for t in band), spec)
            if val:
                return result(val, _value_tokens(band, val) or band)
        return None

    if pick == "table_cell":
        col = spec["col"]
        for lj in range(li, min(li + 2, len(page["lines"]))):
            cur = page["lines"][lj]
            cell = [t for t in cur["tokens"] if col[0] <= t["x0"] <= col[1]]
            val = _apply_regex(" ".join(t["t"] for t in cell), spec)
            if val:
                val = _guards(val, spec)
                if val is None:
                    continue
                src = _value_tokens(cell, val) or cell
                return {"value": _format(val, spec), "page": page["n"], "bbox": _bbox(src),
                        "snippet": cur["text"], "anchor": spec["anchor"], "method": "profile"}
        return None

    if pick == "regex_near":
        span = spec.get("span", 1)
        block = " ".join(page["lines"][k]["text"]
                         for k in range(li, min(li + 1 + span, len(page["lines"]))))
        val = _guards(_apply_regex(block, spec), spec)
        if val:
            return {"value": _format(val, spec), "page": page["n"], "bbox": list(abbox),
                    "snippet": block[:160], "anchor": spec["anchor"], "method": "profile"}
        return None

    return None


def extract_alts(pages, specs):
    """Executa a spec (ou a LISTA de alternativas) e devolve a primeira que casar."""
    for spec in (specs if isinstance(specs, list) else [specs]):
        if not isinstance(spec, dict):
            continue
        try:
            prov = extract_field(pages, spec)
        except Exception:
            prov = None
        if prov and str(prov.get("value", "")).strip():
            return prov
    return None


def _value_tokens(tokens, value):
    """Tenta achar o subconjunto de tokens cujo texto forma o valor (p/ bbox)."""
    if not value:
        return None
    nv = norm(value)
    for i in range(len(tokens)):
        chosen = []
        for j in range(i, len(tokens)):
            chosen.append(tokens[j])
            if nv in norm(" ".join(t["t"] for t in chosen)):
                return chosen
    return None


# ---------------------------------------------------------------- API do motor
def run_profile(pages, profile, skip=()):
    """Roda todos os campos do perfil. Retorna {fields, provenance, consumed}."""
    fields, provenance, consumed = {}, {}, []
    for key, spec in profile.get("fields", {}).items():
        if key in skip:
            continue
        prov = extract_alts(pages, spec)
        if prov:
            fields[key] = prov["value"]
            provenance[key] = prov
            consumed.append((prov["page"], tuple(round(v) for v in prov["bbox"])))
    return {"fields": fields, "provenance": provenance, "consumed": consumed}


def run_generic(pages, profiles, filled):
    """Camada genérica: dicionário de rótulos que roda em QUALQUER layout,
    só para os campos que o perfil específico não resolveu."""
    gen = next((p for p in profiles if p.get("id") == "_generic"), None)
    if not gen:
        return {"fields": {}, "provenance": {}, "consumed": []}
    return run_profile(pages, gen, skip=set(filled))


CURRENCY_RX = re.compile(r"R\$ ?[\d.]+,\d{2}")
NOISE_RX = re.compile(r"impresso|uso interno|p[áa]g\.|\bsusep\b|cnpj|@|\(\d{2}\)\s?\d|^\s*v\d|cota[çc][ãa]o:|^[A-Z0-9.]{14,}$", re.I)


def build_unmapped(pages, consumed):
    """Valores em R$ presentes no PDF que NÃO foram capturados por nenhum campo."""
    out, seen = [], set()
    for page in pages:
        for line in page["lines"]:
            txt = line["text"].strip()
            if not CURRENCY_RX.search(txt):
                continue
            if NOISE_RX.search(txt):
                continue
            if _overlaps_consumed(page["n"], line["bbox"], consumed):
                continue
            key = (page["n"], txt)
            if key in seen:
                continue
            seen.add(key)
            out.append({"page": page["n"], "bbox": [round(v, 1) for v in line["bbox"]], "text": txt})
    return out


def _overlaps_consumed(pno, bbox, consumed):
    for cp, cb in consumed:
        if cp != pno:
            continue
        if not (bbox[3] < cb[1] or bbox[1] > cb[3]):
            if not (bbox[2] < cb[0] or bbox[0] > cb[2]):
                return True
    return False


def page_maps(pages):
    """Mapa portátil de fragmentos por página (para o modo Visual sem raster)."""
    out = []
    for page in pages:
        frags = [{"bbox": [round(l["bbox"][0], 1), round(l["bbox"][1], 1),
                           round(l["bbox"][2], 1), round(l["bbox"][3], 1)], "text": l["text"]}
                 for l in page["lines"]]
        out.append({"n": page["n"], "w": round(page["w"], 1), "h": round(page["h"], 1),
                    "fragments": frags})
    return out
