# Auditoría del dataset de ubicaciones (fase 6)

*Generado por `python3 scripts/locations.py audit` a partir de `data/locations/resolutions.json`. No editar a mano.*

Recordatorio: la ubicación es la que Bandcamp da **hoy** a la cuenta que publica (grupo o sello). Estas cifras describen **el archivo**, no la escena ni la residencia histórica de nadie.

## Resumen

| | Releases | % |
|---|---:|---:|
| **Total** | 7568 | 100 % |
| direct — directa (Bandcamp, esta release) | 4953 | 65.4 % |
| same_account — misma cuenta de Bandcamp | 1486 | 19.6 % |
| artist_inferred — inferida por artista | 83 | 1.1 % |
| manual — manual | 0 | 0.0 % |
| region_only — solo región/país | 558 | 7.4 % |
| outside_scope — fuera de Euskal Herria | 286 | 3.8 % |
| tag_hint — solo pista de tag | 36 | 0.5 % |
| unresolved — sin resolver | 166 | 2.2 % |

- **En el mapa por defecto** (direct + same_account + artist_inferred + manual): **6522** (86.2 %).
- **Fiables** (Bandcamp de la propia cuenta o decisión manual, sin inferencia): **6439** (85.1 %).
- Situadas por la ubicación de una **cuenta con varios artistas** (probable sello, índice `data/derived/labels.json`): 2026. Su lugar es el de esa cuenta, no necesariamente el del grupo.
- **Sin municipio** en el mapa por defecto: **1046** (13.8 %); de ellas, 155 consultadas en Bandcamp sin ubicación.
- Sin resolver (166): 141 porque Bandcamp no da ubicación, 22 con evidencia descartada (ver abajo) y 3 sin evidencia.
- Municipios con al menos una release: **104**.
- Releases con contradicciones registradas: 33 (tag 30, tag_hints_multiple 3).

## Por territorio (mapa por defecto)

| Territorio | Releases |
|---|---:|
| Bizkaia | 3003 |
| Gipuzkoa | 1894 |
| Nafarroa | 961 |
| Araba | 586 |
| Iparralde | 78 |

## Solo región (region_only)

| Región | Releases |
|---|---:|
| euskal-herria | 421 |
| france | 73 |
| spain | 37 |
| nafarroa | 13 |
| enkarterri | 8 |
| nouvelle-aquitaine | 4 |
| arratia-nerbioi | 2 |

## Por décadas (año de la release)

