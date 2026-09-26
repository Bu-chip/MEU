"""Tests del robot de propuestas del público (sin red)."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import proposals as P  # noqa: E402


CSV = """Marca temporal,"URL de Bandcamp (disco, grupo o sello)",¿De dónde es el grupo? (pueblo o ciudad),Sello o colectivo,Otros grupos o sellos relacionados que deberían estar en el MEU,Comentario
26/09/2026 16:02:11,https://fontso.bandcamp.com/album/la-distancia,Bilbo,,"https://otro.bandcamp.com, y también https://tercero.bandcamp.com/music.",gran disco
26/09/2026 16:05:00,https://queimadacircuitrecords.com/album/x,,,,
26/09/2026 16:06:00,,,,,
"""


class Csv(unittest.TestCase):
    def test_columnas_por_palabra_clave(self):
        cols = P.map_columns(["Marca temporal", "URL", "¿De dónde?", "Sello", "Otros grupos", "Comentario"])
        self.assertEqual(cols, {"submitted_at": 0, "url": 1, "place": 2,
                                "label": 3, "related": 4, "comment": 5})

    def test_filas(self):
        rows = P.parse_rows(CSV)
        self.assertEqual(len(rows), 2)  # la fila vacía se ignora
        self.assertEqual(rows[0]["url"], "https://fontso.bandcamp.com/album/la-distancia")
        self.assertEqual(rows[0]["place"], "Bilbo")
        self.assertEqual(rows[0]["comment"], "gran disco")
        self.assertEqual(len(rows[0]["key"]), 16)
        self.assertNotEqual(rows[0]["key"], rows[1]["key"])

    def test_sin_columna_url(self):
        with self.assertRaises(ValueError):
            P.parse_rows("a,b\n1,2\n")


class Urls(unittest.TestCase):
    def test_extraer(self):
        urls = P.extract_urls("https://fontso.bandcamp.com/album/la-distancia",
                              "https://otro.bandcamp.com, y https://tercero.bandcamp.com/music.")
        self.assertEqual(urls, ["https://fontso.bandcamp.com/album/la-distancia",
                                "https://otro.bandcamp.com",
                                "https://tercero.bandcamp.com/music"])

    def test_clasificar(self):
        self.assertEqual(P.classify_url("https://fontso.bandcamp.com/album/la-distancia?from=x"),
                         ("album", "https://fontso.bandcamp.com/album/la-distancia"))
        self.assertEqual(P.classify_url("https://fontso.bandcamp.com/track/suelto"),
                         ("track", "https://fontso.bandcamp.com/track/suelto"))
        self.assertEqual(P.classify_url("https://Fontso.bandcamp.com"), ("account", "fontso"))
        self.assertEqual(P.classify_url("https://fontso.bandcamp.com/music"), ("account", "fontso"))
        self.assertEqual(P.classify_url("https://queimadacircuitrecords.com/album/x")[0], "other")
        self.assertEqual(P.classify_url("https://fontso.bandcamp.com/merch")[0], "other")


class Cola(unittest.TestCase):
    def setUp(self):
        self.state = {"rows": {}, "accounts": {}, "pending_fichas": {}, "fichas_error": {}}
        self.row = {"key": "k1", "submitted_at": "hoy", "url": "u", "place": "Bilbo",
                    "label": None, "related": "", "comment": None}

    def test_encolar_disco(self):
        known = set()
        r = P.enqueue_album(self.state, known, "https://fontso.bandcamp.com/album/la-distancia", self.row)
        self.assertEqual(r, "encolado")
        partial = self.state["pending_fichas"]["fontso.bandcamp.com/album/la-distancia"]
        self.assertEqual(partial["source_account"], "fontso")
        self.assertEqual(partial["proposal"]["place"], "Bilbo")
        self.assertEqual(partial["source_tags"], [])
        # Segunda vez: ya conocido.
        r = P.enqueue_album(self.state, known, "https://fontso.bandcamp.com/album/la-distancia/", self.row)
        self.assertEqual(r, "ya_conocido")

    def test_propuestas_sin_red(self):
        """Discos, temas, dominios propios y cuentas ya recorridas no
        consumen requests; la fila queda procesada con sus resultados."""
        rows = P.parse_rows(CSV)
        rows[0]["related"] = "https://fontso.bandcamp.com/track/suelto"
        session = P.Session(0, 0, 0)  # presupuesto cero: cualquier fetch reventaría
        fresh = P.run_proposals(session, rows, self.state, set(), {"fontso"}, lambda m: None)
        self.assertEqual(fresh, 1)
        out = self.state["rows"][rows[0]["key"]]["outcomes"]
        self.assertEqual(out["https://fontso.bandcamp.com/album/la-distancia"], "encolado")
        self.assertEqual(out["https://fontso.bandcamp.com/track/suelto"], "tema_suelto")
        self.assertEqual(self.state["rows"][rows[1]["key"]]["outcomes"],
                         {"https://queimadacircuitrecords.com/album/x": "revisar_a_mano"})
        self.assertTrue(P.row_yielded(out))
        self.assertFalse(P.row_yielded({"x": "revisar_a_mano"}))
        self.assertFalse(P.row_yielded({"x": "cuenta: 3 discos, 0 nuevos"}))

    def test_cuenta_ya_recorrida_no_pide(self):
        rows = [dict(self.row, url="https://fontso.bandcamp.com")]
        session = P.Session(0, 0, 0)
        P.run_proposals(session, rows, self.state, set(), {"fontso"}, lambda m: None)
        self.assertEqual(self.state["rows"]["k1"]["outcomes"],
                         {"https://fontso.bandcamp.com": "cuenta_ya_recorrida"})


class Tabla(unittest.TestCase):
    def test_render(self):
        with tempfile.TemporaryDirectory() as tmp:
            cand = Path(tmp) / "c.json"
            cand.write_text(json.dumps({
                "meta": {"month": "2026-09"},
                "candidates": [{
                    "artist": "fontso", "title": "La distancia", "year": 2024,
                    "tags": ["bilbao"], "url": "https://fontso.bandcamp.com/album/la-distancia",
                    "band_location": "Bilbao, Spain", "source_account": "fontso",
                    "proposal": {"submitted_at": "hoy", "place": "Bilbo", "label": None,
                                 "comment": "gran | disco"},
                }],
                "deferred_oleada2": [],
            }), encoding="utf-8")
            st = Path(tmp) / "s.json"
            st.write_text(json.dumps({"rows": {
                "k": {"submitted_at": "ayer", "url": "https://x.bandcamp.com/track/t",
                      "place": "", "label": "", "comment": "",
                      "outcomes": {"https://x.bandcamp.com/track/t": "tema_suelto"}}}}),
                encoding="utf-8")
            md = P.render_table(cand, st)
        self.assertIn("## hoy · fontso — place: Bilbo · comment: gran \\| disco", md)
        self.assertIn("[La distancia](https://fontso.bandcamp.com/album/la-distancia)", md)
        self.assertIn("## Propuestas sin candidatos nuevos", md)
        self.assertIn("tema_suelto", md)


if __name__ == "__main__":
    unittest.main()
