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

Dos vías de entrada al índice (una cuenta entra si cumple CUALQUIERA):
  * umbral: >= 2 clusters de artista (el sello que publica a OTROS).
  * lexico: el account_id lleva un marcador léxico fuerte de sello (records,
    discos, diskak, ...). Caza al sello que se acredita A SÍ MISMO como artista:
    un solo cluster, no llegaba al umbral, era invisible (mendekudiskak,
    makramerecords, zirikaturecords...).
Son señales COMPLEMENTARIAS: el léxico AMPLÍA la entrada, no filtra ni expulsa a
nadie. Ninguna cuenta que entra por umbral puede salir por el léxico. Los flags
MARCAN casos para revisión humana, nunca descartan.

Deduplicación de artistas (dura):
  Se separan dos conceptos que NO se mezclan:
    * clave de dedup (fold): NFKD -> quitar diacríticos -> minúsculas ->
      eliminar todo lo que no sea [a-z0-9]. Solo sirve para AGRUPAR.
    * nombre visible (display): se conserva el string original tal cual.
  "artistas distintos" de una cuenta = nº de claves fold distintas (clusters).
  Esto no es criterio editorial, es escribir bien la comparación: sin ella,
  'BACKBONE'/'Backbone' o 'Belarmiñak'/'belarmiñak' contaban como dos artistas.
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter, defaultdict
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

# Various Artists / VA / V.A. / Various -> posible compilación o falso positivo.
# También VVAA y V.V.A.A. (forma habitual en castellano; caso real: cuenta `wldv`
# acredita "VVAA"). El orden de alternativas pone VVAA antes que VA para que no se
# quede a medias en el prefijo. Se mantienen puntos/espacios opcionales.
_VA_RE = re.compile(
    r"^(?:various artists|various|v\.?\s*v\.?\s*a\.?\s*a\.?|v\.?\s*a\.?)$",
    re.IGNORECASE,
)


def normalize_artist(raw: str) -> str:
    """Nombre visible normalizado: solo recorta y colapsa espacios.

    NO toca mayúsculas ni acentos: es el string que se muestra. La agrupación de
    "artistas distintos" NO usa esto, usa `fold()`.
    """
    return re.sub(r"\s+", " ", (raw or "").strip())


