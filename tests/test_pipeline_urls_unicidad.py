"""Tests de pipeline.clean_url / step_clean_urls y de las guardas de unicidad
de validate() (python3 -m unittest discover -s tests)."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import pipeline as P  # noqa: E402


def album(i, url, album_id=None):
    return {"id": i, "artist": "A", "title": "T", "genre": "rock", "year": 2020,
            "tags": ["rock"], "url": url, "cover_url": None, "album_id": album_id}


def dataset(albums):
    return {"albums": albums, "artists": ["A"], "tags": ["rock"], "years": [2020]}


class CleanUrl(unittest.TestCase):
    def test_variantes_sucias(self):
        limpia = "https://grupo.bandcamp.com/album/disco"
        for sucia in ("https://grupo.bandcamp.com/album/disco?from=search&search_sig=abc",
                      "https://grupo.bandcamp.com/album/disco#top",
                      "https://grupo.bandcamp.com/album/disco/",
                      "  https://grupo.bandcamp.com/album/disco ",
                      "https://grupo.bandcamp.com/album/ disco",
                      "http://grupo.bandcamp.com/album/disco",
                      "https://GRUPO.Bandcamp.com/album/disco",
                      "HTTP://Grupo.bandcamp.com/album/disco/?from=x#y"):
            self.assertEqual(P.clean_url(sucia), limpia, sucia)

    def test_respeta_limpias_nulas_y_path(self):
        self.assertEqual(P.clean_url("https://crudobilbao.com/album/loyal"), "https://crudobilbao.com/album/loyal")
        self.assertEqual(P.clean_url("https://a.bandcamp.com/album/Con-Mayus"), "https://a.bandcamp.com/album/Con-Mayus")
        self.assertIsNone(P.clean_url(None))
        self.assertEqual(P.clean_url(""), "")

    def test_url_key(self):
        self.assertEqual(P.url_key("http://A.bandcamp.com/album/X/?from=s"), "a.bandcamp.com/album/x")
        self.assertIsNone(P.url_key(None))


class StepCleanUrls(unittest.TestCase):
    def test_limpia_y_es_idempotente(self):
        data = dataset([album(1, "https://a.bandcamp.com/album/x?from=search"),
                        album(2, "https://a.bandcamp.com/album/y/"),
                        album(3, "https://a.bandcamp.com/album/z"), album(4, None)])
        msgs = P.step_clean_urls(data)
        self.assertEqual(len(msgs), 1)
        self.assertIn("2", msgs[0])
        self.assertEqual([a["url"] for a in data["albums"]],
                         ["https://a.bandcamp.com/album/x", "https://a.bandcamp.com/album/y",
                          "https://a.bandcamp.com/album/z", None])
        self.assertEqual(P.step_clean_urls(data), [])


class Unicidad(unittest.TestCase):
    def test_dataset_correcto_pasa(self):
        P.validate(dataset([album(1, "https://a.bandcamp.com/album/x", 11),
                            album(2, "https://a.bandcamp.com/album/y", 22),
                            album(3, None, None), album(4, None, None)]))

    def test_album_id_duplicado(self):
        with self.assertRaisesRegex(AssertionError, "album_id duplicado: 11 en albums id=1 y id=2"):
            P.validate(dataset([album(1, "https://a.bandcamp.com/album/x", 11),
                                album(2, "https://a.bandcamp.com/album/y", 11)]))

    def test_url_duplicada_tras_normalizar(self):
        with self.assertRaisesRegex(AssertionError, "url duplicado"):
            P.validate(dataset([album(1, "https://a.bandcamp.com/album/x"),
                                album(2, "http://A.bandcamp.com/album/x/?from=s")]))

    def test_id_duplicado(self):
        with self.assertRaisesRegex(AssertionError, "id duplicado: 1"):
            P.validate(dataset([album(1, "https://a.bandcamp.com/album/x"),
                                album(1, "https://a.bandcamp.com/album/y")]))


if __name__ == "__main__":
    unittest.main()
