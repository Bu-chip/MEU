#!/usr/bin/env python3
"""Scrape de portadas y album_id de Bandcamp — MEU / Bilbao Underground.

Lee data/bandcamp_bilbaotags_clean.json (SOLO lectura: este script
nunca modifica el dataset canónico) y, para cada álbum con URL,
descarga la página y extrae:

  - cover_url: del meta <meta property="og:image" ...>. El sufijo de
    tamaño de bcbits.com (_10, _16...) es intercambiable, así que se
    guarda la URL tal cual y los thumbnails se pueden derivar después
    sin re-scrapear.
  - album_id / item_type: del meta <meta name="bc-page-properties" ...>
    (JSON HTML-escapado con item_id e item_type). Si falta, se intenta
    recuperar album_id del og:video (.../EmbeddedPlayer/v=2/album=NNN/...).
    El album_id alimenta el player embebido oficial de Bandcamp.

El resultado se escribe en data/covers.json, keyed por el `id` del
dataset. La pasada es REANUDABLE: si el archivo de salida ya existe,
los items con status "ok" se saltan y los que quedaron en "error" se
reintentan. Cada --checkpoint items se reescribe el archivo de forma
atómica, así un corte a mitad de pasada pierde como mucho ese tramo.

Los errores por item (403, timeout, metas ausentes...) quedan
registrados en el propio item y por stderr, pero NUNCA abortan la
pasada. El exit code es 0 aunque haya errores de item; solo es != 0
ante un fallo fatal (dataset ilegible, etc.).

Uso:
    python3 scripts/scrape_covers.py --limit 20   # pasada de prueba
    python3 scripts/scrape_covers.py              # pasada completa
"""

import argparse
import html
import json
import os
import random
import re
import socket
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = REPO_ROOT / "data" / "bandcamp_bilbaotags_clean.json"
OUT_FILE = REPO_ROOT / "data" / "covers.json"

# Bandcamp devuelve 403 a los User-Agent por defecto de urllib/requests,
# así que nos presentamos como un navegador de escritorio corriente.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
}

REQUEST_TIMEOUT = 30  # segundos


def fetch(url):
    """Descarga una página y devuelve su HTML como texto."""
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
        return resp.read().decode("utf-8", errors="replace")


def classify_error(exc):
    """Mapea una excepción de red a un código corto para el campo `error`."""
    if isinstance(exc, urllib.error.HTTPError):
        return f"http_{exc.code}"
    if isinstance(exc, (socket.timeout, TimeoutError)):
        return "timeout"
    if isinstance(exc, urllib.error.URLError):
        if isinstance(exc.reason, (socket.timeout, TimeoutError)):
            return "timeout"
        return "network_error"
    if isinstance(exc, OSError):
        return "network_error"
    return "unexpected_error"


def meta_content(page, attr, value):
    """Devuelve el content del primer <meta {attr}="{value}" ...> de la página.

    Tolera los atributos en cualquier orden dentro del tag y comillas
    simples o dobles. Devuelve None si el tag o su content no aparecen.
    """
    tag_re = re.compile(
        r"<meta\b[^>]*\b{}=[\"']{}[\"'][^>]*>".format(re.escape(attr), re.escape(value)),
        re.IGNORECASE,
    )
    m = tag_re.search(page)
    if not m:
        return None
    content = re.search(r"\bcontent=[\"']([^\"']*)[\"']", m.group(0))
    return html.unescape(content.group(1)) if content else None


def parse_page(page):
    """Extrae (cover_url, album_id, item_type) del HTML de un álbum."""
    cover_url = meta_content(page, "property", "og:image")

    album_id = None
    item_type = None
    props_raw = meta_content(page, "name", "bc-page-properties")
    if props_raw:
        try:
            props = json.loads(props_raw)
            album_id = props.get("item_id")
            item_type = props.get("item_type")
        except (json.JSONDecodeError, AttributeError):
            pass

    if album_id is None:
        # Fallback: el og:video apunta al EmbeddedPlayer, que lleva el id.
        video = meta_content(page, "property", "og:video")
        if video:
            m = re.search(r"/album=(\d+)", video)
            if m:
                album_id = int(m.group(1))
                item_type = item_type or "a"

    return cover_url, album_id, item_type


def load_previous(out_path):
    """Carga los items de una pasada anterior para reanudar sobre ellos."""
    if not out_path.exists():
        return {}
    try:
        with open(out_path, encoding="utf-8") as f:
            return json.load(f).get("items", {})
    except (json.JSONDecodeError, OSError) as exc:
        print(f"AVISO: no se pudo leer {out_path} ({exc}); se empieza de cero", file=sys.stderr)
        return {}


