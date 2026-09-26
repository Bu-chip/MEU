# Auditoría de calidad del canónico — 2026-09-26

*Generado por `python3 scripts/quality_audit.py`. Solo lectura: este informe no cambia datos. No editar a mano; regenerar.*

Canónico: **7637** fichas, 3632 artistas, 5536 tags. Procedencia por `album_id` (2026-07: 5305, 2026-08: 27, 2026-09: 42, orig.: 2263); «orig.» = catálogo anterior a julio o sin `album_id` en ninguna oleada.

## Cómo leerlo

- Cada categoría trae su recuento total y una tabla con como mucho 30 ejemplos (ordenados por `id`).
- `origen` dice por qué oleada de candidatos entró la ficha (2026-07/08/09) o si es del catálogo original.
- Nada de esto se ha corregido. Lo mecánico y claro va a reglas en `scripts/pipeline.py` (fase 2); lo de artistas lo decide Miguel.

## Ya resuelto por el pipeline (comprobación de regresión)

Lo que `scripts/pipeline.py` corrigió en PRs anteriores no se vuelve a auditar; solo se comprueba que sigue a cero.

| Paso | Restos hoy |
|---|---:|
| `step_clean_urls` (cola `?from=…`) | 0 |
| `step_dedupe_releases` (35 filas auditadas) | 0 |
| `step_normalize_artist_names` (41 variantes) | 0 |
| `step_clean_invisible_chars` | 0 |
| `step_normalize_tags` (`TAG_RENAMES` + `TAG_SPLITS`) | 0 |
| tags repetidos dentro de una ficha | 0 |

## Resumen

