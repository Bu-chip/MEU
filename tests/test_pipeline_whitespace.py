"""Tests de pipeline.step_strip_whitespace (python3 -m unittest discover -s tests)."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import pipeline as P  # noqa: E402


def album(i, artist, title="Disco", tags=("rock",)):
    return {"id": i, "artist": artist, "title": title, "genre": "rock", "year": 2020,
            "tags": list(tags), "url": f"https://a.bandcamp.com/album/{i}",
            "cover_url": None, "album_id": None}


def dataset(albums):
    return {"albums": albums, "artists": sorted({a["artist"] for a in albums}),
            "tags": sorted({t for a in albums for t in a["tags"]}), "years": [2020]}


class StripWhitespace(unittest.TestCase):
    def test_recorta_artist_y_title_y_regenera_artists(self):
        data = dataset([album(1, "Calathea "), album(2, "Calathea", title=" Flowers "),
                        album(3, "QUANTUM9 ERA ")])
        msgs = P.step_strip_whitespace(data)
        self.assertEqual(msgs, ["strip_whitespace: 3 campos recortados"])
        self.assertEqual([a["artist"] for a in data["albums"]], ["Calathea", "Calathea", "QUANTUM9 ERA"])
        self.assertEqual(data["albums"][1]["title"], "Flowers")
        self.assertEqual(data["artists"], ["Calathea", "QUANTUM9 ERA"])

    def test_no_colapsa_espacios_internos_en_artist_ni_title(self):
        data = dataset([album(1, "M E R Y  M A Y", title=".   .  . ... .")])
        self.assertEqual(P.step_strip_whitespace(data), [])
        self.assertEqual(data["albums"][0]["artist"], "M E R Y  M A Y")
        self.assertEqual(data["albums"][0]["title"], ".   .  . ... .")

    def test_no_vacia_un_campo_que_solo_tiene_espacios(self):
        data = dataset([album(1, "   ")])
        self.assertEqual(P.step_strip_whitespace(data), [])
        self.assertEqual(data["albums"][0]["artist"], "   ")

    def test_tags_recorte_colapso_y_dedupe(self):
        data = dataset([album(1, "A", tags=("trap  flow", " punk", "punk", "alternative rock;  laudio"))])
        msgs = P.step_strip_whitespace(data)
        self.assertEqual(msgs, ["strip_whitespace: 1 campos recortados"])
        self.assertEqual(data["albums"][0]["tags"], ["trap flow", "punk", "alternative rock; laudio"])
        self.assertEqual(data["tags"], ["alternative rock; laudio", "punk", "trap flow"])

    def test_idempotente(self):
        data = dataset([album(1, "Calathea ", tags=("trap  flow",))])
        P.step_strip_whitespace(data)
        self.assertEqual(P.step_strip_whitespace(data), [])

    def test_esta_en_steps_antes_de_normalize_tags(self):
        names = [s.__name__ for s in P.STEPS]
        self.assertIn("step_strip_whitespace", names)
        self.assertLess(names.index("step_strip_whitespace"), names.index("step_normalize_tags"))


if __name__ == "__main__":
    unittest.main()
