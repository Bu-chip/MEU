#!/usr/bin/env python3
"""Propuestas del público — MEU / formulario «proponer un disco».

La web (app/src/pages/Proponer.jsx) tiene un formulario sin backend: envía
por debajo a un Google Form privado cuyas respuestas caen en un Sheet
publicado como CSV de solo lectura. Este script lee ese CSV y convierte
cada propuesta en candidatos con el mismo esquema que los robots de
descubrimiento, para que entren al catálogo por el mismo camino: un PR
que revisa Miguel.

PRINCIPIO INNEGOCIABLE: el robot propone, Miguel dispone. Este script
JAMÁS toca data/bandcamp_bilbaotags_clean.json. Y como el formulario es
público (carne de bots), NADA de lo que llega entra sin revisión: el
script solo prepara fichas y las deja en un PR.

Flujo:

  1. CSV: descarga las respuestas (o lee --csv-file). Columnas por
     encabezado (marca temporal, URL, lugar, sello, relacionados,
     comentario); el orden y los textos exactos no importan.
  2. URLS: de la URL principal y del campo «relacionados» se sacan todas
     las de *.bandcamp.com. Cada una es una ficha de disco (/album/), la
     portada de una cuenta (grupo o sello: se recorre su /music como
     discover_accounts.py) o un tema suelto (/track/: no se propone, el
     canónico no tiene temas). Los dominios propios y cualquier otra web
     quedan anotados para revisión manual.
  3. DEDUPE: contra el canónico, rechazados, todos los candidatos y las
     fichas pendientes de los otros robots (load_known de
     discover_accounts.py). Una cuenta ya recorrida por discover_accounts
     no se vuelve a pedir.
  4. FICHA: la de discover_accounts.py (artista, título, año, tags,
     portada, album_id, ubicación de la cuenta).
  5. SALIDA: data/candidates_propuestas-YYYY-MM.json. Cada candidato
     lleva además `proposal`: {submitted_at, place, label, comment} tal
     como lo escribió quien propuso, para que Miguel lo vea en la tabla.
     Se incorpora con `merge_candidates.py propuestas-YYYY-MM` (que
     descarta los campos extra, como con los otros robots).
  6. ESTADO: data/proposals_state.json recuerda qué filas del CSV ya se
     procesaron y con qué resultado; una fila no se repite aunque el CSV
     la traiga siempre.

Uso:
    python3 scripts/proposals.py --budget 200
    python3 scripts/proposals.py --csv-file /tmp/respuestas.csv --month 2026-09
    python3 scripts/proposals.py --table data/candidates_propuestas-2026-09.json
"""

import argparse
import csv
import hashlib
import io
import json
import os
import re
import sys
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
from discover_tags import (  # noqa: E402
    HEADERS, REPO_ROOT, REQUEST_TIMEOUT,
    BudgetExhausted, ContractError, Session,
    atomic_save, load_canonical_keys, load_json_or, load_rejected,
    normalize_url, now_iso,
)
from discover_accounts import (  # noqa: E402
    fetch_page, load_known, music_url, parse_music_page, run_fichas,
)
from locations import ingest_doc as ingest_locations  # noqa: E402

# Sheet de respuestas del Google Form, publicado como CSV de solo lectura
# (Archivo → Compartir → Publicar en la web → CSV). Se puede cambiar con
# la variable PROPOSALS_CSV sin tocar el código.
CSV_URL = os.environ.get("PROPOSALS_CSV") or (
    "https://docs.google.com/spreadsheets/d/e/2PACX-1vQVUGPuO4A87frE3fWm9rxDtoz3dXZ2YJv1mov3ap4qhD7YTuZ9SsJEo9vFXxax6TOX7NGe5FGw-oUW/pub?output=csv"
)

STATE_FILE = REPO_ROOT / "data" / "proposals_state.json"
ACCOUNTS_STATE_FILE = REPO_ROOT / "data" / "discovery_state_cuentas.json"
PREFIX = "propuestas"

