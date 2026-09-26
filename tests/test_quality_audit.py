"""Tests del auditor de calidad (python3 -m unittest discover -s tests).

Solo lectura: se construye un canónico sintético en memoria y se comprueba
que cada categoría del informe detecta lo que debe y nada más.
"""

import datetime as dt
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import quality_audit as Q  # noqa: E402


_DEFAULT = object()


def album(i, artist="Grupo", title="Disco", url=_DEFAULT, album_id=_DEFAULT, genre="rock",
          year=2020, tags=("rock",), cover="https://f4.bcbits.com/img/a1_5.jpg"):
    return {"id": i, "artist": artist, "title": title, "genre": genre, "year": year,
            "tags": list(tags),
            "url": f"https://grupo.bandcamp.com/album/disco-{i}" if url is _DEFAULT else url,
            "cover_url": cover, "album_id": 1000 + i if album_id is _DEFAULT else album_id}


def dataset(albums):
    return {"albums": albums,
            "artists": sorted({a["artist"] for a in albums}),
            "tags": sorted({t for a in albums for t in a["tags"]}),
            "years": sorted({a["year"] for a in albums if a["year"] is not None})}


def by_key(report):
    return {c.key: c for c in report["categories"]}


class Normalizaciones(unittest.TestCase):
    def test_normalize_url(self):
        self.assertEqual(Q.normalize_url("https://A.bandcamp.com/album/X/?from=search#top"),
                         "a.bandcamp.com/album/x")
        self.assertEqual(Q.normalize_url("http://a.bandcamp.com/album/x"), "a.bandcamp.com/album/x")
        self.assertEqual(Q.normalize_url(" https://a.bandcamp.com/album/x "), "a.bandcamp.com/album/x")
        self.assertIsNone(Q.normalize_url(None))

    def test_url_issues(self):
        self.assertEqual(Q.url_issues("https://a.bandcamp.com/album/x"), [])
        self.assertEqual(Q.url_issues(None), ["nula"])
        issues = Q.url_issues("http://A.bandcamp.com/album/x/?from=search#t")
        for expected in ("query ?from", "fragmento #", "http sin s", "mayúsculas", "barra final"):
            self.assertIn(expected, issues)
        self.assertIn("espacios", Q.url_issues("https://a.bandcamp.com/album/x y"))
        self.assertEqual(Q.url_issues("https://crudobilbao.com/album/x"), ["dominio no bandcamp.com"])
        self.assertEqual(Q.url_issues("https://a.bandcamp.com/track/x"), ["ruta no /album/"])

    def test_strong_key_y_case_style(self):
        self.assertEqual(Q.strong_key("Despeñaperros"), Q.strong_key("DESPENAPERROS"))
        self.assertEqual(Q.strong_key("Dual-Split"), Q.strong_key("dual split"))
        self.assertEqual(Q.case_style("COBRA"), "MAYÚSCULAS")
        self.assertEqual(Q.case_style("judy"), "minúsculas")
        self.assertEqual(Q.case_style("Cult of Misery"), "mixta")
        self.assertEqual(Q.case_style("6siss"), "minúsculas")
        self.assertEqual(Q.case_style("::"), "sin letras")

    def test_pair_key_titulo_sin_alfanumericos(self):
        a = album(1, artist="II", title=":::")
        b = album(2, artist="II", title="===")
        self.assertNotEqual(Q.pair_key(a), Q.pair_key(b))
        self.assertEqual(Q.pair_key(album(3, title="Remix It Again!")),
                         Q.pair_key(album(4, title="remix it again")))

    def test_tag_issues(self):
        self.assertEqual(Q.tag_issues("oi!"), [])
        self.assertEqual(Q.tag_issues("a.o.r."), [])
        self.assertEqual(Q.tag_issues("méxico d.f."), [])
        self.assertEqual(Q.tag_issues("¿qué les dejaremos?"), [])
        self.assertEqual(Q.tag_issues("ambient."), ["puntuación final"])
        self.assertEqual(Q.tag_issues("swamp..."), ["puntuación final"])
        self.assertEqual(Q.tag_issues("punk?"), ["puntuación final"])
        self.assertIn("mayúsculas", Q.tag_issues("Punk"))
        self.assertIn("doble espacio", Q.tag_issues("trap  flow"))
        self.assertEqual(Q.tag_issues("  "), ["vacío"])

    def test_title_has_artist_prefix(self):
        self.assertTrue(Q.title_has_artist_prefix("WLDV", "WLDV - The end of man EP"))
        self.assertTrue(Q.title_has_artist_prefix("black insekt", "Black Insekt - future kill"))
        self.assertFalse(Q.title_has_artist_prefix("WLDV", "Alguien - The end"))
        self.assertFalse(Q.title_has_artist_prefix("WLDV", "WLDV The end"))


