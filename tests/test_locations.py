"""Tests de la capa de localización (python3 -m unittest discover tests)."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import locations_lib as L  # noqa: E402

CANON_FIELDS = ("id", "artist", "title", "genre", "year", "tags", "url", "cover_url", "album_id")


def candidate(url, album_id, loc, artist="Grupo", tags=(), discovered="2026-07-12T20:00:00Z"):
    return {"artist": artist, "title": "Disco", "genre": None, "year": 2020, "tags": list(tags),
            "url": url, "cover_url": None, "album_id": album_id, "band_location": loc,
            "source_tags": ["x"], "discovered_at": discovered}


def to_canon(c, new_id):
    """Proyección de un merge real: solo los 9 campos del esquema."""
    ficha = {k: c.get(k) for k in CANON_FIELDS if k != "id"}
    ficha["id"] = new_id
    return ficha


class PreservacionBandLocation(unittest.TestCase):
    def setUp(self):
        self.doc = {"candidates": [
            candidate("https://zarata.bandcamp.com/album/a?from=discover_page", 11, "Zarautz, Spain"),
            candidate("https://nadie.bandcamp.com/album/b", 12, None),
            candidate("https://sinid.bandcamp.com/album/c", None, "  Bilbao, Spain "),
        ], "deferred_oleada2": [candidate("https://baiona.bandcamp.com/album/d", 13, "Bayonne, France")]}

    def test_valor_crudo_sin_normalizar(self):
        obs = L.observations_from_candidates(self.doc, "data/candidates_x.json")
        self.assertEqual(obs["bc:11"][0]["value"], "Zarautz, Spain")
        self.assertEqual(obs["bc:11"][0]["subject"], "publishing_account")
        self.assertEqual(obs["bc:11"][0]["account"], "zarata")
        self.assertEqual(obs["bc:11"][0]["retrieved_at"], "2026-07-12")
        self.assertEqual(obs["url:sinid.bandcamp.com/album/c"][0]["value"], "Bilbao, Spain")
        self.assertIn("bc:13", obs, "la cola oleada-2 también se conserva")

    def test_null_es_hueco_explicito(self):
        obs = L.observations_from_candidates(self.doc, "p")
        self.assertIsNone(obs["bc:12"][0]["value"])

    def test_merge_de_canonico_no_pierde_ubicacion(self):
        """Un merge que solo copia los 9 campos no pierde la ubicación: la
        observación sigue encontrándose por album_id o por URL."""
        obs = L.observations_from_candidates(self.doc, "p")
        by_url, _ = L.index_observations(obs)
        canon = [to_canon(c, i) for i, c in enumerate(self.doc["candidates"])]
        self.assertNotIn("band_location", canon[0])
        found = L.observations_for_release(canon[0], obs, by_url)
        self.assertEqual([o["value"] for o in found], ["Zarautz, Spain"])
        found = L.observations_for_release(canon[2], obs, by_url)
        self.assertEqual([o["value"] for o in found], ["Bilbao, Spain"])

    def test_guardia_detecta_perdidas(self):
        missing = L.missing_candidate_observations([("f", self.doc)], {})
        self.assertEqual(len(missing), 3)  # los 3 con valor; el null no cuenta
        obs = L.observations_from_candidates(self.doc, "p")
        self.assertEqual(L.missing_candidate_observations([("f", self.doc)], obs), [])

    def test_union_sin_perdidas(self):
        a = L.observations_from_candidates(self.doc, "v1")
        doc2 = {"candidates": [candidate("https://zarata.bandcamp.com/album/a", 11, "Donostia, Spain",
                                         discovered="2026-09-01T00:00:00Z")]}
        b = L.observations_from_candidates(doc2, "v2")
        m = L.merge_observations(a, b, a)
        values = sorted(o["value"] for o in m["bc:11"])
        self.assertEqual(values, ["Donostia, Spain", "Zarautz, Spain"])
        z = [o for o in m["bc:11"] if o["value"] == "Zarautz, Spain"][0]
        self.assertEqual(z["provenance"], "v1", "misma observación repetida no se duplica")
        self.assertEqual(len(m["bc:11"]), 2)

    def test_idempotente(self):
        a = L.observations_from_candidates(self.doc, "v1")
        once = L.merge_observations(a)
        self.assertEqual(L.merge_observations(once, a), once)


# ------------------------------------------------------------------
# Normalización (fase 4)
# ------------------------------------------------------------------

PLACES = [
    {"id": "donostia", "name": "Donostia", "country": "ES", "territory": "Gipuzkoa",
     "aliases": ["San Sebastián", "Donostia San Sebastián", "San Sebastián Donostia", "Donosti"]},
    {"id": "bilbo", "name": "Bilbo", "country": "ES", "territory": "Bizkaia", "aliases": ["Bilbao"]},
    {"id": "zarautz", "name": "Zarautz", "country": "ES", "territory": "Gipuzkoa", "aliases": ["Zarauz"]},
    {"id": "irunea", "name": "Iruñea", "country": "ES", "territory": "Nafarroa", "aliases": ["Pamplona", "Iruña"]},
    {"id": "irun", "name": "Irun", "country": "ES", "territory": "Gipuzkoa", "aliases": ["Irún"]},
    {"id": "gernika-lumo", "name": "Gernika-Lumo", "country": "ES", "territory": "Bizkaia",
     "aliases": ["Guernica", "Gernika"]},
    {"id": "getaria-gipuzkoa", "name": "Getaria", "country": "ES", "territory": "Gipuzkoa", "aliases": []},
    {"id": "getaria-iparralde", "name": "Getaria", "country": "FR", "territory": "Iparralde",
     "aliases": ["Guéthary"]},
    {"id": "baiona", "name": "Baiona", "country": "FR", "territory": "Iparralde", "aliases": ["Bayonne"]},
]
RULES = {
    "regions": {
        "euskal-herria": {"name": "Euskal Herria", "aliases": ["Basque Country", "Euskadi", "PV"]},
        "nafarroa": {"name": "Nafarroa", "aliases": ["Navarra", "Navarre"]},
        "spain": {"name": "Spain", "aliases": ["Spain"]},
        "france": {"name": "France", "aliases": ["France"]},
    },
    "outside": ["Madrid"],
    "values": {"Afghanistan": {"category": "invalid", "note": "no literal"}},
}


class Normalizacion(unittest.TestCase):
    def setUp(self):
        self.n = L.Normalizer(PLACES, RULES)

    def cat(self, raw):
        return self.n.classify(raw)

    def test_aliases(self):
        for raw in ["Donostia", "Donosti", "San Sebastian", "San Sebastián",
                    "Donostia-San Sebastián, Spain", "Donostia / San Sebastián, Spain",
                    "Donostia San Sebastian, Spain", "donostia, spain"]:
            self.assertEqual(self.cat(raw), {**self.cat(raw), "category": "resolved", "place": "donostia"}, raw)
        for raw in ["Bilbo", "Bilbao, Spain"]:
            self.assertEqual(self.cat(raw)["place"], "bilbo")
        for raw in ["Gernika", "Guernica, Spain"]:
            self.assertEqual(self.cat(raw)["place"], "gernika-lumo")

    def test_desempate_por_pais(self):
        self.assertEqual(self.cat("Getaria, Spain")["place"], "getaria-gipuzkoa")
        self.assertEqual(self.cat("Getaria, France")["place"], "getaria-iparralde")
        self.assertEqual(self.cat("Getaria")["category"], "ambiguous")

    def test_region_only_nunca_municipio(self):
        for raw in ["Spain", "France", "Basque Country", "Basque Country, Spain", "Euskadi, Spain",
                    "PV, Spain", "PV", "Navarra, Spain", "Euskal Herria"]:
            c = self.cat(raw)
            self.assertEqual(c["category"], "region_only", raw)
            self.assertNotIn("place", c, raw)

    def test_fuera_de_ambito_y_colisiones(self):
        self.assertEqual(self.cat("Madrid, Spain")["category"], "outside_scope")
        self.assertEqual(self.cat("Berlin, Germany")["category"], "outside_scope")
        for raw in ["Pamplona, Colombia", "Irun, Nigeria", "Navarre, Florida", "San Sebastián, Chile"]:
            c = self.cat(raw)
            self.assertEqual(c["category"], "unexpected", raw)
            self.assertNotIn("place", c, raw)

    def test_desconocido_queda_pendiente(self):
        self.assertEqual(self.cat("Deusto, Spain")["category"], "unresolved")
        self.assertEqual(self.cat(None)["category"], "unresolved")

    def test_regla_manual_por_valor(self):
        self.assertEqual(self.cat("Afghanistan")["category"], "invalid")

    def test_tag_hint_solo_por_coincidencia_exacta(self):
        self.assertEqual(self.n.tag_hint("bilbao"), ("place", "bilbo"))
        self.assertEqual(self.n.tag_hint("basque country"), ("region", "euskal-herria"))
        self.assertIsNone(self.n.tag_hint("bilbao techno"))
        self.assertIsNone(self.n.tag_hint("noise"))


# ------------------------------------------------------------------
# Resolución (fase 5)
# ------------------------------------------------------------------

def album(id_, url, album_id, artist="A", tags=()):
    return {"id": id_, "artist": artist, "title": "t", "genre": None, "year": 2010,
            "tags": list(tags), "url": url, "cover_url": None, "album_id": album_id}


class Resolucion(unittest.TestCase):
    def setUp(self):
        self.n = L.Normalizer(PLACES, RULES)

    def resolve(self, albums, cands, labels=frozenset(), manual=None):
        obs = L.observations_from_candidates({"candidates": cands}, "t")
        return L.resolve_catalog(albums, obs, self.n, labels, manual)

    def test_directa_gana_y_tag_contradictorio_se_registra(self):
        """Ejemplo del encargo: Bandcamp Zarautz + tag donostia."""
        a = [album(1, "https://g.bandcamp.com/album/x", 11, tags=["noise", "donostia"])]
        r = self.resolve(a, [candidate(a[0]["url"], 11, "Zarautz, Spain")])[1]
        self.assertEqual((r["type"], r["place"]), ("direct", "zarautz"))
        self.assertEqual(r["tag_hints"], ["donostia"])
        self.assertIn({"kind": "tag", "places": ["donostia"]}, r["conflicts"])

    def test_misma_cuenta(self):
        a = [album(1, "https://g.bandcamp.com/album/x", 11), album(2, "https://g.bandcamp.com/album/y", 12)]
        r = self.resolve(a, [candidate(a[0]["url"], 11, "Bilbao, Spain")])
        self.assertEqual((r[2]["type"], r[2]["place"]), ("same_account", "bilbo"))

    def test_inferencia_por_artista_unanime_y_sin_sellos(self):
        a = [album(1, "https://grupo.bandcamp.com/album/x", 11, artist="Kaos"),
             album(2, "https://sello.bandcamp.com/album/y", 12, artist="KAOS"),
             album(3, "https://sello.bandcamp.com/album/z", 13, artist="Otro")]
        cands = [candidate(a[0]["url"], 11, "Irun, Spain")]
        r = self.resolve(a, cands, labels=frozenset({"sello"}))
        self.assertEqual((r[2]["type"], r[2]["place"]), ("artist_inferred", "irun"))
        self.assertEqual(r[3]["type"], "unresolved", "la ubicación del artista no pasa a otro artista del sello")

    def test_ubicacion_de_sello_no_se_propaga_al_artista(self):
        a = [album(1, "https://sello.bandcamp.com/album/x", 11, artist="Kaos"),
             album(2, "https://kaos.bandcamp.com/album/y", 12, artist="Kaos")]
        r = self.resolve(a, [candidate(a[0]["url"], 11, "Zarautz, Spain")], labels=frozenset({"sello"}))
        self.assertEqual(r[1]["type"], "direct")
        self.assertEqual(r[1]["account_kind"], "label")
        self.assertEqual(r[2]["type"], "unresolved")

    def test_artistas_en_desacuerdo_no_se_infiere(self):
        a = [album(1, "https://a1.bandcamp.com/album/x", 11, artist="Kaos"),
             album(2, "https://a2.bandcamp.com/album/y", 12, artist="Kaos"),
             album(3, "https://sello.bandcamp.com/album/z", 13, artist="Kaos")]
        cands = [candidate(a[0]["url"], 11, "Irun, Spain"), candidate(a[1]["url"], 12, "Bilbao, Spain")]
        r = self.resolve(a, cands, labels=frozenset({"sello"}))
        self.assertEqual(r[3]["type"], "unresolved")
        self.assertEqual(r[3]["conflicts"][0]["kind"], "artist_disagreement")

    def test_region_fuera_y_tag_hint(self):
        a = [album(1, "https://r.bandcamp.com/album/x", 11),
             album(2, "https://m.bandcamp.com/album/y", 12),
             album(3, "https://t.bandcamp.com/album/z", 13, tags=["bilbao", "punk"]),
             album(4, "https://c.bandcamp.com/album/w", 14, tags=["irun"])]
        cands = [candidate(a[0]["url"], 11, "Basque Country, Spain"),
                 candidate(a[1]["url"], 12, "Madrid, Spain"),
                 candidate(a[3]["url"], 14, "Irun, Nigeria")]
        r = self.resolve(a, cands)
        self.assertEqual((r[1]["type"], r[1]["place"], r[1]["region"]), ("region_only", None, "euskal-herria"))
        self.assertEqual((r[2]["type"], r[2]["place"]), ("outside_scope", None))
        self.assertEqual((r[3]["type"], r[3]["place"]), ("tag_hint", "bilbo"))
        self.assertEqual(r[4]["rejected_values"], {"Irun, Nigeria": "unexpected"})
        self.assertEqual(r[4]["type"], "tag_hint", "la colisión no se acepta; queda solo la pista")

    def test_manual_manda(self):
        a = [album(1, "https://g.bandcamp.com/album/x", 11)]
        manual = {"releases": {"1": {"place": "baiona", "note": "confirmado"}}}
        r = self.resolve(a, [candidate(a[0]["url"], 11, "Zarautz, Spain")], manual=manual)[1]
        self.assertEqual((r["type"], r["place"]), ("manual", "baiona"))


class Metrica(unittest.TestCase):
    def test_lift(self):
        self.assertAlmostEqual(L.lift(10, 100, 50, 5000), 10.0)
        self.assertEqual(L.lift(1, 0, 1, 1), 0.0)


class RegistroReal(unittest.TestCase):
    """Regresión sobre data/locations/places.json + rules.json reales."""

    @classmethod
    def setUpClass(cls):
        import json
        root = Path(__file__).resolve().parent.parent / "data" / "locations"
        places = json.loads((root / "places.json").read_text(encoding="utf-8"))["places"]
        rules = json.loads((root / "rules.json").read_text(encoding="utf-8"))
        cls.n = L.Normalizer(places, rules)

    def test_casos_reales(self):
        casos = {
            "Donostia San Sebastian, Spain": ("resolved", "donostia"),
            "Donostia / San Sebastián, Spain": ("resolved", "donostia"),
            "San Sebastián, Spain": ("resolved", "donostia"),
            "Vitoria Gasteiz, Spain": ("resolved", "gasteiz"),
            "Pamplona, Spain": ("resolved", "irunea"),
            "Bilbo, Spain": ("resolved", "bilbo"),
            "Guernica, Spain": ("resolved", "gernika-lumo"),
            "Getaria, Spain": ("resolved", "getaria-gipuzkoa"),
            "Cambo Les Bains, France": ("resolved", "kanbo"),
            "Alsasua – Altsasu, Spain": ("resolved", "altsasu"),
            "Ereñotzu, Spain": ("resolved", "hernani"),
        }
        for raw, (cat, place) in casos.items():
            c = self.n.classify(raw)
            self.assertEqual((c["category"], c.get("place")), (cat, place), raw)

    def test_codigos_iso_y_regiones(self):
        self.assertEqual(self.n.classify("NC, Spain")["region"], "nafarroa")
        self.assertEqual(self.n.classify("PV, Spain")["region"], "euskal-herria")
        self.assertEqual(self.n.classify("CT, Spain")["category"], "outside_scope")
        self.assertEqual(self.n.classify("Basque Country, France")["region"], "iparralde")

    def test_aberraciones_reales(self):
        for raw in ("Pamplona, Colombia", "Irun, Nigeria", "Navarre, Florida", "Guernica, Argentina"):
            self.assertEqual(self.n.classify(raw)["category"], "unexpected", raw)
        self.assertEqual(self.n.classify("Afghanistan")["category"], "invalid")
        self.assertEqual(self.n.classify("Madrid, Spain")["category"], "outside_scope")


if __name__ == "__main__":
    unittest.main()
