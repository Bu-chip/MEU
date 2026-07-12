#!/usr/bin/env python3
"""Scraper de descubrimiento por tags de Bandcamp — MEU / expansión Euskal Herria.

PRINCIPIO INNEGOCIABLE: el robot propone, Miguel dispone. Este script
JAMÁS toca data/bandcamp_bilbaotags_clean.json — solo produce ficheros
de candidatos que entran al catálogo vía PR revisable.

Flujo (diseño aprobado en la Fase 2; contrato de la API verificado en
el sondeo GATE, ver docs/scraping-method.md):

  1. DESCUBRIR: para cada tag con final="incluir" en
     data/tag_candidates.json (lista cerrada 2026-07-12, 107 tags),
     pagina POST bandcamp.com/api/discover/1/discover_web con cursor
     (slice=new, 20 items/página).
  2. DEDUPE: contra el canónico (album_id + URL normalizada), contra
     data/rejected.json (discos rechazados en PRs anteriores) y contra
     lo ya descubierto en pasadas previas.
  3. FICHA: solo para candidatos nuevos, visita la página del álbum y
     extrae los tags (<a class="tag">), verifica cover_url/album_id
     (og:image, bc-page-properties) y el año.
  4. NORMALIZAR: tags vía TAG_RENAMES/TAG_SPLITS/INVISIBLE_CHARS
     importados de pipeline.py (misma normalización que el canónico).
  5. SALIDA: data/candidates_YYYY-MM.json con el esquema del canónico
     (sin `id`, que se asigna al aprobar el merge) + procedencia
     (source_tags, band_location, discovered_at). Los candidatos cuya
     única vía de entrada son basquemusic/euskalmusika y cuya location
     es de Iparralde van a la cola `deferred_oleada2` del mismo fichero
     (decisión 2026-07-12: alcance CAV+Navarra en esta oleada).

Operativa:
  - Presupuesto DURO de requests por pasada (--budget, por defecto 900)
    a 1 req/2s. Lo que no quepa queda en data/discovery_state.json
    (checkpoints atómicos) y la siguiente pasada continúa.
  - Incremental: un tag ya agotado en pasadas anteriores se re-pagina
    desde el principio (slice=new ordena por fecha) y se corta en la
    primera página sin novedades.
  - Si discover_web deja de responder con el contrato verificado (o el
    Client Challenge se extiende a la API/fichas), la pasada se detiene,
    guarda estado y sale con código 2: PAUSA Y REPORTA, sin reintentos
    ciegos. El canario scripts/probe_tag_pages.py da el diagnóstico.
  - Idempotente: una pasada sin novedades no cambia los candidatos.

Uso:
    python3 scripts/discover_tags.py --budget 60 --tags santurtzi,leioa
    python3 scripts/discover_tags.py                  # pasada completa
    python3 scripts/discover_tags.py --table data/candidates_2026-07.json
"""

import argparse
import html as html_mod
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
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = REPO_ROOT / "data" / "bandcamp_bilbaotags_clean.json"
TAGS_FILE = REPO_ROOT / "data" / "tag_candidates.json"
REJECTED_FILE = REPO_ROOT / "data" / "rejected.json"
STATE_FILE = REPO_ROOT / "data" / "discovery_state.json"

# Normalización de tags compartida con el canónico.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline import INVISIBLE_CHARS, TAG_RENAMES, TAG_SPLITS  # noqa: E402

DISCOVER_API = "https://bandcamp.com/api/discover/1/discover_web"
PAGE_SIZE = 20

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
}

REQUEST_TIMEOUT = 30

# Cola oleada-2: solo se aplica a candidatos cuya ÚNICA vía de entrada
# son estos tags (decisión 2026-07-12). El resto lo filtra Miguel en el
# PR con la columna band_location.
IPARRALDE_ONLY_TAGS = {"basquemusic", "euskalmusika"}
IPARRALDE_LOCATION_TERMS = [
    "france", "iparralde", "pays basque", "baiona", "bayonne", "biarritz",
    "anglet", "angelu", "hendaye", "hendaia", "irouléguy", "irouleguy",
    "donibane", "ustaritz", "uztaritze", "itxassou", "itsasu", "mauléon",
    "mauleon", "azkaine", "ascain", "senpere", "ciboure", "ziburu",
]

TAG_LINK_RE = re.compile(r'<a[^>]*class="tag"[^>]*>\s*([^<]+?)\s*</a>')


class ContractError(Exception):
    """discover_web (o una ficha) no responde con el contrato verificado."""