def save(out_path, items):
    """Escritura atómica (tmp + replace): un corte nunca deja el JSON a medias."""
    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "items": items,
    }
    tmp = out_path.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, out_path)


def main():
    parser = argparse.ArgumentParser(
        description="Scrape de portadas y album_id de Bandcamp hacia data/covers.json"
    )
    parser.add_argument("--data", type=Path, default=DATA_FILE, help="dataset canónico (solo lectura)")
    parser.add_argument("--out", type=Path, default=OUT_FILE, help="JSON de salida, reanudable")
    parser.add_argument("--limit", type=int, default=0, help="máx. items pendientes a procesar (0 = todos)")
    parser.add_argument("--checkpoint", type=int, default=25, help="reescribe la salida cada N items")
    parser.add_argument("--delay-min", type=float, default=1.5, help="delay mínimo entre requests (s)")
    parser.add_argument("--delay-max", type=float, default=2.0, help="delay máximo entre requests (s)")
    args = parser.parse_args()

    try:
        with open(args.data, encoding="utf-8") as f:
            albums = json.load(f)["albums"]
    except (OSError, json.JSONDecodeError, KeyError) as exc:
        print(f"ERROR fatal: no se pudo leer el dataset {args.data}: {exc}", file=sys.stderr)
        return 1

    items = load_previous(args.out)

    # Cache por URL: el dataset tiene URLs repetidas (varias entradas para el
    # mismo álbum), así que cada URL se pide una sola vez por pasada. Se
    # siembra con los "ok" de pasadas anteriores.
    url_cache = {}
    for prev in items.values():
        if prev.get("status") == "ok":
            url_cache[prev["url"]] = prev

    counts = {"ok": 0, "cached": 0, "error": 0, "skipped_no_url": 0, "skipped_done": 0}
    error_types = {}
    processed = 0
    since_checkpoint = 0
    did_request = False

    for album in albums:
        key = str(album["id"])
        url = album.get("url")
        if not url:
            counts["skipped_no_url"] += 1
            continue
        if items.get(key, {}).get("status") == "ok":
            counts["skipped_done"] += 1
            continue
        if args.limit and processed >= args.limit:
            continue
        processed += 1

        cached = url_cache.get(url)
        if cached is not None:
            result = dict(cached)
            counts["ok"] += 1
            counts["cached"] += 1
        else:
            if did_request:
                time.sleep(random.uniform(args.delay_min, args.delay_max))
            did_request = True
            try:
                page = fetch(url)
            except Exception as exc:
                err = classify_error(exc)
                result = {"url": url, "status": "error", "error": err}
                counts["error"] += 1
                error_types[err] = error_types.get(err, 0) + 1
                print(f"[{key}] ERROR {err}: {url} ({exc})", file=sys.stderr)
            else:
                cover_url, album_id, item_type = parse_page(page)
                if cover_url is None and album_id is None:
                    result = {"url": url, "status": "error", "error": "meta_not_found"}
                    counts["error"] += 1
                    error_types["meta_not_found"] = error_types.get("meta_not_found", 0) + 1
                    print(f"[{key}] ERROR meta_not_found: {url}", file=sys.stderr)
                else:
                    if cover_url is None or album_id is None:
                        print(
                            f"[{key}] AVISO: metadatos parciales "
                            f"(cover={bool(cover_url)}, album_id={bool(album_id)}): {url}",
                            file=sys.stderr,
                        )
                    result = {
                        "url": url,
                        "cover_url": cover_url,
                        "album_id": album_id,
                        "item_type": item_type,
                        "status": "ok",
                    }
                    url_cache[url] = result
                    counts["ok"] += 1

        items[key] = result
        since_checkpoint += 1
        if since_checkpoint >= args.checkpoint:
            save(args.out, items)
            since_checkpoint = 0
            print(f"checkpoint: {processed} items procesados en esta pasada", file=sys.stderr)

    if processed:
        save(args.out, items)

    pending = sum(
        1
        for album in albums
        if album.get("url") and items.get(str(album["id"]), {}).get("status") != "ok"
    )

    print("\n=== Resumen de la pasada ===")
    print(f"procesados: {processed} (ok: {counts['ok']}, de ellos por cache: {counts['cached']}, errores: {counts['error']})")
    for err in sorted(error_types):
        print(f"  error {err}: {error_types[err]}")
    print(f"saltados sin url: {counts['skipped_no_url']}")
    print(f"saltados ya resueltos en pasadas anteriores: {counts['skipped_done']}")
    print(f"pendientes tras esta pasada (sin intentar o con error): {pending}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