| Década | Localizadas | Sin municipio | % localizadas |
|---|---:|---:|---:|
| 1980s | 7 | 1 | 87.5 % |
| 1990s | 49 | 15 | 76.6 % |
| 2000s | 255 | 74 | 77.5 % |
| 2010s | 2938 | 464 | 86.4 % |
| 2020s | 3254 | 488 | 87.0 % |
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
| Bilbo | Bizkaia | 2440 | 1043 | 1992–2026 | 32 % | electronic (567), rock (507), experimental (397), metal (374), techno (336) | sello ×3.1, bass lee ×3.1, trance electro techno ×3.1, bumping ×3.1 |
| Donostia | Gipuzkoa | 998 | 435 | 1985–2026 | 37 % | rock (312), electronic (280), experimental (184), punk (161), pop (148) | ally morton ×7.6, new age. ×7.6, preqwal ×7.6, tony morton ×7.6 |
| Iruñea | Nafarroa | 911 | 424 | 1998–2026 | 34 % | rock (257), electronic (205), techno (159), house (135), pop (135) | primavera sound ×8.3, sonido muchacho ×8.3, vgm ×8.3, reverbcore ×8.3 |
| Gasteiz | Araba | 548 | 244 | 1998–2026 | 23 % | rock (139), metal (112), electronic (94), punk (83), black metal (70) | minimal techno industrial ×13.8, grove metal ×13.8, freakbeat ×13.8, senoid recordings ×13.8 |
| Zarautz | Gipuzkoa | 279 | 162 | 1989–2026 | 59 % | punk (114), hardcore (105), hardcore punk (100), crust punk (97), live (97) | live recording ×26.3, deep tech ×24.2, tropical ×23.9, live ×22.3 |
| Irun | Gipuzkoa | 113 | 27 | 1997–2025 | 54 % | punk (75), punk rock (62), post-punk (59), hardcore (56), petruska records (28) | petruska records ×67.0, 77 punk ×67.0, 82 punk ×67.0, oi ×23.4 |
| Getxo | Bizkaia | 93 | 36 | 2004–2026 | 9 % | rock (46), indie rock (20), alternative (16), pop (16), acoustic (13) | hardrock ×74.0, heavymetal ×67.8, heavy rock ×33.9, shoegaze ×15.3 |
| Santurtzi | Bizkaia | 75 | 65 | 2012–2025 | 83 % | punk (66), metal (44), crust (40), death metal (40), grindcore (40) | oz rock ×100.9, swamp rock ×100.9, high energy rock ×87.7, blackened crust ×40.4 |
| Hondarribia | Gipuzkoa | 59 | 26 | 2005–2026 | 0 % | rock (19), pop (14), hip-hop/rap (10), dub (7), instrumental (7) | stoner metal ×51.3, sludge metal ×30.2, acoustic rock ×24.1, cumbia ×21.4 |
| Errenteria | Gipuzkoa | 58 | 19 | 1992–2026 | 9 % | pop (29), digicore (24), glitch pop (24), hyper pop (24), internet music (24) | digicore ×130.5, internet music ×130.5, internetcore ×130.5, glitch pop ×125.3 |
| Barakaldo | Bizkaia | 56 | 28 | 1991–2025 | 0 % | rock (34), punk (21), punk rock (9), rock'n'roll (8), garage (7) | melodic metal ×33.8, garage punk ×26.3, rock'n'roll ×20.4, power metal ×14.2 |
| Arrasate | Gipuzkoa | 49 | 29 | 2010–2026 | 26 % | punk rock (25), rock (21), punk (16), metal (9), black metal (7) | metalpunk ×41.2, surf ×22.1, street punk ×15.4, punk rock ×7.8 |
| Leioa | Bizkaia | 48 | 1 | 2017–2025 | 0 % | soundtrack (48), beats (2), cinematic (2), synthwave (2), 8bits (1) | soundtrack ×42.0 |
| Bermeo | Bizkaia | 43 | 22 | 1994–2025 | 5 % | rock (26), punk (10), hard rock (7), hardcore (7), alternative (5) | melodic rock ×51.8, euskal rock ×30.6, punk hardcore ×14.7, d-beat ×12.6 |
| Gernika-Lumo | Bizkaia | 43 | 18 | 2003–2026 | 5 % | metal (11), punk (11), rock (11), hardcore (9), alternative (8) | melodic metal ×55.0, extreme metal ×52.8, acoustic guitar ×29.3, afghanistan ×21.1 |
| Portugalete | Bizkaia | 40 | 25 | 2008–2026 | 62 % | electronic (16), hip hop (16), beattape (15), world beats (15), rock (12) | beattape ×189.2, world beats ×189.2, kraut ×47.3, soft rock ×43.7 |
| Ondarroa | Bizkaia | 39 | 15 | 1998–2026 | 28 % | rock (24), pop rock (14), alternative (12), euskal musika (9), folk (9) | fastcore ×48.5, powerviolence ×35.3, euskal musika ×16.8, screamo ×14.3 |
| Eibar | Gipuzkoa | 37 | 13 | 2009–2025 | 8 % | rock (14), electronic (10), ambient electronic (9), bidehuts (7), metal (7) | soundscapes ×62.9, comedy ×54.5, ambient electronic ×52.6, groove metal ×30.1 |
| Oiartzun | Gipuzkoa | 35 | 15 | 2004–2024 | 23 % | punk (14), hip-hop/rap (11), rap (11), hip hop (9), hardcore (8) | oi ×86.5, occitan ×64.9, street punk ×43.2, trap ×24.7 |
| Tolosa | Gipuzkoa | 34 | 16 | 1998–2025 | 0 % | rock (9), grindcore (8), metal (8), punk (8), crust (7) | raggamuffin ×33.4, dancehall ×12.4, crust ×11.8, grindcore ×8.4 |
| Andoain | Gipuzkoa | 33 | 14 | 1983–2026 | 42 % | rock (19), pop (14), soul (14), electronic (9), experimental (9) | flamenco ×133.8, fantasy ×103.2, horror ×60.7, euskaraz ×24.6 |
| Hernani | Gipuzkoa | 32 | 14 | 2005–2026 | 12 % | punk (14), rock (11), oi! (10), oi! streetpunk (8), skinhead (8) | oi! streetpunk ×189.2, skinhead ×61.0, oi! ×26.0, instrumental ×8.2 |
| Oñati | Gipuzkoa | 29 | 19 | 2012–2026 | 7 % | rock (16), alternative (6), punk (5), 70s (3), free jazz (3) | free jazz ×11.0, post-hardcore ×3.7, post-punk ×2.5, rock ×2.1 |
| Tutera | Nafarroa | 22 | 14 | 2010–2023 | 0 % | rock (14), hard rock (8), alternative (7), rock and roll (5), surf rock (4) | surf rock ×47.5, garage rock ×28.7, hard rock ×17.2, rock and roll ×14.3 |
| Zumaia | Gipuzkoa | 22 | 9 | 2014–2026 | 0 % | rock (12), experimental (8), rock & roll (6), blues (5), blues rock (5) | blues rock ×41.0, rock & roll ×14.4, blues ×13.4, folk ×4.2 |
| Laudio | Araba | 21 | 13 | 2001–2025 | 19 % | rock (8), post-rock (5), acoustic (4), alternative rock;  laudio (4), cantautor (4) | folk pop ×51.5, cantautor ×28.8, post-rock ×11.7, post-hardcore ×6.8 |
| Azpeitia | Gipuzkoa | 18 | 11 | 2006–2026 | 17 % | punk (6), rock (6), street punk (4), alternative (3), hardcore punk (3) | street punk ×42.0, hardcore punk ×4.7, punk ×1.9, alternative ×1.3 |
| Lekeitio | Bizkaia | 17 | 7 | 2010–2026 | 47 % | cloud rap (6), hip hop (6), hip-hop/rap (6), rap (6), trap (6) | trap ×38.2, rap ×11.8, hip hop ×10.6, hip-hop/rap ×9.1 |
| Bergara | Gipuzkoa | 16 | 10 | 2011–2024 | 25 % | punk (8), hardcore (7), punk rock (7), rock (5), euskera (4) | skate punk ×83.5, euskera ×34.4, metalcore ×13.0, post-hardcore ×9.0 |
| Ermua | Bizkaia | 16 | 9 | 2006–2025 | 0 % | rock (7), metal (4), punk (4), alternative (3), diy (3) | diy ×18.0, metal ×1.8, rock ×1.7, alternative ×1.5 |
| Mungia | Bizkaia | 15 | 7 | 1996–2025 | 0 % | alternative (5), melodic hardcore (5), punk (5), skatepunk (5), pop (4) | skatepunk ×168.2, melodic hardcore ×51.5, pop ×2.7, alternative ×2.7 |
| Baiona | Iparralde | 14 | 5 | 2007–2024 | 0 % | alternative (9), rock (6), bidehuts (4), drummond (4), italo noise (4) | bidehuts ×32.3, hardcore punk ×6.0, alternative ×5.1, hardcore ×2.5 |
| Kanbo | Iparralde | 13 | 13 | 2019–2024 | 100 % | belarri (13), euskal musika (13), musika (13), world (13), contemporary (2) | belarri ×582.1, musika ×378.4, euskal musika ×72.8, world ×36.9 |
| Amurrio | Araba | 12 | 9 | 2008–2026 | 33 % | metal (5), alternative (4), crossover (4), groove metal (4), hardcore (4) | crossover ×78.8, groove metal ×74.2, hardcore ×3.9, metal ×3.0 |
| Hendaia | Iparralde | 12 | 3 | 2005–2025 | 0 % | rock (10), rock compilation (10), alternative (1), antzerkia (1), electronic (1) | rock compilation ×630.7, rock ×3.2 |
| Berriz | Bizkaia | 11 | 4 | 2010–2024 | 0 % | ambient (5), electronic (5), experimental (5), hardcore (5), idm (5) | idm ×23.2, industrial ×19.1, noise ×11.0, ambient ×6.1 |
| Mendaro | Gipuzkoa | 11 | 2 | 2003–2023 | 0 % | electronica (10), indie (10), punk (10), rock (10), munlet (7) | electronica ×31.9, indie ×27.3, post-punk ×11.0, punk ×5.1 |
| Sopela | Bizkaia | 11 | 3 | 2014–2021 | 9 % | doom (10), hardcore (10), metal (9), sludge (9), black metal (5) | sludge ×72.8, doom ×58.8, stoner ×42.5, black metal ×13.2 |
| Basauri | Bizkaia | 10 | 5 | 2009–2025 | 0 % | punk (7), hardcore punk (4), punk rock (3), rock (3), skate punk (3) | skatepunk ×151.4, skate punk ×133.6, hardcore punk ×11.3, punk rock ×4.6 |
| Itsasu | Iparralde | 9 | 2 | 2020–2025 | 100 % | alternative (9), basque music (9), eklektrik (9), pop rock (9), txomin larronde (9) | basque music ×49.5, pop rock ×29.0, alternative ×8.0 |
| Zumarraga | Gipuzkoa | 9 | 3 | 2004–2023 | 0 % | punk (5), punk rock (5), rock (5), rock'n'speed (5), death metal (3) | melodic death metal ×45.0, death metal ×9.0, punk rock ×8.5, punk ×3.1 |
| Arrigorriaga | Bizkaia | 8 | 1 | 2020–2025 | 0 % | basque music (8), death metal (8), heavy metal (8), metal (8), thrash metal (8) | thrash metal ×75.7, heavy metal ×74.9, basque music ×49.5, death metal ×27.0 |
| Bera | Nafarroa | 8 | 4 | 2013–2022 | 0 % | alternative (6), alternative rock (6), rock (2), 90s rock (1), angry (1) | alternative rock ×23.3, alternative ×6.0 |
| Legazpi | Gipuzkoa | 8 | 3 | 2010–2024 | 0 % | bloody rock (6), hard rock (6), high energy rock'n'roll (6), punk rock (6), rock (6) | hard rock ×35.5, punk rock ×11.4, rock ×2.9 |
| Urretxu | Gipuzkoa | 8 | 4 | 2014–2023 | 0 % | rock (6), hard rock (5), blues rock (4), country (4), rock and roll (4) | blues rock ×90.1, country ×49.1, rock and roll ×31.5, hard rock ×29.6 |
| Hazparne | Iparralde | 7 | 3 | 2012–2025 | 0 % | folk (6), alternative (5), grunge (5), indie (5), basque music (2) | grunge ×53.5, indie ×21.4, folk ×15.7, alternative ×5.7 |
| Galdakao | Bizkaia | 6 | 5 | 2015–2025 | 0 % | punk (4), punk rock (3), melodic hardcore (2), metal (2), post-hardcore (2) | punk rock ×7.6, punk ×3.7 |
| Ispaster | Bizkaia | 6 | 1 | 2012–2017 | 0 % | alternative (6), beruna (6), crust (6), doom (6), sludge (6) | sludge ×89.0, doom ×64.7, crust ×57.3, alternative ×8.0 |
| Lasarte-Oria | Gipuzkoa | 6 | 5 | 2010–2024 | 0 % | alternative (2), black metal (2), death metal (2), euskal musika (2), metal (2) |  |
| Sestao | Bizkaia | 6 | 6 | 2014–2024 | 67 % | electro glam (4), electronic (4), techno house (4), techno punk (4), batucada (1) | electronic ×3.6 |
| Lekunberri | Nafarroa | 5 | 2 | 2014–2017 | 0 % | lekunberri (5), indie (4), metal (4), punk (4), punk rock (4) | indie ×24.0, punk rock ×12.2, metal ×5.8, punk ×4.5 |
| Orio | Gipuzkoa | 5 | 2 | 2011–2021 | 0 % | rock (5), ambient (4), experimental (4), instrumental (4), math-rock (4) | instrumental ×41.8, post-rock ×39.3, ambient ×10.8, experimental ×6.8 |
| Urnieta | Gipuzkoa | 5 | 1 | 2007–2014 | 0 % | post-hardcore (5), punk rock (5), rock (5), pop (2), alternative metal (1) | post-hardcore ×35.9, punk rock ×15.3, rock ×3.8 |
| Villabona-Amasa | Gipuzkoa | 5 | 2 | 2019–2023 | 0 % | rock (5), alternative rock (3), ambient rock (3), basque music (3), grunge (3) | melodic rock ×267.1, ambient rock ×216.2, grunge ×45.0, basque music ×29.7 |
| Abadiño | Bizkaia | 4 | 1 | 2010–2024 | 0 % | black metal (4), dark power metal (4), death metal (4), metal (4), power metal (4) | power metal ×199.2, black metal ×29.0, death metal ×27.0, metal ×7.2 |
| Donibane Lohizune | Iparralde | 4 | 4 | 2015–2017 | 75 % | electric human machines (3), electronic (3), experimental easy listening (3), baleapop (2), beleak (1) | electronic ×4.1 |
| Elortzibar | Nafarroa | 4 | 1 | 2010–2015 | 0 % | noáin, navarra (4), punk (4), punk-oi (1), punkoi (1) | punk ×5.6 |
| Getaria | Gipuzkoa | 4 | 2 | 2021–2025 | 0 % | getaria (4), punk (4), hardcore (3), punk rock (3), hardcore punk (2) | punk rock ×11.4, hardcore ×8.8, punk ×5.6 |
| Azkoitia | Gipuzkoa | 3 | 2 | 2016–2025 | 0 % | hardcore (3), rock (3), hard rock (2), metal (2), punk (2) | hardcore ×11.7, rock ×3.8 |
| Biarritz | Iparralde | 3 | 3 | 2011–2020 | 0 % | world (2), acoustic rock (1), andoken (1), bask and world music (1), boom bap (1) |  |
| Maule-Lextarre | Iparralde | 3 | 1 | 2018–2025 | 0 % | dub (3), ragga (3), raggamuffin (3), reggae (3), roots (3) | ragga ×630.7, raggamuffin ×378.4, roots ×71.4, dub ×31.0 |
| Moreda Araba | Araba | 3 | 1 | 2013–2018 | 0 % | blues (3), punk (3), rock (3), bluespunk (1) | blues ×59.1, punk ×5.6, rock ×3.8 |
| Zaldibar | Bizkaia | 3 | 1 | 2023–2026 | 0 % | alternative (3), basque music (3), pop (3), post-punk (3) | basque music ×49.5, post-punk ×24.3, pop ×10.1, alternative ×8.0 |
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

