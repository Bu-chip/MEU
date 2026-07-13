#!/usr/bin/env python3
"""Incorporación al canónico de los candidatos del PR #23 (candidates/2026-07).

Ejecuta las decisiones de la revisión del PR #23 (criterio maximalista,
julio 2026). Lee el JSON de candidatos (5.483 filas), clasifica cada una
y muta data/bandcamp_bilbaotags_clean.json + data/rejected.json:

  1. Casi-duplicados contra el canónico (mismo artista+título, distinto
     album_id): gana la edición del GRUPO. Si el candidato es la edición
     del grupo y el canónico tenía la del sello, la ficha canónica adopta
     url/album_id/cover_url del candidato y la URL del sello va a
     rejected.json; si el canónico ya tenía la del grupo, el candidato
     (edición de sello) va a rejected.json.
  2. URL_FIXES: fichas del canónico cuya URL apuntaba a OTRO álbum
     (corrupción de scraping anotada en el backlog de pipeline.py:
     Inigo Lunani LNI01-06, h.101, MotorSex, ELBIS REVER, txopet, más
     la serie II de iikrisgm, AT, Nø Name y TheDaltonics). Adoptan la
     URL correcta que trae el candidato. Cerrojo: solo si la URL actual
     coincide byte a byte con la esperada.
  3. Homónimos extranjeros en el canónico (Heisenberg NY, HUMANO EC):
     el candidato vasco entra como ficha nueva; la ficha vieja queda
     anotada en data/revision_2026-07.json. Meridian y Crossover quedan
     RETENIDOS (ni entran ni a rejected) hasta revisar el catálogo viejo.
  4. Geografía: ubicación fuera de Euskal Herria NO descarta. Caen solo
     los sin ningún vínculo vasco detectable (tag local, tag en euskera,
     nombre/título en euskera, artista ya en el canónico, misma página o
     artista que otro candidato aceptado, o rescate manual auditado).
  5. Dedupe interno grupo/sello entre candidatos: entra una edición por
     disco (la del grupo si es identificable; si no, la de mejor
     coincidencia título<->slug, anotada en revision_2026-07.json).
  6. El resto entra como ficha nueva: ids correlativos desde max(id)+1,
     genre derivado de los tags contra el vocabulario existente del
     canónico (nada inventado; sin señal -> null), y solo los 9 campos
     del esquema (band_location/source_tags/discovered_at se descartan).

El fichero de candidatos NO está en main (viaja en la rama del PR #23),
por eso la ruta se pasa como argumento. Tras este script debe ejecutarse
scripts/pipeline.py para normalizar los datos nuevos (tags, artistas,
invisibles) y dejar el canónico idempotente.

Uso:
    python3 scripts/merge_candidates_2026_07.py RUTA/candidates_2026-07.json
"""

import collections
import json
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from pipeline import DATA_FILE, serialize, validate  # noqa: E402

REJECTED_FILE = REPO_ROOT / "data" / "rejected.json"
REVISION_FILE = REPO_ROOT / "data" / "revision_2026-07.json"
DECISION_DATE = "2026-07-13"
CANDIDATES_PR = 23

# ------------------------------------------------------------------
# Decisiones manuales de la revisión (auditadas en el PR de merge)
# ------------------------------------------------------------------