# Encabezado del CSV → campo. Se casa por palabras clave para que un
# retoque del texto de la pregunta no rompa el robot.
COLUMN_KEYS = [
    ("submitted_at", ("marca temporal", "timestamp")),
    ("url", ("url", "enlace")),
    ("place", ("dónde", "donde", "pueblo", "ciudad")),
    ("label", ("sello", "colectivo")),
    ("related", ("relacionad", "otros grupos")),
    ("comment", ("comentario",)),
]

# Un formulario público recibe basura: tope de enlaces por propuesta.
MAX_URLS_PER_ROW = 10

BANDCAMP_URL_RE = re.compile(r"https?://[a-z0-9-]+\.bandcamp\.com[^\s<>\"']*", re.I)
ACCOUNT_PATHS = {"", "/", "/music", "/releases", "/music/", "/releases/"}


# ------------------------------------------------------------------
# CSV (puro: lo prueban los tests)
# ------------------------------------------------------------------

def map_columns(header):
    """Índice de columna de cada campo, o None si no está."""
    index = {}
    for field, keys in COLUMN_KEYS:
        index[field] = None
        for i, name in enumerate(header):
            low = name.strip().lower()
            if any(k in low for k in keys) and i not in index.values():
                index[field] = i
                break
    return index


def parse_rows(text):
    """CSV publicado → [{submitted_at, url, place, label, related, comment, key}].

    `key` identifica la fila de forma estable entre descargas (marca
    temporal + URL): es la clave del estado. Filas sin URL se ignoran.
    """
    reader = csv.reader(io.StringIO(text))
    try:
        header = next(reader)
    except StopIteration:
        return []
    cols = map_columns(header)
    if cols["url"] is None:
        raise ValueError(f"el CSV no tiene columna de URL: {header}")
    rows = []
    for raw in reader:
        def cell(field):
            i = cols[field]
            return raw[i].strip() if i is not None and i < len(raw) else ""
        row = {f: cell(f) for f, _ in COLUMN_KEYS}
        if not row["url"] and not row["related"]:
            continue
        row["key"] = hashlib.sha1(
            f"{row['submitted_at']}|{row['url']}".encode("utf-8")).hexdigest()[:16]
        rows.append(row)
    return rows


def extract_urls(*texts):
    """Todas las URL de *.bandcamp.com de los textos, sin repetir, en orden."""
    out = []
    for text in texts:
        for m in BANDCAMP_URL_RE.finditer(text or ""):
            url = m.group(0).rstrip(".,;:)")
            if url not in out:
                out.append(url)
    return out


def classify_url(url):
    """→ ("album"|"track"|"account"|"other", clave).

    Para account la clave es el subdominio (cuenta de Bandcamp, como en
    locations_lib.account_of). Los dominios propios no se pueden
    reconocer sin pedir la página: van a "other" para revisión manual.
    """
    u = urlparse(url.strip())
    host = u.netloc.lower()
    if not host.endswith(".bandcamp.com") or host.count(".") != 2:
        return "other", url
    account = host[: -len(".bandcamp.com")]
    path = u.path
    if path.startswith("/album/") and len(path) > len("/album/"):
        return "album", url.split("?", 1)[0].split("#", 1)[0]
    if path.startswith("/track/"):
        return "track", url
    if path in ACCOUNT_PATHS:
        return "account", account
    return "other", url


def proposal_of(row):
    return {
        "submitted_at": row["submitted_at"] or None,
        "place": row["place"] or None,
        "label": row["label"] or None,
        "comment": row["comment"] or None,
    }


def account_of_url(url):
    return urlparse(url).netloc.lower()[: -len(".bandcamp.com")]


# ------------------------------------------------------------------
# Red
# ------------------------------------------------------------------

def download_csv(url):
    req = urllib.request.Request(url, headers={"User-Agent": HEADERS["User-Agent"]})
    with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
        return resp.read().decode("utf-8-sig")


