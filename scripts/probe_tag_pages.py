#!/usr/bin/env python3
"""Sondeo de páginas de tag de Bandcamp — GATE de la Fase 2 (SOLO lectura).

Verifica con una muestra mínima (≤10 requests, 1 req/2s) las hipótesis
sobre las que se diseñará el scraper de descubrimiento:

  1. Estructura: las páginas /tag/<slug> embeben JSON en
     <div id="pagedata" data-blob="...">.
  2. Paginación: endpoint POST bandcamp.com/api/hub/2/dig_deeper
     (formato del body, headers necesarios, forma de la respuesta).
  3. Slugs con ñ: qué hace Bandcamp con /tag/iruñea.
  4. Anti-bot: si los runners de GitHub reciben 200 con UA de navegador
     (las fichas de álbum ya funcionaron en scrape_covers.py).
  5. Solape: cuántos items de la primera página de cada tag ya están en
     el canónico (dedupe por URL normalizada y album_id).

No escribe NADA en data/ ni toca el canónico: todo el output va a
probe_out/ (respuestas crudas + summary.md), que el workflow sube como
artifact. Los errores por request se registran y no abortan el sondeo;
el exit code solo es != 0 ante un fallo fatal del propio script.

Uso:
    python3 scripts/probe_tag_pages.py
    python3 scripts/probe_tag_pages.py --extra-tags gasteiz,euskal-rock
"""

import argparse
import html
import json
import random
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import quote, urlparse

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = REPO_ROOT / "data" / "bandcamp_bilbaotags_clean.json"
OUT_DIR = REPO_ROOT / "probe_out"

# Presupuesto DURO de la pasada completa; el gate acordado es ≤10.
MAX_REQUESTS = 10
DELAY_SECONDS = 2.0

# Mismo disfraz de navegador que scrape_covers.py: Bandcamp devuelve
# 403 a los User-Agent por defecto de urllib.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
}

REQUEST_TIMEOUT = 30

# Tags del sondeo: bilbao ancla el análisis estructural (es el tag del
# dataset original), el resto muestrea volumen/estructura de la primera
# oleada acordada. La lista completa de la oleada va en el scraper, no aquí.
PROBE_TAGS = ["bilbao", "donostia", "euskal-herria", "euskadi", "basque-music"]

_requests_done = 0
_report_lines = []


def note(line=""):
    """Acumula una línea para summary.md y la imprime (logs del job)."""
    print(line, flush=True)
    _report_lines.append(line)


class BudgetExhausted(Exception):
    pass


def fetch(url, post_json=None, extra_headers=None, save_as=None):
    """Un request con presupuesto, rate limit y captura de errores.

    Devuelve (status, body, final_url). status es int o un string de
    error corto ("timeout", "network_error"). Nunca lanza salvo
    BudgetExhausted.
    """
    global _requests_done
    if _requests_done >= MAX_REQUESTS:
        raise BudgetExhausted()
    if _requests_done:
        time.sleep(DELAY_SECONDS + random.uniform(0, 0.3))
    _requests_done += 1

    headers = dict(HEADERS)
    if extra_headers:
        headers.update(extra_headers)
    data = None
    if post_json is not None:
        data = json.dumps(post_json).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=headers)
    status, body, final_url = None, "", url
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            status = resp.status
            body = resp.read().decode("utf-8", errors="replace")
            final_url = resp.geturl()
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
    note(f"[req {_requests_done}/{MAX_REQUESTS}] {status} "
         f"{'POST' if post_json else 'GET'} {url} ({len(body):,} bytes)"
         + (f" → redirigido a {final_url}" if final_url != url else ""))
    return status, body, final_url


# ------------------------------------------------------------------
# Parsing genérico del JSON embebido
# ------------------------------------------------------------------

def extract_blob(page):
    """Extrae y decodifica el data-blob del div#pagedata, o None."""
    m = re.search(r'id="pagedata"[^>]*\bdata-blob="([^"]*)"', page)
    if not m:
        return None
    try:
        return json.loads(html.unescape(m.group(1)))
    except json.JSONDecodeError:
        return None


def walk(obj, path=""):
    """Recorre recursivamente dicts/listas emitiendo (path, valor)."""
    yield path, obj
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:50]):
            yield from walk(v, f"{path}[{i}]")


def looks_like_item(d):
    """¿Parece un dict de release de un listado de tag?"""
    if not isinstance(d, dict):
        return False
    has_title = "title" in d
    has_who = any(k in d for k in ("artist", "band_name", "artist_name"))
    has_url = any(k in d for k in ("tralbum_url", "item_url", "url"))
    return has_title and (has_who or has_url)