# Fichas del canónico con URL corrupta (apuntaba a otro álbum). El
# candidato trae la URL real. id -> (url_corrupta_esperada = cerrojo,
# url_correcta_del_candidato). Incluye los grupos anotados como backlog
# en el comentario de RELEASE_DEDUPE de pipeline.py.
URL_FIXES = {
    1543: ("https://inigolunani.bandcamp.com/album/lni05", "https://inigolunani.bandcamp.com/album/lni01"),
    1541: ("https://inigolunani.bandcamp.com/album/lni05", "https://inigolunani.bandcamp.com/album/lni02"),
    1540: ("https://inigolunani.bandcamp.com/album/lni05", "https://inigolunani.bandcamp.com/album/lni03"),
    1533: ("https://inigolunani.bandcamp.com/album/lni05", "https://inigolunani.bandcamp.com/album/lni04"),
    263: ("https://inigolunani.bandcamp.com/album/lni05", "https://inigolunani.bandcamp.com/album/lni06-2"),
    1942: ("https://h101.bandcamp.com/album/101001", "https://h101.bandcamp.com/album/1010001"),
    1945: ("https://h101.bandcamp.com/album/101001", "https://h101.bandcamp.com/album/10101"),
    2300: ("https://motorsex.bandcamp.com/album/single-iii", "https://motorsex.bandcamp.com/album/single-vii"),
    1751: ("https://elbisrever.bandcamp.com/album/holaaa-2", "https://elbisrever.bandcamp.com/album/holaaa"),
    1507: ("https://txopet.bandcamp.com/album/ostabe-zuloan-remixak", "https://txopet.bandcamp.com/album/ostabe-zuloan"),
    16: ("https://bloxhamtapes.bandcamp.com/album/man-is-an-insect", "https://atatatat.bandcamp.com/album/at"),
    2173: ("https://martinikulture.bandcamp.com/album/god-killing-himself-volume-ii-paper-metal", "https://iikrisgm.bandcamp.com/album/--3"),
    1243: ("https://boniver.bandcamp.com/album/i-i", "https://iikrisgm.bandcamp.com/album/i"),
    2124: ("https://cameronwilson.bandcamp.com/album/ii-i-iv", "https://iikrisgm.bandcamp.com/album/i-iv"),
    2190: ("https://ongoingbox.bandcamp.com/album/hsob086-vv-ii-ss-ii-oo-nn-i-wait-in-the-darkness", "https://iikrisgm.bandcamp.com/album/oo"),
    2050: ("https://x-img.bandcamp.com/album/self-aware-ii-x-img04", "https://iikrisgm.bandcamp.com/album/x"),
    2257: ("https://sigloxx.bandcamp.com/album/dreams-of-pleasure-ii", "https://iikrisgm.bandcamp.com/album/x-x"),
    2153: ("https://irixx.bandcamp.com/album/etudes-ii", "https://iikrisgm.bandcamp.com/album/xx"),
    2106: ("https://andybeatz.bandcamp.com/album/couleurs-ii", "https://iikrisgm.bandcamp.com/album/y"),
    2306: ("https://noname-music.bandcamp.com/album/noname", "https://n0name.bandcamp.com/album/n-name"),
    882: ("https://thedaltonics.bandcamp.com/album/3", "https://thedaltonics.bandcamp.com/album/the-daltonics"),
}

# Homónimos extranjeros en el canónico: el candidato vasco entra como
# ficha NUEVA y la ficha canónica vieja queda anotada para revisión.
# id_canónico -> url_del_candidato_que_entra.
HOMONIMOS_ENTRA = {
    1205: "https://heisenbergbilbo.bandcamp.com/album/heisenberg",
    2292: "https://humanorock.bandcamp.com/album/humano",
}

# Candidatos retenidos (ni entran ni a rejected): su ficha canónica
# homónima está pendiente de revisión manual. url_candidato -> id_canon.
RETENIDOS = {
    "https://meridianrockband.bandcamp.com/album/meridian": 2095,
    "https://crossoverbilbao.bandcamp.com/album/crossover-2": 1464,
}

# Fichas del canónico sospechosas de ser álbumes extranjeros colados
# (homónimos), para revisar el catálogo viejo otro día.
CANON_SOSPECHOSOS = {
    1205: "heisenbergny.bandcamp.com — ¿Heisenberg de New York?",
    2292: "humano-ec.bandcamp.com — ¿HUMANO de Ecuador? (además la URL apunta a 'danza', no a 'HUMANO')",
    2095: "meridianbandaus.bandcamp.com — ¿Meridian de Australia?",
    1464: "crossover-darkbeat.bandcamp.com — URL apunta a 'fantasmo', ni siquiera coincide el título",
}

# Rescates manuales de la lista de geografía (vínculo vasco real
# auditado a mano): entran aunque las señales automáticas no los vean.
GEO_RESCATES = {
    "Niamh Ní Charra - Ibon Koteron - Gavin Ralston": "colaboración con Ibon Koteron, albokari bilbaíno",
    "Ialma, Manu Sabaté, Iñaki Plaza, Ciscu Cardona, Nicolas Scalliet": "proyecto Gaizca con Iñaki Plaza",
}

