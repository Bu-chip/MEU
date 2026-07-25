#!/usr/bin/env python3
"""Sonda de artistas ocultos en el `title` — Fase de MEDICIÓN, READ-ONLY.

Hallazgo que motiva esta sonda: algunos sellos se acreditan a sí mismos como
`artist` y esconden al artista real dentro del `title`. Ejemplos verificados en
el canónico:

    artist="Mendeku Diskak"    title='-015- REVERTT "Bermeo Skinhead Hardcore" 7"'
    artist="Zirikatu Records"  title='ZR04 - INZESTO "La Ciudad de los Muertos"'
    artist="makrame records"   title='Ashtray Navigations "The Banian Tree"'

REVERTT, INZESTO, Ashtray Navigations son actos reales que HOY no existen en el
mapa: aparecen bajo el nombre del sello.

Pero NO es universal. `blackvoguerecords` tiene títulos como "Diva EP", "Drop EP",
"Best Of BlackVogue Records": ahí no hay artista que extraer. Por eso esto se
MIDE antes de construir nada.

QUÉ HACE (y qué NO):
  * SOLO LEE el canónico data/bandcamp_bilbaotags_clean.json. NO extrae de verdad,
    NO corrige, NO escribe ningún artista en ningún sitio.
  * La ÚNICA salida es un informe legible: data/derived/probe_titulos.md.
  * NO escribe labels.json ni ningún fichero de datos.
  * Idempotente: salida ordenada y determinista -> sha256 idéntico al re-ejecutar.

Reutiliza la lógica de agrupación por cuenta y la clave de dedup `fold` de
scripts/labels_index.py (mismo criterio, sin duplicar).

LA TRAMPA DE LA COMILLA (leer antes de tocar ninguna regex):
El símbolo de pulgada de los formatos (7", 10", 12") es EL MISMO CARÁCTER que la
comilla recta de cierre ("). En '-015- REVERTT "Bermeo Skinhead Hardcore" 7"' hay
TRES comillas rectas, no dos. Por eso:
  1. Se normalizan las comillas tipográficas curvas (“ ” ‘ ’) a rectas ANTES de
     parsear (en el catálogo aparecen mezcladas, incluso `7”` como pulgada curva).
  2. La cola de formato (7"/10"/12"/LP/EP/MLP/Tape/Cassette/CD/Demo/Split/
     Promo Tape/One-Sided 12"...) se descarta ANTES de buscar el cierre del título,
     así el 7" final no se confunde con la comilla de cierre.

Los patrones se miden POR SEPARADO (cada uno con nombre propio), no en una sola
regex monstruo. Cada título se asigna a lo sumo a UN patrón (prioridad P1>P2>P3>
P5>P4), así los recuentos particionan sin doble conteo. La cobertura ALTA con
mucho ruido es PEOR que poca y limpia: por eso se miden también las extracciones
que producen basura (vacías, 1-2 caracteres, solo números, VA/VVAA).
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

# Reutilizamos la lógica ya escrita y probada en labels_index (mismo criterio de
# cuenta y misma clave de dedup). NO se duplica. El import no ejecuta nada: el
# main() de labels_index está bajo guarda `if __name__ == "__main__"`.
from labels_index import (  # noqa: E402
    derive_account,
    fold,
    is_various_artists,
    normalize_artist,
    account_slug,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
CANONICAL = REPO_ROOT / "data" / "bandcamp_bilbaotags_clean.json"
DERIVED_DIR = REPO_ROOT / "data" / "derived"
REPORT = DERIVED_DIR / "probe_titulos.md"

# Cuántos ejemplos reales mostrar por cada bloque del informe.
N_EJEMPLOS = 8
# Cuántas cuentas mostrar en la tabla "cuentas más afectadas".
N_CUENTAS = 30


# ---------------------------------------------------------------------------
# Normalización de comillas y descarte de la cola de formato.
# ---------------------------------------------------------------------------

# Comillas dobles curvas / bajas / primas -> comilla recta doble.
_DQUOTE = str.maketrans({
    "“": '"',  # “
    "”": '"',  # ”
    "„": '"',  # „
    "‟": '"',  # ‟
    "″": '"',  # ″ (doble prima, se usa como pulgada)
    "«": '"',  # «
    "»": '"',  # »
})
# Comillas simples curvas / prima -> comilla recta simple.
_SQUOTE = str.maketrans({
    "‘": "'",  # ‘
    "’": "'",  # ’
    "‚": "'",  # ‚
    "′": "'",  # ′
})


def normalize_quotes(title: str) -> str:
    """Normaliza comillas curvas a rectas y colapsa espacios.

    Deja el 7"/10"/12" intactos (la pulgada recta ya es `"`); la cola de formato
    se descarta aparte en `strip_format_tail`, no aquí.
    """
    s = (title or "").translate(_DQUOTE).translate(_SQUOTE)
    return re.sub(r"\s+", " ", s).strip()


# Un token de formato al final del título. Se descarta como cola.
# OJO: (?:7|10|12)" comparte carácter con la comilla de cierre; por eso se
# descarta ANTES de buscar el cierre del título.
_FORMAT_ALT = r"""(?:
      (?:one[-\s]?sided\s+)?(?:7|10|12)"      # 12", One-Sided 12"
    | flexi(?:\s*7")?                          # Flexi 7", Flexi
    | promo\s+tape                             # Promo Tape (antes que 'promo' y 'tape' sueltos)
    | promo\s+kasetea                          # caso real: MENDEKU DISKAK Promo Kasetea
    | one[-\s]?sided                           # One-Sided suelto
    | mlp | lp | ep | maxi | mcd | cdr | cd    # vinilos/cd
    | k7 | tape | cassette | kasetea | cinta   # cinta
    | demo | single | promo | split            # otras colas
)"""
# Cola: uno o más tokens de formato al final, opcionalmente entre paréntesis y
# separados por espacios. Se aplica de forma repetida (varios tokens: "Flexi 7"").
_TAIL_TOKEN = re.compile(
    r"\s*[\(\[]?\s*" + _FORMAT_ALT + r"\s*[\)\]]?\s*$",
    re.IGNORECASE | re.VERBOSE,
)
_SPLIT_WORD = re.compile(r"\bsplit\b", re.IGNORECASE)


def strip_format_tail(s: str) -> tuple[str, bool]:
    """Descarta la cola de formato del final. Devuelve (core, had_split).

    `had_split` recuerda si entre los tokens descartados había un "Split" (señal
    para el patrón P5, que se pierde al descartar la cola). Se descartan tokens
    de derecha a izquierda hasta que ya no queda formato: "Flexi 7"" -> quita 7"
    y luego Flexi; "One-Sided 12"" -> quita 12" y luego One-Sided.
    """
    had_split = bool(_SPLIT_WORD.search(s))
    prev = None
    core = s
    # Tope de seguridad para no bucle infinito; en la práctica bastan 2-3 vueltas.
    for _ in range(8):
        if core == prev:
            break
        prev = core
        core = _TAIL_TOKEN.sub("", core).strip()
    return core, had_split


# ---------------------------------------------------------------------------
# Prefijos de referencia y extracción por comillas / guion.
# ---------------------------------------------------------------------------

# P1: referencia numérica -001-, -015-, -086- ...
_REF_NUM = re.compile(r"^-\s*0*\d+\s*-\s+(?P<body>.+)$")
# P2: referencia alfanumérica ZR04, LADV166, FSR005, ER033, SM027 ... seguida de " - ".
_REF_ALNUM = re.compile(r"^[A-Za-z]{1,6}\d{1,5}\s*-\s+(?P<body>.+)$")

# ARTISTA "Título" -> la cola de formato ya se ha descartado, así que el string
# entero debe ser exactamente `algo "algo"`. El artista no puede llevar comillas.
_QUOTED = re.compile(r'^(?P<artist>[^"]+?)\s*"(?P<title>[^"]+)"\s*$')
# ARTISTA - Título (sin comillas en el core). Guion rodeado de espacios.
_DASHED = re.compile(r'^(?P<artist>[^"\-][^"]*?)\s+-\s+(?P<title>[^"].*)$')


def split_ref(core: str) -> tuple[str | None, str]:
    """Separa un prefijo de referencia. Devuelve (ref_kind, body).

    ref_kind: 'num' (-001-), 'alnum' (ZR04 - ) o None. body = core sin la ref.
    """
    m = _REF_NUM.match(core)
    if m:
        return "num", m.group("body").strip()
    m = _REF_ALNUM.match(core)
    if m:
        return "alnum", m.group("body").strip()
    return None, core


# Orden de patrones (prioridad). Cada título cae en el PRIMERO que casa.
PATRONES = [
    ("P1", "ref_guion_artista_comillas"),
    ("P2", "ref_alfanum_artista_comillas"),
    ("P3", "artista_comillas"),
    ("P5", "split"),
    ("P4", "artista_guion_titulo"),
]
PATRON_NOMBRE = dict(PATRONES)


def classify(title: str) -> dict | None:
    """Clasifica un título en a lo sumo UN patrón y devuelve la extracción.

    Devuelve dict con: patron ('P1'..'P5'), artists (lista de displays crudos),
    core, body. None si ningún patrón casa.

    Prioridad: quoted con ref numérica (P1) > quoted con ref alfanumérica (P2) >
    quoted sin ref (P3) > split (P5, requiere ' / ' Y keyword Split) > guion (P4).
    """
    core, had_split = strip_format_tail(normalize_quotes(title))
    if not core:
        return None
    ref_kind, body = split_ref(core)

    # --- Patrones por comillas (P1/P2/P3) ---------------------------------
    m = _QUOTED.match(body)
    if m:
        artist = m.group("artist").strip()
        if ref_kind == "num":
            patron = "P1"
        elif ref_kind == "alnum":
            patron = "P2"
        else:
            patron = "P3"
        return {"patron": patron, "artists": [artist], "core": core, "body": body}

    # --- Split (P5): dos artistas por ' / ' Y con keyword Split ------------
    # Definición del enunciado: "ARTISTA_A / ARTISTA_B Split [formato]".
    # Requiere AMBAS señales para no tragarse los cientos de ' / ' de letras.
    if had_split and " / " in body:
        partes = [p.strip() for p in body.split(" / ") if p.strip()]
        if len(partes) >= 2:
            return {"patron": "P5", "artists": partes, "core": core, "body": body}

    # --- Guion (P4): ARTISTA - Título, sin comillas -----------------------
    if '"' not in body:
        m = _DASHED.match(body)
        if m:
            artist = m.group("artist").strip()
            return {"patron": "P4", "artists": [artist], "core": core, "body": body}

    return None


# ---------------------------------------------------------------------------
# Control de calidad de la extracción (el ruido importa tanto como la cobertura).
# ---------------------------------------------------------------------------

def artist_problem(name: str, slug: str | None) -> str | None:
    """Motivo por el que un artista extraído es BASURA, o None si es limpio.

    Cubre justo lo que pide el enunciado: vacías, 1-2 caracteres, solo números o
    puntuación, y Various Artists / VVAA. Añade autocuenta (el "artista" extraído
    es el propio sello) como señal de recopilación/promo, no como extracción real.
    """
    n = normalize_artist(name)
    f = fold(n)
    if not f:
        return "vacío / solo puntuación"
    if len(f) < 3:
        return "1-2 caracteres"
    if re.fullmatch(r"\d+", f):
        return "solo números"
    if is_various_artists(n):
        return "Various Artists / VVAA"
    if slug and f == slug:
        return "coincide con el propio sello (autocuenta)"
    return None


def load_data() -> tuple[list[dict], set[str]]:
    """Devuelve (albums, existing_artist_folds).

    existing_artist_folds = folds de la lista canónica `artists` (los artistas que
    YA existen por su cuenta en el mapa). Sirve para medir cuántos artistas
    recuperados ya están y por tanto se podrían ENLAZAR sello<->artista.
    """
    with CANONICAL.open(encoding="utf-8") as fh:
        data = json.load(fh)
    albums = data["albums"]
    existing = {fold(a) for a in data.get("artists", []) if fold(a)}
    return albums, existing


# ---------------------------------------------------------------------------
# Medición.
# ---------------------------------------------------------------------------

def measure(albums: list[dict]) -> dict:
    """Recorre el canónico UNA vez y acumula todo lo medible, de forma ordenada.

    Cada disco se ancla a su cuenta (subdominio de url, mismo criterio que
    labels_index). Para cada disco se guarda su clasificación y, si extrae, si el
    artista es limpio o basura y por qué.
    """
    # account_id -> dict de estado
    accounts: dict[str, dict] = {}
    # patron -> lista de registros de ejemplo (orden determinista)
    por_patron: dict[str, list[dict]] = defaultdict(list)
    # motivo de basura -> lista de ejemplos
    basura: dict[str, list[dict]] = defaultdict(list)
    # casos ambiguos concretos
    quotes_no_sep: list[dict] = []   # comillas presentes pero NO separan artista
    slash_no_split: list[dict] = []  # ' / ' sin keyword Split (posible split sin marcar)
    split_w: list[dict] = []         # "Split w/ X"

    # Extracción limpia global: fold -> display elegido (más frecuente).
    clean_display: dict[str, Counter] = defaultdict(Counter)
    # album ids con extracción limpia (para contar discos), determinista.
    discos_limpios = 0

    _slash_re = re.compile(r"\s/\s")
    _splitw_re = re.compile(r"\bsplit\s+w/", re.IGNORECASE)

    for album in albums:
        kind, account_id = derive_account(album.get("url"))
        if account_id is None:
            account_id = "(hueco)"
        acc = accounts.get(account_id)
        if acc is None:
            acc = accounts[account_id] = {
                "kind": kind,
                "n_discos": 0,
                "n_match": 0,       # títulos que casan con algún patrón
                "n_limpio": 0,      # de esos, con artista limpio
                "por_patron": Counter(),
            }
        acc["n_discos"] += 1

        title = album.get("title", "") or ""
        slug = account_slug(account_id) if account_id != "(hueco)" else None
        res = classify(title)

        # Diagnóstico de ambigüedades (independiente de si casó un patrón).
        norm = normalize_quotes(title)
        if _splitw_re.search(norm):
            if len(split_w) < N_EJEMPLOS:
                split_w.append({"title": title, "account_id": account_id})

        if res is None:
            # ¿Comillas que NO separan artista? (título entrecomillado sin artista
            # delante, o comillas dentro del nombre del disco).
            body_core, _ = strip_format_tail(norm)
            if '"' in body_core and len(quotes_no_sep) < N_EJEMPLOS:
                quotes_no_sep.append({"title": title, "account_id": account_id})
            continue

        acc["n_match"] += 1
        acc["por_patron"][res["patron"]] += 1

        # Split (P5): multiartista, NO cuenta como extracción limpia de 1 artista.
        if res["patron"] == "P5":
            if len(por_patron["P5"]) < N_EJEMPLOS:
                por_patron["P5"].append({
                    "title": title,
                    "artist": " / ".join(res["artists"]),
                    "account_id": account_id,
                })
            continue

        # P1-P4: un solo artista. Control de calidad.
        artist = res["artists"][0]
        problema = artist_problem(artist, slug)
        if problema is None:
            acc["n_limpio"] += 1
            discos_limpios += 1
            f = fold(normalize_artist(artist))
            clean_display[f][normalize_artist(artist)] += 1
            if len(por_patron[res["patron"]]) < N_EJEMPLOS:
                por_patron[res["patron"]].append({
                    "title": title,
                    "artist": normalize_artist(artist),
                    "account_id": account_id,
                })
        else:
            if len(basura[problema]) < N_EJEMPLOS:
                basura[problema].append({
                    "title": title,
                    "artist": normalize_artist(artist) or "(vacío)",
                    "account_id": account_id,
                    "patron": res["patron"],
                })

        # ' / ' sin keyword Split (posible split no marcado -> ambiguo).
        if _slash_re.search(res["body"]) and res["patron"] != "P5":
            if len(slash_no_split) < N_EJEMPLOS:
                slash_no_split.append({
                    "title": title, "account_id": account_id, "patron": res["patron"],
                })

    return {
        "accounts": accounts,
        "por_patron": por_patron,
        "basura": basura,
        "quotes_no_sep": quotes_no_sep,
        "slash_no_split": slash_no_split,
        "split_w": split_w,
        "clean_display": clean_display,
        "discos_limpios": discos_limpios,
    }


def patron_stats(accounts: dict) -> dict[str, dict]:
    """Por patrón: nº de títulos y en cuántas cuentas distintas."""
    stats: dict[str, dict] = {code: {"titulos": 0, "cuentas": set()} for code, _ in PATRONES}
    for aid, acc in accounts.items():
        for code, n in acc["por_patron"].items():
            stats[code]["titulos"] += n
            stats[code]["cuentas"].add(aid)
    return stats


# ---------------------------------------------------------------------------
# Informe.
# ---------------------------------------------------------------------------

def _tabla_ejemplos(a, rows: list[dict], con_patron: bool = False) -> None:
    if not rows:
        a("_(sin ejemplos)_")
        a("")
        return
    if con_patron:
        a("| cuenta | patrón | título original | artista que se extraería |")
        a("| :--- | :--- | :--- | :--- |")
        for r in rows:
            a(f"| {r['account_id']} | {r.get('patron','')} | "
              f"`{r['title']}` | {r.get('artist','')} |")
    else:
        a("| cuenta | título original | artista que se extraería |")
        a("| :--- | :--- | :--- |")
        for r in rows:
            a(f"| {r['account_id']} | `{r['title']}` | {r.get('artist','')} |")
    a("")


def build_report(m: dict, total_albums: int, existing: set[str]) -> str:
    accounts = m["accounts"]
    stats = patron_stats(accounts)

    clean_display = m["clean_display"]
    new_folds = set(clean_display.keys())
    linkables = sorted(new_folds & existing)
    solo_nuevos = new_folds - existing
    discos_limpios = m["discos_limpios"]

    lines: list[str] = []
    a = lines.append

    a("# Sonda de artistas ocultos en el `title` (medición, read-only)")
    a("")
    a("Fase de **medición pura**. Lee el canónico `data/bandcamp_bilbaotags_clean.json` "
      "y NO escribe ni corrige nada: mide qué cobertura tendrían unos patrones que "
      "sacarían al artista real de dentro del `title` cuando el sello se acredita a sí "
      "mismo como `artist`. La única salida es este informe. **No se ha extraído, "
      "corregido ni escrito ningún artista.**")
    a("")
    a("Los patrones se miden por separado; cada título cae en **un solo** patrón "
      "(prioridad P1>P2>P3>P5>P4), así los recuentos particionan sin doble conteo. "
      "Antes de parsear se normalizan las comillas curvas a rectas y se descarta la "
      "cola de formato (7\"/12\"/LP/EP/Tape/Split...), porque la pulgada de `7\"` es el "
      "mismo carácter que la comilla de cierre.")
    a("")

    # --- Patrones ---------------------------------------------------------
    a("## Patrones y definición")
    a("")
    a("| patrón | nombre | forma | ejemplo |")
    a("| :--- | :--- | :--- | :--- |")
    a("| P1 | `ref_guion_artista_comillas` | `-001- ARTISTA \"Título\" [formato]` | `-015- REVERTT \"Bermeo Skinhead Hardcore\" 7\"` |")
    a("| P2 | `ref_alfanum_artista_comillas` | `ZR04 - ARTISTA \"Título\"` | `ZR04 - INZESTO \"La Ciudad de los Muertos\"` |")
    a("| P3 | `artista_comillas` | `ARTISTA \"Título\"` | `Ashtray Navigations \"The Banian Tree\"` |")
    a("| P4 | `artista_guion_titulo` | `ARTISTA - Título` | `Burial Hex - Pentecost` |")
    a("| P5 | `split` | `ARTISTA_A / ARTISTA_B Split [formato]` | `-086- REVERT / KOLPEKA Split 12\"` |")
    a("")

    a("## Cobertura por patrón")
    a("")
    a("Títulos que casan con cada patrón (asignación por prioridad, sin doble "
      "conteo) y en cuántas cuentas distintas aparece.")
    a("")
    a("| patrón | nombre | títulos | cuentas distintas |")
    a("| :--- | :--- | ---: | ---: |")
    for code, nombre in PATRONES:
        s = stats[code]
        a(f"| {code} | `{nombre}` | {s['titulos']} | {len(s['cuentas'])} |")
    total_match = sum(s["titulos"] for s in stats.values())
    a(f"| **Σ** | **cualquier patrón** | **{total_match}** | — |")
    a("")

    # --- Ejemplos por patrón ---------------------------------------------
    a("## Ejemplos reales por patrón")
    a("")
    a("Título original → artista que se extraería. P5 muestra los dos artistas del "
      "split (multiartista: NO cuenta como extracción de un artista).")
    a("")
    for code, nombre in PATRONES:
        a(f"### {code} · `{nombre}` — {stats[code]['titulos']} títulos")
        a("")
        _tabla_ejemplos(a, m["por_patron"].get(code, []))

    # --- Global -----------------------------------------------------------
    a("## Global")
    a("")
    pct_cat = (100 * discos_limpios / total_albums) if total_albums else 0.0
    a(f"- Discos con un artista **extraíble y limpio** (P1-P4, tras control de "
      f"calidad): **{discos_limpios}** de {total_albums} (**{pct_cat:.1f}%** del catálogo).")
    a(f"- Artistas **distintos** que aparecerían (clave `fold`): **{len(new_folds)}**.")
    a(f"- De esos, **ya existen** en el canónico como artista por su cuenta "
      f"(enlazables sello↔artista): **{len(linkables)}**.")
    a(f"- Artistas que serían **completamente nuevos** en el mapa: **{len(solo_nuevos)}**.")
    a("")
    a("> Los P5 (split) se cuentan aparte y **no** entran en el recuento de un "
      "artista: producen dos o más y se tratan como ambiguos (sección de fallos).")
    a("")

    if linkables:
        a("### Artistas recuperados que YA existen por su cuenta (muestra)")
        a("")
        a("Señal fuerte de que el sello y el artista se podrían enlazar: el nombre "
          "escondido en el `title` ya es un artista del mapa.")
        a("")
        a("| artista (fold) | display de la extracción |")
        a("| :--- | :--- |")
        for f in linkables[:20]:
            disp = clean_display[f].most_common(1)[0][0]
            a(f"| `{f}` | {disp} |")
        if len(linkables) > 20:
            a(f"| … | (+{len(linkables) - 20} más) |")
        a("")

    # --- Por cuenta -------------------------------------------------------
    a("## Cuentas más afectadas")
    a("")
    a("Cuentas ordenadas por nº de títulos que casan con algún patrón. El `% casa` "
      "sobre el total de títulos de la cuenta es lo que dice si un sello es "
      "**parseable** o no. `limpios` = extracciones que pasan el control de calidad.")
    a("")
    a("| cuenta | discos | casan | % casa | limpios | P1 | P2 | P3 | P4 | P5 |")
    a("| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    afectadas = sorted(
        (aid for aid in accounts if accounts[aid]["n_match"] > 0),
        key=lambda aid: (-accounts[aid]["n_match"], -accounts[aid]["n_discos"], aid),
    )
    for aid in afectadas[:N_CUENTAS]:
        acc = accounts[aid]
        pct = (100 * acc["n_match"] / acc["n_discos"]) if acc["n_discos"] else 0.0
        pp = acc["por_patron"]
        a(f"| {aid} | {acc['n_discos']} | {acc['n_match']} | {pct:.0f}% | "
          f"{acc['n_limpio']} | {pp.get('P1',0)} | {pp.get('P2',0)} | "
          f"{pp.get('P3',0)} | {pp.get('P4',0)} | {pp.get('P5',0)} |")
    a("")

    # --- Casos que fallan o son ambiguos ---------------------------------
    a("## Casos que fallan o son ambiguos")
    a("")
    a("Un patrón con mucha cobertura pero mucho ruido es PEOR que uno con poca y "
      "limpia. Esta sección lo hace visible.")
    a("")

    # Cuentas sin artista extraíble (blackvogue y similares).
    a("### Cuentas sin artista extraíble")
    a("")
    a("Cuentas con varios discos donde **ningún** título casa con un patrón: el "
      "artista no está escondido en el `title` (títulos tipo \"Diva EP\", "
      "\"Best Of…\"). Extraer aquí sería inventar. Umbral: ≥ 5 discos, 0 casan.")
    a("")
    sin_extraible = sorted(
        (aid for aid in accounts
         if accounts[aid]["n_match"] == 0 and accounts[aid]["n_discos"] >= 5
         and aid != "(hueco)"),
        key=lambda aid: (-accounts[aid]["n_discos"], aid),
    )
    if sin_extraible:
        a("| cuenta | discos | casan |")
        a("| :--- | ---: | ---: |")
        for aid in sin_extraible[:20]:
            a(f"| {aid} | {accounts[aid]['n_discos']} | 0 |")
    else:
        a("_(ninguna)_")
    a("")

    # Comillas que no separan artista.
    a("### Comillas que NO separan artista")
    a("")
    a("Títulos con `\"` donde delante NO hay un artista que extraer: el disco entero "
      "va entrecomillado, las comillas están dentro del nombre, o —el caso dominante "
      "en el catálogo— el `7\"`/`12\"` va como **prefijo de formato al inicio** "
      "(`7\" Hotter The Battle`), no como pulgada de cierre. Parsear por comillas aquí "
      "daría artista vacío o basura.")
    a("")
    _tabla_ejemplos_simple(a, m["quotes_no_sep"])

    # Splits y recopilatorios.
    a("### Splits y recopilatorios (varios artistas en un título)")
    a("")
    a(f"P5 casa **{stats['P5']['titulos']}** títulos con ' / ' **y** keyword `Split`. "
      "Producen 2+ artistas: no son una extracción de un artista. El propio P5 tiene "
      "**falsos positivos** cuando `Split` es parte del título entrecomillado o el "
      "' / ' separa una referencia de catálogo (p. ej. `... \"Split\" LP + CD / PT-04`), "
      "por eso se marca para tratar aparte, no para extraer. Además hay formas que NO "
      "casan P5 y quedan ambiguas:")
    a("")
    a("**' / ' sin keyword `Split`** (posible split o recopilación sin marcar; también "
      "letras con barra):")
    a("")
    _tabla_ejemplos(a, m["slash_no_split"], con_patron=True)
    a("**`Split w/ …`** (colaboración sin el segundo artista dentro del título):")
    a("")
    _tabla_ejemplos_simple(a, m["split_w"])

    # Basura por control de calidad.
    a("### Extracciones basura (control de calidad)")
    a("")
    a("Extracciones que un patrón SÍ produce pero que el control de calidad rechaza. "
      "Son el ruido que restaría fiabilidad si se extrajera a ciegas.")
    a("")
    basura = m["basura"]
    if basura:
        for motivo in sorted(basura.keys()):
            a(f"#### {motivo} ({len(basura[motivo])} ejemplos mostrados)")
            a("")
            _tabla_ejemplos(a, basura[motivo], con_patron=True)
    else:
        a("_(ninguna)_")
        a("")

    # --- Lectura honesta --------------------------------------------------
    a("## Lectura honesta de fiabilidad")
    a("")
    a("- **P1 / P2** (`-NNN-` / `ALNUM -` + comillas): las más fiables. La referencia "
      "de catálogo delante y las comillas alrededor del título dejan el artista sin "
      "ambigüedad. Cobertura baja pero limpia.")
    a("- **P3** (`ARTISTA \"Título\"`): fiable cuando las comillas separan de verdad; "
      "el riesgo es el título que va TODO entrecomillado (artista vacío), ya filtrado "
      "por el control de calidad.")
    a("- **P4** (`ARTISTA - Título`): el más **ruidoso**. El guion aparece en títulos "
      "normales; parte de lo que casa no es artista-título. Mirar la columna "
      "`limpios` vs `casan` por cuenta antes de fiarse.")
    a("- **P5** (`split`): NO es extracción de un artista; marca discos multiartista "
      "para tratar aparte. El ' / ' sin `Split` queda fuera a propósito (demasiado "
      "ruido de letras con barra).")
    a("")
    a("> Recordatorio de guardarraíl: si estos números salen muy distintos de lo "
      "esperado, manda el dato, no se ajustan los patrones para que quede bonito.")
    a("")

    return "\n".join(lines) + "\n"


