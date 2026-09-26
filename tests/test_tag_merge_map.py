"""Tests del mapa de fusión de tags (python3 -m unittest discover -s tests)."""

import json
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import tag_merge_map as M  # noqa: E402


class Normalizacion(unittest.TestCase):
    def test_minusculas_y_acentos(self):
        self.assertEqual(M.normalize("Psicodélico"), "psicodelico")
        self.assertEqual(M.normalize("IRUÑA"), "iruna")

    def test_guiones_barras_y_espacios(self):
        for variante in ("post-punk", "post punk", "Post_Punk", "post-punk.", "  post   punk "):
            self.assertEqual(M.normalize(variante), "post punk", variante)
        self.assertEqual(M.normalize("hip-hop/rap"), "hip hop rap")
        self.assertEqual(M.normalize("metal; punk"), "metal punk")

    def test_ampersand_y_n(self):
        for variante in ("rock & roll", "rock and roll", "rock'n'roll", "rock 'n' roll", "rock n roll"):
            self.assertEqual(M.normalize(variante), "rock and roll", variante)
        self.assertEqual(M.normalize("drum & bass"), "drum and bass")

    def test_puntuacion(self):
        self.assertEqual(M.normalize("oi!"), "oi")
        self.assertEqual(M.normalize("new age."), "new age")
        self.assertEqual(M.normalize('12"'), "12")

    def test_idempotente(self):
        for t in ("Post-Punk!", "rock & roll", "Iruñea", "d-beat", "r&b/soul"):
            self.assertEqual(M.normalize(M.normalize(t)), M.normalize(t))

    def test_clave_compacta_agrupa_variantes(self):
        self.assertEqual(M.compact("post-punk"), M.compact("postpunk"))
        self.assertEqual(M.compact("Heavy Metal"), M.compact("heavymetal"))
        self.assertNotEqual(M.compact("hardcore"), M.compact("hardcore techno"))


class Sinonimos(unittest.TestCase):
    def test_idiomas(self):
        self.assertEqual(M.apply_synonyms("rocka"), "rock")
        self.assertEqual(M.apply_synonyms("punka"), "punk")
        self.assertEqual(M.apply_synonyms("psicodelia"), "psychedelic")
        self.assertEqual(M.apply_synonyms("musica electronica"), "electronic")
        self.assertEqual(M.apply_synonyms("cantautor"), "singer songwriter")
        self.assertEqual(M.apply_synonyms("ruido"), "noise")

    def test_cadena_completa(self):
        self.assertEqual(M.apply_synonyms("dnb"), "drum and bass")
        self.assertEqual(M.apply_synonyms("hip hop rap"), "hip hop")
        self.assertEqual(M.apply_synonyms("crust punk"), "crust")
        self.assertEqual(M.apply_synonyms("trikitixa"), "euskal folk")
        self.assertEqual(M.apply_synonyms("live"), "otro:en directo")

    def test_destinos_son_puntos_fijos(self):
        """Todo destino de FULL_SYNONYMS debe ser estable (si no, dos tags que
        apuntan al mismo sitio acabarían en conceptos distintos)."""
        for origen, destino in M.FULL_SYNONYMS.items():
            if destino == M.RESTO or destino.startswith((M.OTRO_PREFIX, M.LUGAR_PREFIX)):
                continue
            self.assertEqual(M.normalize(destino), destino, origen)
            self.assertEqual(M.apply_synonyms(destino), destino, origen)
            self.assertTrue(M.is_genre(destino), (origen, destino))

    def test_padres_fijados_son_puntos_fijos(self):
        for nodo, padre in M.PARENT_OVERRIDES.items():
            self.assertEqual(M.apply_synonyms(nodo), nodo)
            self.assertEqual(M.apply_synonyms(padre), padre)


