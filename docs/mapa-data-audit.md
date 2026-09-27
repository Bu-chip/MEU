# Auditoría del dataset de ubicaciones (fase 6)

*Generado por `python3 scripts/locations.py audit` a partir de `data/locations/resolutions.json`. No editar a mano.*

Recordatorio: la ubicación es la que Bandcamp da **hoy** a la cuenta que publica (grupo o sello). Estas cifras describen **el archivo**, no la escena ni la residencia histórica de nadie.

## Resumen

| | Releases | % |
|---|---:|---:|
| **Total** | 8046 | 100 % |
| direct — directa (Bandcamp, esta release) | 5419 | 67.4 % |
| same_account — misma cuenta de Bandcamp | 1484 | 18.4 % |
| artist_inferred — inferida por artista | 91 | 1.1 % |
| manual — manual | 0 | 0.0 % |
| region_only — solo región/país | 561 | 7.0 % |
| outside_scope — fuera de Euskal Herria | 288 | 3.6 % |
| tag_hint — solo pista de tag | 36 | 0.4 % |
| unresolved — sin resolver | 167 | 2.1 % |

- **En el mapa por defecto** (direct + same_account + artist_inferred + manual): **6994** (86.9 %).
- **Fiables** (Bandcamp de la propia cuenta o decisión manual, sin inferencia): **6903** (85.8 %).
- Situadas por la ubicación de una **cuenta con varios artistas** (probable sello, índice `data/derived/labels.json`): 2033. Su lugar es el de esa cuenta, no necesariamente el del grupo.
- **Sin municipio** en el mapa por defecto: **1052** (13.1 %); de ellas, 156 consultadas en Bandcamp sin ubicación.
- Sin resolver (167): 142 porque Bandcamp no da ubicación, 22 con evidencia descartada (ver abajo) y 3 sin evidencia.
- Municipios con al menos una release: **105**.
- Releases con contradicciones registradas: 40 (same_account 6, tag 31, tag_hints_multiple 3).

## Por territorio (mapa por defecto)

| Territorio | Releases |
|---|---:|
| Bizkaia | 3223 |
| Gipuzkoa | 2016 |
| Nafarroa | 1041 |
| Araba | 635 |
| Iparralde | 79 |

## Solo región (region_only)

| Región | Releases |
|---|---:|
| euskal-herria | 421 |
| france | 73 |
| spain | 40 |
| nafarroa | 13 |
| enkarterri | 8 |
| nouvelle-aquitaine | 4 |
| arratia-nerbioi | 2 |

## Por décadas (año de la release)

| Década | Localizadas | Sin municipio | % localizadas |
|---|---:|---:|---:|
| 1930s | 1 | 0 | 100.0 % |
| 1980s | 7 | 1 | 87.5 % |
| 1990s | 63 | 16 | 79.7 % |
| 2000s | 296 | 75 | 79.8 % |
| 2010s | 3172 | 465 | 87.2 % |
| 2020s | 3436 | 491 | 87.5 % |
| s/f | 19 | 4 | 82.6 % |

## Valores descartados (evidencia no aceptada)

| Texto crudo | Releases afectadas |
|---|---:|
| Afghanistan | 24 |
| Navarre, Florida | 13 |
| Pamplona, Colombia | 6 |
| Irun, Nigeria | 5 |
| Bayonne, New Jersey | 1 |
| Guernica, Argentina | 1 |
| PM | 1 |
| San Sebastián, Chile | 1 |

## Municipios

Tags sobrerrepresentados: `lift = (releases del municipio con el tag / releases del municipio) ÷ (releases del archivo con el tag / releases del archivo)`, con un mínimo de 3 releases del tag en el municipio y 10 en el archivo, sin contar tags que son topónimos.