# Conocimiento de escena para la clasificación geográfica (artistas
# vascos con ubicación falsa/extranjera en Bandcamp).
CONOCIDOS_VASCOS = {
    "elffor": "black metal de Basauri (proyecto de Numen)",
    "tzesne": "noise donostiarra",
    "nakkiga / kult et morte / stormstone / dilaghran": "Nakkiga es black metal navarro",
    "delirium tremens": "banda histórica del Rock Radical Vasco",
    "bea asurmendi": "apellido vasco + basque music",
    "joseba irazoki": "guitarrista de Bera (Nafarroa)",
}

# ------------------------------------------------------------------
# Utilidades de normalización
# ------------------------------------------------------------------

def unacc(s):
    return "".join(c for c in unicodedata.normalize("NFD", str(s))
                   if unicodedata.category(c) != "Mn")


def cf(s):
    return unacc(s).casefold().strip()


def pair_key(row):
    """Clave de casi-duplicado: artista+título exactos (casefold)."""
    return (str(row["artist"]).casefold().strip(),
            str(row["title"]).casefold().strip())


def normalize_url(url):
    """Misma clave que discover_tags.py / rejected.json."""
    if not url:
        return None
    u = urlparse(url.split("?", 1)[0].split("#", 1)[0])
    return f"{u.netloc.lower()}{u.path.rstrip('/')}"


def subdomain(url):
    m = re.match(r"https?://([^.]+)\.", url or "")
    return m.group(1) if m else ""


def normid(s):
    return re.sub(r"[^a-z0-9]", "", cf(s))


def is_band_page(artist, url):
    """¿El subdominio de Bandcamp es el del propio grupo?"""
    a, s = normid(artist), normid(subdomain(url))
    return bool(a and s) and (a == s or (len(a) >= 4 and (a in s or s in a)))


def slug_similarity(title, url):
    t = set(re.findall(r"[a-z0-9]+", cf(title)))
    u = set(re.findall(r"[a-z0-9]+", (url or "").rsplit("/album/", 1)[-1]))
    return len(t & u) / len(t) if t else 0.0


# ------------------------------------------------------------------
# Clasificación geográfica (criterio maximalista)
# ------------------------------------------------------------------

# Ciudades de España/Francia fuera de EH detectadas en la tanda: entran
# igualmente (diáspora); solo se listan para separarlas del resto de
# "extranjero", que sí exige señal de vínculo vasco.
NONBASQUE_ES = {
    "madrid", "barcelona", "zaragoza", "la linea de la concepcion", "seville",
    "sevilla", "burgos", "valencia", "santander", "logrono", "girona",
    "el bierzo", "talavera de la reina", "vigo", "oviedo", "alicante",
    "principado de asturias", "asturias", "salamanca", "murcia", "nigran",
    "el mas de flors", "pratdip", "castellon de la plana", "toreno", "pinto",
    "la frontera", "nc",
}
NONBASQUE_FR = {
    "paris", "occitanie", "toulouse", "nantes", "nice", "pau", "angers",
    "lille", "tours", "brittany",
}

TOWN_PAT = re.compile(
    r"bilbao|bilbo\b|donosti|gasteiz|irun\b|iruna|irunea|pamplona|navarra|"
    r"nafarroa|bizkaia|vizcaya|gipuzkoa|guipuzcoa|araba\b|alava|zumaia|tolosa|"
    r"guernica|gernika|bermeo|zarautz|barakaldo|lekeitio|getaria|urretxu|"
    r"zumarraga|llodio|laudio|hondarribia|errenteria|ondarroa|eibar|hernani|"
    r"baztan|getxo|santurtzi|portugalete|basauri|mungia|azpeitia|azkoitia|"
    r"onati|arrasate|bergara|antzuola|euskal herria|pais vasco|san sebastian")
EUSK_TAG = re.compile(r"euskar|euskal|eusker|euzkadi|bertso|euskaldun")
# Tags genéricos que por sí solos NO bastan (criterio del PR #23: un
# 'basque' de pasada no convierte a una banda extranjera en vasca).
GENERIC_ONLY = {"basque", "basque country", "basque music", "basque rock",
                "basque folk", "euskadi"}
