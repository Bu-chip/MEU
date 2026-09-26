#!/usr/bin/env python3
"""Descubrimiento por cuenta de Bandcamp — MEU / discografías completas.

Por qué existe: todo el catálogo ha entrado por tags (el BUE original por
el tag `bilbao`; la oleada 1 por 107 tags vía scripts/discover_tags.py),
y la búsqueda por tag deja fuera discos de grupos que ya tenemos
ubicados. Sondeo del 2026-09-26: la cuenta `fontso` (Bilbao) publica 9
discos y el canónico tiene 1; su «La distancia» lleva el tag Bilbao y
discover_web no la devolvió nunca (el tag `bilbao` está agotado en
discovery_state). El filtro por ubicación de discover_web (`geoname_id`)
tampoco sirve: ver docs/scraping-method.md.

Este script recorre la discografía (/music) de cada cuenta que el
canónico ya sitúa en un municipio de Euskal Herria y propone los discos
que faltan.

PRINCIPIO INNEGOCIABLE: el robot propone, Miguel dispone. Este script
JAMÁS toca data/bandcamp_bilbaotags_clean.json — solo produce ficheros
de candidatos que entran al catálogo vía PR revisable.

Flujo:

  1. CUENTAS: las de data/locations/resolutions.json con ubicación en un
     municipio (tipos direct, same_account, artist_inferred, manual). Por
     defecto solo account_kind=artist. Los sellos (--kind label) van a
     otro fichero: su /music es un catálogo con grupos de otros sitios y
     su ubicación es la del sello, no la del grupo.
  2. DISCOGRAFÍA: GET <cuenta>/music (dominio propio incluido). Si la
     cuenta tiene un solo disco, Bandcamp sirve directamente su ficha.
     Solo álbumes: el canónico no tiene temas sueltos (/track/); se
     cuentan en el estado pero no se proponen.
  3. DEDUPE: contra el canónico (album_id + URL normalizada), contra
     data/rejected.json, contra todos los data/candidates_*.json y contra
     las fichas pendientes de este estado y del de discover_tags.py.
  4. FICHA: tags, portada, album_id, artista, título y año de cada disco
     nuevo. A diferencia del descubrimiento por tag, un disco SIN tags
     entra igual: su vínculo vasco es la cuenta, no un tag.
  5. SALIDA: data/candidates_<prefijo>-YYYY-MM.json (prefijo `cuentas`
     para artistas, `sellos` para sellos) con el mismo esquema de
     candidato que discover_tags.py: source_tags=[] y, además,
     source_account y source_place. band_location es la ubicación que la
     propia página de la cuenta declara. Las cuentas de Iparralde van a
     deferred_oleada2 (decisión 2026-07-12: alcance CAV+Navarra).
     Se incorpora al canónico con `merge_candidates.py cuentas-YYYY-MM`.
  6. UBICACIÓN: cada checkpoint vuelca band_location a
     data/locations/observations/ (misma función que discover_tags.py).

Operativa (la de discover_tags.py): presupuesto DURO de requests por
pasada a 1 req/2 s, checkpoints atómicos en
data/discovery_state_<prefijo>.json, reanudable; una cuenta ya recorrida
no se vuelve a pedir. Tres Client Challenge seguidos → la pasada para,
guarda estado y sale con código 2 (PAUSA Y REPORTA).

Uso:
    python3 scripts/discover_accounts.py --budget 20 --accounts fontso
    python3 scripts/discover_accounts.py --places bilbo --budget 3000
    python3 scripts/discover_accounts.py --kind label
    python3 scripts/discover_accounts.py --table data/candidates_cuentas-2026-09.json
"""

import argparse
import html as html_mod
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

sys.path.insert(0, str(Path(__file__).resolve().parent))
from discover_tags import (  # noqa: E402
    REPO_ROOT, STATE_FILE as TAG_STATE_FILE, TAG_LINK_RE,
    BudgetExhausted, ContractError, Session,
    atomic_save, classify_error, load_canonical_keys, load_json_or,
    load_rejected, meta_content, normalize_tags, normalize_url, now_iso,
)
from locations import ingest_doc as ingest_locations  # noqa: E402

RESOLUTIONS_FILE = REPO_ROOT / "data" / "locations" / "resolutions.json"
PLACES_FILE = REPO_ROOT / "data" / "locations" / "places.json"

# Tipos de resolución que sitúan la cuenta en un municipio con evidencia
# de Bandcamp o humana (docs/mapa.md §3). tag_hint no cuenta.
LOCATED_TYPES = {"direct", "same_account", "artist_inferred", "manual"}

