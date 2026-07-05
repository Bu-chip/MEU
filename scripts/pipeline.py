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


STEPS = [
    step_clean_urls,
    step_fix_corrupt_genres,
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
    fields = {"id", "artist", "title", "genre", "year", "tags", "url"}
    for album in data["albums"]:
        assert set(album.keys()) == fields, f"esquema roto en album id={album.get('id')}"


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