def extract_item(d):
    """Normaliza un item de listado a campos conocidos (tolerante)."""
    url = d.get("tralbum_url") or d.get("item_url") or d.get("url")
    return {
        "url": url,
        "artist": d.get("artist") or d.get("band_name") or d.get("artist_name"),
        "title": d.get("title"),
        "item_id": d.get("item_id") or d.get("tralbum_id") or d.get("id"),
        "item_type": d.get("item_type") or d.get("tralbum_type"),
        "_keys": sorted(d.keys()),
    }


def find_item_lists(blob):
    """Localiza en el blob las listas de items de listado: [(path, items)]."""
    found = []
    for path, node in walk(blob):
        if (isinstance(node, list) and len(node) >= 3
                and all(looks_like_item(x) for x in node[:3])):
            # Evita registrar sublistas de una lista ya encontrada.
            if not any(path.startswith(p) and p != path for p, _ in found):
                found.append((path, node))
    return found


def find_dig_deeper(blob):
    """Busca nodos llamados dig_deeper y devuelve [(path, nodo)]."""
    return [(path, node) for path, node in walk(blob)
            if path.endswith("dig_deeper") and isinstance(node, dict)]


# ------------------------------------------------------------------
# Dedupe contra el canónico (offline, sin requests)
# ------------------------------------------------------------------

def normalize_url(url):
    """Clave de dedupe: sin query/fragmento, host en minúsculas, sin / final."""
    if not url:
        return None
    u = urlparse(url.split("?", 1)[0].split("#", 1)[0])
    return f"{u.netloc.lower()}{u.path.rstrip('/')}"


def load_canonical_keys():
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    urls = {normalize_url(a["url"]) for a in data["albums"] if a["url"]}
    ids = {a["album_id"] for a in data["albums"] if a["album_id"] is not None}
    return urls, ids


# ------------------------------------------------------------------
# Sondeo
# ------------------------------------------------------------------

def analyze_tag_page(slug, body, canon_urls, canon_ids):
    """Informe estructural de una página de tag ya descargada."""
    blob = extract_blob(body)
    if blob is None:
        note(f"  {slug}: ✗ SIN data-blob en #pagedata — hipótesis 1 FALLA para este tag")
        # Pistas alternativas: ¿hay otro JSON embebido grande?
        for pat, label in [(r'<script[^>]+type="application/ld\+json"[^>]*>', "ld+json"),
                           (r'data-tralbum=', "data-tralbum"),
                           (r'id="hub-page-app"', "hub-page-app (¿SPA?)")]:
            if re.search(pat, body):
                note(f"    pista: la página contiene {label}")
        return None

    (OUT_DIR / f"blob_{slug}.json").write_text(
        json.dumps(blob, ensure_ascii=False, indent=2), encoding="utf-8")
    note(f"  {slug}: ✓ data-blob presente — claves top-level: {sorted(blob.keys())}")

    for path, node in find_dig_deeper(blob):
        note(f"  {slug}: nodo dig_deeper en '{path}' — claves: {sorted(node.keys())}")
        results = node.get("results")
        if isinstance(results, dict) and results:
            key0 = next(iter(results))
            entry = results[key0]
            note(f"    results['{key0}'] — claves: "
                 f"{sorted(entry.keys()) if isinstance(entry, dict) else type(entry).__name__}")

    total_hits = [(p, n) for p, n in walk(blob)
                  if isinstance(n, (int, float)) and n and
                  any(w in p.lower().rsplit('.', 1)[-1] for w in ("count", "total"))]
    for p, n in total_hits[:8]:
        note(f"  {slug}: posible contador — {p} = {n}")

    lists = find_item_lists(blob)
    all_items = []
    for path, items in lists:
        parsed = [extract_item(x) for x in items]
        all_items.extend(parsed)
        note(f"  {slug}: lista de {len(items)} items en '{path}'")
        note(f"    campos del item[0]: {parsed[0]['_keys']}")
        for it in parsed[:3]:
            note(f"    · {it['artist']!r} — {it['title']!r} → {it['url']} "
                 f"(item_id={it['item_id']}, type={it['item_type']})")

    if all_items:
        urls = {normalize_url(it["url"]) for it in all_items if it["url"]}
        ids = {it["item_id"] for it in all_items if it["item_id"]}
        overlap_url = len(urls & canon_urls)
        overlap_id = len(ids & canon_ids)
        note(f"  {slug}: solape con canónico — {overlap_url}/{len(urls)} por URL, "
             f"{overlap_id}/{len(ids)} por album_id")
    else:
        note(f"  {slug}: ⚠ no se localizó ninguna lista de items en el blob")
    return blob