class Clasificacion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gaz, cls.parents = M.load_gazetteer()

    def test_lugares_van_aparte(self):
        for tag in ("bilbao", "Bilbo", "iruña", "pamplona", "Donostia / San Sebastián", "basque country",
                    "euskal herria", "spain", "madrid, spain", "euskal herria is not spain"):
            grupo, _, _ = M.resolve_tag(tag, self.gaz)
            self.assertEqual(grupo, "lugar", tag)

    def test_lugar_no_se_funde_con_genero(self):
        self.assertEqual(M.resolve_tag("bilbao", self.gaz)[:2], ("lugar", "bilbo"))
        self.assertEqual(M.resolve_tag("bilbo", self.gaz)[:2], ("lugar", "bilbo"))
        self.assertEqual(M.resolve_tag("berlin school", self.gaz)[0], "genero")
        self.assertEqual(M.resolve_tag("uk garage", self.gaz)[:2], ("genero", "uk garage"))

    def test_tag_mixto_lugar_genero(self):
        grupo, canon, flags = M.resolve_tag("punk vasco", self.gaz)
        self.assertEqual((grupo, canon), ("genero", "punk"))
        self.assertIn("lugar-quitado", flags)
        self.assertEqual(M.resolve_tag("barakaldo basque country", self.gaz)[:2], ("lugar", "barakaldo"))

    def test_otro(self):
        self.assertEqual(M.resolve_tag("1994", self.gaz)[:2], ("otro", "año"))
        self.assertEqual(M.resolve_tag("80s", self.gaz)[:2], ("otro", "decada 80"))
        self.assertEqual(M.resolve_tag("1980's", self.gaz)[:2], ("otro", "decada 80"))
        self.assertEqual(M.resolve_tag("euskera", self.gaz)[:2], ("otro", "euskaraz"))
        self.assertEqual(M.resolve_tag("cassette", self.gaz)[:2], ("otro", "cassette"))
        self.assertEqual(M.resolve_tag("diy", self.gaz)[:2], ("otro", "diy"))

    def test_genero_y_resto(self):
        self.assertEqual(M.resolve_tag("Post-Punk", self.gaz)[:2], ("genero", "post punk"))
        self.assertEqual(M.resolve_tag("crustcore", self.gaz)[0], "genero")
        self.assertEqual(M.resolve_tag("kokoshca", self.gaz)[0], M.RESTO)
        self.assertEqual(M.resolve_tag("petruska records", self.gaz)[0], M.RESTO)  # "ska" pegada no cuenta
        self.assertFalse(M.is_genre("petruska records"))
        self.assertTrue(M.is_genre("blackgaze"))

    def test_erratas(self):
        self.assertEqual(M.edit_distance("experiemental", "experimental"), 1)
        self.assertEqual(M.edit_distance("funk rock", "punk rock"), 1)
        self.assertTrue(M.is_known_genre("funk rock"))   # nunca se trata como errata


def mini_catalogo():
    """Catálogo sintético. Cada disco lleva sus tags; los recuentos por nodo
    (con MIN_DISCOS=5) son: rock 6, techno 5, experimental 5, punk 7, metal 5,
    hardcore 5, euskal herria 5; hardcore techno (1) cuelga de techno y queda
    marcado como dudoso porque hardcore también era nodo."""
    tags_por_disco = [
        ["rock", "post-punk", "bilbao", "live", "hardcore", "euskal herria"],
        ["Post Punk", "postpunk", "iruña", "rock", "euskal herria"],
        ["punk", "hardcore", "hardcore techno", "techno", "euskal herria"],
        ["experiemental", "experimental", "1994", "hardcore", "euskal herria"],
        ["rock", "rocka", "rock vasco", "euskal herria"],
        ["crust", "crust punk", "d-beat", "80s", "punk"],
        ["metal", "death metal", "funeral doom", "doom", "hardcore"],
        ["kokoshca", "euskara", "experimental", "metal"],
        ["techno", "trance electro techno", "durango", "punk"],
        ["experimental", "noise", "techno", "metal"],
        ["rock", "punk", "techno", "metal"],
        ["punk", "hardcore", "metal", "techno", "experimental", "rocka"],
        ["rock", "experimental"],
    ]
    return {"albums": [{"id": i, "tags": t} for i, t in enumerate(tags_por_disco)]}