- live recording: ×26.3 (97 releases)
- deep tech: ×24.2 (25 releases)
- tropical: ×23.9 (45 releases)
- live: ×22.3 (97 releases)
- crust punk: ×21.9 (97 releases)
- rub a dub: ×18.6 (13 releases)
- raggamuffin: ×17.6 (13 releases)
- r&b/soul: ×16.9 (45 releases)
- mugre: ×14.8 (6 releases)
- one man band: ×13.6 (6 releases)

**¿Dónde aparece `noise`?** 314 releases en el archivo, 265 localizadas (84.4 %).

| Municipio | Releases con el tag | Releases del municipio | lift |
|---|---:|---:|---:|
| Bilbo | 128 | 2440 | ×1.3 |
| Donostia | 50 | 998 | ×1.2 |
| Gasteiz | 48 | 548 | ×2.1 |
| Iruñea | 14 | 911 | ×0.4 |
| Getxo | 10 | 93 | ×2.6 |
| Berriz | 5 | 11 | ×11.0 |
| Arrasate | 4 | 49 | ×2.0 |
| Azkaine | 2 | 2 | ×24.1 |
| Ondarroa | 2 | 39 | ×1.2 |
| Andoain | 1 | 33 | ×0.7 |

**¿Dónde aparece `hardcore`?** 648 releases en el archivo, 580 localizadas (89.5 %).

