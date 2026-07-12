#!/usr/bin/env python3
"""Investigación de tags territoriales de Euskal Herria (CAV+Navarra) — SOLO lectura.

Construye la tabla de tags candidatos para el scraper de descubrimiento
(oleadas 1 y 2) con un presupuesto duro de requests:

  1. SEMILLA: para cada tag de la lista acordada (capitales con todas
     sus variantes, territorios, identitarios, municipios) → 1 request
     a discover_web: result_count, solape de la 1ª página con el
     canónico y proporción de locations de Euskal Herria (señal de
     colisión: vitoria→Brasil, irun→nombre propio...).
  2. COSECHA: visita unas pocas fichas de álbum por tag con resultados
     (los tags del álbum solo están en la ficha, ver
     docs/scraping-method.md) y extrae qué OTROS tags territoriales
     aparecen que no estaban en la semilla. También cosecha, sin coste
     de red, los tags territoriales ya presentes en el canónico.
  3. SEGUNDA PASADA: los tags cosechados se miden igual que la semilla
     (1 request cada uno, cap por presupuesto).

Salida:
  - probe_out/tag_candidates.json (artifact) y el mismo JSON en JSONL
    entre marcadores por stdout (los logs del job son el canal de
    recuperación: el proxy de la sesión de Claude no puede descargar
    artifacts).
  - Tabla legible por stdout: tag | fuente | result_count | solape |
    eh_share | veredicto (incluir / sospechoso / descartar).

El veredicto es una PROPUESTA para revisión humana, no una decisión:
    descartar   result_count == 0 (o error de la API)
    incluir     solape con el canónico o mayoría de locations de EH
    sospechoso  todo lo demás (pocas locations, colisiones, dudas)

No escribe nada en data/ ni toca el canónico. Errores por request no
abortan la pasada; exit != 0 solo ante fallo fatal.
"""

import argparse
import html as html_mod
import json
import random
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = REPO_ROOT / "data" / "bandcamp_bilbaotags_clean.json"
OUT_DIR = REPO_ROOT / "probe_out"

# Presupuesto DURO acordado para la investigación completa.
MAX_REQUESTS = 200
DELAY_SECONDS = 2.0

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
}

REQUEST_TIMEOUT = 30
DISCOVER_API = "https://bandcamp.com/api/discover/1/discover_web"

# ------------------------------------------------------------------
# Semilla acordada (oleada 1 + municipios para la 2)
# ------------------------------------------------------------------

SEEDS = {
    "capital": [
        "donostia", "donosti", "san-sebastian", "san-sebastián",
        "gasteiz", "vitoria", "vitoria-gasteiz",
        "iruña", "iruñea", "pamplona",
        "bilbao", "bilbo",
    ],
    "territorio": [
        "bizkaia", "vizcaya", "gipuzkoa", "guipuzcoa",
        "araba", "alava", "nafarroa", "navarra",
    ],
    "identitario": [
        "euskadi", "euskal-herria", "basque", "basque-country",
        "pais-vasco", "euskal-musika", "basque-music", "euskaraz",
        "euskal-rock", "euskal-kantagintza",
    ],
    "municipio": [
        "barakaldo", "getxo", "santurtzi", "portugalete", "sestao",
        "basauri", "galdakao", "leioa", "durango", "gernika", "bermeo",
        "ondarroa", "lekeitio", "mungia",
        "errenteria", "eibar", "tolosa", "hernani", "azpeitia",
        "arrasate", "zarautz", "irun", "hondarribia", "oñati", "zumaia",
        "bergara", "oiartzun",
        "laudio", "llodio", "amurrio",
        "tudela", "tafalla", "lizarra", "estella", "altsasu", "baztan",
    ],
}

# ------------------------------------------------------------------
# Heurísticas territoriales
# ------------------------------------------------------------------

