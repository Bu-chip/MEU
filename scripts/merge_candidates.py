#!/usr/bin/env python3
"""Incorporación al canónico de una oleada mensual de candidatos.

Generaliza scripts/merge_candidates_2026_07.py: aplica las MISMAS reglas
mecánicas (las del criterio maximalista del PR #23), pero sin las
decisiones manuales que eran propias de aquella oleada (URL_FIXES,
homónimos, retenidos). Las tablas de conocimiento auditado —artistas
vascos conocidos, rescates geográficos, vocabulario de géneros— se
reutilizan importándolas de aquel script, que sigue siendo la referencia.

Reglas, en este orden:

  1. Ya en el canónico (mismo album_id o misma URL normalizada): la fila
     no entra; se cuenta como «ya presente».
  2. Casi-duplicado (mismo artista+título, distinta edición): gana la
     edición del GRUPO. Si la del grupo es la candidata, la ficha
     canónica adopta url/album_id/cover_url y la del sello va a
     rejected.json; si el canónico ya tenía la del grupo, la candidata va
     a rejected.json; sello contra sello, el disco ya está y se anota en
     revision_YYYY-MM.json.
  3. Geografía: una ubicación fuera de Euskal Herria NO descarta. Caen
     solo las filas sin ningún vínculo vasco detectable (tag local, tag
     en euskera, nombre o título en euskera, artista ya en el canónico,
     misma página o mismo artista que otra fila aceptada).
  4. Dedupe interno grupo/sello entre candidatos de la misma oleada.
  4b. Retención (patrón RETENIDOS de julio): una fila publicada en una
     cuenta que no es la del artista, sin ubicación, cuyo artista no está
     ya en el canónico y sin señal vasca propia (topónimo o euskera en su
     nombre o título) no entra ni se rechaza: queda anotada en
     revision_YYYY-MM.json. Son las cuentas agregadoras que etiquetan
     material internacional como «euskal rock» y el README es explícito:
     ante la duda un disco entra, pero lo clarísimamente ajeno se
     descarta. Retener, no rechazar, deja la decisión a la revisión
     humana y es reversible.
  5. El resto entra como ficha nueva: ids correlativos desde max(id)+1,
     genre derivado de los tags contra el vocabulario del canónico (sin
     señal → null) y solo los 9 campos del esquema.

Las ubicaciones NO viajan en la ficha: viven en data/locations/ como
observaciones (scripts/locations.py). Tras este script hay que ejecutar
`python3 scripts/pipeline.py` y `python3 scripts/locations.py all`.

Uso:
    python3 scripts/merge_candidates.py 2026-08 --pr 65
    python3 scripts/merge_candidates.py 2026-08 --dry-run
"""

import argparse
import collections
import json
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from pipeline import DATA_FILE, serialize, validate  # noqa: E402
from merge_candidates_2026_07 import (  # noqa: E402
    EUSK_LEX, GENERIC_ONLY, TOWN_PAT, basque_signals, build_ficha, cf, geo_zone,
    is_band_page, normalize_url, pair_key, slug_similarity, subdomain,
)


def senal_propia(row):
    """¿La fila trae por sí misma una señal vasca (no de la cuenta)?"""
    import re
    if set(re.findall(r"[a-z]+", cf(row["artist"]))) & EUSK_LEX:
        return True
    if len(set(re.findall(r"[a-z]+", cf(row["title"]))) & EUSK_LEX) >= 2:
        return True
    tags = [cf(t).replace("-", " ") for t in row["tags"]]
    return any(t not in GENERIC_ONLY and TOWN_PAT.search(t) for t in tags)

REJECTED_FILE = REPO_ROOT / "data" / "rejected.json"