# ------------------------------------------------------------------
# Fase 1: propuestas → parciales
# ------------------------------------------------------------------

def enqueue_album(state, known, url, row, account=None, location=None):
    nurl = normalize_url(url)
    if nurl in known:
        return "ya_conocido"
    state["pending_fichas"][nurl] = {
        "artist": None,
        "title": None,
        "genre": None,
        "year": None,
        "tags": [],
        "url": url,
        "cover_url": None,
        "album_id": None,
        "band_location": location,
        "source_tags": [],
        "source_account": account or account_of_url(url),
        "source_place": None,
        "proposal": proposal_of(row),
        "discovered_at": now_iso(),
    }
    known.add(nurl)
    return "encolado"


def run_proposals(session, rows, state, known, swept_accounts, log):
    """Procesa las filas nuevas del CSV. Devuelve nº de parciales nuevos.

    Recorrer la /music de una cuenta consume un request; las demás
    operaciones son gratis. Una fila se marca procesada solo cuando todas
    sus URL han quedado resueltas; si el presupuesto se agota a medias,
    se retoma en la próxima pasada (lo ya encolado está en `known`).
    """
    fresh = 0
    challenge_streak = 0
    for row in rows:
        if row["key"] in state["rows"]:
            continue
        urls = extract_urls(row["url"], row["related"])
        outcomes = {}
        if not urls:
            # Un dominio propio de Bandcamp (p. ej. queimadacircuitrecords.com)
            # llega aquí: no se distingue de otra web sin pedir la página.
            es_url = row["url"].lower().startswith(("http://", "https://"))
            outcomes[row["url"] or "(vacío)"] = "revisar_a_mano" if es_url else "sin_url_bandcamp"
        for url in urls[:MAX_URLS_PER_ROW]:
            kind, key = classify_url(url)
            if kind == "album":
                outcomes[url] = enqueue_album(state, known, key, row)
                fresh += outcomes[url] == "encolado"
            elif kind == "track":
                outcomes[url] = "tema_suelto"
            elif kind == "other":
                outcomes[url] = "revisar_a_mano"
            else:  # cuenta: grupo o sello
                if key in state["accounts"] or key in swept_accounts:
                    outcomes[url] = "cuenta_ya_recorrida"
                    continue
                if session.left() < 1:
                    raise BudgetExhausted()
                murl = music_url(key)
                try:
                    page, err = fetch_page(session, murl)
                except ContractError:
                    challenge_streak += 1
                    if challenge_streak >= 3:
                        raise
                    outcomes[url] = "client_challenge"
                    continue
                challenge_streak = 0
                if page is None:
                    state["accounts"][key] = {"checked_at": now_iso(), "status": err}
                    outcomes[url] = err
                    continue
                albums, n_tracks, location = parse_music_page(page, murl)
                n_new = 0
                for item_id, album_url, _title in albums:
                    if item_id in known:
                        continue
                    if enqueue_album(state, known, album_url, row, key, location) == "encolado":
                        state["pending_fichas"][normalize_url(album_url)]["album_id"] = item_id
                        known.add(item_id)
                        n_new += 1
                fresh += n_new
                state["accounts"][key] = {
                    "checked_at": now_iso(), "status": "ok", "location": location,
                    "albums": len(albums), "tracks": n_tracks, "new": n_new,
                }
                outcomes[url] = f"cuenta: {len(albums)} discos, {n_new} nuevos"
        state["rows"][row["key"]] = {
            "processed_at": now_iso(),
            "submitted_at": row["submitted_at"],
            "url": row["url"],
            "place": row["place"],
            "label": row["label"],
            "related": row["related"],
            "comment": row["comment"],
            "outcomes": outcomes,
        }
        log(f"  {row['submitted_at'] or '?'} {row['url']}: "
            + "; ".join(f"{k} → {v}" for k, v in outcomes.items()))
    return fresh


# ------------------------------------------------------------------
# Tabla legible para la revisión del PR
# ------------------------------------------------------------------