| Categoría | Recuento |
|---|---:|
| [Campos fuera del esquema o con tipo incorrecto](#esquema) | 0 |
| [Duplicados: mismo `album_id`](#dup_album_id) | 0 |
| [Duplicados: misma URL normalizada](#dup_url) | 0 |
| [Duplicados: mismo artista+título normalizados con distinta URL](#dup_artist_title) | 25 grupos |
| [Posibles reediciones: mismo artista y mismo slug de URL en otra cuenta](#reedicion_slug) | 1 grupos |
| [Artistas: mismo nombre escrito de varias formas](#artist_variants) | 170 grupos |
| [Artistas: capitalización rara frente a otra grafía del catálogo](#artist_case) | 123 filas |
| [Artistas solo en MAYÚSCULAS o solo en minúsculas (informativo)](#artist_style) | 549 en MAYÚSCULAS, 250 en minúsculas |
| [Artista o título con espacios sobrantes o puntuación colgante](#whitespace) | 25 filas |
| [`genre` null o vacío](#genre_null) | 46 filas |
| [`genre` fuera del vocabulario](#genre_vocab) | 0 |
| [`tags` vacío](#tags_empty) | 30 filas |
| [Tags sucios (vacíos, espacios, mayúsculas, puntuación colgante)](#tags_dirty) | 32 filas |
| [Tags: variantes del mismo tag no cubiertas por `TAG_RENAMES` (informativo)](#tag_variants) | 182 grupos |
| [URLs sucias](#url_dirty) | 60 filas |
| [URL nula](#url_null) | 5 filas |
| [`year` vacío](#year_null) | 23 filas |
| [`year` imposible (< 1960 o > 2027)](#year_bad) | 0 |
| [Portada vacía (`cover_url` null)](#cover_null) | 15 filas |
| [Portada fuera de bcbits.com](#cover_domain) | 0 |
| [`album_id` nulo](#album_id_null) | 15 filas |
| [Títulos con el artista como prefijo («Artista - Título»)](#title_prefix) | 191 filas |

<a id="esquema"></a>
## Campos fuera del esquema o con tipo incorrecto

**Recuento: 0 filas.**

Sin casos.

<a id="dup_album_id"></a>
## Duplicados: mismo `album_id`

**Recuento: 0 grupos.**

Sin casos.

<a id="dup_url"></a>
## Duplicados: misma URL normalizada

**Recuento: 0 grupos.**

Normalización: sin esquema, query ni fragmento, sin barra final, todo en minúsculas.

Sin casos.

<a id="dup_artist_title"></a>
## Duplicados: mismo artista+título normalizados con distinta URL

**Recuento: 25 grupos.**

Comparación sin acentos, sin mayúsculas ni puntuación. Suelen ser la edición del grupo y la del sello (o dos bandas homónimas): decisión humana.

| id | album_id | origen | artista | título | cuentas | url |
|---|---|---|---|---|---|---|
| 72 | 1478149924 | 2026-07 | Alkuperä | Sendero Desesperanza | alkupera.bandcamp.com, knr-alkupera.bandcamp.com | [↗](https://alkupera.bandcamp.com/album/sendero-desesperanza) |
| 4902 | 1874894446 | 2026-07 | Alkupera | Sendero Desesperanza | ″ | [↗](https://knr-alkupera.bandcamp.com/album/sendero-desesperanza) |
| 113 | 3144832556 | orig. | Marmol | Declaración total de guerra | andaluciauberalles.bandcamp.com, furiousrecords.bandcamp.com | [↗](https://furiousrecords.bandcamp.com/album/m-rmol-declaraci-n-total-de-guerra) |
| 2602 | 1437736180 | 2026-07 | Marmol | Declaración Total de Guerra | ″ | [↗](https://andaluciauberalles.bandcamp.com/album/declaraci-n-total-de-guerra) |
| 464 | 2708679514 | orig. | Negracalavera | NEGRACALAVERA - Espérame en el coche | negracalavera.bandcamp.com, zirikaturecords.bandcamp.com | [↗](https://negracalavera.bandcamp.com/album/negracalavera-esp-rame-en-el-coche) |
| 1848 | 1027867036 | orig. | NEGRACALAVERA | NEGRACALAVERA "Espérame en el coche" | ″ | [↗](https://zirikaturecords.bandcamp.com/album/negracalavera-esp-rame-en-el-coche) |
| 468 | 3440800652 | orig. | Dual Split | Brand New Rain | dual-split.bandcamp.com, forbiddencolours.bandcamp.com | [↗](https://forbiddencolours.bandcamp.com/album/brand-new-rain) |
| 3616 | 2722995738 | 2026-07 | Dual-Split | Brand New Rain | ″ | [↗](https://dual-split.bandcamp.com/album/brand-new-rain) |
| 739 | 1870300254 | orig. | Campamento Rumano | El punk está lleno de sinvergüenzas | campamentorumano.bandcamp.com, discosbanana1.bandcamp.com | [↗](https://campamentorumano.bandcamp.com/album/el-punk-est-lleno-de-sinverg-enzas) |
| 3545 | 3339653347 | 2026-07 | Campamento Rumano | El punk esta lleno de sinvergüenzas | ″ | [↗](https://discosbanana1.bandcamp.com/album/el-punk-esta-lleno-de-sinverg-enzas) |
| 1205 | 868401825 | orig. | Heisenberg | Heisenberg | heisenbergbilbo.bandcamp.com, heisenbergny.bandcamp.com | [↗](https://heisenbergny.bandcamp.com/album/heisenberg) |
| 2396 | 4273830922 | 2026-07 | Heisenberg | Heisenberg | ″ | [↗](https://heisenbergbilbo.bandcamp.com/album/heisenberg) |
| 1380 | 1593996000 | orig. | The Cherry Boppers | Remix It Again! | cherryboppers.bandcamp.com, thecherryboppers.bandcamp.com | [↗](https://thecherryboppers.bandcamp.com/album/remix-it-again) |
| 3247 | 718778818 | 2026-07 | The Cherry Boppers | Remix It Again | ″ | [↗](https://cherryboppers.bandcamp.com/album/remix-it-again) |
| 1789 | 2361714922 | orig. | HURACAN ROSE | 5,04 | huracanrose.bandcamp.com, lafamiliarevolucionrecords.bandcamp.com | [↗](https://lafamiliarevolucionrecords.bandcamp.com/album/504-single) |
| 4270 | 371483084 | 2026-07 | Huracan  Rose | 5,04 | ″ | [↗](https://huracanrose.bandcamp.com/album/504-2) |
| 2153 | 3806144412 | 2026-07 | II | +_xx | iikrisgm.bandcamp.com | [↗](https://iikrisgm.bandcamp.com/album/xx) |
| 2257 | 4273617452 | 2026-07 | II | -X-X | ″ | [↗](https://iikrisgm.bandcamp.com/album/x-x) |
| 2260 | 1142077705 | orig. | Selfshot | 19S Single | dexmusiccom.bandcamp.com, selfshot.bandcamp.com | [↗](https://selfshot.bandcamp.com/album/19s-single) |
| 3507 | 2027225073 | 2026-07 | Selfshot | 19S - Single | ″ | [↗](https://dexmusiccom.bandcamp.com/album/19s-single) |
| 2292 | — | orig. | HUMANO | HUMANO | humano-ec.bandcamp.com, humanorock.bandcamp.com | [↗](https://humano-ec.bandcamp.com/album/danza) |
| 2397 | 1203358172 | 2026-07 | HUMANO | HUMANO | ″ | [↗](https://humanorock.bandcamp.com/album/humano) |
| 2751 | 2573882965 | 2026-07 | Kokoshca | Hay Una Luz | ayosilver.bandcamp.com, kokoshca.bandcamp.com | [↗](https://ayosilver.bandcamp.com/album/hay-una-luz) |
| 4920 | 2349716514 | 2026-07 | K O K O S H C A | HAY UNA LUZ | ″ | [↗](https://kokoshca.bandcamp.com/album/hay-una-luz) |
| 2988 | 946199743 | 2026-07 | Jupiter Jon eta Amaren Alabak | cOUPAGES #03 | bidehuts.bandcamp.com, jupiterjon.bandcamp.com | [↗](https://bidehuts.bandcamp.com/album/coupages-03) |
| 4788 | 1925102212 | 2026-07 | Jupiter Jon eta Amaren Alabak | COUPAGES#03 | ″ | [↗](https://jupiterjon.bandcamp.com/album/coupages-03) |
| 2993 | 4100576229 | 2026-07 | Jupiter Jon | Eta metaforak greba egin zeben | bidehuts.bandcamp.com, jupiterjon.bandcamp.com | [↗](https://bidehuts.bandcamp.com/album/eta-metaforak-greba-egin-zeben) |
| 4789 | 3710792007 | 2026-07 | Jupiter Jon | Eta metaforak greba egin zeben.... | ″ | [↗](https://jupiterjon.bandcamp.com/album/eta-metaforak-greba-egin-zeben) |
| 3001 | 1888407170 | 2026-07 | Joseba Irazoki | Gitarra Lekeitioak (Onomatopeikoa II) | bidehuts.bandcamp.com, josebairazoki.bandcamp.com | [↗](https://bidehuts.bandcamp.com/album/gitarra-lekeitioak-onomatopeikoa-ii) |
| 4735 | 1438532365 | 2026-07 | JOSEBA IRAZOKI | GITARRA LEKEITIOAK(ONOMATOPEIKOA II) | ″ | [↗](https://josebairazoki.bandcamp.com/album/gitarra-lekeitioak-onomatopeikoa-ii) |
| 3278 | 1940686263 | 2026-07 | Massa Confusa | Evolve EP | clartycat.bandcamp.com, massaconfusa.bandcamp.com | [↗](https://clartycat.bandcamp.com/album/evolve-ep) |
| 5434 | 3542197424 | 2026-07 | massa confusa | Evolve (EP) | ″ | [↗](https://massaconfusa.bandcamp.com/album/evolve-ep) |
| 3575 | 2313001102 | 2026-07 | /GÖO! | June - ep | djgoo.bandcamp.com, musexindustries.bandcamp.com | [↗](https://djgoo.bandcamp.com/album/june-ep) |
| 5745 | 136773271 | 2026-07 | Göo | June ep | ″ | [↗](https://musexindustries.bandcamp.com/album/june-ep) |
| 3929 | 2678501800 | 2026-07 | Río Arga | RÍO ARGA | rioarga.bandcamp.com | [↗](https://rioarga.bandcamp.com/album/r-o-arga-2) |
| 6481 | 3360721895 | 2026-07 | Rio Arga | RÍO ARGA | ″ | [↗](https://rioarga.bandcamp.com/album/r-o-arga) |
| 4342 | 193733917 | 2026-07 | miguel a. garcía . tomas gris . lee noyes | asto ilunno | idealstaterecordings.bandcamp.com, xedh.bandcamp.com | [↗](https://idealstaterecordings.bandcamp.com/album/asto-ilunno) |
| 7384 | 2329147452 | 2026-07 | miguel a. garcía , tomas gris , lee noyes | asto ilunno | ″ | [↗](https://xedh.bandcamp.com/album/asto-ilunno) |
| 5256 | 1243027060 | 2026-07 | -Love- | Chasm of Agony | love-evolmusic.bandcamp.com | [↗](https://love-evolmusic.bandcamp.com/album/chasm-of-agony) |
| 5257 | 2761122398 | 2026-07 | -Love- | +Chasm of agony+ | ″ | [↗](https://love-evolmusic.bandcamp.com/album/chasm-of-agony-2) |
| 5271 | 2410844109 | 2026-07 | -Love- | Immolation desperation | love-evolmusic.bandcamp.com | [↗](https://love-evolmusic.bandcamp.com/album/immolation-desperation) |
| 5272 | 3842224473 | 2026-07 | -Love- | +Immolation desperation+ | ″ | [↗](https://love-evolmusic.bandcamp.com/album/immolation-desperation-2) |
| 5277 | 880470302 | 2026-07 | -Love- | Love//Evol | love-evolmusic.bandcamp.com | [↗](https://love-evolmusic.bandcamp.com/album/love-evol) |
| 5278 | 889237957 | 2026-07 | -Love- | +Love//Evol+ | ″ | [↗](https://love-evolmusic.bandcamp.com/album/love-evol-2) |
| 5286 | 1471456538 | 2026-07 | -Love- | Spiral skull decapitation | love-evolmusic.bandcamp.com | [↗](https://love-evolmusic.bandcamp.com/album/spiral-skull-decapitation) |
| 5287 | 2296685037 | 2026-07 | -Love- | +Spiral skull decapitation+ | ″ | [↗](https://love-evolmusic.bandcamp.com/album/spiral-skull-decapitation-2) |
| 5730 | 15450437 | 2026-07 | Reykjavik606 | From.. To... | musexindustries.bandcamp.com, reykjavik606.bandcamp.com | [↗](https://musexindustries.bandcamp.com/album/from-to) |
| 6475 | 2374422358 | 2026-07 | Reykjavik606 | From… To... | ″ | [↗](https://reykjavik606.bandcamp.com/album/from-to) |
| 7126 | 917575561 | 2026-07 | Vibora | BOTÁNICA | uglyandproudrecords.bandcamp.com, viborahc.bandcamp.com | [↗](https://uglyandproudrecords.bandcamp.com/album/bot-nica) |
| 7282 | 1550439116 | 2026-07 | VIBORA | BOTÁNICA | ″ | [↗](https://viborahc.bandcamp.com/album/bot-nica) |

<a id="reedicion_slug"></a>
## Posibles reediciones: mismo artista y mismo slug de URL en otra cuenta

**Recuento: 1 grupos.**

El título difiere (si no, ya estaría en la categoría anterior) pero el slug de Bandcamp es idéntico. Mirar si es el mismo disco.

| id | album_id | origen | artista | título | slug | url |
|---|---|---|---|---|---|---|
| 910 | 3048501598 | orig. | Marmol | MARMOL - Declaración total de guerra | declaraci-n-total-de-guerra | [↗](https://marmolbilbao.bandcamp.com/album/declaraci-n-total-de-guerra) |
| 2602 | 1437736180 | 2026-07 | Marmol | Declaración Total de Guerra | ″ | [↗](https://andaluciauberalles.bandcamp.com/album/declaraci-n-total-de-guerra) |

<a id="artist_variants"></a>
## Artistas: mismo nombre escrito de varias formas

**Recuento: 170 grupos.**

Agrupado con clave fuerte (sin acentos, mayúsculas ni puntuación). Cada fila es un grupo; entre paréntesis, nº de fichas con esa grafía. Los nombres colaborativos («A & B» / «A, B») también caen aquí.

| id | album_id | origen | artista | título | variantes | url |
|---|---|---|---|---|---|---|
| 6 | 911225637 | orig. | V.A. | Kikeku (Haurreskola) | `V.A.` (3), `V/A` (1), `VA` (1) | [↗](https://haziesporak.bandcamp.com/album/kikeku-haurreskola) |
| 5245 | 2873311131 | 2026-07 | V/A | igoerA | ″ | [↗](https://lotura.bandcamp.com/album/igoera) |
| 6571 | 1464573554 | 2026-07 | VA | STMG999 VA - Nguru | ″ | [↗](https://secretsocietychile.bandcamp.com/album/stmg999-va-nguru) |
| 25 | 779448805 | orig. | judy | Eŕoa Bat | `judy` (11), `Judy` (3) | [↗](https://erroa.bandcamp.com/album/e-oa-bat) |
| 546 | 2291292504 | orig. | Judy | ER041 Judy - Tergo | ″ | [↗](https://eclecticreactionsrecords.bandcamp.com/album/er041-judy-tergo) |
| 45 | 784349555 | orig. | VVAA | BAP163 Diamonds In The Night Vol.5 - WLDV - Relax & Enjoy | `VVAA` (8), `VV AA` (1) | [↗](https://wldv.bandcamp.com/album/bap163-diamonds-in-the-night-vol-5-wldv-relax-enjoy) |
| 3156 | 2341552605 | 2026-07 | VV AA | Así que esto es el fin (4 canciones para Josetxo) | ″ | [↗](https://brisadelapalma.bandcamp.com/album/as-que-esto-es-el-fin-4-canciones-para-josetxo) |
| 61 | 1773694445 | orig. | Inigo Lunani | Halloween Electronic [LNI09] | `Inigo Lunani` (14), `Iñigo Lunani` (1) | [↗](https://inigolunani.bandcamp.com/album/halloween-electronic-lni09) |
| 3853 | 2983445889 | 2026-07 | Iñigo Lunani | FNVM | ″ | [↗](https://esnebidearecords.bandcamp.com/album/fnvm) |
| 72 | 1478149924 | 2026-07 | Alkuperä | Sendero Desesperanza | `Alkupera` (1), `Alkuperä` (1) | [↗](https://alkupera.bandcamp.com/album/sendero-desesperanza) |
| 4902 | 1874894446 | 2026-07 | Alkupera | Sendero Desesperanza | ″ | [↗](https://knr-alkupera.bandcamp.com/album/sendero-desesperanza) |
| 113 | 3144832556 | orig. | Marmol | Declaración total de guerra | `Marmol` (8), `MÁRMOL` (1) | [↗](https://furiousrecords.bandcamp.com/album/m-rmol-declaraci-n-total-de-guerra) |
| 146 | 3043169698 | orig. | MÁRMOL | LADV166 - MÁRMOL "declaración total de guerra" LP | ″ | [↗](https://laagoniadevivir.bandcamp.com/album/ladv166-m-rmol-declaraci-n-total-de-guerra-lp) |
| 135 | 1421893965 | orig. | Wicked Wizzard | Warlords Of The Dark Realm | `Wicked Wizzard` (1), `Wicked wizzard` (1) | [↗](https://wickedwizzard.bandcamp.com/album/warlords-of-the-dark-realm) |
| 7349 | 383619485 | 2026-07 | Wicked wizzard | Wicked Wizzard | ″ | [↗](https://wickedwizzard.bandcamp.com/album/wicked-wizzard) |
| 216 | 3196561150 | orig. | Antxon Sagardui, BassDefender | Ugari Geu | `Antxon Sagardui & BassDefender` (3), `Antxon Sagardui, BassDefender` (1) | [↗](https://crudobilbao.com/album/ugari-geu) |
| 536 | 3542454353 | orig. | Antxon Sagardui & BassDefender | Aldapa | ″ | [↗](https://crudobilbao.com/album/aldapa) |
| 261 | 2213600476 | orig. | Negracalavera | Impredecible | `Negracalavera` (2), `NEGRACALAVERA` (1) | [↗](https://negracalavera.bandcamp.com/album/impredecible) |
| 1848 | 1027867036 | orig. | NEGRACALAVERA | NEGRACALAVERA "Espérame en el coche" | ″ | [↗](https://zirikaturecords.bandcamp.com/album/negracalavera-esp-rame-en-el-coche) |
| 288 | 2139577047 | orig. | Ura | URA s/t 2014 | `URA` (1), `Ura` (1) | [↗](https://urapunx.bandcamp.com/album/ura-s-t-2014) |
| 1156 | 2233289320 | orig. | URA | LADV45 - URA "st" 12" | ″ | [↗](https://laagoniadevivir.bandcamp.com/album/ladv45-ura-st-12) |
| 359 | 2688332711 | orig. | Dr. Maha's Miracle Tonic | FSR029 Dr. Maha's Miracle Tonic - Boogie Mama! (EP) | `Dr. Maha's Miracle Tonic` (2), `Dr. Maha´s Miracle Tonic` (1) | [↗](https://familyspreerecordings.bandcamp.com/album/fsr029-dr-mahas-miracle-tonic-boogie-mama-ep) |
| 1459 | 92327523 | 2026-07 | Dr. Maha´s Miracle Tonic | BANK ROBBERS | ″ | [↗](https://drmahasmiracletonic.bandcamp.com/album/bank-robbers) |
| 407 | 2596584165 | 2026-07 | Cult of Misery | Together to hell (LP) | `CULT OF MISERY` (2), `Cult of Misery` (2), `Cult Of Misery` (1) | [↗](https://cultofmisery.bandcamp.com/album/together-to-hell-lp) |
| 3340 | 1365582272 | 2026-07 | Cult Of Misery | Split 7" | ″ | [↗](https://corsariosestudios.bandcamp.com/album/split-7) |
| 4988 | 444668900 | 2026-07 | CULT OF MISERY | LADV121 - CULT OF MISERY "together to hell" LP | ″ | [↗](https://laagoniadevivir.bandcamp.com/album/ladv121-cult-of-misery-together-to-hell-lp) |
| 468 | 3440800652 | orig. | Dual Split | Brand New Rain | `Dual-Split` (3), `Dual Split` (1) | [↗](https://forbiddencolours.bandcamp.com/album/brand-new-rain) |
| 3615 | 1019961771 | 2026-07 | Dual-Split | A Thank You EP | ″ | [↗](https://dual-split.bandcamp.com/album/a-thank-you-ep) |
| 471 | 250551814 | 2026-07 | Diana Lagarto | S/T | `Diana Lagarto` (2), `DIANA LAGARTO` (1) | [↗](https://dianalagarto.bandcamp.com/album/s-t) |
| 1151 | 1232650862 | orig. | DIANA LAGARTO | LADV39 - DIANA LAGARTO "st" LP | ″ | [↗](https://laagoniadevivir.bandcamp.com/album/ladv39-diana-lagarto-st-lp) |
| 501 | 1609686029 | orig. | HiGrade | Insanity | `HiGrade` (1), `Higrade` (1) | [↗](https://crudobilbao.com/album/insanity) |
| 3477 | 719204283 | 2026-07 | Higrade | Thought Experiments | ″ | [↗](https://deepnas.bandcamp.com/album/thought-experiments) |
| 519 | 390897633 | orig. | Sembrando Kaos | Amorruak beldurra jango du | `Sembrando Kaos` (2), `SEMBRANDO KAOS` (1), `sembrando kaos` (1) | [↗](https://sembrandokaos.bandcamp.com/album/amorruak-beldurra-jango-du) |
| 6585 | 3425159365 | 2026-07 | sembrando kaos | Argia Egin Bedi | ″ | [↗](https://sembrandokaos.bandcamp.com/album/argia-egin-bedi) |
| 6587 | 1023742066 | 2026-07 | SEMBRANDO KAOS | KAUSA GALDUEN ZAINDARI | ″ | [↗](https://sembrandokaos.bandcamp.com/album/kausa-galduen-zaindari) |
| 627 | 306842123 | orig. | Mikel R. Nieto | CAA—52 | `MikelRNieto` (14), `Mikel R. Nieto` (1) | [↗](https://mikelrnieto.bandcamp.com/album/caa-52) |
| 1583 | 2186041619 | orig. | MikelRNieto | Sleeplessness - 14th Night | ″ | [↗](https://mikelrnieto.bandcamp.com/album/sleeplessness-14th-night) |
| 882 | 3689476775 | 2026-07 | TheDaltonics | The Daltonics | `TheDaltonics` (2), `The Daltonics` (1) | [↗](https://thedaltonics.bandcamp.com/album/the-daltonics) |
| 1598 | 1051914071 | orig. | The Daltonics | 3 | ″ | [↗](https://familyspreerecordings.bandcamp.com/album/fsr120-the-daltonics-3) |
| 909 | 3233000682 | orig. | DESPEÑAPERROS | LADV60 - DESPEÑAPERROS "herejía" LP | `Despeñaperros` (5), `DESPEÑAPERROS` (2) | [↗](https://laagoniadevivir.bandcamp.com/album/ladv60-despe-aperros-herej-a-lp) |
| 1107 | 729016215 | orig. | Despeñaperros | "Herejía" (2015) | ″ | [↗](https://despeaperros.bandcamp.com/album/herej-a-2015) |
| 975 | 1318770188 | orig. | kalipotxo | error bakui | `Kalipotxo` (1), `kalipotxo` (1) | [↗](https://kalipotxo.bandcamp.com/album/error-bakui) |
| 7645 | 739345812 | 2026-09 | Kalipotxo | KARNE Y WESOS | ″ | [↗](https://kalipotxo.bandcamp.com/album/karne-y-wesos) |
| 979 | 2399994912 | orig. | Meido | Zandergraun | `Meido` (2), `MEIDO` (1) | [↗](https://cosmictentacles.bandcamp.com/album/zandergraun) |
| 5461 | 2090885633 | 2026-07 | MEIDO | Munduko kamioirik handiena | ″ | [↗](https://meido.bandcamp.com/album/munduko-kamioirik-handiena) |
| 1039 | 1201707454 | orig. | HURACAN ROSE | RARA AVIS | `HURACAN ROSE` (4), `Huracan  Rose` (1), `Huracan rose` (1) | [↗](https://huracanrose.bandcamp.com/album/rara-avis) |
| 4270 | 371483084 | 2026-07 | Huracan  Rose | 5,04 | ″ | [↗](https://huracanrose.bandcamp.com/album/504-2) |
| 4271 | 3983558265 | 2026-07 | Huracan rose | Circulos electricos | ″ | [↗](https://huracanrose.bandcamp.com/album/circulos-electricos) |
| 1113 | 1371046895 | orig. | SISTEMA DE ENTRETENIMIENTO | Canciones Bélicas para Jóvenes | `SISTEMA DE ENTRETENIMIENTO` (1), `Sistema de entretenimiento` (1) | [↗](https://jgcproducciones.bandcamp.com/album/canciones-b-licas-para-jovenes-st) |
| 3544 | 355101788 | 2026-07 | Sistema de entretenimiento | 300 noches sin dormir | ″ | [↗](https://discosbanana1.bandcamp.com/album/300-noches-sin-dormir) |
| 1184 | 1806192180 | orig. | B FLAT | EL TIGRE | `B FLAT` (2), `B-Flat` (1) | [↗](https://bflat.bandcamp.com/album/el-tigre) |
| 1185 | 3008562370 | orig. | B-Flat | the B-FLAT album | ″ | [↗](https://bflat.bandcamp.com/album/the-b-flat-album) |
| 1268 | 1386362604 | orig. | Live Lüla | Blue Sun | `Live Lüla` (3), `Livelüla` (2) | [↗](https://livelula.bandcamp.com/album/blue-sun) |
| 5139 | 1528923309 | 2026-07 | Livelüla | Gure Bazterrak | ″ | [↗](https://livelulamusic.bandcamp.com/album/gure-bazterrak) |
| 1355 | 262980317 | orig. | ANCIENT EMBLEM | LADV38 - ANCIENT EMBLEM "throne with no god" LP | `ANCIENT EMBLEM` (2), `Ancient Emblem` (1) | [↗](https://laagoniadevivir.bandcamp.com/album/ladv38-ancient-emblem-throne-with-no-god-lp) |
| 3341 | 436489792 | 2026-07 | Ancient Emblem | Throne With No God | ″ | [↗](https://corsariosestudios.bandcamp.com/album/throne-with-no-god) |
| 1496 | 2700200235 | orig. | Mr. Yogo | ¿Qué les dejaremos? | `Mr. Yogo` (1), `Mr. Yogo,` (1) | [↗](https://mryogo.bandcamp.com/album/qu-les-dejaremos) |
| 2150 | 3202051067 | orig. | Mr. Yogo, | ¿Qué les dejaremos? Vol.3: Amor | ″ | [↗](https://mryogo.bandcamp.com/album/qu-les-dejaremos-vol-3-amor) |
| 1700 | 1793814919 | orig. | UrbanXtrm | Ammonites | `UrbanXtrm` (89), `URBANxTRM` (1) | [↗](https://urbanxtrm.bandcamp.com/album/ammonites) |
| 7164 | 208197830 | 2026-07 | URBANxTRM | Cantina de Cuba | ″ | [↗](https://urbanxtrm.bandcamp.com/album/cantina-de-cuba) |
| 2374 | 837672060 | orig. | Wayne & Neila | Split | `Wayne & Neila` (1), `Wayne/Neila` (1) | [↗](https://radixrecords.bandcamp.com/album/split) |
| 4958 | 434959812 | 2026-07 | Wayne/Neila | Wayne-Neila split | ″ | [↗](https://ktcdomesticproductions.bandcamp.com/album/wayne-neila-split) |
| 2416 | 79179195 | 2026-07 | 6jerseys | 333 - Tres tristes trans | `6jerseys` (13), `6Jerseys` (1) | [↗](https://6jerseys.bandcamp.com/album/333-tres-tristes-trans) |
| 2423 | 1774500612 | 2026-07 | 6Jerseys | Ilegal loops | ″ | [↗](https://6jerseys.bandcamp.com/album/ilegal-loops) |

*… y 140 más (solo se muestran 30).*

<a id="artist_case"></a>
## Artistas: capitalización rara frente a otra grafía del catálogo

**Recuento: 123 filas.**

Nombre TODO EN MAYÚSCULAS o todo en minúsculas cuando el mismo nombre existe en el catálogo con mayúscula inicial. No se propone canónica: eso lo decide Miguel (ver `ARTIST_RENAMES` en pipeline.py para las 41 ya decididas).

| id | album_id | origen | artista | título | estilo | otras grafías | url |
|---|---|---|---|---|---|---|---|
| 25 | 779448805 | orig. | judy | Eŕoa Bat | minúsculas (11 fichas) | `Judy` (3) | [↗](https://erroa.bandcamp.com/album/e-oa-bat) |
| 146 | 3043169698 | orig. | MÁRMOL | LADV166 - MÁRMOL "declaración total de guerra" LP | MAYÚSCULAS (1 fichas) | `Marmol` (8) | [↗](https://laagoniadevivir.bandcamp.com/album/ladv166-m-rmol-declaraci-n-total-de-guerra-lp) |
| 909 | 3233000682 | orig. | DESPEÑAPERROS | LADV60 - DESPEÑAPERROS "herejía" LP | MAYÚSCULAS (2 fichas) | `Despeñaperros` (5) | [↗](https://laagoniadevivir.bandcamp.com/album/ladv60-despe-aperros-herej-a-lp) |
| 975 | 1318770188 | orig. | kalipotxo | error bakui | minúsculas (1 fichas) | `Kalipotxo` (1) | [↗](https://kalipotxo.bandcamp.com/album/error-bakui) |
| 1039 | 1201707454 | orig. | HURACAN ROSE | RARA AVIS | MAYÚSCULAS (4 fichas) | `Huracan  Rose` (1), `Huracan rose` (1) | [↗](https://huracanrose.bandcamp.com/album/rara-avis) |
| 1113 | 1371046895 | orig. | SISTEMA DE ENTRETENIMIENTO | Canciones Bélicas para Jóvenes | MAYÚSCULAS (1 fichas) | `Sistema de entretenimiento` (1) | [↗](https://jgcproducciones.bandcamp.com/album/canciones-b-licas-para-jovenes-st) |
| 1151 | 1232650862 | orig. | DIANA LAGARTO | LADV39 - DIANA LAGARTO "st" LP | MAYÚSCULAS (1 fichas) | `Diana Lagarto` (2) | [↗](https://laagoniadevivir.bandcamp.com/album/ladv39-diana-lagarto-st-lp) |
| 1156 | 2233289320 | orig. | URA | LADV45 - URA "st" 12" | MAYÚSCULAS (1 fichas) | `Ura` (1) | [↗](https://laagoniadevivir.bandcamp.com/album/ladv45-ura-st-12) |
| 1184 | 1806192180 | orig. | B FLAT | EL TIGRE | MAYÚSCULAS (2 fichas) | `B-Flat` (1) | [↗](https://bflat.bandcamp.com/album/el-tigre) |
| 1355 | 262980317 | orig. | ANCIENT EMBLEM | LADV38 - ANCIENT EMBLEM "throne with no god" LP | MAYÚSCULAS (2 fichas) | `Ancient Emblem` (1) | [↗](https://laagoniadevivir.bandcamp.com/album/ladv38-ancient-emblem-throne-with-no-god-lp) |
| 1848 | 1027867036 | orig. | NEGRACALAVERA | NEGRACALAVERA "Espérame en el coche" | MAYÚSCULAS (1 fichas) | `Negracalavera` (2) | [↗](https://zirikaturecords.bandcamp.com/album/negracalavera-esp-rame-en-el-coche) |
| 2416 | 79179195 | 2026-07 | 6jerseys | 333 - Tres tristes trans | minúsculas (13 fichas) | `6Jerseys` (1) | [↗](https://6jerseys.bandcamp.com/album/333-tres-tristes-trans) |
| 2544 | 3503869306 | 2026-07 | ALITRUTA | PASAIA LIVE 2019 | MAYÚSCULAS (2 fichas) | `Alitruta` (1) | [↗](https://alitruta.bandcamp.com/album/pasaia-live-2019) |
| 2788 | 1815773577 | 2026-07 | BACKBONE | Rebirth | MAYÚSCULAS (1 fichas) | `Backbone` (2) | [↗](https://backbonehick.bandcamp.com/album/rebirth) |
| 2841 | 3681930577 | 2026-07 | BANANAS | Azal bat, urdina | MAYÚSCULAS (4 fichas) | `Bananas` (1) | [↗](https://bananas.bandcamp.com/album/azal-bat-urdina) |
| 2876 | 2539884001 | 2026-07 | BARRACUS | BUENAVENTURA | MAYÚSCULAS (3 fichas) | `Barracus` (1) | [↗](https://barracus.bandcamp.com/album/buenaventura-2) |
| 2919 | 1634798052 | 2026-07 | belarmiñak | Zerbaitengatik | minúsculas (1 fichas) | `Belarmiñak` (3) | [↗](https://belarmi-ak.bandcamp.com/album/zerbaitengatik) |
| 2979 | 4251922407 | 2026-07 | GAILU | Autosuntsipena Hasia Da 3,2,1...Znort!!! | MAYÚSCULAS (1 fichas) | `-Gailu` (1) | [↗](https://bidehuts.bandcamp.com/album/autosuntsipena-hasia-da-321-znort) |
| 3117 | 19263043 | 2026-07 | BORJA MOSKV | Between two waters | MAYÚSCULAS (2 fichas) | `Borja Moskv` (9) | [↗](https://borjamoskv.bandcamp.com/album/between-two-waters) |
| 3155 | 3391985317 | 2026-07 | BRINGAS | mentiras y otras verdades | MAYÚSCULAS (1 fichas) | `Bringas` (2) | [↗](https://bringas.bandcamp.com/album/mentiras-y-otras-verdades) |
| 3163 | 3456018402 | 2026-07 | BRUMADENSA | Brumadensa | MAYÚSCULAS (1 fichas) | `Brumadensa` (1) | [↗](https://brumadensa.bandcamp.com/album/brumadensa) |
| 3222 | 1637053804 | 2026-07 | campingás | Demuéstrame Que No Eres Una Máquina. | minúsculas (1 fichas) | `Campingás` (1) | [↗](https://campingas.bandcamp.com/album/demu-strame-que-no-eres-una-m-quina) |
| 3228 | 680305721 | 2026-07 | CAPITÁN TORTUGA | Diario Estelar | MAYÚSCULAS (3 fichas) | `Capitán Tortuga` (1) | [↗](https://capitantortuga.bandcamp.com/album/diario-estelar-2) |
| 3273 | 1600728021 | 2026-07 | CICLOS ITURGAIZ | ¿TIENES WEBCAM? | MAYÚSCULAS (1 fichas) | `Ciclos Iturgaiz` (1) | [↗](https://ciclositurgaiz.bandcamp.com/album/tienes-webcam) |
| 3368 | 2514083858 | 2026-07 | ARKADA SOCIAL | CR 006 - Hil Orduko Bizi | MAYÚSCULAS (1 fichas) | `Arkada Social` (1) | [↗](https://cromrecords.bandcamp.com/album/cr-006-hil-orduko-bizi) |
| 3575 | 2313001102 | 2026-07 | /GÖO! | June - ep | MAYÚSCULAS (1 fichas) | `Göo` (1) | [↗](https://djgoo.bandcamp.com/album/june-ep) |
| 3588 | 1851418528 | 2026-07 | DOMINISTIKUM | MIERDA CITY SAMPLER 2025 V/A | MAYÚSCULAS (2 fichas) | `Doministikum` (2) | [↗](https://doministikumtaldea.bandcamp.com/album/mierda-city-sampler-2025-v-a) |
| 3605 | 697001016 | 2026-07 | DR MUGRE | PROFESSIONAL DISSECTION | MAYÚSCULAS (1 fichas) | `Dr Mugre` (3) | [↗](https://drmugre.bandcamp.com/album/professional-dissection) |
| 3624 | 1524572066 | 2026-07 | DUKKHA | Jainko Berriak (des)Eraikiz | MAYÚSCULAS (1 fichas) | `Dukkha` (2) | [↗](https://dukkha.bandcamp.com/album/jainko-berriak-des-eraikiz) |
| 3697 | 2560422447 | 2026-07 | elcrack | b - 2020 | minúsculas (6 fichas) | `elCrack` (1) | [↗](https://elcrack.bandcamp.com/album/b-2020) |

*… y 93 más (solo se muestran 30).*

<a id="artist_style"></a>
## Artistas solo en MAYÚSCULAS o solo en minúsculas (informativo)

**Recuento: 549 en MAYÚSCULAS, 250 en minúsculas.**

Sin otra grafía en el catálogo: casi siempre es la estilización del propio grupo (COBRA, judy). Se listan solo los recuentos y una muestra; no es accionable sin mirar la página.

| id | album_id | origen | artista | título | estilo | url |
|---|---|---|---|---|---|---|
| 122 | 2563474460 | orig. | 0N4B | 0N4B - dots \| polygon network [NW0007] | MAYÚSCULAS | [↗](https://polygonnetwork.bandcamp.com/album/0n4b-dots-polygon-network-nw0007) |
| 193 | 3592945085 | orig. | AFTER LIFE | Gates Of Madness | MAYÚSCULAS | [↗](https://afterlifemetal.bandcamp.com/album/gates-of-madness) |
| 526 | 2696563145 | orig. | 6siss | Concrete Poetry . UNMTD246E | minúsculas | [↗](https://unsound-methods.bandcamp.com/album/concrete-poetry-unmtd246e) |
| 545 | 1106525880 | orig. | ABI | ABI - data elements \| polygon network [NW0048] | MAYÚSCULAS | [↗](https://polygonnetwork.bandcamp.com/album/abi-data-elements-polygon-network-nw0048) |
| 616 | 3380835526 | orig. | AFO & SAGACE | AFO&SAGACE - Subtire de Vara EP (2013) | MAYÚSCULAS | [↗](https://afomusic.bandcamp.com/album/afo-sagace-subtire-de-vara-ep-2013) |
| 823 | 476585357 | orig. | A.T.A | Maketa | MAYÚSCULAS | [↗](https://atta.bandcamp.com/album/maketa) |
| 908 | 1226537202 | 2026-07 | 5000 rpm | "Manifesto" (2.011) | minúsculas | [↗](https://5000rpm.bandcamp.com/album/manifesto-2011) |
| 980 | 695304507 | orig. | [sholl] | Un año de guerra | minúsculas | [↗](https://sholl.bandcamp.com/album/un-a-o-de-guerra) |
| 1246 | 1830456122 | orig. | 3kuad | streams | minúsculas | [↗](https://3kuad.bandcamp.com/album/streams) |
| 1634 | 3393318853 | orig. | adarbakar | Live at Kremlin | minúsculas | [↗](https://adarbakar.bandcamp.com/album/live-at-kremlin) |
| 1702 | 1457530502 | orig. | 83x5t | 77 Vol. 01 | minúsculas | [↗](https://83x5t.bandcamp.com/album/77-vol-01) |
| 2398 | 2423195149 | 2026-07 | 11vx | .powerlines remixtape | minúsculas | [↗](https://11vx.bandcamp.com/album/powerlines-remixtape) |
| 2408 | 2676410721 | 2026-07 | 25th coming fire | Bitterness | minúsculas | [↗](https://25thcomingfire.bandcamp.com/album/bitterness) |
| 2414 | 1253960866 | 2026-07 | 2ZIO | Orain eta hemen (2018) | MAYÚSCULAS | [↗](https://2zio.bandcamp.com/album/orain-eta-hemen-2018) |
| 2429 | 847501640 | 2026-07 | 6nemen9 | Pop-atic | minúsculas | [↗](https://6nemen9.bandcamp.com/album/pop-atic-2) |
| 2430 | 2935009775 | 2026-07 | A-13 | A-13 | MAYÚSCULAS | [↗](https://a-13.bandcamp.com/album/a-13) |
| 2433 | 2182395668 | 2026-07 | abenúe (avenue) | one year later | minúsculas | [↗](https://abenue.bandcamp.com/album/one-year-later) |
| 2434 | 4153802707 | 2026-07 | abereh | Joan-etorrian | minúsculas | [↗](https://abereh.bandcamp.com/album/joan-etorrian) |
| 2438 | 1008945489 | 2026-07 | ABOGADOS DEL RITMO | AdR - II | MAYÚSCULAS | [↗](https://abogadosdelritmo.bandcamp.com/album/adr-ii) |
| 2440 | 915556593 | 2026-07 | abra kadaver | La era del sueño | minúsculas | [↗](https://abrakadaver.bandcamp.com/album/la-era-del-sue-o) |
| 2441 | 2787049459 | 2026-07 | ACID LOVERZ ROCK | clases de frances pipu | MAYÚSCULAS | [↗](https://acidloverzrock.bandcamp.com/album/clases-de-frances-pipu) |
| 2578 | 3906284112 | 2026-07 | A.MAIAH | Desagerpenak | MAYÚSCULAS | [↗](https://amaiah.bandcamp.com/album/desagerpenak) |
| 2612 | 1149384024 | 2026-07 | A.KLEE | FOR MA PEEPZ EP | MAYÚSCULAS | [↗](https://andreiklee.bandcamp.com/album/for-ma-peepz-ep) |
| 4201 | 3723114385 | 2026-07 | (H)ERO | (H)ERO | MAYÚSCULAS | [↗](https://herotaldea.bandcamp.com/album/h-ero-2) |
| 4840 | 558753538 | 2026-07 | ---- KARLITOS PINTXA RUBEN CT ---- | DEMO | MAYÚSCULAS | [↗](https://karlitospintxarubenct.bandcamp.com/album/demo) |
| 5645 | 797387391 | 2026-07 | AGATHOCLES, MIXOMATOSIS & SACTHU | Split | MAYÚSCULAS | [↗](https://muertematarrecords.bandcamp.com/album/split-3) |
| 5732 | 628048934 | 2026-07 | 14anger | Fuel14 | minúsculas | [↗](https://musexindustries.bandcamp.com/album/fuel14) |
| 6582 | 4247860560 | 2026-07 | 3 y yos | El punto | minúsculas | [↗](https://segundosmusic.bandcamp.com/album/el-punto) |
| 6696 | 3207142379 | 2026-07 | 9n9u9e9v9e9 | Acero 9n9u9e9v9e9 | minúsculas | [↗](https://somniferumrec.bandcamp.com/album/acero-9n9u9e9v9e9) |
| 7449 | 4063459521 | 2026-07 | A.F.K | A.F.K (2023-09-23) | MAYÚSCULAS | [↗](https://zaratazarautz.bandcamp.com/album/a-f-k-2023-09-23) |

<a id="whitespace"></a>
## Artista o título con espacios sobrantes o puntuación colgante

**Recuento: 25 filas.**

| id | album_id | origen | artista | título | campo | problema | url |
|---|---|---|---|---|---|---|---|
| 2150 | 3202051067 | orig. | Mr. Yogo, | ¿Qué les dejaremos? Vol.3: Amor | artist | puntuación colgante | [↗](https://mryogo.bandcamp.com/album/qu-les-dejaremos-vol-3-amor) |
| 2296 | 3585143250 | orig. | Mr. Yogo, Salda Dago, Dj Ibai, | ¿Qué les dejaremos? Vol.lI: Guerra | artist | puntuación colgante | [↗](https://mryogo.bandcamp.com/album/qu-les-dejaremos-vol-li-guerra) |
| 2566 | 228369489 | 2026-07 | Alternatived Music | AM018__  Stan Garac - All About Meow | title | doble espacio | [↗](https://alternativedmusic.bandcamp.com/album/am018-stan-garac-all-about-meow) |
| 2567 | 3481102508 | 2026-07 | Alternatived Music | AM019__  ANDRSON - Used to Do | title | doble espacio | [↗](https://alternativedmusic.bandcamp.com/album/am019-andrson-used-to-do) |
| 2569 | 4038999666 | 2026-07 | Alternatived Music | AM021__  Charles Ramirez - Give it Up | title | doble espacio | [↗](https://alternativedmusic.bandcamp.com/album/am021-charles-ramirez-give-it-up) |
| 2570 | 2846285758 | 2026-07 | Alternatived Music | AM022__  ARATZH - I´M BACK | title | doble espacio | [↗](https://alternativedmusic.bandcamp.com/album/am022-aratzh-i-m-back) |
| 2571 | 674058937 | 2026-07 | Alternatived Music | AM023__  Stan Garac - Freaking Turntables | title | doble espacio | [↗](https://alternativedmusic.bandcamp.com/album/am023-stan-garac-freaking-turntables) |
| 2736 | 2748575918 | 2026-07 | Aterpe | Ez Zan Hil - 2 song  7" Inch Lathe Cut Txoriene Records 01 | title | doble espacio | [↗](https://aterpe.bandcamp.com/album/ez-zan-hil-2-song-7-inch-lathe-cut-txoriene-records-01) |
| 2737 | 3790131574 | 2026-07 | Various Artist tape compilation  Epilectic Media Records | Fast&Loud Epilectic Media Records various artists sampler | artist | doble espacio | [↗](https://aterpe.bandcamp.com/album/fast-loud-epilectic-media-records-various-artists-sampler) |
| 2986 | 4127068152 | 2026-07 | inoren ero  ni / lisabö | cOUPAGES #01 | artist | doble espacio | [↗](https://bidehuts.bandcamp.com/album/coupages-01) |
| 3108 | 4053269476 | 2026-07 | Bojaman, Kini DK, Beñaranks, Eira, Lua, Gustab, George Palmer, TalirasT, IbañezSound, | BOJAMAN - THE MEETING | artist | puntuación colgante | [↗](https://bojamanstyle.bandcamp.com/album/bojaman-the-meeting) |
| 3336 | 3089010054 | 2026-07 | CØRRUPT TRAX | Portage -  Vinyl Ride | title | doble espacio | [↗](https://corrupttrax.bandcamp.com/album/portage-vinyl-ride) |
| 3614 | 2449110766 | 2026-07 | Drumm&Cat | Drumm&cat-  Especie en extincion | title | doble espacio | [↗](https://drummandcat.bandcamp.com/album/drumm-cat-especie-en-extincion) |
| 4162 | 2696558397 | 2026-07 | HARDFLIP | Split  HF & HHD (2013ko Otsaila) | title | doble espacio | [↗](https://hardflip.bandcamp.com/album/split-hf-hhd-2013ko-otsaila) |
| 4270 | 371483084 | 2026-07 | Huracan  Rose | 5,04 | artist | doble espacio | [↗](https://huracanrose.bandcamp.com/album/504-2) |
| 4349 | 2535110334 | 2026-07 | Iker Munduate | .   .  . ... .  .   . | title | doble espacio | [↗](https://ikermunduate.bandcamp.com/album/-) |
| 4761 | 2139645594 | 2026-07 | JOXE CABALLERO | ZELAI  BERRIAK | title | doble espacio | [↗](https://joxecaballero.bandcamp.com/album/zelai-berriak) |
| 4768 | 1757298497 | 2026-07 | Juantxo Zeberio Etxetxipia | Eguberri Umama (Basque Christmas Songs)  Deluxe edition | title | doble espacio | [↗](https://juantxozeberioetxetxipia.bandcamp.com/album/eguberri-umama-basque-christmas-songs-deluxe-edition) |
| 5357 | 2747101219 | 2026-07 | Mike & Cara Gangloff | Mike & Cara Gangloff  "A Domestic Art" | title | doble espacio | [↗](https://makramerecords.bandcamp.com/album/mike-cara-gangloff-a-domestic-art) |
| 5502 | 1855873389 | 2026-07 | M E R Y  M A Y | Rue Matignon | artist | doble espacio | [↗](https://merymay.bandcamp.com/album/rue-matignon) |
| 5680 | 2639762978 | 2026-07 | MURGI | dUAL [1/2] :  GORDEKA | title | doble espacio | [↗](https://murgi.bandcamp.com/album/dual-1-2-gordeka) |
| 6208 | 1033400519 | 2026-07 | Petruska Records | PR020 / V/A LOCAL PUNK FOR GLOBAL CHAOS  feat. KOKOSHA GLAVA / KAOS KOOPERATIV / NOVI TSVETYA / THE PAUKI | title | doble espacio | [↗](https://petruskarecords.bandcamp.com/album/pr020-v-a-local-punk-for-global-chaos-feat-kokosha-glava-kaos-kooperativ-novi-tsvetya-the-pauki) |
| 7021 | 4174631765 | 2026-07 | Marcelino Gutierrez -  Iratxe Castrillo | La Linda Flor / Escenas | artist | doble espacio | [↗](https://tkuento.bandcamp.com/album/la-linda-flor-escenas) |
| 7263 | 3529421856 | 2026-07 | UYULALA | Safo  /’Σαπφώ/ | title | doble espacio | [↗](https://uyulala.bandcamp.com/album/safo) |
| 7360 | 2741279075 | 2026-07 | willis drummond | istanteak   (bIDEhUTS - 2011 // TRR 2016) | title | doble espacio | [↗](https://willisdrummond.bandcamp.com/album/istanteak-bidehuts-2011-trr-2016) |

<a id="genre_null"></a>
## `genre` null o vacío

**Recuento: 46 filas.**

| id | album_id | origen | artista | título | tags (primeros 4) | url |
|---|---|---|---|---|---|---|
| 43 | 2704024920 | orig. | Galder | Esc | — | [↗](https://forbiddencolours.bandcamp.com/album/esc) |
| 85 | 2391244327 | orig. | キマタジュン aka Jun Kimata | Shape Of My Voice | — | [↗](https://forbiddencolours.bandcamp.com/album/shape-of-my-voice) |
| 177 | 1913655492 | orig. | Ke Lepo | Izpi | — | [↗](https://forbiddencolours.bandcamp.com/album/izpi) |
| 234 | — | orig. | Elena Setién, GranDays & Xabier Erkizia | Mirande | — | — |
| 254 | 4291808219 | orig. | Xabier Zeberio | Pause | — | [↗](https://forbiddencolours.bandcamp.com/album/pause) |
| 361 | 1189147937 | orig. | Bruma | Far From Me | — | [↗](https://forbiddencolours.bandcamp.com/album/far-from-me) |
| 457 | 3615162349 | orig. | Ander Unzaga | // /// | — | [↗](https://forbiddencolours.bandcamp.com/album/--2) |
| 468 | 3440800652 | orig. | Dual Split | Brand New Rain | — | [↗](https://forbiddencolours.bandcamp.com/album/brand-new-rain) |
| 497 | 2095523926 | orig. | Sara Muñiz | Animus | — | [↗](https://forbiddencolours.bandcamp.com/album/animus) |
| 679 | 3974934473 | orig. | Yamila | Iras Fajro | — | [↗](https://forbiddencolours.bandcamp.com/album/iras-fajro) |
| 952 | 2383984186 | orig. | Andres Aguirre | Last Call | — | [↗](https://forbiddencolours.bandcamp.com/album/last-call) |
| 2611 | 2587664464 | 2026-07 | Andoni Etxebeste | Cartas a bamboo neko | classical, cinematic music, narrative music, orchestral music | [↗](https://andonietxebeste.bandcamp.com/album/cartas-a-bamboo-neko) |
| 3048 | 3137756616 | 2026-07 | Billy Prince | The Soulful Member of the Precisions - Live! Mojo Workin' 2016 | detroit, gure gauza, mojo workin festival, motown+ | [↗](https://billyprince.bandcamp.com/album/the-soulful-member-of-the-precisions-live-mojo-workin-2016) |
| 3338 | 1251126532 | 2026-07 | Arrotzak | Arrotzak | devotional, donostia | [↗](https://corsariosestudios.bandcamp.com/album/arrotzak) |
| 3340 | 1365582272 | 2026-07 | Cult Of Misery | Split 7" | devotional, donostia | [↗](https://corsariosestudios.bandcamp.com/album/split-7) |
| 3341 | 436489792 | 2026-07 | Ancient Emblem | Throne With No God | devotional, donostia | [↗](https://corsariosestudios.bandcamp.com/album/throne-with-no-god) |
| 3580 | 166416457 | 2026-07 | Dj Mau | Maumousse | r&b/soul, varios generos, hondarribia | [↗](https://djmau.bandcamp.com/album/maumousse) |
| 3581 | 2736138984 | 2026-07 | Dj Mau | Solo quiero ser tu amig@ | r&b/soul, varios generos, hondarribia | [↗](https://djmau.bandcamp.com/album/solo-quiero-ser-tu-amig) |
| 3866 | 785494255 | 2026-07 | Split // Estricalla + The Capaces | CRASS PUNK OUTSIDERS [2012] | devotional, euskal herria is not, spain | [↗](https://estricalla.bandcamp.com/album/crass-punk-outsiders-2012) |
| 3867 | 2850673776 | 2026-07 | Estricallla | DRAMATIK-THLON [2016] | devotional, euskal herria is not, spain | [↗](https://estricalla.bandcamp.com/album/dramatik-thlon-2016) |
| 3868 | 3385314639 | 2026-07 | Estricalla | FUEGOS OLIMPICOS [2011] | devotional, euskal herria is not, spain | [↗](https://estricalla.bandcamp.com/album/fuegos-olimpicos-2011) |
| 3869 | 3084651217 | 2026-07 | Estricalla | HUTSARTEA [2015] | devotional, euskal herria is not, spain | [↗](https://estricalla.bandcamp.com/album/hutsartea-2015) |
| 3870 | 4278253908 | 2026-07 | Estricalla | TRIPLE ASALTO MORTAL [2013] | devotional, euskal herria is not, spain | [↗](https://estricalla.bandcamp.com/album/triple-asalto-mortal-2013) |
| 3890 | 369652811 | 2026-07 | Eventónica | ITZALI EZIÑA inextinguible | classical, basque music, classical contemporary, contemporary classical | [↗](https://eventonica.bandcamp.com/album/itzali-ezi-a-inextinguible) |
| 3957 | 1881318840 | 2026-07 | Elena Setién, Grande Days & Xabier Erkizia | Mirande | bilbao | [↗](https://forbiddencolours.bandcamp.com/album/mirande) |
| 4549 | 1232947606 | 2026-07 | IZAR BELTZ LIBURUA | 28 ESCUPITAJOS DE SEMEN - Maketa Izar Beltz (2012) | bilbo | [↗](https://izarbeltzliburua.bandcamp.com/album/28-escupitajos-de-semen-maketa-izar-beltz-2012) |
| 4550 | 3178829621 | 2026-07 | IZAR BELTZ LIBURUA | 28 ESCUPITAJOS - Difundiendo valores, formando personas | bilbo | [↗](https://izarbeltzliburua.bandcamp.com/album/28-escupitajos-difundiendo-valores-formando-personas) |
| 4551 | 3943180271 | 2026-07 | IZAR BELTZ LIBURUA | BANDA SONORA - Márgen de error | bilbo | [↗](https://izarbeltzliburua.bandcamp.com/album/banda-sonora-m-rgen-de-error) |
| 4552 | 1211023118 | 2026-07 | IZAR BELTZ LIBURUA | DEPOSITO DE CADÁVERES - Vuestras ciudades | bilbo | [↗](https://izarbeltzliburua.bandcamp.com/album/deposito-de-cad-veres-vuestras-ciudades) |
| 4553 | 356969937 | 2026-07 | IZAR BELTZ LIBURUA | DEPOSITO DE CADAVERES - Estais muertos | bilbo | [↗](https://izarbeltzliburua.bandcamp.com/album/deposito-de-cadaveres-estais-muertos) |

*… y 16 más (solo se muestran 30).*

<a id="genre_vocab"></a>
## `genre` fuera del vocabulario

**Recuento: 0 filas.**

Sin casos.

<a id="tags_empty"></a>
## `tags` vacío

**Recuento: 30 filas.**

| id | album_id | origen | artista | título | genre | url |
|---|---|---|---|---|---|---|
| 43 | 2704024920 | orig. | Galder | Esc | null | [↗](https://forbiddencolours.bandcamp.com/album/esc) |
| 52 | 1407368718 | 2026-07 | Dj Rumaniak Presenta Lo Mejor del Balkan Klezmer Peninsular | Dj Rumaniak Presenta In Balkan Klezmer We Trust | world | [↗](https://bilbaobalkanbeatz.bandcamp.com/album/dj-rumaniak-presenta-in-balkan-klezmer-we-trust) |
| 85 | 2391244327 | orig. | キマタジュン aka Jun Kimata | Shape Of My Voice | null | [↗](https://forbiddencolours.bandcamp.com/album/shape-of-my-voice) |
| 103 | 2568623108 | orig. | Inshore, Costin Rp | The track is called Ep | electronic | [↗](https://samelevel.bandcamp.com/album/the-track-is-called-ep) |
| 107 | 1465008926 | 2026-07 | izena | Identikatea | rock | [↗](https://izena.bandcamp.com/album/identikatea) |
| 177 | 1913655492 | orig. | Ke Lepo | Izpi | null | [↗](https://forbiddencolours.bandcamp.com/album/izpi) |
| 234 | — | orig. | Elena Setién, GranDays & Xabier Erkizia | Mirande | null | — |
| 254 | 4291808219 | orig. | Xabier Zeberio | Pause | null | [↗](https://forbiddencolours.bandcamp.com/album/pause) |
| 283 | 1139911696 | 2026-07 | Abyme Nabar / Passion Farolas eta Mikel Lauki | ER051 Abyme Nabar & Passion Farolas eta Mikel Lauki - Split | electronic | [↗](https://eclecticreactionsrecords.bandcamp.com/album/er051-abyme-nabar-passion-farolas-eta-mikel-lauki-split) |
| 296 | 2871217733 | 2026-07 | Valerio Tricoli / Werner Dafeldecker / Mattin | ER044 Valerio Tricoli / Werner Dafeldecker / Mattin - Le Diable probablement | electronic | [↗](https://eclecticreactionsrecords.bandcamp.com/album/er044-valerio-tricoli-werner-dafeldecker-mattin-le-diable-probablement) |
| 321 | 368696371 | orig. | Zabala | Martian Civilization OST | ambient | [↗](https://forbiddencolours.bandcamp.com/album/martian-civilization-ost) |
| 325 | 3078021545 | 2026-07 | King Kong, Lone Ranger & Lone Ark Riddim Force | King Kong - Some A Dem Say / Lone Ranger - Jah A Me Saviour | reggae | [↗](https://bombbasshifi.bandcamp.com/album/king-kong-some-a-dem-say-lone-ranger-jah-a-me-saviour) |
| 348 | 4254839542 | 2026-07 | Horace Martin & Dub Crucials, Sammy Gold & Raggattack | Horace Martin - Dem Just a Push Me / Sammy Gold - Greatest Sound | reggae | [↗](https://bombbasshifi.bandcamp.com/album/horace-martin-dem-just-a-push-me-sammy-gold-greatest-sound) |
| 361 | 1189147937 | orig. | Bruma | Far From Me | null | [↗](https://forbiddencolours.bandcamp.com/album/far-from-me) |
| 372 | 2584462072 | orig. | Eduardo De La Calle | Colour Planet Corporation | electronic | [↗](https://forbiddencolours.bandcamp.com/album/colour-planet-corporation) |
| 457 | 3615162349 | orig. | Ander Unzaga | // /// | null | [↗](https://forbiddencolours.bandcamp.com/album/--2) |
| 468 | 3440800652 | orig. | Dual Split | Brand New Rain | null | [↗](https://forbiddencolours.bandcamp.com/album/brand-new-rain) |
| 497 | 2095523926 | orig. | Sara Muñiz | Animus | null | [↗](https://forbiddencolours.bandcamp.com/album/animus) |
| 679 | 3974934473 | orig. | Yamila | Iras Fajro | null | [↗](https://forbiddencolours.bandcamp.com/album/iras-fajro) |
| 708 | 655236709 | 2026-07 | GLYDAN | NEW EMOTIONS II | hip-hop/rap | [↗](https://glyyyydan.bandcamp.com/album/new-emotions-ii) |
| 715 | 337104022 | 2026-07 | Mikey Boy & The Yee-Haws | S/T | country | [↗](https://mikeyboyandtheyee-haws.bandcamp.com/album/s-t) |
| 952 | 2383984186 | orig. | Andres Aguirre | Last Call | null | [↗](https://forbiddencolours.bandcamp.com/album/last-call) |
| 991 | 3931382158 | 2026-07 | Joaquín Mendoza Sebastián | ER014 Joaquin Mendoza Sebastián - …everything about the beating of dead horses | electronic | [↗](https://eclecticreactionsrecords.bandcamp.com/album/er014-joaquin-mendoza-sebasti-n-everything-about-the-beating-of-dead-horses) |
| 1104 | 4236546462 | 2026-07 | Miusichole Recs. | Jon Koldo L. Salas - "Lanzando tus zapatos atados a un cable de la luz" (2013)- MH018 | alternative | [↗](https://miusichole.bandcamp.com/album/jon-koldo-l-salas-lanzando-tus-zapatos-atados-a-un-cable-de-la-luz-2013-mh018) |
| 1257 | — | orig. | MaBy Kerwin | Lofi Ninja | hip-hop/rap | — |
| 1538 | — | orig. | Monday Potions | Monday Potions - Sea Green | rock | — |
| 1539 | — | orig. | Monday Potions | Monday Potions - Floral White | rock | — |
| 1630 | — | orig. | J. Bilbao | All Life - Bizi Guztia | soundtrack | — |
| 1648 | 3894727503 | 2026-07 | GLYDAN | NEW EMOTIONS | hip-hop/rap | [↗](https://glyyyydan.bandcamp.com/album/new-emotions) |
| 2072 | 1454521486 | 2026-07 | artxanda | concierto en gaztelugatxe (edo 2017-2018 negua dezente latxa izan zan ta danok pixkat galdutago gaude) | folk | [↗](https://artxanda.bandcamp.com/album/concierto-en-gaztelugatxe-edo-2017-2018-negua-dezente-latxa-izan-zan-ta-danok-pixkat-galdutago-gaude) |

<a id="tags_dirty"></a>
## Tags sucios (vacíos, espacios, mayúsculas, puntuación colgante)

**Recuento: 32 filas.**

| id | album_id | origen | artista | título | tag | problema | url |
|---|---|---|---|---|---|---|---|
| 930 | 2094486891 | orig. | Lee Perk | Tumbleweed | pop music. | puntuación final | [↗](https://leeperk.bandcamp.com/album/tumbleweed) |
| 1397 | 3950606019 | orig. | FEROSZ | Blasphemer | metal melódico. | puntuación final | [↗](https://ferosz.bandcamp.com/album/blasphemer) |
| 1442 | 3297233913 | orig. | Lee Perk | The bloody vaults | pop music. | puntuación final | [↗](https://leeperk.bandcamp.com/album/the-bloody-vaults) |
| 1451 | 947743118 | orig. | Lee Perk | brand new records 2017 | pop music. | puntuación final | [↗](https://leeperk.bandcamp.com/album/brand-new-records-2017) |
| 2106 | 868319604 | 2026-07 | II | Y | beatz. | puntuación final | [↗](https://iikrisgm.bandcamp.com/album/y) |
| 2202 | 223515606 | orig. | Lee Perk | B-sides and rarities | pop music. | puntuación final | [↗](https://leeperk.bandcamp.com/album/b-sides-and-rarities) |
| 2853 | 203050501 | 2026-07 | The Chrome Cranks | Diabolical Boogie (3LP) | swamp blues noise... | puntuación final | [↗](https://bangrecords.bandcamp.com/album/diabolical-boogie-3lp) |
| 3159 | 3117411912 | 2026-07 | Bris | Hira | post punk. | puntuación final | [↗](https://briscorp.bandcamp.com/album/hira) |
| 3369 | 3495716917 | 2026-07 | Crownledge Collective | Ashes Of The Black Easter | inmersive. | puntuación final | [↗](https://crownledge.bandcamp.com/album/ashes-of-the-black-easter) |
| 3370 | 2102328704 | 2026-07 | Crownledge | Azaburu | inmersive. | puntuación final | [↗](https://crownledge.bandcamp.com/album/azaburu) |
| 3371 | 2808151512 | 2026-07 | Crownledge | Smrt fašizmu, sloboda narodu! | inmersive. | puntuación final | [↗](https://crownledge.bandcamp.com/album/smrt-fa-izmu-sloboda-narodu) |
| 4007 | 724520228 | 2026-07 | Gaueko Goñi | Future Architecture | thematic and programmatic music. | puntuación final | [↗](https://gauekogoni.bandcamp.com/album/future-architecture) |
| 4008 | 2296641436 | 2026-07 | Gaueko Goñi | Hijos del norte | thematic and programmatic music. | puntuación final | [↗](https://gauekogoni.bandcamp.com/album/hijos-del-norte) |
| 4009 | 3631223056 | 2026-07 | Gaueko Goñi | Inferno:Impromptu No.1,Op.1 | thematic and programmatic music. | puntuación final | [↗](https://gauekogoni.bandcamp.com/album/inferno-impromptu-no-1-op-1-4) |
| 4010 | 77074567 | 2026-07 | Gaueko Goñi | Interstellar Journey | thematic and programmatic music. | puntuación final | [↗](https://gauekogoni.bandcamp.com/album/interstellar-journey) |
| 4011 | 783406984 | 2026-07 | Gaueko Goñi | Música junto al fuego negro de invierno | thematic and programmatic music. | puntuación final | [↗](https://gauekogoni.bandcamp.com/album/m-sica-junto-al-fuego-negro-de-invierno) |
| 4012 | 873476638 | 2026-07 | Gaueko Goñi | The Anomaly Manor (Original Videogame Soundtrack) | thematic and programmatic music. | puntuación final | [↗](https://gauekogoni.bandcamp.com/album/the-anomaly-manor-original-videogame-soundtrack) |
| 5347 | 3832546990 | 2026-07 | Aum Sahib | Aum Sahib "The Formula of Atavistic Resurgence" | aum sahib. | puntuación final | [↗](https://makramerecords.bandcamp.com/album/aum-sahib-the-formula-of-atavistic-resurgence) |
| 5349 | 3957246561 | 2026-07 | Bolide | Bolide "The Last Thoughts of an Aqua Sabbat" | bolide. | puntuación final | [↗](https://makramerecords.bandcamp.com/album/bolide-the-last-thoughts-of-an-aqua-sabbat) |
| 5354 | 2525746403 | 2026-07 | J.Collin | J.Collin "Albert Road Room Odorisor" | j.collin. | puntuación final | [↗](https://makramerecords.bandcamp.com/album/j-collin-albert-road-room-odorisor) |
| 5358 | 3542484755 | 2026-07 | Pan del Indio | Pan del Indio "Un Disco" | pan del indio. | puntuación final | [↗](https://makramerecords.bandcamp.com/album/pan-del-indio-un-disco) |
| 5361 | 3604757740 | 2026-07 | Schrein | Schrein "Afternoon Shadows" | schrein. | puntuación final | [↗](https://makramerecords.bandcamp.com/album/schrein-afternoon-shadows) |
| 5363 | 2218362255 | 2026-07 | Uton | Uton "Say Hello to the Butterflies" | uton. | puntuación final | [↗](https://makramerecords.bandcamp.com/album/uton-say-hello-to-the-butterflies) |
| 5377 | 2685028423 | 2026-07 | Mamushka! | Maketa 1 | pop y lo que sea... | puntuación final | [↗](https://mamushkarock.bandcamp.com/album/maketa-1) |
| 5538 | 2305512722 | 2026-07 | Marian Gerrikabeitia | MINIMA EP | blues etc. | puntuación final | [↗](https://minima2.bandcamp.com/album/minima-ep) |
| 6128 | 309484152 | 2026-07 | Ozki | Ta orain zer? | ta orain zer? | puntuación final | [↗](https://ozki.bandcamp.com/album/ta-orain-zer) |
| 6200 | 1092386356 | 2026-07 | Petruska Records | PR012 SLEVY - Cuentos aquaticos | ??? | puntuación final | [↗](https://petruskarecords.bandcamp.com/album/pr012-slevy-cuentos-aquaticos) |
| 6936 | 1854574674 | 2026-07 | THE SOULBREAKER COMPANY | Graceless | ....... | puntuación final | [↗](https://thesoulbreakercompany.bandcamp.com/album/graceless) |
| 7353 | 3446549475 | 2026-07 | WILHELM | How High Lily? | how high lily? | puntuación final | [↗](https://wilhelmusic.bandcamp.com/album/how-high-lily) |
| 7376 | 1565886615 | 2026-07 | Xabi Guevara | Amapola | son. | puntuación final | [↗](https://xabiguevara.bandcamp.com/album/amapola) |

*… y 2 más (solo se muestran 30).*

<a id="tag_variants"></a>
## Tags: variantes del mismo tag no cubiertas por `TAG_RENAMES` (informativo)

**Recuento: 182 grupos.**

Misma clave fuerte (sin acentos, espacios, guiones ni puntuación). El pipeline ya fusiona las variantes auditadas en la PR C; estas son las que quedan. Candidatas a `TAG_RENAMES`, pero la política de la PR C exige decidirlas una a una.

| id | album_id | origen | artista | título | variantes | url |
|---|---|---|---|---|---|---|
| 57 | 607295345 | orig. | REPRESION | Represion | `77 punk` (11), `77punk` (1) | [↗](https://crapouletrecords.bandcamp.com/album/represion) |
| 235 | 3452519598 | orig. | Brigada suicida | Sucias lenguas | `metalpunk` (15), `metal; punk` (1) | [↗](https://brigadasuicida.bandcamp.com/album/sucias-lenguas) |
| 333 | 2546932655 | orig. | Feline | FSR101 Feline - Feline (LP) | `after punk` (6), `afterpunk` (3) | [↗](https://familyspreerecordings.bandcamp.com/album/fsr101-feline-feline-lp) |
| 579 | 1303736141 | orig. | Incursed | Beer Bloodbath EP | `game of thrones` (1), `gameofthrones` (1) | [↗](https://incursed.bandcamp.com/album/beer-bloodbath-ep) |
| 1056 | 880511061 | orig. | Dr. Skyloop | Plex! | `sinth pop` (1), `sinthpop` (1) | [↗](https://drskyloop.bandcamp.com/album/plex) |
| 1920 | 1275663510 | orig. | Samuel Cano | veinte veinte | `post-folk` (6), `postfolk` (1) | [↗](https://samuelcano.bandcamp.com/album/veinte-veinte) |
| 2190 | 490265248 | 2026-07 | II | OO | `modular synth` (1), `modularsynth` (1) | [↗](https://iikrisgm.bandcamp.com/album/oo) |
| 2255 | 1771951307 | orig. | KRAKENS | KRAKENS | `new orleans` (2), `neworleans⚜️` (1) | [↗](https://krakens.bandcamp.com/album/krakens) |
| 2280 | 3378561365 | orig. | Distrito suicida | 24 pasos hacia la locura | `rock punk` (1), `rock-punk` (1) | [↗](https://distritosuicida.bandcamp.com/album/24-pasos-hacia-la-locura) |
| 2407 | 2400817006 | 2026-07 | 25th coming fire + Zinc | 25th coming fire / Zinc | `old school` (15), `old_school` (7) | [↗](https://25thcomingfire.bandcamp.com/album/25th-coming-fire-zinc) |
| 2436 | 2943534057 | 2026-07 | abereh | Logela Sessions | `alt folk` (1), `alt-folk` (1) | [↗](https://abereh.bandcamp.com/album/logela-sessions) |
| 2445 | 269892546 | 2026-07 | The Dealers | Turning Upside Down | `rnb` (5), `r'n'b` (3) | [↗](https://actionweekend.bandcamp.com/album/turning-upside-down) |
| 2461 | 3976218622 | 2026-07 | Adiktos Al Kaos | Territorio Hostil | `rock'n'speed` (5), `rock´n´speed` (1) | [↗](https://adiktosalkaos.bandcamp.com/album/territorio-hostil) |
| 2462 | 942963498 | 2026-07 | Adrenalized | Docet Umbra | `skate punk` (17), `skatepunk` (15) | [↗](https://adrenalized.bandcamp.com/album/docet-umbra) |
| 2473 | 1115931345 | 2026-07 | Hurricane Studio & Afrihooop | African FemMc's Vol 1 | `underground hip hop` (31), `underground hip-hop` (7), `underground hiphop` (4) | [↗](https://afrihooop.bandcamp.com/album/african-femmcs-vol-1) |
| 2515 | 350939189 | 2026-07 | Aitor Suarez | Syberia Urbexplay (Original Soundtrack) | `film score` (5), `filmscore` (2) | [↗](https://aitorsu.bandcamp.com/album/syberia-urbexplay-original-soundtrack) |
| 2515 | 350939189 | 2026-07 | Aitor Suarez | Syberia Urbexplay (Original Soundtrack) | `videogame music` (8), `videogamemusic` (1) | [↗](https://aitorsu.bandcamp.com/album/syberia-urbexplay-original-soundtrack) |
| 2528 | 450660096 | 2026-07 | Alain Concepción | R | `aor` (8), `a.o.r` (1), `a.o.r.` (1) | [↗](https://alainconcepcion.bandcamp.com/album/r) |
| 2543 | 3022832892 | 2026-07 | Alitruta | La ciudad sigue dormida ( Tus manos y el mundo) | `krautrock` (22), `kraut rock` (3) | [↗](https://alitruta.bandcamp.com/album/la-ciudad-sigue-dormida-tus-manos-y-el-mundo) |
| 2613 | 465479922 | 2026-07 | A.Klee & Gab | FULGOR | `chill hop` (1), `chillhop` (1) | [↗](https://andreiklee.bandcamp.com/album/fulgor) |
| 2624 | 46495773 | 2026-07 | ANIMA | Anima EP | `heavy metal` (102), `heavymetal` (12) | [↗](https://animametalband.bandcamp.com/album/anima-ep) |
| 2670 | 71541519 | 2026-07 | Aquí y ahora | Auge y ocaso del hemisferio accidental EP | `montreal` (4), `montréal` (1) | [↗](https://aquiahora.bandcamp.com/album/auge-y-ocaso-del-hemisferio-accidental-ep) |
| 2679 | 2449937471 | 2026-07 | Arbusto Crower | Pragmasónico | `electro urbano` (1), `electrourbano` (1) | [↗](https://arbustocrower.bandcamp.com/album/pragmas-nico) |
| 2734 | 2841165389 | 2026-07 | Various Artists 7 inch Compilation | CONTINUUM.35-V/A "Tunes From The Toilet Vol.2" 57 Bands 7” Compilation (Ltd. to 300 copies) | `hc . punk` (1), `hc punk` (1) | [↗](https://aterpe.bandcamp.com/album/c-ontinuum-35-v-a-tunes-from-the-toilet-vol-2-57-bands-7-compilation-ltd-to-300-copies) |
| 2739 | 1579349976 | 2026-07 | Atmospheric Drum & Bass | Atmospheric Drum & Bass, Volume 6 | `spoken word` (25), `spokenword` (1) | [↗](https://atmosphericdrumbass.bandcamp.com/album/atmospheric-drum-bass-volume-6-2) |
| 2740 | 2408179960 | 2026-07 | Atodamadre | #TIRALOPATRA | `baile funk` (1), `bailefunk` (1) | [↗](https://atodamadre.bandcamp.com/album/tiralopatra) |
| 2772 | 99445156 | 2026-07 | Azken Sustraiak | Goierri | `oi! punk` (8), `oi!punk` (4) | [↗](https://azkensustraiak.bandcamp.com/album/goierri) |
| 2773 | 384055295 | 2026-07 | Unai Azkune | Abesti bat herri bat izan daiteke | `electric guitar` (5), `electricguitar` (1) | [↗](https://azkune.bandcamp.com/album/abesti-bat-herri-bat-izan-daiteke) |
| 2793 | 2641546772 | 2026-07 | Badmintones | Sinestarazi / Hutsune | `donostia san sebastián` (104), `donostia / san sebastián` (48), `donostia-san sebastian` (1) | [↗](https://badmintonestaldea.bandcamp.com/album/sinestarazi-hutsune) |
| 2880 | 194451364 | 2026-07 | Barraks Promotion | BP004 - Keziah "The Ocean Is Not Silent" (EP) | `post-metal` (40), `post metal` (7) | [↗](https://barraks.bandcamp.com/album/bp004-keziah-the-ocean-is-not-silent-ep) |

*… y 152 más (solo se muestran 30).*

<a id="url_dirty"></a>
## URLs sucias

**Recuento: 60 filas.**

`dominio no bandcamp.com`: cuentas con dominio propio (crudobilbao.com, ekiza.com…) ya verificadas como Bandcamp en auditorías anteriores; se listan para que quede constancia, no como error.

| id | album_id | origen | artista | título | problema | url |
|---|---|---|---|---|---|---|
| 29 | 3475529902 | orig. | Antxon Sagardui / Belén Natali / Illiam Keys | Loyal | dominio no bandcamp.com | [↗](https://crudobilbao.com/album/loyal) |
| 46 | 1665196553 | orig. | Antxon Sagardui | Sei Sor Gin | dominio no bandcamp.com | [↗](https://crudobilbao.com/album/sei-sor-gin) |
| 79 | 2796063736 | orig. | Antxon Sagardui | Neodymium Chapter II | dominio no bandcamp.com | [↗](https://crudobilbao.com/album/neodymium-chapter-ii) |
| 118 | 1221652230 | orig. | CrudoBilbao Dubbers & Shamann | Revelations | dominio no bandcamp.com | [↗](https://crudobilbao.com/album/revelations) |
| 124 | 1146225166 | orig. | Natty Nature | Bad Man Politics | dominio no bandcamp.com | [↗](https://crudobilbao.com/album/bad-man-politics) |
| 125 | 2652782821 | orig. | Sista Kata/ Illiam Keys/ Ka Dub | Give me the power | dominio no bandcamp.com | [↗](https://crudobilbao.com/album/give-me-the-power) |
| 133 | 2549793185 | orig. | CrudoBilbao Dubbers | [ODGP198] - Soundscapes | dominio no bandcamp.com | [↗](https://crudobilbao.com/album/odgp198-soundscapes) |
| 176 | 3333094601 | orig. | Antxon Sagardui, Tenor Brown | Water The Seed | dominio no bandcamp.com | [↗](https://crudobilbao.com/album/water-the-seed) |
| 183 | 2099000680 | orig. | Azùal Dub | Myths & Legends | dominio no bandcamp.com | [↗](https://crudobilbao.com/album/myths-legends) |
| 216 | 3196561150 | orig. | Antxon Sagardui, BassDefender | Ugari Geu | dominio no bandcamp.com | [↗](https://crudobilbao.com/album/ugari-geu) |
| 233 | 4085804521 | orig. | Antxon Sagardui & Kbless | Ilusiones | dominio no bandcamp.com | [↗](https://crudobilbao.com/album/ilusiones) |
| 242 | 3188240146 | orig. | Antxon Sagardui | Island Groove | dominio no bandcamp.com | [↗](https://crudobilbao.com/album/island-groove) |
| 272 | 230710054 | orig. | Azùal Dub | Incandescent World | dominio no bandcamp.com | [↗](https://crudobilbao.com/album/incandescent-world) |
| 298 | 3073746891 | orig. | Antxon Sagardui | Neodymium | dominio no bandcamp.com | [↗](https://crudobilbao.com/album/neodymium) |
| 300 | 1461986152 | orig. | BassDefender | Wilderness EP | dominio no bandcamp.com | [↗](https://crudobilbao.com/album/wilderness-ep) |
| 305 | 2359865751 | orig. | Antxon Sagardui | Water The Seed (Riddims) | dominio no bandcamp.com | [↗](https://crudobilbao.com/album/water-the-seed-riddims) |
| 324 | 2179407332 | orig. | Tenor youthman, Ranking Sepah | State Riddim | dominio no bandcamp.com | [↗](https://crudobilbao.com/album/state-riddim) |
| 335 | 4284326595 | orig. | Antxon Sagarui & Burian Fyah | New Lights | dominio no bandcamp.com | [↗](https://crudobilbao.com/album/new-lights) |
| 343 | 614267751 | orig. | BassDefender | Battle | dominio no bandcamp.com | [↗](https://crudobilbao.com/album/battle) |
| 354 | 1006183206 | orig. | Antxon Sagardui feat Isabel Sharpe | Mama Says | dominio no bandcamp.com | [↗](https://crudobilbao.com/album/mama-says) |
| 384 | 932611261 | orig. | Antxon Sagardui | Island Dub | dominio no bandcamp.com | [↗](https://crudobilbao.com/album/island-dub) |
| 397 | 1518405447 | orig. | BassDefender | The monster | dominio no bandcamp.com | [↗](https://crudobilbao.com/album/the-monster) |
| 427 | 3282409577 | orig. | Various Artists | One Year Compilation | dominio no bandcamp.com | [↗](https://wavememory.net/album/one-year-compilation) |
| 461 | 1910198580 | orig. | Q-Hork/ Antxon Sagardui | Sounds of Forest | dominio no bandcamp.com | [↗](https://crudobilbao.com/album/sounds-of-forest) |
| 474 | 2344703320 | orig. | Antxon Sagardui feat Don Camilo | Love is the answer | dominio no bandcamp.com | [↗](https://crudobilbao.com/album/love-is-the-answer) |
| 481 | 1251553879 | orig. | Antxon Sagardui & Friends | Remixes from Neodymium | dominio no bandcamp.com | [↗](https://crudobilbao.com/album/remixes-from-neodymium) |
| 493 | 4125443783 | orig. | BassDefender | Portuko Ranpi | dominio no bandcamp.com | [↗](https://crudobilbao.com/album/portuko-ranpi) |
| 501 | 1609686029 | orig. | HiGrade | Insanity | dominio no bandcamp.com | [↗](https://crudobilbao.com/album/insanity) |
| 514 | 2622669645 | orig. | BassDefender feat Yeyo Perez | Murderation/ Give dem shelter | dominio no bandcamp.com | [↗](https://crudobilbao.com/album/murderation-give-dem-shelter) |
| 521 | 3880066508 | orig. | Ka Dub & Ovella Negra | Dinasty | dominio no bandcamp.com | [↗](https://crudobilbao.com/album/dinasty) |

*… y 30 más (solo se muestran 30).*

<a id="url_null"></a>
## URL nula

**Recuento: 5 filas.**

| id | album_id | origen | artista | título | album_id | url |
|---|---|---|---|---|---|---|
| 234 | — | orig. | Elena Setién, GranDays & Xabier Erkizia | Mirande | None | — |
| 1257 | — | orig. | MaBy Kerwin | Lofi Ninja | None | — |
| 1538 | — | orig. | Monday Potions | Monday Potions - Sea Green | None | — |
| 1539 | — | orig. | Monday Potions | Monday Potions - Floral White | None | — |
| 1630 | — | orig. | J. Bilbao | All Life - Bizi Guztia | None | — |

<a id="year_null"></a>
## `year` vacío

**Recuento: 23 filas.**

| id | album_id | origen | artista | título | genre | url |
|---|---|---|---|---|---|---|
| 0 | 2842819630 | orig. | COBRA | Henko | rock | [↗](https://cobrarocks.bandcamp.com/album/henko) |
| 31 | 2568942792 | orig. | Lone Ark & Message | Singers & Players | reggae | [↗](https://bassleemusic.bandcamp.com/album/singers-players) |
| 52 | 1407368718 | 2026-07 | Dj Rumaniak Presenta Lo Mejor del Balkan Klezmer Peninsular | Dj Rumaniak Presenta In Balkan Klezmer We Trust | world | [↗](https://bilbaobalkanbeatz.bandcamp.com/album/dj-rumaniak-presenta-in-balkan-klezmer-we-trust) |
| 107 | 1465008926 | 2026-07 | izena | Identikatea | rock | [↗](https://izena.bandcamp.com/album/identikatea) |
| 234 | — | orig. | Elena Setién, GranDays & Xabier Erkizia | Mirande | null | — |
| 283 | 1139911696 | 2026-07 | Abyme Nabar / Passion Farolas eta Mikel Lauki | ER051 Abyme Nabar & Passion Farolas eta Mikel Lauki - Split | electronic | [↗](https://eclecticreactionsrecords.bandcamp.com/album/er051-abyme-nabar-passion-farolas-eta-mikel-lauki-split) |
| 296 | 2871217733 | 2026-07 | Valerio Tricoli / Werner Dafeldecker / Mattin | ER044 Valerio Tricoli / Werner Dafeldecker / Mattin - Le Diable probablement | electronic | [↗](https://eclecticreactionsrecords.bandcamp.com/album/er044-valerio-tricoli-werner-dafeldecker-mattin-le-diable-probablement) |
| 325 | 3078021545 | 2026-07 | King Kong, Lone Ranger & Lone Ark Riddim Force | King Kong - Some A Dem Say / Lone Ranger - Jah A Me Saviour | reggae | [↗](https://bombbasshifi.bandcamp.com/album/king-kong-some-a-dem-say-lone-ranger-jah-a-me-saviour) |
| 348 | 4254839542 | 2026-07 | Horace Martin & Dub Crucials, Sammy Gold & Raggattack | Horace Martin - Dem Just a Push Me / Sammy Gold - Greatest Sound | reggae | [↗](https://bombbasshifi.bandcamp.com/album/horace-martin-dem-just-a-push-me-sammy-gold-greatest-sound) |
| 708 | 655236709 | 2026-07 | GLYDAN | NEW EMOTIONS II | hip-hop/rap | [↗](https://glyyyydan.bandcamp.com/album/new-emotions-ii) |
| 715 | 337104022 | 2026-07 | Mikey Boy & The Yee-Haws | S/T | country | [↗](https://mikeyboyandtheyee-haws.bandcamp.com/album/s-t) |
| 991 | 3931382158 | 2026-07 | Joaquín Mendoza Sebastián | ER014 Joaquin Mendoza Sebastián - …everything about the beating of dead horses | electronic | [↗](https://eclecticreactionsrecords.bandcamp.com/album/er014-joaquin-mendoza-sebasti-n-everything-about-the-beating-of-dead-horses) |
| 1104 | 4236546462 | 2026-07 | Miusichole Recs. | Jon Koldo L. Salas - "Lanzando tus zapatos atados a un cable de la luz" (2013)- MH018 | alternative | [↗](https://miusichole.bandcamp.com/album/jon-koldo-l-salas-lanzando-tus-zapatos-atados-a-un-cable-de-la-luz-2013-mh018) |
| 1257 | — | orig. | MaBy Kerwin | Lofi Ninja | hip-hop/rap | — |
| 1270 | 3363103930 | orig. | lowveld | fifteen, seventy four [592, 951] | electronic | [↗](https://lowveld.bandcamp.com/album/fifteen-seventy-four-592-951) |
| 1538 | — | orig. | Monday Potions | Monday Potions - Sea Green | rock | — |
| 1539 | — | orig. | Monday Potions | Monday Potions - Floral White | rock | — |
| 1602 | 2827668889 | orig. | Titu Rodriguez Band | Cicatrices | rock | [↗](https://titurodriguezband.bandcamp.com/album/cicatrices) |
| 1630 | — | orig. | J. Bilbao | All Life - Bizi Guztia | soundtrack | — |
| 1648 | 3894727503 | 2026-07 | GLYDAN | NEW EMOTIONS | hip-hop/rap | [↗](https://glyyyydan.bandcamp.com/album/new-emotions) |
| 1868 | 3978347108 | orig. | Bulletnoise | Bulletnoise - EP | metal | [↗](https://bulletnoise.bandcamp.com/album/bulletnoise-ep) |
| 2072 | 1454521486 | 2026-07 | artxanda | concierto en gaztelugatxe (edo 2017-2018 negua dezente latxa izan zan ta danok pixkat galdutago gaude) | folk | [↗](https://artxanda.bandcamp.com/album/concierto-en-gaztelugatxe-edo-2017-2018-negua-dezente-latxa-izan-zan-ta-danok-pixkat-galdutago-gaude) |
| 2316 | 2183643888 | orig. | Aladino & His Friends | Death Sound Track | experimental | [↗](https://aladinoandhisfriends.bandcamp.com/album/death-sound-track) |

<a id="year_bad"></a>
## `year` imposible (< 1960 o > 2027)

**Recuento: 0 filas.**

Sin casos.

<a id="cover_null"></a>
## Portada vacía (`cover_url` null)

**Recuento: 15 filas.**

| id | album_id | origen | artista | título | album_id | url |
|---|---|---|---|---|---|---|
| 234 | — | orig. | Elena Setién, GranDays & Xabier Erkizia | Mirande | None | — |
| 318 | — | orig. | Lord Bakartia | About cursed water temples and colored crystals (MMXXV remaster) | None | [↗](https://lordbakartia.bandcamp.com/album/about-cursed-water-temples-and-colored-crystals-mmxxv-remaster) |
| 347 | — | orig. | Lord Bakartia | Demos I-II | None | [↗](https://lordbakartia.bandcamp.com/album/demos-i-ii) |
| 1257 | — | orig. | MaBy Kerwin | Lofi Ninja | None | — |
| 1413 | — | orig. | GORKA | Mundo Portátil | None | [↗](https://gorka.bandcamp.com/album/mundo-port-til) |
| 1528 | — | orig. | J. Bilbao | HEARTRENDING | None | [↗](https://asoundtrack.bandcamp.com/album/heartrending) |
| 1538 | — | orig. | Monday Potions | Monday Potions - Sea Green | None | — |
| 1539 | — | orig. | Monday Potions | Monday Potions - Floral White | None | — |
| 1566 | — | orig. | Dj Lobo EDM | Alice in WonderDance | None | [↗](https://djloboedm.bandcamp.com/album/alice-in-wonderdance) |
| 1608 | — | orig. | izena | izena | None | [↗](https://izena.bandcamp.com/album/izena) |
| 1630 | — | orig. | J. Bilbao | All Life - Bizi Guztia | None | — |
| 1631 | — | orig. | J. Bilbao | Quicksands | None | [↗](https://asoundtrack.bandcamp.com/album/quicksands) |
| 1696 | — | orig. | Narbaiz, Forlorn Prophecies, Vassal, Ilunabar, Lord Bakartia | Euskal Ziegetako Akelarrea | None | [↗](https://narbaiz.bandcamp.com/album/euskal-ziegetako-akelarrea) |
| 1748 | — | orig. | J. Bilbao | Sayari Hai (Living Planet) | None | [↗](https://asoundtrack.bandcamp.com/album/sayari-hai-living-planet) |
| 2292 | — | orig. | HUMANO | HUMANO | None | [↗](https://humano-ec.bandcamp.com/album/danza) |

<a id="cover_domain"></a>
## Portada fuera de bcbits.com

**Recuento: 0 filas.**

Sin casos.

<a id="album_id_null"></a>
## `album_id` nulo

**Recuento: 15 filas.**

| id | album_id | origen | artista | título | cover_url | url |
|---|---|---|---|---|---|---|
| 234 | — | orig. | Elena Setién, GranDays & Xabier Erkizia | Mirande | None | — |
| 318 | — | orig. | Lord Bakartia | About cursed water temples and colored crystals (MMXXV remaster) | None | [↗](https://lordbakartia.bandcamp.com/album/about-cursed-water-temples-and-colored-crystals-mmxxv-remaster) |
| 347 | — | orig. | Lord Bakartia | Demos I-II | None | [↗](https://lordbakartia.bandcamp.com/album/demos-i-ii) |
| 1257 | — | orig. | MaBy Kerwin | Lofi Ninja | None | — |
| 1413 | — | orig. | GORKA | Mundo Portátil | None | [↗](https://gorka.bandcamp.com/album/mundo-port-til) |
| 1528 | — | orig. | J. Bilbao | HEARTRENDING | None | [↗](https://asoundtrack.bandcamp.com/album/heartrending) |
| 1538 | — | orig. | Monday Potions | Monday Potions - Sea Green | None | — |
| 1539 | — | orig. | Monday Potions | Monday Potions - Floral White | None | — |
| 1566 | — | orig. | Dj Lobo EDM | Alice in WonderDance | None | [↗](https://djloboedm.bandcamp.com/album/alice-in-wonderdance) |
| 1608 | — | orig. | izena | izena | None | [↗](https://izena.bandcamp.com/album/izena) |
| 1630 | — | orig. | J. Bilbao | All Life - Bizi Guztia | None | — |
| 1631 | — | orig. | J. Bilbao | Quicksands | None | [↗](https://asoundtrack.bandcamp.com/album/quicksands) |
| 1696 | — | orig. | Narbaiz, Forlorn Prophecies, Vassal, Ilunabar, Lord Bakartia | Euskal Ziegetako Akelarrea | None | [↗](https://narbaiz.bandcamp.com/album/euskal-ziegetako-akelarrea) |
| 1748 | — | orig. | J. Bilbao | Sayari Hai (Living Planet) | None | [↗](https://asoundtrack.bandcamp.com/album/sayari-hai-living-planet) |
| 2292 | — | orig. | HUMANO | HUMANO | None | [↗](https://humano-ec.bandcamp.com/album/danza) |

<a id="title_prefix"></a>
## Títulos con el artista como prefijo («Artista - Título»)

**Recuento: 191 filas.**

Patrón P4 del sondeo de títulos (PR #49), dejado fuera a propósito de fix_artist_from_title.py. Informativo: quitar el prefijo sería un arreglo mecánico, pero el título es el que el artista puso en Bandcamp.

| id | album_id | origen | artista | título | problema | url |
|---|---|---|---|---|---|---|
| 9 | 1243416088 | orig. | WLDV | WLDV - A Demon Among Us | prefijo `WLDV - ` | [↗](https://wldv.bandcamp.com/album/wldv-a-demon-among-us) |
| 10 | 1976152780 | orig. | WLDV | WLDV - Blood Ceremony EP | prefijo `WLDV - ` | [↗](https://wldv.bandcamp.com/album/wldv-blood-ceremony-ep) |
| 17 | 3007267570 | orig. | WLDV | WLDV - Val And the Thief EP | prefijo `WLDV - ` | [↗](https://wldv.bandcamp.com/album/wldv-val-and-the-thief-ep) |
| 22 | 4057258264 | orig. | black insekt | black insekt - future kill \| polygon network [NW0074] | prefijo `black insekt - ` | [↗](https://polygonnetwork.bandcamp.com/album/black-insekt-future-kill-polygon-network-nw0074) |
| 24 | 2551805757 | orig. | WLDV | WLDV - Bewitched EP | prefijo `WLDV - ` | [↗](https://wldv.bandcamp.com/album/wldv-bewitched-ep) |
| 36 | 2770870287 | orig. | WLDV | WLDV - Primigenium EP | prefijo `WLDV - ` | [↗](https://wldv.bandcamp.com/album/wldv-primigenium-ep) |
| 88 | 701522284 | orig. | WLDV | WLDV - Bloodlust Dominion EP | prefijo `WLDV - ` | [↗](https://wldv.bandcamp.com/album/wldv-bloodlust-dominion-ep) |
| 95 | 753724967 | orig. | Ras Tekio | Ras Tekio - Hills Of Judah | prefijo `Ras Tekio - ` | [↗](https://sustraidunyouths.bandcamp.com/album/ras-tekio-hills-of-judah) |
| 109 | 4223303649 | orig. | WLDV | WLDV - From The Vault | prefijo `WLDV - ` | [↗](https://wldv.bandcamp.com/album/wldv-from-the-vault) |
| 122 | 2563474460 | orig. | 0N4B | 0N4B - dots \| polygon network [NW0007] | prefijo `0N4B - ` | [↗](https://polygonnetwork.bandcamp.com/album/0n4b-dots-polygon-network-nw0007) |
| 127 | 1082534791 | orig. | vortex count | vortex count - mantra \| polygon network [NW0066] | prefijo `vortex count - ` | [↗](https://polygonnetwork.bandcamp.com/album/vortex-count-mantra-polygon-network-nw0066) |
| 132 | 3385312159 | orig. | WLDV | WLDV - Black XX Plague EP | prefijo `WLDV - ` | [↗](https://wldv.bandcamp.com/album/wldv-black-xx-plague-ep) |
| 136 | 1416505145 | orig. | add obscurae | add obscurae - nonlinnear process \| polygon network [NW0065] | prefijo `add obscurae - ` | [↗](https://polygonnetwork.bandcamp.com/album/add-obscurae-nonlinnear-process-polygon-network-nw0065) |
| 145 | 869633404 | orig. | def. | def. - experiencia cercana a la vida \| polygon network [NW0034] | prefijo `def. - ` | [↗](https://polygonnetwork.bandcamp.com/album/def-experiencia-cercana-a-la-vida-polygon-network-nw0034) |
| 152 | 3191718365 | orig. | vortex count | vortex count - linnaean binomial \| polygon network [NW0033] | prefijo `vortex count - ` | [↗](https://polygonnetwork.bandcamp.com/album/vortex-count-linnaean-binomial-polygon-network-nw0033) |
| 158 | 2997231490 | orig. | WLDV | WLDV - Isolated EP | prefijo `WLDV - ` | [↗](https://wldv.bandcamp.com/album/wldv-isolated-ep) |
| 159 | 973947946 | orig. | WLDV | WLDV - Embraced By The Moon EP | prefijo `WLDV - ` | [↗](https://wldv.bandcamp.com/album/wldv-embraced-by-the-moon-ep) |
| 167 | 854433918 | orig. | WLDV | WLDV - The Blood And The Dagger EP | prefijo `WLDV - ` | [↗](https://wldv.bandcamp.com/album/wldv-the-blood-and-the-dagger-ep) |
| 173 | 2060627051 | orig. | WLDV | WLDV - Cult Liturgy EP | prefijo `WLDV - ` | [↗](https://wldv.bandcamp.com/album/wldv-cult-liturgy-ep) |
| 179 | 3331935061 | orig. | celine arnauld | celine arnauld - data control v1 \| polygon network [NW0069] | prefijo `celine arnauld - ` | [↗](https://polygonnetwork.bandcamp.com/album/celine-arnauld-data-control-v1-polygon-network-nw0069) |
| 185 | 4012274330 | orig. | WLDV | WLDV - Rise Of The Machines EP | prefijo `WLDV - ` | [↗](https://wldv.bandcamp.com/album/wldv-rise-of-the-machines-ep) |
| 192 | 2344138138 | orig. | WLDV | WLDV - Past Has Gone EP | prefijo `WLDV - ` | [↗](https://wldv.bandcamp.com/album/wldv-past-has-gone-ep) |
| 205 | 2675519908 | orig. | WLDV | WLDV - The Countess EP | prefijo `WLDV - ` | [↗](https://wldv.bandcamp.com/album/wldv-the-countess-ep) |
| 207 | 3499425380 | orig. | nuanae | nuanae - diorama \| polygon network [NW0057] | prefijo `nuanae - ` | [↗](https://polygonnetwork.bandcamp.com/album/nuanae-diorama-polygon-network-nw0057) |
| 208 | 1158008840 | orig. | seeker | seeker - espacio tiempo \| polygon network [NW0073] | prefijo `seeker - ` | [↗](https://polygonnetwork.bandcamp.com/album/seeker-espacio-tiempo-polygon-network-nw0073) |
| 211 | 108819394 | orig. | vortex count | vortex count - mantra remixed \| polygon network [NW0072] | prefijo `vortex count - ` | [↗](https://polygonnetwork.bandcamp.com/album/vortex-count-mantra-remixed-polygon-network-nw0072) |
| 224 | 947932996 | orig. | WLDV | WLDV - Malediction EP | prefijo `WLDV - ` | [↗](https://wldv.bandcamp.com/album/wldv-malediction-ep) |
| 238 | 759638299 | orig. | panopticum | panopticum - multisensory metaphors \| polygon network [NW0063] | prefijo `panopticum - ` | [↗](https://polygonnetwork.bandcamp.com/album/panopticum-multisensory-metaphors-polygon-network-nw0063) |
| 241 | 3383953089 | orig. | add obscurae | add obscurae - live from hangar 14 \| polygon network [NW0070] | prefijo `add obscurae - ` | [↗](https://polygonnetwork.bandcamp.com/album/add-obscurae-live-from-hangar-14-polygon-network-nw0070) |
| 246 | 744212845 | orig. | automatisme | automatisme - unlocked vol. 2 \| polygon network [NW0064] | prefijo `automatisme - ` | [↗](https://polygonnetwork.bandcamp.com/album/automatisme-unlocked-vol-2-polygon-network-nw0064) |

*… y 161 más (solo se muestran 30).*