class Auditoria(unittest.TestCase):
    def setUp(self):
        self.today = dt.date(2026, 9, 26)

    def audit(self, albums, waves=None):
        return Q.audit(dataset(albums), wave_index=waves or {}, today=self.today)

    def test_dataset_limpio_da_cero_en_todo(self):
        cats = by_key(self.audit([album(1), album(2, title="Otro")]))
        for key, c in cats.items():
            self.assertEqual(c.count, 0, key)

    def test_duplicados(self):
        albums = [
            album(1, album_id=7), album(2, title="B", album_id=7),                  # mismo album_id
            album(3, title="C", url="https://x.bandcamp.com/album/c"),
            album(4, title="D", url="https://X.bandcamp.com/album/c/?from=search"),  # misma URL normalizada
            album(5, artist="Marmol", title="Declaración total", url="https://sello.bandcamp.com/album/m"),
            album(6, artist="MÁRMOL", title="declaracion total!", url="https://marmol.bandcamp.com/album/m2"),
            album(7, artist="Río Arga", title="Uno", url="https://rioarga.bandcamp.com/album/r-o-arga"),
            album(8, artist="Rio Arga", title="Dos", url="https://sello.bandcamp.com/album/r-o-arga"),
        ]
        cats = by_key(self.audit(albums))
        self.assertEqual(cats["dup_album_id"].count, 1)
        self.assertEqual(cats["dup_url"].count, 1)
        self.assertEqual(cats["dup_artist_title"].count, 1)
        self.assertEqual({a["id"] for a in cats["dup_artist_title"].rows[0][0]}, {5, 6})
        self.assertEqual(cats["reedicion_slug"].count, 1)
        self.assertEqual({a["id"] for a in cats["reedicion_slug"].rows[0][0]}, {7, 8})

    def test_mismo_disco_en_varias_ediciones_no_es_reedicion_por_slug(self):
        # Ya está en dup_artist_title: no se repite en reedicion_slug.
        albums = [album(1, title="X", url="https://a.bandcamp.com/album/x"),
                  album(2, title="X", url="https://b.bandcamp.com/album/x")]
        cats = by_key(self.audit(albums))
        self.assertEqual(cats["dup_artist_title"].count, 1)
        self.assertEqual(cats["reedicion_slug"].count, 0)

    def test_artistas(self):
        albums = [album(1, artist="Cult of Misery"), album(2, artist="CULT OF MISERY", title="B"),
                  album(3, artist="cult of misery", title="C"), album(4, artist="Cult Of Misery", title="D"),
                  album(5, artist="COBRA", title="E"), album(6, artist="judy", title="F"),
                  album(7, artist="Huracan  Rose", title="G"), album(8, artist="Calathea ", title="H"),
                  album(9, artist="Mr. Yogo,", title="I"), album(10, title="Portage -  Vinyl")]
        cats = by_key(self.audit(albums))
        self.assertEqual(cats["artist_variants"].count, 1)
        self.assertIn("`Cult of Misery` (1)", cats["artist_variants"].rows[0][1]["variantes"])
        flagged = {(r[0]["artist"], r[1]["estilo"].split(" ")[0]) for r in cats["artist_case"].rows}
        self.assertEqual(flagged, {("CULT OF MISERY", "MAYÚSCULAS"), ("cult of misery", "minúsculas")})
        self.assertEqual(cats["artist_style"].count, 2)          # COBRA y judy, sin otra grafía
        self.assertEqual(cats["artist_style"].summary, "1 en MAYÚSCULAS, 1 en minúsculas")
        ws = {(r[0]["id"], r[1]["campo"], r[1]["problema"]) for r in cats["whitespace"].rows}
        self.assertEqual(ws, {(7, "artist", "doble espacio"), (8, "artist", "espacio inicial/final"),
                              (9, "artist", "puntuación colgante"), (10, "title", "doble espacio")})

    def test_genre_tags(self):
        albums = [album(1, genre=None), album(2, title="B", genre=""), album(3, title="C", genre="techno"),
                  album(4, title="D", tags=()), album(5, title="E", tags=("Punk", "ambient.", "oi!", "trap  flow")),
                  album(6, title="F", tags=("post-punk", "post punk", "punk"))]
        cats = by_key(self.audit(albums))
        self.assertEqual({r[0]["id"] for r in cats["genre_null"].rows}, {1, 2})
        self.assertEqual({r[0]["id"] for r in cats["genre_vocab"].rows}, {3})
        self.assertEqual({r[0]["id"] for r in cats["tags_empty"].rows}, {4})
        dirty = {r[1]["tag"] for r in cats["tags_dirty"].rows}
        self.assertEqual(dirty, {"Punk", "ambient.", "trap  flow"})
        variants = " / ".join(r[1]["variantes"] for r in cats["tag_variants"].rows)
        self.assertEqual(len(cats["tag_variants"].rows), 2)      # Punk/punk y post-punk/post punk
        for expected in ("`post-punk` (1)", "`post punk` (1)", "`Punk` (1)", "`punk` (1)"):
            self.assertIn(expected, variants)

    def test_urls_fechas_portadas(self):
        albums = [album(1, url="https://a.bandcamp.com/album/x?from=search"),
                  album(2, title="B", url=None, album_id=None, cover=None),
                  album(3, title="C", url="https://crudobilbao.com/album/y"),
                  album(4, title="D", year=None), album(5, title="E", year=1888),
                  album(6, title="F", year=2050), album(7, title="G", cover="https://otro.com/img.jpg"),
                  album(8, title="WLDV - H", artist="WLDV")]
        cats = by_key(self.audit(albums))
        self.assertEqual({(r[0]["id"], r[1]["problema"]) for r in cats["url_dirty"].rows},
                         {(1, "query ?from"), (3, "dominio no bandcamp.com")})
        self.assertEqual({r[0]["id"] for r in cats["url_null"].rows}, {2})
        self.assertEqual({r[0]["id"] for r in cats["year_null"].rows}, {4})
        self.assertEqual({r[0]["id"] for r in cats["year_bad"].rows}, {5, 6})
        self.assertEqual({r[0]["id"] for r in cats["cover_null"].rows}, {2})
        self.assertEqual({r[0]["id"] for r in cats["cover_domain"].rows}, {7})
        self.assertEqual({r[0]["id"] for r in cats["album_id_null"].rows}, {2})
        self.assertEqual({r[0]["id"] for r in cats["title_prefix"].rows}, {8})

    def test_esquema(self):
        albums = [album(1), album(2, title="B"), album(2, title="C")]
        data = dataset(albums)
        albums[0]["extra"] = 1
        albums[0]["year"] = "2020"
        data["artists"] = []
        cats = by_key(Q.audit(data, today=self.today))
        problems = [r[1]["problema"] for r in cats["esquema"].rows]
        self.assertTrue(any("campos extra: extra" in p and "year es str" in p for p in problems))
        self.assertTrue(any("id repetido ×2" in p for p in problems))
        self.assertTrue(any("`artists` no coincide" in p for p in problems))

    def test_regresion_y_origen(self):
        albums = [album(1, album_id=11), album(2, title="B", album_id=22), album(3, title="C", album_id=33)]
        report = self.audit(albums, waves={11: "2026-08", 22: "2026-09"})
        self.assertEqual(report["meta"]["waves"], {"2026-08": 1, "2026-09": 1, "orig.": 1})
        self.assertTrue(all(n == 0 for _, n in report["regression"]))
        self.assertEqual(report["origin"](albums[0]), "2026-08")
        self.assertEqual(report["origin"](albums[2]), "orig.")


class Render(unittest.TestCase):
    def test_markdown_con_limite_de_ejemplos(self):
        albums = [album(i, genre=None, title=f"T{i}") for i in range(1, 41)]
        report = Q.audit(dataset(albums), max_examples=30, today=dt.date(2026, 9, 26))
        md = Q.render_markdown(report)
        self.assertIn("# Auditoría de calidad del canónico — 2026-09-26", md)
        self.assertIn("**Recuento: 40 filas.**", md)
        self.assertIn("*… y 10 más (solo se muestran 30).*", md)
        self.assertIn("| [`genre` null o vacío](#genre_null) | 40 filas |", md)
        self.assertIn("Sin casos.", md)
        self.assertTrue(md.endswith("\n"))

    def test_escapa_barras_verticales(self):
        albums = [album(1, artist="a|b", genre=None)]
        md = Q.render_markdown(Q.audit(dataset(albums), today=dt.date(2026, 9, 26)))
        self.assertIn("a\\|b", md)


if __name__ == "__main__":
    unittest.main()
