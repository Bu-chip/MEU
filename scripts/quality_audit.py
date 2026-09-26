#!/usr/bin/env python3
"""Auditoría de calidad del canónico — SOLO LECTURA.

Recorre data/bandcamp_bilbaotags_clean.json y escribe un informe en
Markdown (por defecto docs/quality-audit-YYYY-MM.md) con recuento y
ejemplos (máx. 30 por categoría) de:

  * duplicados: mismo album_id, misma URL normalizada, mismo artista+título
    normalizados con distinta URL, y mismo artista + mismo slug en otra cuenta;
  * artistas: mismo nombre con varias grafías, capitalización rara (TODO EN
    MAYÚSCULAS / todo en minúsculas cuando el catálogo lo tiene con mayúscula
    inicial), espacios sobrantes;
  * genre / tags null o vacíos, genre fuera del vocabulario, tags sucios;
  * URLs sucias (query, fragmento, espacios, http, mayúsculas, barra final,
    dominio que no es bandcamp.com, ruta que no es /album/) o nulas;
  * fechas imposibles o vacías, portadas vacías, album_id nulo, campos fuera
    del esquema o con tipo incorrecto;
  * títulos con el artista como prefijo («Artista - Título»).

Y una sección de regresión: comprueba que lo que scripts/pipeline.py ya
resolvió (cola ?from=, dedupe auditado, ARTIST_RENAMES, invisibles,
TAG_RENAMES) sigue resuelto, para no repetir auditorías anteriores.

No modifica ningún dato. Lo único que escribe es el informe.

Uso:
    python3 scripts/quality_audit.py                  # escribe docs/quality-audit-YYYY-MM.md
    python3 scripts/quality_audit.py --out informe.md
    python3 scripts/quality_audit.py --stdout         # imprime el informe
"""

import argparse
import collections
import datetime as dt
import json
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import urlsplit

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = REPO_ROOT / "data" / "bandcamp_bilbaotags_clean.json"
CANDIDATE_FILES = sorted((REPO_ROOT / "data").glob("candidates_20??-??.json"))
DOCS_DIR = REPO_ROOT / "docs"

sys.path.insert(0, str(REPO_ROOT / "scripts"))
import pipeline  # noqa: E402  (solo se importan constantes; no se ejecuta nada)

MAX_EXAMPLES = 30

# Esquema: campo -> tipos admitidos (None se expresa con type(None)).
SCHEMA = {
    "id": (int,),
    "artist": (str,),
    "title": (str,),
    "genre": (str, type(None)),
    "year": (int, type(None)),
    "tags": (list,),
    "url": (str, type(None)),
    "cover_url": (str, type(None)),
    "album_id": (int, type(None)),
}

# Géneros de primer nivel de Bandcamp que usa el canónico (el merge deriva
# `genre` contra este mismo vocabulario, ver merge_candidates_2026_07.GENRE_RULES).
GENRE_VOCAB = {
    "acoustic", "alternative", "ambient", "blues", "comedy", "country",
    "devotional", "electronic", "experimental", "folk", "funk", "hip-hop/rap",
    "jazz", "kids", "latin", "metal", "podcasts", "pop", "punk", "r&b/soul",
    "reggae", "rock", "soundtrack", "spoken word", "world",
}

YEAR_MIN = 1960
BANDCAMP_DOMAIN = "bandcamp.com"
COVER_DOMAIN = "bcbits.com"
INVISIBLE = {chr(c) for c in pipeline.INVISIBLE_CHARS}


# ------------------------------------------------------------------
# Normalizaciones (puras, testeables)
# ------------------------------------------------------------------

def normalize_url(url):
    """Clave de duplicado: sin esquema, sin query ni fragmento, sin barra
    final, sin espacios y todo en minúsculas. Superconjunto de la clave del
    scraper (discover_tags.normalize_url), que no baja a minúsculas el path."""
    if not url:
        return None
    u = urlsplit(url.strip().replace(" ", ""))
    return f"{u.netloc}{u.path.rstrip('/')}".lower()