PREFIX_BY_KIND = {"artist": "cuentas", "label": "sellos"}

# Errores de ficha definitivos: no se reintentan en pasadas futuras.
FINAL_ERRORS = {"http_404", "http_410", "no_es_album", "sin_metadatos"}

GRID_ITEM_RE = re.compile(
    r'<li\b[^>]*\bdata-item-id="(album|track)-(\d+)"[^>]*>(.*?)</li>', re.S)
HREF_RE = re.compile(r'href="([^"]+)"')
CLIENT_ITEMS_RE = re.compile(r'data-client-items="([^"]+)"')
TRALBUM_RE = re.compile(r'data-tralbum="([^"]+)"')
LOCATION_RE = re.compile(r'<span class="location[^"]*">\s*([^<]*?)\s*</span>')
YEAR_RE = re.compile(r"\b(\d{4})\b")


# ------------------------------------------------------------------
# Cuentas
# ------------------------------------------------------------------

def music_url(account):
    """`custom:<host>` para dominio propio (locations_lib.account_of)."""
    if account.startswith("custom:"):
        return f"https://{account[len('custom:'):]}/music"
    return f"https://{account}.bandcamp.com/music"


def located_accounts():
    """Todas las cuentas que el canónico ubica en un municipio.

    Devuelve {cuenta: {account, place, places, territory, kind}}. `place`
    es el municipio mayoritario entre sus releases (en Bandcamp la
    ubicación es de la cuenta, así que casi siempre es único).
    """
    res = json.loads(RESOLUTIONS_FILE.read_text(encoding="utf-8"))
    places = json.loads(PLACES_FILE.read_text(encoding="utf-8"))["places"]
    territory = {p["id"]: p.get("territory") for p in places}
    seen = defaultdict(Counter)
    kinds = {}
    for r in res.values():
        acc = r.get("account")
        if not acc or not r.get("place") or r.get("type") not in LOCATED_TYPES:
            continue
        seen[acc][r["place"]] += 1
        kinds.setdefault(acc, r.get("account_kind"))
    index = {}
    for acc, counts in seen.items():
        place = counts.most_common(1)[0][0]
        index[acc] = {"account": acc, "place": place, "places": set(counts),
                      "territory": territory.get(place), "kind": kinds[acc]}
    return index


def select_accounts(index, kind, places=None, only=None):
    """Filtro de la pasada, en orden determinista. `only` ignora `kind`."""
    out = []
    for acc in sorted(index):
        info = index[acc]
        if only is not None:
            if acc not in only:
                continue
        elif info["kind"] != kind:
            continue
        if places and not info["places"] & places:
            continue
        out.append(info)
    return out


# ------------------------------------------------------------------
# Parsers (puros: los prueba tests/test_discover_accounts.py)
# ------------------------------------------------------------------

def parse_location(page):
    m = LOCATION_RE.search(page)
    if not m:
        return None
    return html_mod.unescape(m.group(1)).strip() or None


def parse_music_page(page, base_url):
    """Página /music de una cuenta → (albums, n_tracks, location).

    albums = [(item_id, url_sin_query, título_o_None)]. Cubre la rejilla
    <li data-item-id>, la parte diferida `data-client-items` de las
    discografías largas y la cuenta de un solo disco (Bandcamp sirve su
    ficha en lugar de la rejilla).
    """
    albums, tracks = {}, set()

    def add(kind, item_id, href, title=None):
        if kind == "track":
            tracks.add(item_id)
        elif kind == "album" and href:
            url = urljoin(base_url, html_mod.unescape(href)).split("?", 1)[0]
            albums.setdefault(item_id, (item_id, url, title))

    for m in GRID_ITEM_RE.finditer(page):
        href = HREF_RE.search(m.group(3))
        add(m.group(1), int(m.group(2)), href.group(1) if href else None)

    m = CLIENT_ITEMS_RE.search(page)
    if m:
        try:
            for it in json.loads(html_mod.unescape(m.group(1))):
                add(it.get("type"), it.get("id"), it.get("page_url"), it.get("title"))
        except (json.JSONDecodeError, AttributeError, TypeError):
            pass

    if not albums and not tracks:
        # Cuenta de un solo lanzamiento: /music sirve la propia ficha.
        props = _page_properties(page)
        og_url = meta_content(page, "property", "og:url")
        if props.get("item_id") and og_url:
            kind = {"a": "album", "t": "track"}.get(props.get("item_type"))
            add(kind, props["item_id"], og_url)

    return list(albums.values()), len(tracks), parse_location(page)


def _page_properties(page):
    raw = meta_content(page, "name", "bc-page-properties")
    try:
        return json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        return {}


