#!/usr/bin/env python3
"""Corrige `artist` cuando el sello se acredita a sí mismo y esconde al artista
real dentro del `title`. Fase de ESCRITURA sobre el canónico (PR curado).

Contexto: continuación del sondeo de títulos (PR #49). Algunos sellos figuran
como `artist` mientras el acto real está en el `title`:

    artist="Mendeku Diskak"  title='-012- CUERO "Black Metal Skinheads" Promo Tape'

El artista real es CUERO. Este script reescribe SOLO el campo `artist` de esas
filas. NO añade campos (el esquema sigue siendo de 9). NO toca el `title`. NO se
pierde el sello: ya es derivable del subdominio de `url` (scripts/labels_index.py).

Por qué es legítimo tocar el canónico aquí: "el canónico no se toca" aplica a
procesos automáticos (scraper, cron). Esto es un PR pequeño y curado que Miguel
revisa fila a fila y mergea él. Aun así, todo lo de abajo es obligatorio.

ALCANCE — SOLO P1, P2, P3 (los patrones fiables del sondeo). P4 (artista - título)
y P5 (splits) quedan FUERA a propósito.

GATES (una fila se corrige solo si CUMPLE TODO):
  1. El título casa con P1, P2 o P3 (regex de probe_titulos, comilla-segura).
  2. La cuenta es un SELLO reconocido por labels_index (>= 2 clusters de artista
     o marcador léxico). Esto distingue el sello auto-acreditado de la BANDA cuya
     cuenta coincide con su nombre (adrenalized, ancientsettlers...): esas NO se
     tocan, su `artist` ya es un artista real.
  3. El `artist` actual ES el nombre del sello: fold(artist_actual) == fold(cuenta).
     Si el `artist` actual ya es otro artista real (o un código de catálogo), NO
     se toca.
  4. El artista extraído pasa el control de calidad de probe_titulos: no vacío,
     no 1-2 caracteres, no solo dígitos/puntuación, no Various Artists/VVAA, y no
     coincide con el propio sello.

Todo lo que casa P1/P2/P3 pero NO pasa un gate se REPORTA en el informe con su
motivo; no se corrige.

Salidas:
  * data/derived/artist_fixes.md  — informe legible en iPad (P1, P2, P3 y
    exclusiones), SIEMPRE se escribe.
  * data/bandcamp_bilbaotags_clean.json — corrección aplicada, salvo --dry-run.

Invariantes (se verifican y el script FALLA EN ALTO si alguno se rompe):
  * nº de álbumes idéntico antes/después.
  * nº de filas modificadas == nº de propuestas del informe.
  * el ÚNICO campo que cambia en todo el fichero es `artist`.
  * todas las filas conservan 9 campos; validate() de pipeline.py pasa.
  * el formato de serialización es el mismo (serialize() de pipeline.py): el diff
    solo toca líneas de `artist`, no reescribe el fichero entero.

Idempotente: tras corregir, la fila lleva el artista real, que ya NO folda al
nombre del sello (gate 3 falla), así que re-ejecutar no cambia el canónico. Se
demuestra con sha256 en el bloque de pruebas del PR.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

# Reutilizamos lo ya escrito y probado. Sin duplicar lógica.
from labels_index import (  # noqa: E402
    derive_account,
    fold,
    normalize_artist,
    account_slug,
    build_index,
    candidate_records,
)
from probe_titulos import classify, artist_problem  # noqa: E402
from pipeline import serialize, validate  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
CANONICAL = REPO_ROOT / "data" / "bandcamp_bilbaotags_clean.json"
DERIVED_DIR = REPO_ROOT / "data" / "derived"
REPORT = DERIVED_DIR / "artist_fixes.md"

PATRONES = ("P1", "P2", "P3")

# Motivos de exclusión, redactados y ORDENADOS para que el desglose 95 -> 59
# mapee 1:1 con las exclusiones obligatorias del enunciado. Un motivo por fila.
R_VA = "el artista extraído es Various Artists / VVAA"
R_BASURA = "el artista extraído es vacío, de 1-2 caracteres, o solo dígitos/puntuación"
R_ES_SELLO = "el artista extraído es igual al nombre del sello (no aporta)"
R_NO_CUENTA = "el artist actual no es el nombre de la cuenta (ya es un artista real o un código de catálogo)"
R_NO_SELLO = "el artist actual ya es un artista real: la cuenta no es un sello reconocido por labels_index (es la propia banda)"

# Orden fijo de los motivos en el informe y en el desglose numérico.
EXC_ORDEN = [R_VA, R_BASURA, R_ES_SELLO, R_NO_CUENTA, R_NO_SELLO]

# Traducción de la salida de artist_problem() a los tres motivos de calidad.
_PROB_BUCKET = {
    "Various Artists / VVAA": R_VA,
    "1-2 caracteres": R_BASURA,
    "vacío / solo puntuación": R_BASURA,
    "solo números": R_BASURA,
    "coincide con el propio sello (autocuenta)": R_ES_SELLO,
}


def scan(data: dict) -> tuple[list[dict], dict[str, list[dict]], set[str]]:
    """Recorre el canónico y separa PROPUESTAS de EXCLUSIONES.

    Devuelve (propuestas, exclusiones_por_motivo, existing_folds). Cada propuesta/
    exclusión guarda referencia al objeto álbum (para mutar después) y los datos
    para el informe. `existing_folds` = folds de la lista canónica `artists`, para
    marcar qué artistas recuperados YA existen por su cuenta (enlazables).
    """
    albums = data["albums"]
    existing = {fold(a) for a in data.get("artists", []) if fold(a)}

    # Sellos reconocidos por labels_index (>=2 clusters o marcador léxico).
    index = build_index(albums)
    label_accounts = {c["account_id"] for c in candidate_records(index)}

    propuestas: list[dict] = []
    exclusiones: dict[str, list[dict]] = defaultdict(list)

    for album in albums:
        _, account_id = derive_account(album.get("url"))
        if account_id is None:
            continue
        res = classify(album.get("title", "") or "")
        if not res or res["patron"] not in PATRONES:
            continue

        art = normalize_artist(res["artists"][0])
        cur = normalize_artist(album.get("artist", "") or "")
        slug = account_slug(account_id)
        rec = {
            "album": album,
            "id": album.get("id"),
            "album_id": album.get("album_id"),
            "account_id": account_id,
            "patron": res["patron"],
            "cur": cur,
            "art": art,
            "title": album.get("title", "") or "",
        }

        # Los gates se evalúan en el ORDEN del enunciado, para que cada fila
        # excluida reciba el motivo que corresponde a su exclusión obligatoria.
        # (El conjunto de FIJADAS es el mismo con cualquier orden: es la
        # conjunción de todos los gates.)
        #
        # Gate #4a: el artist actual debe ser el nombre de la cuenta (sello
        # auto-acreditado). Si no lo es, ya es un artista real o un código de
        # catálogo: no se toca.
        if not slug or fold(cur) != slug:
            exclusiones[R_NO_CUENTA].append(rec)
            continue
        # Gates #1/#2/#3: control de calidad de la extracción (VA, basura, ==sello).
        problema = artist_problem(art, slug)
        if problema is not None:
            exclusiones[_PROB_BUCKET[problema]].append(rec)
            continue
        # Gate #4b: el artist actual == cuenta PERO la cuenta no es un sello
        # reconocido (1 cluster, sin marcador léxico): es una banda cuya cuenta
        # coincide con su nombre (adrenalized, ancientsettlers...). El artist
        # actual ya es un artista real: NO se toca.
        if account_id not in label_accounts:
            exclusiones[R_NO_SELLO].append(rec)
            continue

        rec["ya_existe"] = fold(art) in existing
        propuestas.append(rec)

    # Orden determinista.
    propuestas.sort(key=lambda r: (r["patron"], r["account_id"], r["id"]))
    for motivo in exclusiones:
        exclusiones[motivo].sort(key=lambda r: (r["account_id"], r["id"]))

    # La divergencia 95 -> N debe quedar EXPLICADA ENTERA por las exclusiones:
    # cada match P1/P2/P3 es o una propuesta o una exclusión con motivo conocido.
    # Si aparece un motivo no contemplado, falla en alto (no escribas nada).
    desconocidos = set(exclusiones) - set(EXC_ORDEN)
    assert not desconocidos, f"motivos de exclusión no contemplados: {desconocidos}"
    return propuestas, exclusiones, existing


# ---------------------------------------------------------------------------
# Informe.
# ---------------------------------------------------------------------------

def _fila(a, r: dict) -> None:
    marca = " ✓existe" if r.get("ya_existe") else ""
    a(f"| {r['id']} | {r['album_id']} | {r['cur']} | **{r['art']}**{marca} | "
      f"{r['patron']} | `{r['title']}` |")


def build_report(propuestas: list[dict], exclusiones: dict, existing: set[str]) -> str:
    lines: list[str] = []
    a = lines.append

    por_patron = {p: [r for r in propuestas if r["patron"] == p] for p in PATRONES}
    cuentas = sorted({r["account_id"] for r in propuestas})
    nuevos_folds = {fold(r["art"]) for r in propuestas}
    enlazables = sorted(nuevos_folds & existing)

    a("# Corrección de `artist` desde el `title` (sello auto-acreditado)")
    a("")
    a("PR curado, **read-and-write** sobre el canónico. Reescribe **solo** el campo "
      "`artist` de filas donde el sello se acredita a sí mismo y el artista real está "
      "escondido en el `title`. **No** se toca el `title`, **no** se añaden campos, el "
      "esquema sigue siendo de 9. El sello no se pierde: es derivable del subdominio "
      "de `url`.")
    a("")
    a(f"- **Filas propuestas: {len(propuestas)}** "
      f"(P1={len(por_patron['P1'])}, P2={len(por_patron['P2'])}, P3={len(por_patron['P3'])}).")
    a(f"- Cuentas (sellos) afectadas: **{len(cuentas)}** — {', '.join(cuentas)}.")
    a(f"- Artistas distintos recuperados: **{len(nuevos_folds)}**.")
    a(f"- De esos, **ya existen** en el canónico por su cuenta (enlazables "
      f"sello↔artista): **{len(enlazables)}**.")
    a("")
    a("Solo se corrige P1/P2/P3 y solo cuando la cuenta es un sello reconocido por "
      "`labels_index` **y** el `artist` actual es el nombre del sello. Todo lo demás "
      "se lista en «Exclusiones» con su motivo. Columna `artist propuesto`: ✓existe = "
      "ese artista ya está en el canónico por su cuenta.")
    a("")

    # --- Desglose 95 -> 59 (obligatorio) ----------------------------------
    total_exc = sum(len(v) for v in exclusiones.values())
    total_matches = len(propuestas) + total_exc
    a(f"## Desglose: {total_matches} títulos casan P1/P2/P3 → {len(propuestas)} corregidos")
    a("")
    a(f"El sondeo apuntaba a ~95 filas por P1+P2+P3. Casan **{total_matches}**; se "
      f"corrigen **{len(propuestas)}**. La diferencia la explican **enteras** las "
      "exclusiones obligatorias (cada fila cae en un único motivo):")
    a("")
    a("| # | exclusión | filas |")
    a("| :--- | :--- | ---: |")
    etiquetas = {
        R_VA: "① artista extraído = Various Artists / VVAA",
        R_BASURA: "② artista extraído vacío / 1-2 caracteres / solo dígitos-puntuación",
        R_ES_SELLO: "③ artista extraído = nombre del sello",
        R_NO_CUENTA: "④a artist actual ≠ nombre de la cuenta (ya es artista real / código)",
        R_NO_SELLO: "④b artist actual = cuenta, pero la cuenta no es un sello (banda)",
    }
    for motivo in EXC_ORDEN:
        a(f"| {etiquetas[motivo]} | {motivo} | {len(exclusiones.get(motivo, []))} |")
    a(f"| | **Σ exclusiones** | **{total_exc}** |")
    a(f"| | **corregidas** | **{len(propuestas)}** |")
    a(f"| | **total P1+P2+P3** | **{total_matches}** |")
    a("")
    a(f"Reconciliación: **{len(propuestas)} + {total_exc} = {total_matches}**. Cuadra; "
      "no hay filas sin explicar.")
    a("")

    _COLS = "| id | album_id | artist actual | artist propuesto | patrón | title original |"
    _SEP = "| ---: | ---: | :--- | :--- | :--- | :--- |"

    def _seccion(patron: str, titulo: str, extra: str = "") -> None:
        rows = por_patron[patron]
        a(f"## {patron} · {titulo} — {len(rows)} filas")
        a("")
        if extra:
            a(extra)
            a("")
        if not rows:
            a("_(ninguna)_")
            a("")
            return
        for acc in sorted({r["account_id"] for r in rows}):
            sub = [r for r in rows if r["account_id"] == acc]
            a(f"### {acc} ({len(sub)})")
            a("")
            a(_COLS)
            a(_SEP)
            for r in sub:
                _fila(a, r)
            a("")

    _seccion("P1", "`-NNN- ARTISTA \"Título\" [formato]`",
             "Referencia de catálogo numérica + comillas. El patrón más fiable.")
    _seccion("P2", "`ALNUM - ARTISTA \"Título\"`",
             "Referencia alfanumérica (ZR04, LADV166...) + comillas. Fiable.")
    _seccion(
        "P3", "`ARTISTA \"Título\"`",
        "**⚠ LA QUE MÁS REVISIÓN NECESITA.** Sin referencia de catálogo delante: "
        "solo las comillas separan artista y título, sobre más cuentas y con más "
        "superficie de error. Revisar fila a fila.",
    )

    # --- Exclusiones ------------------------------------------------------
    a(f"## Exclusiones — {total_exc} filas que casan P1/P2/P3 pero NO se corrigen")
    a("")
    a("Todo lo que un patrón casa pero un gate rechaza, con su motivo. Un patrón con "
      "cobertura pero con ruido es peor que poco y limpio: aquí se ve el ruido que se "
      "deja fuera a propósito.")
    a("")
    for motivo in EXC_ORDEN:
        rows = exclusiones.get(motivo, [])
        if not rows:
            continue
        a(f"### {motivo} — {len(rows)}")
        a("")
        a("| id | cuenta | artist actual | se extraería | patrón | title original |")
        a("| ---: | :--- | :--- | :--- | :--- | :--- |")
        for r in rows:
            a(f"| {r['id']} | {r['account_id']} | {r['cur']} | {r['art']} | "
              f"{r['patron']} | `{r['title']}` |")
        a("")

    if enlazables:
        a("## Artistas recuperados que YA existen por su cuenta")
        a("")
        a("Base del enlace sello↔artista: el nombre escondido en el `title` ya es un "
          "artista del mapa. (En el sondeo global salían 126 enlazables sobre P1-P4; "
          "aquí, solo P1-P3 y solo sellos auto-acreditados.)")
        a("")
        a("| artista (fold) |")
        a("| :--- |")
        for f in enlazables:
            a(f"| `{f}` |")
        a("")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Aplicación + invariantes.
# ---------------------------------------------------------------------------

def apply_and_check(original_text: str, data: dict, propuestas: list[dict]) -> str:
    """Aplica las correcciones sobre `data` y verifica TODOS los invariantes.

    Devuelve el texto serializado nuevo. Lanza AssertionError si algo se rompe.
    """
    original = json.loads(original_text)  # copia intacta para comparar campo a campo
    n_before = len(data["albums"])

    # Aplica: cambia SOLO `artist`.
    ids_esperados = set()
    for r in propuestas:
        r["album"]["artist"] = r["art"]
        ids_esperados.add(r["id"])

    # Invariante: nº de álbumes idéntico.
    assert len(data["albums"]) == n_before, "cambió el nº de álbumes"
    assert len(data["albums"]) == len(original["albums"]), "nº de álbumes != original"

    # Invariante: SOLO cambia `artist`, y exactamente en las filas propuestas.
    campos = {"id", "artist", "title", "genre", "year", "tags", "url",
              "cover_url", "album_id"}
    ids_modificados = set()
    for nuevo, viejo in zip(data["albums"], original["albums"]):
        assert set(nuevo.keys()) == campos, f"esquema != 9 campos en id={nuevo.get('id')}"
        for k in campos:
            if k == "artist":
                if nuevo[k] != viejo[k]:
                    ids_modificados.add(nuevo["id"])
                continue
            assert nuevo[k] == viejo[k], (
                f"cambió el campo '{k}' en id={nuevo.get('id')} (solo se permite 'artist')"
            )
    # Top-level: artists/tags/years intactos.
    for k in ("artists", "tags", "years"):
        assert data.get(k) == original.get(k), f"cambió el bloque top-level '{k}'"

    assert ids_modificados == ids_esperados, (
        f"filas modificadas {len(ids_modificados)} != propuestas {len(ids_esperados)}"
    )
    assert len(ids_modificados) == len(propuestas), "conteo de modificaciones != propuestas"

    # Invariante de esquema del proyecto.
    validate(data)

    # Invariante de formato: mismo serializador; el diff solo toca líneas de artist.
    new_text = serialize(data)
    orig_lines = original_text.split("\n")
    new_lines = new_text.split("\n")
    assert len(orig_lines) == len(new_lines), (
        "cambió el nº de líneas del fichero (el formato no coincide: el diff sería enorme)"
    )
    diff_idx = [i for i in range(len(orig_lines)) if orig_lines[i] != new_lines[i]]
    assert len(diff_idx) == len(propuestas), (
        f"líneas cambiadas {len(diff_idx)} != propuestas {len(propuestas)}"
    )
    for i in diff_idx:
        assert '"artist":' in orig_lines[i] and '"artist":' in new_lines[i], (
            f"la línea {i+1} cambió y NO es un campo artist: {orig_lines[i]!r}"
        )
    return new_text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true",
                        help="genera el informe pero NO reescribe el canónico")
    args = parser.parse_args()

    original_text = CANONICAL.read_text(encoding="utf-8")
    data = json.loads(original_text)

    propuestas, exclusiones, existing = scan(data)
    report = build_report(propuestas, exclusiones, existing)

    DERIVED_DIR.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report, encoding="utf-8")

    new_text = apply_and_check(original_text, data, propuestas)

    # Resumen a stdout.
    from collections import Counter
    by_pat = Counter(r["patron"] for r in propuestas)
    cuentas = sorted({r["account_id"] for r in propuestas})
    nuevos = {fold(r["art"]) for r in propuestas}
    enlazables = len(nuevos & existing)
    print(f"Propuestas         : {len(propuestas)} "
          f"(P1={by_pat['P1']}, P2={by_pat['P2']}, P3={by_pat['P3']})")
    print(f"Sellos afectados   : {len(cuentas)} -> {', '.join(cuentas)}")
    print(f"Artistas distintos : {len(nuevos)} (ya existen / enlazables: {enlazables})")
    total_exc = sum(len(v) for v in exclusiones.values())
    print(f"Exclusiones        : {total_exc}")
    for motivo in EXC_ORDEN:
        print(f"    - {len(exclusiones.get(motivo, [])):>2}  {motivo}")
    print(f"Reconciliación     : {len(propuestas)} + {total_exc} = "
          f"{len(propuestas) + total_exc} títulos P1/P2/P3")
    print(f"Informe            : {REPORT.relative_to(REPO_ROOT)}")

    if args.dry_run:
        print("dry-run: canónico NO reescrito.")
        return 0

    if new_text != original_text:
        CANONICAL.write_text(new_text, encoding="utf-8")
        print(f"Canónico reescrito : {CANONICAL.relative_to(REPO_ROOT)} "
              f"({len(propuestas)} filas de artist)")
    else:
        print("Canónico sin cambios (ya corregido): no se reescribe.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