class BudgetExhausted(Exception):
    pass


# ------------------------------------------------------------------
# Red
# ------------------------------------------------------------------

class Session:
    """Requests con presupuesto duro, rate limit y contadores."""

    def __init__(self, budget, delay_min, delay_max):
        self.budget = budget
        self.delay_min = delay_min
        self.delay_max = delay_max
        self.done = 0

    def left(self):
        return self.budget - self.done

    def fetch(self, url, post_json=None, extra_headers=None):
        if self.done >= self.budget:
            raise BudgetExhausted()
        if self.done:
            time.sleep(random.uniform(self.delay_min, self.delay_max))
        self.done += 1

        headers = dict(HEADERS)
        if extra_headers:
            headers.update(extra_headers)
        data = None
        if post_json is not None:
            data = json.dumps(post_json).encode("utf-8")
            headers["Content-Type"] = "application/json"

        req = urllib.request.Request(url, data=data, headers=headers)
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            return resp.read().decode("utf-8", errors="replace")


def classify_error(exc):
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


# ------------------------------------------------------------------
# Utilidades de datos
# ------------------------------------------------------------------

def normalize_url(url):
    """Clave de dedupe: sin query/fragmento, host en minúsculas, sin / final."""
    if not url:
        return None
    u = urlparse(url.split("?", 1)[0].split("#", 1)[0])
    return f"{u.netloc.lower()}{u.path.rstrip('/')}"


def normalize_tags(tags):
    """La misma normalización que aplica el pipeline al canónico."""
    out = []
    for tag in tags:
        tag = tag.translate(INVISIBLE_CHARS).strip().lower()
        if not tag:
            continue
        parts = TAG_SPLITS[tag] if tag in TAG_SPLITS else [TAG_RENAMES.get(tag, tag)]
        for part in parts:
            if part and part not in out:
                out.append(part)
    return out


def parse_year(release_date):
    """'2026-07-09 20:32:40 UTC' -> 2026; None si no parsea."""
    m = re.match(r"(\d{4})-", release_date or "")
    return int(m.group(1)) if m else None


def meta_content(page, attr, value):
    """content del primer <meta {attr}="{value}"> (mismo parser que scrape_covers)."""
    tag_re = re.compile(
        r"<meta\b[^>]*\b{}=[\"']{}[\"'][^>]*>".format(re.escape(attr), re.escape(value)),
        re.IGNORECASE,
    )
    m = tag_re.search(page)
    if not m:
        return None
    content = re.search(r"\bcontent=[\"']([^\"']*)[\"']", m.group(0))
    return html_mod.unescape(content.group(1)) if content else None


def atomic_save(path, payload):
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, path)


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ------------------------------------------------------------------
# Carga de entradas
# ------------------------------------------------------------------

def load_tag_list():
    """Tags aprobados (final=incluir), pequeños primero para completar más
    tags por pasada; los grandes consumen el resto y se reanudan."""
    data = json.loads(TAGS_FILE.read_text(encoding="utf-8"))
    rows = [r for r in data["tags"] if r.get("final") == "incluir"]
    rows.sort(key=lambda r: (r.get("result_count") or 0, r["tag"]))
    return [r["tag"] for r in rows]


def load_canonical_keys():
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    urls = {normalize_url(a["url"]) for a in data["albums"] if a["url"]}
    ids = {a["album_id"] for a in data["albums"] if a["album_id"] is not None}
    return urls, ids


def load_rejected():
    """data/rejected.json: {"meta": {...}, "rejected": {url_normalizada: {...}}}.

    La convención completa está documentada en el meta del propio
    fichero. Puede no existir en checkouts antiguos.
    """
    if not REJECTED_FILE.exists():
        return set()
    data = json.loads(REJECTED_FILE.read_text(encoding="utf-8"))
    return set(data.get("rejected", {}).keys())


def load_json_or(path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"AVISO: no se pudo leer {path} ({exc}); se ignora", file=sys.stderr)
        return default


# ------------------------------------------------------------------
# Fase 1: descubrimiento vía discover_web
# ------------------------------------------------------------------