# Gazetteer de municipios/comarcas de EH (para reconocer tags cosechados
# que son topónimos aunque no lleven raíz euskal-/basque-).
GAZETTEER = {
    # Bizkaia
    "abadiño", "abanto", "amorebieta", "arrigorriaga", "balmaseda",
    "berango", "berriz", "elorrio", "erandio", "ermua", "etxebarri",
    "gorliz", "igorre", "markina", "muskiz", "ortuella", "plentzia",
    "sopela", "urduña", "orduña", "zalla", "zamudio", "getxo",
    "barakaldo", "santurtzi", "portugalete", "sestao", "basauri",
    "galdakao", "leioa", "durango", "gernika", "guernica", "bermeo",
    "ondarroa", "lekeitio", "mungia", "bilbao", "bilbo",
    # Gipuzkoa
    "andoain", "aretxabaleta", "azkoitia", "beasain", "deba",
    "elgoibar", "eskoriatza", "getaria", "lasarte", "lazkao", "legazpi",
    "mutriku", "ordizia", "orio", "pasaia", "urretxu", "usurbil",
    "villabona", "zestoa", "zumarraga", "errenteria", "orereta",
    "eibar", "tolosa", "hernani", "azpeitia", "arrasate", "mondragon",
    "zarautz", "irun", "hondarribia", "oñati", "zumaia", "bergara",
    "oiartzun", "donostia", "donosti",
    # Araba
    "agurain", "amurrio", "laudio", "llodio", "oion", "salvatierra",
    "gasteiz", "vitoria",
    # Navarra
    "altsasu", "alsasua", "atarrabia", "villava", "barañain",
    "baranain", "berriozar", "burlada", "burlata", "corella", "estella",
    "lizarra", "noain", "olite", "peralta", "sanguesa", "zangoza",
    "tafalla", "tudela", "zizur", "pamplona", "iruña", "iruñea",
    "baztan", "bortziriak", "sakana", "erribera",
    # Comarcas / zonas
    "busturialdea", "goierri", "txorierri", "uribe", "enkarterri",
    "ezkerraldea", "durangaldea", "urola", "debagoiena", "debabarrena",
    "lea-artibai", "arratia",
}

# Raíces que delatan un tag territorial/identitario de EH.
TERRITORIAL_SUBSTRINGS = [
    "euskal", "euskad", "euskar", "euskera", "basque", "vasco", "vasca",
    "bilb", "donost", "gasteiz", "vitoria", "iruñ", "pamplona",
    "navarr", "nafarro", "bizkai", "vizcay", "gipuzko", "guipuzc",
    "araba", "alava",
]

# Términos para clasificar band_location como "de Euskal Herria".
EH_LOCATION_TERMS = [
    "bilbao", "bilbo", "bizkaia", "vizcaya", "barakaldo", "getxo",
    "basauri", "santurtzi", "portugalete", "sestao", "leioa",
    "galdakao", "durango", "gernika", "bermeo", "ondarroa", "lekeitio",
    "mungia", "donostia", "san sebasti", "gipuzkoa", "guipúzcoa",
    "guipuzcoa", "errenteria", "eibar", "irun,", "zarautz", "tolosa",
    "hernani", "azpeitia", "arrasate", "mondrag", "hondarribia",
    "oñati", "zumaia", "bergara", "oiartzun", "vitoria", "gasteiz",
    "araba", "álava", "alava", "laudio", "llodio", "amurrio",
    "pamplona", "iruñ", "navarr", "nafarro", "tudela", "tafalla",
    "estella", "euskadi", "euskal", "basque",
]

_requests_done = 0
_report_lines = []


def note(line=""):
    print(line, flush=True)
    _report_lines.append(line)


class BudgetExhausted(Exception):
    pass


def budget_left():
    return MAX_REQUESTS - _requests_done


