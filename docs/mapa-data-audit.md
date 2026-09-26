# Auditoría del dataset de ubicaciones (fase 6)

*Generado por `python3 scripts/locations.py audit` a partir de `data/locations/resolutions.json`. No editar a mano.*

Recordatorio: la ubicación es la que Bandcamp da **hoy** a la cuenta que publica (grupo o sello). Estas cifras describen **el archivo**, no la escena ni la residencia histórica de nadie.

## Resumen

| | Releases | % |
|---|---:|---:|
| **Total** | 7637 | 100 % |
| direct — directa (Bandcamp, esta release) | 5018 | 65.7 % |
| same_account — misma cuenta de Bandcamp | 1486 | 19.5 % |
| artist_inferred — inferida por artista | 83 | 1.1 % |
| manual — manual | 0 | 0.0 % |
| region_only — solo región/país | 560 | 7.3 % |
| outside_scope — fuera de Euskal Herria | 287 | 3.8 % |
| tag_hint — solo pista de tag | 36 | 0.5 % |
| unresolved — sin resolver | 167 | 2.2 % |

- **En el mapa por defecto** (direct + same_account + artist_inferred + manual): **6587** (86.3 %).
- **Fiables** (Bandcamp de la propia cuenta o decisión manual, sin inferencia): **6504** (85.2 %).
- Situadas por la ubicación de una **cuenta con varios artistas** (probable sello, índice `data/derived/labels.json`): 2039. Su lugar es el de esa cuenta, no necesariamente el del grupo.
- **Sin municipio** en el mapa por defecto: **1050** (13.7 %); de ellas, 156 consultadas en Bandcamp sin ubicación.
- Sin resolver (167): 142 porque Bandcamp no da ubicación, 22 con evidencia descartada (ver abajo) y 3 sin evidencia.
- Municipios con al menos una release: **104**.
- Releases con contradicciones registradas: 33 (tag 30, tag_hints_multiple 3).

## Por territorio (mapa por defecto)

| Territorio | Releases |
|---|---:|
| Bizkaia | 3034 |
| Gipuzkoa | 1903 |
| Nafarroa | 975 |
| Araba | 596 |
| Iparralde | 79 |

## Solo región (region_only)

| Región | Releases |
|---|---:|
| euskal-herria | 421 |
| france | 73 |
| spain | 39 |
| nafarroa | 13 |
| enkarterri | 8 |
| nouvelle-aquitaine | 4 |
| arratia-nerbioi | 2 |

## Por décadas (año de la release)