def row_yielded(outcomes):
    """¿La propuesta encoló al menos una ficha nueva?"""
    for v in outcomes.values():
        if v == "encolado":
            return True
        if str(v).startswith("cuenta:") and not str(v).endswith(" 0 nuevos"):
            return True
    return False


def render_table(candidates_path, state_path=STATE_FILE):
    """Markdown agrupado por propuesta, más las propuestas sin resultado."""
    data = load_json_or(Path(candidates_path), {"meta": {}, "candidates": [], "deferred_oleada2": []})
    state = load_json_or(Path(state_path), {"rows": {}})
    rows = data["candidates"] + data.get("deferred_oleada2", [])
    by_prop = defaultdict(list)
    for c in rows:
        p = c.get("proposal") or {}
        by_prop[(p.get("submitted_at") or "?", c["source_account"])].append(c)
    cell = lambda s: str(s or "").replace("|", "\\|").replace("\n", " ")  # noqa: E731
    lines = [
        f"# Candidatos propuestos por el público — {data['meta'].get('month', '?')}",
        "",
        f"{len(rows)} candidatos de {len(by_prop)} propuestas del formulario "
        "«proponer un disco». Lo que escribió quien propuso (lugar, sello, "
        "comentario) va tal cual, sin verificar. `source_tags` va vacío a propósito.",
        "",
    ]
    for (when, account), cands in sorted(by_prop.items()):
        p = cands[0].get("proposal") or {}
        extra = " · ".join(f"{k}: {cell(p[k])}" for k in ("place", "label", "comment") if p.get(k))
        lines += [f"## {when} · {account}" + (f" — {extra}" if extra else ""), "",
                  "| Artista | Título | Año | Tags | Ubicación (Bandcamp) |",
                  "|---|---|---|---|---|"]
        for c in sorted(cands, key=lambda c: (c["year"] or 0, c["title"] or "")):
            tags = ", ".join(c["tags"][:6]) + (" …" if len(c["tags"]) > 6 else "")
            lines.append(f"| {cell(c['artist'])} | [{cell(c['title'])}]({c['url']}) "
                         f"| {c['year'] or ''} | {cell(tags)} | {cell(c['band_location'])} |")
        lines.append("")

    sin = [(r["submitted_at"] or "?", r) for r in state.get("rows", {}).values()
           if not row_yielded(r["outcomes"])]
    if sin:
        lines += ["## Propuestas sin candidatos nuevos", "",
                  "Ya estaban en el catálogo o en otro PR, eran temas sueltos, o no "
                  "eran enlaces de bandcamp.com (revisar a mano si merece la pena).", "",
                  "| Fecha | Propuesta | Resultado | Lugar · sello · comentario |", "|---|---|---|---|"]
        for when, r in sorted(sin, key=lambda x: x[0]):
            res = "; ".join(f"{cell(k)} → {cell(v)}" for k, v in r["outcomes"].items())
            extra = " · ".join(cell(r[k]) for k in ("place", "label", "comment") if r.get(k))
            lines.append(f"| {when} | {cell(r['url'])} | {res} | {extra} |")
        lines.append("")
    return "\n".join(lines)