def discover_page(session, tag, cursor):
    """Una página del Discover. Devuelve (items, next_cursor).

    Lanza ContractError si la respuesta no cumple el contrato verificado
    en el sondeo: eso significa que la API cambió o el Client Challenge
    se extendió, y la pasada debe PARAR Y REPORTAR, no insistir.
    """
    body = {"tag_norm_names": [tag], "include_result_types": ["a", "s"],
            "category_id": 0, "geoname_id": 0, "slice": "new",
            "cursor": cursor or "*", "size": PAGE_SIZE}
    try:
        raw = session.fetch(DISCOVER_API, post_json=body, extra_headers={
            "Referer": f"https://bandcamp.com/discover/{tag}",
            "Origin": "https://bandcamp.com",
            "X-Requested-With": "XMLHttpRequest",
        })
    except BudgetExhausted:
        raise
    except Exception as exc:
        raise ContractError(f"{tag}: {classify_error(exc)} ({exc})") from exc
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        raise ContractError(f"{tag}: respuesta no-JSON ({raw[:120]!r})")
    results = payload.get("results")
    if not isinstance(results, list):
        raise ContractError(f"{tag}: sin 'results' ({raw[:200]!r})")
    return results, payload.get("cursor")


def item_to_partial(item, tag):
    """Item del listado -> candidato parcial (a falta de la ficha)."""
    url = (item.get("item_url") or "").split("?", 1)[0]
    if not url:
        return None
    image_id = (item.get("primary_image") or {}).get("image_id")
    return {
        "artist": item.get("album_artist") or item.get("band_name"),
        "title": item.get("title"),
        "genre": None,
        "year": parse_year(item.get("release_date")),
        "tags": [],
        "url": url,
        "cover_url": f"https://f4.bcbits.com/img/a{image_id}_5.jpg" if image_id else None,
        "album_id": item.get("item_id"),
        "band_location": (item.get("band_location") or "").strip() or None,
        "source_tags": [tag],
        "discovered_at": now_iso(),
    }


def run_discovery(session, tags, state, known, log):
    """Pagina cada tag acumulando parciales en state['pending_fichas'].

    `known` es el conjunto de claves (norm_url y album_id) ya resueltas:
    canónico + rechazados + candidatos previos + pendientes. Devuelve el
    número de parciales nuevos.
    """
    new_partials = 0
    for tag in tags:
        tstate = state["tags"].setdefault(
            tag, {"cursor": None, "exhausted": False, "pages_done": 0})
        # Re-visita incremental de un tag agotado: desde el principio,
        # cortando en la primera página sin novedades.
        incremental = tstate["exhausted"]
        cursor = None if incremental else tstate["cursor"]
        while True:
            if session.left() < 1:
                raise BudgetExhausted()
            results, next_cursor = discover_page(session, tag, cursor)
            tstate["pages_done"] += 1
            page_new = 0
            for item in results:
                partial = item_to_partial(item, tag)
                if partial is None:
                    continue
                nurl = normalize_url(partial["url"])
                aid = partial["album_id"]
                pend = state["pending_fichas"].get(nurl)
                if pend is not None:
                    if tag not in pend["source_tags"]:
                        pend["source_tags"].append(tag)
                    continue
                if nurl in known or (aid is not None and aid in known):
                    continue
                state["pending_fichas"][nurl] = partial
                known.add(nurl)
                if aid is not None:
                    known.add(aid)
                page_new += 1
                new_partials += 1
            log(f"  {tag}: página {tstate['pages_done']} → {page_new} nuevos "
                f"({len(results)} items)")
            if incremental and page_new == 0:
                break  # al día: el resto ya se conocía
            if not results or not next_cursor or next_cursor == cursor:
                tstate["exhausted"] = True
                tstate["cursor"] = None
                break
            cursor = next_cursor
            tstate["cursor"] = cursor
        tstate["last_run"] = now_iso()
    return new_partials


# ------------------------------------------------------------------
# Fase 2: fichas de los candidatos nuevos
# ------------------------------------------------------------------

def scrape_ficha(session, partial):
    """Completa un parcial con la ficha real. Devuelve (candidato, None)
    o (None, error). Lanza ContractError ante el Client Challenge."""
    url = partial["url"]
    try:
        page = session.fetch(url)
    except BudgetExhausted:
        raise
    except Exception as exc:
        return None, classify_error(exc)
    if "<title>Client Challenge</title>" in page:
        raise ContractError(f"Client Challenge en ficha: {url}")

    tags = normalize_tags(html_mod.unescape(t) for t in TAG_LINK_RE.findall(page))
    if not tags:
        return None, "sin_tags"

    candidate = dict(partial)
    candidate["tags"] = tags

    og_image = meta_content(page, "property", "og:image")
    if og_image:
        candidate["cover_url"] = og_image
    props_raw = meta_content(page, "name", "bc-page-properties")
    if props_raw:
        try:
            item_id = json.loads(props_raw).get("item_id")
            if item_id is not None:
                candidate["album_id"] = item_id
        except (json.JSONDecodeError, AttributeError):
            pass
    if candidate["year"] is None:
        m = re.search(r"released [A-Z][a-z]+ \d{1,2}, (\d{4})", page)
        if m:
            candidate["year"] = int(m.group(1))
    return candidate, None


