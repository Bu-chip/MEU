#!/usr/bin/env python3
"""Pipeline de localización del MEU (sección MAPA).

El canónico (data/bandcamp_bilbaotags_clean.json) NO se toca: toda la
geografía vive en data/locations/, separada en evidencia → normalización
→ resolución → índice del mapa. Ver docs/mapa.md.

Subcomandos (todos idempotentes):

  ingest FICHERO...   observaciones desde ficheros de candidatos
                      (lo llama discover_tags.py y el workflow mensual)
  check               guardia: ningún band_location de candidatos se pierde
  recover             reconstruye observaciones desde TODO el histórico
                      (working tree + ramas/commits locales de git)
  scrape              completa cuentas sin evidencia visitando UNA ficha por
                      cuenta (red; presupuesto y ritmo del scraper)
  gazetteer           descarga el nomenclátor de Wikidata (red) a caché
  places              (re)genera el registro de lugares desde el nomenclátor
  normalize           clasifica cada texto crudo → normalized.json + revisión
  resolve             resolución por release → resolutions.json
  audit               auditoría del dataset → docs/mapa-data-audit.md
  query               consultas municipio × tag (--place / --tag)
  build               índice compacto del mapa para la app
  all                 normalize + resolve + audit + build (sin red)

Uso típico tras un merge de candidatos:
    python3 scripts/locations.py ingest data/candidates_2026-09.json
    python3 scripts/locations.py all
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
import locations_lib as L  # noqa: E402

DATA_FILE = REPO_ROOT / "data" / "bandcamp_bilbaotags_clean.json"
LOC_DIR = REPO_ROOT / "data" / "locations"
OBS_DIR = LOC_DIR / "observations"
REPORTS_DIR = LOC_DIR / "reports"
CACHE_DIR = LOC_DIR / "cache"
PLACES_FILE = LOC_DIR / "places.json"
RULES_FILE = LOC_DIR / "rules.json"
MANUAL_FILE = LOC_DIR / "manual.json"
NORMALIZED_FILE = LOC_DIR / "normalized.json"
RESOLUTIONS_FILE = LOC_DIR / "resolutions.json"
GAZETTEER_FILE = CACHE_DIR / "gazetteer_wikidata.json"
PAGES_CACHE = CACHE_DIR / "bandcamp_pages.json"
LABELS_FILE = REPO_ROOT / "data" / "derived" / "labels.json"
MAP_INDEX_FILE = LOC_DIR / "map_index.json"
AUDIT_DOC = REPO_ROOT / "docs" / "mapa-data-audit.md"


# ------------------------------------------------------------------
# E/S
# ------------------------------------------------------------------

def rel(path):
    try:
        return str(Path(path).resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def load_json(path, default=None):
    path = Path(path)
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_text(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def write_json(path, payload):
    write_text(path, json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_obs_file(path, meta, observations):
    """Fichero de observaciones: meta + una release por línea."""
    body = L.dumps_lines(observations).rstrip("\n")
    body = "\n".join("  " + line if i else line for i, line in enumerate(body.split("\n")))
    text = ("{\n"
            f'  "meta": {json.dumps(meta, ensure_ascii=False, sort_keys=True)},\n'
            f'  "observations": {body}\n'
            "}\n")
    write_text(path, text)


def load_obs_file(path):
    doc = load_json(path, {"meta": {}, "observations": {}})
    return doc.get("meta", {}), doc.get("observations", {})


def load_all_observations():
    groups = []
    for f in sorted(OBS_DIR.glob("*.json")):
        groups.append(load_obs_file(f)[1])
    return L.merge_observations(*groups)


def load_catalog():
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def today():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def obs_file_for(candidates_path):
    """data/candidates_2026-09.json → observations/candidates_2026-09.json."""
    return OBS_DIR / Path(candidates_path).name


def ingest_doc(doc, source_name, provenance):
    """Añade (unión, nunca borra) las observaciones de un doc de candidatos
    a su fichero observations/<source_name>. Devuelve (nuevas, total)."""
    target = OBS_DIR / source_name
    meta, existing = load_obs_file(target)
    fresh = L.observations_from_candidates(doc, provenance)
    merged = L.merge_observations(existing, fresh)
    before = sum(len(v) for v in existing.values())
    after = sum(len(v) for v in merged.values())
    meta = {
        "source": source_name,
        "source_type": L.OBS_SOURCE_DISCOVER,
        "subject": L.OBS_SUBJECT,
        "sources_read": sorted(set(meta.get("sources_read", [])) | {provenance}),
        "note": "band_location de discover_web, tal cual (sin normalizar). "
                "value=null: Bandcamp no daba ubicación. Ubicación de la cuenta "
                "que publica (grupo o sello), actual y sin fecha.",
    }
    write_obs_file(target, meta, merged)
    return after - before, after


# ------------------------------------------------------------------
# Fase 1 — ingest / check
# ------------------------------------------------------------------

def cmd_ingest(args):
    for f in args.files:
        doc = load_json(f)
        if doc is None:
            print(f"no existe: {f}", file=sys.stderr)
            return 1
        new, total = ingest_doc(doc, Path(f).name, rel(f))
        print(f"{rel(f)} → {rel(obs_file_for(f))}: +{new} observaciones ({total} en total)")
    return 0


def candidate_docs_in_tree():
    return [(rel(p), load_json(p)) for p in sorted((REPO_ROOT / "data").glob("candidates_*.json"))]


def cmd_check(args):
    """Falla si algún band_location de un fichero de candidatos del árbol,
    o de una release del canónico, no está en las observaciones."""
    obs = load_all_observations()
    docs = candidate_docs_in_tree()
    missing = L.missing_candidate_observations(docs, obs)
    catalog = load_catalog()
    by_url, _ = L.index_observations(obs)
    in_catalog = 0
    for a in catalog["albums"]:
        if L.observations_for_release(a, obs, by_url):
            in_catalog += 1
    if missing:
        print(f"ERROR: {len(missing)} ubicaciones de candidatos sin observación:")
        for name, url, value in missing[:20]:
            print(f"  {name}: {url} → {value!r}")
        print("Ejecuta: python3 scripts/locations.py ingest data/candidates_*.json")
        return 1
    print(f"ok: {len(docs)} ficheros de candidatos cubiertos; "
          f"{in_catalog}/{len(catalog['albums'])} releases del canónico con observación")
    return 0


# ------------------------------------------------------------------
# Fase 2 — recover
# ------------------------------------------------------------------

def git(*args):
    return subprocess.run(["git", "-C", str(REPO_ROOT), *args], check=True,
                          capture_output=True, text=True).stdout


def historical_blobs():
    """Todas las versiones de candidates_*.json y discovery_state.json en
    cualquier commit alcanzable de cualquier ref local (ramas locales y
    remote-tracking). Solo lectura de objetos git; no toca el remoto.

    → [(path, commit, blob_sha)] sin repetir blob.
    """
    out = []
    seen = set()
    log = git("log", "--all", "--format=%H", "--",
              "data/candidates_*.json", "data/discovery_state.json")
    for commit in log.split():
        tree = git("ls-tree", "-r", commit, "--", "data/")
        for line in tree.splitlines():
            meta, path = line.split("\t", 1)
            blob = meta.split()[2]
            name = Path(path).name
            if not (name.startswith("candidates_") and name.endswith(".json")) \
                    and name != "discovery_state.json":
                continue
            if blob in seen:
                continue
            seen.add(blob)
            out.append((path, commit, blob))
    return out


def cmd_recover(args):
    """Reconstruye observaciones desde el working tree y desde todo el
    histórico git local. Unión sin pérdidas; conflictos registrados."""
    sources = []  # (source_name, provenance, doc, kind)
    for p in sorted((REPO_ROOT / "data").glob("candidates_*.json")):
        sources.append((p.name, rel(p), load_json(p), "candidates"))
    blobs = [] if args.no_git else historical_blobs()
    for path, commit, blob in blobs:
        doc = json.loads(git("cat-file", "-p", blob))
        name = Path(path).name
        prov = f"git:{commit[:10]}:{path}"
        kind = "state" if name == "discovery_state.json" else "candidates"
        sources.append((name, prov, doc, kind))

    per_file = defaultdict(list)
    source_rows = []
    for name, prov, doc, kind in sources:
        if kind == "state":
            obs = L.observations_from_pending(doc, prov)
            target = "discovery_state_pending.json"
        else:
            obs = L.observations_from_candidates(doc, prov)
            target = name
        per_file[target].append(obs)
        source_rows.append((prov, target, sum(len(v) for v in obs.values()),
                            sum(1 for v in obs.values() for o in v if o["value"] is not None)))

    written = {}
    sources_by_target = defaultdict(list)
    for prov, target, _, _ in source_rows:
        sources_by_target[target].append(prov)
    candidate_targets = sorted(t for t in per_file if not t.startswith("discovery_state"))
    for target in candidate_targets + ["discovery_state_pending.json"]:
        groups = per_file.get(target)
        if not groups:
            continue
        _, existing = load_obs_file(OBS_DIR / target)
        merged = L.merge_observations(existing, *groups)
        if target.startswith("discovery_state"):
            # Solo lo que no llegó a ningún fichero de candidatos.
            merged = L.drop_known(merged, L.merge_observations(*written.values()))
            note = "parciales pendientes de ficha en discovery_state.json que nunca llegaron a candidatos"
        else:
            note = "band_location de discover_web, tal cual (sin normalizar)"
        meta = {
            "source": target,
            "source_type": L.OBS_SOURCE_DISCOVER,
            "subject": L.OBS_SUBJECT,
            "sources_read": sorted(set(sources_by_target[target])),
            "note": note + ". value=null: Bandcamp no daba ubicación. Ubicación de la cuenta "
                    "que publica (grupo o sello), actual y sin fecha.",
        }
        write_obs_file(OBS_DIR / target, meta, merged)
        written[target] = merged

    stats = recovery_stats(load_all_observations())
    stats["sources"] = [{"provenance": p, "target": t, "observations": n, "with_value": nv}
                        for p, t, n, nv in source_rows]
    stats["files"] = {t: sum(len(v) for v in m.values()) for t, m in written.items()}
    write_json(REPORTS_DIR / "recover.json", stats)
    write_text(REPORTS_DIR / "recover.md", render_recover(stats))
    print(render_recover(stats))
    return 0


def recovery_stats(obs):
    catalog = load_catalog()
    albums = catalog["albums"]
    by_url, _ = L.index_observations(obs)
    with_direct = 0
    with_any = 0
    artists = set()
    contradictory = []
    values = Counter()
    for a in albums:
        lst = L.observations_for_release(a, obs, by_url)
        vals = {o["value"] for o in lst if o["value"] is not None}
        if lst:
            with_any += 1
        if vals:
            with_direct += 1
            artists.add(L.fold(a["artist"]))
            for v in vals:
                values[v] += 1
        if len(vals) > 1:
            contradictory.append({"id": a["id"], "url": a["url"], "values": sorted(vals)})
    # Contradicciones dentro de una misma cuenta (varios valores distintos).
    by_account = defaultdict(set)
    for lst in obs.values():
        for o in lst:
            if o["value"] is not None and o.get("account"):
                by_account[o["account"]].add(o["value"])
    account_conflicts = {k: sorted(v) for k, v in by_account.items() if len(v) > 1}
    all_values = Counter(o["value"] for lst in obs.values() for o in lst if o["value"] is not None)
    return {
        "total_releases": len(albums),
        "releases_with_observation": with_any,
        "releases_with_direct_location": with_direct,
        "releases_checked_without_location": with_any - with_direct,
        "releases_without_information": len(albums) - with_any,
        "artists_with_location": len(artists),
        "artists_total": len({L.fold(a["artist"]) for a in albums}),
        "unique_values_in_catalog": len(values),
        "unique_values_all_observations": len(all_values),
        "observation_keys_total": len(obs),
        "contradictory_releases": contradictory,
        "accounts_with_multiple_values": account_conflicts,
        "top_values_in_catalog": values.most_common(40),
    }


def render_recover(s):
    lines = [
        "# Recuperación de ubicaciones (fase 2)",
        "",
        "*Generado por `python3 scripts/locations.py recover`. No editar a mano.*",
        "",
        "Fuentes: ficheros `data/candidates_*.json` del árbol y todas sus versiones "
        "en el histórico git local (ramas locales y remote-tracking, incluidas "
        "`candidates/2026-08`, `candidates/2026-09` y `discovery-state`). Los "
        "valores se guardan **sin normalizar**.",
        "",
        "| Métrica | Valor |",
        "|---|---:|",
        f"| Releases del canónico | {s['total_releases']} |",
        f"| Con ubicación directa (Bandcamp, esta release) | {s['releases_with_direct_location']} |",
        f"| Consultadas sin ubicación (valor vacío) | {s['releases_checked_without_location']} |",
        f"| Sin ninguna información | {s['releases_without_information']} |",
        f"| Artistas (clave fold) con alguna ubicación | {s['artists_with_location']} / {s['artists_total']} |",
        f"| Valores únicos (releases del canónico) | {s['unique_values_in_catalog']} |",
        f"| Valores únicos (todas las observaciones) | {s['unique_values_all_observations']} |",
        f"| Releases con valores contradictorios | {len(s['contradictory_releases'])} |",
        f"| Cuentas con más de un valor | {len(s['accounts_with_multiple_values'])} |",
        f"| Claves de release con observación (incl. candidatos pendientes) | {s['observation_keys_total']} |",
        "",
        "## Fuentes leídas",
        "",
        "| Procedencia | Fichero de observaciones | Obs. | Con valor |",
        "|---|---|---:|---:|",
    ]
    for r in s.get("sources", []):
        lines.append(f"| `{r['provenance']}` | `{r['target']}` | {r['observations']} | {r['with_value']} |")
    lines += ["", "## Releases con valores contradictorios", ""]
    if s["contradictory_releases"]:
        lines += [f"- id {c['id']}: {' / '.join(c['values'])} — {c['url']}" for c in s["contradictory_releases"]]
    else:
        lines.append("Ninguna.")
    lines += ["", "## Cuentas con más de un valor", ""]
    if s["accounts_with_multiple_values"]:
        lines += [f"- `{k}`: {' / '.join(v)}" for k, v in sorted(s["accounts_with_multiple_values"].items())]
    else:
        lines.append("Ninguna.")
    lines += ["", "## Valores más frecuentes (releases del canónico)", "",
              "| Valor crudo | Releases |", "|---|---:|"]
    lines += [f"| {v} | {n} |" for v, n in s["top_values_in_catalog"]]
    return "\n".join(lines) + "\n"



# ------------------------------------------------------------------
# Fase 3 — scrape (red)
# ------------------------------------------------------------------

PAGE_HEADERS = {
    # Mismo UA de navegador que scrape_covers.py / discover_tags.py: los UA
    # por defecto de urllib reciben 403.
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
}


def parse_album_page(page):
    """→ dict con la ubicación de la cuenta y quién publica.

    - location: <span class="location secondaryText">…</span> (None si no
      aparece o está vacío).
    - item_id: bc-page-properties (para comprobar que la ficha es el disco).
    - by_artist_url / publisher_url: JSON-LD; si difieren, publica otra
      cuenta (típicamente un sello) y la ubicación es la de esa cuenta.
    """
    import html as html_mod
    import re
    out = {"location": None, "location_span": False, "item_id": None,
           "by_artist_url": None, "publisher_url": None}
    m = re.search(r'<span class="location secondaryText">(.*?)</span>', page, re.S)
    if m:
        out["location_span"] = True
        out["location"] = L.clean_value(html_mod.unescape(re.sub(r"<[^>]+>", "", m.group(1))))
    m = re.search(r'<meta\b[^>]*name=["\']bc-page-properties["\'][^>]*>', page)
    if m:
        c = re.search(r'content=["\']([^"\']*)["\']', m.group(0))
        if c:
            try:
                out["item_id"] = json.loads(html_mod.unescape(c.group(1))).get("item_id")
            except (ValueError, AttributeError):
                pass
    m = re.search(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', page, re.S)
    if m:
        try:
            ld = json.loads(m.group(1))
            out["by_artist_url"] = (ld.get("byArtist") or {}).get("@id")
            out["publisher_url"] = (ld.get("publisher") or {}).get("@id")
        except (ValueError, AttributeError):
            pass
    return out


def scrape_targets(catalog, obs):
    """Cuentas del canónico SIN ninguna observación (ni en sus releases ni
    en otra release de la misma cuenta) → [(cuenta, [releases por id])].

    Bandcamp localiza la cuenta, así que basta UNA ficha por cuenta; el
    resto de releases de esa cuenta se resuelven como same_account.
    """
    by_url, by_acc = L.index_observations(obs)
    pending = defaultdict(list)
    for a in catalog["albums"]:
        acc = L.account_of(a.get("url"))
        if not acc or by_acc.get(acc):
            continue
        if L.observations_for_release(a, obs, by_url):
            continue
        pending[acc].append(a)
    return sorted((acc, sorted(rows, key=lambda a: a["id"])) for acc, rows in pending.items())


def pages_to_observations(cache, catalog):
    """Observaciones derivadas de la caché de fichas (solo estados ok)."""
    by_nurl = {L.normalize_url(a["url"]): a for a in catalog["albums"]}
    out = defaultdict(list)
    for nurl, entry in sorted(cache.items()):
        if entry.get("status") != "ok":
            continue
        a = by_nurl.get(nurl)
        url = a["url"] if a else entry.get("url")
        if entry.get("kind") == "account_page":
            key = f"acct:{entry['account']}"
        else:
            key = L.release_key(a.get("album_id") if a else entry.get("item_id"), url)
        extra = {}
        if entry.get("publisher_url") and entry.get("by_artist_url") \
                and entry["publisher_url"].rstrip("/") != entry["by_artist_url"].rstrip("/"):
            extra["publisher_differs_from_artist"] = True
        out[key].append(L.observation(
            entry.get("location"), L.OBS_SOURCE_PAGE, url, entry.get("fetched_at"),
            "data/locations/cache/bandcamp_pages.json", **extra))
    return dict(out)


def write_page_observations(cache, catalog):
    meta = {
        "source": "bandcamp_pages.json",
        "source_type": L.OBS_SOURCE_PAGE,
        "subject": L.OBS_SUBJECT,
        "sources_read": ["data/locations/cache/bandcamp_pages.json"],
        "note": "<span class=\"location\"> de UNA ficha por cuenta sin evidencia previa "
                "(scripts/locations.py scrape). value=null: la ficha no muestra ubicación. "
                "Ubicación de la cuenta que publica, actual y sin fecha.",
    }
    write_obs_file(OBS_DIR / "bandcamp_pages.json", meta,
                   L.merge_observations(pages_to_observations(cache, catalog)))


def cmd_scrape(args):
    import random
    import time
    import urllib.error
    import urllib.request

    catalog = load_catalog()
    # Las observaciones de fichas ya visitadas cuentan como resueltas: no
    # se repite ninguna petición con estado ok en la caché.
    cache = load_json(PAGES_CACHE, {})
    obs = L.merge_observations(load_all_observations(), pages_to_observations(cache, catalog))
    targets = scrape_targets(catalog, obs)
    print(f"cuentas sin evidencia: {len(targets)} "
          f"({sum(len(r) for _, r in targets)} releases); presupuesto {args.budget}")
    if args.dry_run:
        for acc, rows in targets[:20]:
            print(f"  {acc}: {len(rows)} releases → {rows[0]['url']}")
        return 0

    done = 0
    last = 0.0

    def save():
        write_json(PAGES_CACHE, cache)
        write_page_observations(cache, catalog)

    try:
        for i, (acc, rows) in enumerate(targets):
            tries = [(a["url"], a) for a in rows[: args.tries_per_account]]
            if not acc.startswith("custom:"):
                # Respaldo: la portada de la cuenta también muestra la
                # ubicación si los discos se retiraron (404).
                tries.append((f"https://{acc}.bandcamp.com/", None))
            for url, a in tries:
                nurl = L.normalize_url(url)
                prev = cache.get(nurl)
                if prev and prev.get("status") == "ok":
                    break
                if prev and prev.get("status") == "gone" and not args.retry_gone:
                    continue
                if done >= args.budget:
                    raise StopIteration
                wait = random.uniform(args.delay_min, args.delay_max) - (time.time() - last)
                if wait > 0:
                    time.sleep(wait)
                last = time.time()
                done += 1
                entry = {"url": url, "account": acc, "fetched_at": today()}
                if a is None:
                    entry["kind"] = "account_page"
                try:
                    req = urllib.request.Request(url, headers=PAGE_HEADERS)
                    with urllib.request.urlopen(req, timeout=30) as resp:
                        page = resp.read().decode("utf-8", errors="replace")
                    parsed = parse_album_page(page)
                    if "Client Challenge" in page[:5000] and not parsed["location_span"]:
                        print("ERROR: Client Challenge de Bandcamp; pausa y reporta.")
                        cache[nurl] = {**entry, "status": "error", "error": "client_challenge"}
                        raise StopIteration
                    entry.update(parsed, status="ok")
                    if a and a.get("album_id") and parsed["item_id"] and parsed["item_id"] != a["album_id"]:
                        entry["note"] = "item_id de la ficha distinto del album_id del canónico"
                except urllib.error.HTTPError as exc:
                    entry.update(status="gone" if exc.code in (404, 410) else "error",
                                 error=f"http_{exc.code}")
                except (urllib.error.URLError, TimeoutError, OSError) as exc:
                    entry.update(status="error", error=type(exc).__name__)
                cache[nurl] = entry
                detail = repr(entry.get("location")) if entry["status"] == "ok" else entry.get("error")
                print(f"[{i + 1}/{len(targets)}] {acc}: {entry['status']} {detail}", flush=True)
                if entry["status"] == "ok":
                    break
            if done and done % 25 == 0:
                save()
    except StopIteration:
        pass
    finally:
        save()
    ok = sum(1 for e in cache.values() if e.get("status") == "ok")
    with_loc = sum(1 for e in cache.values() if e.get("status") == "ok" and e.get("location"))
    print(f"peticiones: {done}; caché: {len(cache)} fichas, {ok} ok, {with_loc} con ubicación")
    return 0


# ------------------------------------------------------------------
# Fase 4 — nomenclátor (Wikidata) y registro de lugares
# ------------------------------------------------------------------

WIKIDATA_SPARQL = "https://query.wikidata.org/sparql"
# Prefijo INE de provincia → territorio. Los códigos de 5 dígitos son
# municipios; los de 11, entidades singulares (núcleos) cuyo municipio es
# el prefijo de 5.
INE_TERRITORY = {"48": "Bizkaia", "20": "Gipuzkoa", "01": "Araba", "31": "Nafarroa"}
CAPB_QID = "Q28092866"  # Communauté d'agglomération du Pays Basque = Iparralde

SPARQL_SOUTH = """SELECT ?item ?code ?coord ?es ?eu ?end WHERE {
  ?item wdt:P772 ?code .
  FILTER(STRSTARTS(?code,"48") || STRSTARTS(?code,"20") || STRSTARTS(?code,"01") || STRSTARTS(?code,"31"))
  ?item wdt:P625 ?coord .
  OPTIONAL { ?item rdfs:label ?es FILTER(LANG(?es)="es") }
  OPTIONAL { ?item rdfs:label ?eu FILTER(LANG(?eu)="eu") }
  OPTIONAL { ?item wdt:P576 ?end }
}"""

SPARQL_NORTH = """SELECT ?item ?code ?coord ?fr ?eu ?end WHERE {
  ?item wdt:P463 wd:%s ; wdt:P374 ?code ; wdt:P625 ?coord .
  OPTIONAL { ?item rdfs:label ?fr FILTER(LANG(?fr)="fr") }
  OPTIONAL { ?item rdfs:label ?eu FILTER(LANG(?eu)="eu") }
  OPTIONAL { ?item wdt:P576 ?end }
}""" % CAPB_QID


def sparql(query):
    import urllib.parse
    import urllib.request
    url = WIKIDATA_SPARQL + "?" + urllib.parse.urlencode({"query": query})
    req = urllib.request.Request(url, headers={
        "Accept": "application/sparql-results+json",
        "User-Agent": "MEU-mapa/1.0 (https://mapa.queimadacircuitrecords.com)",
    })
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read())["results"]["bindings"]


def parse_point(wkt):
    import re
    m = re.match(r"Point\(([-\d.eE]+) ([-\d.eE]+)\)", wkt)
    return (round(float(m.group(2)), 5), round(float(m.group(1)), 5)) if m else None


def cmd_gazetteer(args):
    """Descarga el nomenclátor a data/locations/cache/gazetteer_wikidata.json.

    Una sola vez (o para refrescar): el resto del pipeline trabaja offline
    sobre esta caché versionada.
    """
    rows = {}
    for b in sparql(SPARQL_SOUTH):
        code = b["code"]["value"]
        if not code.isdigit() or len(code) not in (5, 11):
            continue
        qid = b["item"]["value"].rsplit("/", 1)[1]
        pt = parse_point(b["coord"]["value"])
        if not pt:
            continue
        key = (qid, code)
        r = rows.setdefault(key, {
            "qid": qid, "code": code, "country": "ES",
            "kind": "municipality" if len(code) == 5 else "locality",
            "municipality_code": code[:5],
            "territory": INE_TERRITORY[code[:2]],
            "names": {}, "coords": set(),
        })
        r["coords"].add(pt)
        if "end" in b:
            r["dissolved"] = True
        for lang in ("es", "eu"):
            if lang in b:
                r["names"][lang] = b[lang]["value"]
    for b in sparql(SPARQL_NORTH):
        code = b["code"]["value"]
        qid = b["item"]["value"].rsplit("/", 1)[1]
        pt = parse_point(b["coord"]["value"])
        if not pt:
            continue
        r = rows.setdefault((qid, code), {
            "qid": qid, "code": code, "country": "FR", "kind": "municipality",
            "municipality_code": code, "territory": "Iparralde",
            "names": {}, "coords": set(),
        })
        r["coords"].add(pt)
        if "end" in b:
            r["dissolved"] = True
        for lang in ("fr", "eu"):
            if lang in b:
                r["names"][lang] = b[lang]["value"]
    out = []
    for r in rows.values():
        if r.pop("dissolved", False) and r["kind"] == "municipality":
            # Municipio histórico que comparte código con el actual (Ezkio,
            # Itsaso → Ezkio-Itsaso): sus nombres son núcleos del vigente.
            r["kind"] = "former_municipality"
        lat, lon = sorted(r.pop("coords"))[0]  # determinista si hay varias
        r["lat"], r["lon"] = lat, lon
        out.append(r)
    out.sort(key=lambda r: (r["country"], r["code"], r["qid"]))
    meta = {
        "source": "Wikidata SPARQL (P772 INE / P374 INSEE + P463 CAPB, P625 coordenadas)",
        "retrieved_at": today(),
        "note": "Coordenada = punto representativo del municipio/núcleo en Wikidata (P625). "
                "Solo para dibujar: no es la ubicación de ningún artista.",
        "counts": dict(Counter(f"{r['territory']}:{r['kind']}" for r in out)),
    }
    write_text(GAZETTEER_FILE, json.dumps({"meta": meta, "places": out}, ensure_ascii=False,
                                          sort_keys=True, separators=(",", ":")) + "\n")
    print(json.dumps(meta, ensure_ascii=False, indent=1))
    return 0


def load_gazetteer():
    doc = load_json(GAZETTEER_FILE)
    if not doc:
        raise SystemExit("falta el nomenclátor: python3 scripts/locations.py gazetteer")
    return doc["places"]


def build_places(gazetteer, overrides):
    """Registro de lugares = municipios vigentes del nomenclátor + overrides.

    - id estable: slug del nombre canónico (eu si existe); si colisiona, se
      añade el territorio y, si aún colisiona, el código oficial.
    - aliases: etiquetas eu/es/fr y sus partes bilingües («A / B»), nombres
      de núcleos y de municipios históricos del mismo código, y overrides.
      Un nombre OFICIAL de municipio nunca se retira; un nombre de núcleo
      compartido por varios municipios se retira (ambiguo) y se informa.
    - lat/lon: punto representativo de Wikidata (solo para dibujar).
    """
    munis = [g for g in gazetteer if g["kind"] == "municipality"]
    minor = defaultdict(list)
    for g in gazetteer:
        if g["kind"] in ("locality", "former_municipality"):
            minor[g["municipality_code"]].append(g)
    places = []
    for m in munis:
        names = m["names"]
        name = names.get("eu") or names.get("es") or names.get("fr")
        if not name:
            continue
        official = set()
        for v in names.values():
            official.add(v)
            for part in v.replace(" / ", "/").split("/"):
                official.add(part.strip())
        # Nombres oficiales bilingües: «Donostia / San Sebastián»,
        # «Vitoria-Gasteiz», «Alsasua – Altsasu» = combinación de las
        # etiquetas eu y es/fr en cualquier orden (los separadores se
        # igualan al normalizar).
        eu, other = names.get("eu"), names.get("es") or names.get("fr")
        if eu and other and L.norm_text(eu) != L.norm_text(other):
            official |= {f"{eu} {other}", f"{other} {eu}"}
        minor_names = {v for g in minor.get(m["code"], []) for v in g["names"].values()}
        places.append({
            "id": L.slugify(name),
            "name": name,
            "names": dict(sorted(names.items())),
            "lat": m["lat"],
            "lon": m["lon"],
            "territory": m["territory"],
            "country": m["country"],
            "area": "Euskal Herria",
            "comarca": None,
            "wikidata": m["qid"],
            "code": m["code"],
            "coord_source": "wikidata:P625",
            "_official": official,
            "_minor": minor_names - official,
        })
    for attempt in ("territory", "code"):
        ids = Counter(p["id"] for p in places)
        for p in places:
            if ids[p["id"]] > 1:
                p["id"] = f"{p['id']}-{L.slugify(p[attempt])}"
    by_id = {p["id"]: p for p in places}
    for pid, ov in (overrides or {}).items():
        if pid not in by_id:
            raise SystemExit(f"override de lugar desconocido: {pid}")
        p = by_id[pid]
        p["_official"] |= set(ov.get("aliases", []))
        for k in ("name", "comarca"):
            if k in ov:
                p[k] = ov[k]
    official_owner = defaultdict(set)
    minor_owner = defaultdict(set)
    for p in places:
        for a in p["_official"]:
            official_owner[L.norm_text(a)].add(p["id"])
        for a in p["_minor"]:
            minor_owner[L.norm_text(a)].add(p["id"])
    removed = set()
    for p in places:
        keep = set(p["_official"])
        for a in p["_minor"]:
            n = L.norm_text(a)
            if n in official_owner or len(minor_owner[n]) > 1:
                removed.add(n)
                continue
            keep.add(a)
        p["aliases"] = sorted(a for a in keep if a != p["name"])
        del p["_official"], p["_minor"]
    places.sort(key=lambda p: p["id"])
    return places, sorted(removed)


def cmd_places(args):
    rules = load_json(RULES_FILE, {})
    places, ambiguous = build_places(load_gazetteer(), rules.get("place_overrides", {}))
    doc = {
        "meta": {
            "generated_by": "python3 scripts/locations.py places",
            "source": "data/locations/cache/gazetteer_wikidata.json + rules.json:place_overrides",
            "note": "Registro controlado de municipios de Euskal Herria. lat/lon = punto "
                    "representativo para dibujar (Wikidata P625), nunca la ubicación exacta "
                    "de un artista. comarca: reservado.",
            "ambiguous_aliases_removed": ambiguous,
        },
        "places": places,
    }
    write_text(PLACES_FILE, json.dumps(doc, ensure_ascii=False, indent=1, sort_keys=True) + "\n")
    print(f"{len(places)} lugares; {len(ambiguous)} alias ambiguos retirados")
    return 0


def load_places():
    doc = load_json(PLACES_FILE)
    if not doc:
        raise SystemExit("falta el registro: python3 scripts/locations.py places")
    return doc["places"]


def load_rules():
    return load_json(RULES_FILE, {})


def make_normalizer():
    return L.Normalizer(load_places(), load_rules())


def catalog_value_counts(catalog, obs):
    """valor crudo → nº de releases del canónico con esa observación directa."""
    by_url, _ = L.index_observations(obs)
    counts = Counter()
    for a in catalog["albums"]:
        for v in {o["value"] for o in L.observations_for_release(a, obs, by_url) if o["value"]}:
            counts[v] += 1
    return counts


def cmd_normalize(args):
    """Clasifica cada texto crudo observado → data/locations/normalized.json
    y data/locations/reports/review.md (todo lo que pide ojo humano)."""
    norm = make_normalizer()
    obs = load_all_observations()
    catalog = load_catalog()
    obs_counts = Counter(o["value"] for lst in obs.values() for o in lst if o["value"])
    cat_counts = catalog_value_counts(catalog, obs)
    accounts = defaultdict(set)
    for lst in obs.values():
        for o in lst:
            if o["value"] and o.get("account"):
                accounts[o["value"]].add(o["account"])
    table = {}
    for value in sorted(obs_counts, key=lambda v: (L.norm_text(v), v)):
        c = norm.classify(value)
        c["observations"] = obs_counts[value]
        c["catalog_releases"] = cat_counts.get(value, 0)
        c["accounts"] = len(accounts[value])
        table[value] = c
    write_text(NORMALIZED_FILE, L.dumps_lines(table))
    cats = Counter(c["category"] for c in table.values())
    rel_cats = Counter()
    for c in table.values():
        rel_cats[c["category"]] += c["catalog_releases"]
    write_text(REPORTS_DIR / "review.md", render_review(table, norm))
    print(f"{len(table)} valores: " + ", ".join(f"{k} {v}" for k, v in cats.most_common()))
    print("releases del canónico por categoría del valor: "
          + ", ".join(f"{k} {v}" for k, v in rel_cats.most_common()))
    return 0


def render_review(table, norm):
    lines = [
        "# Revisión manual de ubicaciones",
        "",
        "*Generado por `python3 scripts/locations.py normalize`. No editar a mano: las "
        "decisiones van en `data/locations/rules.json` (`values`, `outside`, "
        "`place_overrides`) o en `data/locations/manual.json` (por release).*",
        "",
        "Cada fila es un **texto crudo** tal como lo dio Bandcamp. `rel.` = releases del "
        "canónico con ese texto como observación directa; `cuentas` = cuentas de Bandcamp "
        "distintas que lo usan.",
        "",
    ]
    order = ["unresolved", "unexpected", "ambiguous", "invalid", "outside_scope", "region_only"]
    titles = {
        "unresolved": "Sin regla (¿municipio nuevo, barrio, errata?)",
        "unexpected": "Topónimo del ámbito con país incoherente",
        "ambiguous": "Ambiguos",
        "invalid": "Inválidos o improbables (regla manual)",
        "outside_scope": "Fuera de Euskal Herria",
        "region_only": "Solo región, comarca o país (sin municipio)",
    }
    for cat in order:
        rows = [(v, c) for v, c in table.items() if c["category"] == cat]
        rows.sort(key=lambda r: (-r[1]["catalog_releases"], -r[1]["observations"], r[0]))
        lines += [f"## {titles[cat]} — {len(rows)} valores, "
                  f"{sum(c['catalog_releases'] for _, c in rows)} releases", ""]
        if not rows:
            lines += ["Ninguno.", ""]
            continue
        lines += ["| Texto crudo | rel. | obs. | cuentas | Motivo |", "|---|---:|---:|---:|---|"]
        for v, c in rows:
            extra = c.get("region") or c.get("place_collision") or ", ".join(c.get("candidates", []))
            reason = c["reason"] + (f" ({extra})" if extra else "")
            lines.append(f"| {v} | {c['catalog_releases']} | {c['observations']} | {c['accounts']} | {reason} |")
        lines.append("")
    # Resueltos: para verificación rápida, agrupados por lugar.
    by_place = defaultdict(list)
    for v, c in table.items():
        if c["category"] == "resolved":
            by_place[c["place"]].append((v, c["catalog_releases"]))
    lines += [f"## Resueltos a municipio — {len(by_place)} municipios", "",
              "| Municipio | Territorio | Textos crudos (releases) |", "|---|---|---|"]
    for pid in sorted(by_place, key=lambda p: -sum(n for _, n in by_place[p])):
        place = norm.places[pid]
        vals = "; ".join(f"{v} ({n})" for v, n in sorted(by_place[pid], key=lambda x: -x[1]))
        lines.append(f"| {place['name']} (`{pid}`) | {place['territory']} | {vals} |")
    return "\n".join(lines) + "\n"


# ------------------------------------------------------------------
# Fase 5 — resolución
# ------------------------------------------------------------------

def label_accounts():
    """Cuentas que el índice de sellos (labels_index.py) marca como sello:
    su ubicación es la del sello y nunca se propaga a sus artistas."""
    return frozenset(r["account_id"] for r in load_json(LABELS_FILE, []))


def compute_resolutions():
    catalog = load_catalog()
    obs = load_all_observations()
    norm = make_normalizer()
    manual = load_json(MANUAL_FILE, {})
    res = L.resolve_catalog(catalog["albums"], obs, norm, label_accounts(), manual)
    return catalog, norm, res


def cmd_resolve(args):
    catalog, norm, res = compute_resolutions()
    write_text(RESOLUTIONS_FILE, L.dumps_lines({str(k): v for k, v in sorted(res.items())}))
    types = Counter(r["type"] for r in res.values())
    conflicts = sum(1 for r in res.values() if r.get("conflicts"))
    print(f"{len(res)} releases: " + ", ".join(f"{k} {v}" for k, v in types.most_common())
          + f"; con contradicciones: {conflicts}")
    return 0


# ------------------------------------------------------------------
# Fase 6 — auditoría y consultas municipio × tag
# ------------------------------------------------------------------

# Tipos que el mapa sitúa por defecto (tag_hint solo si se activa).
DEFAULT_MAP_TYPES = ("manual", "direct", "same_account", "artist_inferred")
RELIABLE_TYPES = ("manual", "direct", "same_account")
TYPE_LABELS = {
    "manual": "manual",
    "direct": "directa (Bandcamp, esta release)",
    "same_account": "misma cuenta de Bandcamp",
    "artist_inferred": "inferida por artista",
    "region_only": "solo región/país",
    "outside_scope": "fuera de Euskal Herria",
    "tag_hint": "solo pista de tag",
    "unresolved": "sin resolver",
}


class Analysis:
    """Cruces municipio × tag sobre la resolución vigente."""

    def __init__(self, catalog, norm, res, types=DEFAULT_MAP_TYPES):
        self.albums = {a["id"]: a for a in catalog["albums"]}
        self.norm = norm
        self.res = res
        self.types = types
        self.total = len(self.albums)
        self.tag_counts = Counter(t for a in self.albums.values() for t in set(a["tags"]))
        # Los tags que son topónimos no cuentan como «tags de la escena».
        self.geo_tags = frozenset(t for t in self.tag_counts if norm.tag_hint(t))
        self.by_place = defaultdict(list)
        for rid, r in res.items():
            if r["type"] in types and r.get("place"):
                self.by_place[r["place"]].append(rid)

    def place_name(self, pid):
        return self.norm.places[pid]["name"]

    def overrepresented(self, pid, limit=10):
        return L.overrepresented_tags(self.by_place[pid], self.albums, self.tag_counts, self.total,
                                      limit=limit, exclude=self.geo_tags)

    def top_tags(self, pid, limit=10):
        c = Counter(t for rid in self.by_place[pid] for t in set(self.albums[rid]["tags"])
                    if t not in self.geo_tags)
        return c.most_common(limit)

    def tag_places(self, tag, limit=15):
        rows = []
        n_tag = self.tag_counts.get(tag, 0)
        for pid, ids in self.by_place.items():
            n = sum(1 for rid in ids if tag in self.albums[rid]["tags"])
            if n:
                rows.append((pid, n, len(ids), L.lift(n, len(ids), n_tag, self.total)))
        rows.sort(key=lambda r: (-r[1], -r[3], r[0]))
        located = sum(r[1] for r in rows)
        return rows[:limit], n_tag, located


def audit_stats(catalog, norm, res):
    albums = {a["id"]: a for a in catalog["albums"]}
    types = Counter(r["type"] for r in res.values())
    an = Analysis(catalog, norm, res)
    places = norm.places
    per_place = []
    for pid, ids in an.by_place.items():
        artists = {L.fold(albums[i]["artist"]) for i in ids}
        years = [albums[i]["year"] for i in ids if albums[i]["year"]]
        per_type = Counter(res[i]["type"] for i in ids)
        per_place.append({
            "id": pid, "name": places[pid]["name"], "territory": places[pid]["territory"],
            "releases": len(ids), "artists": len(artists),
            "years": [min(years), max(years)] if years else None,
            "by_type": dict(per_type),
            "label_account_share": round(sum(1 for i in ids if res[i]["account_kind"] == "label") / len(ids), 3),
            "top_tags": an.top_tags(pid, 8),
            "overrepresented": [(t, n, round(x, 2)) for t, n, x in an.overrepresented(pid, 8)],
        })
    per_place.sort(key=lambda r: (-r["releases"], r["id"]))
    territory = Counter()
    for r in res.values():
        if r["type"] in DEFAULT_MAP_TYPES and r.get("place"):
            territory[places[r["place"]]["territory"]] += 1
    region_counts = Counter(r.get("region") for r in res.values() if r["type"] == "region_only")
    decades = defaultdict(Counter)
    for rid, r in res.items():
        y = albums[rid]["year"]
        d = f"{y // 10 * 10}s" if y else "s/f"
        decades[d]["located" if (r["type"] in DEFAULT_MAP_TYPES and r.get("place")) else "not_located"] += 1
    conflicts = Counter()
    for r in res.values():
        for c in r.get("conflicts", []):
            conflicts[c["kind"]] += 1
    located = sum(1 for r in res.values() if r["type"] in DEFAULT_MAP_TYPES and r.get("place"))
    reliable = sum(1 for r in res.values() if r["type"] in RELIABLE_TYPES and r.get("place"))
    label_loc = sum(1 for r in res.values() if r["type"] in DEFAULT_MAP_TYPES and r.get("place")
                    and r["account_kind"] == "label")
    not_located = [r for r in res.values() if not (r["type"] in DEFAULT_MAP_TYPES and r.get("place"))]
    checked_empty = sum(1 for r in not_located if r.get("checked_empty"))
    unresolved = [r for r in res.values() if r["type"] == "unresolved"]
    unresolved_breakdown = {
        "bandcamp_sin_ubicacion": sum(1 for r in unresolved if r.get("checked_empty")),
        "evidencia_descartada": sum(1 for r in unresolved if r.get("rejected_values") and not r.get("checked_empty")),
        "sin_evidencia": sum(1 for r in unresolved if not r.get("checked_empty") and not r.get("rejected_values")),
    }
    rejected = Counter(v for r in res.values() for v in r.get("rejected_values", {}))
    questions = {}
    if "zarautz" in an.by_place:
        questions["overrepresented_zarautz"] = [(t, n, round(x, 2)) for t, n, x in an.overrepresented("zarautz", 10)]
    for tag in ("noise", "hardcore", "techno", "trikitixa"):
        rows, n_tag, located_tag = an.tag_places(tag, 10)
        questions[f"tag:{tag}"] = {"tag_releases": n_tag, "located": located_tag,
                                   "places": [(places[p]["name"], n, tot, round(x, 2)) for p, n, tot, x in rows]}
    return {
        "total_releases": len(res),
        "types": dict(types),
        "located_default": located,
        "reliable": reliable,
        "located_via_label_account": label_loc,
        "not_located": len(res) - located,
        "checked_empty": checked_empty,
        "unresolved_breakdown": unresolved_breakdown,
        "municipalities": len(an.by_place),
        "territories": dict(territory),
        "regions_only": dict(region_counts),
        "decades": {d: dict(c) for d, c in sorted(decades.items())},
        "conflicts": dict(conflicts),
        "releases_with_conflicts": sum(1 for r in res.values() if r.get("conflicts")),
        "rejected_values": dict(rejected.most_common()),
        "places": per_place,
        "questions": questions,
    }


def pct(n, total):
    return f"{100 * n / total:.1f} %" if total else "—"


def render_audit(s):
    T = s["total_releases"]
    t = s["types"]
    L_ = [
        "# Auditoría del dataset de ubicaciones (fase 6)",
        "",
        "*Generado por `python3 scripts/locations.py audit` a partir de "
        "`data/locations/resolutions.json`. No editar a mano.*",
        "",
        "Recordatorio: la ubicación es la que Bandcamp da **hoy** a la cuenta que publica "
        "(grupo o sello). Estas cifras describen **el archivo**, no la escena ni la residencia "
        "histórica de nadie.",
        "",
        "## Resumen",
        "",
        "| | Releases | % |",
        "|---|---:|---:|",
        f"| **Total** | {T} | 100 % |",
    ]
    for k in ("direct", "same_account", "artist_inferred", "manual", "region_only",
              "outside_scope", "tag_hint", "unresolved"):
        L_.append(f"| {k} — {TYPE_LABELS[k]} | {t.get(k, 0)} | {pct(t.get(k, 0), T)} |")
    L_ += [
        "",
        f"- **En el mapa por defecto** (direct + same_account + artist_inferred + manual): "
        f"**{s['located_default']}** ({pct(s['located_default'], T)}).",
        f"- **Fiables** (Bandcamp de la propia cuenta o decisión manual, sin inferencia): "
        f"**{s['reliable']}** ({pct(s['reliable'], T)}).",
        f"- Situadas por la ubicación de una **cuenta con varios artistas** (probable sello, "
        f"índice `data/derived/labels.json`): {s['located_via_label_account']}. Su lugar es el "
        f"de esa cuenta, no necesariamente el del grupo.",
        f"- **Sin municipio** en el mapa por defecto: **{s['not_located']}** "
        f"({pct(s['not_located'], T)}); de ellas, {s['checked_empty']} consultadas en Bandcamp "
        f"sin ubicación.",
        f"- Sin resolver ({t.get('unresolved', 0)}): {s['unresolved_breakdown']['bandcamp_sin_ubicacion']} "
        f"porque Bandcamp no da ubicación, {s['unresolved_breakdown']['evidencia_descartada']} con "
        f"evidencia descartada (ver abajo) y {s['unresolved_breakdown']['sin_evidencia']} sin evidencia.",
        f"- Municipios con al menos una release: **{s['municipalities']}**.",
        f"- Releases con contradicciones registradas: {s['releases_with_conflicts']} "
        f"({', '.join(f'{k} {v}' for k, v in sorted(s['conflicts'].items())) or 'ninguna'}).",
        "",
        "## Por territorio (mapa por defecto)",
        "",
        "| Territorio | Releases |",
        "|---|---:|",
    ]
    L_ += [f"| {k} | {v} |" for k, v in sorted(s["territories"].items(), key=lambda x: -x[1])]
    L_ += ["", "## Solo región (region_only)", "", "| Región | Releases |", "|---|---:|"]
    L_ += [f"| {k} | {v} |" for k, v in sorted(s["regions_only"].items(), key=lambda x: -x[1])]
    L_ += ["", "## Por décadas (año de la release)", "",
           "| Década | Localizadas | Sin municipio | % localizadas |", "|---|---:|---:|---:|"]
    for d, c in s["decades"].items():
        a, b = c.get("located", 0), c.get("not_located", 0)
        L_.append(f"| {d} | {a} | {b} | {pct(a, a + b)} |")
    L_ += ["", "## Valores descartados (evidencia no aceptada)", "",
           "| Texto crudo | Releases afectadas |", "|---|---:|"]
    L_ += [f"| {k} | {v} |" for k, v in s["rejected_values"].items()]
    L_ += ["", "## Municipios", "",
           "Tags sobrerrepresentados: `lift = (releases del municipio con el tag / releases del "
           "municipio) ÷ (releases del archivo con el tag / releases del archivo)`, con un mínimo "
           "de 3 releases del tag en el municipio y 10 en el archivo, sin contar tags que son "
           "topónimos.",
           "",
           "| Municipio | Territorio | Releases | Artistas | Años | % cuenta multiartista | Tags principales | Sobrerrepresentados |",
           "|---|---|---:|---:|---|---:|---|---|"]
    for p in s["places"]:
        years = f"{p['years'][0]}–{p['years'][1]}" if p["years"] else "—"
        top = ", ".join(f"{t} ({n})" for t, n in p["top_tags"][:5])
        over = ", ".join(f"{t} ×{x:.1f}" for t, n, x in p["overrepresented"][:4])
        L_.append(f"| {p['name']} | {p['territory']} | {p['releases']} | {p['artists']} | {years} | "
                  f"{round(100 * p['label_account_share'])} % | {top} | {over} |")
    q = s["questions"]
    L_ += ["", "## Preguntas de ejemplo", ""]
    if "overrepresented_zarautz" in q:
        L_ += ["**¿Qué tags están sobrerrepresentados en Zarautz?**", ""]
        L_ += [f"- {t}: ×{x:.1f} ({n} releases)" for t, n, x in q["overrepresented_zarautz"]]
        L_.append("")
    for key, v in q.items():
        if not key.startswith("tag:"):
            continue
        tag = key[4:]
        L_ += [f"**¿Dónde aparece `{tag}`?** {v['tag_releases']} releases en el archivo, "
               f"{v['located']} localizadas ({pct(v['located'], v['tag_releases'])}).", "",
               "| Municipio | Releases con el tag | Releases del municipio | lift |", "|---|---:|---:|---:|"]
        L_ += [f"| {name} | {n} | {tot} | ×{x:.1f} |" for name, n, tot, x in v["places"]]
        L_.append("")
    L_ += ["**¿Qué parte del catálogo tiene ubicación fiable?** "
           f"{s['reliable']} de {T} ({pct(s['reliable'], T)}); con inferencia por artista, "
           f"{s['located_default']} ({pct(s['located_default'], T)}).", "",
           "Consultas propias: `python3 scripts/locations.py query --place zarautz` o "
           "`--tag noise` (matriz municipio × tag y tag × municipio).", ""]
    return "\n".join(L_)


def cmd_audit(args):
    catalog, norm, res = compute_resolutions()
    s = audit_stats(catalog, norm, res)
    write_json(REPORTS_DIR / "audit.json", s)
    write_text(AUDIT_DOC, render_audit(s))
    print(f"auditoría: {rel(AUDIT_DOC)}; en mapa {s['located_default']}/{s['total_releases']}, "
          f"{s['municipalities']} municipios")
    return 0


def cmd_query(args):
    catalog, norm, res = compute_resolutions()
    types = DEFAULT_MAP_TYPES + (("tag_hint",) if args.with_tag_hints else ())
    an = Analysis(catalog, norm, res, types)
    if args.place:
        pid = args.place if args.place in norm.places else norm.place_for_text(args.place)
        if not pid:
            print(f"lugar desconocido: {args.place}")
            return 1
        ids = an.by_place.get(pid, [])
        print(f"{an.place_name(pid)} — {len(ids)} releases")
        print("\nmunicipio × tag (más frecuentes):")
        for t, n in an.top_tags(pid, args.limit):
            print(f"  {t:30} {n}")
        print("\nsobrerrepresentados (lift; mín. 3 en el lugar y 10 en el archivo):")
        for t, n, x in an.overrepresented(pid, args.limit):
            print(f"  {t:30} ×{x:5.2f}  ({n})")
    if args.tag:
        rows, n_tag, located = an.tag_places(args.tag, args.limit)
        print(f"\ntag × municipio: «{args.tag}» — {n_tag} releases, {located} localizadas")
        for p, n, tot, x in rows:
            print(f"  {an.place_name(p):24} {n:5}  de {tot:5}  ×{x:5.2f}")
    return 0


# ------------------------------------------------------------------
# Índice del mapa (lo que carga la app)
# ------------------------------------------------------------------

TERRITORIES = ["Bizkaia", "Gipuzkoa", "Araba", "Nafarroa", "Iparralde"]
MAP_TYPES = ["direct", "same_account", "artist_inferred", "manual",
             "tag_hint", "region_only", "outside_scope", "unresolved"]
GRID_CELL_LAT = 0.045   # ~5 km: la retícula es silueta, no precisión
GRID_REACH = 0.06       # una celda es «tierra» si hay un núcleo a < ~6,5 km
PROJ_LAT0 = 42.8        # equirectangular con corrección de coseno


def silhouette_points(gazetteer):
    """Núcleos para la silueta; descarta coordenadas absurdas (núcleo a más
    de ~20 km de su municipio: errores de Wikidata)."""
    import math
    munis = {g["municipality_code"]: g for g in gazetteer if g["kind"] == "municipality"}
    pts = []
    for g in gazetteer:
        m = munis.get(g["municipality_code"])
        if not m:
            continue
        if g is not m and math.hypot(g["lat"] - m["lat"], g["lon"] - m["lon"]) > 0.2:
            continue
        pts.append((g["lat"], g["lon"], g["territory"]))
    return pts


def build_grid(points):
    import math
    k = math.cos(math.radians(PROJ_LAT0))
    cw = GRID_CELL_LAT / k
    lats = [p[0] for p in points]
    lons = [p[1] for p in points]
    top = round(max(lats) + GRID_CELL_LAT, 4)
    left = round(min(lons) - cw, 4)
    rows = int((max(lats) - min(lats)) / GRID_CELL_LAT) + 3
    cols = int((max(lons) - min(lons)) / cw) + 3
    # Cubo espacial para no comparar cada celda con los 2.000 núcleos.
    buckets = defaultdict(list)
    for p in points:
        buckets[(int((top - p[0]) / GRID_CELL_LAT), int((p[1] - left) / cw))].append(p)
    cells = []
    for r in range(rows):
        for c in range(cols):
            la = top - (r + 0.5) * GRID_CELL_LAT
            lo = left + (c + 0.5) * cw
            best, bd = None, 9.0
            for dr in (-2, -1, 0, 1, 2):
                for dc in (-2, -1, 0, 1, 2):
                    for p in buckets.get((r + dr, c + dc), ()):
                        d = math.hypot(p[0] - la, (p[1] - lo) * k)
                        if d < bd:
                            best, bd = p, d
            if best and bd < GRID_REACH:
                cells.append([c, r, TERRITORIES.index(best[2])])
    return {"top": top, "left": left, "cell_lat": GRID_CELL_LAT, "cell_lon": round(cw, 6),
            "rows": rows, "cols": cols, "cells": cells}


def cmd_build(args):
    catalog, norm, res = compute_resolutions()
    grid = build_grid(silhouette_points(load_gazetteer()))
    used = sorted({r["place"] for r in res.values() if r.get("place")},
                  key=lambda pid: (norm.places[pid]["territory"], pid))
    pidx = {pid: i for i, pid in enumerate(used)}
    regions = sorted({r["region"] for r in res.values() if r.get("region")})
    ridx = {rid: i for i, rid in enumerate(regions)}
    rules = load_rules()

    def xy(lat, lon):
        return [round((lon - grid["left"]) / grid["cell_lon"], 2),
                round((grid["top"] - lat) / grid["cell_lat"], 2)]

    places = []
    for pid in used:
        p = norm.places[pid]
        alt = sorted({v for v in p["names"].values() if v != p["name"]})
        places.append([pid, p["name"], *xy(p["lat"], p["lon"]),
                       TERRITORIES.index(p["territory"]), " · ".join(alt)])
    ids, place, typ, region, flags = [], [], [], [], []
    for a in sorted(catalog["albums"], key=lambda a: a["id"]):
        r = res[a["id"]]
        ids.append(a["id"])
        place.append(pidx[r["place"]] if r.get("place") else -1)
        typ.append(MAP_TYPES.index(r["type"]))
        region.append(ridx[r["region"]] if r.get("region") else -1)
        flags.append((1 if r.get("account_kind") == "label" else 0)
                     | (2 if r.get("conflicts") else 0)
                     | (4 if r.get("checked_empty") else 0))
    reg_meta = rules.get("regions", {})
    # Tags que son topónimos (pistas): la app los excluye del cálculo de
    # tags sobrerrepresentados, igual que la auditoría.
    tag_counts = Counter(t for a in catalog["albums"] for t in set(a["tags"]))
    geo_tags = sorted(t for t in tag_counts if norm.tag_hint(t))
    doc = {
        "meta": {
            "generated_by": "python3 scripts/locations.py build",
            "releases": len(ids),
            "note": "Índice del mapa. Posiciones en unidades de celda de la retícula "
                    "(proyección equirectangular, lat0 42,8). La coordenada de un municipio "
                    "es un punto representativo para dibujar, no la ubicación de nadie.",
            "flags": {"1": "cuenta-sello", "2": "contradicciones", "4": "Bandcamp sin ubicación"},
        },
        "territories": TERRITORIES,
        "types": MAP_TYPES,
        "regions": [[rid, reg_meta.get(rid, {}).get("name", rid), reg_meta.get(rid, {}).get("level"),
                     reg_meta.get(rid, {}).get("territory")] for rid in regions],
        "grid": grid,
        "places": places,
        "geo_tags": geo_tags,
        "releases": {"id": ids, "place": place, "type": typ, "region": region, "flags": flags},
    }
    write_text(MAP_INDEX_FILE, json.dumps(doc, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(f"{rel(MAP_INDEX_FILE)}: {len(places)} lugares, {len(grid['cells'])} celdas, "
          f"{MAP_INDEX_FILE.stat().st_size // 1024} KB")
    return 0


def cmd_all(args):
    for f in (cmd_normalize, cmd_resolve, cmd_audit, cmd_build):
        rc = f(args)
        if rc:
            return rc
    return 0

# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("ingest")
    p.add_argument("files", nargs="+")
    p.set_defaults(func=cmd_ingest)
    p = sub.add_parser("check")
    p.set_defaults(func=cmd_check)
    p = sub.add_parser("recover")
    p.add_argument("--no-git", action="store_true", help="solo el working tree")
    p.set_defaults(func=cmd_recover)
    p = sub.add_parser("scrape")
    p.add_argument("--budget", type=int, default=900, help="presupuesto duro de peticiones")
    p.add_argument("--delay-min", type=float, default=2.0)
    p.add_argument("--delay-max", type=float, default=2.3)
    p.add_argument("--tries-per-account", type=int, default=3,
                   help="fichas a probar por cuenta si la primera falla")
    p.add_argument("--retry-gone", action="store_true", help="reintentar 404/410")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=cmd_scrape)
    p = sub.add_parser("gazetteer")
    p.set_defaults(func=cmd_gazetteer)
    p = sub.add_parser("places")
    p.set_defaults(func=cmd_places)
    p = sub.add_parser("normalize")
    p.set_defaults(func=cmd_normalize)
    p = sub.add_parser("resolve")
    p.set_defaults(func=cmd_resolve)
    p = sub.add_parser("audit")
    p.set_defaults(func=cmd_audit)
    p = sub.add_parser("query")
    p.add_argument("--place")
    p.add_argument("--tag")
    p.add_argument("--limit", type=int, default=15)
    p.add_argument("--with-tag-hints", action="store_true")
    p.set_defaults(func=cmd_query)
    p = sub.add_parser("build")
    p.set_defaults(func=cmd_build)
    p = sub.add_parser("all")
    p.set_defaults(func=cmd_all)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