class Determinismo(unittest.TestCase):
    def test_cada_tag_tiene_nodo(self):
        cat = mini_catalogo()
        res = M.build(cat)
        todos = {t for a in cat["albums"] for t in a["tags"]}
        self.assertEqual(set(res["map"]), todos)
        self.assertEqual(res["_meta"]["n_tags"], len(todos))

    def test_dos_ejecuciones_identicas(self):
        a = json.dumps(M.build(mini_catalogo()), ensure_ascii=False, sort_keys=False)
        b = json.dumps(M.build(mini_catalogo()), ensure_ascii=False, sort_keys=False)
        self.assertEqual(a, b)

    def test_independiente_del_orden_de_entrada(self):
        cat = mini_catalogo()
        ref = M.build(cat)
        rnd = random.Random(7)
        for _ in range(3):
            albums = list(cat["albums"])
            rnd.shuffle(albums)
            for a in albums:
                a = dict(a)
                rnd.shuffle(a["tags"])
            res = M.build({"albums": albums})
            self.assertEqual(res["map"], ref["map"])
            self.assertEqual([n["id"] for n in res["nodos"]], [n["id"] for n in ref["nodos"]])

    def test_variantes_al_mismo_nodo(self):
        m = M.build(mini_catalogo())["map"]
        self.assertEqual(len({m["post-punk"], m["Post Punk"], m["postpunk"]}), 1)
        self.assertEqual(m["rocka"], m["rock"])
        self.assertEqual(m["rock vasco"], m["rock"])
        self.assertEqual(m["experiemental"], m["experimental"])
        self.assertTrue(m["bilbao"].startswith("lugar:"))
        self.assertTrue(m["euskal herria"].startswith("lugar:"))
        self.assertEqual(m["kokoshca"], M.RESTO)
        self.assertEqual(m["live"], "otro:formato")        # 1 disco: cuelga del subtipo
        self.assertEqual(m["1994"], "otro:época")
        # bilbao (1 disco) -> bizkaia (0) -> euskal herria (5): sube por la cadena
        self.assertEqual(m["bilbao"], "lugar:euskal herria")
        self.assertEqual(m["durango"], "lugar:euskal herria")
        self.assertEqual(m["iruña"], "lugar:euskal herria")

    def test_umbral_cuelga_del_padre(self):
        """Con MIN_DISCOS=5 "hardcore techno" (1 disco) cuelga de techno (5 discos)."""
        res = M.build(mini_catalogo())
        m = res["map"]
        self.assertEqual(m["hardcore techno"], m["techno"])
        dud = {d["tag"]: d for d in res["dudosas"]}
        self.assertIn("hardcore techno", dud)          # hardcore también encajaba
        self.assertIn("hardcore", dud["hardcore techno"]["motivo"])

    def test_nodos_con_recuento(self):
        res = M.build(mini_catalogo())
        nodos = {n["id"]: n for n in res["nodos"]}
        self.assertEqual(nodos["rock"]["discos"], 6)       # 0, 1, 4, 10, 11 (rocka), 12
        self.assertEqual(nodos["techno"]["discos"], 5)     # 2, 8, 9, 10, 11
        self.assertEqual(nodos["punk"]["discos"], 7)       # 2, 5, 8, 10, 11 + hardcore (0, 3, 6) cuelga
        self.assertEqual(nodos["hardcore"]["discos"], 5)
        self.assertEqual(nodos["hardcore"]["padre"], "punk")
        self.assertEqual(nodos["lugar:euskal herria"]["discos"], 6)   # 0-4 + durango (8)
        self.assertEqual(nodos["rock"]["grupo"], "genero")
        self.assertEqual(nodos["punk"]["padre"], "rock")
        self.assertEqual(nodos["rock"]["padre"], None)
        for n in res["nodos"]:
            self.assertEqual(n["discos"], len({a["id"] for a in mini_catalogo()["albums"]
                                               if any(res["map"][t] == n["id"] for t in a["tags"])}))


class FicheroDerivado(unittest.TestCase):
    """El JSON versionado debe coincidir byte a byte con una regeneración."""

    def test_derivado_al_dia(self):
        if not (M.CANONICAL.exists() and M.MAP_JSON.exists()):
            self.skipTest("sin catálogo o sin derivado")
        catalog = json.loads(M.CANONICAL.read_text(encoding="utf-8"))
        result = M.build(catalog)
        aviso = "no está al día: python3 scripts/tag_merge_map.py"
        self.assertEqual(M.render_map_json(result), M.MAP_JSON.read_text(encoding="utf-8"),
                         f"{M.MAP_JSON.name} {aviso}")
        self.assertEqual(M.render_nodes_json(result), M.NODES_JSON.read_text(encoding="utf-8"),
                         f"{M.NODES_JSON.name} {aviso}")

    def test_nodes_json_es_compacto_y_completo(self):
        res = M.build(mini_catalogo())
        slim = json.loads(M.render_nodes_json(res))
        self.assertEqual([n["id"] for n in slim["nodos"]], [n["id"] for n in res["nodos"]])
        self.assertEqual(set(slim["nodos"][0]), {"id", "grupo", "padre", "discos", "tags"})
        tags = {t for n in slim["nodos"] for t in n["tags"]}
        self.assertEqual(tags, set(res["map"]))


if __name__ == "__main__":
    unittest.main()
