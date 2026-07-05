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


STEPS = [
    step_clean_urls,
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
