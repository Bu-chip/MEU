#!/usr/bin/env python3
"""Pipeline de saneamiento de datos — MEU / Bilbao Underground.

data/bandcamp_bilbaotags_clean.json es la FUENTE DE VERDAD: el CSV
original del scraping no está versionado, así que el pipeline lee el
JSON, lo transforma in situ y lo reescribe con el mismo formato
(indent=4, UTF-8 sin escapar, sin newline final). Nunca asume que el
dataset sea regenerable desde otro sitio.

Uso:
    python3 scripts/pipeline.py            # aplica los pasos y reescribe el JSON
    python3 scripts/pipeline.py --dry-run  # informa de lo que cambiaría, sin escribir

Cada paso es una función step(data) -> list[str] que muta `data` (el
dict completo {albums, artists, tags, years}) y devuelve una lista de
mensajes describiendo lo que ha cambiado (vacía si no tocó nada).
Todos los pasos deben ser IDEMPOTENTES: ejecutar el pipeline sobre su
propia salida no puede producir ningún cambio. `--dry-run` sobre un
dataset ya saneado debe informar "0 cambios".

Para añadir un paso nuevo (previstos: géneros corruptos, dedupe de
URLs repetidas, normalización de tags y artistas): definir la función
y añadirla a STEPS en el orden en que deba ejecutarse.
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = REPO_ROOT / "data" / "bandcamp_bilbaotags_clean.json"


# ------------------------------------------------------------------
# Pasos del pipeline
# ------------------------------------------------------------------

def step_clean_urls(data):
    """Elimina los parámetros de tracking de búsqueda de las URLs.

    El scraping guardó cada URL con la cola `?from=search&search_sig=...`
    de Bandcamp, que no aporta nada y engorda el archivo. Se corta la URL
    en el primer `?`. Las URLs nulas se dejan tal cual.
    """
    changes = []
    cleaned = 0
    for album in data["albums"]:
        url = album.get("url")
        if url and "?" in url:
            album["url"] = url.split("?", 1)[0]
            cleaned += 1
    if cleaned:
        changes.append(f"clean_urls: {cleaned} URLs limpiadas de parámetros de tracking")
    return changes


# Correcciones de géneros corruptos, auditadas a mano (PR A de limpieza).
#
# Mecanismo de la corrupción: en 39 filas del CSV original la celda
# `genre` tomó el TÍTULO de la fila siguiente (verificado: en las 38
# comprobables genre[i] == title[i+1]; la nº 39 es el último registro
# y su "fila siguiente" quedó fuera del dataset). El género real se
# perdió, así que cada corrección se dedujo de los datos locales:
# otros releases del mismo artista y/o co-ocurrencia tags→género en el
# resto del catálogo. Donde no había señal fiable, None (misma
# convención que `year`; el frontend lo pinta como '?').
#
# Formato: id -> (genre_corrupto_esperado, genre_corregido). El valor
# esperado actúa de cerrojo: si la celda ya no contiene exactamente el
# valor corrupto, el paso no toca nada (idempotencia y protección
# frente a ediciones posteriores).
GENRE_FIXES = {
    38: ("ER052 Intensidades Ortega - Deseo", "electronic"),   # tag techno
    43: ("Gurs", None),                                        # sin señal
    49: ("Full Cab", "folk"),                                  # tags folk / euskal kantagintza
    85: ("Decadence & Renaissance", None),                     # sin señal
    89: ("Zeru Freq.", "electronic"),                          # tags electronica / new beat / proto techno
    103: ("300 noches sin dormir", "electronic"),              # proyecto Inshore (id 128)
    107: ("Endinghent", "rock"),                               # otro release de izena (id 1608)
    128: ("The Anthropodermic Manuscript of Retribution", "electronic"),  # tags deephouse / minimal
    130: ("Full Moon in Scorpio", "experimental"),             # tag experimental + Mikel Vega 4x experimental
    170: ("Total Necro D-Beat Desecration", "rock"),           # tags rock'n'roll / power pop / pub rock
    177: ('7" Enlightenment', None),                           # sin señal
    199: ("michael valentine west - multi-surface function | polygon network [NW0059]", "punk"),  # tags punk / punk rock
    228: ("Amalur", "rock"),                                   # otro release rock + tags rock & roll
    234: ("Sucias lenguas", None),                             # sin señal
    237: ("panopticum - multisensory metaphors | polygon network [NW0063]", "acoustic"),  # tag acoustic
    254: ("Izei [Album]", None),                               # sin señal
    271: ("Incandescent World", "rock"),                       # NIZE (ids 472, 550) = rock + tag rock
    321: ("Pale Dream", "ambient"),                            # Zabala 4x ambient
    333: ('12" Earl Zero, Bass Lee, Kenny Knotts, Roberto Sánchez - Fire In The City / Love & Glory', "punk"),  # tags punk / afterpunk
    359: ("Demo MMXX", "rock"),                                # otro release del artista (id 896) = rock
    361: ("Inertzia", None),                                   # sin señal
    372: ("Doctrines of the Temple of the Moon", "electronic"),  # mismo artista que id 38
    457: ("Mapa eta lurraldea", None),                         # sin señal
    468: ("vortex count - eleven | polygon network [NW0054]", None),  # sin señal
    497: ("decomposed elements fragance - tokyo 2022 | polygon network [NW0052]", None),  # sin señal
    577: ("Glory To The King LP", "punk"),                     # tags punk / pop, co-ocurrencia favorece punk
    679: ("IRAULTZA GARA", None),                              # sin señal
    791: ("Let There Be Darkness (Demo'MMXVII)", "kids"),      # los 5 releases de VULK son kids + tag kids
    825: ("Visones", "alternative"),                           # tag alternative
    840: ("Is That Wet or Just Cold?", "soundtrack"),          # título (Soundtrack) + tag film soundtrack
    895: ("Dr. Maha's Miracle Tonic", "rock"),                 # tag rock cinematográfico
    952: ("Neguaren Ostean", None),                            # sin señal
    1380: ("They Took Democracy and Threw It onto the Pyre with the Rest of the Legion of Swine", "funk"),  # 6 releases funk
    1421: ("European Core #3", "funk"),                        # 6 releases funk
    2081: ("European-Core #2", "experimental"),                # tags noise / ruido / acousmatic
    2385: ("La Linea De Fuego", "experimental"),               # tags experimental + noise
    2386: ("LA SEÑAL EP", "punk"),                             # tag hardcore (contexto HC punk)
    2387: ("Demo 2010", "rock"),                               # tags rock x2 / spanish rock
    2395: ("Aberrato Ictus EP", "experimental"),               # tags noise / ruido / acousmatic
}


def step_fix_corrupt_genres(data):
    """Repara los 39 registros cuyo `genre` era el título de otro álbum.

    Aplica GENRE_FIXES: solo toca un álbum si su genre actual coincide
    byte a byte con el valor corrupto registrado, de modo que el paso es
    idempotente y nunca pisa una corrección manual posterior.
    """
    changes = []
    fixed = nulled = 0
    for album in data["albums"]:
        fix = GENRE_FIXES.get(album["id"])
        if fix is None:
            continue
        corrupt, correct = fix
        if album["genre"] == corrupt:
            album["genre"] = correct
            if correct is None:
                nulled += 1
            else:
                fixed += 1
    if fixed or nulled:
        changes.append(
            f"fix_corrupt_genres: {fixed} géneros corregidos, "
            f"{nulled} sin señal fiable puestos a null"
        )
    return changes


# ------------------------------------------------------------------
# Dedupe de releases (PR B, paso 1)
# ------------------------------------------------------------------
#
# El scraping capturó 35 páginas de Bandcamp dos (o más) veces: una fila
# con el título/artista "de listado" del sello (p. ej. `FSR120 The
# Daltonics - 3`, o `Miusichole Recs.` como artista) y otra con los de
# la propia página. Dentro de cada grupo tags y year son idénticos, así
# que la "fusión de tags" es trivial (unión == los del superviviente).
#
# Se fusionan 30 grupos auditados a mano. Quedan FUERA, anotados para
# re-scrape futuro porque las filas parecen releases reales distintos
# con la URL corrompida: Inigo Lunani LNI01-06 (6 filas -> /lni05),
# h.101 (3 filas -> /101001), MotorSex Single III vs VII, ELBIS REVER
# holaaa vs holaaa 2, txopet Ostabe Zuloan vs (Remixak).
#
# Formato cerrojo: id_a_borrar -> (url_esperada, id_superviviente). Una
# fila solo se elimina si su URL coincide byte a byte con la esperada Y
# el superviviente sigue presente con esa misma URL; así el paso es
# idempotente y no puede borrar nada si el dataset cambió por debajo.
RELEASE_DEDUPE = {
    2216: ("https://breathingthecore.bandcamp.com/album/stay-djent-1", 1364),
    1773: ("https://campamentorumano.bandcamp.com/album/el-punk-est-lleno-de-sinverg-enzas", 739),
    1344: ("https://chicoychica.bandcamp.com/album/s-edici-n-xx-aniversario", 403),
    2062: ("https://clorah.bandcamp.com/album/la-pena-extended-edition", 897),
    375: ("https://eclecticreactionsrecords.bandcamp.com/album/er028-garazi-gorostiaga-irauten-ii", 1779),
    1489: ("https://electricsoundmuchachos.bandcamp.com/album/electric-sound-muchachos", 2004),
    228: ("https://familyspreerecordings.bandcamp.com/album/fsr120-the-daltonics-3", 1598),
    50: ("https://fullcabb.bandcamp.com/album/full-cab-demos", 523),
    184: ("https://furiousrecords.bandcamp.com/album/m-rmol-declaraci-n-total-de-guerra", 113),
    329: ("https://hiddenbayrecords.bandcamp.com/album/con-las-vantanas-tan-grandes-me-da-verg-enza-mirar-voy-tan-deprisa", 134),
    724: ("https://jamesroom.bandcamp.com/album/fear", 1404),
    1098: ("https://juza.bandcamp.com/album/juza-true-love-blm006", 448),
    463: ("https://knekelput.bandcamp.com/album/demos-mmxix-mmxx", 360),
    69: ("https://laagoniadevivir.bandcamp.com/album/ladv214-alkuper-sendero-desesperanza-lp", 72),
    1527: ("https://laagoniadevivir.bandcamp.com/album/ladv214-alkuper-sendero-desesperanza-lp", 72),
    775: ("https://lahumanidadeslaplaga.bandcamp.com/album/cult-of-misery-together-to-hell-lp", 407),
    2146: ("https://meyorecords.bandcamp.com/album/vulk-beat-kamerlanden", 590),
    1309: ("https://miusichole.bandcamp.com/album/5000-rpm-manifesto-2011-mh-009", 908),
    1300: ("https://miusichole.bandcamp.com/album/despe-aperros-el-foso-7-2013-mh019", 2345),
    1322: ("https://miusichole.bandcamp.com/album/despe-aperros-el-foso-7-2013-mh019", 2345),
    1297: ("https://miusichole.bandcamp.com/album/diana-lagarto-s-t-2014-mh021", 471),
    1296: ("https://miusichole.bandcamp.com/album/los-cosm-ticos-danze-zizek-danze-2016-mh024", 1384),
    1295: ("https://miusichole.bandcamp.com/album/los-cosm-ticos-puro-pl-stico-2018-mh025", 1132),
    1305: ("https://miusichole.bandcamp.com/album/maderacore-el-camino-del-asombro-2013-mh-013", 783),
    1310: ("https://miusichole.bandcamp.com/album/maderacore-la-importancia-de-llamarse-humano-2009-mh-006", 1284),
    491: ("https://muertematarrecords.bandcamp.com/album/no-ser", 1619),
    1269: ("https://neila.bandcamp.com/album/neila-wayne-split", 773),
    225: ("https://runawaylovers.bandcamp.com/album/fsr074-santiago-delgado-y-los-runaway-lovers-por-amor-al-rocknroll-10-aniversario-lp", 729),
    2262: ("https://selfshot.bandcamp.com/album/19s-single", 2260),
    510: ("https://soma101.bandcamp.com/album/soma-101", 562),
    694: ("https://sustraidunyouths.bandcamp.com/album/problems-of-war-digital-cuts-vol-1", 258),
    1625: ("https://thecherryboppers.bandcamp.com/album/remix-it-again", 1380),
}

# Ajustes de campo en supervivientes cuyo valor era el equivocado del
# par. Mismo cerrojo que GENRE_FIXES: id -> campo -> (esperado, nuevo).
DEDUPE_OVERRIDES = {
    72: {"genre": ("devotional", "punk")},      # Alkuperä; 'devotional' era glitch, la fila gemela decía punk
    2345: {"genre": ("rock", "punk")},          # Despeñaperros, banda punk (fila gemela id 1322)
    729: {"genre": ("pop", "rock")},            # Santiago Delgado y los Runaway Lovers, rock'n'roll
    360: {"title": ("Demo MMXX", "Demos MMXIX-MMXX")},  # Saguzar: la página real es el recopilatorio de ambas demos
}


def rebuild_artists(data):
    """Regenera la lista top-level `artists` desde los albums.

    `tags` y `years` no se tocan: los duplicados eliminados tenían tags
    y year idénticos a sus supervivientes, así que nada queda huérfano.
    """
    data["artists"] = sorted({a["artist"] for a in data["albums"]})


def step_dedupe_releases(data):
    """Elimina las filas duplicadas por URL y aplica los overrides."""
    changes = []
    by_id = {a["id"]: a for a in data["albums"]}
    to_drop = set()
    for dead_id, (url, survivor_id) in RELEASE_DEDUPE.items():
        dead, survivor = by_id.get(dead_id), by_id.get(survivor_id)
        if dead and survivor and dead["url"] == url and survivor["url"] == url:
            to_drop.add(dead_id)
    if to_drop:
        data["albums"] = [a for a in data["albums"] if a["id"] not in to_drop]
        changes.append(f"dedupe_releases: {len(to_drop)} filas duplicadas eliminadas "
                       f"({len(data['albums'])} albums)")
    fixed = 0
    for album in data["albums"]:
        for field, (expected, new) in DEDUPE_OVERRIDES.get(album["id"], {}).items():
            if album[field] == expected:
                album[field] = new
                fixed += 1
    if fixed:
        changes.append(f"dedupe_releases: {fixed} campos de supervivientes corregidos")
    if changes:
        rebuild_artists(data)
    return changes


# ------------------------------------------------------------------
# Normalización de nombres de artista (PR B, paso 2)
# ------------------------------------------------------------------
#
# 41 grupos de variantes del mismo artista por mayúsculas/espacios/
# acentos. Forma canónica elegida, por orden: (1) la que el artista usa
# en las filas de su propio subdominio de Bandcamp, (2) la más
# frecuente tras el dedupe, (3) empates 1-a-1 decididos a mano.
#
# Casos EXCLUIDOS a propósito: nombres colaborativos (`Inshore, Javier
# Ho`, `Antxon Sagardui & ...`) son entidades distintas, no variantes;
# y `Judy`/`judy` quedan separados hasta verificar manualmente que el
# release de Eclectic Reactions es de la misma judy de erroa.
#
# El propio dict es el cerrojo: solo renombra filas cuyo artista
# coincide exactamente con la variante; tras aplicarse, ya no queda
# ninguna y el paso es un no-op.
ARTIST_RENAMES = {
    "6SISS": "6siss",
    "Add Obscurae": "add obscurae",
    "Azúal Dub": "Azùal Dub",
    "BIRKIT": "Birkit",
    "BISTIWARRIOR": "Bistiwarrior",
    "CAMPAMENTO RUMANO": "Campamento Rumano",
    "DABELYU": "Dabelyu",
    "distorsion": "DISTORSION",
    "edificios": "Edificios",
    "Elbis Rever": "ELBIS REVER",
    "ENKORE": "Enkore",
    "Ensemble KLEM": "Ensemble Klem",
    "Ensemble klem": "Ensemble Klem",
    "FALLING BLACK": "Falling Black",
    "FRANCO": "Franco",
    "GURS": "Gurs",
    "Huracan Rose": "HURACAN ROSE",
    "IN THOUSAND LAKES": "In Thousand Lakes",
    "iñigo ibaibarriaga": "Iñigo Ibaibarriaga",
    "jana jan": "JANA JAN",
    "kurixe": "KURIXE",
    "la sombra / Itzala": "La Sombra / Itzala",
    "LIFELOST": "Lifelost",
    "Mármol": "Marmol",
    "matutano": "Matutano",
    "miguel a. garcía": "Miguel A. García",
    "Motorsex": "MotorSex",
    "Myriam Rzm": "Myriam RZM",
    "neox": "NeOx",
    "Nize": "NIZE",
    "Onepointsix": "onepointsix",
    "ORBAIN UNIT": "Orbain Unit",
    "Shintoma": "SHINTOMA",
    "SHÖCK": "Shöck",
    "Sonic Trash": "SONIC TRASH",
    "Still RIver": "Still River",
    "TAKE WARNING": "Take Warning",
    "THE CRAZY WHEELS BAND": "The Crazy Wheels Band",
    "The Wizards": "THE WIZARDS",
    "Txarly Usher y los Ejemplares": "Txarly Usher y Los Ejemplares",
    "UMBRA OHM": "Umbra Ohm",
    "Vulk": "VULK",
}


def step_normalize_artist_names(data):
    """Unifica las variantes de nombre de artista en su forma canónica."""
    renamed = 0
    for album in data["albums"]:
        new = ARTIST_RENAMES.get(album["artist"])
        if new:
            album["artist"] = new
            renamed += 1
    if renamed:
        rebuild_artists(data)
        return [f"normalize_artist_names: {renamed} filas renombradas "
                f"({len(data['artists'])} artistas únicos)"]
    return []


# ------------------------------------------------------------------
# Limpieza de caracteres invisibles (PR C, paso 1)
# ------------------------------------------------------------------
#
# Restos de copy-paste en el scraping: U+200B (ZWSP) en dos títulos de
# judy, U+200E (LRM) al final del tag 'cáceres' y U+FEFF (BOM) al
# inicio de cuatro títulos de la serie ＃ＮＮＮ (los dígitos fullwidth
# son estilización del artista y se conservan). El paso elimina toda la
# familia de invisibles de title, artist y tags; es idempotente por
# naturaleza (sobre texto limpio no hace nada).
INVISIBLE_CHARS = dict.fromkeys(map(ord, (
    "\u200b"  # zero width space
    "\u200c"  # zero width non-joiner
    "\u200d"  # zero width joiner
    "\ufeff"  # BOM / zero width no-break space
    "\u200e"  # left-to-right mark
    "\u200f"  # right-to-left mark
    "\u2060"  # word joiner
    "\u00ad"  # soft hyphen
)), None)


def step_clean_invisible_chars(data):
    """Elimina caracteres invisibles de title, artist y tags."""
    cleaned = 0
    for album in data["albums"]:
        for field in ("title", "artist"):
            new = album[field].translate(INVISIBLE_CHARS)
            if new != album[field]:
                album[field] = new
                cleaned += 1
        new_tags = [t.translate(INVISIBLE_CHARS) for t in album["tags"]]
        if new_tags != album["tags"]:
            album["tags"] = new_tags
            cleaned += 1
    if cleaned:
        rebuild_artists(data)
        return [f"clean_invisible_chars: {cleaned} campos limpiados"]
    return []


# ------------------------------------------------------------------
# Normalización de tags (PR C, paso 2)
# ------------------------------------------------------------------
#
# Fusiona variantes del mismo tag (guiones/espacios/acentos/apóstrofes/
# puntuación colgante), typos con forma correcta ya existente y
# topónimos. Política auditada en la PR C:
#   - canónica = variante más frecuente del cluster; la puntuación
#     colgante nunca es canónica y los empates van a la forma con
#     espaciado estándar (excepciones decididas a mano: e.l.e.c.t.r.o
#     -> electro, non-conventional, improvisacion libre bilbao);
#   - topónimos vascos en euskera (donostia, gasteiz, bizkaia, iruña,
#     santurtzi, euskal herria); no vascos en su forma local (sevilla);
#   - NUNCA se cruzan familias léxicas ni idiomas: rock & roll /
#     rock'n'roll / rock and roll, dnb / drum & bass, synthpop /
#     tecnopop, hardcore punk / punk hardcore, basque music / euskal
#     musika, free improvisation / improvisacion libre, basque / vasco
#     quedan como están (candidatos a capa de alias del buscador en la
#     migración Vite+React).
#
# El propio dict es el cerrojo: solo renombra apariciones exactas de la
# variante; tras aplicarse no queda ninguna y el paso es un no-op.
TAG_RENAMES = {
    '2 step': '2-step',
    '2step': '2-step',
    '2stepgarage': '2-step garage',
    "70's": '70s',
    '70´s rock': '70s rock',
    '8-bit': '8bit',
    "90's": '90s',
    '90-s': '90s',
    'acústico': 'acustico',
    'afrocuban': 'afro-cuban',
    'alternative rock...': 'alternative rock',
    'ambient-electronic': 'ambient electronic',
    'amniótico': 'amniotico',
    'anarcho-punk': 'anarchopunk',
    'avant garde': 'avant-garde',
    'avantgarde': 'avant-garde',
    'avantgarde jazz': 'avantgardejazz',
    'basque coutry': 'euskal herria',
    'basquemusic': 'basque music',
    'bass.': 'bass',
    'bassmusic': 'bass music',
    'boombap': 'boom bap',
    'break beat': 'breakbeat',
    'chill out': 'chillout',
    'cold wave': 'coldwave',
    'cowntry': 'country',
    'crustpunk': 'crust punk',
    "d'nb": 'dnb',
    'd.i.y': 'diy',
    'dance-music': 'dance music',
    'dark ambient.': 'dark ambient',
    'dark-ambient': 'dark ambient',
    'darkdisco': 'dark disco',
    'darkpop': 'dark pop',
    'darktechno': 'dark techno',
    'dbeat': 'd-beat',
    'deathdoom metal': 'death doom metal',
    'deathmetal': 'death metal',
    'djtools': 'dj tools',
    'donostia san sebastian': 'donostia',
    'dreampop': 'dream pop',
    'drum-bass': 'drum & bass',
    'drumandbass': 'drum and bass',
    'dungeonsynth': 'dungeon synth',
    'e.b.m': 'ebm',
    'e.l.e.c.t.r.o': 'electro',
    'e.l.e.c.t.r.o.': 'electro',
    'eclecticreactions': 'eclectic reactions',
    'electro pop': 'electropop',
    'electrodub': 'electro dub',
    'electropunk': 'electro punk',
    'electrónica': 'electronica',
    'euskal heria': 'euskal herria',
    'euskalmusika': 'euskal musika',
    'experimental-electronic': 'experimental electronic',
    'fieldrecording': 'field recording',
    'flavourgz': "flavour g'z",
    'folk-rock': 'folk rock',
    'freeimprovisation': 'free improvisation',
    'freejazz': 'free jazz',
    'giallodisco': 'giallo disco',
    'gorka sanchez': 'gorka sánchez',
    'grind...': 'grind',
    'grungerock': 'grunge rock',
    'hard bass': 'hardbass',
    'hard core': 'hardcore',
    'hard core melodico': 'hardcore melódico',
    'hardcore-punk': 'hardcore punk',
    'hardcorepunk': 'hardcore punk',
    'harddance': 'hard dance',
    'hardhouse': 'hard house',
    'hardtechno': 'hard techno',
    'heavy metal.': 'heavy metal',
    'heavyrock': 'heavy rock',
    'hip-hop': 'hip hop',
    'hip_hop': 'hip hop',
    'hiphop': 'hip hop',
    'hiphop rap': 'hip-hop/rap',
    'horrordisco': 'horror disco',
    'hyperpop': 'hyper pop',
    'idm.': 'idm',
    'improvisacionlibrebilbao': 'improvisacion libre bilbao',
    'improvisación libre': 'improvisacion libre',
    'improvisaciónlibre': 'improvisacion libre',
    'indiepop': 'indie pop',
    'indiepoprock': 'indie pop rock',
    'indierock': 'indie rock',
    'indusrial': 'industrial',
    'italodisco': 'italo disco',
    'livecoding': 'live coding',
    'lo fi': 'lo-fi',
    'lo-fi house': 'lofi house',
    'lofi': 'lo-fi',
    'mathrock': 'math rock',
    'melodic hardcore...': 'melodic hardcore',
    'melodic metal.': 'melodic metal',
    'melodichardcore': 'melodic hardcore',
    'metal punk': 'metalpunk',
    'metalcore.': 'metalcore',
    'miguel a garcia': 'miguel a. garcia',
    'mikel ndong': "mikel n'dong",
    'minimalhouse': 'minimal house',
    'modernclassical': 'modern classical',
    'mongopunk': 'mongo punk',
    'moonshakers': 'moon shakers',
    'neo-classical': 'neo classical',
    'neoclassical': 'neo classical',
    'noise-punk': 'noise punk',
    'noiserock': 'noise rock',
    'non - conventional': 'non-conventional',
    'nu jazz': 'nujazz',
    'nu-jazz': 'nujazz',
    'nu-metal': 'nu metal',
    'nü metal': 'nu metal',
    'old school death metal': 'oldschool death metal',
    'oldschool': 'old school',
    'pamplona': 'iruña',
    'pays basque': 'euskal herria',
    'país vasco': 'euskal herria',
    'pcmusic': 'pc music',
    'pop-punk': 'pop punk',
    'pop-rock': 'pop rock',
    'pop.rock': 'pop rock',
    'poppunk': 'pop punk',
    'poprock': 'pop rock',
    'post hardcore': 'post-hardcore',
    'post punk': 'post-punk',
    'post rock': 'post-rock',
    'post-blackmetal': 'post black metal',
    'posthardcore': 'post-hardcore',
    'postmetal': 'post-metal',
    'postpunk': 'post-punk',
    'postrock': 'post-rock',
    'power violence': 'powerviolence',
    'powerpop': 'power pop',
    'powertrio': 'power trio',
    "punk'n'roll": "punk 'n' roll",
    'punk.rock': 'punk rock',
    'punkhardcore': 'punk hardcore',
    'punkpop': 'punk pop',
    'punkrock': 'punk rock',
    'rap metal': 'rapmetal',
    'ratzinger': 'rat-zinger',
    'ravepunk': 'rave punk',
    'reggae.': 'reggae',
    'rock n roll': "rock'n'roll",
    "rock n' roll": "rock'n'roll",
    'rock&roll': 'rock & roll',
    'rockabillly': 'rockabilly',
    'rockandroll': 'rock and roll',
    'rootsrock': 'roots rock',
    'rubadub': 'rub a dub',
    'rubén g. mateos': 'ruben g mateos',
    'rythm & blues': 'rhythm & blues',
    'samuel cano': 'samuelcano',
    'san sebastián': 'donostia',
    'santurz': 'santurtzi',
    'scifi': 'sci-fi',
    'seville': 'sevilla',
    'singersongwriter': 'singer-songwriter',
    'soundart': 'sound art',
    'soundsystem': 'sound system',
    'spacedisco': 'space disco',
    'spacerock': 'space rock',
    'streetpunk': 'street punk',
    'synth pop': 'synthpop',
    'synth wave': 'synthwave',
    'synthpunk': 'synth punk',
    'techno.': 'techno',
    'technopop': 'techno pop',
    'tecno pop': 'tecnopop',
    'thebiterbitten': 'the biter bitten',
    'triphop': 'trip hop',
    'uk grime': 'ukgrime',
    'uk roots': 'ukroots',
    'ukgarage': 'uk garage',
    'video game music': 'videogame music',
    'videogame': 'video game',
    'vitoria-gasteiz': 'gasteiz',
    'vizcaya': 'bizkaia',
    'worldmusic': 'world music',
    'zaragoza.': 'zaragoza',
}


# Tags-mezcla con '#' (restos de redes sociales): se trocean en sus
# componentes reales; lista vacía = el tag se elimina por no tener
# contenido musical. 'irish music' es forma nueva (no existía).
TAG_SPLITS = {
    "2025 #spotify #youtube #google": [],
    "etc.": [],
    "etc...": [],
    "celticmusic #irishmusic #folk": ["celtic", "irish music", "folk"],
    "deephouse #deephousemusic": ["deep house"],
    "downtempomusic #steppa": ["downtempo", "steppa"],
    "dubtechno #downtempo": ["dub techno", "downtempo"],
    "jazz #funk #afro beat #": ["jazz", "funk", "afrobeat"],
    "punk #dark #garage #post-punk": ["punk", "dark", "garage", "post-punk"],
    "steppastyle #dubsteppa": ["steppa", "dubsteppa"],
}


def rebuild_tags(data):
    """Regenera la lista top-level `tags` desde los albums."""
    data["tags"] = sorted({t for a in data["albums"] for t in a["tags"]})


def step_normalize_tags(data):
    """Aplica TAG_RENAMES y TAG_SPLITS y deduplica cada lista de tags.

    La deduplicación conserva el orden de primera aparición; ya había
    367 entradas repetidas literales en 299 álbumes antes de esta PR,
    y las fusiones pueden crear alguna más. Ningún álbum pierde
    información: cada variante se sustituye por su forma canónica.
    """
    touched = 0
    for album in data["albums"]:
        out = []
        for tag in album["tags"]:
            parts = TAG_SPLITS[tag] if tag in TAG_SPLITS else [TAG_RENAMES.get(tag, tag)]
            for part in parts:
                if part not in out:
                    out.append(part)
        if out != album["tags"]:
            album["tags"] = out
            touched += 1
    if touched:
        rebuild_tags(data)
        return [f"normalize_tags: {touched} álbumes con tags normalizados "
                f"({len(data['tags'])} tags únicos)"]
    return []


def step_merge_covers(data):
    """Fusiona data/covers.json (scrape de Bandcamp) en el canónico.

    Añade a cada álbum cover_url (string|null) y album_id (int|null)
    cruzando por id contra los items del scrape. Los álbumes cuya
    entrada quedó en "error" (404s de Bandcamp) o que no tienen URL
    reciben null en ambos campos, la misma convención que `year`.

    data/covers.json no está versionado en main (viaja como artifact o
    en la rama scrape-covers-test); si el archivo no existe el paso no
    hace nada, así el pipeline sigue siendo ejecutable en cualquier
    checkout. Solo se asigna cuando el valor difiere del actual, de
    modo que una segunda pasada informa 0 cambios.
    """
    covers_file = REPO_ROOT / "data" / "covers.json"
    if not covers_file.exists():
        return []
    with open(covers_file, encoding="utf-8") as f:
        items = json.load(f)["items"]

    filled = 0
    nulled = 0
    for album in data["albums"]:
        item = items.get(str(album["id"]))
        if item is not None and item.get("status") == "ok":
            cover_url, album_id = item["cover_url"], item["album_id"]
        else:
            cover_url, album_id = None, None
        if album.get("cover_url", "\0") != cover_url or album.get("album_id", "\0") != album_id:
            album["cover_url"] = cover_url
            album["album_id"] = album_id
            if cover_url is None and album_id is None:
                nulled += 1
            else:
                filled += 1
    if filled or nulled:
        return [f"merge_covers: {filled} álbumes con cover_url+album_id, {nulled} a null"]
    return []


STEPS = [
    step_clean_urls,
    step_fix_corrupt_genres,
    step_dedupe_releases,
    step_normalize_artist_names,
    step_clean_invisible_chars,
    step_normalize_tags,
    step_merge_covers,
]


# ------------------------------------------------------------------
# Ejecución
# ------------------------------------------------------------------

def serialize(data):
    # Mismo formato que el archivo original: indent 4, UTF-8 literal,
    # sin newline final. Mantenerlo estable hace los diffs mínimos y
    # la idempotencia verificable byte a byte.
    return json.dumps(data, indent=4, ensure_ascii=False)


def validate(data):
    """Invariantes de esquema que ningún paso puede romper."""
    assert set(data.keys()) == {"albums", "artists", "tags", "years"}
    # Esquema consolidado tras el merge de portadas: los 9 campos son
    # obligatorios en todos los álbumes. El canónico ya los lleva, así
    # que el pipeline sigue ejecutable aunque falte data/covers.json
    # (merge_covers sería no-op sobre un dataset ya completo).
    expected = {"id", "artist", "title", "genre", "year", "tags", "url",
                "cover_url", "album_id"}
    for album in data["albums"]:
        assert set(album.keys()) == expected, \
            f"esquema roto en album id={album.get('id')}"
        assert album["cover_url"] is None or isinstance(album["cover_url"], str), \
            f"cover_url no es string|null en album id={album.get('id')}"
        assert album["album_id"] is None or isinstance(album["album_id"], int), \
            f"album_id no es int|null en album id={album.get('id')}"


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true",
                        help="informa de los cambios sin reescribir el JSON")
    args = parser.parse_args()

    original_text = DATA_FILE.read_text(encoding="utf-8")
    data = json.loads(original_text)
    size_before = len(original_text.encode("utf-8"))

    all_changes = []
    for step in STEPS:
        all_changes.extend(step(data))

    validate(data)
    new_text = serialize(data)
    size_after = len(new_text.encode("utf-8"))

    for line in all_changes:
        print(f"  · {line}")
    if not all_changes:
        print("  · 0 cambios (dataset ya saneado)")

    delta = size_before - size_after
    print(f"  · tamaño: {size_before:,} → {size_after:,} bytes ({delta:+,d} = {delta / 1024:.1f} KB ahorrados)"
          if delta else f"  · tamaño: {size_before:,} bytes (sin cambios)")

    if args.dry_run:
        print("dry-run: no se ha escrito nada")
        return 0

    if new_text != original_text:
        DATA_FILE.write_text(new_text, encoding="utf-8")
        print(f"escrito {DATA_FILE.relative_to(REPO_ROOT)}")
    else:
        print("el archivo ya estaba al día, no se reescribe")
    return 0


if __name__ == "__main__":
    sys.exit(main())