def parse_album_page(page):
    """Ficha de disco → dict con los campos del candidato, o None si no
    es un álbum. Artista/título/año salen de data-tralbum, con og:title y
    el texto «released …» de respaldo."""
    props = _page_properties(page)
    if props.get("item_type") not in (None, "a"):
        return None
    tralbum = {}
    m = TRALBUM_RE.search(page)
    if m:
        try:
            tralbum = json.loads(html_mod.unescape(m.group(1)))
        except json.JSONDecodeError:
            tralbum = {}
    current = tralbum.get("current") or {}

    artist = tralbum.get("artist")
    title = current.get("title")
    if not (artist and title):
        og_title = meta_content(page, "property", "og:title") or ""
        if ", by " in og_title:
            t, a = og_title.rsplit(", by ", 1)
            title, artist = title or t.strip(), artist or a.strip()

    year = None
    for raw in (current.get("release_date"), tralbum.get("album_release_date")):
        y = YEAR_RE.search(raw or "")
        if y:
            year = int(y.group(1))
            break
    if year is None:
        y = re.search(r"released [A-Z][a-z]+ \d{1,2}, (\d{4})", page)
        year = int(y.group(1)) if y else None

    return {
        "artist": artist,
        "title": title,
        "year": year,
        "tags": normalize_tags(html_mod.unescape(t) for t in TAG_LINK_RE.findall(page)),
        "cover_url": meta_content(page, "property", "og:image"),
        "album_id": props.get("item_id") or tralbum.get("id"),
        "location": parse_location(page),
    }


# ------------------------------------------------------------------
# Fase 1: discografías
# ------------------------------------------------------------------

def fetch_page(session, url):
    """GET con la guardia de contrato común. Devuelve (page, error)."""
    try:
        page = session.fetch(url)
    except BudgetExhausted:
        raise
    except Exception as exc:
        return None, classify_error(exc)
    if "<title>Client Challenge</title>" in page:
        raise ContractError(f"Client Challenge en {url}")
    return page, None


def run_accounts(session, accounts, state, known, log, checkpoint):
    """Recorre /music de cada cuenta no visitada; acumula parciales."""
    new_partials = 0
    challenge_streak = 0
    for i, acc in enumerate(accounts, 1):
        name = acc["account"]
        if name in state["accounts"]:
            continue
        if session.left() < 1:
            raise BudgetExhausted()
        url = music_url(name)
        try:
            page, err = fetch_page(session, url)
        except ContractError:
            challenge_streak += 1
            if challenge_streak >= 3:
                raise
            continue  # sin marcar: se reintenta en la próxima pasada
        challenge_streak = 0
        if page is None:
            state["accounts"][name] = {"checked_at": now_iso(), "status": err}
            log(f"  ✗ {name}: {err}")
            continue

        albums, n_tracks, location = parse_music_page(page, url)
        fresh = 0
        for item_id, album_url, title in albums:
            nurl = normalize_url(album_url)
            if nurl in known or item_id in known:
                continue
            state["pending_fichas"][nurl] = {
                "artist": None,
                "title": title,
                "genre": None,
                "year": None,
                "tags": [],
                "url": album_url,
                "cover_url": None,
                "album_id": item_id,
                "band_location": location,
                "source_tags": [],
                "source_account": name,
                "source_place": acc["place"],
                "discovered_at": now_iso(),
            }
            known.update((nurl, item_id))
            fresh += 1
        new_partials += fresh
        state["accounts"][name] = {
            "checked_at": now_iso(), "status": "ok", "place": acc["place"],
            "albums": len(albums), "tracks": n_tracks, "new": fresh,
        }
        if fresh:
            log(f"  {name} ({acc['place']}): {len(albums)} discos, {fresh} nuevos")
        if i % 25 == 0:
            checkpoint()
    return new_partials


# ------------------------------------------------------------------
# Fase 2: fichas
# ------------------------------------------------------------------

