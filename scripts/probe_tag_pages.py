#!/usr/bin/env python3
"""Sondeo de descubrimiento por tags en Bandcamp — GATE de la Fase 2 (SOLO lectura). v2.

El sondeo v1 (run 29197223469) demostró que las páginas /tag/<slug>
clásicas YA NO EXISTEN: Bandcamp redirige todas a /discover/<slug>
(shell SPA de ~3 KB sin JSON embebido) y el endpoint antiguo
api/hub/2/dig_deeper responde {error, error_message}. Anti-bot: ninguno
desde runners de GitHub (todo 200 con UA de navegador).

Esta v2 sondea (≤10 requests, 1 req/2s) los DOS canales de descubrimiento
que quedan vivos:

  A. El Discover nuevo: shell de /discover/<tag> + su API JSON
     (POST bandcamp.com/api/discover/1/discover_web), probando cuerpos
     candidatos de forma adaptativa y leyendo los mensajes de error de
     la propia API para caracterizar el contrato real.
  B. La búsqueda clásica (/search?q=<tag>&item_type=a&page=N), que es de
     donde salió el dataset original (?from=search&search_sig=...) y
     sigue siendo HTML renderizado en servidor con paginación por URL.

Todas las respuestas se imprimen (truncadas) a stdout — los logs del job
son el informe — y las crudas van a probe_out/ como artifact. No escribe
NADA en data/ ni toca el canónico. Los errores por request no abortan el
sondeo; exit != 0 solo ante fallo fatal del script.

Uso:
    python3 scripts/probe_tag_pages.py
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

# Presupuesto DURO acordado para el gate.
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
    """Un request con presupuesto, rate limit y captura de errores."""
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
# Dedupe contra el canónico (offline)
# ------------------------------------------------------------------

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


# ------------------------------------------------------------------
# Canal A: Discover nuevo
# ------------------------------------------------------------------

DISCOVER_API = "https://bandcamp.com/api/discover/1/discover_web"

# Cuerpos candidatos, del más completo (hipótesis del contrato del
# Discover 2023) al mínimo. Los mensajes de error de la API ante campos
# ausentes/erróneos son parte del resultado del sondeo.
def candidate_bodies(tag):
    return [
        {"tag_norm_names": [tag], "include_result_types": ["a", "s"],
         "category_id": 0, "geoname_id": 0, "slice": "new",
         "cursor": "*", "size": 20},
        {"tag_norm_names": [tag]},
    ]


def extract_result(d):
    """Normaliza un resultado del discover/search a campos conocidos."""
    url = d.get("item_url") or d.get("tralbum_url") or d.get("url")
    return {
        "url": url,
        "artist": d.get("band_name") or d.get("artist") or d.get("artist_name"),
        "title": d.get("title"),
        "item_id": d.get("item_id") or d.get("id") or d.get("tralbum_id"),
        "item_type": d.get("item_type") or d.get("result_type"),
        "location": d.get("band_location") or d.get("location"),
    }


def report_results_list(label, results, canon_urls, canon_ids):
    note(f"  {label}: {len(results)} resultados")
    if not results:
        return
    note(f"    campos del result[0]: {sorted(results[0].keys())}")
    for d in results[:3]:
        r = extract_result(d)
        note(f"    · {r['artist']!r} — {r['title']!r} → {r['url']}")
        note(f"      item_id={r['item_id']} type={r['item_type']} location={r['location']!r}")
    urls = {normalize_url(extract_result(d)["url"]) for d in results} - {None}
    ids = {extract_result(d)["item_id"] for d in results} - {None}
    note(f"    solape con canónico: {len(urls & canon_urls)}/{len(urls)} por URL, "
         f"{len(ids & canon_ids)}/{len(ids)} por album_id")


def probe_discover(canon_urls, canon_ids):
    note("=== CANAL A: Discover nuevo ===")
    note()
    # A1. Shell HTML: se imprime entero (es ~3 KB) buscando el contrato
    # del frontend (endpoints, JSON embebido, bundles).
    status, body, _ = fetch("https://bandcamp.com/discover/bilbao",
                            save_as="discover_bilbao.html")
    if isinstance(status, int) and status == 200:
        note("  --- shell de /discover/bilbao (completo) ---")
        for line in body.splitlines():
            if line.strip():
                note("  | " + line[:400])
        note("  --- fin del shell ---")
    note()

    # A2. API discover_web con cuerpos candidatos (adaptativo).
    payload = None
    for i, cand in enumerate(candidate_bodies("bilbao"), 1):
        note(f"  discover_web intento {i}: {json.dumps(cand, ensure_ascii=False)}")
        status, resp, _ = fetch(
            DISCOVER_API, post_json=cand,
            extra_headers={"Referer": "https://bandcamp.com/discover/bilbao",
                           "Origin": "https://bandcamp.com",
                           "X-Requested-With": "XMLHttpRequest"},
            save_as=f"discover_web_bilbao_try{i}.json")
        note(f"    respuesta cruda (1500 chars): {resp[:1500]!r}")
        try:
            parsed = json.loads(resp)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, dict) and isinstance(parsed.get("results"), list):
            payload = parsed
            note(f"    ✓ contrato encontrado — claves de la respuesta: {sorted(parsed.keys())}")
            break
        if budget_left() <= 4:
            note("    (reservando presupuesto para el canal B; no más intentos)")
            break

    if payload is None:
        note("  ✗ discover_web no devolvió resultados con ningún cuerpo candidato")
        note()
        return

    report_results_list("discover bilbao p1", payload["results"], canon_urls, canon_ids)
    for k in ("cursor", "total", "total_count", "batch_result_count", "more_available"):
        if k in payload:
            note(f"    {k} = {json.dumps(payload[k])[:200]}")
    note()

    # A3. Continuidad de paginación con el cursor devuelto.
    cursor = payload.get("cursor")
    if cursor and budget_left() > 3:
        body2 = dict(candidate_bodies("bilbao")[0])
        body2["cursor"] = cursor
        note(f"  discover_web página 2 (cursor={str(cursor)[:60]!r}...)")
        status, resp, _ = fetch(DISCOVER_API, post_json=body2,
                                save_as="discover_web_bilbao_p2.json")
        try:
            p2 = json.loads(resp)
            if isinstance(p2.get("results"), list):
                report_results_list("discover bilbao p2", p2["results"],
                                    canon_urls, canon_ids)
            else:
                note(f"    ✗ sin results: {resp[:400]!r}")
        except json.JSONDecodeError:
            note(f"    ✗ no-JSON: {resp[:400]!r}")
        note()

    # A4. Volumen de un segundo tag de la oleada.
    if budget_left() > 2:
        note("  discover_web donostia (volumen)")
        status, resp, _ = fetch(DISCOVER_API,
                                post_json=candidate_bodies("donostia")[0],
                                save_as="discover_web_donostia.json")
        try:
            pd = json.loads(resp)
            if isinstance(pd.get("results"), list):
                report_results_list("discover donostia p1", pd["results"],
                                    canon_urls, canon_ids)
                for k in ("total", "total_count", "cursor"):
                    if k in pd:
                        note(f"    {k} = {json.dumps(pd[k])[:200]}")
            else:
                note(f"    ✗ sin results: {resp[:400]!r}")
        except json.JSONDecodeError:
            note(f"    ✗ no-JSON: {resp[:400]!r}")
        note()


# ------------------------------------------------------------------
# Canal B: búsqueda clásica (origen del dataset)
# ------------------------------------------------------------------

def probe_search(canon_urls, canon_ids):
    note("=== CANAL B: búsqueda clásica /search ===")
    note()
    for tag, page in (("bilbao", 1), ("donostia", 2)):
        if budget_left() < 1:
            note("  (sin presupuesto para más búsquedas)")
            break
        url = f"https://bandcamp.com/search?q={quote(tag)}&item_type=a&page={page}"
        status, body, final = fetch(url, save_as=f"search_{tag}_p{page}.html")
        if not (isinstance(status, int) and status == 200):
            note(f"  search {tag} p{page}: ✗ status {status}")
            continue

        # Resultados: enlaces a álbum con la firma ?from=search.
        links = re.findall(
            r'href="(https://[^"/]+\.bandcamp\.com/(?:album|track)/[^"?]+)[^"]*from=search',
            body)
        uniq = list(dict.fromkeys(links))
        note(f"  search {tag} p{page}: {len(uniq)} URLs de resultado con firma from=search")
        for u in uniq[:3]:
            note(f"    · {u}")
        if uniq:
            norm = {normalize_url(u) for u in uniq}
            note(f"    solape con canónico: {len(norm & canon_urls)}/{len(norm)} por URL")

        # Estructura y paginación.
        for pat, label in [
            (r'class="searchresult', "items 'searchresult'"),
            (r'class="result-info', "bloques 'result-info'"),
            (r'class="itemtype"', "campo itemtype"),
            (r'class="subhead"', "subhead (artista/location)"),
            (r'class="released"', "campo released (¡año en el listado!)"),
            (r'class="tags[^"]*"', "campo tags en el listado"),
            (r'search_page=\d+|&page=\d+', "paginación por URL"),
            (r'class="pager|class="pagelabel', "bloque de paginación"),
        ]:
            n = len(re.findall(pat, body))
            if n:
                note(f"    estructura: {n}x {label}")

        # ¿Cuántas páginas dice haber?
        m = re.findall(r'page=(\d+)', body)
        if m:
            note(f"    máxima página referenciada en el HTML: {max(int(x) for x in m)}")
        note()


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--extra-tags", default="", help="(reservado; sin uso en v2)")
    parser.parse_args()

    OUT_DIR.mkdir(exist_ok=True)
    canon_urls, canon_ids = load_canonical_keys()
    note(f"Sondeo v2 — presupuesto {MAX_REQUESTS} requests, {DELAY_SECONDS}s entre requests")
    note(f"Canónico: {len(canon_urls)} URLs normalizadas, {len(canon_ids)} album_ids")
    note()

    try:
        probe_discover(canon_urls, canon_ids)
        probe_search(canon_urls, canon_ids)
    except BudgetExhausted:
        note(f"\n⚠ presupuesto de {MAX_REQUESTS} requests agotado; sondeo truncado")

    note()
    note(f"=== Fin del sondeo v2: {_requests_done}/{MAX_REQUESTS} requests usados ===")
    (OUT_DIR / "summary.md").write_text("\n".join(_report_lines) + "\n",
                                        encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