def url_issues(url):
    """Lista de problemas de una URL (vacía si está limpia)."""
    if url is None:
        return ["nula"]
    issues = []
    if url != url.strip() or " " in url:
        issues.append("espacios")
    u = urlsplit(url.strip())
    if u.query:
        issues.append("query ?" + u.query.split("=", 1)[0])
    if u.fragment or url.rstrip().endswith("#"):
        issues.append("fragmento #")
    if u.scheme == "http":
        issues.append("http sin s")
    elif u.scheme != "https":
        issues.append("sin esquema https")
    if u.netloc != u.netloc.lower() or u.path != u.path.lower():
        issues.append("mayúsculas")
    if u.path.endswith("/"):
        issues.append("barra final")
    host = u.netloc.lower()
    if not (host == BANDCAMP_DOMAIN or host.endswith("." + BANDCAMP_DOMAIN)):
        issues.append("dominio no bandcamp.com")
    if not u.path.startswith("/album/"):
        issues.append("ruta no /album/")
    return issues


def strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s)
                   if not unicodedata.combining(c))


def strong_key(s):
    """Clave fuerte de comparación: sin acentos, casefold, solo alfanumérico."""
    return re.sub(r"[^a-z0-9]", "", strip_accents(s).casefold())


def case_style(name):
    letters = [c for c in name if c.isalpha()]
    if not letters:
        return "sin letras"
    if all(c.isupper() for c in letters):
        return "MAYÚSCULAS"
    if all(c.islower() for c in letters):
        return "minúsculas"
    return "mixta"


def whitespace_issues(s):
    issues = []
    if s != s.strip():
        issues.append("espacio inicial/final")
    if "  " in s:
        issues.append("doble espacio")
    if any(c in INVISIBLE for c in s):
        issues.append("carácter invisible")
    if re.search(r"[,;]$", s.strip()):
        issues.append("puntuación colgante")
    return issues


def url_slug(url):
    if not url:
        return None
    return urlsplit(url).path.rstrip("/").rsplit("/", 1)[-1].lower() or None


def account_of(url):
    if not url:
        return None
    return urlsplit(url).netloc.lower()


def pair_key(album):
    """Clave de casi-duplicado artista+título. Si el título se queda vacío al
    normalizar (`:::`, `===`, `/Φ\\`), se usa el título literal en casefold
    para no agrupar discos distintos."""
    tkey = strong_key(album["title"]) or ("raw:" + album["title"].casefold().strip())
    return (strong_key(album["artist"]), tkey)


def tag_issues(tag):
    """Problemas de un tag. `oi!` y las abreviaturas con puntos (`a.o.r.`,
    `méxico d.f.`) y las preguntas enteras («¿qué les dejaremos?») son
    legítimas; `punk?`, `ambient.` o `swamp...` no."""
    if not tag.strip():
        return ["vacío"]
    issues = whitespace_issues(tag)
    if tag != tag.lower():
        issues.append("mayúsculas")
    t = tag.rstrip()
    if t.endswith("...") or re.search(r"[,;:]$", t):
        issues.append("puntuación final")
    elif t.endswith(".") and not re.search(r"(^|[\s.])[^\s.]\.$", t):
        issues.append("puntuación final")
    elif t.endswith("?") and "¿" not in t:
        issues.append("puntuación final")
    return issues


def title_has_artist_prefix(artist, title):
    """«WLDV - The end of man EP» con artist «WLDV»."""
    if " - " not in title:
        return False
    head = title.split(" - ", 1)[0]
    return bool(strong_key(head)) and strong_key(head) == strong_key(artist)


# ------------------------------------------------------------------
# Auditoría
# ------------------------------------------------------------------

def load_wave_index(files=None):
    """album_id -> etiqueta de oleada (YYYY-MM) para saber por dónde entró."""
    index = {}
    for path in (files if files is not None else CANDIDATE_FILES):
        m = re.search(r"candidates_(\d{4}-\d{2})", path.name)
        if not m:
            continue
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        rows = doc.get("candidates", []) if isinstance(doc, dict) else doc
        for row in rows:
            aid = row.get("album_id")
            if aid is not None and aid not in index:
                index[aid] = m.group(1)
    return index