# ------------------------------------------------------------------
# Principal
# ------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--budget", type=int, default=200,
                        help="presupuesto duro de requests a Bandcamp")
    parser.add_argument("--csv-file", default=None,
                        help="leer las respuestas de este fichero en vez de descargarlas")
    parser.add_argument("--month", default=None,
                        help="sufijo YYYY-MM (por defecto, el mes actual UTC)")
    parser.add_argument("--delay-min", type=float, default=2.0)
    parser.add_argument("--delay-max", type=float, default=2.3)
    parser.add_argument("--table", metavar="CANDIDATES_JSON",
                        help="no scrapea: imprime la tabla markdown del fichero dado")
    args = parser.parse_args()

    if args.table:
        print(render_table(args.table))
        return 0

    month = args.month or datetime.now(timezone.utc).strftime("%Y-%m")
    out_file = REPO_ROOT / "data" / f"candidates_{PREFIX}-{month}.json"
    log = lambda msg: print(msg, flush=True)  # noqa: E731

    text = Path(args.csv_file).read_text(encoding="utf-8-sig") if args.csv_file \
        else download_csv(CSV_URL)
    rows = parse_rows(text)

    state = load_json_or(STATE_FILE, {})
    state.setdefault("rows", {})
    state.setdefault("accounts", {})
    state.setdefault("pending_fichas", {})
    state.setdefault("fichas_error", {})

    out = load_json_or(out_file, {})
    out.setdefault("meta", {})
    out.setdefault("candidates", [])
    out.setdefault("deferred_oleada2", [])

    canon_urls, canon_ids = load_canonical_keys()
    known = load_known(canon_urls, canon_ids, load_rejected(), out_file, state)
    for c in out["candidates"] + out["deferred_oleada2"]:
        known.add(normalize_url(c["url"]))
        if c["album_id"] is not None:
            known.add(c["album_id"])
    swept = set(load_json_or(ACCOUNTS_STATE_FILE, {}).get("accounts", {}))

    session = Session(args.budget, args.delay_min, args.delay_max)

    def content_sig():
        out["candidates"].sort(key=lambda c: normalize_url(c["url"]))
        return json.dumps(out["candidates"], ensure_ascii=False, sort_keys=True)

    baseline_sig = content_sig()

    def checkpoint():
        atomic_save(STATE_FILE, state)
        if content_sig() != baseline_sig or not out_file.exists():
            out["meta"].update({
                "generated_at": now_iso(),
                "month": month,
                "source": "scripts/proposals.py (formulario «proponer un disco»)",
                "schema": "candidato = canónico sin id + band_location, source_tags "
                          "(vacío: entra por propuesta), source_account, proposal "
                          "{submitted_at, place, label, comment} sin verificar, "
                          "discovered_at; los id se asignan al merge",
            })
            atomic_save(out_file, out)
            ingest_locations(out, out_file.name, f"data/{out_file.name}")

    new_rows = [r for r in rows if r["key"] not in state["rows"]]
    log(f"Propuestas del formulario — {len(rows)} filas en el CSV, {len(new_rows)} nuevas; "
        f"presupuesto {args.budget} requests")
    log(f"Dedupe contra {len(known)} claves (canónico, rechazados, candidatos, pendientes)")
    log("")

    exit_code = 0
    fresh = fichas_ok = fichas_err = 0
    try:
        log("=== Fase 1: propuestas ===")
        fresh = run_proposals(session, rows, state, known, swept, log)
        checkpoint()
        log(f"  parciales nuevos: {fresh} (pendientes de ficha: {len(state['pending_fichas'])})")
        log("")
        log("=== Fase 2: fichas ===")
        # Sin cola oleada-2: quien propone ya ha decidido que es de aquí;
        # Miguel ve la ubicación en la tabla.
        fichas_ok, fichas_err, _ = run_fichas(session, state, out, {}, log, checkpoint)
    except BudgetExhausted:
        log(f"\npresupuesto de {args.budget} requests agotado; "
            "la próxima pasada continúa desde el checkpoint")
    except ContractError as exc:
        log(f"\nERROR DE CONTRATO: {exc}")
        log("La pasada se detiene sin reintentos. Ejecuta el canario "
            "(workflow probe-tag-pages) y revisa docs/scraping-method.md.")
        exit_code = 2
    finally:
        checkpoint()

    log("")
    log("=== Resumen de la pasada ===")
    log(f"requests usados: {session.done}/{args.budget}")
    log(f"filas procesadas: {len(state['rows'])}/{len(rows)}")
    log(f"parciales nuevos descubiertos: {fresh}")
    log(f"fichas completadas: {fichas_ok} (errores: {fichas_err})")
    log(f"candidatos acumulados: {len(out['candidates'])}")
    log(f"fichas pendientes para la próxima pasada: {len(state['pending_fichas'])}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
