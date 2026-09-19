"""Capa de localización del MEU — funciones puras (sin red, sin escritura).

Tres niveles separados, en este orden y sin colapsarlos nunca:

  1. OBSERVACIÓN  (data/locations/observations/*.json)
     Evidencia original tal cual la dio una fuente: el texto crudo de
     Bandcamp («Zarautz, Spain»), de qué release/cuenta sale, la URL y la
     fecha. Nunca se normaliza ni se corrige aquí.

  2. NORMALIZACIÓN  (data/locations/places.json + rules.json)
     Traduce cada TEXTO crudo a una categoría: resolved (municipio del
     registro), region_only, ambiguous, outside_scope, unexpected,
     invalid o unresolved. Es una función del texto, no del disco.

  3. RESOLUCIÓN  (data/locations/resolutions.json)
     Decide, para cada release del canónico, qué lugar usar y por qué
     (direct, same_account, artist_inferred, manual, region_only,
     outside_scope, tag_hint, unresolved), conservando la evidencia usada
     y la que contradice.

La ubicación de Bandcamp es la de la CUENTA QUE PUBLICA (grupo o sello) y
es la actual, sin fecha: el mapa describe asociaciones geográficas del
archivo, no residencias históricas.

Todo lo de este módulo es determinista: misma entrada → misma salida.
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter, defaultdict
from urllib.parse import urlparse

# ------------------------------------------------------------------
# Claves
# ------------------------------------------------------------------


def normalize_url(url):
    """Clave de URL: sin query/fragmento, host en minúsculas, sin / final.

    Idéntica a discover_tags.normalize_url (mismo dedupe que el scraper).
    """
    if not url:
        return None
    u = urlparse(url.split("?", 1)[0].split("#", 1)[0])
    return f"{u.netloc.lower()}{u.path.rstrip('/')}"


def release_key(album_id, url):
    """Clave estable de una release en las observaciones.

    `bc:<album_id>` si Bandcamp dio id (99,8 % del canónico); si no, la URL
    normalizada. Los candidatos aún no tienen `id` del canónico, por eso no
    se usa ese.
    """
    if album_id is not None:
        return f"bc:{album_id}"
    return f"url:{normalize_url(url)}"


def account_of(url):
    """Cuenta de Bandcamp que publica (misma derivación que labels_index).

    `subdominio` para *.bandcamp.com, `custom:<host>` para dominio propio,
    None si no hay URL atribuible.
    """
    host = urlparse((url or "").strip()).netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    if not host or host == "bandcamp.com":
        return None
    if host.endswith(".bandcamp.com"):
        return host[: -len(".bandcamp.com")]
    return f"custom:{host}"


def fold(raw):
    """Clave de agrupación de artistas (misma que labels_index.fold)."""
    decomposed = unicodedata.normalize("NFKD", raw or "")
    without_marks = "".join(c for c in decomposed if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", without_marks.lower())


def norm_text(s):
    """Normaliza texto de lugar para comparar: minúsculas, sin diacríticos,
    separadores (- / – _ . ') como espacio, espacios colapsados."""
    decomposed = unicodedata.normalize("NFKD", s or "")
    t = "".join(c for c in decomposed if not unicodedata.combining(c)).lower()
    t = re.sub(r"[\-/–—_.'’`()]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", norm_text(s)).strip("-")


# ------------------------------------------------------------------
# 1. Observaciones
# ------------------------------------------------------------------

OBS_SOURCE_DISCOVER = "bandcamp_discover"   # campo band_location de discover_web
OBS_SOURCE_PAGE = "bandcamp_page"           # <span class="location"> de la ficha
OBS_SUBJECT = "publishing_account"          # Bandcamp localiza la cuenta, no el disco


def observation(value, source_type, source_url, retrieved_at, provenance, **extra):
    """Una observación. `value` es el texto crudo (None = la fuente se
    consultó y no dio ubicación: hueco explícito, no ausencia de dato)."""
    obs = {
        "value": value,
        "source_type": source_type,
        "subject": OBS_SUBJECT,
        "account": account_of(source_url),
        "source_url": source_url,
        "retrieved_at": retrieved_at,
        "provenance": provenance,
    }
    obs.update({k: v for k, v in extra.items() if v is not None})
    return obs


def clean_value(raw):
    """Recorta espacios; vacío → None. No toca mayúsculas ni grafía."""
    if raw is None:
        return None
    raw = str(raw).strip()
    return raw or None


def observations_from_candidates(doc, provenance):
    """Observaciones de un fichero de candidatos (`candidates_YYYY-MM.json`).

    Recorre `candidates` y `deferred_oleada2`. Una fila sin la clave
    `band_location` (formato antiguo) no produce observación; una fila con
    `band_location: null` produce una observación de valor None (Bandcamp
    no daba ubicación).
    """
    out = defaultdict(list)
    for bucket in ("candidates", "deferred_oleada2"):
        for c in doc.get(bucket) or []:
            if "band_location" not in c:
                continue
            key = release_key(c.get("album_id"), c.get("url"))
            out[key].append(observation(
                clean_value(c.get("band_location")),
                OBS_SOURCE_DISCOVER,
                c.get("url"),
                (c.get("discovered_at") or "")[:10] or None,
                provenance,
            ))
    return dict(out)


def observations_from_pending(state, provenance):
    """Parciales pendientes de ficha en discovery_state.json (mismo formato)."""
    rows = list((state.get("pending_fichas") or {}).values())
    return observations_from_candidates({"candidates": rows}, provenance)


def _obs_identity(o):
    return (o.get("value"), o.get("source_type"), normalize_url(o.get("source_url")))


def merge_observations(*groups):
    """Une grupos {key: [obs]} sin perder nada.

    Dos observaciones son la misma si coinciden valor, tipo de fuente y URL:
    se conserva UNA, con la fecha más antigua y la procedencia del primer
    grupo en que apareció (los grupos se pasan de más a menos autorizado;
    el `meta` de cada fichero lista todas las fuentes leídas). Una
    observación distinta (otro valor) NUNCA pisa a otra: se añade.
    """
    merged = {}
    for group in groups:
        for key, lst in group.items():
            slot = merged.setdefault(key, {})
            for o in lst:
                ident = _obs_identity(o)
                prev = slot.get(ident)
                if prev is None:
                    o = dict(o)
                    if isinstance(o.get("provenance"), list):
                        o["provenance"] = o["provenance"][0] if o["provenance"] else None
                    slot[ident] = o
                    continue
                if o.get("retrieved_at") and (
                    not prev.get("retrieved_at") or o["retrieved_at"] < prev["retrieved_at"]
                ):
                    prev["retrieved_at"] = o["retrieved_at"]
    return {
        key: sorted(slot.values(), key=lambda o: (
            o.get("retrieved_at") or "", o.get("source_type") or "", o.get("value") or ""))
        for key, slot in sorted(merged.items())
    }


def drop_known(obs_by_key, known):
    """Quita de un grupo las observaciones ya presentes en `known`."""
    out = {}
    for key, lst in obs_by_key.items():
        idents = {_obs_identity(o) for o in known.get(key, [])}
        rest = [o for o in lst if _obs_identity(o) not in idents]
        if rest:
            out[key] = rest
    return out


def index_observations(obs_by_key):
    """Índices de búsqueda: por clave de release y por URL normalizada."""
    by_url = defaultdict(list)
    by_account = defaultdict(list)
    for key, lst in obs_by_key.items():
        for o in lst:
            nurl = normalize_url(o.get("source_url"))
            if nurl:
                by_url[nurl].append(o)
            if o.get("account"):
                by_account[o["account"]].append(o)
    return by_url, by_account


def observations_for_release(album, obs_by_key, by_url):
    """Observaciones sobre ESTA release: por album_id o por su URL."""
    seen = set()
    out = []
    candidates = []
    if album.get("album_id") is not None:
        candidates += obs_by_key.get(f"bc:{album['album_id']}", [])
    nurl = normalize_url(album.get("url"))
    if nurl:
        candidates += obs_by_key.get(f"url:{nurl}", [])
        candidates += by_url.get(nurl, [])
    for o in candidates:
        ident = _obs_identity(o)
        if ident not in seen:
            seen.add(ident)
            out.append(o)
    return out


def missing_candidate_observations(candidate_docs, obs_by_key):
    """Guardia de la fase 1: filas de candidatos con `band_location` cuya
    observación no está en data/locations/observations/. Devuelve la lista
    de (fichero, url, valor) que se perderían."""
    missing = []
    for name, doc in candidate_docs:
        for bucket in ("candidates", "deferred_oleada2"):
            for c in doc.get(bucket) or []:
                value = clean_value(c.get("band_location"))
                if value is None:
                    continue
                key = release_key(c.get("album_id"), c.get("url"))
                values = {o.get("value") for o in obs_by_key.get(key, [])}
                if value not in values:
                    missing.append((name, c.get("url"), value))
    return missing


# ------------------------------------------------------------------
# 2. Normalización de textos crudos
# ------------------------------------------------------------------

CATEGORIES = (
    "resolved",       # municipio del registro dentro del ámbito
    "region_only",    # solo región/país/comarca: no hay municipio
    "ambiguous",      # podría ser varias cosas; decisión humana
    "outside_scope",  # lugar real fuera de Euskal Herria
    "unexpected",     # topónimo vasco con país incoherente (Irun, Nigeria)
    "invalid",        # valor no geográfico o improbable (reglas manuales)
    "unresolved",     # sin regla: pendiente de revisión
)

SPAIN = {"spain", "espana", "espainia", "es"}
FRANCE = {"france", "frantzia", "francia", "fr"}


class Normalizer:
    """Traduce textos crudos de ubicación a categorías y lugares.

    places: lista de lugares del registro (data/locations/places.json).
    rules:  reglas controladas (data/locations/rules.json):
      - regions:  {region_id: {"name", "level", "territory"?, "aliases"}}
      - values:   {texto_crudo_exacto: {"category", "place"?, "region"?, "note"}}
                  (decisiones manuales por valor; mandan sobre todo lo demás)
      - outside:  [nombres normalizados de lugares reales fuera del ámbito
                  cuando el país dado es España o Francia]
    """

    def __init__(self, places, rules):
        self.places = {p["id"]: p for p in places}
        self.alias = {}
        for p in places:
            for name in [p["name"], *p.get("aliases", [])]:
                self.alias.setdefault(norm_text(name), p["id"])
        self.regions = rules.get("regions", {})
        self.region_alias = {}
        for rid, r in self.regions.items():
            for name in [r["name"], *r.get("aliases", [])]:
                self.region_alias.setdefault(norm_text(name), rid)
        self.value_rules = rules.get("values", {})
        self.outside = {norm_text(x) for x in rules.get("outside", [])}

    def place_for_text(self, text):
        return self.alias.get(norm_text(text))

    def classify(self, raw):
        """→ dict {category, place?, region?, reason}. Nunca lanza."""
        if raw is None:
            return {"category": "unresolved", "reason": "sin valor"}
        if raw in self.value_rules:
            r = dict(self.value_rules[raw])
            r.setdefault("reason", "regla manual por valor")
            r["reason"] = "manual: " + r.pop("note", r["reason"])
            return r
        whole = norm_text(raw)
        if not whole:
            return {"category": "unresolved", "reason": "vacío"}
        parts = [p.strip() for p in raw.split(",") if p.strip()]
        tail = norm_text(parts[-1]) if len(parts) > 1 else None
        head_parts = parts[:-1] if len(parts) > 1 else parts

        # Región entera («Basque Country, Spain», «PV, Spain», «Spain»).
        if whole in self.region_alias:
            return {"category": "region_only", "region": self.region_alias[whole],
                    "reason": "el valor completo es una región"}
        head = norm_text(", ".join(head_parts))
        if len(parts) == 1:
            if head in SPAIN:
                return {"category": "region_only", "region": "spain", "reason": "solo país"}
            if head in FRANCE:
                return {"category": "region_only", "region": "france", "reason": "solo país"}
        in_home_country = tail is None or tail in SPAIN or tail in FRANCE

        # Probar la cabeza entera y, si hay varias comas («Noáin, Navarra,
        # Spain»), su primer tramo.
        heads = [head]
        if len(head_parts) > 1:
            heads.append(norm_text(head_parts[0]))
        for h in heads:
            pid = self.alias.get(h)
            if pid:
                if in_home_country and self._country_ok(pid, tail):
                    return {"category": "resolved", "place": pid,
                            "reason": "alias del registro"}
                return {"category": "unexpected", "place_collision": pid,
                        "reason": f"topónimo del ámbito con país «{parts[-1]}»"}
            if h in self.region_alias and in_home_country:
                return {"category": "region_only", "region": self.region_alias[h],
                        "reason": "región/comarca, sin municipio"}
        if in_home_country:
            if any(h in self.outside for h in heads):
                return {"category": "outside_scope", "reason": "lugar fuera del ámbito"}
            return {"category": "unresolved",
                    "reason": "no está en el registro: revisar (¿municipio nuevo?)"}
        # País extranjero sin colisión con el ámbito.
        return {"category": "outside_scope", "reason": f"fuera de ES/FR ({parts[-1]})"}

    def _country_ok(self, pid, tail):
        if tail is None:
            return True
        country = self.places[pid].get("country")
        return (country == "ES" and tail in SPAIN) or (country == "FR" and tail in FRANCE)

    def tag_hint(self, tag):
        """Un tag es pista de lugar solo si coincide EXACTAMENTE con un
        nombre/alias del registro (o de una región). Nunca es resolución."""
        t = norm_text(tag)
        if t in self.alias:
            return ("place", self.alias[t])
        if t in self.region_alias:
            return ("region", self.region_alias[t])
        return None


# ------------------------------------------------------------------
# 3. Resolución por release
# ------------------------------------------------------------------

RESOLUTION_TYPES = (
    "manual",           # decisión humana registrada en manual.json
    "direct",           # Bandcamp, observado en ESTA release
    "same_account",     # Bandcamp, observado en otra release de la misma cuenta
    "artist_inferred",  # mismo artista (clave fold) en cuentas propias, unánime
    "region_only",      # solo región/país: sin municipio
    "outside_scope",    # lugar real fuera de Euskal Herria
    "tag_hint",         # SOLO un tag geográfico (nunca por defecto en el mapa)
    "unresolved",       # sin evidencia útil
)

PLACED_TYPES = ("manual", "direct", "same_account", "artist_inferred")


def _evidence(kind, o, cls):
    e = {
        "kind": kind,
        "value": o.get("value"),
        "category": cls["category"],
        "source_type": o.get("source_type"),
        "source_url": o.get("source_url"),
        "retrieved_at": o.get("retrieved_at"),
        "account": o.get("account"),
    }
    for k in ("place", "region"):
        if cls.get(k):
            e[k] = cls[k]
    return e


def _pick(evidence):
    """De varias evidencias del mismo nivel, la más reciente con valor."""
    with_value = [e for e in evidence if e["value"] is not None]
    if not with_value:
        return None
    return sorted(with_value, key=lambda e: (e.get("retrieved_at") or "", e["value"]))[-1]


def resolve_catalog(albums, obs_by_key, normalizer, label_accounts=frozenset(), manual=None):
    """Resolución de todo el canónico. → {id: resolución}.

    Orden de preferencia (el primero que dé municipio del ámbito gana; el
    resto de evidencia con otro lugar queda en `conflicts`):
      manual > direct > same_account > artist_inferred
      > (direct/same_account no municipales: region_only / outside_scope)
      > tag_hint > unresolved

    - artist_inferred solo se usa si TODAS las releases del mismo artista
      resueltas vía Bandcamp en cuentas que no son sello coinciden en un
      único municipio; si discrepan, no se infiere y se registra.
    - La ubicación de una cuenta-sello nunca se propaga al artista.
    """
    manual = manual or {}
    manual_rel = manual.get("releases", {})
    by_url, by_account = index_observations(obs_by_key)
    cls_cache = {}

    def classify(v):
        if v not in cls_cache:
            cls_cache[v] = normalizer.classify(v)
        return cls_cache[v]

    # Paso 1: evidencia Bandcamp por release (directa y de cuenta).
    base = {}
    for a in albums:
        acc = account_of(a.get("url"))
        direct_obs = observations_for_release(a, obs_by_key, by_url)
        direct_ids = {_obs_identity(o) for o in direct_obs}
        acc_obs = [o for o in by_account.get(acc, []) if _obs_identity(o) not in direct_ids] if acc else []
        base[a["id"]] = {
            "account": acc,
            "account_kind": "label" if acc in label_accounts else ("artist" if acc else None),
            "direct": [_evidence("direct", o, classify(o.get("value"))) for o in direct_obs],
            "same_account": [_evidence("same_account", o, classify(o.get("value"))) for o in acc_obs],
        }

    def municipal(evs):
        return [e for e in evs if e["category"] == "resolved"]

    # Paso 2: lugar Bandcamp por artista (solo cuentas no-sello).
    artist_places = defaultdict(Counter)
    artist_sources = defaultdict(list)
    for a in albums:
        b = base[a["id"]]
        if b["account_kind"] != "artist":
            continue
        chosen = _pick(municipal(b["direct"])) or _pick(municipal(b["same_account"]))
        if chosen:
            k = fold(a.get("artist"))
            artist_places[k][chosen["place"]] += 1
            artist_sources[k].append((a["id"], chosen))

    out = {}
    for a in albums:
        b = base[a["id"]]
        rid = a["id"]
        res = {
            "album_id": a.get("album_id"),
            "account": b["account"],
            "account_kind": b["account_kind"],
            "type": "unresolved",
            "place": None,
            "evidence": [],
            "conflicts": [],
        }
        all_evidence = b["direct"] + b["same_account"]

        # Pistas por tag (evidencia secundaria, siempre separadas).
        hints = []
        for t in a.get("tags", []):
            h = normalizer.tag_hint(t)
            if h and h[0] == "place" and h[1] not in hints:
                hints.append(h[1])
        if hints:
            res["tag_hints"] = hints

        chosen = None
        if str(rid) in manual_rel:
            m = manual_rel[str(rid)]
            res.update(type="manual", place=m.get("place"))
            res["evidence"].append({"kind": "manual", "place": m.get("place"),
                                    "note": m.get("note"), "decided_at": m.get("decided_at")})
            if m.get("category"):
                res["type"] = m["category"] if m["category"] in RESOLUTION_TYPES else "manual"
        else:
            chosen = _pick(municipal(b["direct"]))
            if chosen:
                res.update(type="direct", place=chosen["place"])
            else:
                chosen = _pick(municipal(b["same_account"]))
                if chosen:
                    res.update(type="same_account", place=chosen["place"])
            if not chosen:
                k = fold(a.get("artist"))
                places = artist_places.get(k)
                if places and len(places) == 1:
                    place = next(iter(places))
                    src = [s for s in artist_sources[k] if s[0] != rid]
                    if src:
                        res.update(type="artist_inferred", place=place)
                        res["evidence"].append({
                            "kind": "artist_inferred", "place": place,
                            "from_release_ids": sorted({s[0] for s in src})[:10],
                        })
                elif places and len(places) > 1:
                    res["conflicts"].append({
                        "kind": "artist_disagreement",
                        "places": sorted(places),
                    })
            if res["type"] == "unresolved":
                # Evidencia Bandcamp no municipal: región o fuera de ámbito.
                nonmun = _pick([e for e in b["direct"] if e["category"] in ("region_only", "outside_scope")]) \
                    or _pick([e for e in b["same_account"] if e["category"] in ("region_only", "outside_scope")])
                if nonmun:
                    chosen = nonmun
                    res["type"] = nonmun["category"]
                    if nonmun.get("region"):
                        res["region"] = nonmun["region"]
            if res["type"] == "unresolved" and len(hints) == 1:
                res.update(type="tag_hint", place=hints[0])
            elif res["type"] == "unresolved" and len(hints) > 1:
                res["conflicts"].append({"kind": "tag_hints_multiple", "places": hints})

        if chosen:
            res["evidence"].insert(0, chosen)
            res["value"] = chosen["value"]

        # Contradicciones: evidencia Bandcamp con otro municipio o categoría
        # problemática, y pistas de tag con otro municipio.
        for e in all_evidence:
            if e is chosen or e["value"] is None:
                continue
            if e["category"] == "resolved" and e.get("place") != res["place"]:
                res["conflicts"].append({"kind": e["kind"], "value": e["value"], "place": e["place"],
                                         "source_url": e["source_url"]})
            elif e["category"] in ("unexpected", "invalid", "ambiguous", "unresolved") and res["type"] != "manual":
                res["conflicts"].append({"kind": e["kind"], "value": e["value"],
                                         "category": e["category"], "source_url": e["source_url"]})
        if res["place"] and res["type"] != "tag_hint":
            other = [h for h in hints if h != res["place"]]
            if other and res["place"] not in hints:
                res["conflicts"].append({"kind": "tag", "places": other})
        # Evidencias vacías (Bandcamp consultado sin ubicación): trazables.
        if not all_evidence or all(e["value"] is None for e in all_evidence):
            if all_evidence:
                res["checked_empty"] = True
        # Deduplicar evidencias adicionales (máx. 5 de cuenta para no inflar).
        extra = [e for e in b["direct"] if e is not chosen]
        extra += [e for e in b["same_account"] if e is not chosen][:5]
        res["evidence"] += extra
        if not res["conflicts"]:
            del res["conflicts"]
        out[rid] = res
    return out


# ------------------------------------------------------------------
# 4. Análisis (municipio × tag)
# ------------------------------------------------------------------


def lift(count_in_place, place_total, count_global, global_total):
    """Sobrerrepresentación de un tag en un lugar respecto al archivo.

    lift = (releases del lugar con el tag / releases del lugar)
         / (releases del archivo con el tag / releases del archivo)

    1,0 = misma proporción que el archivo; 2,0 = el doble. Solo describe
    el archivo, no la escena real.
    """
    if not place_total or not count_global or not global_total:
        return 0.0
    return (count_in_place / place_total) / (count_global / global_total)


def overrepresented_tags(place_ids, albums_by_id, global_tag_counts, global_total,
                         min_count=3, limit=10, exclude=frozenset()):
    """Tags sobrerrepresentados en un conjunto de releases.

    Filtro mínimo `min_count` releases en el lugar para que un tag con 1
    disco no dé un ×40 espurio. Orden: lift desc, luego nº de releases.
    """
    total = len(place_ids)
    counts = Counter()
    for rid in place_ids:
        for t in set(albums_by_id[rid].get("tags", [])):
            if t not in exclude:
                counts[t] += 1
    rows = []
    for t, n in counts.items():
        if n < min_count:
            continue
        rows.append((t, n, lift(n, total, global_tag_counts[t], global_total)))
    rows.sort(key=lambda r: (-r[2], -r[1], r[0]))
    return rows[:limit]


def dumps_lines(mapping):
    """JSON con una entrada por línea: compacto y con diffs legibles."""
    items = [f"{json.dumps(str(k), ensure_ascii=False)}: "
             f"{json.dumps(v, ensure_ascii=False, sort_keys=True)}"
             for k, v in mapping.items()]
    return "{\n" + ",\n".join(items) + "\n}\n"