def fetch(url, post_json=None, save_as=None, quiet=False):
    global _requests_done
    if _requests_done >= MAX_REQUESTS:
        raise BudgetExhausted()
    if _requests_done:
        time.sleep(DELAY_SECONDS + random.uniform(0, 0.3))
    _requests_done += 1

    headers = dict(HEADERS)
    data = None
    if post_json is not None:
        data = json.dumps(post_json).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=headers)
    status, body = None, ""
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            status = resp.status
            body = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        status = exc.code
        try:
            body = exc.read().decode("utf-8", errors="replace")
        except Exception:
            body = ""
    except Exception as exc:
        status = type(exc).__name__
        body = str(exc)

    if save_as:
        (OUT_DIR / save_as).write_text(body, encoding="utf-8")
    if not quiet:
        note(f"[req {_requests_done}/{MAX_REQUESTS}] {status} "
             f"{'POST' if post_json else 'GET'} {url} ({len(body):,} bytes)")
    return status, body


# ------------------------------------------------------------------
# Canónico y utilidades
# ------------------------------------------------------------------

def normalize_url(url):
    if not url:
        return None
    u = urlparse(url.split("?", 1)[0].split("#", 1)[0])
    return f"{u.netloc.lower()}{u.path.rstrip('/')}"


def load_canonical():
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    urls = {normalize_url(a["url"]) for a in data["albums"] if a["url"]}
    ids = {a["album_id"] for a in data["albums"] if a["album_id"] is not None}
    return data, urls, ids


def norm_tag(tag):
    """Forma normalizada de un tag para consultar la API y deduplicar."""
    return re.sub(r"\s+", "-", tag.strip().lower())


def is_territorial(tag):
    t = tag.strip().lower()
    n = norm_tag(t)
    if n in {norm_tag(g) for g in GAZETTEER}:
        return True
    return any(s in t for s in TERRITORIAL_SUBSTRINGS)


def eh_location_share(results):
    """(nº locations no vacías, fracción que parecen de Euskal Herria)."""
    locs = [(r.get("band_location") or "").strip().lower() for r in results]
    locs = [l for l in locs if l]
    if not locs:
        return 0, 0.0
    hits = sum(1 for l in locs if any(t in l for t in EH_LOCATION_TERMS))
    return len(locs), hits / len(locs)


# ------------------------------------------------------------------
# Medición de un tag vía discover_web
# ------------------------------------------------------------------

def measure_tag(tag, source, canon_urls, canon_ids):
    body = {"tag_norm_names": [norm_tag(tag)], "include_result_types": ["a", "s"],
            "category_id": 0, "geoname_id": 0, "slice": "new",
            "cursor": "*", "size": 20}
    status, resp = fetch(DISCOVER_API, post_json=body, quiet=True)
    row = {"tag": norm_tag(tag), "source": source, "result_count": None,
           "overlap_url": None, "overlap_id": None, "locations_sampled": 0,
           "eh_share": None, "top_locations": [], "verdict": None,
           "reasons": [], "sample": []}
    try:
        p = json.loads(resp)
    except json.JSONDecodeError:
        row["verdict"] = "descartar"
        row["reasons"].append(f"respuesta no-JSON (status {status})")
        return row, []
    results = p.get("results")
    if not isinstance(results, list):
        row["verdict"] = "descartar"
        row["reasons"].append(f"API sin results: {str(resp)[:120]}")
        return row, []

    row["result_count"] = p.get("result_count")
    urls = {normalize_url(r.get("item_url")) for r in results} - {None}
    ids = {r.get("item_id") for r in results} - {None}
    row["overlap_url"] = len(urls & canon_urls)
    row["overlap_id"] = len(ids & canon_ids)
    n_locs, share = eh_location_share(results)
    row["locations_sampled"] = n_locs
    row["eh_share"] = round(share, 2) if n_locs else None
    row["top_locations"] = [loc for loc, _ in Counter(
        (r.get("band_location") or "").strip() for r in results
        if (r.get("band_location") or "").strip()).most_common(3)]
    row["sample"] = [
        {"artist": r.get("band_name"), "title": r.get("title"),
         "location": r.get("band_location")}
        for r in results[:2]
    ]

    if not row["result_count"]:
        row["verdict"] = "descartar"
        row["reasons"].append("0 resultados")
    elif row["overlap_id"] >= 1 or row["overlap_url"] >= 1:
        row["verdict"] = "incluir"
        row["reasons"].append("solape con el canónico")
        if n_locs >= 5 and share < 0.5:
            row["verdict"] = "sospechoso"
            row["reasons"].append(f"pero solo {share:.0%} de locations de EH")
    elif n_locs >= 5 and share >= 0.5:
        row["verdict"] = "incluir"
        row["reasons"].append(f"{share:.0%} de locations de EH")
    elif n_locs < 5:
        row["verdict"] = "sospechoso"
        row["reasons"].append(f"señal débil: solo {n_locs} locations en la muestra")
    else:
        row["verdict"] = "sospechoso"
        row["reasons"].append(f"solo {share:.0%} de locations de EH (posible colisión)")
    return row, results