EUSK_LEX = set(
    "gizon berria guda bakartia hodei eutsi aterpe egun beltzak urdangak "
    "mendeku diskak ttun gau gaua herri herria bihotz zuri beltz gorri itsaso "
    "lur sua ura amets kanta abesti bizi maite gure zure berri zahar izar "
    "haize euri elur mendi baso hitz argi ilun urte agur kaixo txiki handi".split())


def geo_zone(row):
    """'eh' (o ambiguo, entra directo), 'diaspora' (entra) o 'ext'."""
    loc = (row["band_location"] or "").strip()
    if not loc:
        return "eh"
    parts = [p.strip() for p in loc.split(",")]
    country = parts[-1]
    if country in ("PV", "Donostia"):
        return "eh"
    city = cf(", ".join(parts[:-1]))
    if country == "Spain":
        return "diaspora" if city in NONBASQUE_ES else "eh"
    if country == "France":
        return "diaspora" if city in NONBASQUE_FR else "eh"
    return "ext"


def basque_signals(row, canon_artists, canon_artists_long, eh_artists):
    """Señales de vínculo vasco para candidatos con ubicación extranjera."""
    sig = []
    tags = [cf(t).replace("-", " ") for t in row["tags"]]
    for t in tags:
        if t not in GENERIC_ONLY and TOWN_PAT.search(t):
            sig.append(f"tag local: {t}")
            break
    for t in tags:
        if t not in GENERIC_ONLY and EUSK_TAG.search(t):
            sig.append(f"tag euskera: {t}")
            break
    artist = cf(row["artist"])
    if set(re.findall(r"[a-z]+", artist)) & EUSK_LEX:
        sig.append("nombre en euskera")
    if len(set(re.findall(r"[a-z]+", cf(row["title"]))) & EUSK_LEX) >= 2:
        sig.append("título en euskera")
    if artist in canon_artists:
        sig.append("artista ya en el canónico")
    elif any(x in artist for x in canon_artists_long):
        sig.append("contiene artista del canónico")
    if artist in CONOCIDOS_VASCOS:
        sig.append(f"conocido: {CONOCIDOS_VASCOS[artist]}")
    if artist in eh_artists:
        sig.append("mismo artista con ubicación EH en otra fila")
    # cf() a ambos lados: el scraping trae acentos en forma NFD y una
    # comparación exacta fallaría según cómo esté escrito este fichero.
    rescate = {cf(k): v for k, v in GEO_RESCATES.items()}.get(artist)
    if rescate:
        sig.append(f"rescate manual: {rescate}")
    return sig


# ------------------------------------------------------------------
# Derivación de genre desde los tags
# ------------------------------------------------------------------

# Vocabulario = los géneros que YA usa el canónico. Orden por
# especificidad: un "hardcore punk, rock" debe dar punk, no rock.
GENRE_RULES = [
    ("punk", r"\bpunk|hardcore|oi!|crust|d-beat|screamo|emoviolence|ska punk"),
    ("metal", r"metal|doom|sludge|stoner|grindcore|deathcore"),
    ("hip-hop/rap", r"hip.?hop|rap\b|trap\b|beats"),
    ("reggae", r"reggae|dub\b|dancehall|ska\b|rocksteady|sound system"),
    ("electronic", r"electroni|techno|house\b|idm|synth|breakcore|jungle|"
                   r"drum ?& ?bass|edm|electro\b|dubstep|vaporwave|"
                   r"witch house|darkwave|coldwave|chillwave"),
    ("folk", r"\bfolk|americana|bluegrass|country folk|bertso"),
    ("jazz", r"jazz"),
    ("blues", r"blues"),
    ("ambient", r"ambient|drone|dungeon synth"),
    ("experimental", r"experimental|noise|improv|avant|musique concr|"
                     r"sound art|field record"),
    ("funk", r"funk"),
    ("latin", r"latin|salsa|cumbia|ranchera"),
    ("world", r"world|klezmer|balkan"),
    ("acoustic", r"acoustic|singer.songwriter|cantautor"),
    ("soundtrack", r"soundtrack|\bost\b|film music|score"),
    ("pop", r"\bpop\b|indie pop|synthpop|electropop|dream pop"),
    ("rock", r"rock|garage|surf|shoegaze|post-punk|grunge"),
    ("alternative", r"alternative|indie|emo\b"),
    ("spoken word", r"spoken word"),
    ("comedy", r"comedy"),
    ("kids", r"kids|children"),
]
GENRE_RULES = [(g, re.compile(p)) for g, p in GENRE_RULES]


