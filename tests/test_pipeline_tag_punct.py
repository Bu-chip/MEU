"""Tests de pipeline.step_strip_tag_punct (python3 -m unittest discover -s tests)."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import pipeline as P  # noqa: E402


def album(i, tags):
    return {"id": i, "artist": "A", "title": "T", "genre": "rock", "year": 2020,
            "tags": list(tags), "url": f"https://a.bandcamp.com/album/{i}",
            "cover_url": None, "album_id": None}


def dataset(*tag_lists):
    albums = [album(i, t) for i, t in enumerate(tag_lists, 1)]
    return {"albums": albums, "artists": ["A"],
            "tags": sorted({t for a in albums for t in a["tags"]}), "years": [2020]}


class FormaLimpia(unittest.TestCase):
    def test_recorta_punto_puntos_suspensivos_e_interrogacion(self):
        self.assertEqual(P.strip_trailing_punct("ambient."), "ambient")
        self.assertEqual(P.strip_trailing_punct("beats..."), "beats")
        self.assertEqual(P.strip_trailing_punct("swamp blues noise..."), "swamp blues noise")
        self.assertEqual(P.strip_trailing_punct("punk?"), "punk")

    def test_respeta_abreviaturas_preguntas_y_tags_limpios(self):
        for tag in ("a.o.r.", "méxico d.f.", "pi l.t.", "¿qué les dejaremos?", "oi!", "punk", "j.collin"):
            self.assertEqual(P.strip_trailing_punct(tag), tag, tag)

    def test_solo_puntuacion_queda_vacio(self):
        self.assertEqual(P.strip_trailing_punct("......."), "")
        self.assertEqual(P.strip_trailing_punct("???"), "??")


class StepStripTagPunct(unittest.TestCase):
    def test_solo_si_la_forma_limpia_existe(self):
        data = dataset(["ambient.", "blues etc.", "rock"], ["ambient", "punk?"])
        msgs = P.step_strip_tag_punct(data)
        self.assertEqual(msgs, ["strip_tag_punct: 1 álbumes con tags sin puntuación final (4 tags únicos)"])
        self.assertEqual(data["albums"][0]["tags"], ["ambient", "blues etc.", "rock"])
        self.assertEqual(data["albums"][1]["tags"], ["ambient", "punk?"])   # «punk» no existe: se deja
        self.assertEqual(data["tags"], ["ambient", "blues etc.", "punk?", "rock"])

    def test_deduplica_si_la_forma_limpia_ya_estaba_en_la_ficha(self):
        data = dataset(["ambient", "ambient."])
        P.step_strip_tag_punct(data)
        self.assertEqual(data["albums"][0]["tags"], ["ambient"])

    def test_no_toca_abreviaturas_ni_vacia_tags(self):
        data = dataset(["a.o.r.", "a.o.r", ".......", ""], ["¿qué les dejaremos?", "qué les dejaremos"])
        self.assertEqual(P.step_strip_tag_punct(data), [])
        self.assertEqual(data["albums"][0]["tags"], ["a.o.r.", "a.o.r", ".......", ""])

    def test_idempotente(self):
        data = dataset(["ambient.", "beats..."], ["ambient", "beats"])
        P.step_strip_tag_punct(data)
        self.assertEqual(P.step_strip_tag_punct(data), [])

    def test_va_despues_de_normalize_tags(self):
        names = [s.__name__ for s in P.STEPS]
        self.assertLess(names.index("step_normalize_tags"), names.index("step_strip_tag_punct"))


if __name__ == "__main__":
    unittest.main()