# ------------------------------------------------------------------
# Cosecha de tags desde fichas
# ------------------------------------------------------------------

TAG_LINK_RE = re.compile(r'<a[^>]*class="tag"[^>]*>\s*([^<]+?)\s*</a>')


def harvest_from_album(url):
    status, body = fetch(url, quiet=True)
    if not (isinstance(status, int) and status == 200):
        return None
    if "<title>Client Challenge</title>" in body:
        return None
    return [html_mod.unescape(t).strip().lower() for t in TAG_LINK_RE.findall(body)]


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--fichas-por-tag", type=int, default=2,
                        help="fichas a cosechar por tag de semilla con resultados")
    parser.add_argument("--reserva-segunda-pasada", type=int, default=25,
                        help="requests reservados para medir tags cosechados")
    args = parser.parse_args()

    OUT_DIR.mkdir(exist_ok=True)
    canon, canon_urls, canon_ids = load_canonical()
    seeds = [(tag, cat) for cat, tags in SEEDS.items() for tag in tags]
    note(f"Investigación de tags — presupuesto {MAX_REQUESTS} requests, "
         f"{DELAY_SECONDS}s entre requests")
    note(f"Semilla: {len(seeds)} tags | canónico: {len(canon_urls)} URLs, "
         f"{len(canon_ids)} album_ids")
    note()

    rows = []
    seen = {norm_tag(t) for t, _ in seeds}
    harvest_counter = Counter()
    ficha_urls = []  # (tag_origen, url) candidatas a cosecha

    try:
        # ---- Fase 1: semilla -------------------------------------
        note("=== Fase 1: medición de la semilla ===")
        for tag, cat in seeds:
            row, results = measure_tag(tag, f"semilla:{cat}", canon_urls, canon_ids)
            rows.append(row)
            note(f"  [{_requests_done}/{MAX_REQUESTS}] {row['tag']}: "
                 f"count={row['result_count']} solape={row['overlap_id']} "
                 f"eh={row['eh_share']} → {row['verdict']}")
            # candidatas a cosecha: items nuevos (no canónicos), EH primero
            fresh = [r for r in results
                     if normalize_url(r.get("item_url")) not in canon_urls
                     and r.get("item_type") == "a" and r.get("item_url")]
            fresh.sort(key=lambda r: 0 if any(
                t in (r.get("band_location") or "").lower()
                for t in EH_LOCATION_TERMS) else 1)
            for r in fresh[:args.fichas_por_tag]:
                ficha_urls.append((row["tag"], r["item_url"].split("?", 1)[0]))
        note()

        # ---- Fase 2a: cosecha offline desde el canónico ----------
        note("=== Fase 2a: cosecha offline (tags del canónico) ===")
        canon_harvest = sorted({
            norm_tag(t) for a in canon["albums"] for t in a["tags"]
            if is_territorial(t) and norm_tag(t) not in seen})
        note(f"  {len(canon_harvest)} tags territoriales en el canónico "
             f"fuera de la semilla: {canon_harvest}")
        for t in canon_harvest:
            harvest_counter[t] += 1
        note()

        # ---- Fase 2b: cosecha desde fichas ------------------------
        # Presupuesto de fichas: lo que quede menos la reserva.
        max_fichas = max(0, budget_left() - args.reserva_segunda_pasada)
        note(f"=== Fase 2b: cosecha desde fichas (hasta {max_fichas} fichas, "
             f"{len(ficha_urls)} candidatas) ===")
        # dedupe de URLs conservando el orden (un álbum puede salir por 2 tags)
        seen_urls = set()
        harvested_pages = 0
        for origin, url in ficha_urls:
            if harvested_pages >= max_fichas:
                break
            if url in seen_urls:
                continue
            seen_urls.add(url)
            tags = harvest_from_album(url)
            harvested_pages += 1
            if tags is None:
                note(f"  [{_requests_done}/{MAX_REQUESTS}] ✗ {url}")
                continue
            new_terr = [t for t in tags
                        if is_territorial(t) and norm_tag(t) not in seen]
            for t in new_terr:
                harvest_counter[norm_tag(t)] += 1
            if new_terr:
                note(f"  [{_requests_done}/{MAX_REQUESTS}] {url} (vía {origin}): "
                     f"nuevos {sorted(set(map(norm_tag, new_terr)))}")
        note(f"  fichas visitadas: {harvested_pages}; tags cosechados "
             f"(canónico+fichas): {len(harvest_counter)}")
        note()

        # ---- Fase 3: medición de lo cosechado ---------------------
        note("=== Fase 3: medición de tags cosechados ===")
        for t, freq in harvest_counter.most_common():
            if budget_left() < 1:
                note("  (presupuesto agotado; el resto queda sin medir)")
                break
            if t in seen:
                continue
            seen.add(t)
            row, _ = measure_tag(t, "cosecha", canon_urls, canon_ids)
            row["harvest_freq"] = freq
            rows.append(row)
            note(f"  [{_requests_done}/{MAX_REQUESTS}] {t} (freq {freq}): "
                 f"count={row['result_count']} solape={row['overlap_id']} "
                 f"eh={row['eh_share']} → {row['verdict']}")
    except BudgetExhausted:
        note(f"\n⚠ presupuesto de {MAX_REQUESTS} requests agotado")

    # ---- Salida ------------------------------------------------
    payload = {
        "meta": {
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "budget_used": _requests_done,
            "budget_max": MAX_REQUESTS,
            "seeds": {cat: tags for cat, tags in SEEDS.items()},
            "note": ("Veredictos = propuesta para revisión humana. "
                     "eh_share = fracción de band_location de la 1ª página "
                     "que parecen de Euskal Herria; solape medido contra "
                     "el canónico por album_id y URL normalizada."),
        },
        "tags": rows,
    }
    (OUT_DIR / "tag_candidates.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    note()
    note("=== Tabla resumen (tag | fuente | count | solape | eh_share | veredicto) ===")
    order = {"incluir": 0, "sospechoso": 1, "descartar": 2}
    for r in sorted(rows, key=lambda r: (order.get(r["verdict"], 9),
                                         -(r["result_count"] or 0))):
        note(f"  {r['tag']:<28} {r['source']:<18} "
             f"{str(r['result_count']):>6} {r['overlap_id']!s:>3} "
             f"{str(r['eh_share']):>5}  {r['verdict']}  ({'; '.join(r['reasons'])})")

    # JSONL entre marcadores: canal de recuperación vía logs del job.
    note()
    print("### TAG_CANDIDATES_JSONL_BEGIN", flush=True)
    print(json.dumps({"meta": payload["meta"]}, ensure_ascii=False), flush=True)
    for r in rows:
        print(json.dumps(r, ensure_ascii=False), flush=True)
    print("### TAG_CANDIDATES_JSONL_END", flush=True)

    note()
    note(f"=== Fin: {_requests_done}/{MAX_REQUESTS} requests usados, "
         f"{len(rows)} tags medidos ===")
    (OUT_DIR / "summary.md").write_text("\n".join(_report_lines) + "\n",
                                        encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
