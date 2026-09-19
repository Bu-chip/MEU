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
    for target, groups in sorted(per_file.items()):
        meta, existing = load_obs_file(OBS_DIR / target)
        merged = L.merge_observations(existing, *groups)
        meta = {
            "source": target,
            "source_type": L.OBS_SOURCE_DISCOVER,
            "subject": L.OBS_SUBJECT,
            "note": ("parciales pendientes de ficha en discovery_state.json" if target.startswith("discovery_state")
                     else "band_location de discover_web, tal cual (sin normalizar)")
            + ". value=null: Bandcamp no daba ubicación. Ubicación de la cuenta que publica, actual y sin fecha.",
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
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