class Category:
    def __init__(self, key, title, note=None, columns=None, count_label="filas"):
        self.key = key
        self.title = title
        self.note = note
        self.columns = columns or ["problema"]
        self.rows = []       # cada fila: (album, extra) con extra dict por columna
        self.count = 0
        self.count_label = count_label

    def add(self, album, **extra):
        self.count += 1
        self.rows.append((album, extra))

    def add_group(self, albums, **extra):
        """Un hallazgo que agrupa varias fichas (duplicados, variantes)."""
        self.count += 1
        self.rows.append((albums, extra))


def audit(data, wave_index=None, max_examples=MAX_EXAMPLES, today=None):
    """Devuelve el informe como estructura: {meta, categories, regression}."""
    albums = data["albums"]
    wave_index = wave_index or {}
    today = today or dt.date.today()
    cats = []

    def origin(album):
        return wave_index.get(album.get("album_id"), "orig.")

    # --- esquema -------------------------------------------------------
    c_schema = Category("esquema", "Campos fuera del esquema o con tipo incorrecto",
                        columns=["problema"])
    ids = collections.Counter()
    for a in albums:
        problems = []
        extra_keys = set(a) - set(SCHEMA)
        missing = set(SCHEMA) - set(a)
        if extra_keys:
            problems.append("campos extra: " + ", ".join(sorted(extra_keys)))
        if missing:
            problems.append("faltan: " + ", ".join(sorted(missing)))
        for field, types in SCHEMA.items():
            if field in a and not isinstance(a[field], types):
                problems.append(f"{field} es {type(a[field]).__name__}")
        if isinstance(a.get("tags"), list) and any(not isinstance(t, str) for t in a["tags"]):
            problems.append("tags con elementos no string")
        for field in ("artist", "title"):
            if isinstance(a.get(field), str) and not a[field].strip():
                problems.append(f"{field} vacío")
        if problems:
            c_schema.add(a, problema="; ".join(problems))
        ids[a.get("id")] += 1
    for dup_id, n in ids.items():
        if n > 1:
            c_schema.add({"id": dup_id, "album_id": None, "artist": "", "title": "", "url": None},
                         problema=f"id repetido ×{n}")
    top = []
    if set(data) != {"albums", "artists", "tags", "years"}:
        top.append("claves de primer nivel: " + ", ".join(sorted(data)))
    if data.get("artists") != sorted({a["artist"] for a in albums if isinstance(a.get("artist"), str)}):
        top.append("`artists` no coincide con los álbumes")
    if data.get("tags") != sorted({t for a in albums for t in a.get("tags", []) if isinstance(t, str)}):
        top.append("`tags` no coincide con los álbumes")
    if data.get("years") != sorted({a["year"] for a in albums if isinstance(a.get("year"), int)}):
        top.append("`years` no coincide con los álbumes")
    for msg in top:
        c_schema.add({"id": "—", "album_id": None, "artist": "", "title": "", "url": None},
                     problema="índice top-level: " + msg)
    cats.append(c_schema)

    # --- duplicados ----------------------------------------------------
    by_album_id = collections.defaultdict(list)
    by_url = collections.defaultdict(list)
    by_pair = collections.defaultdict(list)
    by_slug = collections.defaultdict(list)
    for a in albums:
        if a.get("album_id") is not None:
            by_album_id[a["album_id"]].append(a)
        key = normalize_url(a.get("url"))
        if key:
            by_url[key].append(a)
        by_pair[pair_key(a)].append(a)
        slug = url_slug(a.get("url"))
        if slug:
            by_slug[(strong_key(a["artist"]), slug)].append(a)

    c_dup_id = Category("dup_album_id", "Duplicados: mismo `album_id`",
                        count_label="grupos", columns=["album_id"])
    for aid, rows in sorted(by_album_id.items()):
        if len(rows) > 1:
            c_dup_id.add_group(rows, album_id=str(aid))
    cats.append(c_dup_id)

    c_dup_url = Category("dup_url", "Duplicados: misma URL normalizada",
                         note="Normalización: sin esquema, query ni fragmento, sin barra final, "
                              "todo en minúsculas.",
                         count_label="grupos", columns=["clave"])
    for key, rows in sorted(by_url.items()):
        if len(rows) > 1:
            c_dup_url.add_group(rows, clave=key)
    cats.append(c_dup_url)

    c_dup_pair = Category(
        "dup_artist_title", "Duplicados: mismo artista+título normalizados con distinta URL",
        note="Comparación sin acentos, sin mayúsculas ni puntuación. Suelen ser la edición "
             "del grupo y la del sello (o dos bandas homónimas): decisión humana.",
        count_label="grupos", columns=["cuentas"])
    for key, rows in sorted(by_pair.items()):
        urls = {normalize_url(r.get("url")) for r in rows}
        if len(rows) > 1 and len(urls) > 1:
            c_dup_pair.add_group(rows, cuentas=", ".join(sorted(filter(None, {account_of(r.get("url")) for r in rows}))))
    cats.append(c_dup_pair)

    pair_groups = {id(r) for rows in by_pair.values() if len(rows) > 1 for r in rows}
    c_slug = Category(
        "reedicion_slug", "Posibles reediciones: mismo artista y mismo slug de URL en otra cuenta",
        note="El título difiere (si no, ya estaría en la categoría anterior) pero el slug "
             "de Bandcamp es idéntico. Mirar si es el mismo disco.",
        count_label="grupos", columns=["slug"])
    for (akey, slug), rows in sorted(by_slug.items()):
        if len(rows) > 1 and len({account_of(r["url"]) for r in rows}) > 1 \
                and not all(id(r) in pair_groups for r in rows):
            c_slug.add_group(rows, slug=slug)
    cats.append(c_slug)

    # --- artistas ------------------------------------------------------
    artist_rows = collections.defaultdict(list)
    for a in albums:
        artist_rows[a["artist"]].append(a)
    groups = collections.defaultdict(dict)
    for name, rows in artist_rows.items():
        k = strong_key(name)
        if k:
            groups[k][name] = rows

    c_var = Category(
        "artist_variants", "Artistas: mismo nombre escrito de varias formas",
        note="Agrupado con clave fuerte (sin acentos, mayúsculas ni puntuación). Cada fila "
             "es un grupo; entre paréntesis, nº de fichas con esa grafía. Los nombres "
             "colaborativos («A & B» / «A, B») también caen aquí.",
        count_label="grupos", columns=["variantes"])
    for k, variants in sorted(groups.items()):
        if len(variants) > 1:
            label = ", ".join(f"`{n}` ({len(r)})" for n, r in
                              sorted(variants.items(), key=lambda kv: (-len(kv[1]), kv[0])))
            sample = [r[0] for r in variants.values()]
            c_var.add_group(sample, variantes=label)
    cats.append(c_var)

    c_case = Category(
        "artist_case", "Artistas: capitalización rara frente a otra grafía del catálogo",
        note="Nombre TODO EN MAYÚSCULAS o todo en minúsculas cuando el mismo nombre existe "
             "en el catálogo con mayúscula inicial. No se propone canónica: eso lo decide "
             "Miguel (ver `ARTIST_RENAMES` en pipeline.py para las 41 ya decididas).",
        columns=["estilo", "otras grafías"])
    for k, variants in sorted(groups.items()):
        if len(variants) < 2:
            continue
        styles = {n: case_style(n) for n in variants}
        if "mixta" not in styles.values():
            continue
        for name, style in sorted(styles.items()):
            if style in ("MAYÚSCULAS", "minúsculas"):
                others = ", ".join(f"`{n}` ({len(variants[n])})" for n in sorted(variants) if n != name)
                c_case.add(variants[name][0], estilo=f"{style} ({len(variants[name])} fichas)",
                           **{"otras grafías": others})
    cats.append(c_case)

    upper_only = sorted(n for n, rows in artist_rows.items()
                        if case_style(n) == "MAYÚSCULAS" and len(groups[strong_key(n)]) == 1)
    lower_only = sorted(n for n, rows in artist_rows.items()
                        if case_style(n) == "minúsculas" and len(groups[strong_key(n)]) == 1)
    c_style = Category(
        "artist_style", "Artistas solo en MAYÚSCULAS o solo en minúsculas (informativo)",
        note="Sin otra grafía en el catálogo: casi siempre es la estilización del propio "
             "grupo (COBRA, judy). Se listan solo los recuentos y una muestra; no es "
             "accionable sin mirar la página.",
        columns=["estilo"])
    for name in upper_only[:max_examples // 2]:
        c_style.add(artist_rows[name][0], estilo="MAYÚSCULAS")
    for name in lower_only[:max_examples // 2]:
        c_style.add(artist_rows[name][0], estilo="minúsculas")
    c_style.count = len(upper_only) + len(lower_only)
    c_style.summary = f"{len(upper_only)} en MAYÚSCULAS, {len(lower_only)} en minúsculas"
    cats.append(c_style)

    c_ws = Category("whitespace", "Artista o título con espacios sobrantes o puntuación colgante",
                    columns=["campo", "problema"])
    for a in albums:
        for field in ("artist", "title"):
            issues = whitespace_issues(a[field])
            if issues:
                c_ws.add(a, campo=field, problema=", ".join(issues))
    cats.append(c_ws)

    # --- genre / tags --------------------------------------------------
    c_genre_null = Category("genre_null", "`genre` null o vacío", columns=["tags (primeros 4)"])
    c_genre_vocab = Category("genre_vocab", "`genre` fuera del vocabulario", columns=["genre"])
    c_tags_empty = Category("tags_empty", "`tags` vacío", columns=["genre"])
    c_tags_dirty = Category("tags_dirty", "Tags sucios (vacíos, espacios, mayúsculas, puntuación colgante)",
                            columns=["tag", "problema"])
    for a in albums:
        if not a.get("genre"):
            c_genre_null.add(a, **{"tags (primeros 4)": ", ".join(a["tags"][:4]) or "—"})
        elif a["genre"] not in GENRE_VOCAB:
            c_genre_vocab.add(a, genre=a["genre"])
        if not a.get("tags"):
            c_tags_empty.add(a, genre=a.get("genre") or "null")
        for t in a.get("tags", []):
            if not isinstance(t, str):
                continue
            issues = tag_issues(t)
            if issues:
                c_tags_dirty.add(a, tag=t, problema=", ".join(issues))
    cats += [c_genre_null, c_genre_vocab, c_tags_empty, c_tags_dirty]

    tag_count = collections.Counter(t for a in albums for t in a.get("tags", []) if isinstance(t, str))
    tag_groups = collections.defaultdict(list)
    for t in tag_count:
        k = strong_key(t)
        if k:
            tag_groups[k].append(t)
    c_tag_var = Category(
        "tag_variants", "Tags: variantes del mismo tag no cubiertas por `TAG_RENAMES` (informativo)",
        note="Misma clave fuerte (sin acentos, espacios, guiones ni puntuación). El pipeline ya "
             "fusiona las variantes auditadas en la PR C; estas son las que quedan. Candidatas "
             "a `TAG_RENAMES`, pero la política de la PR C exige decidirlas una a una.",
        count_label="grupos", columns=["variantes"])
    for k, names in sorted(tag_groups.items()):
        if len(names) > 1:
            label = ", ".join(f"`{n}` ({tag_count[n]})" for n in sorted(names, key=lambda n: (-tag_count[n], n)))
            rarest = min(names, key=lambda n: (tag_count[n], n))
            example = min((a for a in albums if rarest in a.get("tags", [])), key=lambda a: a["id"])
            c_tag_var.add_group([example], variantes=label)
    cats.append(c_tag_var)

    # --- URLs ----------------------------------------------------------
    c_url = Category("url_dirty", "URLs sucias",
                     note="`dominio no bandcamp.com`: cuentas con dominio propio (crudobilbao.com, "
                          "ekiza.com…) ya verificadas como Bandcamp en auditorías anteriores; se listan "
                          "para que quede constancia, no como error.",
                     columns=["problema"])
    c_url_null = Category("url_null", "URL nula", columns=["album_id"])
    for a in albums:
        url = a.get("url")
        if url is None:
            c_url_null.add(a, album_id=str(a.get("album_id")))
            continue
        issues = url_issues(url)
        if issues:
            c_url.add(a, problema=", ".join(issues))
    cats += [c_url, c_url_null]

    # --- fechas / portadas ---------------------------------------------
    c_year_null = Category("year_null", "`year` vacío", columns=["genre"])
    c_year_bad = Category("year_bad", f"`year` imposible (< {YEAR_MIN} o > {today.year + 1})",
                          columns=["year"])
    c_cover = Category("cover_null", "Portada vacía (`cover_url` null)", columns=["album_id"])
    c_cover_dom = Category("cover_domain", "Portada fuera de bcbits.com", columns=["cover_url"])
    c_aid_null = Category("album_id_null", "`album_id` nulo", columns=["cover_url"])
    for a in albums:
        y = a.get("year")
        if y is None:
            c_year_null.add(a, genre=a.get("genre") or "null")
        elif isinstance(y, int) and not (YEAR_MIN <= y <= today.year + 1):
            c_year_bad.add(a, year=str(y))
        if not a.get("cover_url"):
            c_cover.add(a, album_id=str(a.get("album_id")))
        elif COVER_DOMAIN not in urlsplit(a["cover_url"]).netloc.lower():
            c_cover_dom.add(a, cover_url=a["cover_url"])
        if a.get("album_id") is None:
            c_aid_null.add(a, cover_url=str(a.get("cover_url")))
    cats += [c_year_null, c_year_bad, c_cover, c_cover_dom, c_aid_null]

    # --- títulos -------------------------------------------------------
    c_prefix = Category(
        "title_prefix", "Títulos con el artista como prefijo («Artista - Título»)",
        note="Patrón P4 del sondeo de títulos (PR #49), dejado fuera a propósito de "
             "fix_artist_from_title.py. Informativo: quitar el prefijo sería un arreglo "
             "mecánico, pero el título es el que el artista puso en Bandcamp.")
    for a in albums:
        if title_has_artist_prefix(a["artist"], a["title"]):
            c_prefix.add(a, problema=f"prefijo `{a['title'].split(' - ', 1)[0]} - `")
    cats.append(c_prefix)

    # --- regresión de lo ya resuelto -----------------------------------
    artists_now = {a["artist"] for a in albums}
    tags_now = {t for a in albums for t in a.get("tags", []) if isinstance(t, str)}
    regression = [
        ("`step_clean_urls` (cola `?from=…`)", sum(1 for a in albums if a.get("url") and "?" in a["url"])),
        ("`step_dedupe_releases` (35 filas auditadas)",
         sum(1 for dead_id in pipeline.RELEASE_DEDUPE if any(a["id"] == dead_id for a in albums))),
        ("`step_normalize_artist_names` (41 variantes)",
         len(artists_now & set(pipeline.ARTIST_RENAMES))),
        ("`step_clean_invisible_chars`",
         sum(1 for a in albums if any(c in INVISIBLE for c in a["artist"] + a["title"] + "".join(a["tags"])))),
        ("`step_normalize_tags` (`TAG_RENAMES` + `TAG_SPLITS`)",
         len(tags_now & (set(pipeline.TAG_RENAMES) | set(pipeline.TAG_SPLITS)))),
        ("tags repetidos dentro de una ficha",
         sum(1 for a in albums if len(set(a["tags"])) != len(a["tags"]))),
    ]

    waves = collections.Counter(wave_index.get(a.get("album_id"), "orig.") for a in albums)
    meta = {
        "date": today.isoformat(),
        "total": len(albums),
        "artists": len(artists_now),
        "tags": len(tags_now),
        "waves": dict(sorted(waves.items())),
        "max_examples": max_examples,
    }
    return {"meta": meta, "categories": cats, "regression": regression,
            "origin": origin}


# ------------------------------------------------------------------
# Render
# ------------------------------------------------------------------

def _cell(s):
    if s is None:
        return "—"
    s = str(s).replace("|", "\\|").replace("\n", " ")
    return s if len(s) <= 120 else s[:117] + "…"


def _url_cell(url):
    return f"[↗]({url})" if url else "—"


def render_markdown(report):
    meta, cats = report["meta"], report["categories"]
    origin = report["origin"]
    out = []
    out.append(f"# Auditoría de calidad del canónico — {meta['date']}")
    out.append("")
    out.append("*Generado por `python3 scripts/quality_audit.py`. Solo lectura: este informe "
               "no cambia datos. No editar a mano; regenerar.*")
    out.append("")
    waves = ", ".join(f"{k}: {v}" for k, v in meta["waves"].items())
    out.append(f"Canónico: **{meta['total']}** fichas, {meta['artists']} artistas, "
               f"{meta['tags']} tags. Procedencia por `album_id` ({waves}); "
               "«orig.» = catálogo anterior a julio o sin `album_id` en ninguna oleada.")
    out.append("")
    out.append("## Cómo leerlo")
    out.append("")
    out.append("- Cada categoría trae su recuento total y una tabla con como mucho "
               f"{meta['max_examples']} ejemplos (ordenados por `id`).")
    out.append("- `origen` dice por qué oleada de candidatos entró la ficha (2026-07/08/09) "
               "o si es del catálogo original.")
    out.append("- Nada de esto se ha corregido. Lo mecánico y claro va a reglas en "
               "`scripts/pipeline.py` (fase 2); lo de artistas lo decide Miguel.")
    out.append("")

    out.append("## Ya resuelto por el pipeline (comprobación de regresión)")
    out.append("")
    out.append("Lo que `scripts/pipeline.py` corrigió en PRs anteriores no se vuelve a auditar; "
               "solo se comprueba que sigue a cero.")
    out.append("")
    out.append("| Paso | Restos hoy |")
    out.append("|---|---:|")
    for label, n in report["regression"]:
        flag = "" if n == 0 else " ⚠️"
        out.append(f"| {label} | {n}{flag} |")
    out.append("")

    out.append("## Resumen")
    out.append("")
    out.append("| Categoría | Recuento |")
    out.append("|---|---:|")
    for c in cats:
        summary = getattr(c, "summary", None)
        n = summary or (f"{c.count} {c.count_label}" if c.count else "0")
        out.append(f"| [{c.title}](#{c.key}) | {n} |")
    out.append("")

    for c in cats:
        out.append(f'<a id="{c.key}"></a>')
        out.append(f"## {c.title}")
        out.append("")
        summary = getattr(c, "summary", None)
        out.append(f"**Recuento: {summary or f'{c.count} {c.count_label}'}.**")
        if c.note:
            out.append("")
            out.append(c.note)
        out.append("")
        if not c.rows:
            out.append("Sin casos.")
            out.append("")
            continue
        grouped = isinstance(c.rows[0][0], list)
        rows = sorted(c.rows, key=lambda r: _sort_key(r[0]))
        shown = rows[:meta["max_examples"]]
        head = ["id", "album_id", "origen", "artista", "título"] + c.columns + ["url"]
        out.append("| " + " | ".join(head) + " |")
        out.append("|" + "|".join("---" for _ in head) + "|")
        for subject, extra in shown:
            members = subject if grouped else [subject]
            for i, a in enumerate(members):
                extras = [_cell(extra.get(col)) if i == 0 else "″" for col in c.columns]
                cells = [_cell(a.get("id")), _cell(a.get("album_id")), origin(a),
                         _cell(a.get("artist")), _cell(a.get("title"))] + extras + [_url_cell(a.get("url"))]
                out.append("| " + " | ".join(cells) + " |")
        if len(rows) > len(shown):
            out.append("")
            out.append(f"*… y {len(rows) - len(shown)} más (solo se muestran "
                       f"{meta['max_examples']}).*")
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def _sort_key(subject):
    a = subject[0] if isinstance(subject, list) else subject
    i = a.get("id")
    return (0, i) if isinstance(i, int) else (1, str(i))


# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--data", type=Path, default=DATA_FILE, help="canónico a auditar")
    parser.add_argument("--out", type=Path, default=None,
                        help="ruta del informe (por defecto docs/quality-audit-YYYY-MM.md)")
    parser.add_argument("--stdout", action="store_true", help="imprime el informe en vez de escribirlo")
    parser.add_argument("--max-examples", type=int, default=MAX_EXAMPLES)
    args = parser.parse_args(argv)

    data = json.loads(args.data.read_text(encoding="utf-8"))
    today = dt.date.today()
    report = audit(data, wave_index=load_wave_index(), max_examples=args.max_examples, today=today)
    text = render_markdown(report)

    if args.stdout:
        sys.stdout.write(text)
        return 0
    out = args.out or DOCS_DIR / f"quality-audit-{today:%Y-%m}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"informe escrito en {out.relative_to(REPO_ROOT) if out.is_relative_to(REPO_ROOT) else out}")
    for c in report["categories"]:
        print(f"  · {c.title}: {getattr(c, 'summary', None) or c.count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
