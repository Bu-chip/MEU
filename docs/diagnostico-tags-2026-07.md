# Diagnóstico del campo `tags` — ¿hay material para un explorador de microgéneros?

**Fecha:** 2026-07-13 · **Fuente:** `data/bandcamp_bilbaotags_clean.json` (7.568 discos, tras el merge del PR #24)
**Datos completos de la clasificación:** `data/tag_buckets_2026-07.json`
**Pregunta:** ¿el campo `tags` contiene microgéneros ricos tipo EveryNoise, con al menos un grupo por microgénero, como para alimentar un futuro "explorador de microgéneros de Euskal Herria" al estilo del genre-explorer (Bu-chip/genre-explorer)?

**Veredicto corto: sí hay material.** ~700 microgéneros con ≥3 discos reproducibles y ~350 con ≥10. El cuello de botella no es la riqueza sino la limpieza/fusión de tags (trabajo acotado y mecánico). Detalle al final.

---

## 1. Tags únicos: 5.537 (antes del merge: 2.090)

El campo `tags` a nivel raíz del JSON y el recuento real sobre los álbumes coinciden exactamente: **5.537 tags únicos**.

| | Discos | Tags únicos |
|---|---|---|
| Antes del merge (commit `442e766`) | 2.364 | 2.090 |
| Después del merge PR #24 | 7.568 | 5.537 |

Los 5.204 discos incorporados aportaron **3.447 tags nunca vistos** (+165%) y no se perdió ninguno de los 2.090 originales. El merge no solo triplicó el catálogo: casi triplicó el vocabulario.

## 2. Distribución de frecuencias: cola larga real

| Frecuencia | Tags | % |
|---|---|---|
| 1 solo disco | 3.328 | 60% |
| 2–5 discos | 1.381 | 25% |
| 6–20 discos | 529 | 10% |
| 21+ discos | 299 | 5% |

La forma es exactamente la de una cola larga tipo EveryNoise: unos pocos tags gigantes (rock 1.983, electronic 1.398, punk 1.348, metal 1.048) y miles de tags específicos. La zona útil para un explorador es la franja 2–20 discos: ~1.900 tags.

## 3. Señal vs. ruido: clasificación de los 5.537 tags

### Criterios usados

Heurística por vocabulario + correcciones manuales de todos los tags con ≥6 discos:

- **Territorial**: gazetteer de municipios/provincias/regiones de Euskal Herria (~130 topónimos: bilbao, iruña, zarautz, enkarterri, hasparren...) más países y ciudades externas (spain, madrid, tokyo...).
- **Otro**: años (regex `19xx`/`20xx`), formatos (vinyl, cassette, ep, demo, split...), idiomas (euskara, castellano...), instrumentos usados como tag (piano, cello, mellotron...), sellos identificables (bidehuts, elefant records...) y nombres propios de artistas usados como tag (kokoshca, lisabo, ibon errazkin...).
- **Género**: ~700 raíces de vocabulario musical (punk, core, gaze, wave, synth, triki, bertso...) más ~100 expresiones multipalabra (dream pop, boom bap, d-beat, oi!...).
- **Ambiguo/resto**: lo que no casa con nada de lo anterior.

### Resultado

| Categoría | Tags únicos | Apariciones (disco×tag) |
|---|---|---|
| **Género/microgénero** | **1.789 (32%)** | **32.028 (67%)** |
| Territorial | 225 (4%) | 7.401 (15%) |
| Otro (años, formatos, idioma, sellos, instrumentos) | 163 (3%) | 1.844 (4%) |
| Ambiguo/resto | 3.360 (61%) | 6.990 (14%) |

Matices importantes:

- El bloque "ambiguo" son casi todos singletons (2.427 de 3.360) y, muestreándolo, es mayormente nombres de grupo, sellos pequeños, palabras sueltas ("lluvia", "frodo", "michel foucault") y erratas ("experiemental", "reagge") — con quizá un 15-20% de géneros que el vocabulario heurístico no cazó. La cifra honesta de géneros estaría entre **1.800 y 2.200**.
- Aunque el ruido domina en tags *únicos*, **el 67% de todas las asignaciones tag→disco son de género**. El campo trabaja mayoritariamente como campo de género.

Distribución solo dentro de los 1.789 tags de género: 825 con 1 disco · 467 con 2–5 · 292 con 6–20 · 205 con 21+.

## 4. Los microgéneros jugosos (ejemplos reales, nº de discos)

Excluyendo los ~55 tags "paraguas" (rock, punk, techno, pop, metal...), lo más EveryNoise que hay dentro:

**Extremo / punk**: crust punk (120), oi! (91), d-beat (42), street punk (40), garage punk (36), atmospheric black metal (27), goregrind (24), powerviolence (22), anarchopunk (17), fastcore (16), raw black metal (15), neocrust (11), emoviolence (8), skramz (5), stenchcore (4), raw punk (4), egg punk (3), noise punk (3), rock radical vasco/rrv (2).

**Electrónica**: dark ambient (240), idm (148), dub techno (92), dungeon synth (53), scouse house (34), **poky (34), bumping (34), hardbass (34)** ← la escena makina/poky vasca, un microgénero regional genuino que EveryNoise lista como "bumping" —, digicore (24), internetcore (24), vaporwave (19), breakcore (18), italo disco (14), coldwave (12), **dreampunk (11), medicalcore (11), postvore (11), deathdream (11)** ← microgéneros de internet ultraespecíficos —, musique concrete (10), new beat (7), berlin school (6), hexd (2).

**Pop / rock de nicho**: dream pop (71), bedroom pop (22), krautrock (22), noise pop (19), slowcore (14), jangle pop (14), freakbeat (10), midwest emo (6), blackgaze (2).

**Raíz / jamaicano / latino**: rocksteady (26), boom bap (23), raggamuffin (20), cumbia (18), lovers rock (9), steppas (9).

**Vasco-específicos**: euskal musika (104), euskal rock (23), euskal rap (8), alboka (7), txalaparta (4), trikitixa (3), bertso (3), euskal kantagintza (3), euskaltrap (3), bertsolaritza (2), euskal-wave (1).

Top 40 de microgéneros por volumen (sin paraguas): post-punk (312), death metal (280), hardcore punk (268), black metal (261), dark ambient (240), grindcore (213), post-hardcore (211), soundtrack (180), post-rock (154), idm (148), tech house (148), rock & roll (143), minimal (132), crust (132), experimental electronic (129), indie pop (128), crust punk (120), deathcore (120), lo-fi (118), doom (117), djent (116), metalcore (109), psychedelic (104), grunge (101), thrash metal (100), doom metal (97), improvisation (96), pop punk (96), folk rock (94), dub techno (92), oi! (91), garage (89), emo (86), sludge (85), deep house (82), brutal death metal (82), stoner (81), synthpop (81), downtempo (79), progressive rock (74).

## 5. Utilizabilidad: casi todo tiene preview

7.553 de 7.568 discos (99,8%) tienen `album_id`.

| Umbral | Tags de género que lo cumplen (discos con `album_id`) |
|---|---|
| ≥1 disco | 1.787 (de 1.789) |
| ≥3 discos | 738 — excluyendo paraguas: **693 microgéneros** |
| ≥5 discos | 548 |
| ≥10 discos | 350 |

## 6. Veredicto

**Sí hay material, y más del esperado.** No es un catálogo de "punk/rock/pop y para de contar": hay ~700 microgéneros con ≥3 discos reproducibles y ~350 con ≥10, incluyendo joyas regionales (poky/bumping, euskal kantagintza, trikitixa) y microgéneros de internet inesperados en un catálogo vasco (dreampunk, medicalcore, hexd). Para comparar: EveryNoise cubre el planeta con ~6.000 géneros; que una sola escena regional sostenga 350–700 nodos navegables es riqueza real.

Dos avisos antes de construir nada:

1. **Necesitará normalización, no está listo tal cual.** Duplicados masivos por grafía ("crust"/"crust punk"/"crustcore", "rock and roll"/"rock & roll"/"rock'n'roll" son 3 nodos que deberían ser uno; "euskal herria" aparece de 4 formas), erratas ("experiemental" con 29 discos), tags compuestos basura ("trance electro techno", 74) y tags-consigna ("euskal herria is not"). Un mapa de fusión reduciría los ~700 a quizá 400–500 nodos limpios — que sigue siendo mucho.
2. **La cola de singletons (3.328 tags) es mayormente ruido** (nombres de grupo, sellos, palabras sueltas): no contar con ella para nodos, aunque algún microgénero de 1 disco ("dsbm", "makina", "funeral doom") podría rescatarse fusionándolo con su vecino.

Conclusión: la idea tiene suelo debajo. El cuello de botella no será la falta de microgéneros sino la limpieza/fusión de tags.

---

## Apéndice: reproducibilidad

- La clasificación completa de los 5.537 tags (categoría + nº de discos + nº de discos con `album_id` por tag) está en **`data/tag_buckets_2026-07.json`**.
- Los recuentos se calculan directamente sobre `data/bandcamp_bilbaotags_clean.json`; la comparación pre-merge usa el estado del catálogo en el commit `442e766` (último commit antes de incorporar los candidatos del PR #23).
- La clasificación es heurística (vocabulario + revisión manual de todos los tags con ≥6 discos); los tags con ≤5 discos del bloque "ambiguo" no fueron revisados uno a uno.