def run_fichas(session, state, out, territory_of, log, checkpoint):
    done = errors = deferred = 0
    challenge_streak = 0
    for nurl in sorted(state["pending_fichas"]):
        if session.left() < 1:
            raise BudgetExhausted()
        partial = state["pending_fichas"][nurl]
        try:
            page, err = fetch_page(session, partial["url"])
        except ContractError:
            challenge_streak += 1
            if challenge_streak >= 3:
                raise
            state["fichas_error"][nurl] = "client_challenge"
            errors += 1
            continue
        challenge_streak = 0

        parsed = parse_album_page(page) if page is not None else None
        if page is not None and parsed is None:
            err = "no_es_album"
        elif parsed is not None and not (parsed["artist"] and parsed["title"]):
            err = "sin_metadatos"
        if err:
            state["fichas_error"][nurl] = err
            if err in FINAL_ERRORS:
                del state["pending_fichas"][nurl]
            log(f"  ✗ {partial['url']}: {err}")
            errors += 1
        else:
            candidate = dict(partial)
            for field in ("artist", "title", "year", "tags"):
                candidate[field] = parsed[field]
            if parsed["cover_url"]:
                candidate["cover_url"] = parsed["cover_url"]
            if parsed["album_id"] is not None:
                candidate["album_id"] = parsed["album_id"]
            if parsed["location"] and not candidate["band_location"]:
                candidate["band_location"] = parsed["location"]
            del state["pending_fichas"][nurl]
            state["fichas_error"].pop(nurl, None)
            if territory_of.get(candidate["source_account"]) == "Iparralde":
                out["deferred_oleada2"].append(candidate)
                deferred += 1
            else:
                out["candidates"].append(candidate)
            done += 1
        if (done + errors) % 25 == 0:
            checkpoint()
    return done, errors, deferred


# ------------------------------------------------------------------
# Tabla legible para la revisión del PR
# ------------------------------------------------------------------

def render_table(candidates_path):
    """Markdown agrupado por municipio y cuenta."""
    data = json.loads(Path(candidates_path).read_text(encoding="utf-8"))
    rows = data["candidates"] + data["deferred_oleada2"]
    by_place = defaultdict(lambda: defaultdict(list))
    for c in rows:
        by_place[c.get("source_place") or "?"][c["source_account"]].append(c)
    n_acc = len({c["source_account"] for c in rows})
    lines = [
        f"# Candidatos por cuenta — {data['meta'].get('month', '?')}",
        "",
        f"{len(data['candidates'])} candidatos (+{len(data['deferred_oleada2'])} "
        f"en cola oleada-2 Iparralde) de {n_acc} cuentas. Descubiertos "
        "recorriendo la discografía (/music) de cuentas que el canónico ya "
        "ubica; `source_tags` va vacío a propósito.",
        "",
    ]
    for place in sorted(by_place, key=lambda p: (-sum(map(len, by_place[p].values())), p)):
        accounts = by_place[place]
        lines += [f"## {place} ({sum(map(len, accounts.values()))})", "",
                  "| Cuenta | Artista | Título | Año | Tags | Ubicación |",
                  "|---|---|---|---|---|---|"]
        for acc in sorted(accounts):
            for c in sorted(accounts[acc], key=lambda c: (c["year"] or 0, c["title"] or "")):
                tags = ", ".join(c["tags"][:6]) + (" …" if len(c["tags"]) > 6 else "")
                cell = lambda s: str(s or "").replace("|", "\\|")  # noqa: E731
                lines.append(
                    f"| {cell(acc)} | {cell(c['artist'])} | [{cell(c['title'])}]({c['url']}) "
                    f"| {c['year'] or ''} | {cell(tags)} | {cell(c['band_location'])} |")
        lines.append("")
    return "\n".join(lines)


# ------------------------------------------------------------------
# Principal
# ------------------------------------------------------------------