| Década | Localizadas | Sin municipio | % localizadas |
|---|---:|---:|---:|
| 1980s | 7 | 1 | 87.5 % |
| 1990s | 49 | 16 | 75.4 % |
| 2000s | 255 | 74 | 77.5 % |
| 2010s | 2938 | 465 | 86.3 % |
| 2020s | 3319 | 490 | 87.1 % |
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
| Bilbo | Bizkaia | 2469 | 1052 | 1992–2026 | 32 % | electronic (587), rock (509), experimental (398), metal (375), techno (353) | sello ×3.1, death metal melódico ×3.1, xtreem music ×3.1, eurotrance ×3.1 |
| Donostia | Gipuzkoa | 1005 | 435 | 1985–2026 | 37 % | rock (312), electronic (286), experimental (184), punk (161), pop (148) | art-blues ×7.6, deathdream ×7.6, dreampunk ×7.6, folk psicodelia ×7.6 |
| Iruñea | Nafarroa | 925 | 427 | 1998–2026 | 34 % | rock (258), electronic (212), techno (166), metal (136), pop (136) | vgm ×8.3, primavera sound ×8.3, sonido muchacho ×8.3, reverbcore ×8.3 |
| Gasteiz | Araba | 557 | 246 | 1998–2026 | 23 % | rock (140), metal (118), electronic (96), punk (84), black metal (76) | freakbeat ×13.7, senoid recordings ×13.7, grove metal ×13.7, minimal techno industrial ×13.7 |
| Zarautz | Gipuzkoa | 280 | 163 | 1989–2026 | 59 % | punk (115), hardcore (106), hardcore punk (101), crust punk (98), live (98) | live recording ×26.5, deep tech ×24.4, tropical ×24.1, live ×22.3 |
| Irun | Gipuzkoa | 113 | 27 | 1997–2025 | 54 % | punk (75), punk rock (62), post-punk (59), hardcore (56), petruska records (28) | 77 punk ×67.6, 82 punk ×67.6, petruska records ×67.6, oi ×23.6 |
| Getxo | Bizkaia | 93 | 36 | 2004–2026 | 9 % | rock (46), indie rock (20), alternative (16), pop (16), acoustic (14) | hardrock ×74.7, heavymetal ×68.4, heavy rock ×34.2, shoegaze ×15.1 |
| Santurtzi | Bizkaia | 75 | 65 | 2012–2025 | 83 % | punk (66), metal (44), crust (40), death metal (40), grindcore (40) | oz rock ×101.8, swamp rock ×101.8, high energy rock ×88.5, blackened crust ×40.7 |
| Hondarribia | Gipuzkoa | 59 | 26 | 2005–2026 | 0 % | rock (19), pop (14), hip-hop/rap (10), dub (7), instrumental (7) | stoner metal ×51.8, sludge metal ×30.5, acoustic rock ×21.6, cumbia ×21.6 |
| Errenteria | Gipuzkoa | 58 | 19 | 1992–2026 | 9 % | pop (29), digicore (24), glitch pop (24), hyper pop (24), internet music (24) | digicore ×131.7, internet music ×131.7, internetcore ×131.7, glitch pop ×126.4 |
| Barakaldo | Bizkaia | 56 | 28 | 1991–2025 | 0 % | rock (34), punk (21), punk rock (9), rock'n'roll (8), garage (7) | melodic metal ×34.1, garage punk ×25.8, rock'n'roll ×20.6, power metal ×14.4 |
| Arrasate | Gipuzkoa | 49 | 29 | 2010–2026 | 26 % | punk rock (25), rock (21), punk (16), metal (9), black metal (7) | metalpunk ×41.6, surf ×22.3, street punk ×15.2, punk rock ×7.8 |
| Leioa | Bizkaia | 48 | 1 | 2017–2025 | 0 % | soundtrack (48), beats (2), cinematic (2), synthwave (2), 8bits (1) | soundtrack ×42.2 |
| Bermeo | Bizkaia | 43 | 22 | 1994–2025 | 5 % | rock (26), punk (10), hard rock (7), hardcore (7), alternative (5) | melodic rock ×52.2, euskal rock ×28.4, punk hardcore ×14.8, d-beat ×12.7 |
| Gernika-Lumo | Bizkaia | 43 | 18 | 2003–2026 | 5 % | metal (11), punk (11), rock (11), hardcore (9), alternative (8) | melodic metal ×55.5, extreme metal ×53.3, acoustic guitar ×29.6, afghanistan ×21.3 |
| Portugalete | Bizkaia | 41 | 25 | 2008–2026 | 61 % | electronic (17), hip hop (16), beattape (15), world beats (15), rock (12) | beattape ×186.3, world beats ×186.3, kraut ×46.6, soft rock ×43.0 |
| Ondarroa | Bizkaia | 39 | 15 | 1998–2026 | 28 % | rock (24), pop rock (14), alternative (12), euskal musika (9), folk (9) | fastcore ×49.0, powerviolence ×35.6, euskal musika ×16.9, screamo ×14.4 |
| Eibar | Gipuzkoa | 37 | 13 | 2009–2025 | 8 % | rock (14), electronic (10), ambient electronic (9), bidehuts (7), metal (7) | soundscapes ×63.5, comedy ×55.0, ambient electronic ×51.6, groove metal ×30.4 |
| Oiartzun | Gipuzkoa | 35 | 15 | 2004–2024 | 23 % | punk (14), hip-hop/rap (11), rap (11), hip hop (9), hardcore (8) | oi ×87.3, occitan ×65.5, street punk ×42.6, trap ×24.6 |
| Tolosa | Gipuzkoa | 34 | 16 | 1998–2025 | 0 % | rock (9), grindcore (8), metal (8), punk (8), crust (7) | raggamuffin ×33.7, dancehall ×12.5, crust ×11.7, grindcore ×8.2 |
| Andoain | Gipuzkoa | 33 | 14 | 1983–2026 | 42 % | rock (19), pop (14), soul (14), electronic (9), experimental (9) | flamenco ×135.0, fantasy ×104.1, horror ×61.3, euskaraz ×24.8 |
| Hernani | Gipuzkoa | 32 | 14 | 2005–2026 | 12 % | punk (14), rock (11), oi! (10), oi! streetpunk (8), skinhead (8) | oi! streetpunk ×190.9, skinhead ×61.6, oi! ×26.2, instrumental ×8.2 |
| Oñati | Gipuzkoa | 29 | 19 | 2012–2026 | 7 % | rock (16), alternative (6), punk (5), 70s (3), free jazz (3) | free jazz ×11.1, post-hardcore ×3.7, post-punk ×2.5, rock ×2.1 |
| Laudio | Araba | 22 | 13 | 2001–2026 | 18 % | rock (8), post-rock (5), acoustic (4), alternative rock; laudio (4), cantautor (4) | folk pop ×49.6, cantautor ×27.8, post-rock ×11.2, post-hardcore ×6.5 |
| Tutera | Nafarroa | 22 | 14 | 2010–2023 | 0 % | rock (14), hard rock (8), alternative (7), rock and roll (5), surf rock (4) | surf rock ×47.9, garage rock ×28.9, hard rock ×17.1, rock and roll ×14.5 |
| Zumaia | Gipuzkoa | 22 | 9 | 2014–2026 | 0 % | rock (12), experimental (8), rock & roll (6), blues (5), blues rock (5) | blues rock ×40.4, rock & roll ×14.6, blues ×13.4, folk ×4.2 |
| Azpeitia | Gipuzkoa | 18 | 11 | 2006–2026 | 17 % | punk (6), rock (6), street punk (4), alternative (3), hardcore punk (3) | street punk ×41.4, hardcore punk ×4.7, punk ×1.9, alternative ×1.3 |
| Lekeitio | Bizkaia | 17 | 7 | 2010–2026 | 47 % | cloud rap (6), hip hop (6), hip-hop/rap (6), rap (6), trap (6) | trap ×38.0, rap ×11.9, hip hop ×10.7, hip-hop/rap ×9.2 |
| Bergara | Gipuzkoa | 16 | 10 | 2011–2024 | 25 % | punk (8), hardcore (7), punk rock (7), rock (5), euskera (4) | skate punk ×84.2, euskera ×34.7, metalcore ×13.1, post-hardcore ×9.0 |
| Ermua | Bizkaia | 16 | 9 | 2006–2025 | 0 % | rock (7), metal (4), punk (4), alternative (3), diy (3) | diy ×17.7, metal ×1.8, rock ×1.7, alternative ×1.5 |
| Mungia | Bizkaia | 16 | 8 | 1996–2026 | 0 % | alternative (5), melodic hardcore (5), punk (5), skatepunk (5), pop (4) | skatepunk ×159.1, melodic hardcore ×48.7, pop ×2.5, alternative ×2.5 |
| Baiona | Iparralde | 14 | 5 | 2007–2024 | 0 % | alternative (9), rock (6), bidehuts (4), drummond (4), italo noise (4) | bidehuts ×32.6, hardcore punk ×6.1, alternative ×5.2, hardcore ×2.5 |
| Hendaia | Iparralde | 13 | 4 | 2005–2026 | 0 % | rock (10), rock compilation (10), alternative (2), antzerkia (1), electronic (1) | rock compilation ×587.5, rock ×3.0 |
| Kanbo | Iparralde | 13 | 13 | 2019–2024 | 100 % | belarri (13), euskal musika (13), musika (13), world (13), contemporary (2) | belarri ×587.5, musika ×381.9, euskal musika ×73.4, world ×37.2 |
| Amurrio | Araba | 12 | 9 | 2008–2026 | 33 % | metal (5), alternative (4), crossover (4), groove metal (4), hardcore (4) | crossover ×79.5, groove metal ×74.9, hardcore ×3.9, metal ×3.0 |
| Berriz | Bizkaia | 11 | 4 | 2010–2024 | 0 % | ambient (5), electronic (5), experimental (5), hardcore (5), idm (5) | idm ×23.5, industrial ×19.2, noise ×11.0, ambient ×6.1 |
| Mendaro | Gipuzkoa | 11 | 2 | 2003–2023 | 0 % | electronica (10), indie (10), punk (10), rock (10), munlet (7) | electronica ×31.7, indie ×27.6, post-punk ×11.1, punk ×5.1 |
| Sopela | Bizkaia | 11 | 3 | 2014–2021 | 9 % | doom (10), hardcore (10), metal (9), sludge (9), black metal (5) | sludge ×73.5, doom ×59.3, stoner ×42.9, black metal ×12.9 |
| Basauri | Bizkaia | 10 | 5 | 2009–2025 | 0 % | punk (7), hardcore punk (4), punk rock (3), rock (3), skate punk (3) | skatepunk ×152.7, skate punk ×134.8, hardcore punk ×11.4, punk rock ×4.6 |
| Itsasu | Iparralde | 9 | 2 | 2020–2025 | 100 % | alternative (9), basque music (9), eklektrik (9), pop rock (9), txomin larronde (9) | basque music ×49.9, pop rock ×29.1, alternative ×8.0 |
| Zumarraga | Gipuzkoa | 9 | 3 | 2004–2023 | 0 % | punk (5), punk rock (5), rock (5), rock'n'speed (5), death metal (3) | melodic death metal ×45.5, death metal ×9.1, punk rock ×8.5, punk ×3.1 |
| Arrigorriaga | Bizkaia | 8 | 1 | 2020–2025 | 0 % | basque music (8), death metal (8), heavy metal (8), metal (8), thrash metal (8) | thrash metal ×76.4, heavy metal ×74.9, basque music ×49.9, death metal ×27.3 |
| Bera | Nafarroa | 8 | 4 | 2013–2022 | 0 % | alternative (6), alternative rock (6), rock (2), 90s rock (1), angry (1) | alternative rock ×23.4, alternative ×6.0 |
| Legazpi | Gipuzkoa | 8 | 3 | 2010–2024 | 0 % | bloody rock (6), hard rock (6), high energy rock'n'roll (6), punk rock (6), rock (6) | hard rock ×35.4, punk rock ×11.5, rock ×2.9 |
| Urretxu | Gipuzkoa | 8 | 4 | 2014–2023 | 0 % | rock (6), hard rock (5), blues rock (4), country (4), rock and roll (4) | blues rock ×88.8, country ×49.6, rock and roll ×31.8, hard rock ×29.5 |
| Hazparne | Iparralde | 7 | 3 | 2012–2025 | 0 % | folk (6), alternative (5), grunge (5), indie (5), basque music (2) | grunge ×54.0, indie ×21.6, folk ×15.8, alternative ×5.7 |
| Galdakao | Bizkaia | 6 | 5 | 2015–2025 | 0 % | punk (4), punk rock (3), melodic hardcore (2), metal (2), post-hardcore (2) | punk rock ×7.6, punk ×3.8 |
| Ispaster | Bizkaia | 6 | 1 | 2012–2017 | 0 % | alternative (6), beruna (6), crust (6), doom (6), sludge (6) | sludge ×89.8, doom ×65.3, crust ×57.0, alternative ×8.0 |
| Lasarte-Oria | Gipuzkoa | 6 | 5 | 2010–2024 | 0 % | alternative (2), black metal (2), death metal (2), euskal musika (2), metal (2) |  |
| Sestao | Bizkaia | 6 | 6 | 2014–2024 | 67 % | electro glam (4), electronic (4), techno house (4), techno punk (4), batucada (1) | electronic ×3.5 |
| Getaria | Gipuzkoa | 5 | 3 | 2021–2026 | 0 % | getaria (5), punk (5), hardcore (3), punk rock (3), hardcore punk (2) | getaria ×763.7, punk rock ×9.2, hardcore ×7.1, punk ×5.6 |
| Lekunberri | Nafarroa | 5 | 2 | 2014–2017 | 0 % | lekunberri (5), indie (4), metal (4), punk (4), punk rock (4) | indie ×24.2, punk rock ×12.2, metal ×5.8, punk ×4.5 |
| Orio | Gipuzkoa | 5 | 2 | 2011–2021 | 0 % | rock (5), ambient (4), experimental (4), instrumental (4), math-rock (4) | instrumental ×42.1, post-rock ×39.4, ambient ×10.7, experimental ×6.8 |
| Urnieta | Gipuzkoa | 5 | 1 | 2007–2014 | 0 % | post-hardcore (5), punk rock (5), rock (5), pop (2), alternative metal (1) | post-hardcore ×36.0, punk rock ×15.3, rock ×3.8 |
| Villabona-Amasa | Gipuzkoa | 5 | 2 | 2019–2023 | 0 % | rock (5), alternative rock (3), ambient rock (3), basque music (3), grunge (3) | melodic rock ×269.5, ambient rock ×218.2, grunge ×45.4, basque music ×29.9 |
| Abadiño | Bizkaia | 4 | 1 | 2010–2024 | 0 % | black metal (4), dark power metal (4), death metal (4), metal (4), power metal (4) | power metal ×201.0, black metal ×28.4, death metal ×27.3, metal ×7.2 |
| Donibane Lohizune | Iparralde | 4 | 4 | 2015–2017 | 75 % | electric human machines (3), electronic (3), experimental easy listening (3), baleapop (2), beleak (1) | electronic ×4.0 |
| Elortzibar | Nafarroa | 4 | 1 | 2010–2015 | 0 % | noáin, navarra (4), punk (4), punk-oi (1), punkoi (1) | punk ×5.6 |
| Azkoitia | Gipuzkoa | 3 | 2 | 2016–2025 | 0 % | hardcore (3), rock (3), hard rock (2), metal (2), punk (2) | hardcore ×11.8, rock ×3.8 |
| Biarritz | Iparralde | 3 | 3 | 2011–2020 | 0 % | world (2), acoustic rock (1), andoken (1), bask and world music (1), boom bap (1) |  |
| Maule-Lextarre | Iparralde | 3 | 1 | 2018–2025 | 0 % | dub (3), ragga (3), raggamuffin (3), reggae (3), roots (3) | ragga ×636.4, raggamuffin ×381.9, roots ×72.0, dub ×31.3 |
| Moreda Araba | Araba | 3 | 1 | 2013–2018 | 0 % | blues (3), punk (3), rock (3), bluespunk (1) | blues ×59.2, punk ×5.6, rock ×3.8 |
| Zaldibar | Bizkaia | 3 | 1 | 2023–2026 | 0 % | alternative (3), basque music (3), pop (3), post-punk (3) | basque music ×49.9, post-punk ×24.4, pop ×10.1, alternative ×8.0 |
| Azkaine | Iparralde | 2 | 1 | 2015–2018 | 0 % | alternative (2), doom (2), noise (2), post-rock (2), stoner (2) |  |
| Baigorri | Iparralde | 2 | 1 | 2016–2018 | 0 % | black metal (2), medieval (2), metal (2), dark medieval (1), history (1) |  |
| Bastida | Iparralde | 2 | 1 | 2021–2026 | 0 % | alternative (2), female vocals (2), strings (2), traditional (2), traditional jazz (2) |  |
| Beasain | Gipuzkoa | 2 | 2 | 2017–2023 | 0 % | composer (1), diy (1), experimental (1), instrumental (1), midi (1) |  |
| Deba | Gipuzkoa | 2 | 2 | 2022–2024 | 100 % | aitor huergo (2), barruko (2), euskal (2), folk (2), paisaiak (2) |  |
| Durango | Bizkaia | 2 | 2 | 2012–2020 | 50 % | boom-bap (1), euskera (1), funk (1), hard rock (1), hip-hop/rap (1) |  |
| Elgoibar | Gipuzkoa | 2 | 1 | 2011–2013 | 0 % | acoustic (2), folk (2), rock (2) |  |
| Elorrio | Bizkaia | 2 | 1 | 2010–2013 | 0 % | rock (2), rock roll punk-rock-stoner (2), sermonds (2) |  |
| Eskoriatza | Gipuzkoa | 2 | 1 | 2005–2013 | 0 % | hardcore (2), hardcore punk (2), punk (2) |  |
| Irulegi | Iparralde | 2 | 1 | 2019–2024 | 0 % | basque music (2), euskal kantagintza (2), euskal musika (2), folk (2) |  |
| Martzilla | Nafarroa | 2 | 1 | 2020–2021 | 0 % | pop rock (2), rock (2), txente (2) |  |
| Otxandio | Bizkaia | 2 | 1 | 2023–2025 | 0 % | alternative (2), euskera (2), oi! (2), punk (2), punk rock (2) |  |
| Soraluze | Gipuzkoa | 2 | 2 | 2011–2012 | 0 % | blues (1), country (1), metal (1), metal progresivo (1), progressive metal (1) |  |
| Suhuskune | Iparralde | 2 | 1 | 2018–2020 | 0 % | duo (2), euskara (2), euskaraz (2), heavy blues rock (2), power duo (2) |  |
| Zaldibia | Gipuzkoa | 2 | 1 | 2014–2021 | 0 % | acoustic (2), bertsioak (2), covers (2), q ez da (2), version (2) |  |
| Zestoa | Gipuzkoa | 2 | 1 | 2013–2017 | 0 % | acoustic (2), africa (2), euskara (2), kora (2), strings (2) |  |
| Ainhize-Monjolose | Iparralde | 1 | 1 | 2016–2016 | 0 % | bilau (1), euskal musika (1), experimental (1), folk minimal (1), ghostfolk (1) |  |
| Altsasu | Nafarroa | 1 | 1 | 2023–2023 | 0 % | album (1), d-beat (1), disasko (1), disbrigade (1), hardcore (1) |  |
| Angelu | Iparralde | 1 | 1 | 2025–2025 | 0 % | chant (1), gascon (1), polyphonie (1), traditionnel (1), world (1) |  |
| Aramaio | Araba | 1 | 1 | 2021–2021 | 0 % | album release (1), basque music (1), basque rock alternative (1), phoenix (1), rock (1) |  |
| Arellano | Nafarroa | 1 | 1 | 2015–2015 | 0 % | balcan (1), ska (1), tango (1), tumbao (1), world (1) |  |
| Aretxabaleta | Gipuzkoa | 1 | 1 | 2025–2025 | 0 % | euskal musika (1), nhil (1), nhilband (1), pop (1), soul (1) |  |
| Berango | Bizkaia | 1 | 1 | 2025–2025 | 0 % | alternative pop rock (1), basque rock alternative (1), pop (1), psychopunk (1), rock (1) |  |
| Burlata | Nafarroa | 1 | 1 | 2018–2018 | 0 % | euskara (1), hardcore (1), metal (1), thrash metal (1) |  |
| Donibane Garazi | Iparralde | 1 | 1 | 2017–2017 | 0 % | alternative rock (1), bass (1), drums (1), duo (1), euskal (1) |  |
| Erandio | Bizkaia | 1 | 1 | 2015–2015 | 0 % | metal (1), rock (1), scandinavian (1), skate (1) |  |
| Legorreta | Gipuzkoa | 1 | 1 | 2012–2012 | 0 % | punk (1), punk-rock (1) |  |
| Legutio | Araba | 1 | 1 | 2020–2020 | 0 % | hardcore punk (1), punk (1), punk oi! (1), street punk (1) |  |
| Lizarra | Nafarroa | 1 | 1 | 2024–2024 | 0 % | alternative (1), folk (1), songwriter (1) |  |
| Markina-Xemein | Bizkaia | 1 | 1 | 2016–2016 | 0 % | electronic (1), electronic rock (1), indie rock (1), rock (1) |  |
| Mundaka | Bizkaia | 1 | 1 | 2012–2012 | 0 % | hau ez dek (1), mala ostia (1), punk (1) |  |
| Mutriku | Gipuzkoa | 1 | 1 | 2013–2013 | 0 % | beat (1), hip hop (1), hip hop instrumentals (1), hip hop soul (1), hip-hop/rap (1) |  |
| San Adrián | Nafarroa | 1 | 1 | 2016–2016 | 0 % | blues (1), humor (1), rock and roll (1), show (1) |  |
| Tafalla | Nafarroa | 1 | 1 | 2021–2021 | 0 % | acoustic (1), classical (1), new age (1), new age music (1), piano solo (1) |  |
| Trapagaran | Bizkaia | 1 | 1 | 2020–2020 | 0 % | basque music (1), doom (1), metal (1), rock (1), shaman (1) |  |
| Untzue | Nafarroa | 1 | 1 | 2021–2021 | 0 % | diy (1), etxekopunk (1), garage (1), punk (1), rural streetpunk (1) |  |
| Urdazubi | Nafarroa | 1 | 1 | 2022–2022 | 0 % | euskal rock (1), hard rock (1), kamuts (1), rock (1) |  |
| Usurbil | Gipuzkoa | 1 | 1 | 2024–2024 | 0 % | electronic (1), euskaraz (1), pop (1), rap (1), rock (1) |  |
| Zaratamo | Bizkaia | 1 | 1 | 2019–2019 | 0 % | kon (1), perros (1), punk rock (1), rock (1) |  |
| Zizur Nagusia | Nafarroa | 1 | 1 | 2025–2025 | 0 % | davma (1), electronic (1), electronica (1), rebels (1), riot (1) |  |
| Zornotza | Bizkaia | 1 | 1 | 2012–2012 | 0 % | hip hop (1), hip-hop/rap (1), pablo gil aguirre (1), ronda (1) |  |

