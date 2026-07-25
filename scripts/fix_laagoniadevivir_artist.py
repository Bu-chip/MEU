#!/usr/bin/env python3
"""Excepción manual y explícita: las 8 filas de `laagoniadevivir` acreditadas con
la grafía «La Agonía Vivir» (sin "de").

Por qué esto es un script aparte y NO una ampliación del gate:
    La corrección automática (scripts/fix_artist_from_title.py) exige que el
    `artist` actual folde EXACTAMENTE al subdominio de la cuenta
    (fold("La Agonía de Vivir") == "laagoniadevivir"). Ese sello se acredita con
    DOS grafías: «La Agonía de Vivir» (folda, se corrigió en su PR) y «La Agonía
    Vivir» sin "de" (fold == "laagoniavivir", NO folda). Ampliar el gate para
    pillar la segunda grafía (p. ej. por parecido difuso) reintroduciría los
    falsos positivos que aquel gate evita a propósito (bandas cuya cuenta ==
    nombre, códigos de catálogo, etc.). Así que estas 8 se corrigen a mano, como
    excepción cerrada y auditable para ESTA cuenta, sin tocar aquella lógica.

Las 8 filas siguen el mismo patrón P2 del sondeo:
    LADV### - ARTISTA "Título" [formato]
El artista real está en el `title`; el sello se acreditó a sí mismo. Se reescribe
SOLO el campo `artist`. No se toca `title`, no se añaden campos (esquema de 9), no
se pierde el sello (derivable del subdominio de `url`).

Salidas:
  * data/derived/artist_fixes_laagoniadevivir.md — informe con las 8 filas.
  * data/bandcamp_bilbaotags_clean.json — corrección aplicada (diff = 8 líneas
    de `artist`), salvo --dry-run.

Invariantes (verificados; el script FALLA EN ALTO si alguno se rompe): nº de
álbumes idéntico; se modifican EXACTAMENTE las 8 filas de esta tabla; el único
campo que cambia es `artist`; 9 campos por fila y validate() de pipeline.py pasa;
mismo serializador (el diff son 8 líneas, no reescribe el fichero).

Idempotente: cada fila se corrige solo si su `artist` actual es la grafía vieja;
si ya lleva el artista nuevo, se salta. Re-ejecutar no cambia nada (sha256
estable). Si una fila está en un estado inesperado (ni viejo ni nuevo), aborta.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from labels_index import derive_account  # noqa: E402
from pipeline import serialize, validate  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
CANONICAL = REPO_ROOT / "data" / "bandcamp_bilbaotags_clean.json"
DERIVED_DIR = REPO_ROOT / "data" / "derived"
REPORT = DERIVED_DIR / "artist_fixes_laagoniadevivir.md"

CUENTA = "laagoniadevivir"
GRAFIA_VIEJA = "La Agonía Vivir"  # la que NO folda al subdominio (sin "de")

# Tabla CERRADA y explícita. Cada entrada: (id, album_id, artista_real, title).
# El artista_real es el token que está entre la referencia de catálogo (LADV###)
# y el título entrecomillado; se ha extraído a mano y se fija aquí para que la
# corrección sea auditable y no dependa de ninguna regex. album_id y title se
# comprueban contra el canónico antes de tocar nada (defensa contra un id movido).
FIXES = [
    (146,  3043169698, "MÁRMOL",         'LADV166 - MÁRMOL "declaración total de guerra" LP'),
    (163,  3399851741, "OHIL",           'LADV206 - OHIL "akorde beste orbain" LP'),
    (909,  3233000682, "DESPEÑAPERROS",  'LADV60 - DESPEÑAPERROS "herejía" LP'),
    (1151, 1232650862, "DIANA LAGARTO",  'LADV39 - DIANA LAGARTO "st" LP'),
    (1156, 2233289320, "URA",            'LADV45 - URA "st" 12"'),
    (1258, 3729234297, "1991",           'LADV46 - 1991 "st" 12"'),
    (1355, 262980317,  "ANCIENT EMBLEM", 'LADV38 - ANCIENT EMBLEM "throne with no god" LP'),
    (1356, 3400350081, "DESPEÑAPERROS",  'LADV16 - DESPEÑAPERROS "el foso" 7"'),
]


def build_report(applied: list[tuple], ya_estaban: list[tuple]) -> str:
    lines: list[str] = []
    a = lines.append
    a("# Corrección manual — `laagoniadevivir` (grafía «La Agonía Vivir», sin \"de\")")
    a("")
    a("Excepción explícita y cerrada para **una** cuenta. El sello `laagoniadevivir` "
      "se acredita con dos grafías; la variante «La Agonía de Vivir» ya se corrigió en "
      "su PR (foldaba al subdominio). Esta variante «La Agonía Vivir» (sin \"de\") **no** "
      "folda, así que la corrección automática la dejó fuera a propósito. Aquí se "
      "corrigen esas **8 filas a mano**, sin ampliar ni tocar la lógica de "
      "`scripts/fix_artist_from_title.py`. Mismo patrón P2: `LADV### - ARTISTA \"Título\" "
      "[formato]`. Solo cambia el campo `artist`.")
    a("")
    a(f"- Filas de la excepción: **{len(FIXES)}** (todas de `{CUENTA}`, patrón P2).")
    a(f"- Aplicadas en esta ejecución: **{len(applied)}**.")
    if ya_estaban:
        a(f"- Ya estaban corregidas (idempotencia): **{len(ya_estaban)}**.")
    a("")
    a("| id | album_id | artist actual | artist propuesto | patrón | title original |")
    a("| ---: | ---: | :--- | :--- | :--- | :--- |")
    for _id, album_id, nuevo, title in FIXES:
        a(f"| {_id} | {album_id} | {GRAFIA_VIEJA} | **{nuevo}** | P2 | `{title}` |")
    a("")
    return "\n".join(lines) + "\n"


def apply_and_check(original_text: str, data: dict):
    """Aplica la tabla FIXES y verifica los invariantes. Devuelve (new_text,
    applied, ya_estaban). Lanza AssertionError si algo no cuadra."""
    original = json.loads(original_text)
    n_before = len(data["albums"])
    by_id = {alb.get("id"): alb for alb in data["albums"]}

    esperados = {_id for _id, *_ in FIXES}
    aplicados: list[tuple] = []
    ya_estaban: list[tuple] = []

    for _id, album_id, nuevo, title in FIXES:
        alb = by_id.get(_id)
        assert alb is not None, f"id {_id} no existe en el canónico"
        # Defensa: la fila debe ser EXACTAMENTE la esperada.
        assert alb.get("album_id") == album_id, f"album_id no coincide en id={_id}"
        assert (alb.get("title") or "") == title, f"title no coincide en id={_id}"
        _, acc = derive_account(alb.get("url"))
        assert acc == CUENTA, f"id={_id} no es de la cuenta {CUENTA} (es {acc})"

        actual = alb.get("artist")
        if actual == nuevo:
            ya_estaban.append((_id, nuevo))          # idempotencia
            continue
        assert actual == GRAFIA_VIEJA, (
            f"id={_id}: artist en estado inesperado {actual!r} "
            f"(se esperaba {GRAFIA_VIEJA!r} o {nuevo!r}); abortando"
        )
        alb["artist"] = nuevo
        aplicados.append((_id, nuevo))

    # --- Invariantes ------------------------------------------------------
    assert len(data["albums"]) == n_before == len(original["albums"]), "cambió el nº de álbumes"

    campos = {"id", "artist", "title", "genre", "year", "tags", "url",
              "cover_url", "album_id"}
    ids_modificados = set()
    for nuevo_alb, viejo_alb in zip(data["albums"], original["albums"]):
        assert set(nuevo_alb.keys()) == campos, f"esquema != 9 campos en id={nuevo_alb.get('id')}"
        for k in campos:
            if k == "artist":
                if nuevo_alb[k] != viejo_alb[k]:
                    ids_modificados.add(nuevo_alb["id"])
                continue
            assert nuevo_alb[k] == viejo_alb[k], (
                f"cambió el campo '{k}' en id={nuevo_alb.get('id')} (solo se permite 'artist')"
            )
    for k in ("artists", "tags", "years"):
        assert data.get(k) == original.get(k), f"cambió el bloque top-level '{k}'"

    # Solo pueden haber cambiado filas de la tabla, y exactamente las aplicadas.
    assert ids_modificados <= esperados, f"se modificaron filas fuera de la tabla: {ids_modificados - esperados}"
    assert ids_modificados == {i for i, _ in aplicados}, "conteo de modificaciones != aplicadas"

    validate(data)

    new_text = serialize(data)
    orig_lines = original_text.split("\n")
    new_lines = new_text.split("\n")
    assert len(orig_lines) == len(new_lines), "cambió el nº de líneas (formato distinto)"
    diff_idx = [i for i in range(len(orig_lines)) if orig_lines[i] != new_lines[i]]
    assert len(diff_idx) == len(aplicados), (
        f"líneas cambiadas {len(diff_idx)} != aplicadas {len(aplicados)}"
    )
    for i in diff_idx:
        assert '"artist":' in orig_lines[i] and '"artist":' in new_lines[i], (
            f"la línea {i+1} cambió y NO es un campo artist: {orig_lines[i]!r}"
        )
    return new_text, aplicados, ya_estaban


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true",
                        help="genera el informe pero NO reescribe el canónico")
    args = parser.parse_args()

    original_text = CANONICAL.read_text(encoding="utf-8")
    data = json.loads(original_text)

    new_text, aplicados, ya_estaban = apply_and_check(original_text, data)

    DERIVED_DIR.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(build_report(aplicados, ya_estaban), encoding="utf-8")

    print(f"Cuenta            : {CUENTA} (grafía «{GRAFIA_VIEJA}»)")
    print(f"Filas de la tabla : {len(FIXES)} (patrón P2)")
    print(f"Aplicadas         : {len(aplicados)}")
    if ya_estaban:
        print(f"Ya corregidas     : {len(ya_estaban)} (idempotencia)")
    print(f"Informe           : {REPORT.relative_to(REPO_ROOT)}")

    if args.dry_run:
        print("dry-run: canónico NO reescrito.")
        return 0

    if new_text != original_text:
        CANONICAL.write_text(new_text, encoding="utf-8")
        print(f"Canónico reescrito: {CANONICAL.relative_to(REPO_ROOT)} ({len(aplicados)} líneas de artist)")
    else:
        print("Canónico sin cambios (ya corregido): no se reescribe.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