| Municipio | Releases con el tag | Releases del municipio | lift |
|---|---:|---:|---:|
| Bilbo | 181 | 2440 | ×0.9 |
| Zarautz | 105 | 279 | ×4.4 |
| Irun | 56 | 113 | ×5.8 |
| Donostia | 53 | 998 | ×0.6 |
| Gasteiz | 46 | 548 | ×1.0 |
| Iruñea | 23 | 911 | ×0.3 |
| Sopela | 10 | 11 | ×10.6 |
| Santurtzi | 10 | 75 | ×1.6 |
| Gernika-Lumo | 9 | 43 | ×2.4 |
| Oiartzun | 8 | 35 | ×2.7 |

**¿Dónde aparece `techno`?** 654 releases en el archivo, 623 localizadas (95.3 %).

| Municipio | Releases con el tag | Releases del municipio | lift |
|---|---:|---:|---:|
| Bilbo | 336 | 2440 | ×1.6 |
| Iruñea | 159 | 911 | ×2.0 |
| Donostia | 79 | 998 | ×0.9 |
| Gasteiz | 39 | 548 | ×0.8 |
| Portugalete | 3 | 40 | ×0.9 |
| Hondarribia | 2 | 59 | ×0.4 |
| Zizur Nagusia | 1 | 1 | ×11.6 |
| Sestao | 1 | 6 | ×1.9 |
| Hernani | 1 | 32 | ×0.4 |
| Errenteria | 1 | 58 | ×0.2 |

**¿Dónde aparece `trikitixa`?** 3 releases en el archivo, 3 localizadas (100.0 %).

| Municipio | Releases con el tag | Releases del municipio | lift |
|---|---:|---:|---:|
| Kanbo | 1 | 13 | ×194.1 |
| Portugalete | 1 | 40 | ×63.1 |
| Gasteiz | 1 | 548 | ×4.6 |

**¿Qué parte del catálogo tiene ubicación fiable?** 6439 de 7568 (85.1 %); con inferencia por artista, 6522 (86.2 %).

Consultas propias: `python3 scripts/locations.py query --place zarautz` o `--tag noise` (matriz municipio × tag y tag × municipio).