def load_known(canon_urls, canon_ids, rejected, out_file, state):
    """Claves ya resueltas: canónico, rechazados, cualquier fichero de
    candidatos del árbol y fichas pendientes (de este estado y del de
    discover_tags.py, si está restaurado)."""
    known = set(canon_urls) | set(canon_ids) | rejected
    docs = [load_json_or(p, {}) for p in sorted((REPO_ROOT / "data").glob("candidates_*.json"))
            if p != out_file]
    tag_state = load_json_or(TAG_STATE_FILE, {})
    pendings = [state["pending_fichas"], tag_state.get("pending_fichas", {})]
    for doc in docs:
        for c in (doc.get("candidates") or []) + (doc.get("deferred_oleada2") or []):
            known.add(normalize_url(c.get("url")))
            if c.get("album_id") is not None:
                known.add(c["album_id"])
    for pending in pendings:
        for nurl, partial in pending.items():
            known.add(nurl)
            if partial.get("album_id") is not None:
                known.add(partial["album_id"])
    known.discard(None)
    return known


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--budget", type=int, default=900,
                        help="presupuesto duro de requests de la pasada")
    parser.add_argument("--kind", choices=sorted(PREFIX_BY_KIND), default="artist",
                        help="tipo de cuenta a recorrer (por defecto, artist)")
    parser.add_argument("--places", default="",
                        help="solo cuentas de estos municipios (ids de places.json, "
                             "separados por comas; p. ej. bilbo)")
    parser.add_argument("--accounts", default="",
                        help="override: solo estas cuentas (separadas por comas)")
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

    prefix = PREFIX_BY_KIND[args.kind]
    month = args.month or datetime.now(timezone.utc).strftime("%Y-%m")
    out_file = REPO_ROOT / "data" / f"candidates_{prefix}-{month}.json"
    state_file = REPO_ROOT / "data" / f"discovery_state_{prefix}.json"

    split = lambda s: {x.strip() for x in s.split(",") if x.strip()}  # noqa: E731
    index = located_accounts()
    accounts = select_accounts(index, args.kind, split(args.places) or None,
                               split(args.accounts) or None)
    # Índice completo: las fichas pendientes pueden venir de una pasada
    # anterior con otro filtro de municipios.
    territory_of = {acc: info["territory"] for acc, info in index.items()}

    state = load_json_or(state_file, {})
    state.setdefault("accounts", {})
    state.setdefault("pending_fichas", {})
    state.setdefault("fichas_error", {})

    out = load_json_or(out_file, {})
    out.setdefault("meta", {})
    out.setdefault("candidates", [])
    out.setdefault("deferred_oleada2", [])

    canon_urls, canon_ids = load_canonical_keys()
    rejected = load_rejected()
    known = load_known(canon_urls, canon_ids, rejected, out_file, state)
    for c in out["candidates"] + out["deferred_oleada2"]:
        known.add(normalize_url(c["url"]))
        if c["album_id"] is not None:
            known.add(c["album_id"])

    session = Session(args.budget, args.delay_min, args.delay_max)
    log = lambda msg: print(msg, flush=True)  # noqa: E731

    def content_sig():
        out["candidates"].sort(key=lambda c: normalize_url(c["url"]))
        out["deferred_oleada2"].sort(key=lambda c: normalize_url(c["url"]))
        return json.dumps([out["candidates"], out["deferred_oleada2"]],
                          ensure_ascii=False, sort_keys=True)

    baseline_sig = content_sig()

    def checkpoint():
        atomic_save(state_file, state)
        if content_sig() != baseline_sig or not out_file.exists():
            out["meta"].update({
                "generated_at": now_iso(),
                "month": month,
                "source": f"scripts/discover_accounts.py --kind {args.kind}",
                "schema": "candidato = canónico sin id + band_location, "
                          "source_tags (vacío: entra por cuenta), source_account, "
                          "source_place, discovered_at; los id se asignan al merge",
            })
            atomic_save(out_file, out)
            ingest_locations(out, out_file.name, f"data/{out_file.name}")

    pending_accounts = sum(1 for a in accounts if a["account"] not in state["accounts"])
    log(f"Descubrimiento por cuenta ({args.kind}) — {len(accounts)} cuentas, "
        f"{pending_accounts} sin recorrer; presupuesto {args.budget} requests, "
        f"{args.delay_min}-{args.delay_max}s entre requests")
    log(f"Dedupe contra {len(known)} claves (canónico, rechazados, candidatos, pendientes)")
    log("")

    exit_code = 0
    new_partials = fichas_ok = fichas_err = deferred = 0
    try:
        log("=== Fase 1: discografías ===")
        new_partials = run_accounts(session, accounts, state, known, log, checkpoint)
        checkpoint()
        log(f"  nuevos parciales: {new_partials} "
            f"(pendientes de ficha: {len(state['pending_fichas'])})")
        log("")
        log("=== Fase 2: fichas ===")
        fichas_ok, fichas_err, deferred = run_fichas(
            session, state, out, territory_of, log, checkpoint)
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

    checked = [state["accounts"][a["account"]] for a in accounts
               if a["account"] in state["accounts"]]
    status = Counter(s["status"] for s in checked)
    log("")
    log("=== Resumen de la pasada ===")
    log(f"requests usados: {session.done}/{args.budget}")
    log(f"cuentas recorridas: {len(checked)}/{len(accounts)} ({dict(status)})")
    log(f"discos vistos: {sum(s.get('albums', 0) for s in checked)}; temas sueltos "
        f"(no se proponen): {sum(s.get('tracks', 0) for s in checked)}")
    log(f"parciales nuevos descubiertos: {new_partials}")
    log(f"fichas completadas: {fichas_ok} (errores: {fichas_err}, "
        f"a cola oleada-2: {deferred})")
    log(f"candidatos acumulados: {len(out['candidates'])} "
        f"(+{len(out['deferred_oleada2'])} en cola oleada-2)")
    log(f"fichas pendientes para la próxima pasada: {len(state['pending_fichas'])}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
