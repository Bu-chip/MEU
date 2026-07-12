#!/usr/bin/env python3
"""Sondeo de descubrimiento por tags en Bandcamp — GATE de la Fase 2 (SOLO lectura). v3.

Hallazgos previos:
  v1 (run 29197223469): /tag/<slug> redirige a /discover/<slug>;
     api/hub/2/dig_deeper responde {error}. El sistema de hubs no existe.
  v2 (run 29197367346): la API nueva POST api/discover/1/discover_web
     FUNCIONA sin desafío (contrato verificado: results con item_url,
     item_id, band_name, band_location, release_date, primary_image;
     paginación por cursor; claves result_count/batch_result_count).
     PERO todas las páginas HTML de bandcamp.com (discover, search)
     devuelven un shell "Client Challenge" anti-bot de ~3 KB: la
     búsqueda clásica está muerta como canal de scraping.

Esta v3 cierra el gate con ≤10 requests:
  A. ¿Siguen siendo accesibles las FICHAS de álbum en subdominios de
     artista (*.bandcamp.com/album/...)? Es la fase 2 del flujo de
     ingesta y el método probado de scrape_covers.py. Se comprueba una
     ficha del canónico y una recién descubierta, verificando og:image,
     bc-page-properties y la extracción de tags (<a class="tag">).
  B. Volumen por tag de la oleada 1: result_count de discover_web para
     los tags clave, incluida la prueba del slug con ñ (iruña).

Output: stdout (los logs del job son el informe) + probe_out/ como
artifact. No escribe nada en data/. Errores por request no abortan.
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
from pathlib import Path
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = REPO_ROOT / "data" / "bandcamp_bilbaotags_clean.json"
OUT_DIR = REPO_ROOT / "probe_out"

MAX_REQUESTS = 10
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

_requests_done = 0
_report_lines = []


def note(line=""):
    print(line, flush=True)
    _report_lines.append(line)


class BudgetExhausted(Exception):
    pass


def budget_left():
    return MAX_REQUESTS - _requests_done


def fetch(url, post_json=None, extra_headers=None, save_as=None):
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
# Parte A: fichas de álbum (reutiliza el parsing de scrape_covers.py)
# ------------------------------------------------------------------

def meta_content(page, attr, value):
    tag_re = re.compile(
        r"<meta\b[^>]*\b{}=[\"']{}[\"'][^>]*>".format(re.escape(attr), re.escape(value)),
        re.IGNORECASE,
    )
    m = tag_re.search(page)
    if not m:
        return None
    content = re.search(r"\bcontent=[\"']([^\"']*)[\"']", m.group(0))
    return html_mod.unescape(content.group(1)) if content else None


def probe_album_page(label, url):
    note(f"--- ficha: {label} ---")
    status, body, final = fetch(url, save_as=f"album_{label}.html")
    if not (isinstance(status, int) and status == 200):
        note(f"  ✗ status {status}")
        note()
        return
    if "<title>Client Challenge</title>" in body:
        note("  ✗ CLIENT CHALLENGE también en la ficha — el scrape de fichas está roto")
        note()
        return
    note(f"  ✓ página real ({len(body):,} bytes, sin challenge)")
    og_image = meta_content(body, "property", "og:image")
    note(f"  og:image: {og_image}")
    props_raw = meta_content(body, "name", "bc-page-properties")
    note(f"  bc-page-properties: {props_raw}")
    keywords = meta_content(body, "name", "keywords")
    note(f"  meta keywords: {keywords}")

    # Tags visibles: <a class="tag" href="...">nombre</a>
    tags = re.findall(r'<a[^>]*class="tag"[^>]*>\s*([^<]+?)\s*</a>', body)
    note(f"  tags en la página ({len(tags)}): {tags}")

    # Fecha de publicación (para year).
    m = re.search(r'(released|releases)\s+([A-Z][a-z]+ \d{1,2}, \d{4})', body)
    if m:
        note(f"  fecha en la página: '{m.group(0)}'")

    # data-tralbum lleva el JSON completo del release (fuente alternativa).
    note(f"  data-tralbum presente: {'data-tralbum=' in body}")
    note()


# ------------------------------------------------------------------
# Parte B: volúmenes por tag vía discover_web
# ------------------------------------------------------------------

def discover_body(tag):
    return {"tag_norm_names": [tag], "include_result_types": ["a", "s"],
            "category_id": 0, "geoname_id": 0, "slice": "new",
            "cursor": "*", "size": 20}


def probe_tag_volume(tag, canon_urls, canon_ids):
    safe = re.sub(r"[^a-z0-9-]", "_", tag)
    status, resp, _ = fetch(DISCOVER_API, post_json=discover_body(tag),
                            save_as=f"discover_{safe}.json")
    try:
        p = json.loads(resp)
    except json.JSONDecodeError:
        note(f"  {tag}: ✗ no-JSON: {resp[:200]!r}")
        return
    if not isinstance(p.get("results"), list):
        note(f"  {tag}: ✗ sin results: {resp[:300]!r}")
        return
    urls = {normalize_url((r.get("item_url") or "")) for r in p["results"]} - {None}
    ids = {r.get("item_id") for r in p["results"]} - {None}
    first = p["results"][0] if p["results"] else {}
    note(f"  {tag}: result_count={p.get('result_count')} "
         f"batch={p.get('batch_result_count')} | solape 1ª página: "
         f"{len(urls & canon_urls)}/{len(urls)} URL, {len(ids & canon_ids)}/{len(ids)} id")
    if first:
        note(f"    1º: {first.get('band_name')!r} — {first.get('title')!r} "
             f"[{first.get('band_location')!r}]")


def normalize_url(url):
    if not url:
        return None
    u = urlparse(url.split("?", 1)[0].split("#", 1)[0])
    return f"{u.netloc.lower()}{u.path.rstrip('/')}"


def load_canonical_keys():
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    urls = {normalize_url(a["url"]) for a in data["albums"] if a["url"]}
    ids = {a["album_id"] for a in data["albums"] if a["album_id"] is not None}
    return urls, ids


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--extra-tags", default="", help="(reservado; sin uso en v3)")
    parser.parse_args()

    OUT_DIR.mkdir(exist_ok=True)
    canon_urls, canon_ids = load_canonical_keys()
    note(f"Sondeo v3 — presupuesto {MAX_REQUESTS} requests, {DELAY_SECONDS}s entre requests")
    note()

    try:
        note("=== A: ¿fichas de álbum accesibles? ===")
        note()
        # Una ficha veterana del canónico (id 0) y una descubierta en v2.
        probe_album_page("canonico", "https://cobrarocks.bandcamp.com/album/henko")
        probe_album_page("nueva", "https://zaratazarautz.bandcamp.com/album/1991-2026-05-22")

        note("=== B: volumen por tag (discover_web, slice=new) ===")
        note()
        for tag in ("bilbao", "donostia", "gasteiz", "iruña", "euskal-herria",
                    "euskadi", "basque"):
            if budget_left() < 1:
                note("  (presupuesto agotado)")
                break
            probe_tag_volume(tag, canon_urls, canon_ids)
    except BudgetExhausted:
        note(f"\n⚠ presupuesto de {MAX_REQUESTS} requests agotado; sondeo truncado")

    note()
    note(f"=== Fin del sondeo v3: {_requests_done}/{MAX_REQUESTS} requests usados ===")
    (OUT_DIR / "summary.md").write_text("\n".join(_report_lines) + "\n",
                                        encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