def derive_genre(row):
    tags = [cf(t) for t in row["tags"]]
    for genre, pat in GENRE_RULES:
        for t in tags:
            if pat.search(t):
                return genre
    return None


# ------------------------------------------------------------------
# Merge
# ------------------------------------------------------------------

def build_ficha(row, new_id):
    return {
        "id": new_id,
        "artist": row["artist"],
        "title": row["title"],
        "genre": derive_genre(row),
        "year": row["year"],
        "tags": list(row["tags"]),
        "url": row["url"],
        "cover_url": row["cover_url"],
        "album_id": row["album_id"],
    }


def main():
    if len(sys.argv) != 2:
        sys.exit("uso: merge_candidates_2026_07.py RUTA/candidates_2026-07.json")
    cand_rows = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["candidates"]

    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    albums = data["albums"]
    by_id = {a["id"]: a for a in albums}
    canon_by_key = collections.defaultdict(list)
    for a in albums:
        canon_by_key[pair_key(a)].append(a)
    canon_artists = {cf(a["artist"]) for a in albums}
    canon_artists_long = [a for a in canon_artists if len(a) >= 8]
    urlfix_by_cand = {cand: (cid, lock) for cid, (lock, cand) in URL_FIXES.items()}
    homonimo_urls = set(HOMONIMOS_ENTRA.values())

    rejected_new = {}   # url_normalizada -> {reason, date, pr}
    revision = {"sello_vs_sello": [], "internos_ambiguos": [],
                "urls_desplazadas": [], "retenidos_homonimo": []}
    stats = collections.Counter()

    def reject(url, reason):
        key = normalize_url(url)
        assert key not in rejected_new, f"clave rejected duplicada: {key}"
        rejected_new[key] = {"reason": reason, "date": DECISION_DATE,
                             "pr": CANDIDATES_PR}

    # --- 1. candidatos que casan con una ficha del canónico -----------
    to_incorporate = []   # filas que acaban siendo ficha nueva
    pool = []             # filas que siguen al dedupe interno
    for row in cand_rows:
        if row["url"] in urlfix_by_cand:
            cid, lock = urlfix_by_cand[row["url"]]
            canon = by_id[cid]
            assert canon["url"] == lock, \
                f"cerrojo URL_FIXES roto en id {cid}: {canon['url']!r}"
            revision["urls_desplazadas"].append(
                {"canon_id": cid, "url_corrupta": canon["url"],
                 "url_correcta": row["url"]})
            canon["url"] = row["url"]
            canon["album_id"] = row["album_id"]
            canon["cover_url"] = row["cover_url"]
            stats["url_corrupta_corregida"] += 1
            continue
        if row["url"] in homonimo_urls:
            to_incorporate.append((row, "homónimo: ficha vasca nueva"))
            stats["homonimo_entra"] += 1
            continue
        if row["url"] in RETENIDOS:
            revision["retenidos_homonimo"].append(
                {"candidato_url": row["url"], "artist": row["artist"],
                 "title": row["title"], "canon_id": RETENIDOS[row["url"]],
                 "nota": "retenido hasta revisar el homónimo del canónico"})
            stats["retenido"] += 1
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
                # gana el grupo: el canónico adopta la edición del grupo
                # y la URL del sello queda apuntada en rejected.json
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
                # sello vs sello: el disco ya está, no entra duplicado
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

    # --- 2. geografía --------------------------------------------------
    # Las señales y su propagación se calculan sobre TODOS los candidatos
    # (una fila consumida por el dedupe sigue siendo evidencia de que su
    # página/artista es vasco); el descarte solo se aplica al pool.
    eh_artists = {cf(r["artist"]) for r in cand_rows if geo_zone(r) != "ext"}
    eh_subs = {subdomain(r["url"]) for r in cand_rows if geo_zone(r) != "ext"}
    ext_rows = [r for r in cand_rows if geo_zone(r) == "ext"]
    signals = {id(r): basque_signals(r, canon_artists, canon_artists_long,
                                     eh_artists) for r in ext_rows}
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
    geo_out = {id(r) for r in ext_rows
               if not signals[id(r)] and id(r) in pool_ids}
    for r in ext_rows:
        if id(r) in geo_out:
            reject(r["url"],
                   f"sin vínculo vasco detectable (tag genérico de pasada); "
                   f"ubicación: {r['band_location']}")
            stats["geografia_descartada"] += 1
    pool = [r for r in pool if id(r) not in geo_out]

    # --- 3. dedupe interno grupo/sello ----------------------------------
    groups = collections.defaultdict(list)
    for r in pool:
        groups[pair_key(r)].append(r)
    for rows in groups.values():
        if len(rows) == 1:
            to_incorporate.append((rows[0], None))
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
        to_incorporate.append((chosen, None))
        for r in rows:
            if r is not chosen:
                reject(r["url"],
                       f"edición duplicada del mismo disco; entra {chosen['url']}")
                stats["edicion_interna_descartada"] += 1

    # --- 4. incorporación ------------------------------------------------
    seen_keys = {pair_key(a) for a in albums}
    next_id = max(a["id"] for a in albums) + 1
    for row, _nota in to_incorporate:
        k = pair_key(row)
        assert k not in seen_keys or row["url"] in homonimo_urls, \
            f"duplicado inesperado al incorporar: {k}"
        seen_keys.add(k)
        albums.append(build_ficha(row, next_id))
        next_id += 1
        stats["ficha_nueva"] += 1

    # --- 5. listas top-level, validación y escritura ----------------------
    data["artists"] = sorted({a["artist"] for a in albums})
    data["tags"] = sorted({t for a in albums for t in a["tags"]})
    data["years"] = sorted({a["year"] for a in albums if a["year"] is not None})

    album_ids = [a["album_id"] for a in albums if a["album_id"] is not None]
    assert len(album_ids) == len(set(album_ids)), "album_id duplicado tras el merge"
    ids = [a["id"] for a in albums]
    assert len(ids) == len(set(ids)), "id duplicado tras el merge"
    validate(data)

    rej = json.loads(REJECTED_FILE.read_text(encoding="utf-8"))
    overlap = set(rej["rejected"]) & set(rejected_new)
    assert not overlap, f"claves ya presentes en rejected.json: {overlap}"
    rej["rejected"].update(dict(sorted(rejected_new.items())))
    REJECTED_FILE.write_text(
        json.dumps(rej, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")

    revision_doc = {
        "meta": {
            "que_es": "Pendientes de revisión manual tras el merge de "
                      "candidates/2026-07 (PR #23). No bloquean el canónico.",
            "date": DECISION_DATE,
            "canon_sospechosos_homonimos": [
                {"canon_id": cid, "nota": nota, "url": by_id[cid]["url"]}
                for cid, nota in sorted(CANON_SOSPECHOSOS.items())],
        },
        **revision,
    }
    REVISION_FILE.write_text(
        json.dumps(revision_doc, indent=4, ensure_ascii=False) + "\n",
        encoding="utf-8")

    DATA_FILE.write_text(serialize(data), encoding="utf-8")

    # cuadre: cada fila de candidatos acaba en exactamente un destino.
    # homonimo_entra e interno_ambiguo_grupo son sub-métricas de
    # ficha_nueva, no destinos propios.
    total = sum(v for k, v in stats.items()
                if k not in ("homonimo_entra", "interno_ambiguo_grupo"))
    print(f"candidatos procesados: {total} (de {len(cand_rows)})")
    for k, v in sorted(stats.items()):
        print(f"  · {k}: {v}")
    print(f"canónico: {len(albums)} álbumes, {len(data['artists'])} artistas, "
          f"{len(data['tags'])} tags")
    print(f"rejected.json: +{len(rejected_new)} entradas")
    assert total == len(cand_rows), "cuadre roto: hay filas sin clasificar"


if __name__ == "__main__":
    main()