def cargar(mes):
    ruta = REPO_ROOT / "data" / f"candidates_{mes}.json"
    if not ruta.exists():
        sys.exit(f"no existe {ruta.relative_to(REPO_ROOT)}")
    doc = json.loads(ruta.read_text(encoding="utf-8"))
    if doc.get("deferred_oleada2"):
        print(f"aviso: {len(doc['deferred_oleada2'])} filas en la cola "
              "oleada-2 (Iparralde); no se incorporan aquí")
    return doc["candidates"]


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("mes", help="sufijo YYYY-MM del fichero de candidatos")
    parser.add_argument("--pr", type=int, default=None, help="nº del PR de candidatos")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    cand_rows = cargar(args.mes)
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    albums = data["albums"]
    canon_by_key = collections.defaultdict(list)
    for a in albums:
        canon_by_key[pair_key(a)].append(a)
    canon_artists = {cf(a["artist"]) for a in albums}
    canon_artists_long = [a for a in canon_artists if len(a) >= 8]
    canon_ids = {a["album_id"] for a in albums if a["album_id"] is not None}
    canon_urls = {normalize_url(a["url"]) for a in albums if a["url"]}

    rejected_new = {}
    revision = {"sello_vs_sello": [], "internos_ambiguos": [], "retenidos": []}
    stats = collections.Counter()
    decision_date = date.today().isoformat()

    def reject(url, reason):
        key = normalize_url(url)
        if key in rejected_new:
            return
        rejected_new[key] = {"reason": reason, "date": decision_date,
                             "pr": args.pr}

    # --- 1-2. contra el canónico ---------------------------------------
    pool = []
    to_incorporate = []
    for row in cand_rows:
        if row["album_id"] in canon_ids or normalize_url(row["url"]) in canon_urls:
            stats["ya_en_el_canonico"] += 1
            continue
        matches = canon_by_key.get(pair_key(row))
        if matches:
            canon = matches[0]
            if not canon["url"]:
                canon["url"] = row["url"]
                canon["album_id"] = row["album_id"]
                canon["cover_url"] = row["cover_url"]
                stats["canon_enriquecido"] += 1
                continue
            cand_band = is_band_page(row["artist"], row["url"])
            canon_band = is_band_page(canon["artist"], canon["url"])
            if cand_band and not canon_band:
                reject(canon["url"],
                       f"edición de sello sustituida por la del grupo "
                       f"(id {canon['id']}: {row['url']})")
                canon["url"] = row["url"]
                canon["album_id"] = row["album_id"]
                canon["cover_url"] = row["cover_url"]
                stats["sello_sustituido_por_grupo"] += 1
            elif canon_band and not cand_band:
                reject(row["url"],
                       f"edición de sello; el canónico tiene la del grupo "
                       f"(id {canon['id']})")
                stats["edicion_sello_descartada"] += 1
            else:
                reject(row["url"],
                       f"mismo disco ya en el canónico (id {canon['id']}) "
                       f"en otra edición; sello vs sello")
                revision["sello_vs_sello"].append(
                    {"candidato_url": row["url"], "canon_id": canon["id"],
                     "canon_url": canon["url"], "artist": row["artist"],
                     "title": row["title"]})
                stats["sello_vs_sello"] += 1
            continue
        pool.append(row)

    # --- 3. geografía ---------------------------------------------------
    eh_artists = {cf(r["artist"]) for r in cand_rows if geo_zone(r) != "ext"}
    eh_subs = {subdomain(r["url"]) for r in cand_rows if geo_zone(r) != "ext"}
    ext_rows = [r for r in cand_rows if geo_zone(r) == "ext"]
    signals = {id(r): basque_signals(r, canon_artists, canon_artists_long, eh_artists)
               for r in ext_rows}
    for _ in range(2):  # propagación: misma página / mismo artista aceptado
        ok_subs = {subdomain(r["url"]) for r in ext_rows if signals[id(r)]} | eh_subs
        ok_artists = {cf(r["artist"]) for r in ext_rows if signals[id(r)]}
        for r in ext_rows:
            if not signals[id(r)]:
                if subdomain(r["url"]) in ok_subs:
                    signals[id(r)] = ["misma página que artista aceptado"]
                elif cf(r["artist"]) in ok_artists:
                    signals[id(r)] = ["mismo artista aceptado"]
    pool_ids = {id(r) for r in pool}
    geo_out = {id(r) for r in ext_rows if not signals[id(r)] and id(r) in pool_ids}
    for r in ext_rows:
        if id(r) in geo_out:
            reject(r["url"],
                   f"sin vínculo vasco detectable (tag genérico de pasada); "
                   f"ubicación: {r['band_location']}")
            stats["geografia_descartada"] += 1
    pool = [r for r in pool if id(r) not in geo_out]

    # --- 4. dedupe interno grupo/sello ----------------------------------
    groups = collections.defaultdict(list)
    for r in pool:
        groups[pair_key(r)].append(r)
    for rows in groups.values():
        if len(rows) == 1:
            to_incorporate.append(rows[0])
            continue
        band_editions = [r for r in rows if is_band_page(r["artist"], r["url"])]
        if len(band_editions) == 1:
            chosen = band_editions[0]
        else:
            chosen = max(rows, key=lambda r: (slug_similarity(r["title"], r["url"]),
                                              is_band_page(r["artist"], r["url"])))
            revision["internos_ambiguos"].append(
                {"artist": chosen["artist"], "title": chosen["title"],
                 "elegido": chosen["url"],
                 "alternativas": [x["url"] for x in rows if x is not chosen]})
            stats["interno_ambiguo_grupo"] += 1
        to_incorporate.append(chosen)
        for r in rows:
            if r is not chosen:
                reject(r["url"],
                       f"edición duplicada del mismo disco; entra {chosen['url']}")
                stats["edicion_interna_descartada"] += 1

    # --- 4b. retención de material ajeno publicado por agregadoras -------
    retenidas = []
    for row in list(to_incorporate):
        if (not is_band_page(row["artist"], row["url"])
                and not row["band_location"]
                and cf(row["artist"]) not in canon_artists
                and not senal_propia(row)):
            to_incorporate.remove(row)
            retenidas.append(row)
            revision["retenidos"].append(
                {"artist": row["artist"], "title": row["title"], "url": row["url"],
                 "cuenta": subdomain(row["url"]),
                 "nota": "cuenta ajena al artista, sin ubicación y sin señal vasca "
                         "propia: ni entra ni se rechaza, pendiente de revisión"})
            stats["retenido"] += 1

    # --- 5. incorporación ------------------------------------------------
    seen_keys = {pair_key(a) for a in albums}
    next_id = max(a["id"] for a in albums) + 1
    nuevas = []
    for row in to_incorporate:
        k = pair_key(row)
        assert k not in seen_keys, f"duplicado inesperado al incorporar: {k}"
        seen_keys.add(k)
        ficha = build_ficha(row, next_id)
        albums.append(ficha)
        nuevas.append(ficha)
        next_id += 1
        stats["ficha_nueva"] += 1

    data["artists"] = sorted({a["artist"] for a in albums})
    data["tags"] = sorted({t for a in albums for t in a["tags"]})
    data["years"] = sorted({a["year"] for a in albums if a["year"] is not None})

    album_ids = [a["album_id"] for a in albums if a["album_id"] is not None]
    assert len(album_ids) == len(set(album_ids)), "album_id duplicado tras el merge"
    ids = [a["id"] for a in albums]
    assert len(ids) == len(set(ids)), "id duplicado tras el merge"
    validate(data)

    total = sum(v for k, v in stats.items() if k != "interno_ambiguo_grupo")
    assert total == len(cand_rows), \
        f"cuadre roto: {total} clasificados de {len(cand_rows)}"

    print(f"candidatos {args.mes}: {len(cand_rows)} filas")
    for k, v in sorted(stats.items()):
        print(f"  · {k}: {v}")
    print(f"canónico: {len(albums)} álbumes, {len(data['artists'])} artistas, "
          f"{len(data['tags'])} tags")
    if retenidas:
        print("retenidos (pendientes de revisión, ni entran ni se rechazan):")
        for r in retenidas:
            print(f"  ? {r['artist']} — {r['title']} ({subdomain(r['url'])})")
    if nuevas:
        print("altas:")
        for f in nuevas:
            print(f"  + {f['id']} · {f['artist']} — {f['title']} "
                  f"({f['year']}, {f['genre']})")
    if args.dry_run:
        print("dry-run: no se ha escrito nada")
        return 0

    rej = json.loads(REJECTED_FILE.read_text(encoding="utf-8"))
    # rejected.json es acumulativo: una URL ya rechazada en una oleada
    # anterior (el descubrimiento vuelve a proponerla) conserva su decisión
    # original, con su fecha y su PR. No se pisa ni se aborta.
    ya = set(rej["rejected"]) & set(rejected_new)
    if ya:
        print(f"  · ya rechazadas en una oleada anterior: {len(ya)} "
              "(se conserva la decisión original)")
    nuevas_rej = {k: v for k, v in rejected_new.items() if k not in ya}
    rej["rejected"].update(dict(sorted(nuevas_rej.items())))
    REJECTED_FILE.write_text(
        json.dumps(rej, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")

    if any(revision.values()):
        revision_file = REPO_ROOT / "data" / f"revision_{args.mes}.json"
        revision_file.write_text(
            json.dumps({"meta": {
                "que_es": f"Pendientes de revisión manual tras el merge de "
                          f"candidates/{args.mes}. No bloquean el canónico.",
                "date": decision_date, "pr": args.pr}, **revision},
                indent=4, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"revisión pendiente: {revision_file.relative_to(REPO_ROOT)}")

    DATA_FILE.write_text(serialize(data), encoding="utf-8")
    print(f"rejected.json: +{len(nuevas_rej)} entradas")
    print("siguiente: python3 scripts/pipeline.py && python3 scripts/locations.py all")
    return 0


if __name__ == "__main__":
    sys.exit(main())
