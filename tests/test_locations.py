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


if __name__ == "__main__":
    unittest.main()