| Municipio | Territorio | Releases | Artistas | Años | % cuenta multiartista | Tags principales | Sobrerrepresentados |
|---|---|---:|---:|---|---:|---|---|
| Bilbo | Bizkaia | 2609 | 1060 | 1992–2026 | 30 % | electronic (603), rock (552), experimental (404), metal (385), techno (361) | trance electro techno ×3.1, non-conventional ×3.1, poems ×3.1, sound textures ×3.1 |
| Donostia | Gipuzkoa | 1050 | 437 | 1937–2026 | 35 % | rock (330), electronic (294), experimental (197), punk (170), pop (153) | preqwal ×7.7, tony morton ×7.7, le mans ×7.7, matt o'brien ×7.7 |
| Iruñea | Nafarroa | 979 | 429 | 1993–2026 | 32 % | rock (283), electronic (213), techno (166), pop (155), metal (142) | primavera sound ×8.2, sonido muchacho ×8.2, vgm ×8.2, reverbcore ×8.2 |
| Gasteiz | Araba | 589 | 247 | 1997–2026 | 22 % | rock (148), metal (124), electronic (102), punk (94), black metal (79) | grove metal ×13.7, freakbeat ×13.7, minimal techno industrial ×13.7, senoid recordings ×13.7 |
| Zarautz | Gipuzkoa | 297 | 163 | 1989–2026 | 56 % | punk (123), hardcore (108), hardcore punk (107), crust punk (98), live (98) | live recording ×26.3, deep tech ×24.2, tropical ×23.9, crust punk ×21.9 |
| Irun | Gipuzkoa | 114 | 27 | 1997–2025 | 54 % | punk (75), punk rock (62), post-punk (59), hardcore (56), petruska records (28) | petruska records ×70.6, 77 punk ×70.6, 82 punk ×70.6, oi ×24.7 |
| Getxo | Bizkaia | 96 | 36 | 2004–2026 | 8 % | rock (49), indie rock (20), pop (18), alternative (16), acoustic (14) | hardrock ×69.8, heavymetal ×69.8, heavy rock ×33.5, shoegaze ×17.7 |
| Santurtzi | Bizkaia | 76 | 65 | 2012–2025 | 82 % | punk (67), metal (44), crust (40), death metal (40), grindcore (40) | oz rock ×105.9, swamp rock ×105.9, high energy rock ×88.2, blackened crust ×38.5 |
| Barakaldo | Bizkaia | 66 | 28 | 1991–2026 | 0 % | rock (36), punk (25), pop (10), punk rock (10), rock'n'roll (8) | rock alternative ×55.4, melodic metal ×33.9, remix ×33.2, retro ×31.8 |
| Hondarribia | Gipuzkoa | 62 | 26 | 2005–2026 | 0 % | rock (20), pop (14), hip-hop/rap (11), instrumental (8), punk (8) | stoner metal ×51.9, sludge metal ×30.5, acoustic rock ×25.9, underground ×22.2 |
| Errenteria | Gipuzkoa | 60 | 19 | 1992–2026 | 8 % | pop (30), digicore (25), glitch pop (25), hyper pop (25), internet music (25) | digicore ×134.1, internet music ×134.1, internetcore ×134.1, glitch pop ×128.9 |
| Arrasate | Gipuzkoa | 50 | 29 | 2010–2026 | 26 % | punk rock (26), rock (22), punk (17), metal (9), black metal (7) | metalpunk ×42.9, surf ×22.4, street punk ×14.6, punk rock ×7.8 |
| Bermeo | Bizkaia | 48 | 23 | 1994–2026 | 4 % | rock (29), punk (11), alternative (7), hard rock (7), hardcore (7) | punk-rock ×91.4, melodic rock ×52.9, euskal rock ×26.8, punk hardcore ×13.7 |
| Leioa | Bizkaia | 48 | 1 | 2017–2025 | 0 % | soundtrack (48), beats (2), cinematic (2), synthwave (2), 8bits (1) | soundtrack ×44.2 |
| Gernika-Lumo | Bizkaia | 47 | 18 | 2003–2026 | 4 % | punk (13), metal (12), rock (12), hardcore (11), alternative (8) | extreme metal ×57.1, melodic metal ×47.5, acoustic guitar ×25.4, afghanistan ×20.5 |
| Eibar | Gipuzkoa | 41 | 14 | 2009–2025 | 5 % | rock (16), electronic (11), ambient electronic (10), bidehuts (8), metal (7) | comedy ×61.3, soundscapes ×60.4, ambient electronic ×53.0, groove metal ×28.0 |
| Portugalete | Bizkaia | 41 | 25 | 2008–2026 | 61 % | electronic (17), hip hop (16), beattape (15), world beats (15), rock (12) | beattape ×196.2, world beats ×196.2, kraut ×45.3, soft rock ×45.3 |
| Ondarroa | Bizkaia | 40 | 15 | 1998–2026 | 28 % | rock (25), pop rock (15), alternative (12), euskal musika (9), folk (9) | fastcore ×50.3, powerviolence ×35.0, euskal musika ×17.2, screamo ×14.6 |
| Tolosa | Gipuzkoa | 38 | 16 | 1998–2025 | 0 % | rock (13), punk (12), grindcore (8), metal (8), crust (7) | raggamuffin ×31.8, dancehall ×11.8, crust ×10.7, psychedelic ×9.1 |
| Oiartzun | Gipuzkoa | 35 | 15 | 2004–2024 | 23 % | punk (14), hip-hop/rap (11), rap (11), hip hop (9), hardcore (8) | oi ×92.0, occitan ×69.0, street punk ×41.8, trap ×25.9 |
| Andoain | Gipuzkoa | 33 | 14 | 1983–2026 | 42 % | rock (19), pop (14), soul (14), electronic (9), experimental (9) | flamenco ×142.2, fantasy ×109.7, horror ×64.5, euskaraz ×26.1 |
| Hernani | Gipuzkoa | 32 | 14 | 2005–2026 | 12 % | punk (14), rock (11), oi! (10), oi! streetpunk (8), skinhead (8) | oi! streetpunk ×201.2, skinhead ×64.9, oi! ×27.0, instrumental ×8.4 |
| Oñati | Gipuzkoa | 31 | 19 | 2012–2026 | 6 % | rock (16), alternative (7), punk (6), post-hardcore (4), 70s (3) | free jazz ×10.8, post-hardcore ×4.7, hardcore punk ×2.7, post-punk ×2.4 |
| Tutera | Nafarroa | 24 | 14 | 2010–2023 | 0 % | rock (15), alternative (9), hard rock (8), rock and roll (5), folk (4) | rock alternativo ×61.0, surf rock ×46.2, garage rock ×27.9, hard rock ×14.7 |
| Zumaia | Gipuzkoa | 23 | 9 | 2014–2026 | 0 % | rock (13), experimental (8), rock & roll (6), blues (5), blues rock (5) | blues rock ×38.0, rock & roll ×14.1, blues ×12.8, stoner ×11.4 |
| Laudio | Araba | 22 | 13 | 2001–2026 | 18 % | rock (8), post-rock (5), acoustic (4), alternative rock; laudio (4), cantautor (4) | folk pop ×48.8, cantautor ×28.1, post-rock ×11.5, post-hardcore ×6.6 |
| Mungia | Bizkaia | 21 | 8 | 1994–2026 | 0 % | melodic hardcore (9), punk (9), skatepunk (9), alternative (6), pop (4) | skatepunk ×181.5, melodic hardcore ×65.1, indie ×4.0, punk ×2.4 |
| Azpeitia | Gipuzkoa | 19 | 11 | 2006–2026 | 16 % | punk (7), rock (6), street punk (4), alternative (3), hardcore punk (3) | street punk ×38.5, hardcore punk ×4.5, punk ×2.0, alternative ×1.2 |
| Sopela | Bizkaia | 19 | 3 | 2010–2021 | 5 % | doom (18), hardcore (18), metal (17), sludge (17), stoner (13) | sludge ×76.6, doom ×60.0, stoner ×59.8, hardcore ×11.4 |
| Ermua | Bizkaia | 17 | 9 | 2006–2025 | 0 % | rock (8), metal (4), punk (4), alternative (3), diy (3) | diy ×14.8, rock ×1.8, metal ×1.7, alternative ×1.4 |
| Lekeitio | Bizkaia | 17 | 7 | 2010–2026 | 47 % | cloud rap (6), hip hop (6), hip-hop/rap (6), rap (6), trap (6) | trap ×40.0, rap ×12.1, hip hop ×10.9, hip-hop/rap ×9.4 |
| Bergara | Gipuzkoa | 16 | 10 | 2011–2024 | 25 % | punk (8), hardcore (7), punk rock (7), rock (5), euskera (4) | skate punk ×88.7, euskera ×35.3, metalcore ×13.7, post-hardcore ×9.1 |
| Mendaro | Gipuzkoa | 15 | 2 | 2003–2026 | 0 % | electronica (10), indie (10), punk (10), rock (10), ambient (7) | devotional ×58.3, electronica ×23.9, indie ×18.7, alternative rock ×9.9 |
| Baiona | Iparralde | 14 | 5 | 2007–2024 | 0 % | alternative (9), rock (6), bidehuts (4), drummond (4), italo noise (4) | bidehuts ×33.8, hardcore punk ×6.0, alternative ×5.1, hardcore ×2.6 |
| Urretxu | Gipuzkoa | 14 | 5 | 1994–2023 | 0 % | rock (12), hard rock (7), blues rock (6), country (6), rock and roll (6) | blues rock ×75.0, alternative pop ×47.9, indie folk ×46.9, country ×41.5 |
| Hendaia | Iparralde | 13 | 4 | 2005–2026 | 0 % | rock (10), rock compilation (10), alternative (2), antzerkia (1), electronic (1) | rock compilation ×618.9, rock ×2.9 |
| Kanbo | Iparralde | 13 | 13 | 2019–2024 | 100 % | belarri (13), euskal musika (13), musika (13), world (13), contemporary (2) | belarri ×618.9, musika ×402.3, euskal musika ×76.6, world ×37.8 |
| Amurrio | Araba | 12 | 9 | 2008–2026 | 33 % | metal (5), alternative (4), crossover (4), groove metal (4), hardcore (4) | crossover ×83.8, groove metal ×76.6, hardcore ×4.0, metal ×3.0 |
| Basauri | Bizkaia | 12 | 5 | 2009–2025 | 0 % | punk (8), hardcore punk (4), rock (4), punk hardcore (3), punk rock (3) | skate punk ×118.3, skatepunk ×105.9, punk hardcore ×41.0, hardcore punk ×9.4 |
| Legazpi | Gipuzkoa | 12 | 3 | 2007–2024 | 0 % | bloody rock (6), hard rock (6), high energy rock'n'roll (6), metal (6), punk rock (6) | high energy rock'n'roll ×402.3, groove metal ×57.5, hard rock ×22.0, punk rock ×7.5 |
| Lekunberri | Nafarroa | 12 | 2 | 2001–2017 | 0 % | lekunberri (12), indie (11), metal (11), punk (11), punk rock (11) | lekunberri ×670.5, indie ×25.7, punk rock ×13.8, metal ×6.6 |
| Berriz | Bizkaia | 11 | 4 | 2010–2024 | 0 % | ambient (5), electronic (5), experimental (5), hardcore (5), idm (5) | idm ×24.7, industrial ×19.7, noise ×11.0, ambient ×6.3 |
| Zaldibia | Gipuzkoa | 10 | 1 | 2014–2026 | 0 % | acoustic (10), bertsioak (10), covers (10), q ez da (10), version (10) | bertsioak ×804.6, q ez da ×804.6, version ×574.7, covers ×502.9 |
| Bera | Nafarroa | 9 | 4 | 2012–2022 | 0 % | alternative (7), alternative rock (7), rock (2), 90s rock (1), angry (1) | alternative rock ×23.1, alternative ×6.1 |
| Itsasu | Iparralde | 9 | 2 | 2020–2025 | 100 % | alternative (9), basque music (9), eklektrik (9), pop rock (9), txomin larronde (9) | basque music ×52.6, pop rock ×29.1, alternative ×7.9 |
| Zumarraga | Gipuzkoa | 9 | 3 | 2004–2023 | 0 % | punk (5), punk rock (5), rock (5), rock'n'speed (5), death metal (3) | melodic death metal ×47.0, death metal ×9.2, punk rock ×8.4, punk ×3.1 |
| Arrigorriaga | Bizkaia | 8 | 1 | 2020–2025 | 0 % | basque music (8), death metal (8), heavy metal (8), metal (8), thrash metal (8) | thrash metal ×78.1, heavy metal ×73.8, basque music ×52.6, death metal ×27.6 |
| Sestao | Bizkaia | 8 | 6 | 2012–2024 | 50 % | electro glam (4), electronic (4), techno house (4), techno punk (4), metal (3) | rapmetal ×177.5, metal ×2.7, electronic ×2.7 |
| Hazparne | Iparralde | 7 | 3 | 2012–2025 | 0 % | folk (6), alternative (5), grunge (5), indie (5), basque music (2) | grunge ×51.3, indie ×20.0, folk ×15.7, alternative ×5.6 |
| Lasarte-Oria | Gipuzkoa | 7 | 5 | 2010–2024 | 0 % | alternative (2), black metal (2), death metal (2), euskal musika (2), metal (2) |  |
| Markina-Xemein | Bizkaia | 7 | 1 | 2014–2019 | 0 % | electronic (7), electronic rock (7), indie rock (7), rock (7), indie electronic rock (1) | electronic rock ×502.9, indie rock ×32.7, electronic ×5.4, rock ×3.7 |
| Moreda Araba | Araba | 7 | 1 | 2011–2018 | 0 % | blues (7), punk (7), rock (7), bluespunk (1), pop (1) | blues ×58.7, punk ×5.6, rock ×3.7 |
| Galdakao | Bizkaia | 6 | 5 | 2015–2025 | 0 % | punk (4), punk rock (3), melodic hardcore (2), metal (2), post-hardcore (2) | punk rock ×7.5, punk ×3.7 |
| Ispaster | Bizkaia | 6 | 1 | 2012–2017 | 0 % | alternative (6), beruna (6), crust (6), doom (6), sludge (6) | sludge ×85.6, doom ×63.4, crust ×58.3, alternative ×7.9 |
| Urnieta | Gipuzkoa | 6 | 1 | 2007–2014 | 0 % | post-hardcore (6), punk rock (6), rock (6), pop (2), alternative metal (1) | post-hardcore ×36.4, punk rock ×15.1, rock ×3.7 |
| Villabona-Amasa | Gipuzkoa | 6 | 2 | 2019–2023 | 0 % | rock (6), alternative rock (4), ambient rock (4), melodic rock (4), basque music (3) | melodic rock ×282.3, ambient rock ×223.5, grunge ×35.9, basque music ×26.3 |
| Beasain | Gipuzkoa | 5 | 2 | 2017–2023 | 0 % | punk (4), punk rock (4), rock (2), acoustic (1), acustic (1) | punk rock ×12.1, punk ×4.5 |
| Elgoibar | Gipuzkoa | 5 | 1 | 2006–2013 | 0 % | acoustic (5), folk (5), rock (5), acoustic rock (1), eh (1) | acoustic ×31.8, folk ×18.3, rock ×3.7 |
| Getaria | Gipuzkoa | 5 | 3 | 2021–2026 | 0 % | getaria (5), punk (5), hardcore (3), punk rock (3), hardcore punk (2) | getaria ×804.6, punk rock ×9.0, hardcore ×7.2, punk ×5.6 |
| Orio | Gipuzkoa | 5 | 2 | 2011–2021 | 0 % | rock (5), ambient (4), experimental (4), instrumental (4), math-rock (4) | instrumental ×43.2, post-rock ×40.5, ambient ×11.1, experimental ×7.0 |
| Abadiño | Bizkaia | 4 | 1 | 2010–2024 | 0 % | black metal (4), dark power metal (4), death metal (4), metal (4), power metal (4) | power metal ×187.1, black metal ×29.3, death metal ×27.6, metal ×7.2 |
| Donibane Lohizune | Iparralde | 4 | 4 | 2015–2017 | 75 % | electric human machines (3), electronic (3), experimental easy listening (3), baleapop (2), beleak (1) | electronic ×4.1 |
| Elortzibar | Nafarroa | 4 | 1 | 2010–2015 | 0 % | noáin, navarra (4), punk (4), punk-oi (1), punkoi (1) | punk ×5.6 |
| Azkoitia | Gipuzkoa | 3 | 2 | 2016–2025 | 0 % | hardcore (3), rock (3), hard rock (2), metal (2), punk (2) | hardcore ×12.0, rock ×3.7 |
| Biarritz | Iparralde | 3 | 3 | 2011–2020 | 0 % | world (2), acoustic rock (1), andoken (1), bask and world music (1), boom bap (1) |  |
| Legutio | Araba | 3 | 1 | 2013–2020 | 0 % | hardcore punk (3), punk (3), punk oi! (3), street punk (3) | punk oi! ×804.6, street punk ×182.9, hardcore punk ×28.2, punk ×5.6 |
| Maule-Lextarre | Iparralde | 3 | 1 | 2018–2025 | 0 % | dub (3), ragga (3), raggamuffin (3), reggae (3), roots (3) | ragga ×670.5, raggamuffin ×402.3, roots ×75.9, dub ×32.7 |
| Zaldibar | Bizkaia | 3 | 1 | 2023–2026 | 0 % | alternative (3), basque music (3), pop (3), post-punk (3) | basque music ×52.6, post-punk ×24.3, pop ×9.9, alternative ×7.9 |
| Altsasu | Nafarroa | 2 | 1 | 2023–2023 | 0 % | d-beat (2), punk (2), album (1), disasko (1), disbrigade (1) |  |
| Aramaio | Araba | 2 | 1 | 2019–2021 | 0 % | rock (2), rock'n'roll (2), album release (1), basque music (1), basque rock alternative (1) |  |
| Azkaine | Iparralde | 2 | 1 | 2015–2018 | 0 % | alternative (2), doom (2), noise (2), post-rock (2), stoner (2) |  |
| Baigorri | Iparralde | 2 | 1 | 2016–2018 | 0 % | black metal (2), medieval (2), metal (2), dark medieval (1), history (1) |  |
| Bastida | Iparralde | 2 | 1 | 2021–2026 | 0 % | alternative (2), female vocals (2), strings (2), traditional (2), traditional jazz (2) |  |
| Deba | Gipuzkoa | 2 | 2 | 2022–2024 | 100 % | aitor huergo (2), barruko (2), euskal (2), folk (2), paisaiak (2) |  |
| Durango | Bizkaia | 2 | 2 | 2012–2020 | 50 % | boom-bap (1), euskera (1), funk (1), hard rock (1), hip-hop/rap (1) |  |
| Elorrio | Bizkaia | 2 | 1 | 2010–2013 | 0 % | rock (2), rock roll punk-rock-stoner (2), sermonds (2) |  |
| Eskoriatza | Gipuzkoa | 2 | 1 | 2005–2013 | 0 % | hardcore (2), hardcore punk (2), punk (2) |  |
| Irulegi | Iparralde | 2 | 1 | 2019–2024 | 0 % | basque music (2), euskal kantagintza (2), euskal musika (2), folk (2) |  |
| Martzilla | Nafarroa | 2 | 1 | 2020–2021 | 0 % | pop rock (2), rock (2), txente (2) |  |
| Otxandio | Bizkaia | 2 | 1 | 2023–2025 | 0 % | alternative (2), euskera (2), oi! (2), punk (2), punk rock (2) |  |
| Soraluze | Gipuzkoa | 2 | 2 | 2011–2012 | 0 % | blues (1), country (1), metal (1), metal progresivo (1), progressive metal (1) |  |
| Suhuskune | Iparralde | 2 | 1 | 2018–2020 | 0 % | duo (2), euskara (2), euskaraz (2), heavy blues rock (2), power duo (2) |  |
| Zestoa | Gipuzkoa | 2 | 1 | 2013–2017 | 0 % | acoustic (2), africa (2), euskara (2), kora (2), strings (2) |  |
| Zizur Nagusia | Nafarroa | 2 | 2 | 2022–2025 | 0 % | electronic (2), electronica (2), techno (2), techno; downtempo; electro (2), davma (1) |  |
| Zornotza | Bizkaia | 2 | 2 | 2012–2016 | 0 % | hip hop (2), hip-hop/rap (2), pablo gil aguirre (2), ronda (2) |  |
| Ainhize-Monjolose | Iparralde | 1 | 1 | 2016–2016 | 0 % | bilau (1), euskal musika (1), experimental (1), folk minimal (1), ghostfolk (1) |  |
| Angelu | Iparralde | 1 | 1 | 2025–2025 | 0 % | chant (1), gascon (1), polyphonie (1), traditionnel (1), world (1) |  |
| Arellano | Nafarroa | 1 | 1 | 2015–2015 | 0 % | balcan (1), ska (1), tango (1), tumbao (1), world (1) |  |
| Aretxabaleta | Gipuzkoa | 1 | 1 | 2025–2025 | 0 % | euskal musika (1), nhil (1), nhilband (1), pop (1), soul (1) |  |
| Berango | Bizkaia | 1 | 1 | 2025–2025 | 0 % | alternative pop rock (1), basque rock alternative (1), pop (1), psychopunk (1), rock (1) |  |
| Burlata | Nafarroa | 1 | 1 | 2018–2018 | 0 % | euskara (1), hardcore (1), metal (1), thrash metal (1) |  |
| Donibane Garazi | Iparralde | 1 | 1 | 2017–2017 | 0 % | alternative rock (1), bass (1), drums (1), duo (1), euskal (1) |  |
| Erandio | Bizkaia | 1 | 1 | 2015–2015 | 0 % | metal (1), rock (1), scandinavian (1), skate (1) |  |
| Legorreta | Gipuzkoa | 1 | 1 | 2012–2012 | 0 % | punk (1), punk-rock (1) |  |
| Lizarra | Nafarroa | 1 | 1 | 2024–2024 | 0 % | alternative (1), folk (1), songwriter (1) |  |
| Mundaka | Bizkaia | 1 | 1 | 2012–2012 | 0 % | hau ez dek (1), mala ostia (1), punk (1) |  |
| Mutriku | Gipuzkoa | 1 | 1 | 2013–2013 | 0 % | beat (1), hip hop (1), hip hop instrumentals (1), hip hop soul (1), hip-hop/rap (1) |  |
| San Adrián | Nafarroa | 1 | 1 | 2016–2016 | 0 % | blues (1), humor (1), rock and roll (1), show (1) |  |
| Tafalla | Nafarroa | 1 | 1 | 2021–2021 | 0 % | acoustic (1), classical (1), new age (1), new age music (1), piano solo (1) |  |
| Trapagaran | Bizkaia | 1 | 1 | 2020–2020 | 0 % | basque music (1), doom (1), metal (1), rock (1), shaman (1) |  |
| Untzue | Nafarroa | 1 | 1 | 2021–2021 | 0 % | diy (1), etxekopunk (1), garage (1), punk (1), rural streetpunk (1) |  |
| Urdazubi | Nafarroa | 1 | 1 | 2022–2022 | 0 % | euskal rock (1), hard rock (1), kamuts (1), rock (1) |  |
| Usurbil | Gipuzkoa | 1 | 1 | 2024–2024 | 0 % | electronic (1), euskaraz (1), pop (1), rap (1), rock (1) |  |
| Zaratamo | Bizkaia | 1 | 1 | 2019–2019 | 0 % | kon (1), perros (1), punk rock (1), rock (1) |  |
| Zizurkil | Gipuzkoa | 1 | 1 | 2026–2026 | 0 % | antifa electropop (1), electro (1), electronic (1), political pop (1), post-punk (1) |  |