def is_iparralde_deferred(candidate):
    """Decisión 2026-07-12: solo si TODA la procedencia es basquemusic/
    euskalmusika y la location es claramente de Iparralde."""
    if not set(candidate["source_tags"]) <= IPARRALDE_ONLY_TAGS:
        return False
    loc = (candidate["band_location"] or "").lower()
    return any(t in loc for t in IPARRALDE_LOCATION_TERMS)


def run_fichas(session, state, out, log, checkpoint):
    """Consume state['pending_fichas'] completando candidatos."""
    done = errors = deferred = 0
    challenge_streak = 0
    # Orden determinista para reanudaciones reproducibles.
    for nurl in sorted(state["pending_fichas"]):
        if session.left() < 1:
            raise BudgetExhausted()
        partial = state["pending_fichas"][nurl]
        try:
            candidate, err = scrape_ficha(session, partial)
        except ContractError:
            challenge_streak += 1
            if challenge_streak >= 3:
                raise
            state["fichas_error"][nurl] = "client_challenge"
            errors += 1
            continue
        challenge_streak = 0
        if candidate is None:
            state["fichas_error"][nurl] = err
            log(f"  ✗ {partial['url']}: {err}")
            errors += 1
        else:
            del state["pending_fichas"][nurl]
            state["fichas_error"].pop(nurl, None)
            if is_iparralde_deferred(candidate):
                out["deferred_oleada2"].append(candidate)
                deferred += 1
            else:
                out["candidates"].append(candidate)
            done += 1
        if (done + errors) % 25 == 0:
            checkpoint()
    return done, errors, deferred


# ------------------------------------------------------------------
# Tabla legible para el cuerpo del PR de candidatos
# ------------------------------------------------------------------

def render_table(candidates_path):
    """Markdown agrupado por tag de origen (el primero que lo descubrió)."""
    data = json.loads(Path(candidates_path).read_text(encoding="utf-8"))
    lines = []
    for section, title in (("candidates", "Candidatos"),
                           ("deferred_oleada2", "Cola oleada-2 (Iparralde)")):
        rows = data.get(section, [])
        lines.append(f"## {title} ({len(rows)})")
        lines.append("")
        if not rows:
            lines.append("_(vacío)_")
            lines.append("")
            continue
        by_tag = {}
        for c in rows:
            by_tag.setdefault(c["source_tags"][0], []).append(c)
        for tag in sorted(by_tag):
            group = sorted(by_tag[tag], key=lambda c: ((c["artist"] or "").lower(),
                                                       (c["title"] or "").lower()))
            lines.append(f"### {tag} ({len(group)})")
            lines.append("")
            lines.append("| Artista | Título | Año | Tags | Location | Otros tags de origen |")
            lines.append("|---|---|---|---|---|---|")
            for c in group:
                extra = ", ".join(c["source_tags"][1:]) or "—"
                tags = ", ".join(c["tags"][:6]) + ("…" if len(c["tags"]) > 6 else "")
                lines.append(
                    f"| {c['artist'] or '?'} | [{c['title'] or '?'}]({c['url']}) "
                    f"| {c['year'] or '?'} | {tags} | {c['band_location'] or '?'} "
                    f"| {extra} |")
            lines.append("")
    return "\n".join(lines)


