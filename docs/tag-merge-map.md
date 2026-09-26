# Mapa de fusión de tags — método

**Qué es:** un mapa determinista `tag original → nodo canónico` que reduce los
~5.575 tags de Bandcamp del catálogo a ~450 nodos navegables sin perder ningún
tag. Punto de partida: el diagnóstico de julio de 2026 (rama
`claude/meu-tags-diagnostic-lv6x9t`), que clasificó los tags en
género / territorial / otro / ambiguo y concluyó que el cuello de botella era la
limpieza, no la riqueza.

**Ficheros:**

- `scripts/tag_merge_map.py` — reglas (todo en un fichero, stdlib, sin red).
- `data/derived/tag_merge_map.json` — `{"map": {tag: nodo}, "nodos": [...], "dudosas": [...]}`.
- `data/derived/tag_merge_report.md` — cifras, top 50, nodos por grupo, fusiones dudosas.
- `tests/test_tag_merge_map.py` — normalización, sinónimos, clasificación, determinismo y
  que el JSON versionado esté al día.

Regenerar: `python3 scripts/tag_merge_map.py`. Solo LEE el canónico
`data/bandcamp_bilbaotags_clean.json`; no toca `app/`.

## Cadena de reglas (en este orden)

1. **Normalización.** NFKD sin diacríticos, minúsculas, `&` y `'n'` → `and`,
   separadores (`- _ / ; , . :`) → espacio, sin puntuación, espacios colapsados.
   La **clave compacta** (sin espacios) agrupa variantes: `post-punk`,
   `postpunk` y `Post Punk` son el mismo concepto. La etiqueta visible del nodo
   es la forma original más frecuente (`post-punk`, `rock & roll`, `oi!`).
2. **Sinónimos de cadena completa** (`FULL_SYNONYMS`, ~1.200 entradas): umbrellas de
   Bandcamp (`hip-hop/rap` → hip hop), abreviaturas (`dnb`, `hxc`), equivalencias
   editoriales (`crust punk` → crust, `bumping` → poky), y todo lo que va a
   `otro:*` o `lugar:*` por decisión explícita.
3. **Sinónimos por palabra** (`WORD_SYNONYMS`): traducción es/eu/en (`rocka` →
   rock, `psicodelia` → psychedelic, `musika` → ∅) y palabras vacías.
4. **Lugar.** Si la clave compacta está en el gaceteer (`data/locations/places.json`
   + `rules.json` + lista de países y ciudades externas), el tag es de LUGAR y va
   al grupo `lugar:*`. Nunca se funde con un género. Un tag mixto (`punk vasco`,
   `freejazz bilbao`) pierde la parte de lugar y sigue como género, marcado como
   dudoso. `basque music` / `euskal musika` se tratan como marca de origen →
   `lugar:euskal herria` (dudoso, listado).
5. **Otro.** Años y décadas, formatos (ep, demo, cassette, en directo…), idiomas
   (euskaraz, castellano…), instrumentos y etiquetas de escena (diy, antifa,
   queer…) van a `otro:*`, cada uno con subtipo.
6. **Género.** Lo demás es género si contiene una raíz musical conocida
   (`GENRE_ROOTS`) o está en `GENRE_TERMS`. Raíces pegadas solo de una lista corta
   (`crustcore`, `blackgaze`; `petruska` no cuenta por "-ska").
7. **Erratas.** Concepto pequeño (< 30 discos) a distancia 1 (≥ 6 letras) o 2
   (≥ 10) de un nodo con ≥ 20 discos, misma letra inicial, y que no sea ya un
   término conocido → se funde (`experiemental` → experimental). Siempre dudoso.
8. **Umbral.** `MIN_DISCOS = 5`. Un concepto de género con menos discos no es nodo:
   cuelga del padre más cercano (sufijo de palabras más largo que sea nodo →
   subsecuencia contigua → palabra suelta → raíz pegada). Sin padre → `otros
   géneros`. Lugares pequeños suben municipio → territorio → Euskal Herria →
   `otros lugares`; los `otro` pequeños cuelgan de su subtipo.

Lo que no cumple nada (nombres de grupo, sellos, palabras sueltas, consignas)
va al nodo `resto`: sigue en el mapa, pero no es navegable. El informe lista
los 40 más frecuentes por si alguno es un género que el vocabulario no cazó.

## Umbral

| MIN_DISCOS | Nodos |
|---|---|
| 3 | 507 |
| 4 | 476 |
| **5** | **452** |
| 6 | 431 |
| 8 | 391 |

Se ha fijado 5: está dentro del objetivo (400-500) y coincide con el corte que
el diagnóstico usó para "microgénero con material".

## Qué se marca como dudoso

- Erratas fusionadas.
- Cuelgues donde más de una palabra del tag era nodo (`hardcore techno` bajo
  techno, pero hardcore también encajaba).
- Prefijos que cambian el sentido (post-, anti-, neo-, proto-, no-).
- Tags a los que se les quitó la parte de lugar.
- Sinónimos editoriales discutibles (`DOUBTFUL_SYNONYMS`): alternative →
  alternative rock, indie → indie rock, electronica → electronic, crust punk →
  crust, skinhead → oi!, trash → thrash metal, euskal rock → rock, etc.

Están en la sección final del informe (los de ≥ 2 discos) y completos en el
campo `dudosas` del JSON.

## Decisiones abiertas para Miguel

- **`alternative` (954 discos) e `indie` (252)** se funden con `alternative rock` e
  `indie rock`. Son umbrellas de Bandcamp; la alternativa es dejarlos como nodos
  propios (ruidosos).
- **`euskal rock`, `rock vasco`, `euskal punk`, `basque metal`…** pierden el
  gentilicio y van al género; la escena queda cubierta por `lugar:euskal herria`.
  Excepción deliberada: **`euskal folk`** es nodo propio (trikitixa, txalaparta,
  alboka, bertso, euskal kantagintza), porque es una tradición musical, no solo
  un origen.
- **`poky`** absorbe bumping, hardbass, scouse house, bakalao, hard dance (escena
  makina).
- Segunda fase (cuando se apruebe el mapa): consumirlo desde `Explorar.jsx` y
  `Archivo.jsx`. Esta rama no toca `app/`.