def try_dig_deeper(slug, blob, page):
    """Intenta la llamada de paginación derivando el formato del blob."""
    filters = {"format": "all", "location": 0, "sort": "pop", "tags": [slug]}
    derived_from = "valores por defecto (hipótesis)"
    for _, node in find_dig_deeper(blob or {}):
        results = node.get("results")
        if isinstance(results, dict) and results:
            parts = next(iter(results)).split("---")
            if len(parts) == 4:
                tag, fmt, loc, sort = parts
                filters = {"format": fmt, "location": int(loc) if loc.isdigit() else loc,
                           "sort": sort, "tags": [tag]}
                derived_from = f"clave de results '{'---'.join(parts)}'"
            break
    body = {"filters": filters, "page": page}
    note(f"  dig_deeper {slug} p{page}: body derivado de {derived_from}")
    note(f"    POST body: {json.dumps(body, ensure_ascii=False)}")

    status, resp, _ = fetch(
        "https://bandcamp.com/api/hub/2/dig_deeper",
        post_json=body,
        extra_headers={
            "Referer": f"https://bandcamp.com/tag/{quote(slug)}",
            "Origin": "https://bandcamp.com",
            "X-Requested-With": "XMLHttpRequest",
        },
        save_as=f"dig_deeper_{slug}_p{page}.json",
    )
    if status != 200:
        note(f"  dig_deeper {slug} p{page}: ✗ status {status} — cuerpo: {resp[:300]!r}")
        return None
    try:
        payload = json.loads(resp)
    except json.JSONDecodeError:
        note(f"  dig_deeper {slug} p{page}: ✗ respuesta no-JSON: {resp[:300]!r}")
        return None
    note(f"  dig_deeper {slug} p{page}: ✓ JSON — claves: {sorted(payload.keys())}")
    items = payload.get("items")
    if isinstance(items, list):
        note(f"    {len(items)} items; more_available={payload.get('more_available')}")
        if items:
            it = extract_item(items[0])
            note(f"    campos del item[0]: {it['_keys']}")
            note(f"    · {it['artist']!r} — {it['title']!r} → {it['url']}")
    return payload


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--extra-tags", default="",
                        help="tags adicionales a sondear, separados por comas")
    args = parser.parse_args()

    OUT_DIR.mkdir(exist_ok=True)
    canon_urls, canon_ids = load_canonical_keys()
    note(f"Sondeo de tags de Bandcamp — presupuesto {MAX_REQUESTS} requests, "
         f"{DELAY_SECONDS}s entre requests")
    note(f"Canónico: {len(canon_urls)} URLs normalizadas, {len(canon_ids)} album_ids")
    note()

    tags = PROBE_TAGS + [t.strip() for t in args.extra_tags.split(",") if t.strip()]
    blobs = {}

    try:
        # 1) Páginas de tag de la muestra.
        for slug in tags:
            note(f"--- tag/{slug} ---")
            status, body, final = fetch(f"https://bandcamp.com/tag/{quote(slug)}",
                                        save_as=f"tag_{slug}.html")
            if status == 200:
                blobs[slug] = analyze_tag_page(slug, body, canon_urls, canon_ids)
            else:
                note(f"  {slug}: ✗ status {status}")
            note()

        # 2) Slug con ñ: ¿existe /tag/iruñea? Si falla, probar sin ñ.
        note("--- slug con ñ: iruñea ---")
        status, body, final = fetch("https://bandcamp.com/tag/" + quote("iruñea"),
                                    save_as="tag_irunea_enye.html")
        if status == 200:
            blobs["iruñea"] = analyze_tag_page("iruñea", body, canon_urls, canon_ids)
        else:
            note(f"  iruñea: ✗ status {status}; pruebo 'irunea' sin ñ")
            status2, body2, _ = fetch("https://bandcamp.com/tag/irunea",
                                      save_as="tag_irunea_ascii.html")
            if status2 == 200:
                blobs["irunea"] = analyze_tag_page("irunea", body2, canon_urls, canon_ids)
        note()

        # 3) Paginación: dig_deeper sobre bilbao (el tag ancla).
        note("--- paginación: dig_deeper ---")
        try_dig_deeper("bilbao", blobs.get("bilbao"), page=2)
        # Si queda presupuesto, una segunda página confirma continuidad.
        if _requests_done < MAX_REQUESTS:
            try_dig_deeper("bilbao", blobs.get("bilbao"), page=3)

    except BudgetExhausted:
        note(f"\n⚠ presupuesto de {MAX_REQUESTS} requests agotado; sondeo truncado")

    note()
    note(f"=== Fin del sondeo: {_requests_done}/{MAX_REQUESTS} requests usados ===")
    (OUT_DIR / "summary.md").write_text("\n".join(_report_lines) + "\n",
                                        encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