def fold(raw: str) -> str:
    """Clave de dedup: NFKD -> sin diacríticos -> minúsculas -> solo [a-z0-9].

    Solo para AGRUPAR, nunca se muestra. Colapsa a la misma clave variantes que
    son el mismo artista escrito distinto ('BACKBONE'/'Backbone',
    'Belarmiñak'/'belarmiñak', '6Jerseys'/'6jerseys').
    """
    decomposed = unicodedata.normalize("NFKD", raw or "")
    without_marks = "".join(c for c in decomposed if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", without_marks.lower())


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


def account_slug(account_id: str) -> str:
    """Fold del id de cuenta (sin el prefijo `custom:`), para comparar con folds
    de artistas en la regla `posible_autocuenta`."""
    ident = account_id[len("custom:"):] if account_id.startswith("custom:") else account_id
    return fold(ident)


# Marcadores léxicos FUERTES de sello. Segunda vía de entrada al índice: una
# cuenta con marcador entra aunque tenga un solo cluster de artista (el sello que
# se acredita a sí mismo). El orden importa: `marcadores` conserva este orden, así
# la salida es determinista.
#
# EXCLUIDOS a propósito (NO añadir "para pillar más"): "music", "musika", "sound",
# "audio" y "rec" suelto. Son demasiado genéricos y "rec" además casa DENTRO de
# palabras cualquiera (co-rec-ord, di-rec-t...), lo que dispararía falsos
# positivos a mansalva. Solo marcadores inequívocos de sello.
MARCADORES = (
    # inglés
    "records", "record", "recordings", "recording", "label", "tapes",
    # castellano
    "discos", "grabaciones", "ediciones", "producciones", "cintas", "sello",
    # euskera
    "diskak", "diskoak", "zintak", "banaketak", "ekoizpenak", "argitalpenak",
)


def account_lexico_key(account_id: str) -> str:
    """Cadena normalizada del account_id sobre la que se buscan marcadores:
    minúsculas + solo [a-z0-9]. Para cuentas `custom:` se quita el TLD antes de
    normalizar (crudobilbao.com -> crudobilbao), para no casar por el dominio."""
    ident = account_id[len("custom:"):] if account_id.startswith("custom:") else account_id
    if account_id.startswith("custom:"):
        parts = ident.rsplit(".", 1)  # separa el TLD final
        if len(parts) == 2 and parts[1]:
            ident = parts[0]
    return fold(ident)


def marcadores_hit(account_id: str) -> list[str]:
    """Marcadores que dispara el account_id (substring sobre la cadena
    normalizada). Devuelve la LISTA de marcadores, no un booleano, en el orden de
    MARCADORES para que sea determinista."""
    key = account_lexico_key(account_id)
    return [m for m in MARCADORES if m in key]


def lexico_subtipo(origen: str, flags: list[str]) -> str | None:
    """Subtipo de las entradas que entran SOLO por léxico (1 cluster de artista).
    Distingue las dos poblaciones que resultaron ser (medido: 14 vs 62):

      * "autoacreditada" : el sello firma como artista, así que posible_autocuenta
        dispara (mendekudiskak -> "Mendeku Diskak"). Es lo ESPERADO, no una alarma.
      * "acto_distinto"  : el único artista tiene nombre distinto al del sello
        (gondolinrecords -> "Lord Bakartia", meyorecords -> "VULK"); autocuenta no
        dispara. No es mala detección: es señal de que el scraper solo capturó UN
        acto de ese sello (cobertura incompleta).

    Para el resto de orígenes (umbral / ambos) no aplica: devuelve None.
    """
    if origen != "lexico":
        return None
    return "autoacreditada" if "posible_autocuenta" in flags else "acto_distinto"


def load_albums() -> list[dict]:
    with CANONICAL.open(encoding="utf-8") as fh:
        data = json.load(fh)
    return data["albums"]


def build_index(albums: list[dict]) -> dict:
    """Agrupa discos por cuenta y clusteriza artistas por clave fold.

    Cada cuenta guarda:
      kind, url, n_discos, album_ids(list),
      clusters : {fold_key -> Counter(display_original -> nº apariciones)}

    El Counter por cluster permite elegir luego el display más frecuente de forma
    determinista y conservar las variantes crudas sin perder dato.
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
                "clusters": defaultdict(Counter),
                "album_ids": [],
                "n_discos": 0,
            }
        display = normalize_artist(album.get("artist", ""))
        acc["clusters"][fold(display)][display] += 1
        acc["album_ids"].append(album.get("album_id"))
        acc["n_discos"] += 1

    return {"accounts": accounts, "huecos": huecos}


def cluster_display(counter: Counter) -> str:
    """Display determinista de un cluster: la forma original más frecuente;
    empate -> orden alfabético. Estable entre ejecuciones."""
    return sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]


def n_artistas(acc: dict) -> int:
    """Nº de artistas distintos de una cuenta = nº de clusters fold."""
    return len(acc["clusters"])


def account_flags(account_id: str, clusters: dict) -> list[str]:
    """Flags de caso frontera. MARCAN para revisión humana, NUNCA descartan.

    * borde_2artistas    : exactamente 2 clusters.
    * posible_VA         : algún display es Various Artists / VA / V.A. / Various
                           (posible compilación o falso positivo).
    * nombre_anidado     : exactamente 2 clusters donde el fold de uno está
                           contenido en el fold del otro. Caza featurings y alias
                           ('X' vs 'X eta lagunak', 'X' vs 'X featuring Y').
    * posible_autocuenta : el id de cuenta parece el nombre de uno de sus propios
                           artistas: fold(artista) == slug(account_id), o bien
                           fold(artista) contenido en slug(account_id) con
                           longitud > 4.

      OJO — posible_autocuenta tiene FALSOS POSITIVOS REALES y comprobados:
      dispara en sellos/colectivos legítimos que además editan bajo su propio
      nombre. Ejemplos reales: zaratazarautz (94 artistas), raperosdeemaus,
      josebairazoki, ensemblesinkro. Por eso es un flag de REVISIÓN HUMANA y
      NUNCA un descarte automático.

      NOTA sobre las entradas de origen "lexico" (1 solo cluster). Medido sobre el
      canónico, son DOS poblaciones distintas (ver `lexico_subtipo`):
        * 14 auto-acreditadas: el sello firma como artista (mendekudiskak ->
          "Mendeku Diskak"), así que posible_autocuenta SÍ dispara y ES LO
          ESPERADO, no una alarma: es justo por lo que el umbral no las veía.
        * 62 con acto de nombre distinto (gondolinrecords -> "Lord Bakartia",
          meyorecords -> "VULK"): posible_autocuenta NO dispara. No es mala
          detección: es señal de que el scraper solo ha capturado UN acto de ese
          sello (cobertura incompleta).
      (La predicción "dispara en casi todas" era optimista; el dato manda: 14/76.)
      borde_2artistas y nombre_anidado no aplican con 1 cluster: no se fuerzan,
      simplemente no disparan.
    """
    fold_keys = list(clusters.keys())
    displays = [cluster_display(counter) for counter in clusters.values()]

    flags: list[str] = []

    if len(fold_keys) == 2:
        flags.append("borde_2artistas")

    if any(is_various_artists(d) for d in displays):
        flags.append("posible_VA")

    if len(fold_keys) == 2:
        f0, f1 = fold_keys
        if f0 and f1 and (f0 in f1 or f1 in f0):
            flags.append("nombre_anidado")

    slug = account_slug(account_id)
    if slug:
        for fk in fold_keys:
            if not fk:
                continue
            if fk == slug or (len(fk) > 4 and fk in slug):
                flags.append("posible_autocuenta")
                break

    return flags


def cluster_records(clusters: dict) -> list[dict]:
    """Clusters de una cuenta en orden estable, con display elegido y variantes
    crudas (para no perder dato). Orden: por display, desempate por fold."""
    records = []
    for fk, counter in clusters.items():
        records.append(
            {
                "display": cluster_display(counter),
                "fold": fk,
                "n_discos": sum(counter.values()),
                "variantes": sorted(counter.keys()),
            }
        )
    records.sort(key=lambda r: (r["display"], r["fold"]))
    return records


def candidate_records(index: dict) -> list[dict]:
    """Lista de sellos candidatos, orden estable.

    Una cuenta entra si cumple CUALQUIERA de las dos vías:
      * umbral: >= MIN_ARTISTS clusters de artista.
      * lexico: el account_id lleva un marcador léxico fuerte de sello.
    Se anota el `origen` ("umbral" | "lexico" | "ambos") y qué `marcadores`
    dispararon (lista, vacía si ninguno). El léxico AMPLÍA, no expulsa: nadie que
    entre por umbral queda fuera por esto.

    Orden determinista: n_artistas desc, n_discos desc, account_id asc.
    """
    records: list[dict] = []
    for account_id, acc in index["accounts"].items():
        clusters = acc["clusters"]
        marcadores = marcadores_hit(account_id)

        por_umbral = len(clusters) >= MIN_ARTISTS
        por_lexico = bool(marcadores)
        if not (por_umbral or por_lexico):
            continue

        if por_umbral and por_lexico:
            origen = "ambos"
        elif por_umbral:
            origen = "umbral"
        else:
            origen = "lexico"

        cl = cluster_records(clusters)
        flags = account_flags(account_id, clusters)
        records.append(
            {
                "account_id": account_id,
                "url": acc["url"],
                "n_discos": acc["n_discos"],
                "n_artistas": len(clusters),
                "artistas": [c["display"] for c in cl],
                "clusters": cl,
                "album_ids": sorted(aid for aid in acc["album_ids"] if aid is not None),
                "origen": origen,
                "marcadores": marcadores,
                "lexico_subtipo": lexico_subtipo(origen, flags),
                "flags": flags,
            }
        )

    records.sort(key=lambda r: (-r["n_artistas"], -r["n_discos"], r["account_id"]))
    return records


def count_soft_candidates(index: dict) -> int:
    """Nº de candidatos con la normalización BLANDA anterior (solo trim + colapso
    de espacios, sin fold). Sirve para mostrar el delta antes/después de endurecer
    la comparación. Se calcula, no se hardcodea, para que siga siendo honesto."""
    total = 0
    for acc in index["accounts"].values():
        soft_distinct = set()
        for counter in acc["clusters"].values():
            soft_distinct.update(counter.keys())  # displays crudos distintos
        if len(soft_distinct) >= MIN_ARTISTS:
            total += 1
    return total


def build_report(index: dict, candidates: list[dict], total_albums: int) -> str:
    """Informe markdown legible para iPad."""
    accounts = index["accounts"]
    huecos = index["huecos"]

    total_accounts = len(accounts)
    n_candidates = len(candidates)
    n_soft = count_soft_candidates(index)
    discos_cubiertos = sum(c["n_discos"] for c in candidates)
    pct_catalogo = (100 * discos_cubiertos / total_albums) if total_albums else 0.0

    flag_counts: dict[str, int] = defaultdict(int)
    for c in candidates:
        for f in c["flags"]:
            flag_counts[f] += 1
    sin_flags = [c for c in candidates if not c["flags"]]

    origen_counts: dict[str, int] = defaultdict(int)
    for c in candidates:
        origen_counts[c["origen"]] += 1
    # Los que entraban solo por umbral (umbral + ambos) son los del índice previo;
    # el delta de esta pasada es lo que suma la vía léxica (origen == "lexico").
    n_umbral_prev = origen_counts["umbral"] + origen_counts["ambos"]
    solo_lexico = sorted(
        (c for c in candidates if c["origen"] == "lexico"),
        key=lambda c: (-c["n_discos"], c["account_id"]),
    )
    # Dos poblaciones dentro de las que entran solo por léxico (ver lexico_subtipo).
    lex_auto = [c for c in solo_lexico if c["lexico_subtipo"] == "autoacreditada"]
    lex_acto = [c for c in solo_lexico if c["lexico_subtipo"] == "acto_distinto"]

    # Cuentas con dominio propio (custom:), sean o no candidatas a sello.
    customs = sorted(
        (
            {
                "account_id": aid,
                "url": acc["url"],
                "n_discos": acc["n_discos"],
                "n_artistas": n_artistas(acc),
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

    a("# Índice de sellos (derivado, read-only)")
    a("")
    a("Dato derivado del subdominio de `url` en el canónico. Una cuenta entra en el "
      "índice por **cualquiera** de dos vías complementarias: **umbral** "
      f"(>= {MIN_ARTISTS} artistas distintos, el sello que publica a otros) o "
      "**léxico** (el account_id lleva un marcador fuerte de sello: `records`, "
      "`discos`, `diskak`...; caza al sello que se acredita a sí mismo). El léxico "
      "**amplía** la entrada, no filtra. Los flags MARCAN casos para revisión "
      "humana; **nunca descartan**.")
    a("")

    # --- Totales -----------------------------------------------------------
    a("## Totales")
    a("")
    a(f"- Cuentas totales (con cuenta atribuible): **{total_accounts}**")
    a(f"- **Candidatas a sello (total): {n_candidates}**")
    a(f"- Candidatos **antes / después** de añadir la vía léxica: "
      f"**{n_umbral_prev} → {n_candidates}** (+{origen_counts['lexico']})")
    a(f"- Discos cubiertos por candidatas: **{discos_cubiertos}** de {total_albums} "
      f"(**{pct_catalogo:.1f}%** del catálogo)")
    a(f"- Cuentas con dominio propio (`custom:`): **{len(customs)}**")
    a(f"- Huecos honestos (url vacía o `bandcamp.com`): **{len(huecos)}**")
    a("")
    a("### Desglose por origen de entrada")
    a("")
    a(f"- `umbral` (solo por >= {MIN_ARTISTS} artistas): **{origen_counts['umbral']}**")
    a(f"- `ambos` (umbral **y** marcador léxico): **{origen_counts['ambos']}**")
    a(f"- `lexico` (solo por marcador léxico; 1 cluster, antes invisibles): "
      f"**{origen_counts['lexico']}**")
    a("")
    a(f"> Nota: las {origen_counts['lexico']} entradas que entran **solo por "
      "léxico** (1 cluster) son **dos poblaciones distintas**, y conviene tratarlas "
      "aparte (detalle más abajo):")
    a(f">")
    a(f"> - **{len(lex_auto)} auto-acreditadas**: el sello firma como artista "
      "(`mendekudiskak` → \"Mendeku Diskak\"). Aquí `posible_autocuenta` dispara y "
      "**es lo esperado**, no una alarma: es justo por lo que el umbral no las veía.")
    a(f"> - **{len(lex_acto)} con acto de nombre distinto**: el único artista no es "
      "el sello (`gondolinrecords` → \"Lord Bakartia\", `meyorecords` → \"VULK\"). No "
      "disparan `posible_autocuenta`. No es mala detección: es señal de que el "
      "scraper solo ha capturado **un acto** de ese sello (cobertura incompleta).")
    a(">")
    a("> `borde_2artistas` y `nombre_anidado` no aplican con un solo cluster.")
    a("")
    a("Nota histórica: al endurecer la normalización de artistas los candidatos por "
      f"umbral pasaron de {n_soft} a {n_umbral_prev} (dedup dura por clave `fold`).")
    a("")
    a("### Recuento por flag (dentro de las candidatas)")
    a("")
    a(f"- `borde_2artistas` (exactamente 2 artistas): **{flag_counts['borde_2artistas']}**")
    a(f"- `posible_VA` (Various Artists / VA / V.A. / Various): **{flag_counts['posible_VA']}**")
    a(f"- `nombre_anidado` (2 clusters, uno contenido en el otro; featurings/alias): "
      f"**{flag_counts['nombre_anidado']}**")
    a(f"- `posible_autocuenta` (id de cuenta ≈ nombre de un artista propio; "
      f"tiene falsos positivos, revisión humana): **{flag_counts['posible_autocuenta']}**")
    a(f"- **Sin ningún flag** (sellos limpios): **{len(sin_flags)}**")
    a("")

    # --- Histograma --------------------------------------------------------
    a("## Histograma: cuentas por nº de discos")
    a("")
    a("| nº discos | nº cuentas |")
    a("| ---: | ---: |")
    for n_discos in sorted(hist):
        a(f"| {n_discos} | {hist[n_discos]} |")
    a("")

    # --- Entran solo por léxico (hallazgo de esta fase) -------------------
    a("## Entran solo por léxico")
    a("")
    a("Cuentas con un **solo** cluster de artista (no llegaban al umbral) que entran "
      "por llevar un marcador de sello en el account_id. Es el hallazgo principal de "
      f"esta fase: **{len(solo_lexico)}** cuentas antes invisibles. Son **dos "
      "poblaciones distintas** (campo `lexico_subtipo` en labels.json). Tablas "
      "ordenadas por nº de discos.")
    a("")

    def _tabla_lexico(rows: list[dict]) -> None:
        if not rows:
            a("_(ninguno)_")
            a("")
            return
        a("| account_id | n_discos | artista único | marcador(es) |")
        a("| :--- | ---: | :--- | :--- |")
        for c in rows:
            artista = c["artistas"][0] if c["artistas"] else ""
            marc = ", ".join(f"`{m}`" for m in c["marcadores"])
            a(f"| {c['account_id']} | {c['n_discos']} | {artista} | {marc} |")
        a("")

    a(f"### Auto-acreditadas — el sello firma como artista ({len(lex_auto)})")
    a("")
    a("`posible_autocuenta` dispara y **es lo esperado**: es justo el caso que el "
      "umbral no veía. Sellos reales acreditados a su propio nombre.")
    a("")
    _tabla_lexico(lex_auto)

    a(f"### Con acto de nombre distinto — cobertura incompleta ({len(lex_acto)})")
    a("")
    a("El único artista capturado no es el sello. No es mala detección: el scraper "
      "solo ha traído **un acto** de este sello, así que se ve como cuenta de un "
      "artista. Señal de **cobertura incompleta**, candidatos a re-scrapear.")
    a("")
    _tabla_lexico(lex_acto)

    # --- Lista completa de candidatas -------------------------------------
    a("## Sellos candidatos (orden: nº artistas desc, nº discos desc, account_id asc)")
    a("")
    a("| account_id | origen | n_discos | n_artistas | flags |")
    a("| :--- | :--- | ---: | ---: | :--- |")
    for c in candidates:
        flags = ", ".join(c["flags"]) if c["flags"] else "—"
        a(f"| {c['account_id']} | {c['origen']} | {c['n_discos']} | {c['n_artistas']} | {flags} |")
    a("")

    # --- Candidatas SIN flags ---------------------------------------------
    a("## Sin flags (sellos limpios, menos revisión)")
    a("")
    a("Candidatas que no disparan ninguna bandera: los sellos más claros.")
    a("")
    if sin_flags:
        a("| account_id | n_discos | n_artistas |")
        a("| :--- | ---: | ---: |")
        for c in sin_flags:
            a(f"| {c['account_id']} | {c['n_discos']} | {c['n_artistas']} |")
    else:
        a("_(ninguno)_")
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
    flag_counts: dict[str, int] = defaultdict(int)
    origen_counts: dict[str, int] = defaultdict(int)
    for c in candidates:
        origen_counts[c["origen"]] += 1
        for f in c["flags"]:
            flag_counts[f] += 1
    sin_flags = sum(1 for c in candidates if not c["flags"])
    n_umbral_prev = origen_counts["umbral"] + origen_counts["ambos"]
    print(f"Discos leídos            : {total_albums}")
    print(f"Cuentas totales          : {len(index['accounts'])}")
    print(f"Candidatos (umbral→total): {n_umbral_prev} → {len(candidates)} (+{origen_counts['lexico']} léxico)")
    print(f"  origen umbral          : {origen_counts['umbral']}")
    print(f"  origen ambos           : {origen_counts['ambos']}")
    print(f"  origen lexico          : {origen_counts['lexico']}")
    print(f"Cobertura catálogo       : {discos_cubiertos}/{total_albums} ({pct:.1f}%)")
    print(f"Dominios propios         : {sum(1 for a in index['accounts'].values() if a['kind'] == 'custom')}")
    print(f"Huecos honestos          : {len(index['huecos'])}")
    print(f"flag borde_2artistas     : {flag_counts['borde_2artistas']}")
    print(f"flag posible_VA          : {flag_counts['posible_VA']}")
    print(f"flag nombre_anidado      : {flag_counts['nombre_anidado']}")
    print(f"flag posible_autocuenta  : {flag_counts['posible_autocuenta']}")
    print(f"sin flags                : {sin_flags}")
    print(f"Escrito: {LABELS_JSON.relative_to(REPO_ROOT)}")
    print(f"Escrito: {LABELS_REPORT.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