## Preguntas de ejemplo

**¿Qué tags están sobrerrepresentados en Zarautz?**

- live recording: ×26.3 (98 releases)
- deep tech: ×24.2 (25 releases)
- tropical: ×23.9 (45 releases)
- crust punk: ×21.9 (98 releases)
- live: ×21.8 (98 releases)
- rub a dub: ×18.5 (13 releases)
- raggamuffin: ×17.6 (13 releases)
- r&b/soul: ×16.9 (45 releases)
- mugre: ×14.8 (6 releases)
- one man band: ×13.6 (6 releases)

**¿Dónde aparece `noise`?** 333 releases en el archivo, 284 localizadas (85.3 %).

| Municipio | Releases con el tag | Releases del municipio | lift |
|---|---:|---:|---:|
| Bilbo | 133 | 2609 | ×1.2 |
| Gasteiz | 59 | 589 | ×2.4 |
| Donostia | 50 | 1050 | ×1.1 |
| Iruñea | 15 | 979 | ×0.4 |
| Getxo | 12 | 96 | ×3.0 |
| Berriz | 5 | 11 | ×11.0 |
| Arrasate | 4 | 50 | ×1.9 |
| Azkaine | 2 | 2 | ×24.2 |
| Ondarroa | 2 | 40 | ×1.2 |
| Andoain | 1 | 33 | ×0.7 |

