"""Tests de los parsers del descubrimiento por cuenta (sin red)."""

import html
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import discover_accounts as D  # noqa: E402


def attr(payload):
    return html.escape(json.dumps(payload), quote=True)


GRID = """
<p id="band-name-location"><span class="title">fontso</span>
<span class="location secondaryText">Bilbao, Spain</span></p>
<ol id="music-grid" class="music-grid">
  <li data-item-id="album-3893219629" class="music-grid-item square">
    <a href="/album/la-distancia"><p class="title">La distancia</p></a></li>
  <li data-item-id="track-1446942825" class="music-grid-item square">
    <a href="/track/suelto"><p class="title">Suelto</p></a></li>
  <li data-item-id="album-2198837024" class="music-grid-item square">
    <a href="https://otro.bandcamp.com/album/d-as-de-lluvia?label=1&amp;tab=music">
    <p class="title">Días de lluvia</p></a></li>
</ol>
"""


class PaginaMusic(unittest.TestCase):
    def test_rejilla(self):
        albums, tracks, loc = D.parse_music_page(GRID, "https://fontso.bandcamp.com/music")
        self.assertEqual(loc, "Bilbao, Spain")
        self.assertEqual(tracks, 1)
        self.assertEqual(sorted(albums), [
            (2198837024, "https://otro.bandcamp.com/album/d-as-de-lluvia", None),
            (3893219629, "https://fontso.bandcamp.com/album/la-distancia", None),
        ])

    def test_discografia_diferida(self):
        extra = [{"id": 1, "type": "album", "page_url": "/album/uno", "title": "Uno"},
                 {"id": 3893219629, "type": "album", "page_url": "/album/la-distancia"},
                 {"id": 2, "type": "track", "page_url": "/track/dos"}]
        page = GRID.replace('<ol id="music-grid"',
                            f'<ol data-client-items="{attr(extra)}" id="music-grid"')
        albums, tracks, _ = D.parse_music_page(page, "https://fontso.bandcamp.com/music")
        self.assertEqual(len(albums), 3)  # sin duplicar la-distancia
        self.assertIn((1, "https://fontso.bandcamp.com/album/uno", "Uno"), albums)
        self.assertEqual(tracks, 2)

    def test_cuenta_de_un_solo_disco(self):
        page = (
            '<meta name="bc-page-properties" content="'
            + attr({"item_type": "a", "item_id": 42}) + '">'
            '<meta property="og:url" content="https://algapoe.bandcamp.com/album/bso">'
            '<span class="location secondaryText">Bilbao, Spain</span>'
        )
        albums, tracks, loc = D.parse_music_page(page, "https://algapoe.bandcamp.com/music")
        self.assertEqual(albums, [(42, "https://algapoe.bandcamp.com/album/bso", None)])
        self.assertEqual((tracks, loc), (0, "Bilbao, Spain"))

    def test_cuenta_vacia(self):
        self.assertEqual(D.parse_music_page("<html></html>", "https://x.bandcamp.com/music"),
                         ([], 0, None))


class FichaDisco(unittest.TestCase):
    def ficha(self, tralbum=None, tags=("acoustic", "Bilbao"), props=None, og_title=None):
        props = props or {"item_type": "a", "item_id": 3893219629}
        parts = ['<meta name="bc-page-properties" content="' + attr(props) + '">',
                 '<meta property="og:image" content="https://f4.bcbits.com/img/a1_5.jpg">']
        if og_title:
            parts.append(f'<meta property="og:title" content="{og_title}">')
        if tralbum is not None:
            parts.append(f'<div data-tralbum="{attr(tralbum)}"></div>')
        parts += [f'<a class="tag" href="/t">{t}</a>' for t in tags]
        return "\n".join(parts)

    def test_tralbum(self):
        got = D.parse_album_page(self.ficha({
            "artist": "Fontso", "id": 3893219629,
            "current": {"title": "La distancia", "release_date": "14 Feb 1998 00:00:00 GMT"}}))
        self.assertEqual((got["artist"], got["title"], got["year"]),
                         ("Fontso", "La distancia", 1998))
        self.assertEqual(got["album_id"], 3893219629)
        self.assertEqual(got["cover_url"], "https://f4.bcbits.com/img/a1_5.jpg")
        self.assertEqual(got["tags"], ["acoustic", "bilbao"])  # normalize_tags del canónico

    def test_sin_tags_y_respaldo_og_title(self):
        page = self.ficha(tags=(), og_title="Spells, by Erroa") + "\nreleased March 3, 2015"
        got = D.parse_album_page(page)
        self.assertEqual((got["artist"], got["title"], got["year"], got["tags"]),
                         ("Erroa", "Spells", 2015, []))

    def test_tema_no_es_album(self):
        self.assertIsNone(D.parse_album_page(self.ficha(props={"item_type": "t", "item_id": 1})))


class SeleccionDeCuentas(unittest.TestCase):
    INDEX = {
        "fontso": {"account": "fontso", "place": "bilbo", "places": {"bilbo"},
                   "territory": "Bizkaia", "kind": "artist"},
        "sello": {"account": "sello", "place": "bilbo", "places": {"bilbo"},
                  "territory": "Bizkaia", "kind": "label"},
        "zarata": {"account": "zarata", "place": "zarautz", "places": {"zarautz"},
                   "territory": "Gipuzkoa", "kind": "artist"},
    }

    def names(self, *args, **kw):
        return [a["account"] for a in D.select_accounts(self.INDEX, *args, **kw)]

    def test_filtros(self):
        self.assertEqual(self.names("artist"), ["fontso", "zarata"])
        self.assertEqual(self.names("artist", {"bilbo"}), ["fontso"])
        self.assertEqual(self.names("label"), ["sello"])
        self.assertEqual(self.names("artist", only={"sello"}), ["sello"])

    def test_dominio_propio(self):
        self.assertEqual(D.music_url("custom:crudobilbao.com"), "https://crudobilbao.com/music")
        self.assertEqual(D.music_url("fontso"), "https://fontso.bandcamp.com/music")


if __name__ == "__main__":
    unittest.main()