# ------------------------------------------------------------------
# Pasada completa
# ------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--budget", type=int, default=900,
                        help="presupuesto duro de requests de la pasada")
    parser.add_argument("--tags", default="",
                        help="override: solo estos tags (separados por comas)")
    parser.add_argument("--month", default=None,
                        help="sufijo YYYY-MM del fichero de candidatos "
                             "(por defecto, el mes actual UTC)")
    parser.add_argument("--delay-min", type=float, default=2.0)
    parser.add_argument("--delay-max", type=float, default=2.3)
    parser.add_argument("--table", metavar="CANDIDATES_JSON",
                        help="no scrapea: imprime la tabla markdown del fichero dado")
    args = parser.parse_args()

    if args.table:
        print(render_table(args.table))
        return 0

    month = args.month or datetime.now(timezone.utc).strftime("%Y-%m")
    out_file = REPO_ROOT / "data" / f"candidates_{month}.json"

    tags = ([t.strip() for t in args.tags.split(",") if t.strip()]
            if args.tags else load_tag_list())
    canon_urls, canon_ids = load_canonical_keys()
    rejected = load_rejected()

    state = load_json_or(STATE_FILE, {})
    state.setdefault("tags", {})
    state.setdefault("pending_fichas", {})
    state.setdefault("fichas_error", {})

    out = load_json_or(out_file, {})
    out.setdefault("meta", {})
    out.setdefault("candidates", [])
    out.setdefault("deferred_oleada2", [])

    # Conjunto de claves conocidas para el dedupe (urls normalizadas y
    # album_ids comparten set: no colisionan, unos son str y otros int).
    known = set(canon_urls) | set(canon_ids) | rejected
    for c in out["candidates"] + out["deferred_oleada2"]:
        known.add(normalize_url(c["url"]))
        if c["album_id"] is not None:
            known.add(c["album_id"])
    for nurl in state["pending_fichas"]:
        known.add(nurl)
    for nurl, partial in state["pending_fichas"].items():
        if partial.get("album_id") is not None:
            known.add(partial["album_id"])

    session = Session(args.budget, args.delay_min, args.delay_max)
    log = lambda msg: print(msg, flush=True)  # noqa: E731

    def content_sig():
        out["candidates"].sort(key=lambda c: normalize_url(c["url"]))
        out["deferred_oleada2"].sort(key=lambda c: normalize_url(c["url"]))
        return json.dumps([out["candidates"], out["deferred_oleada2"]],
                          ensure_ascii=False, sort_keys=True)

    baseline_sig = content_sig()

    def checkpoint():
        # El estado operativo (cursors, last_run) se guarda siempre; el
        # fichero de candidatos solo se reescribe si su contenido cambió,
        # así una pasada sin novedades lo deja byte a byte idéntico y el
        # futuro workflow puede decidir "sin diff → sin PR".
        atomic_save(STATE_FILE, state)
        if content_sig() != baseline_sig or not out_file.exists():
            out["meta"].update({
                "generated_at": now_iso(),
                "month": month,
                "schema": "candidato = canónico sin id + band_location, "
                          "source_tags, discovered_at; los id se asignan al merge",
            })
            atomic_save(out_file, out)

    log(f"Descubrimiento — {len(tags)} tags, presupuesto {args.budget} requests, "
        f"{args.delay_min}-{args.delay_max}s entre requests")
    log(f"Dedupe contra: {len(canon_urls)} URLs canónicas, {len(canon_ids)} "
        f"album_ids, {len(rejected)} rechazados, "
        f"{len(out['candidates'])} candidatos previos, "
        f"{len(state['pending_fichas'])} fichas pendientes")
    log("")

    exit_code = 0
    new_partials = fichas_ok = fichas_err = deferred = 0
    try:
        log("=== Fase 1: descubrimiento ===")
        new_partials = run_discovery(session, tags, state, known, log)
        checkpoint()
        log(f"  nuevos parciales: {new_partials} "
            f"(pendientes de ficha: {len(state['pending_fichas'])})")
        log("")
        log("=== Fase 2: fichas ===")
        fichas_ok, fichas_err, deferred = run_fichas(session, state, out, log, checkpoint)
    except BudgetExhausted:
        log(f"\npresupuesto de {args.budget} requests agotado; "
            "la próxima pasada continúa desde el checkpoint")
    except ContractError as exc:
        # PAUSA Y REPORTA: la API o las fichas ya no se comportan como
        # lo verificado. Ejecutar el canario probe_tag_pages.py.
        log(f"\nERROR DE CONTRATO: {exc}")
        log("La pasada se detiene sin reintentos. Ejecuta el canario "
            "(workflow probe-tag-pages) y revisa docs/scraping-method.md.")
        exit_code = 2
    finally:
        checkpoint()

    pending = len(state["pending_fichas"])
    tags_done = sum(1 for t in tags if state["tags"].get(t, {}).get("exhausted"))
    log("")
    log("=== Resumen de la pasada ===")
    log(f"requests usados: {session.done}/{args.budget}")
    log(f"tags al día: {tags_done}/{len(tags)}")
    log(f"parciales nuevos descubiertos: {new_partials}")
    log(f"fichas completadas: {fichas_ok} (errores: {fichas_err}, "
        f"a cola oleada-2: {deferred})")
    log(f"candidatos acumulados: {len(out['candidates'])} "
        f"(+{len(out['deferred_oleada2'])} en cola oleada-2)")
    log(f"fichas pendientes para la próxima pasada: {pending}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
