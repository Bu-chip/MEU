#!/usr/bin/env python3
"""Mapa de fusión de tags — dato DERIVADO, READ-ONLY sobre el canónico.

Lee data/bandcamp_bilbaotags_clean.json (NO lo modifica) y escribe:

  * data/derived/tag_merge_map.json    -> {"map": {tag_original: nodo}, "nodos": [...]}
  * data/derived/tag_merge_report.md   -> resumen legible + "fusiones dudosas"

Objetivo: reducir los ~5.500 tags distintos de Bandcamp a unos 400-500 nodos
navegables SIN perder información: cada tag original apunta a exactamente un
nodo. El fichero es determinista (misma entrada -> mismos bytes).

Método (ver docs/tag-merge-map.md). Cada tag pasa por esta cadena, en orden:

  1. NORMALIZACIÓN (normalize):  NFKD sin diacríticos, minúsculas, "&" y
     "'n'" -> "and", separadores (-_/;,.:+) -> espacio, sin puntuación,
     espacios colapsados.  "Post-Punk" == "post punk" == "postpunk" (la clave
     compacta, sin espacios, es la que agrupa variantes ortográficas).
  2. SINÓNIMOS DE CADENA COMPLETA (FULL_SYNONYMS): equivalencias que no salen
     de ninguna regla (dnb -> drum and bass, hip hop rap -> hip hop, oi ->
     oi!, rocknroll -> rock and roll...).
  3. SINÓNIMOS POR PALABRA (WORD_SYNONYMS): traducción es/eu/en palabra a
     palabra (rocka -> rock, psicodelia -> psychedelic, musika -> ∅) y sufijo
     vasco "-a" (punka -> punk) solo si el resultado ya es un tag conocido.
  4. LUGAR: si la clave compacta está en el gaceteer (data/locations/places.json
     + rules.json + lista de lugares externos) el tag es de LUGAR y va al
     grupo "lugar:*", nunca se fusiona con un género. Si un tag mezcla lugar y
     género ("freejazz bilbao", "punk vasco") se quita la parte de lugar y el
     resto sigue como género (marcado como dudoso).
  5. OTRO: años/décadas, formatos (ep, demo, cassette...), idiomas, instrumentos
     y etiquetas de escena (diy, antifa, queer...) van al grupo "otro:*".
  6. GÉNERO: el resto se acepta como género solo si contiene una raíz musical
     conocida (GENRE_ROOTS: punk, core, gaze, wave, house...) o está en
     GENRE_TERMS. Lo que no cumple nada (nombres de grupo, sellos, palabras
     sueltas, consignas) va al nodo "resto".
  7. ERRATAS: un concepto pequeño (< FUZZY_MAX_DISCOS discos) a distancia de
     edición 1 (clave >= 6 letras) o 2 (>= 10) de un nodo grande (>=
     FUZZY_MIN_TARGET_DISCOS) se fusiona con él (experiemental ->
     experimental). Salvaguardas: la primera letra tiene que coincidir y un
     término conocido nunca se trata como errata ("funk rock" está a una letra
     de "punk rock"). Siempre marcado como dudoso.
  8. UMBRAL: un concepto de género con < MIN_DISCOS discos no es nodo: se
     cuelga de su padre más cercano. Padre = el nodo grande que coincide con
     el sufijo más largo de palabras ("raw black metal" -> "black metal"), si
     no una subsecuencia contigua, si no una palabra suelta, si no la raíz
     pegada ("crustcore" -> "crust"). Sin padre -> "otros géneros".
     Los lugares pequeños cuelgan de su territorio (lugar:bizkaia...) y los
     "otro" pequeños de su subtipo (otro:formato, otro:idioma...).

Se marcan como DUDOSAS (sección del informe + campo "dudosas" del JSON):
  * fusiones por errata (paso 7);
  * cuelgues donde más de una palabra del tag era un nodo grande
    ("hardcore techno" -> techno, pero hardcore también encajaba);
  * cuelgues donde el tag lleva un prefijo que cambia el sentido (post-,
    anti-, proto-, neo-, no-, non-, pre-);
  * tags a los que se les quitó una parte de lugar;
  * sinónimos marcados a mano como discutibles (DOUBTFUL_SYNONYMS).
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Rutas (relativas a la raíz del repo para que funcione desde cualquier cwd).
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
CANONICAL = REPO_ROOT / "data" / "bandcamp_bilbaotags_clean.json"
PLACES_JSON = REPO_ROOT / "data" / "locations" / "places.json"
RULES_JSON = REPO_ROOT / "data" / "locations" / "rules.json"
DERIVED_DIR = REPO_ROOT / "data" / "derived"
MAP_JSON = DERIVED_DIR / "tag_merge_map.json"
REPORT_MD = DERIVED_DIR / "tag_merge_report.md"

# ---------------------------------------------------------------------------
# Parámetros. MIN_DISCOS es el umbral de microgénero: un concepto con menos
# discos no es nodo propio y cuelga de su padre. Sensibilidad sobre el
# catálogo de 2026-09 (7.637 discos): N=3 -> 507 nodos, N=4 -> 476,
# N=5 -> 452, N=6 -> 431, N=8 -> 391, N=10 -> 367.
# ---------------------------------------------------------------------------
MIN_DISCOS = 5
FUZZY_MIN_TARGET_DISCOS = 20   # un nodo solo "atrae" erratas si es grande
FUZZY_MAX_DISCOS = 30          # un tag con >= 30 discos no se trata como errata
TOP_NODES_IN_REPORT = 50

RESTO = "resto"
OTROS_GENEROS = "otros géneros"
LUGAR_PREFIX = "lugar:"
OTRO_PREFIX = "otro:"

# ---------------------------------------------------------------------------
# 1. Normalización
# ---------------------------------------------------------------------------
_SEPARATORS = re.compile(r"[-_/;,.:+|·•–—]+")
_APOS = re.compile(r"[’'`´\"“”«»()\[\]{}!?¡¿*#@$%^~<>=]")
_SPACES = re.compile(r"\s+")


def strip_accents(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in text if not unicodedata.combining(ch))


def normalize(tag: str) -> str:
    """Forma normalizada con espacios: 'Post-Punk!' -> 'post punk'.

    Idempotente: normalize(normalize(x)) == normalize(x).
    """
    t = strip_accents(tag).lower()
    t = t.replace("&", " and ")
    t = re.sub(r"(?<=\w)'n'(?=\w)", " and ", t)      # rock'n'roll
    t = re.sub(r"\s'n'\s", " and ", t)                 # rock 'n' roll
    t = _APOS.sub("", t)
    t = _SEPARATORS.sub(" ", t)
    t = _SPACES.sub(" ", t).strip()
    t = re.sub(r"\b(\w+) n (\w+)\b", r"\1 and \2", t)   # rock n roll
    return t


def compact(text: str) -> str:
    """Clave compacta: sin espacios ni nada que no sea [a-z0-9]."""
    return re.sub(r"[^a-z0-9]", "", normalize(text))


# ---------------------------------------------------------------------------
# 2. Sinónimos de cadena completa (clave: forma normalizada; valor: forma
#    normalizada canónica). Se aplican antes y después de la traducción por
#    palabra. Comentar el porqué cuando no sea obvio.
# ---------------------------------------------------------------------------
FULL_SYNONYMS: dict[str, str] = {
    # umbrella tags de Bandcamp que juntan dos géneros
    "hip hop rap": "hip hop",
    "rap and hip hop": "hip hop",
    "rap and hip hop underground": "underground hip hop",
    "hiphop": "hip hop",
    "hip hop instrumentals": "instrumental hip hop",
    "hiphop instrumental": "instrumental hip hop",
    "lofi hiphop": "lo fi hip hop",
    "underground hiphop": "underground hip hop",
    "beats hiphop": "beats",
    "rap beats": "beats",
    "trap beats": "beats",
    "beats for sale": "beats",
    "r and b soul": "r and b",
    "rnb": "r and b",
    "rhythm and blues": "r and b",
    "rythm and blues": "r and b",
    "rythmnblues": "r and b",
    "funk rythm and blues": "funk",
    # rock & roll y familia
    "rocknroll": "rock and roll",
    "rock n f k roll": "rock and roll",
    "r and r": "rock and roll",
    "rock roll": "rock and roll",
    "high energy rock and roll": "high energy rock",
    "highenergyrockandroll": "high energy rock",
    "highenergyrock and roll": "high energy rock",
    "africanhiphop": "hip hop",
    "worldbeat": "world music",
    "bass lee": RESTO,
    "intrumental funk": "funk",
    "world beat": "world music",
    "filmscore": "soundtrack",
    "afrihooop": "hip hop",
    "psycobilly": "psychobilly",
    "chill hop": "lo fi hip hop",
    "chillhop": "lo fi hip hop",
    "big beat": "breakbeat",
    "drumstep": "drum and bass",
    "miami bass": "electro",
    "riot": "riot grrrl",
    "riot girl": "riot grrrl",
    "spoken": "spoken word",
    "harsh": "harsh noise",
    "juke": "footwork",
    "step": "dubstep",
    "hillbilly": "country",
    "bebop": "bebop",
    "opera": "opera",
    "bolero": "bolero",
    "merengue": "merengue",
    "bachata": "bachata",
    "stoner doom": "stoner rock",
    "melodic death doom": "death doom metal",
    "thrash black": "black thrash metal",
    "speed black thrash": "black thrash metal",
    "blackened deathmetal": "black death",
    "alternative indie": "indie rock",
    "guitar indie": "indie rock",
    "post hc": "post hardcore",
    "psycho core": "hardcore",
    "thrash core": "fastcore",
    "euskal wave": "darkwave",
    "veganwave": "punk",
    "dystopiawave": "synthwave",
    "bachatawave": "bachata",
    "dark cabaret": "cabaret",
    "cabaret": "cabaret",
    "vaudeville": "cabaret",
    "high energy": "high energy rock",
    "punk and roll": "punk rock",
    "death and roll": "death metal",
    "rock and oi": "oi",
    # oi!
    "oi streetpunk": "street punk",
    "oi punk": "oi",
    "punk oi": "oi",
    "oipunk": "oi",
    "punkoi": "oi",
    "napar oi": "oi",
    "oi mondra": "oi",
    "skinhead": "oi",
    "skinhead rock": "oi",
    "skinhead rock and roll": "oi",
    "streetpunk": "street punk",
    # drum & bass
    "dnb": "drum and bass",
    "d and b": "drum and bass",
    "drumnbass": "drum and bass",
    "drum n bass": "drum and bass",
    "jungle dnb": "jungle",
    # hardcore
    "hxc": "hardcore",
    "hc": "hardcore",
    "h c": "hardcore",
    "hard core": "hardcore",
    "punk hardcore": "hardcore punk",
    "punk rock hardcore": "hardcore punk",
    "hardcore punk melodico": "melodic hardcore",
    "melodic hard core": "melodic hardcore",
    "hardcore melodico": "melodic hardcore",
    "hardcore melodic punk rock": "melodic hardcore",
    "emotional hardcore": "emo",
    "emocore": "emo",
    "emo revival": "emo",
    "midwest emo": "emo",
    "post hardcore": "post hardcore",
    "metal core": "metalcore",
    # crust
    "crust punk": "crust",
    "crustcore": "crust",
    "hardcore crust": "crust",
    "neocrust": "neo crust",
    "stenchcore": "crust",
    "d beat crust": "d beat",
    "d beat raw punk": "d beat",
    # punk variantes
    "punk 77": "77 punk",
    "punk77": "77 punk",
    "82 punk": "uk 82",
    "uk82": "uk 82",
    "punk 82": "uk 82",
    "anarcopunk": "anarcho punk",
    "anarchopunk": "anarcho punk",
    "anarko punk": "anarcho punk",
    "rawpunk": "raw punk",
    "skatepunk": "skate punk",
    "punk rock": "punk rock",
    "pop punk": "pop punk",
    "punk pop": "pop punk",
    "punk metal": "metalpunk",
    "metal punk": "metalpunk",
    "after punk": "post punk",
    "thrashcore": "fastcore",
    "trashcore": "fastcore",
    # metal
    "trash metal": "thrash metal",
    "trash": "thrash metal",
    "thash": "thrash metal",
    "thrash": "thrash metal",
    "heavy": "heavy metal",
    "heavymetal": "heavy metal",
    "heavy metal hard rock": "heavy metal",
    "death": "death metal",
    "melodic death": "melodic death metal",
    "melodic deathmetal": "melodic death metal",
    "death metal melodico": "melodic death metal",
    "modern melodic death metal": "melodic death metal",
    "brutal death": "brutal death metal",
    "slamming brutal death metal": "slam",
    "slamming beatdown": "slam",
    "black": "black metal",
    "blackened": "black metal",
    "doom": "doom metal",
    "doom death": "death doom metal",
    "doom death metal": "death doom metal",
    "death doom": "death doom metal",
    "melodic doom death": "death doom metal",
    "melodic doom death metal": "death doom metal",
    "black doom metal": "blackened doom",
    "grove metal": "groove metal",
    "prog metal": "progressive metal",
    "prog rock": "progressive rock",
    "prog": "progressive rock",
    "progg rock": "progressive rock",
    "rock progresivo": "progressive rock",
    "progressive": "progressive rock",
    "nu metal": "nu metal",
    "numetal": "nu metal",
    "rapmetal": "rap metal",
    "rap rock": "rap metal",
    "rapcore": "rap metal",
    "grind": "grindcore",
    "grind core": "grindcore",
    "extreme metal": "metal",
    "modern metal": "metal",
    "rock metal": "hard rock",
    "hard rock metal": "hard rock",
    "hard rock hard blues": "hard rock",
    "black thrash": "black thrash metal",
    "post black metal": "blackgaze",
    "atmospheric black metal": "atmospheric black metal",
    # rock / pop
    "alt rock": "alternative rock",
    "rock alternative": "alternative rock",
    "rock alternativo": "alternative rock",
    "alternative": "alternative rock",
    "alternativa": "alternative rock",
    "alternativo": "alternative rock",
    "grunge rock": "grunge",
    "grunge rock alternative": "grunge",
    "post grunge": "grunge",
    "indie": "indie rock",
    "mod indie": "indie rock",
    "rock indie": "indie rock",
    "indie rock pop": "indie pop",
    "indie pop rock": "indie pop",
    "pop rock indie": "indie pop",
    "pop indie": "indie pop",
    "popindie": "indie pop",
    "rock pop": "pop rock",
    "power pop rock": "power pop",
    "powerpoprock": "power pop",
    "punk power pop rock": "power pop",
    "psych": "psychedelic",
    "psicodelia": "psychedelic",
    "neo psicodelia": "psychedelic",
    "psicodelico": "psychedelic",
    "psicodelic": "psychedelic",
    "psychodelic": "psychedelic",
    "pyschodelic": "psychedelic",
    "psychedellic rock": "psychedelic rock",
    "heavy psych": "psychedelic rock",
    "psych rock": "psychedelic rock",
    "garaje": "garage rock",
    "garage": "garage rock",
    "kraut": "krautrock",
    "kraut rock": "krautrock",
    "shoegazing": "shoegaze",
    "gaze": "shoegaze",
    "songwriter": "singer songwriter",
    "singer songwriter": "singer songwriter",
    "cantautor": "singer songwriter",
    "cantautora": "singer songwriter",
    "cantautores": "singer songwriter",
    "kantautorea": "singer songwriter",
    "kantagintza": "singer songwriter",
    "cancion de autor": "singer songwriter",
    "musica de autor": "singer songwriter",
    "autor": "singer songwriter",
    "americana": "americana",
    "alt country": "alternative country",
    "country alt": "alternative country",
    "alternative country rock": "alternative country",
    "rockmantic": "rock",
    "rock and roll punk": "punk rock",
    "goth": "gothic rock",
    "gothic": "gothic rock",
    "goth rock": "gothic rock",
    "dark wave": "darkwave",
    "cold wave": "coldwave",
    "minimal wave": "minimal synth",
    "synth pop": "synthpop",
    "tecnopop": "synthpop",
    "techno pop": "synthpop",
    "electropop": "synthpop",
    "electro pop": "synthpop",
    "new wave": "new wave",
    "nueva ola": "new wave",
    "hyper pop": "hyperpop",
    "bedroom": "bedroom pop",
    "lo fi": "lo fi",
    "lofi": "lo fi",
    "low fi": "lo fi",
    # electrónica
    "electronic music": "electronic",
    "electronica": "electronic",
    "electronics": "electronic",
    "elektronika": "electronic",
    "electronica experimental": "experimental electronic",
    "alternative electronica": "experimental electronic",
    "alternative electronic": "experimental electronic",
    "i d m": "idm",
    "idm experemental": "idm",
    "techno and variations": "techno",
    "tekno": "techno",
    "underground techno": "techno",
    "hardtechno": "hard techno",
    "hardtechno acid techno": "hard techno",
    "techno electro hardtechno": "hard techno",
    "trance electro techno": "techno",
    "electro techno": "electro",
    "techno industrial": "industrial techno",
    "minimal techno industrial": "industrial techno",
    "minimaltechno": "minimal techno",
    "deephouse": "deep house",
    "housemusic": "house",
    "house music": "house",
    "tech house": "tech house",
    "deep tech": "tech house",
    "bumping": "poky",
    "hardbass": "poky",
    "scouse house": "poky",
    "bakalao": "poky",
    "hard dance": "poky",
    "makina": "poky",
    "ukg": "uk garage",
    "ukgrime": "grime",
    "ukroots": "roots reggae",
    "uk steppa": "steppa",
    "uk dub": "dub",
    "uk bass": "bass music",
    "bass": "bass music",
    "global bass": "bass music",
    "tropical bass": "bass music",
    "edm": "dance",
    "dance music": "dance",
    "club": "dance",
    "club music": "dance",
    "clubbing": "dance",
    "club culture": "dance",
    "dancefloor": "dance",
    "breaks": "breakbeat",
    "break beats": "breakbeat",
    "broken beat": "breakbeat",
    "hardcore breaks": "breakbeat",
    "chill": "chillout",
    "chill out": "chillout",
    "relax": "chillout",
    "relaxation": "chillout",
    "old school": "old school",
    "oldschool": "old school",
    "old skool": "old school",
    "old_school": "old school",
    "vgm": "video game music",
    "video game": "video game music",
    "videogame music": "video game music",
    "game soundtrack": "video game music",
    "game music": "video game music",
    "8bit": "chiptune",
    "8 bit": "chiptune",
    "chip tune": "chiptune",
    "ost": "soundtrack",
    "bso": "soundtrack",
    "banda sonora": "soundtrack",
    "original soundtrack": "soundtrack",
    "film score": "soundtrack",
    "film music": "soundtrack",
    "cinematic": "soundtrack",
    "cinematic electronic": "soundtrack",
    "cinematic soundscape": "soundtrack",
    "documentary music": "soundtrack",
    "synthwave and darksynth": "synthwave",
    "synthwave 80s": "synthwave",
    "darksynth": "synthwave",
    "retrowave": "synthwave",
    "old school dungeon synth": "dungeon synth",
    "dark dungeon music": "dungeon synth",
    "dungeon metal": "dungeon synth",
    "comfy synth": "dungeon synth",
    "winter synth": "dungeon synth",
    "fantasy synth": "dungeon synth",
    "medieval synth": "dungeon synth",
    "trip hop": "trip hop",
    "triphop": "trip hop",
    "nujazz": "nu jazz",
    "future jazz": "nu jazz",
    "jazz and improvised music": "free improvisation",
    "improvisation": "free improvisation",
    "improvised music": "free improvisation",
    "improv": "free improvisation",
    "free improv": "free improvisation",
    "improvisacion": "free improvisation",
    "improvisacion libre": "free improvisation",
    "libre improvisacion": "free improvisation",
    "avant": "avant garde",
    "avantgarde": "avant garde",
    "avant garde jazz": "free jazz",
    "avantgardejazz": "free jazz",
    "freejazz": "free jazz",
    "fusion": "jazz fusion",
    "fusion jazz": "jazz fusion",
    "field recordings": "field recording",
    "fiedrecording": "field recording",
    "phonography": "field recording",
    "musique concrete": "musique concrete",
    "concrete": "musique concrete",
    "acousmatic": "electroacoustic",
    "electroacustic": "electroacoustic",
    "electroacustica": "electroacoustic",
    "sound art": "sound art",
    "art sonore": "sound art",
    "arte sonoro": "sound art",
    "soundscape": "ambient",
    "soundscapes": "ambient",
    "sound textures": "ambient",
    "ambience": "ambient",
    "ambient music": "ambient",
    "droneambient": "drone ambient",
    "ambient drone": "drone ambient",
    "dark ambient drone": "dark ambient",
    "dark ambient noise": "dark ambient",
    "ritual": "ritual ambient",
    "damned ritual": "ritual ambient",
    "new age music": "new age",
    "meditation": "new age",
    "meditative": "new age",
    "mantra": "new age",
    "spiritual": "new age",
    "neo classical": "neoclassical",
    "neoclassic": "neoclassical",
    "neo classic": "neoclassical",
    "modern classical": "contemporary classical",
    "clasical music": "classical",
    "classical music": "classical",
    "clasica": "classical",
    "musica clasica": "classical",
    "klasikoa": "classical",
    "orchestral music": "orchestral",
    "sinfonico": "symphonic",
    "rock sinfonico": "symphonic rock",
    "harsh noise": "harsh noise",
    "power electronics": "power electronics",
    "ruido": "noise",
    "zarata": "noise",
    "white noise": "noise",
    "rhythmic noise": "industrial",
    "industria": "industrial",
    "electro industrial": "ebm",
    "ebm dark electro": "ebm",
    "dark electro": "ebm",
    "world": "world music",
    "world beats": "world music",
    "fourth world music": "world music",
    "world groove": "world music",
    "ethnic": "world music",
    "african": "afro",
    "afro beat": "afrobeat",
    "afro cuban": "latin",
    "afro latin": "latin",
    "latino": "latin",
    "latin music": "latin",
    "tropical": "latin",
    "tropicalia": "mpb",
    "brazilian": "mpb",
    "bossa": "bossa nova",
    "son cubano": "salsa",
    "roots": "roots reggae",
    "root": "roots reggae",
    "reggae roots": "roots reggae",
    "roots reggae dub": "roots reggae",
    "roots dub records": "roots reggae",
    "reggae dub": "dub reggae",
    "dub reggae": "dub reggae",
    "reggae dancehall hip hop": "dancehall",
    "dancehall reggae": "dancehall",
    "ragga": "raggamuffin",
    "reagge": "reggae",
    "jah music": "roots reggae",
    "conscious music": "roots reggae",
    "rockers": "roots reggae",
    "steppers": "steppa",
    "steppas": "steppa",
    "stepper": "steppa",
    "stepper one drop dub two drops": "steppa",
    "rub a dub": "dub",
    "dubwise": "dub",
    "lo end dub": "dub",
    "dub noir": "dub",
    "melodica dub": "dub",
    "sound system": "sound system",
    "soundsystem": "sound system",
    "riddim": "dancehall",
    "flamenco fusion": "flamenco",
    "pop flamenco": "flamenco",
    "flamenco rock": "flamenco",
    "rock flamensivo": "flamenco",
    "folclore": "folk",
    "folklore": "folk",
    "folk music": "folk",
    "traditional folk": "folk",
    "traditional": "folk",
    "traditional music": "folk",
    "musica tradicional": "folk",
    "acustico": "acoustic",
    "acustica": "acoustic",
    "acustic": "acoustic",
    "accoustic": "acoustic",
    "akustikoa": "acoustic",
    "acoustic guitar": "acoustic",
    "acoustic guitar solo": "acoustic",
    "guitar instrumental": "instrumental",
    "instrumental guitar": "instrumental",
    "almost instrumental": "instrumental",
    "instrumentals": "instrumental",
    "instrumentala": "instrumental",
    "spoken word poetry": "spoken word",
    "poetry and music": "spoken word",
    "poems": "spoken word",
    "poetry": "spoken word",
    "poesia": "spoken word",
    "acapella": "a cappella",
    "acappella": "a cappella",
    "choral": "choral",
    "vocal harmonies": "choral",
    "comedy": "comedy",
    "comedy songs": "comedy",
    "comedia": "comedy",
    "humor": "comedy",
    "infantil": "infantil",
    "infantiles": "infantil",
    "haurrak": "infantil",
    "haurrentzako": "infantil",
    "kids": "infantil",
    "children": "infantil",
    "musica infantil": "infantil",
    "horror": "horror",
    "horror disco": "horror disco",
    "giallo disco": "horror disco",
    "italo": "italo disco",
    "urban": "urban",
    "urbano": "urban",
    "urban music": "urban",
    "musica urbana": "urban",
    "urban pop": "urban",
    "corean pop": "k pop",
    "kpop": "k pop",
    "jazz manouche": "gypsy jazz",
    "gypsy": "gypsy jazz",
    "swing jazz": "swing",
    "boogie": "boogie woogie",
    "internet music": "internetcore",
    "trap music": "trap",
    "cloud rap": "trap",
    "drill": "drill",
    "abstract": "abstract",
    "leftfield": "experimental electronic",
    "minimalism": "minimal",
    "minimalist": "minimal",
    "contemporary": "contemporary classical",
    "hardtek": "hardtek",
    "tribe": "hardtek",
    "free tekno": "hardtek",
    "gabber": "hardcore techno",
    "happy hardcore": "hardcore techno",
    "hardstyle": "hardcore techno",
    "schranz": "hard techno",
    "eurotrance": "trance",
    "vocal trance": "trance",
    "progressive trance": "trance",
    "psytrance": "trance",
    "goa": "trance",
    "eurodance": "dance",
    "pop trance": "trance",
    "juke footwork": "footwork",
    "2 step": "uk garage",
    "2 step garage": "uk garage",
    "speed garage": "uk garage",
    "future garage": "uk garage",
    "melodic": "melodic rock",
    "epic": "power metal",
    "epic music": "soundtrack",
    "dark": "dark ambient",
    "groove": "funk",
    "funky": "funk",
    "jazzy": "nu jazz",
    "jazzgroove": "nu jazz",
    "beat": "beats",
    "beat tape": "beats",
    "beattape": "beats",
    "beatmaker": "beats",
    "dj": "dj",
    "dj tools": "dj",
    "dj tool": "dj",
    "medieval": "medieval",
    "medieval music": "medieval",
    "early music": "medieval",
    "baroque": "classical",
    "celtic": "celtic",
    "celtic music": "celtic",
    "irish music": "celtic",
    "balkan": "balkan",
    "arabic": "world music",
    "mpb": "mpb",
    "ranchera": "latin",
    "cumbia": "cumbia",
    "guaracha": "guaracha",
    "reggaeton": "reggaeton",
    "amapiano": "afro",
    "afro": "afro",
    "afrobeat": "afrobeat",
    "surf": "surf rock",
    "surf music": "surf rock",
    "surf instro": "surf rock",
    "surf oscuro": "surf rock",
    "instro": "surf rock",
    "rockabilly": "rockabilly",
    "psychobilly": "psychobilly",
    "crocobilly": "psychobilly",
    "pop abilly": "rockabilly",
    "glam": "glam rock",
    "aor": "melodic rock",
    "hardrock": "hard rock",
    "heavy rock": "hard rock",
    "art blues": "blues",
    "bluesy": "blues",
    "blues harp": "blues",
    "punk band": "punk",
    "rap band": "rap",
    "neopunk": "punk",
    "punk patatero": "punk",
    "punk estiloso": "punk",
    "mongo punk": "punk",
    "pathetic punk": "punk",
    "arcade punk": "punk",
    "young punk": "punk",
    "exotic punk": "punk",
    "ollateiko punk e": "punk",
    "punk is not dead": "punk",
    "rock txatarrero": "rock",
    "rock urbano": "urban rock",
    "urban rock": "urban rock",
    "pop radical": "pop",
    "toxic pop": "pop",
    "falsepop": "pop",
    "brioche pop": "pop",
    "political pop": "pop",
    "pop music": "pop",
    "songs": "pop",
    "canciones": "pop",
    "pop classic rock rock and roll": "classic rock",
    "vintage rock": "classic rock",
    "70s rock": "classic rock",
    "70s hard rock": "hard rock",
    "90s rock": "alternative rock",
    "90s house": "house",
    "classic house": "house",
    "60s garage r and b": "garage rock",
    "amerikana garage rock kick ass": "garage rock",
    "getxo bilbao gringo rock": "rock",
    "alternative rock laudio": "alternative rock",
    "improvisacion libre bilbao": "free improvisation",
    "freejazz bilbao": "free jazz",
    "barcelona punk": "punk",
    "new york hardcore": "hardcore",
    "detroit techno": "techno",
    "berlin school": "berlin school",
    "hardgroove": "hard techno",
    "hardgroove techno": "hard techno",
    "deep techno": "techno",
    "dark techno": "techno",
    "melodic techno": "techno",
    "leftfield techno": "techno",
    "techno house": "tech house",
    "electro dub": "electro dub",
    "electro electrobass breaks bass": "electro",
    "electro glam": "electro",
    "electro punk": "synth punk",
    "techno punk": "synth punk",
    "punk funk": "dance punk",
    "funk punk": "dance punk",
    "indie dance": "dance punk",
    "electro rock": "electronic rock",
    "electronic rock": "electronic rock",
    "synth driven": "synth",
    "synths": "synth",
    "synthesizer": "synth",
    "sinthesizer": "synth",
    "modular": "synth",
    "modular synth": "synth",
    "fm synth": "synth",
    "analog": "synth",
    "sequences": "berlin school",
    "krautrock": "krautrock",
    "space rock": "space rock",
    "space": "space rock",
    "space music": "ambient",
    "cosmic": "space rock",
    "space disco": "disco",
    "nu disco": "disco",
    "dark disco": "disco",
    "italo noise": "noise",
    "experimental noise": "noise",
    "devotional noise": "noise",
    "noise punk": "noise rock",
    "noisecore": "grindcore",
    "goregrind": "goregrind",
    "deathgrind": "grindcore",
    "brutal death grind": "grindcore",
    "powerviolence": "powerviolence",
    "power violence": "powerviolence",
    "fastcore": "fastcore",
    "youth crew": "hardcore punk",
    "beatdown": "beatdown",
    "metallic hardcore": "metalcore",
    "hardcore metal": "metalcore",
    "melodic metalcore": "metalcore",
    "post metalcore": "metalcore",
    "mathcore": "mathcore",
    "math": "math rock",
    "progressive core": "mathcore",
    "crazy core": "mathcore",
    "synth core": "synthcore",
    "core": "hardcore",
    "bidasoa core": "hardcore",
    "horrorcore": "horrorcore",
    "skramz": "screamo",
    "emoviolence": "screamo",
    "reverbcore": "reverbcore",
    "pop psicodelia reverb core": "reverbcore",
    "dreampunk": "dreampunk",
    "internetcore": "internetcore",
    "digicore": "digicore",
    "hexd": "digicore",
    "medicalcore": "postvore",
    "deathdream": "postvore",
    "postvore": "postvore",
    "breakcore for autists": "breakcore",
    "queercore": "queercore",
    "queer punk": "queercore",
    "riot grrrl": "riot grrrl",
    "riot folk": "anarcho folk",
    "anarcho folk": "anarcho folk",
    "punk folk": "folk punk",
    "folk punk": "folk punk",
    "acoustic punk": "folk punk",
    "political punk": "punk",
    "political punk rock": "punk",
    "political rock": "rock",
    "diy punk": "punk",
    "diy rock": "rock",
    "feminist rock": "rock",
    "comedy rock": "comedy",
    "nerd rock": "rock",
    "action rock": "rock",
    "sleaze rock": "glam rock",
    "bloody rock": "rock",
    "sudden rock": "rock",
    "power rock": "hard rock",
    "modern rock": "alternative rock",
    "eclectic rock": "rock",
    "noise epic rock": "noise rock",
    "deep sea rock": "rock",
    "oz rock": "rock",
    "scandinavian rock": "rock",
    "swamp rock": "swamp rock",
    "swamp blues": "blues",
    "swampy": "swamp rock",
    "southern": "southern rock",
    "desert rock": "stoner rock",
    "stoner": "stoner rock",
    "stoner metal": "stoner rock",
    "stoner punk": "stoner rock",
    "stoner punk rock": "stoner rock",
    "sludge": "sludge metal",
    "drone metal": "drone doom",
    "drone funeral doom": "funeral doom",
    "occult": "occult rock",
    "pagan": "pagan metal",
    "viking": "viking metal",
    "black sabbath": "doom metal",
    "ramones": "punk rock",
    "pixies": "indie rock",
    "rage against the machine": "rap metal",
    "wilhelm": RESTO,
    "sound experimental games": "experimental",
    "experimental with others": "experimental",
    "experimental easy listening": "experimental",
    "experimental muzak": "experimental",
    "esperimentala": "experimental",
    "experiemental": "experimental",
    "non conventional": "experimental",
    "eclectic": "experimental",
    "eklektrik": "experimental",
    "raw": "raw punk",
    "raw sounds": "raw punk",
    "raw hardcore": "hardcore punk",
    "black metal punk": "blackened punk",
    "blackened crust": "blackened crust",
    "blackened hardcore": "blackened punk",
    "blackened death metal": "black death",
    "black death": "black death",
    "thrash death": "death metal",
    "old school metal": "heavy metal",
    "old school black metal": "black metal",
    "oldschool death metal": "death metal",
    "underground metal": "metal",
    "rotten metal": "metal",
    "comic metal": "metal",
    "cannabis metal": "stoner rock",
    "dark metal": "gothic metal",
    "female fronted metal": "metal",
    "dark power metal": "power metal",
    "epic metal": "power metal",
    "modern dnb": "drum and bass",
    "deep dnb": "drum and bass",
    "deep drum and bass": "drum and bass",
    "techy dnb": "drum and bass",
    "atmospheric dnb": "drum and bass",
    "dark dnb": "drum and bass",
    "rolling dnb": "drum and bass",
    "liquid": "drum and bass",
    "liquid dnb": "drum and bass",
    "melodic dnb": "drum and bass",
    "jump up dnb": "drum and bass",
    "jump up drum and bass": "drum and bass",
    "dancefloor dnb": "drum and bass",
    "techstep": "drum and bass",
    "neurofunk": "drum and bass",
    "atmospheric jungle": "jungle",
    "lofi house": "house",
    "filter house": "house",
    "rally house": "house",
    "tribal house": "house",
    "hard house": "house",
    "microhouse": "minimal house",
    "minimal house": "minimal house",
    "minimal": "minimal",
    "acid": "acid",
    "acid house": "acid",
    "acid techno": "acid",
    "ghettotech": "electro",
    "bounce": "electro",
    "freestyle": "electro",
    "bassline": "uk garage",
    "future bass": "bass music",
    "glitch pop": "glitch",
    "plunderphonics": "sampling",
    "sampling": "sampling",
    "collage": "sampling",
    "turntablism": "turntablism",
    "scratch music": "turntablism",
    "g funk": "g funk",
    "gangsta rap": "rap",
    "hard rap": "rap",
    "dark rap": "rap",
    "rap latino": "rap",
    "rap alternative": "rap",
    "underground rap": "underground hip hop",
    "pop hip hop": "hip hop",
    "abstract hip hop": "abstract hip hop",
    "experimental hip hop": "abstract hip hop",
    "boom bap rap": "boom bap",
    "dark boom bap": "boom bap",
    "punk hop": "hip hop",
    "trap fusion triste": "trap",
    "pop electronic": "synthpop",
    "dance pop": "synthpop",
    "dark pop": "darkwave",
    "dark punk": "deathrock",
    "dark dream pop": "dream pop",
    "dark folk": "dark folk",
    "neofolk": "dark folk",
    "doom folk": "dark folk",
    "pagan folk": "dark folk",
    "epic folk": "folk",
    "freak folk": "freak folk",
    "anti folk": "freak folk",
    "psych folk": "freak folk",
    "folk psicodelia": "freak folk",
    "chamber pop": "chamber pop",
    "chamber": "chamber pop",
    "art pop": "art pop",
    "jangle pop": "jangle pop",
    "twee": "indie pop",
    "twee pop": "indie pop",
    "c86": "indie pop",
    "noise pop": "noise pop",
    "dream pop": "dream pop",
    "slowcore": "slowcore",
    "sadcore": "slowcore",
    "britpop": "britpop",
    "mod": "mod",
    "freakbeat": "freakbeat",
    "beat music": "freakbeat",
    "power pop": "power pop",
    "pub rock": "pub rock",
    "punk pub rock": "pub rock",
    "proto punk": "proto punk",
    "proto metal": "hard rock",
    "no wave": "no wave",
    "post rock instrumental": "post rock",
    "instrumental post rock": "post rock",
    "post folk": "post rock",
    "post industrial": "industrial",
    "post": "post punk",
    "post punk": "post punk",
    "post metal": "post metal",
    "math rock": "math rock",
    "ambient rock": "post rock",
    "instrumental rock": "instrumental rock",
    "rock instrumental": "instrumental rock",
    "instrumental metal": "instrumental rock",
    "guitar rock": "rock",
    "power trio": "rock",
    "power duo": "rock",
    "one man band": RESTO,
    "duo": RESTO,
    "band": RESTO,
    "banda": RESTO,
    "taldea": RESTO,
    "music": RESTO,
    "musica": RESTO,
    "musika": RESTO,
    "singer": RESTO,
    "vocal": "otro:voz",
    "vocals": "otro:voz",
    "voice": "otro:voz",
    "voz": "otro:voz",
    "ahotsa": "otro:voz",
    "female vocals": "otro:voz",
    "female vocalist": "otro:voz",
    "female fronted": "otro:voz",
    "female vocal": "otro:voz",
    "women": "otro:voz",
    "musica mujeres": "otro:voz",
    "spanish pop": "pop",
    "spanish rock": "rock",
    "spanish metal": "metal",
    "spanish punk": "punk",
    "spanish rap": "rap",
    "punk español": "punk",
    "pop en español": "pop",
    "rap español": "rap",
    "rap en español": "rap",
    "rock español": "rock",
    "rock en español": "rock",
    "rock en castellano": "rock",
    "pop rock en español": "pop rock",
    "punk argentino": "punk",
    "musica chilena": "latin",
    "latin rock": "latin rock",
    "latin folk": "latin",
    "latin jazz": "latin jazz",
    "latin pop": "latin",
    "rumba": "rumba",
    "salsa": "salsa",
    "tango": "tango",
    "samba": "samba",
    "batucada": "samba",
    "muineira": "celtic",
    "gaita": "celtic",
    "chanson": "chanson",
    "chanson francaise": "chanson",
    "chanson française": "chanson",
    "occitan": "otro:occitan",
    "gascon": "otro:occitan",
    "western": "country",
    "western swing": "country",
    "bluegrass": "bluegrass",
    "country folk": "country",
    "country blues": "blues",
    "delta blues": "blues",
    "blues folk": "folk",
    "folk blues": "folk",
    "rock folk": "folk rock",
    "folk pop rock": "folk pop",
    "folk pop acoustic alternative": "folk pop",
    "folk indie pop": "indie folk",
    "indie folk rock": "indie folk",
    "acoustic folk": "folk",
    "ambient folk": "folk",
    "experimental folk": "freak folk",
    "european folk music": "folk",
    "folk world country": "folk",
    "americana rock alt folk": "americana",
    "roots rock": "americana",
    "nature": "field recording",
    "nature sounds": "field recording",
    "landscapes": "ambient",
    "infinite loops": "ambient",
    "fantasy": "dungeon synth",
    "fantasy music": "dungeon synth",
    "fantasy ambient": "dungeon synth",
    "sci fi": "synthwave",
    "cyberpunk": "synthwave",
    "vapor": "vaporwave",
    "vaporwave": "vaporwave",
    "chillwave": "chillwave",
    "lounge": "lounge",
    "exotica": "lounge",
    "easy listening": "lounge",
    "balearic": "balearic",
    "downtempo": "downtempo",
    "chillout": "chillout",
    "trip": "trip hop",
    "trippy": "psychedelic",
    "classic": "classic rock",
    "deep": "deep house",
    "cold": "coldwave",
    "ethereal": "ethereal",
    "ethereal wave": "ethereal",
    "tribal": "tribal",
    "computer music": "experimental electronic",
    "folktronica": "folktronica",
    "devotional": "devotional",
    "rocksteady": "rocksteady",
    "raggamuffin": "raggamuffin",
    "power electronics": "power electronics",
    "melancholy": "slowcore",
    "sad": "slowcore",
    "winter": "dungeon synth",
    "summer": "pop",
    "happy": "pop",
    "amor": "pop",
    "hyper energetic": "punk rock",
    "kick ass": "rock",
    "extreme music": "metal",
    "extreme underground sounds": "metal",
    "mastering of the universe": RESTO,
    "outside your house": RESTO,
    "primitive": "raw punk",
    "primative": "raw punk",
    "reverb": "reverbcore",
    "fuzz": "garage rock",
    "feedback": "noise rock",
    "no input mixer": "harsh noise",
    "autotune": "trap",
    "producer": "beats",
    "beats": "beats",
    "piano solo": "otro:piano",
    "solo piano": "otro:piano",
    "performance art": "sound art",
    "theatre": "sound art",
    "video": RESTO,
    "anime": RESTO,
    "samurai": RESTO,
    "cover": "otro:versiones",
    "covers": "otro:versiones",
    "version": "otro:versiones",
    "versiones": "otro:versiones",
    "versions": "otro:versiones",
    "bertsioak": "otro:versiones",
    "tribute": "otro:versiones",
    "tributo": "otro:versiones",
    "rework": "otro:remix",
    "remix": "otro:remix",
    "remixes": "otro:remix",
    "remezcla": "otro:remix",
    "remezclas": "otro:remix",
    "live": "otro:en directo",
    "live recording": "otro:en directo",
    "live album": "otro:en directo",
    "live looping": "otro:en directo",
    "directo": "otro:en directo",
    "en directo": "otro:en directo",
    "en vivo": "otro:en directo",
    "zuzenean": "otro:en directo",
    "zuzenekoa": "otro:en directo",
    "concert": "otro:en directo",
    "concierto": "otro:en directo",
    "kontzertua": "otro:en directo",
    "demo": "otro:demo",
    "demos": "otro:demo",
    "maqueta": "otro:demo",
    "maketa": "otro:demo",
    "cassette": "otro:cassette",
    "cassettes": "otro:cassette",
    "tape": "otro:cassette",
    "tapes": "otro:cassette",
    "kasete": "otro:cassette",
    "kasetea": "otro:cassette",
    "k7": "otro:cassette",
    "cassette and digital label": "otro:cassette",
    "vinyl": "otro:vinilo",
    "vinilo": "otro:vinilo",
    "binilo": "otro:vinilo",
    "lp": "otro:vinilo",
    "long play": "otro:vinilo",
    "12": "otro:vinilo",
    "7": "otro:vinilo",
    "cd": "otro:cd",
    "ep": "otro:ep",
    "single": "otro:single",
    "split": "otro:split",
    "compilation": "otro:recopilatorio",
    "compilations": "otro:recopilatorio",
    "recopilatorio": "otro:recopilatorio",
    "recopilacion": "otro:recopilatorio",
    "bilduma": "otro:recopilatorio",
    "rock compilation": "otro:recopilatorio",
    "various artists": "otro:recopilatorio",
    "va": "otro:recopilatorio",
    "vvaa": "otro:recopilatorio",
    "album": "otro:album",
    "lp album": "otro:album",
    "concept album": "otro:album",
    "digital": "otro:digital",
    "download": "otro:digital",
    "free download": "otro:digital",
    "free": "otro:digital",
    "name your price": "otro:digital",
    "limited edition": "otro:vinilo",
    "reissue": "otro:reedicion",
    "reedicion": "otro:reedicion",
    "retro": "otro:decada 80",
    "ochentero": "otro:decada 80",
    "sixties": "otro:decada 60",
    "seventies": "otro:decada 70",
    "eighties": "otro:decada 80",
    "nineties": "otro:decada 90",
    "euskara": "otro:euskaraz",
    "euskaraz": "otro:euskaraz",
    "euskera": "otro:euskaraz",
    "euskeraz": "otro:euskaraz",
    "euskarazko": "otro:euskaraz",
    "en euskera": "otro:euskaraz",
    "basque language": "otro:euskaraz",
    "euskaldun": "otro:euskaraz",
    "rock euskera": "rock",
    "castellano": "otro:castellano",
    "espanol": "otro:castellano",
    "spanish": "otro:castellano",
    "espagnol": "otro:castellano",
    "en castellano": "otro:castellano",
    "en espanol": "otro:castellano",
    "spanish language": "otro:castellano",
    "english": "otro:english",
    "ingles": "otro:english",
    "in english": "otro:english",
    "french": "otro:francais",
    "francais": "otro:francais",
    "frances": "otro:francais",
    "en francais": "otro:francais",
    "catalan": "otro:catala",
    "catala": "otro:catala",
    "galego": "otro:galego",
    "gallego": "otro:galego",
    "italiano": "otro:italiano",
    "italian": "otro:italiano",
    "portugues": "otro:portugues",
    "portuguese": "otro:portugues",
    "piano": "otro:piano",
    "guitar": "otro:guitarra",
    "guitars": "otro:guitarra",
    "guitarra": "otro:guitarra",
    "gitarra": "otro:guitarra",
    "electric guitar": "otro:guitarra",
    "guitarra electrica": "otro:guitarra",
    "cello": "otro:cello",
    "violoncello": "otro:cello",
    "violonchelo": "otro:cello",
    "violin": "otro:violin",
    "violín": "otro:violin",
    "strings": "otro:cuerdas",
    "harp": "otro:arpa",
    "harpa": "otro:arpa",
    "arpa": "otro:arpa",
    "drums": "otro:bateria",
    "drumset": "otro:bateria",
    "bateria": "otro:bateria",
    "percussion": "otro:percusion",
    "percusion": "otro:percusion",
    "mellotron": "otro:teclados",
    "organ": "otro:teclados",
    "keyboards": "otro:teclados",
    "oboe": "otro:vientos",
    "trumpet": "otro:vientos",
    "trombone": "otro:vientos",
    "sax": "otro:vientos",
    "saxophone": "otro:vientos",
    "saxofon": "otro:vientos",
    "clarinet": "otro:vientos",
    "flute": "otro:vientos",
    "melodica": "otro:vientos",
    "accordion": "otro:acordeon",
    "acordeon": "otro:acordeon",
    "akordeoia": "otro:acordeon",
    "hurdy gurdy": "otro:zanfona",
    "zanfona": "otro:zanfona",
    "vibraphone": "otro:percusion",
    "mpc": "otro:maquinas",
    "303": "otro:maquinas",
    "808": "otro:maquinas",
    "909": "otro:maquinas",
    "606": "otro:maquinas",
    "drum machine": "otro:maquinas",
    "caja de musica": "otro:maquinas",
    "ableton": RESTO,
    "ableton live": RESTO,
    "fl studio": RESTO,
    "diy": "otro:diy",
    "d i y": "otro:diy",
    "do it yourself": "otro:diy",
    "autogestion": "otro:diy",
    "autogestionado": "otro:diy",
    "selfmanagement and free creation": "otro:diy",
    "self released": "otro:diy",
    "underground": "otro:underground",
    "undergorund": "otro:underground",
    "subterraneo": "otro:underground",
    "pop underground": "pop",
    "independent": "otro:independiente",
    "independent music": "otro:independiente",
    "independent musician": "otro:independiente",
    "independiente": "otro:independiente",
    "indepedent": "otro:independiente",
    "copyleft": "otro:copyleft",
    "creative commons": "otro:copyleft",
    "anticopyright": "otro:copyleft",
    "antifa": "otro:antifa",
    "antifascist": "otro:antifa",
    "antifascista": "otro:antifa",
    "antifaxista": "otro:antifa",
    "antifa electropop": "synthpop",
    "anticapitalist": "otro:politica",
    "anticapitalista": "otro:politica",
    "political": "otro:politica",
    "politico": "otro:politica",
    "politika": "otro:politica",
    "protest": "otro:politica",
    "protesta": "otro:politica",
    "rebelion": "otro:politica",
    "matxinada": "otro:politica",
    "desobediencia civil": "otro:politica",
    "activism": "otro:politica",
    "anarchist": "otro:politica",
    "anarquista": "otro:politica",
    "anarkista": "otro:politica",
    "queer": "otro:queer",
    "lgtb": "otro:queer",
    "lgtbi": "otro:queer",
    "lgbt": "otro:queer",
    "feminist": "otro:feminismo",
    "feminism": "otro:feminismo",
    "feminista": "otro:feminismo",
    "feminismo": "otro:feminismo",
    "feminismoa": "otro:feminismo",
    "vegan": "otro:vegan",
    "veganismo": "otro:vegan",
    "straight edge": "otro:straight edge",
    "sxe": "otro:straight edge",
    # eslóganes territoriales
    "euskal herria is not spain": LUGAR_PREFIX + "euskal herria",
    "euskal herria is not": LUGAR_PREFIX + "euskal herria",
    "basque country is not": LUGAR_PREFIX + "euskal herria",
    "eh is not spain": LUGAR_PREFIX + "euskal herria",
    "is not spain not": LUGAR_PREFIX + "euskal herria",
    "is not": LUGAR_PREFIX + "euskal herria",
    "not": LUGAR_PREFIX + "euskal herria",
    "qeuskalherria ez da": LUGAR_PREFIX + "euskal herria",
    "euskal herria ez da espainia": LUGAR_PREFIX + "euskal herria",
    "eh": LUGAR_PREFIX + "euskal herria",
    "euskal": LUGAR_PREFIX + "euskal herria",
    "euskal musika": LUGAR_PREFIX + "euskal herria",
    "basque music": LUGAR_PREFIX + "euskal herria",
    "musica vasca": LUGAR_PREFIX + "euskal herria",
    "euskal kantak": LUGAR_PREFIX + "euskal herria",
    "basqueland": LUGAR_PREFIX + "euskal herria",
    "vasque country": LUGAR_PREFIX + "euskal herria",
    "vasc country": LUGAR_PREFIX + "euskal herria",
    "basque _country": LUGAR_PREFIX + "euskal herria",
    "basque country": LUGAR_PREFIX + "euskal herria",
    "basque": LUGAR_PREFIX + "euskal herria",
    "vasco": LUGAR_PREFIX + "euskal herria",
    "bardulia": LUGAR_PREFIX + "gipuzkoa",
    "beruna": LUGAR_PREFIX + "iruñea",
    "pamplona sound": LUGAR_PREFIX + "iruñea",
    "donosti sound": LUGAR_PREFIX + "donostia",
    "bilbo zaharra": LUGAR_PREFIX + "bilbo",
    "crudobilbao": LUGAR_PREFIX + "bilbo",
    "bilbaomusikak": LUGAR_PREFIX + "bilbo",
    "alava underground": LUGAR_PREFIX + "araba",
    "moreda de alava": LUGAR_PREFIX + "araba",
    "noain navarra": LUGAR_PREFIX + "nafarroa",
    "irun kasernarat orereta": LUGAR_PREFIX + "irun",
    "orereta": LUGAR_PREFIX + "errenteria",
    "mondra": LUGAR_PREFIX + "arrasate",
    "ondarru": LUGAR_PREFIX + "ondarroa",
    "gernika": LUGAR_PREFIX + "gernika-lumo",
    "guernica": LUGAR_PREFIX + "gernika-lumo",
    "madrid spain": LUGAR_PREFIX + "madrid",
    "london uk": LUGAR_PREFIX + "london",
    "west london": LUGAR_PREFIX + "london",
    "north east": LUGAR_PREFIX + "united kingdom",
    "newcastle upon tyne": LUGAR_PREFIX + "united kingdom",
    "leeds": LUGAR_PREFIX + "united kingdom",
    "uk": LUGAR_PREFIX + "united kingdom",
    "mexico city": LUGAR_PREFIX + "mexico",
    "juarez": LUGAR_PREFIX + "mexico",
    "buenos aires": LUGAR_PREFIX + "argentina",
    "punta del este": LUGAR_PREFIX + "uruguay",
    "sao paulo": LUGAR_PREFIX + "brasil",
    "brazil": LUGAR_PREFIX + "brasil",
    "italia": LUGAR_PREFIX + "italy",
    "espana": LUGAR_PREFIX + "spain",
    "espainia": LUGAR_PREFIX + "spain",
    "francia": LUGAR_PREFIX + "france",
    "frantzia": LUGAR_PREFIX + "france",
    "la linea de la concepcion": LUGAR_PREFIX + "andalucia",
    "sevilla": LUGAR_PREFIX + "andalucia",
    "granada": LUGAR_PREFIX + "andalucia",
    "mallorca": LUGAR_PREFIX + "spain",
    "medina de pomar": LUGAR_PREFIX + "burgos",
    "toreno": LUGAR_PREFIX + "spain",
    "toledo": LUGAR_PREFIX + "spain",
    "melilla": LUGAR_PREFIX + "spain",
    "murcia": LUGAR_PREFIX + "spain",
    "salamanca": LUGAR_PREFIX + "spain",
    "valencia": LUGAR_PREFIX + "spain",
    "zaragoza": LUGAR_PREFIX + "spain",
    "phoenix": LUGAR_PREFIX + "united states",
    "las vegas": LUGAR_PREFIX + "united states",
    "los angeles": LUGAR_PREFIX + "united states",
    "new york": LUGAR_PREFIX + "united states",
    "detroit": LUGAR_PREFIX + "united states",
    "sacramento": LUGAR_PREFIX + "united states",
    "usa": LUGAR_PREFIX + "united states",
    "oslo": LUGAR_PREFIX + "norway",
    "berlin": LUGAR_PREFIX + "germany",
    "paris": LUGAR_PREFIX + "france",
    "toulouse": LUGAR_PREFIX + "france",
    "bordeaux": LUGAR_PREFIX + "france",
    "corse": LUGAR_PREFIX + "france",
    "tokyo": LUGAR_PREFIX + "japan",
    "hong kong": LUGAR_PREFIX + "hong kong",
    "africa": LUGAR_PREFIX + "africa",
}

# Sinónimos que existen por decisión editorial discutible. Se listan en el
# informe para que Miguel los revise. clave -> motivo.
DOUBTFUL_SYNONYMS: dict[str, str] = {
    "crust punk": "crust y crust punk se funden en un solo nodo",
    "crustcore": "crustcore -> crust",
    "electronica": "electronica (en inglés puede ser un género propio) -> electronic",
    "alternative": "alternative a secas -> alternative rock",
    "indie": "indie a secas -> indie rock",
    "progressive": "progressive a secas -> progressive rock",
    "trash": "trash -> thrash metal (asumido como errata)",
    "trash metal": "trash metal -> thrash metal (asumido como errata)",
    "skinhead": "skinhead (subcultura) -> oi!",
    "euskal musika": "euskal musika / basque music -> lugar:euskal herria (se usa como marca de origen, no de estilo)",
    "basque music": "basque music -> lugar:euskal herria",
    "bumping": "bumping / hardbass / scouse house / bakalao / hard dance -> poky (escena makina)",
    "hardbass": "hardbass -> poky",
    "scouse house": "scouse house -> poky",
    "hard dance": "hard dance -> poky",
    "minimalism": "minimalism (clásica) -> minimal (electrónica)",
    "contemporary": "contemporary -> contemporary classical",
    "dark": "dark a secas -> dark ambient",
    "soundscape": "soundscape -> ambient",
    "world": "world -> world music",
    "roots": "roots -> roots reggae",
    "tropical": "tropical -> latin",
    "epic": "epic -> power metal (podría ser soundtrack)",
    "melodic": "melodic -> melodic rock",
    "groove": "groove -> funk",
    "space": "space -> space rock",
    "cinematic": "cinematic -> soundtrack",
    "post": "post a secas -> post punk",
    "core": "core a secas -> hardcore",
    "death": "death a secas -> death metal",
    "black": "black a secas -> black metal",
    "heavy": "heavy a secas -> heavy metal",
    "doom": "doom -> doom metal",
    "stoner": "stoner -> stoner rock",
    "sludge": "sludge -> sludge metal",
    "garage": "garage -> garage rock (podría ser uk garage)",
    "acoustic guitar": "acoustic guitar -> acoustic",
    "r and b soul": "r&b/soul (umbrella de Bandcamp) -> r&b",
    "hip hop rap": "hip-hop/rap (umbrella de Bandcamp) -> hip hop",
    "is not": "fragmentos de 'euskal herria is not spain' -> lugar:euskal herria",
    "not": "fragmentos de 'euskal herria is not spain' -> lugar:euskal herria",
    "ramones": "nombre de grupo usado como tag -> punk rock",
    "pixies": "nombre de grupo usado como tag -> indie rock",
    "black sabbath": "nombre de grupo usado como tag -> doom metal",
    "rage against the machine": "nombre de grupo usado como tag -> rap metal",
    "trap": "trap (por umbral, cloud rap y autotune cuelgan aquí)",
    "urban": "urban / musica urbana como nodo propio",
    "fuzz": "fuzz -> garage rock",
    "classic": "classic -> classic rock",
    "deep": "deep -> deep house",
    "cold": "cold -> coldwave",
    "alternative rock": "alternative (954 discos, umbrella de Bandcamp) se funde con alternative rock",
    "indie rock": "indie (umbrella de Bandcamp) se funde con indie rock",
    "reverb": "reverb -> reverbcore",
    "spanish": "spanish -> idioma castellano (podría ser lugar)",
    "retro": "retro -> década 80",
    "summer": "summer -> pop",
    "happy": "happy -> pop",
    "songs": "songs / canciones -> pop",
    "women": "women / musica mujeres -> otro:voz",
    "female fronted": "female fronted -> otro:voz",
}

# ---------------------------------------------------------------------------
# 3. Sinónimos por palabra (traducción es/eu/en). "" = palabra que se elimina.
# ---------------------------------------------------------------------------
WORD_SYNONYMS: dict[str, str] = {
    # palabras vacías (artículos, preposiciones) y "música"
    "en": "", "in": "", "de": "", "del": "", "la": "", "el": "", "los": "", "las": "",
    "the": "", "of": "", "y": "", "e": "", "eta": "", "et": "",
    "music": "", "musica": "", "musika": "", "musique": "", "musikoa": "",
    "sounds": "", "sonidos": "", "soinuak": "",
    "rocka": "rock", "rockeroa": "rock", "rocker": "rock",
    "punka": "punk", "punkie": "punk",
    "metala": "metal",
    "rapa": "rap",
    "trapa": "trap",
    "folka": "folk",
    "popa": "pop",
    "jazza": "jazz",
    "hardcorra": "hardcore",
    "electronica": "electronic", "electronico": "electronic", "electronique": "electronic",
    "elektronika": "electronic", "elektronikoa": "electronic",
    "experimentala": "experimental", "esperimentala": "experimental", "experimentales": "experimental",
    "psicodelico": "psychedelic", "psicodelica": "psychedelic", "psicodelia": "psychedelic",
    "psikodelikoa": "psychedelic", "psychedelia": "psychedelic", "psych": "psychedelic",
    "acustico": "acoustic", "acustica": "acoustic", "akustikoa": "acoustic",
    "alternativo": "alternative", "alternativa": "alternative", "alternatiboa": "alternative",
    "progresivo": "progressive", "progresiva": "progressive",
    "melodico": "melodic", "melodica": "melodic", "melodiko": "melodic",
    "instrumentala": "instrumental",
    "industriala": "industrial",
    "clasica": "classical", "clasico": "classical", "klasikoa": "classical",
    "tradicional": "traditional", "tradizionala": "traditional",
    "oscuro": "dark", "oscura": "dark", "iluna": "dark",
    "ruido": "noise", "zarata": "noise",
    "gitarra": "guitar", "guitarra": "guitar",
    "bateria": "drums",
    "elektro": "electro",
    "sinfonico": "symphonic", "sinfonica": "symphonic",
    "urbano": "urban", "urbana": "urban",
    "underground": "underground",
    "kantak": "songs", "kanta": "songs", "abestiak": "songs",
    "herri": "folk", "herrikoia": "folk",
    "vasco": "basque", "vasca": "basque", "euskal": "basque", "basques": "basque",
    "euskadi": "basque", "euzkadi": "basque", "napar": "basque", "nafar": "basque",
    "espanol": "spanish", "espanola": "spanish", "castellano": "spanish",
    "argentino": "argentinian",
    "latino": "latin", "latina": "latin",
    "hiphop": "hip hop", "hopa": "hop",
    "hardcore": "hardcore",
}

# Palabras de lugar/gentilicio que se quitan de un tag mixto ("punk vasco" ->
# "punk"). El tag queda marcado como dudoso.
DEMONYM_WORDS = {"basque", "spanish", "argentinian", "bilbao", "bilbo", "gasteiz",
                 "vitoria", "donostia", "donosti", "iruna", "irunea", "pamplona",
                 "zarautz", "getxo", "laudio", "mondra", "arrasate", "barcelona",
                 "madrid", "detroit", "berlin", "london"}

# Prefijos que cambian el sentido: colgar "post metal" de "metal" es dudoso.
MODIFIER_PREFIXES = {"post", "anti", "proto", "neo", "no", "non", "pre", "nu", "avant"}

# ---------------------------------------------------------------------------
# Vocabulario de género. Un concepto es género si (a) está en GENRE_TERMS o
# (b) alguna palabra es una raíz de GENRE_ROOTS o termina en una raíz pegada
# (crustcore, blackgaze). Todo lo demás cae en "resto".
# ---------------------------------------------------------------------------
GENRE_ROOTS = {
    "rock", "punk", "metal", "core", "gaze", "wave", "synth", "pop", "jazz",
    "blues", "folk", "funk", "soul", "disco", "house", "techno", "trance",
    "electro", "electronic", "ambient", "drone", "noise", "industrial", "dub",
    "reggae", "ska", "rap", "hop", "trap", "grime", "bass", "beat", "beats",
    "step", "garage", "hardcore", "grind", "crust", "doom", "sludge", "stoner",
    "thrash", "death", "black", "emo", "screamo", "indie", "shoegaze", "surf",
    "country", "americana", "swing", "bebop", "tango", "cumbia", "salsa",
    "flamenco", "rumba", "bossa", "samba", "latin", "afro", "afrobeat",
    "dancehall", "ragga", "steppa", "idm", "glitch", "breakbeat", "breakcore",
    "jungle", "dnb", "acid", "minimal", "experimental", "improvisation",
    "classical", "orchestral", "symphonic", "choral", "opera", "chanson",
    "soundtrack", "lofi", "lo", "chiptune", "vaporwave", "synthwave", "kraut",
    "krautrock", "psychedelic", "psych", "grunge", "goth", "gothic", "darkwave",
    "coldwave", "ebm", "dance", "rave", "hardtek", "hardstyle", "footwork",
    "juke", "dubstep", "oi", "billy", "rockabilly", "psychobilly", "slam",
    "djent", "deathcore", "metalcore", "mathcore", "powerviolence", "fastcore",
    "grindcore", "goregrind", "crossover", "beatdown", "hxc", "hc", "punkrock", "oi",
    "electronica", "downtempo", "chillout", "chillwave", "lounge", "balearic",
    "new age", "neoclassical", "spoken", "acoustic", "instrumental", "world",
    "celtic", "balkan", "medieval", "gypsy", "urban", "reggaeton", "mpb",
    "sound art", "musique", "acousmatic", "electroacoustic", "harsh",
    "power electronics", "noisecore", "fusion", "boogie", "mod",
    "freakbeat", "britpop", "twee", "slowcore", "sadcore", "shoegazing",
    "ethereal", "tribal",
    "drill", "boom bap", "turntablism", "hyperpop", "digicore", "internetcore",
    "postvore", "dreampunk", "reverbcore", "queercore", "riot", "horrorcore",
    "cabaret", "vaudeville", "gospel", "ambientdub", "dubtechno", "hardgroove",
    "devotional", "abstract", "rocksteady", "raggamuffin", "folktronica",
    "schranz", "gabber", "makina", "poky", "bumping", "hardbass", "eurodance",
    "italo", "electropop", "synthpop", "tecnopop", "kpop", "jpop", "guaracha",
    "cumbiaton", "bachata", "merengue", "bolero", "ranchera", "mariachi",
    "vals", "polka", "trikitixa", "txalaparta", "alboka", "bertso",
    "bertsolaritza", "txistu", "kantagintza", "kantautorea",
}
# Raíces que se reconocen PEGADAS al final de una palabra (crustcore, blackgaze,
# rapmetal). Lista corta a propósito: "ska" pegada cazaría "petruska".
GLUED_SUFFIXES = {
    "core", "gaze", "wave", "punk", "rock", "metal", "pop", "step", "beat",
    "billy", "tronica", "hop", "house", "techno", "grind", "crust", "tek",
    "synth", "jazz", "funk", "tronic", "noise", "folk", "trance", "disco",
}

GENRE_TERMS = {
    "a cappella", "abstract hip hop", "afro", "alternative country", "alternative rock",
    "anarcho folk", "anarcho punk", "art pop", "atmospheric", "avant garde",
    "berlin school", "black death", "blackened crust", "blackened doom",
    "blackened punk", "bluegrass", "boom bap", "chamber pop", "cinematic",
    "comedy", "d beat", "dark folk", "death doom metal", "dj", "dream pop",
    "dungeon synth", "electro dub", "field recording",
    "free improvisation", "free jazz", "freak folk", "funeral doom", "g funk",
    "guaracha", "high energy rock", "horror", "horror disco", "hyperpop",
    "infantil", "k pop", "latin", "latin jazz", "latin rock", "mathcore",
    "metalpunk", "musique concrete", "neo crust", "new age", "new wave",
    "no wave", "nu jazz", "nu metal", "oi", "old school", "orchestral",
    "otros", "poky", "power pop", "proto punk", "r and b", "raw punk",
    "ritual ambient", "rock and roll", "rock urbano", "sampling", "screamo",
    "singer songwriter", "sound system", "street punk", "swamp rock",
    "synthcore", "uk 82", "uk garage", "video game music", "77 punk",
    "alboka", "bertso", "bertsolaritza", "euskal folk", "trikitixa",
    "txalaparta", "txistu", "sound art", "power electronics", "rocksteady",
    "raggamuffin", "devotional", "abstract", "berlin school", "folktronica",
    "ethereal", "tribal", "urban rock", "classic rock",
    "hardcore techno", "electronic rock", "instrumental rock", "melodic rock",
    "space rock", "gypsy jazz", "boogie woogie", "minimal synth", "dance punk",
}

# Nodo curado "euskal folk": música de raíz vasca (instrumentos y formas propias).
EUSKAL_FOLK_SYNONYMS = {
    "basque folk", "euskal folk", "folk vasco", "folk basque", "herri musika",
    "musika herrikoia", "euskal musika tradizionala", "musica tradicional vasca",
    "basque traditional music", "trikitixa", "triki", "trikitilari", "txalaparta",
    "alboka", "txistu", "bertso", "bertsoak", "bertsolaritza", "bertsolari",
    "euskal kantagintza", "kantagintza berria", "euskal kantutegia", "euskal folk rock",
    "basque folk rock", "folk rock vasco", "euskal kantautorea",
}
for _s in EUSKAL_FOLK_SYNONYMS:
    FULL_SYNONYMS[_s] = "euskal folk"

# Padres fijados a mano (nodo -> padre) para la jerarquía exportada. Solo se
# usa cuando la regla de sufijo no encuentra nada razonable.
PARENT_OVERRIDES: dict[str, str] = {
    "euskal folk": "folk",
    "oi": "punk",
    "d beat": "hardcore punk",
    "crust": "hardcore punk",
    "neo crust": "crust",
    "grindcore": "hardcore",
    "goregrind": "grindcore",
    "powerviolence": "hardcore punk",
    "fastcore": "hardcore punk",
    "screamo": "emo",
    "emo": "post hardcore",
    "deathcore": "metalcore",
    "djent": "progressive metal",
    "slam": "brutal death metal",
    "black death": "death metal",
    "metalpunk": "metal",
    "uk 82": "punk",
    "77 punk": "punk",
    "street punk": "punk",
    "anarcho punk": "punk",
    "raw punk": "punk",
    "proto punk": "punk",
    "high energy rock": "rock and roll",
    "rock and roll": "rock",
    "rockabilly": "rock and roll",
    "psychobilly": "rockabilly",
    "americana": "country",
    "bluegrass": "country",
    "bebop": "jazz",
    "opera": "classical",
    "bolero": "latin",
    "merengue": "latin",
    "bachata": "latin",
    "cabaret": "chanson",
    "riot grrrl": "punk",
    "alternative country": "country",
    "swamp rock": "rock",
    "krautrock": "rock",
    "no wave": "post punk",
    "new wave": "post punk",
    "darkwave": "post punk",
    "coldwave": "post punk",
    "deathrock": "post punk",
    "gothic rock": "post punk",
    "synthpop": "pop",
    "hyperpop": "pop",
    "k pop": "pop",
    "dream pop": "indie pop",
    "shoegaze": "indie rock",
    "slowcore": "indie rock",
    "britpop": "indie rock",
    "freakbeat": "garage rock",
    "mod": "garage rock",
    "surf rock": "rock and roll",
    "grunge": "alternative rock",
    "emo": "post hardcore",
    "screamo": "emo",
    "idm": "electronic",
    "glitch": "idm",
    "ambient": "electronic",
    "dark ambient": "ambient",
    "drone": "ambient",
    "dungeon synth": "dark ambient",
    "new age": "ambient",
    "downtempo": "electronic",
    "trip hop": "downtempo",
    "chillout": "downtempo",
    "chillwave": "downtempo",
    "lounge": "downtempo",
    "balearic": "downtempo",
    "vaporwave": "electronic",
    "synthwave": "electronic",
    "electro": "electronic",
    "ebm": "industrial",
    "techno": "electronic",
    "house": "electronic",
    "trance": "electronic",
    "dance": "electronic",
    "rave": "electronic",
    "poky": "dance",
    "hardtek": "hardcore techno",
    "hardcore techno": "techno",
    "breakbeat": "electronic",
    "breakcore": "breakbeat",
    "jungle": "breakbeat",
    "drum and bass": "breakbeat",
    "dubstep": "bass music",
    "uk garage": "bass music",
    "grime": "bass music",
    "footwork": "bass music",
    "bass music": "electronic",
    "acid": "techno",
    "minimal": "techno",
    "beats": "hip hop",
    "boom bap": "hip hop",
    "trap": "hip hop",
    "drill": "trap",
    "rap": "hip hop",
    "abstract hip hop": "hip hop",
    "abstract": "experimental",
    "devotional": "new age",
    "ethereal": "dream pop",
    "tribal": "world music",
    "folktronica": "electronic",
    "classic rock": "rock",
    "deep house": "house",
    "rocksteady": "reggae",
    "raggamuffin": "dancehall",
    "power electronics": "noise",
    "turntablism": "hip hop",
    "g funk": "hip hop",
    "sampling": "hip hop",
    "dub": "reggae",
    "steppa": "dub",
    "dancehall": "reggae",
    "raggamuffin": "dancehall",
    "rocksteady": "reggae",
    "ska": "reggae",
    "sound system": "dub",
    "reggaeton": "latin",
    "cumbia": "latin",
    "salsa": "latin",
    "rumba": "flamenco",
    "flamenco": "world music",
    "tango": "latin",
    "samba": "mpb",
    "bossa nova": "mpb",
    "mpb": "latin",
    "guaracha": "latin",
    "afro": "world music",
    "afrobeat": "afro",
    "celtic": "folk",
    "balkan": "world music",
    "medieval": "folk",
    "chanson": "folk",
    "singer songwriter": "folk",
    "acoustic": "folk",
    "spoken word": "experimental",
    "sound art": "experimental",
    "field recording": "experimental",
    "musique concrete": "experimental",
    "electroacoustic": "experimental",
    "free improvisation": "experimental",
    "free jazz": "jazz",
    "nu jazz": "jazz",
    "swing": "jazz",
    "gypsy jazz": "jazz",
    "noise": "experimental",
    "harsh noise": "noise",
    "power electronics": "noise",
    "industrial": "experimental",
    "classical": "classical",
    "neoclassical": "classical",
    "contemporary classical": "classical",
    "orchestral": "classical",
    "symphonic": "classical",
    "choral": "classical",
    "soundtrack": "instrumental",
    "video game music": "soundtrack",
    "chiptune": "electronic",
    "world music": "folk",
    "latin": "world music",
    "instrumental": "instrumental",
    "r and b": "soul",
    "funk": "soul",
    "disco": "dance",
    "italo disco": "disco",
    "horror disco": "disco",
    "old school": "hip hop",
    "berlin school": "ambient",
    "a cappella": "choral",
    "comedy": "otros",
    "horror": "otros",
    "infantil": "otros",
    "urban": "hip hop",
    "lo fi": "indie rock",
    "hardcore": "punk",
    "hardcore punk": "hardcore",
    "post hardcore": "hardcore",
    "melodic hardcore": "hardcore",
    "beatdown": "hardcore",
    "metalcore": "hardcore",
    "mathcore": "metalcore",
    "synthcore": "post hardcore",
    "reverbcore": "shoegaze",
    "dreampunk": "vaporwave",
    "internetcore": "hyperpop",
    "digicore": "hyperpop",
    "postvore": "hyperpop",
    "queercore": "punk",
    "riot grrrl": "punk",
    "horrorcore": "hip hop",
    "anarcho folk": "folk punk",
    "folk punk": "punk",
    "dark folk": "folk",
    "freak folk": "folk",
    "electro dub": "dub",
    "dj": "electronic",
    "atmospheric": "ambient",
    "avant garde": "experimental",
    "urban rock": "rock",
    "punk": "rock",
    "metal": "rock",
    "pop": "pop",
    "rock": "rock",
    "electronic": "electronic",
    "jazz": "jazz",
    "folk": "folk",
    "reggae": "reggae",
    "hip hop": "hip hop",
    "experimental": "experimental",
    "soul": "soul",
    "blues": "blues",
    "country": "folk",
}

# ---------------------------------------------------------------------------
# Grupo OTRO: subtipos por nodo (para colgar los pequeños del subtipo).
# ---------------------------------------------------------------------------
OTRO_SUBTYPES: dict[str, str] = {
    "en directo": "formato", "demo": "formato", "cassette": "formato",
    "vinilo": "formato", "cd": "formato", "ep": "formato", "single": "formato",
    "split": "formato", "recopilatorio": "formato", "album": "formato",
    "digital": "formato", "remix": "formato", "versiones": "formato",
    "reedicion": "formato",
    "euskaraz": "idioma", "castellano": "idioma", "english": "idioma",
    "francais": "idioma", "catala": "idioma", "galego": "idioma",
    "italiano": "idioma", "portugues": "idioma", "occitan": "idioma",
    "piano": "instrumento", "guitarra": "instrumento", "cello": "instrumento",
    "violin": "instrumento", "cuerdas": "instrumento", "arpa": "instrumento",
    "bateria": "instrumento", "percusion": "instrumento", "teclados": "instrumento",
    "vientos": "instrumento", "acordeon": "instrumento", "zanfona": "instrumento",
    "maquinas": "instrumento", "voz": "instrumento",
    "diy": "escena", "underground": "escena", "independiente": "escena",
    "copyleft": "escena", "antifa": "escena", "politica": "escena",
    "queer": "escena", "feminismo": "escena", "vegan": "escena",
    "straight edge": "escena",
}
OTRO_SUBTYPE_LABEL = {"formato": "formato", "idioma": "idioma", "instrumento": "instrumento",
                      "escena": "escena", "epoca": "época"}

_YEAR = re.compile(r"^(19|20)\d\d$")
_DECADE = re.compile(r"^(19|20)?(\d0)s?$")   # 80s, 1980s, 80 (tras quitar ')


def classify_epoca(norm: str) -> str | None:
    """'1994' -> 'otro:año' ; '80s'/'1980s' -> 'otro:decada 80'."""
    if _YEAR.match(norm):
        return OTRO_PREFIX + "año"
    m = _DECADE.match(norm)
    if m and len(norm) >= 3:
        return OTRO_PREFIX + "decada " + m.group(2)
    return None


# ---------------------------------------------------------------------------
# Lugares: gaceteer de data/locations + lugares externos.
# ---------------------------------------------------------------------------
# Alias del gaceteer demasiado genéricos para fiarse de ellos como tag.
GAZETTEER_BLACKLIST = {"barrio", "maya", "belako", "san miguel", "sabino arana", "ali",
                       "castillo", "margarita", "mendoza", "jugo", "zarate", "arriaga",
                       "bolibar", "san gregorio", "itziar"}

FOREIGN_PLACES = {
    # nodo -> alias (todo normalizado por compact)
    "spain": ["spain", "españa", "espana", "espainia", "estado español"],
    "france": ["france", "francia", "frantzia"],
    "madrid": ["madrid"],
    "barcelona": ["barcelona"],
    "catalunya": ["catalunya", "cataluña", "catalonia"],
    "galicia": ["galicia", "galiza"],
    "asturias": ["asturias", "asturies", "oviedo", "gijon"],
    "cantabria": ["cantabria", "santander"],
    "burgos": ["burgos"],
    "logroño": ["logroño", "logrono", "la rioja"],
    "andalucia": ["andalucia", "andalucía"],
    "united kingdom": ["united kingdom", "england", "scotland", "london", "manchester", "bristol", "glasgow"],
    "united states": ["united states", "usa", "america", "california", "chicago"],
    "germany": ["germany", "alemania", "deutschland"],
    "italy": ["italy", "italia"],
    "portugal": ["portugal", "lisboa", "porto"],
    "belgium": ["belgium", "belgica"],
    "netherlands": ["netherlands", "holland", "amsterdam"],
    "sweden": ["sweden", "suecia"],
    "norway": ["norway", "noruega"],
    "argentina": ["argentina"],
    "chile": ["chile"],
    "colombia": ["colombia"],
    "cuba": ["cuba"],
    "mexico": ["mexico", "méxico"],
    "brasil": ["brasil", "brazil"],
    "uruguay": ["uruguay"],
    "jamaica": ["jamaica"],
    "japan": ["japan", "japon"],
    "hong kong": ["hong kong"],
    "thailand": ["thailand"],
    "afghanistan": ["afghanistan"],
    "africa": ["africa"],
    "antigua y barbuda": ["antigua y barbuda"],
}
# Lugares pequeños sin territorio grande cuelgan de este nodo.
OTROS_LUGARES_NAME = "otros lugares"
OTROS_LUGARES = LUGAR_PREFIX + OTROS_LUGARES_NAME


def load_gazetteer() -> tuple[dict[str, str], dict[str, str]]:
    """Devuelve (clave compacta -> nombre de lugar, nombre -> nombre del padre).

    El nombre de lugar es el `name` del gaceteer en minúsculas (vasco primero:
    bilbo, iruñea, donostia, gasteiz). Los padres son territorio o comarca.
    """
    key_to_name: dict[str, str] = {}
    parents: dict[str, str] = {}
    rules = json.loads(RULES_JSON.read_text(encoding="utf-8"))
    for rid, reg in sorted(rules["regions"].items()):
        name = reg["name"].lower()
        aliases = [reg["name"], rid] + list(reg.get("aliases", []))
        for a in aliases:
            key_to_name.setdefault(compact(a), name)
        level = reg.get("level")
        if level in ("territory", "comarca") and reg.get("territory"):
            parent = reg["territory"].lower()
            parents[name] = parent if parent != name else "euskal herria"
        elif level == "region" and rid == "iparralde":
            parents[name] = "euskal herria"
        elif level == "region":
            parents[name] = "france"
        elif level == "state":
            parents[name] = OTROS_LUGARES_NAME
        else:
            parents[name] = "euskal herria"
    parents["euskal herria"] = OTROS_LUGARES_NAME
    places = json.loads(PLACES_JSON.read_text(encoding="utf-8"))["places"]
    for p in sorted(places, key=lambda x: x["id"]):
        name = p["name"].lower()
        aliases = [p["name"], p["id"]] + list(p.get("aliases", [])) + list(p.get("names", {}).values())
        for a in aliases:
            k = compact(a)
            if len(k) < 4 or normalize(a) in GAZETTEER_BLACKLIST:
                continue
            key_to_name.setdefault(k, name)
        parents[name] = (p.get("territory") or "euskal herria").lower()
    for name, aliases in sorted(FOREIGN_PLACES.items()):
        for a in aliases:
            key_to_name.setdefault(compact(a), name)
        parents.setdefault(name, OTROS_LUGARES_NAME)
    parents[OTROS_LUGARES_NAME] = OTROS_LUGARES_NAME
    return key_to_name, parents


# ---------------------------------------------------------------------------
# Resolución de un tag a su concepto (forma normalizada canónica).
# ---------------------------------------------------------------------------
def translate_words(norm: str) -> str:
    words = [WORD_SYNONYMS.get(w, w) for w in norm.split()]
    return _SPACES.sub(" ", " ".join(w for w in words if w)).strip()


def apply_synonyms(norm: str) -> str:
    """Sinónimos de cadena -> traducción por palabra -> sinónimos otra vez."""
    seen = set()
    cur = norm
    for _ in range(6):
        if cur in seen:
            break
        seen.add(cur)
        nxt = FULL_SYNONYMS.get(cur, cur)
        if nxt.startswith((OTRO_PREFIX, LUGAR_PREFIX)) or nxt == RESTO:
            return nxt
        nxt = translate_words(nxt)
        nxt = FULL_SYNONYMS.get(nxt, nxt)
        if nxt == cur:
            break
        cur = nxt
    return cur


_SYNONYM_TARGETS = {v for v in FULL_SYNONYMS.values()
                    if not v.startswith((OTRO_PREFIX, LUGAR_PREFIX)) and v != RESTO}


def glued_root(word: str) -> str | None:
    """'crustcore' -> 'core'; 'petruska' -> None (ska no está en GLUED_SUFFIXES)."""
    for root in sorted(GLUED_SUFFIXES, key=lambda r: (-len(r), r)):
        if word.endswith(root) and len(word) >= len(root) + 3:
            return root
    return None


def is_known_genre(norm: str) -> bool:
    """Término curado o compuesto solo de raíces conocidas: nunca se trata como errata."""
    if norm in GENRE_TERMS or norm in _SYNONYM_TARGETS:
        return True
    words = norm.split()
    return bool(words) and all(w in GENRE_ROOTS or w in _SYNONYM_TARGETS for w in words)


def is_genre(norm: str) -> bool:
    if norm in GENRE_TERMS or norm in _SYNONYM_TARGETS:
        return True
    for w in norm.split():
        if w in GENRE_ROOTS or glued_root(w):
            return True
    return False


PLACE_PHRASES = (("basque country", "basque"), ("euskal herria", "basque"),
                 ("pais vasco", "basque"), ("euskal herri", "basque"))


def strip_place_words(norm: str, gaz: dict[str, str] | None = None) -> tuple[str, bool, str | None]:
    """'punk vasco' -> ('punk', True, None). No toca términos conocidos ('berlin school').

    Devuelve (resto, cambiado, lugar): si al quitar lugares/gentilicios no queda
    nada, `lugar` es el nombre del primer lugar del gaceteer que apareció
    ("barakaldo basque country" -> lugar barakaldo).
    """
    if norm in GENRE_TERMS or norm in _SYNONYM_TARGETS:
        return norm, False, None
    for phrase, repl in PLACE_PHRASES:
        norm = norm.replace(phrase, repl)
    words = norm.split()
    kept, place = [], None
    for w in words:
        if w in DEMONYM_WORDS:
            continue
        if gaz and len(w) >= 4 and compact(w) in gaz:
            place = place or gaz[compact(w)]
            continue
        kept.append(w)
    if len(kept) == len(words):
        return norm, False, None
    return " ".join(kept), True, place


def edit_distance(a: str, b: str) -> int:
    if abs(len(a) - len(b)) > 2:
        return 3
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


# ---------------------------------------------------------------------------
# Construcción del mapa
# ---------------------------------------------------------------------------
class Concept:
    __slots__ = ("norm", "key", "grupo", "tags", "discos", "node", "flags", "subtype")

    def __init__(self, norm: str, key: str, grupo: str):
        self.norm = norm
        self.key = key
        self.grupo = grupo          # genero | lugar | otro | resto
        self.tags: list[str] = []
        self.discos: set[int] = set()
        self.node: str | None = None
        self.flags: list[str] = []
        self.subtype: str | None = None


def resolve_tag(tag: str, gaz: dict[str, str]) -> tuple[str, str, list[str]]:
    """Devuelve (grupo, forma canónica normalizada, avisos)."""
    norm = normalize(tag)
    flags: list[str] = []
    if not norm:
        return RESTO, RESTO, flags
    ep = classify_epoca(norm)
    if ep:
        return "otro", ep[len(OTRO_PREFIX):], flags
    if compact(norm) in gaz:
        return "lugar", gaz[compact(norm)], flags
    cur = apply_synonyms(norm)
    if cur == RESTO:
        return RESTO, RESTO, flags
    if cur.startswith(OTRO_PREFIX):
        return "otro", cur[len(OTRO_PREFIX):], flags
    if cur.startswith(LUGAR_PREFIX):
        return "lugar", cur[len(LUGAR_PREFIX):], flags
    if compact(cur) in gaz:
        return "lugar", gaz[compact(cur)], flags
    stripped, changed, place = strip_place_words(cur, gaz)
    if changed and not stripped:
        return ("lugar", place, flags) if place else (RESTO, RESTO, flags)
    if changed:
        stripped = apply_synonyms(stripped)
        if stripped.startswith(OTRO_PREFIX):
            return "otro", stripped[len(OTRO_PREFIX):], flags + ["lugar-quitado"]
        if stripped.startswith(LUGAR_PREFIX):
            return "lugar", stripped[len(LUGAR_PREFIX):], flags
        if stripped == RESTO:
            return RESTO, RESTO, flags
        flags.append("lugar-quitado")
        cur = stripped
    if cur in DOUBTFUL_SYNONYMS or norm in DOUBTFUL_SYNONYMS:
        flags.append("sinonimo-dudoso")
    if is_genre(cur):
        return "genero", cur, flags
    return RESTO, RESTO, flags


def pick_label(concept: Concept, tag_counts: Counter) -> str:
    """Etiqueta visible: la forma original más frecuente entre los tags cuya
    normalización coincide con la forma canónica; si no hay, la canónica."""
    direct = [t for t in concept.tags if normalize(t) == concept.norm]
    pool = direct or concept.tags
    best = sorted(pool, key=lambda t: (-tag_counts[t], t))[0]
    if normalize(best) != concept.norm:
        return concept.norm
    return best.lower()


def find_parent(norm: str, big: dict[str, Concept], self_key: str | None = None):
    """Padre por sufijo de palabras > subsecuencia contigua > palabra > raíz pegada.

    Devuelve (padre_norm | None, candidatos_alternativos, flags).
    """
    words = norm.split()
    flags: list[str] = []
    candidates: list[str] = []
    chosen = None
    n = len(words)
    # sufijos (longest first), excluyendo el tag entero
    for i in range(1, n):
        cand = apply_synonyms(" ".join(words[i:]))
        if cand in big and compact(cand) != self_key:
            chosen = cand
            break
    # subsecuencias contiguas de longitud n-1..1 (prefijos e interiores)
    if chosen is None:
        for L in range(n - 1, 0, -1):
            for i in range(0, n - L + 1):
                cand = apply_synonyms(" ".join(words[i:i + L]))
                if cand in big and compact(cand) != self_key:
                    chosen = cand
                    break
            if chosen:
                break
    # raíz pegada: "crustcore" -> crust / core ; "blackgaze" -> black metal?
    if chosen is None and n == 1:
        w = words[0]
        root = glued_root(w)
        if root:
            prefix_c = apply_synonyms(w[: -len(root)])
            root_c = apply_synonyms(root)
            for cand in (root_c, prefix_c):
                if cand in big and compact(cand) != self_key:
                    chosen = cand
                    break
            if chosen:
                flags.append("raiz-pegada")
                if prefix_c in big and root_c in big:
                    flags.append("varios-padres")
    # candidatos alternativos: cualquier palabra suelta que sea nodo grande
    for w in words:
        wc = apply_synonyms(w)
        if wc in big and wc != chosen and compact(wc) != self_key and wc not in candidates:
            candidates.append(wc)
    if chosen and candidates:
        flags.append("varios-padres")
    if chosen and words[0] in MODIFIER_PREFIXES and n > 1:
        flags.append("prefijo-modificador")
    return chosen, candidates, flags


def build(catalog: dict) -> dict:
    albums = catalog["albums"]
    tag_counts: Counter = Counter()
    tag_albums: dict[str, set[int]] = defaultdict(set)
    for a in albums:
        for t in a.get("tags") or []:
            tag_counts[t] += 1
            tag_albums[t].add(a["id"])
    gaz, place_parents = load_gazetteer()

    # 1-6: tag -> concepto
    concepts: dict[tuple[str, str], Concept] = {}
    tag_flags: dict[str, list[str]] = {}
    canon_votes: dict[tuple[str, str], Counter] = defaultdict(Counter)
    for tag in sorted(tag_counts):
        grupo, canon, flags = resolve_tag(tag, gaz)
        key = (grupo, compact(canon) if grupo != RESTO else RESTO)
        c = concepts.get(key)
        if c is None:
            c = concepts[key] = Concept(canon, key[1], grupo)
        c.tags.append(tag)
        c.discos |= tag_albums[tag]
        canon_votes[key][canon] += tag_counts[tag]
        tag_flags[tag] = flags
    # la forma canónica del concepto es la más votada (por discos) entre las
    # formas que comparten clave compacta: "hardcore punk" gana a "hard core punk"
    for key, c in concepts.items():
        c.norm = sorted(canon_votes[key].items(), key=lambda kv: (-kv[1], kv[0]))[0][0]

    genres = {k: c for k, c in concepts.items() if c.grupo == "genero"}

    # 7: erratas -> nodo grande (solo género)
    big_keys = {c.key: c for c in genres.values() if len(c.discos) >= FUZZY_MIN_TARGET_DISCOS}
    fuzzy_merges: list[tuple[Concept, Concept]] = []
    for key in sorted(genres):
        c = genres[key]
        if len(c.discos) >= FUZZY_MAX_DISCOS or c.key in big_keys or len(c.key) < 6:
            continue
        if is_known_genre(c.norm):
            continue   # "funk rock" está a 1 letra de "punk rock" pero no es errata
        maxd = 2 if len(c.key) >= 10 else 1
        best = None
        for bk in sorted(big_keys):
            d = edit_distance(c.key, bk)
            if d <= maxd and c.key[0] == bk[0]:
                cand = big_keys[bk]
                if best is None or (-(len(cand.discos)), cand.key) < (-(len(best.discos)), best.key):
                    best = cand
        if best is not None:
            fuzzy_merges.append((c, best))
    for c, target in fuzzy_merges:
        target.tags.extend(c.tags)
        target.discos |= c.discos
        for t in c.tags:
            tag_flags[t].append(f"errata->{target.norm}")
        del concepts[("genero", c.key)]
    genres = {k: c for k, c in concepts.items() if c.grupo == "genero"}

    # 8: umbral y padres (género)
    big = {c.norm: c for c in genres.values() if len(c.discos) >= MIN_DISCOS}
    labels: dict[str, str] = {c.norm: pick_label(c, tag_counts) for c in big.values()}
    labels[OTROS_GENEROS] = OTROS_GENEROS
    parent_of: dict[str, str | None] = {}
    dudosas: list[dict] = []
    for norm in sorted(big):
        c = big[norm]
        override = PARENT_OVERRIDES.get(norm)
        if override and override in big and override != norm:
            parent = override
        else:
            parent, _cands, _fl = find_parent(norm, big, c.key)
            if override and override in big:
                parent = override
        parent_of[norm] = parent if parent != norm else None
        c.node = labels[norm]
    for norm in sorted(genres.keys(), key=lambda k: genres[k].norm):
        c = genres[norm]
        if c.norm in big:
            continue
        parent, cands, fl = find_parent(c.norm, big, c.key)
        override = PARENT_OVERRIDES.get(c.norm)
        if override and override in big:
            # el padre curado manda, pero se sigue avisando si otra palabra
            # del tag también era nodo ("hardcore techno" -> techno, y hardcore)
            cands = [x for x in cands + ([parent] if parent and parent != override else []) if x != override]
            parent = override
            fl = [f for f in fl if f != "varios-padres"] + (["varios-padres"] if cands else [])
        if parent is None:
            c.node = OTROS_GENEROS
            c.flags.append("sin-padre")
        else:
            c.node = labels[parent]
            c.flags.extend(fl)
            if cands:
                c.flags.append("alternativas:" + "|".join(labels[x] for x in cands))

    # lugares: nodo propio si >= MIN_DISCOS; si no, sube por la cadena
    # municipio -> territorio -> euskal herria -> otros lugares hasta un nodo grande
    places = {k: c for k, c in concepts.items() if c.grupo == "lugar"}
    big_places = {c.norm for c in places.values() if len(c.discos) >= MIN_DISCOS}
    for key in sorted(places):
        c = places[key]
        name = c.norm
        if name in big_places:
            c.node = LUGAR_PREFIX + name
            continue
        parent = place_parents.get(name, OTROS_LUGARES_NAME)
        hops = 0
        while parent not in big_places and parent != OTROS_LUGARES_NAME and hops < 6:
            parent = place_parents.get(parent, OTROS_LUGARES_NAME)
            hops += 1
        if parent not in big_places:
            parent = OTROS_LUGARES_NAME
        c.node = LUGAR_PREFIX + parent
        c.flags.append("lugar-pequeño")

    # otro: nodo propio si >= MIN_DISCOS, si no cuelga del subtipo
    otros = {k: c for k, c in concepts.items() if c.grupo == "otro"}
    for key in sorted(otros):
        c = otros[key]
        if c.norm == "año" or c.norm.startswith("decada "):
            sub = "epoca"
        else:
            sub = OTRO_SUBTYPES.get(c.norm, "escena")
        c.subtype = sub
        if len(c.discos) >= MIN_DISCOS:
            c.node = OTRO_PREFIX + c.norm
        else:
            c.node = OTRO_PREFIX + OTRO_SUBTYPE_LABEL[sub]
            c.flags.append("otro-pequeño")
    for key, c in concepts.items():
        if c.grupo == RESTO:
            c.node = RESTO

    # ---- salida ----
    tag_map: dict[str, str] = {}
    node_tags: dict[str, list[str]] = defaultdict(list)
    node_albums: dict[str, set[int]] = defaultdict(set)
    node_grupo: dict[str, str] = {}
    node_subtype: dict[str, str | None] = {}
    for key in sorted(concepts):
        c = concepts[key]
        assert c.node is not None, key
        for t in c.tags:
            tag_map[t] = c.node
            node_tags[c.node].append(t)
            node_albums[c.node] |= tag_albums[t]
        node_grupo[c.node] = c.grupo
        node_subtype[c.node] = c.subtype
    node_grupo[RESTO] = RESTO
    node_grupo[OTROS_GENEROS] = "genero"
    node_grupo.setdefault(OTROS_LUGARES, "lugar")
    for sub in OTRO_SUBTYPE_LABEL.values():
        node_grupo.setdefault(OTRO_PREFIX + sub, "otro")

    label_to_norm = {v: k for k, v in labels.items()}
    nodos = []
    for node in sorted(node_tags, key=lambda n: (-len(node_albums[n]), n)):
        grupo = node_grupo[node]
        padre = None
        if grupo == "genero" and node in label_to_norm:
            p = parent_of.get(label_to_norm[node])
            padre = labels[p] if p else None
        elif grupo == "lugar":
            name = node[len(LUGAR_PREFIX):]
            p = place_parents.get(name)
            if p and p not in (name, OTROS_LUGARES_NAME) and (LUGAR_PREFIX + p) in node_tags:
                padre = LUGAR_PREFIX + p
        elif grupo == "otro":
            sub = node_subtype.get(node)
            if sub and node != OTRO_PREFIX + OTRO_SUBTYPE_LABEL[sub]:
                padre = OTRO_PREFIX + OTRO_SUBTYPE_LABEL[sub]
        nodos.append({
            "id": node,
            "grupo": grupo,
            "padre": padre,
            "discos": len(node_albums[node]),
            "n_tags": len(node_tags[node]),
            "tags": sorted(node_tags[node], key=lambda t: (-tag_counts[t], t)),
        })

    # dudosas
    for key in sorted(concepts):
        c = concepts[key]
        for t in sorted(c.tags, key=lambda t: (-tag_counts[t], t)):
            fl = list(tag_flags.get(t, [])) + [f for f in c.flags if f not in ("otro-pequeño", "lugar-pequeño", "sin-padre")]
            fl = sorted(set(fl))
            if not fl:
                continue
            motivo = []
            for f in fl:
                if f.startswith("errata->"):
                    motivo.append("posible errata fusionada con '" + f[8:] + "'")
                elif f == "varios-padres":
                    motivo.append("más de una palabra era nodo")
                elif f.startswith("alternativas:"):
                    motivo.append("alternativas: " + f[len("alternativas:"):].replace("|", ", "))
                elif f == "prefijo-modificador":
                    motivo.append("prefijo que cambia el sentido (post-, anti-, neo-...)")
                elif f == "lugar-quitado":
                    motivo.append("se ha quitado la parte de lugar/gentilicio")
                elif f == "raiz-pegada":
                    motivo.append("raíz pegada separada")
                elif f == "sinonimo-dudoso":
                    motivo.append(DOUBTFUL_SYNONYMS.get(normalize(t)) or DOUBTFUL_SYNONYMS.get(c.norm) or "sinónimo discutible")
            dudosas.append({"tag": t, "discos": tag_counts[t], "nodo": c.node, "motivo": "; ".join(motivo)})
    dudosas.sort(key=lambda d: (-d["discos"], d["tag"]))

    n_navegables = sum(1 for n in nodos if n["id"] != RESTO)
    meta = {
        "fuente": "data/bandcamp_bilbaotags_clean.json",
        "generado_por": "scripts/tag_merge_map.py",
        "n_discos": len(albums),
        "n_tags": len(tag_counts),
        "n_nodos": n_navegables,
        "n_nodos_por_grupo": dict(sorted(Counter(n["grupo"] for n in nodos if n["id"] != RESTO).items())),
        "umbral_min_discos": MIN_DISCOS,
        "tags_en_resto": len(node_tags[RESTO]),
        "discos_solo_con_tags_resto": sum(
            1 for a in albums if (a.get("tags") or []) and all(tag_map[t] == RESTO for t in a["tags"])),
    }
    return {"_meta": meta, "map": tag_map, "nodos": nodos, "dudosas": dudosas}


# ---------------------------------------------------------------------------
# Informe
# ---------------------------------------------------------------------------
def render_report(result: dict) -> str:
    m = result["_meta"]
    nodos = result["nodos"]
    out = []
    out.append("# Mapa de fusión de tags — informe\n")
    out.append("Generado por `scripts/tag_merge_map.py` a partir de `data/bandcamp_bilbaotags_clean.json`. "
               "El mapa completo está en `data/derived/tag_merge_map.json`; el método, en `docs/tag-merge-map.md`.\n")
    out.append("## Resumen\n")
    out.append("| | |\n|---|---|")
    out.append(f"| Discos | {m['n_discos']} |")
    out.append(f"| Tags distintos (antes) | {m['n_tags']} |")
    out.append(f"| Nodos navegables (después) | {m['n_nodos']} |")
    for g, n in m["n_nodos_por_grupo"].items():
        out.append(f"| &nbsp;&nbsp;· {g} | {n} |")
    out.append(f"| Umbral de microgénero (MIN_DISCOS) | {m['umbral_min_discos']} |")
    out.append(f"| Tags en `resto` (sin nodo navegable) | {m['tags_en_resto']} |")
    out.append(f"| Discos cuyos tags caen todos en `resto` | {m['discos_solo_con_tags_resto']} |")
    out.append("")
    out.append("Grupos: `genero` (sin prefijo), `lugar:*` (aparte, nunca se funde con géneros), "
               "`otro:*` (formato, idioma, instrumento, escena, época) y `resto` (nombres de grupo, "
               "sellos, palabras sueltas: se conservan en el mapa pero no son nodo).\n")

    out.append(f"## Los {TOP_NODES_IN_REPORT} nodos más grandes\n")
    out.append("| # | Nodo | Grupo | Padre | Discos | Tags fusionados | Ejemplos de tags |\n|---|---|---|---|---|---|---|")
    top = [n for n in nodos if n["id"] != RESTO][:TOP_NODES_IN_REPORT]
    for i, n in enumerate(top, 1):
        ejemplos = ", ".join(n["tags"][:6]) + (" …" if len(n["tags"]) > 6 else "")
        out.append(f"| {i} | {n['id']} | {n['grupo']} | {n['padre'] or ''} | {n['discos']} | {n['n_tags']} | {ejemplos} |")
    out.append("")

    out.append("## Nodos por grupo\n")
    for grupo in ("genero", "lugar", "otro"):
        ns = [n for n in nodos if n["grupo"] == grupo]
        out.append(f"### {grupo} ({len(ns)} nodos)\n")
        out.append(", ".join(f"{n['id']} ({n['discos']})" for n in ns))
        out.append("")

    resto = next((n for n in nodos if n["id"] == RESTO), None)
    if resto:
        out.append("## Lo que cae en `resto`\n")
        out.append(f"{resto['n_tags']} tags, {resto['discos']} discos con al menos uno. Los 40 más frecuentes "
                   "(si alguno es un género, añadirlo a GENRE_TERMS o FULL_SYNONYMS):\n")
        out.append(", ".join(resto["tags"][:40]))
        out.append("")

    dud = result["dudosas"]
    shown = [d for d in dud if d["discos"] >= 2]
    out.append("## Fusiones dudosas (para revisar)\n")
    out.append(f"Casos donde la regla podría estar uniendo cosas distintas: {len(dud)} tags marcados. "
               f"Aquí los {len(shown)} con al menos 2 discos, ordenados por nº de discos; la lista completa "
               "(incluidos los de 1 disco) está en el campo `dudosas` del JSON.\n")
    out.append("| Tag | Discos | → Nodo | Motivo |\n|---|---|---|---|")
    for d in shown:
        out.append(f"| {d['tag']} | {d['discos']} | {d['nodo']} | {d['motivo']} |")
    out.append("")
    return "\n".join(out) + "\n"


def main() -> None:
    catalog = json.loads(CANONICAL.read_text(encoding="utf-8"))
    result = build(catalog)
    DERIVED_DIR.mkdir(parents=True, exist_ok=True)
    MAP_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=1, sort_keys=False) + "\n", encoding="utf-8")
    REPORT_MD.write_text(render_report(result), encoding="utf-8")
    m = result["_meta"]
    print(f"tags {m['n_tags']} -> nodos {m['n_nodos']} {m['n_nodos_por_grupo']} "
          f"(resto: {m['tags_en_resto']} tags) -> {MAP_JSON.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