## Preguntas de ejemplo

**¿Qué tags están sobrerrepresentados en Zarautz?**

- live recording: ×26.5 (98 releases)
- deep tech: ×24.4 (25 releases)
- tropical: ×24.1 (45 releases)
- live: ×22.3 (98 releases)
- crust punk: ×22.1 (98 releases)
- rub a dub: ×18.7 (13 releases)
- raggamuffin: ×17.7 (13 releases)
- r&b/soul: ×17.1 (45 releases)
- mugre: ×14.9 (6 releases)
- one man band: ×13.6 (6 releases)

**¿Dónde aparece `noise`?** 315 releases en el archivo, 266 localizadas (84.4 %).

| Municipio | Releases con el tag | Releases del municipio | lift |
|---|---:|---:|---:|
| Bilbo | 128 | 2469 | ×1.3 |
| Donostia | 50 | 1005 | ×1.2 |
| Gasteiz | 49 | 557 | ×2.1 |
| Iruñea | 14 | 925 | ×0.4 |
| Getxo | 10 | 93 | ×2.6 |
| Berriz | 5 | 11 | ×11.0 |
| Arrasate | 4 | 49 | ×2.0 |
| Azkaine | 2 | 2 | ×24.2 |
| Ondarroa | 2 | 39 | ×1.2 |
| Andoain | 1 | 33 | ×0.7 |

