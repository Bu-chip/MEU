#!/usr/bin/env python3
"""Índice de sellos (labels) como dato DERIVADO — Fase 1, READ-ONLY.

El subdominio de Bandcamp ya vive en el campo `url` de cada disco, así que la
"cuenta" (y por extensión el sello) es dato derivable sin tocar nada nuevo.

Este script LEE el canónico data/bandcamp_bilbaotags_clean.json y NO lo modifica
bajo ningún concepto. Escribe dos derivados en data/derived/:

  * labels.json        -> sellos candidatos (cuenta con >= 2 artistas distintos)
  * labels_report.md   -> informe legible (pensado para leer desde el iPad)

Idempotente: la salida es ordenada y determinista, así que re-ejecutar sobre el
mismo canónico produce byte a byte (y por tanto sha256) idéntico.

Definición de SELLO (matiz A): candidato = cuenta con >= 2 artistas distintos.
No se aplica ningún otro filtro automático.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

# ---------------------------------------------------------------------------
# Rutas. Se resuelven relativas a la raíz del repo (padre de scripts/) para que
# el script funcione igual desde cualquier cwd (terminal local o CI).
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
CANONICAL = REPO_ROOT / "data" / "bandcamp_bilbaotags_clean.json"
DERIVED_DIR = REPO_ROOT / "data" / "derived"
LABELS_JSON = DERIVED_DIR / "labels.json"
LABELS_REPORT = DERIVED_DIR / "labels_report.md"

# Umbral único que define "sello candidato". No hay más filtros (matiz A).
MIN_ARTISTS = 2

# Muestra de artistas por cuenta que se incluye en labels.json (los N primeros
# tras orden alfabético estable). No recorta la cuenta de artistas, solo la
# lista de ejemplo para que el JSON no crezca sin control.
ARTIST_SAMPLE_SIZE = 5

# Various Artists / VA / V.A. / Various -> posible compilación o falso positivo.
# El match es sobre el artista normalizado (trim + colapso de espacios).
_VA_RE = re.compile(r"^(?:various artists|various|v\.?\s*a\.?)$", re.IGNORECASE)


def normalize_artist(raw: str) -> str:
    """Normaliza un nombre de artista para comparar/deduplicar.

    Solo recorta y colapsa espacios: no se toca mayúsculas/acentos para no
    fusionar artistas distintos por error. La deduplicación de "artistas
    distintos" usa esta forma normalizada.
    """
    return re.sub(r"\s+", " ", (raw or "").strip())


def is_various_artists(name: str) -> bool:
    return bool(_VA_RE.match(normalize_artist(name)))


def derive_account(url: str) -> tuple[str, str | None]:
    """Deriva el id de cuenta desde la `url` del disco.

    Devuelve (kind, account_id):
      * ("bandcamp", "<subdominio>")   host `*.bandcamp.com`
      * ("custom",   "custom:<host>")  host propio (dominio propio, no bandcamp)
      * ("hueco",    None)             url vacía o exactamente bandcamp.com
    """
    host = urlparse((url or "").strip()).netloc.lower()
    if host.startswith("www."):
        host = host[4:]

    if not host or host == "bandcamp.com":
        # Hueco honesto: no se puede atribuir a una cuenta. No rompe el pipeline.
        return ("hueco", None)

    if host.endswith(".bandcamp.com"):
        subdomain = host[: -len(".bandcamp.com")]
        return ("bandcamp", subdomain)

    # Host propio (crudobilbao.com, ekiza.com, ...): son sellos con dominio
    # propio, no se descartan.
    return ("custom", f"custom:{host}")


def account_url(account_id: str, kind: str) -> str:
    """URL canónica de la cuenta a partir de su id derivado."""
    if kind == "custom":
        # account_id == "custom:<host>"
        host = account_id[len("custom:"):]
        return f"https://{host}"
    return f"https://{account_id}.bandcamp.com"


def load_albums() -> list[dict]:
    with CANONICAL.open(encoding="utf-8") as fh:
        data = json.load(fh)
    return data["albums"]


def build_index(albums: list[dict]) -> dict:
    """Agrupa discos por cuenta y calcula métricas por cuenta.

    Devuelve un dict con:
      accounts : {account_id -> {kind, url, n_discos, artistas(set),
                                 album_ids(list), primer orden estable}}
      huecos   : [discos sin cuenta atribuible]
    """
    accounts: dict[str, dict] = {}
    huecos: list[dict] = []

    for album in albums:
        kind, account_id = derive_account(album.get("url"))
        if kind == "hueco":
            huecos.append(album)
            continue

        acc = accounts.get(account_id)
        if acc is None:
            acc = accounts[account_id] = {
                "kind": kind,
                "url": account_url(account_id, kind),
                "artistas": set(),
                "album_ids": [],
                "n_discos": 0,
            }
        acc["artistas"].add(normalize_artist(album.get("artist", "")))
        acc["album_ids"].append(album.get("album_id"))
        acc["n_discos"] += 1

    return {"accounts": accounts, "huecos": huecos}


def account_flags(artistas: set[str]) -> list[str]:
    """Flags de caso frontera para una cuenta.

    * borde_2artistas : exactamente 2 artistas distintos
    * posible_VA      : algún artista es Various Artists / VA / V.A. / Various
    """
    flags: list[str] = []
    if len(artistas) == 2:
        flags.append("borde_2artistas")
    if any(is_various_artists(a) for a in artistas):
        flags.append("posible_VA")
    return flags


def candidate_records(index: dict) -> list[dict]:
    """Lista de sellos candidatos (>= MIN_ARTISTS artistas), orden estable.

    Orden determinista: por n_artistas desc, luego n_discos desc, luego
    account_id asc. Dentro de cada cuenta, artistas y album_ids van ordenados.
    """
    records: list[dict] = []
    for account_id, acc in index["accounts"].items():
        artistas = acc["artistas"]
        if len(artistas) < MIN_ARTISTS:
            continue
        artistas_sorted = sorted(artistas)
        records.append(
            {
                "account_id": account_id,
                "url": acc["url"],
                "n_discos": acc["n_discos"],
                "n_artistas": len(artistas),
                "artistas": artistas_sorted[:ARTIST_SAMPLE_SIZE],
                "album_ids": sorted(aid for aid in acc["album_ids"] if aid is not None),
                "flags": account_flags(artistas),
            }
        )

    records.sort(key=lambda r: (-r["n_artistas"], -r["n_discos"], r["account_id"]))
    return records


def build_report(index: dict, candidates: list[dict], total_albums: int) -> str:
    """Informe markdown legible para iPad."""
    accounts = index["accounts"]
    huecos = index["huecos"]

    total_accounts = len(accounts)
    n_candidates = len(candidates)
    discos_cubiertos = sum(c["n_discos"] for c in candidates)
    pct_catalogo = (100 * discos_cubiertos / total_albums) if total_albums else 0.0

    n_borde2 = sum(1 for c in candidates if "borde_2artistas" in c["flags"])
    n_va = sum(1 for c in candidates if "posible_VA" in c["flags"])

    # Cuentas con dominio propio (custom:), sean o no candidatas a sello.
    customs = sorted(
        (
            {
                "account_id": aid,
                "url": acc["url"],
                "n_discos": acc["n_discos"],
                "n_artistas": len(acc["artistas"]),
            }
            for aid, acc in accounts.items()
            if acc["kind"] == "custom"
        ),
        key=lambda r: (-r["n_discos"], r["account_id"]),
    )

    # Histograma de cuentas por nº de discos (todas las cuentas, no solo sellos).
    hist: dict[int, int] = defaultdict(int)
    for acc in accounts.values():
        hist[acc["n_discos"]] += 1

    lines: list[str] = []
    a = lines.append

    a("# Índice de sellos — Fase 1 (derivado, read-only)")
    a("")
    a("Dato derivado del subdominio de `url` en el canónico. Un **sello candidato** "
      f"es una cuenta con **>= {MIN_ARTISTS} artistas distintos** (matiz A, sin más filtros).")
    a("")

    # --- Totales -----------------------------------------------------------
    a("## Totales")
    a("")
    a(f"- Cuentas totales (con cuenta atribuible): **{total_accounts}**")
    a(f"- Candidatas a sello (>= {MIN_ARTISTS} artistas): **{n_candidates}**")
    a(f"- Discos cubiertos por candidatas: **{discos_cubiertos}** de {total_albums} "
      f"(**{pct_catalogo:.1f}%** del catálogo)")
    a(f"- Cuentas con dominio propio (`custom:`): **{len(customs)}**")
    a(f"- Huecos honestos (url vacía o `bandcamp.com`): **{len(huecos)}**")
    a("")
    a("### Casos frontera (dentro de las candidatas)")
    a("")
    a(f"- `borde_2artistas` (exactamente 2 artistas): **{n_borde2}**")
    a(f"- `posible_VA` (Various Artists / VA / V.A. / Various): **{n_va}**")
    a("")

    # --- Histograma --------------------------------------------------------
    a("## Histograma: cuentas por nº de discos")
    a("")
    a("| nº discos | nº cuentas |")
    a("| ---: | ---: |")
    for n_discos in sorted(hist):
        a(f"| {n_discos} | {hist[n_discos]} |")
    a("")

    # --- Lista completa de candidatas -------------------------------------
    a("## Sellos candidatos (orden: nº artistas desc)")
    a("")
    a("| account_id | n_discos | n_artistas | flags |")
    a("| :--- | ---: | ---: | :--- |")
    for c in candidates:
        flags = ", ".join(c["flags"]) if c["flags"] else "—"
        a(f"| {c['account_id']} | {c['n_discos']} | {c['n_artistas']} | {flags} |")
    a("")

    # --- Dominios propios --------------------------------------------------
    a("## Dominios propios (`custom:`)")
    a("")
    if customs:
        a("| account_id | n_discos | n_artistas |")
        a("| :--- | ---: | ---: |")
        for c in customs:
            a(f"| {c['account_id']} | {c['n_discos']} | {c['n_artistas']} |")
    else:
        a("_(ninguno)_")
    a("")

    # --- Huecos honestos ---------------------------------------------------
    a("## Huecos honestos (URLs sin subdominio)")
    a("")
    a("Discos cuya `url` está vacía o es exactamente `bandcamp.com`: no se pueden "
      "atribuir a una cuenta. Se listan aparte, no rompen el pipeline.")
    a("")
    if huecos:
        a("| id | artist | title | url |")
        a("| ---: | :--- | :--- | :--- |")
        for alb in sorted(huecos, key=lambda x: x.get("id", 0)):
            url = (alb.get("url") or "").strip() or "—"
            a(f"| {alb.get('id')} | {alb.get('artist', '')} | {alb.get('title', '')} | {url} |")
    else:
        a("_(ninguno)_")
    a("")

    return "\n".join(lines) + "\n"


def main() -> None:
    albums = load_albums()
    total_albums = len(albums)

    index = build_index(albums)
    candidates = candidate_records(index)
    report = build_report(index, candidates, total_albums)

    DERIVED_DIR.mkdir(parents=True, exist_ok=True)

    # JSON determinista: claves ordenadas, indent fijo, newline final.
    with LABELS_JSON.open("w", encoding="utf-8") as fh:
        json.dump(candidates, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")

    LABELS_REPORT.write_text(report, encoding="utf-8")

    # Resumen a stdout (útil en logs de CI y para el PR).
    discos_cubiertos = sum(c["n_discos"] for c in candidates)
    pct = (100 * discos_cubiertos / total_albums) if total_albums else 0.0
    n_borde2 = sum(1 for c in candidates if "borde_2artistas" in c["flags"])
    n_va = sum(1 for c in candidates if "posible_VA" in c["flags"])
    print(f"Discos leídos          : {total_albums}")
    print(f"Cuentas totales        : {len(index['accounts'])}")
    print(f"Sellos candidatos      : {len(candidates)}")
    print(f"Cobertura catálogo     : {discos_cubiertos}/{total_albums} ({pct:.1f}%)")
    print(f"Dominios propios       : {sum(1 for a in index['accounts'].values() if a['kind'] == 'custom')}")
    print(f"Huecos honestos        : {len(index['huecos'])}")
    print(f"Frontera borde_2artistas: {n_borde2}")
    print(f"Frontera posible_VA    : {n_va}")
    print(f"Escrito: {LABELS_JSON.relative_to(REPO_ROOT)}")
    print(f"Escrito: {LABELS_REPORT.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