**¿Dónde aparece `hardcore`?** 670 releases en el archivo, 602 localizadas (89.9 %).

| Municipio | Releases con el tag | Releases del municipio | lift |
|---|---:|---:|---:|
| Bilbo | 185 | 2609 | ×0.8 |
| Zarautz | 108 | 297 | ×4.4 |
| Irun | 56 | 114 | ×5.9 |
| Donostia | 54 | 1050 | ×0.6 |
| Gasteiz | 50 | 589 | ×1.0 |
| Iruñea | 23 | 979 | ×0.3 |
| Sopela | 18 | 19 | ×11.4 |
| Gernika-Lumo | 11 | 47 | ×2.8 |
| Santurtzi | 10 | 76 | ×1.6 |
| Oiartzun | 8 | 35 | ×2.7 |

**¿Dónde aparece `techno`?** 693 releases en el archivo, 662 localizadas (95.5 %).

| Municipio | Releases con el tag | Releases del municipio | lift |
|---|---:|---:|---:|
| Bilbo | 361 | 2609 | ×1.6 |
| Iruñea | 166 | 979 | ×2.0 |
| Donostia | 83 | 1050 | ×0.9 |
| Gasteiz | 41 | 589 | ×0.8 |
| Portugalete | 3 | 41 | ×0.8 |
| Zizur Nagusia | 2 | 2 | ×11.6 |
| Hondarribia | 2 | 62 | ×0.4 |
| Sestao | 1 | 8 | ×1.4 |
| Hernani | 1 | 32 | ×0.4 |
| Errenteria | 1 | 60 | ×0.2 |

**¿Dónde aparece `trikitixa`?** 3 releases en el archivo, 3 localizadas (100.0 %).

| Municipio | Releases con el tag | Releases del municipio | lift |
|---|---:|---:|---:|
| Kanbo | 1 | 13 | ×206.3 |
| Portugalete | 1 | 41 | ×65.4 |
| Gasteiz | 1 | 589 | ×4.5 |

**¿Qué parte del catálogo tiene ubicación fiable?** 6903 de 8046 (85.8 %); con inferencia por artista, 6994 (86.9 %).

Consultas propias: `python3 scripts/locations.py query --place zarautz` o `--tag noise` (matriz municipio × tag y tag × municipio).