def _tabla_ejemplos_simple(a, rows: list[dict]) -> None:
    if not rows:
        a("_(sin ejemplos)_")
        a("")
        return
    a("| cuenta | título original |")
    a("| :--- | :--- |")
    for r in rows:
        a(f"| {r['account_id']} | `{r['title']}` |")
    a("")


def main() -> None:
    albums, existing = load_data()
    total_albums = len(albums)
    m = measure(albums)
    report = build_report(m, total_albums, existing)

    DERIVED_DIR.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report, encoding="utf-8")

    # Resumen a stdout (útil en logs de CI y para el PR).
    stats = patron_stats(m["accounts"])
    new_folds = set(m["clean_display"].keys())
    linkables = len(new_folds & existing)
    print(f"Discos leídos             : {total_albums}")
    for code, nombre in PATRONES:
        s = stats[code]
        print(f"  {code} {nombre:<28}: {s['titulos']:>4} títulos / {len(s['cuentas'])} cuentas")
    print(f"Discos con artista limpio : {m['discos_limpios']}")
    print(f"Artistas nuevos (fold)    : {len(new_folds)}")
    print(f"  ya existen (enlazables) : {linkables}")
    print(f"  completamente nuevos    : {len(new_folds) - linkables}")
    print(f"Escrito: {REPORT.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