**¿Dónde aparece `hardcore`?** 649 releases en el archivo, 581 localizadas (89.5 %).

| Municipio | Releases con el tag | Releases del municipio | lift |
|---|---:|---:|---:|
| Bilbo | 181 | 2469 | ×0.9 |
| Zarautz | 106 | 280 | ×4.5 |
| Irun | 56 | 113 | ×5.8 |
| Donostia | 53 | 1005 | ×0.6 |
| Gasteiz | 46 | 557 | ×1.0 |
| Iruñea | 23 | 925 | ×0.3 |
| Sopela | 10 | 11 | ×10.7 |
| Santurtzi | 10 | 75 | ×1.6 |
| Gernika-Lumo | 9 | 43 | ×2.5 |
| Oiartzun | 8 | 35 | ×2.7 |

**¿Dónde aparece `techno`?** 679 releases en el archivo, 648 localizadas (95.4 %).

| Municipio | Releases con el tag | Releases del municipio | lift |
|---|---:|---:|---:|
| Bilbo | 353 | 2469 | ×1.6 |
| Iruñea | 166 | 925 | ×2.0 |
| Donostia | 80 | 1005 | ×0.9 |
| Gasteiz | 39 | 557 | ×0.8 |
| Portugalete | 3 | 41 | ×0.8 |
| Hondarribia | 2 | 59 | ×0.4 |
| Zizur Nagusia | 1 | 1 | ×11.2 |
| Sestao | 1 | 6 | ×1.9 |
| Hernani | 1 | 32 | ×0.3 |
| Errenteria | 1 | 58 | ×0.2 |

**¿Dónde aparece `trikitixa`?** 3 releases en el archivo, 3 localizadas (100.0 %).

| Municipio | Releases con el tag | Releases del municipio | lift |
|---|---:|---:|---:|
| Kanbo | 1 | 13 | ×195.8 |
| Portugalete | 1 | 41 | ×62.1 |
| Gasteiz | 1 | 557 | ×4.6 |

**¿Qué parte del catálogo tiene ubicación fiable?** 6504 de 7637 (85.2 %); con inferencia por artista, 6587 (86.3 %).

Consultas propias: `python3 scripts/locations.py query --place zarautz` o `--tag noise` (matriz municipio × tag y tag × municipio).
