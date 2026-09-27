# Mapa de fusión de tags — informe

Generado por `scripts/tag_merge_map.py` a partir de `data/bandcamp_bilbaotags_clean.json`. El mapa completo está en `data/derived/tag_merge_map.json`; el método, en `docs/tag-merge-map.md`.

## Resumen

| | |
|---|---|
| Discos | 8046 |
| Tags distintos (antes) | 5645 |
| Nodos navegables (después) | 459 |
| &nbsp;&nbsp;· genero | 321 |
| &nbsp;&nbsp;· lugar | 93 |
| &nbsp;&nbsp;· otro | 45 |
| Umbral de microgénero (MIN_DISCOS) | 5 |
| Tags en `resto` (sin nodo navegable) | 3059 |
| Discos cuyos tags caen todos en `resto` | 2 |

Grupos: `genero` (sin prefijo), `lugar:*` (aparte, nunca se funde con géneros), `otro:*` (formato, idioma, instrumento, escena, época) y `resto` (nombres de grupo, sellos, palabras sueltas: se conservan en el mapa pero no son nodo).

## Los 50 nodos más grandes

| # | Nodo | Grupo | Padre | Discos | Tags fusionados | Ejemplos de tags |
|---|---|---|---|---|---|---|
| 1 | rock | genero |  | 2209 | 99 | rock, euskal rock, oz rock, eclectic rock, spanish rock, kick ass … |
| 2 | electronic | genero |  | 1663 | 17 | electronic, electronica, electronic music, electronics, euzkadi electronic, folktronica … |
| 3 | punk | genero | rock | 1470 | 92 | punk, punk band, neopunk, political punk, political punk rock, egg punk … |
| 4 | alternative rock | genero | rock | 1189 | 25 | alternative, alternative rock, rock alternativo, rock alternative, alt rock, alternativo … |
| 5 | metal | genero | rock | 1125 | 47 | metal, extreme metal, modern metal, extreme music, spanish metal, basque metal … |
| 6 | lugar:euskal herria | lugar |  | 1089 | 26 | basque country, euskal herria, basque, basque music, euskadi, euskal musika … |
| 7 | lugar:donostia | lugar | lugar:gipuzkoa | 1080 | 7 | donostia, donostia san sebastián, donostia / san sebastián, donosti, donosti sound, san sebastian … |
| 8 | lugar:iruñea | lugar | lugar:nafarroa | 1025 | 4 | iruña, iruñea, beruna, pamplona sound |
| 9 | experimental | genero |  | 978 | 19 | experimental, experiemental, non-conventional, eclectic, eklektrik, experimental muzak … |
| 10 | pop | genero |  | 915 | 77 | pop, spanish pop, pop radical, amor, brioche pop, political pop … |
| 11 | techno | genero | electronic | 711 | 28 | techno, trance electro techno, deep techno, techno and variations, dark techno, leftfield techno … |
| 12 | hardcore | genero | punk | 699 | 50 | hardcore, hxc, hc, h.c., alternative hardcore, analcore … |
| 13 | ambient | genero | electronic | 677 | 24 | ambient, soundscape, sound textures, infinite loops, soundscapes, landscapes … |
| 14 | lugar:gasteiz | lugar | lugar:araba | 600 | 3 | vitoria gasteiz, gasteiz, vitoria |
| 15 | punk rock | genero | rock | 565 | 20 | punk rock, punk-rock, ramones, punk and roll, hyper-energetic, pop punk punk rock … |
| 16 | indie rock | genero | rock | 512 | 15 | indie, indie rock, mod indie, pixies, emo indie, indietronica … |
| 17 | lugar:bilbo | lugar | lugar:bizkaia | 504 | 5 | bilbao, bilbo, crudobilbao, bilbaomusikak, bilbo zaharra |
| 18 | lugar:spain | lugar |  | 501 | 10 | spain, zaragoza, españa, mallorca, valencia, toledo … |
| 19 | folk | genero |  | 468 | 47 | folk, traditional, traditional music, acoustic folk, traditional folk, folclore … |
| 20 | house | genero | electronic | 440 | 26 | house, house music, housemusic, 90s house, classic house, rally house … |
| 21 | hip hop | genero |  | 395 | 22 | hip-hop/rap, hip hop, rap & hip-hop, africanhiphop, afrihooop, horrorcore … |
| 22 | reggae | genero |  | 379 | 15 | reggae, reagge, 80s reggae, digi reggae, early reggae, electronic reggae … |
| 23 | noise | genero | experimental | 358 | 24 | noise, ruido, white noise, devotional noise, italo noise, zarata … |
| 24 | post-punk | genero | punk | 358 | 7 | post-punk, post, after punk, post-music, post punk., post punk revival … |
| 25 | rock & roll | genero | rock | 331 | 17 | rock & roll, rock and roll, rock'n'roll, r&r, rock 'n' roll, basque country rock & roll … |
| 26 | hardcore punk | genero | hardcore | 328 | 9 | hardcore punk, punk hardcore, youth crew, punk rock hardcore, raw hardcore, blackened hardcore punk … |
| 27 | acoustic | genero | folk | 309 | 14 | acoustic, acoustic guitar, acustico, acustica, acustic, accoustic … |
| 28 | death metal | genero | metal | 307 | 15 | death metal, death, oldschool death metal, death and roll, thrash death, black ov death … |
| 29 | lugar:zarautz | lugar | lugar:gipuzkoa | 301 | 1 | zarautz |
| 30 | black metal | genero | metal | 296 | 27 | black metal, black, blackened, basque black metal, melodic black metal, ambient black metal … |
| 31 | dark ambient | genero | ambient | 288 | 7 | dark ambient, dark, dark ambient noise, dark ambient drone, dark ambient music, dark emo cowboy sexy dream … |
| 32 | pop rock | genero | rock | 288 | 13 | pop rock, pop rock en español, alternative rock pop, basque pop-rock, garage pop rock, rock pop … |
| 33 | world music | genero | folk | 282 | 19 | world, world music, world beats, arabic, ethnic, world groove … |
| 34 | crust | genero | hardcore punk | 259 | 11 | crust, crust punk, crustcore, hardcore crust, stenchcore, emocrust … |
| 35 | rap | genero | hip hop | 254 | 26 | rap, euskal rap, rap alternative, rap español, rap latino, spanish rap … |
| 36 | dub | genero | reggae | 250 | 22 | dub, rub a dub, dubwise, uk dub, dub noir, lo-end dub … |
| 37 | electro | genero | electronic | 244 | 12 | electro, electro techno, electro electrobass breaks bass, electro glam, ghettotech, bounce … |
| 38 | grindcore | genero | hardcore | 239 | 8 | grindcore, grind, deathgrind, noisecore, brutal death grind, grind core … |
| 39 | doom metal | genero | metal | 226 | 12 | doom, doom metal, funeral doom, black sabbath, drone funeral doom, drone doom metal … |
| 40 | soundtrack | genero | instrumental | 225 | 17 | soundtrack, cinematic, bso, documentary music, film score, ost … |
| 41 | post-hardcore | genero | hardcore | 224 | 4 | post-hardcore, synth core, post-hc, synthcore |
| 42 | hard rock | genero | rock | 220 | 17 | hard rock, heavy rock, hardrock, rock metal, 70s hard rock, 80's hard rock … |
| 43 | jazz | genero |  | 209 | 29 | jazz, dark jazz, bebop, postjazz, punk jazz, traditional jazz … |
| 44 | industrial | genero | experimental | 205 | 9 | industrial, industria, post-industrial, dark industrial, rhythmic noise, death industrial … |
| 45 | post-rock | genero | rock | 191 | 6 | post-rock, ambient rock, post-folk, post rock instrumental, instrumental-post-rock, cinematic post rock |
| 46 | otro:euskaraz | otro | otro:idioma | 189 | 4 | euskara, euskera, euskaraz, euskaldun |
| 47 | psychedelic | genero |  | 185 | 18 | psychedelic, psicodelia, psych, psicodelico, psicodelic, trippy … |
| 48 | funk | genero | soul | 183 | 19 | funk, groove, funky, intrumental funk, funk rythm & blues, jazz-funk … |
| 49 | indie pop | genero | pop | 178 | 9 | indie pop, pop rock indie, indie pop rock, popindie, pop indie, indie rock pop … |
| 50 | roots reggae | genero | reggae | 176 | 10 | roots, roots reggae, reggae roots, conscious music, jah music, roots reggae dub … |

## Nodos por grupo

### genero (321 nodos)

rock (2209), electronic (1663), punk (1470), alternative rock (1189), metal (1125), experimental (978), pop (915), techno (711), hardcore (699), ambient (677), punk rock (565), indie rock (512), folk (468), house (440), hip hop (395), reggae (379), noise (358), post-punk (358), rock & roll (331), hardcore punk (328), acoustic (309), death metal (307), black metal (296), dark ambient (288), pop rock (288), world music (282), crust (259), rap (254), dub (250), electro (244), grindcore (239), doom metal (226), soundtrack (225), post-hardcore (224), hard rock (220), jazz (209), industrial (205), post-rock (191), psychedelic (185), funk (183), indie pop (178), roots reggae (176), minimal (175), instrumental (174), experimental electronic (169), blues (165), drone (163), singer-songwriter (162), free improvisation (161), latin (161), soul (160), garage rock (158), progressive rock (155), tech house (154), idm (152), dance (147), thrash metal (146), stoner rock (142), oi! (135), heavy metal (134), lo-fi (131), pop punk (131), deathcore (130), djent (125), classical (124), grunge (124), metalcore (121), abstract (120), synthpop (119), r&b (118), synth (109), emo (107), sludge metal (107), folk rock (102), beats (98), steppa (97), contemporary classical (96), country (95), dub techno (92), deep house (87), trap (86), brutal death metal (85), dungeon synth (84), avant-garde (81), downtempo (79), dream pop (75), free jazz (74), surf rock (73), screamo (72), ebm (71), ska (71), spoken word (71), power pop (68), slam (68), synthwave (68), new age (67), americana (65), sound art (65), melodic hardcore (64), hard techno (63), dancehall (62), dub reggae (62), noise rock (62), bass music (61), melodic death metal (59), drum & bass (58), melodic rock (58), shoegaze (57), urban (57), indie folk (56), psychedelic rock (56), darkwave (55), acid (54), street punk (54), trip hop (54), electro dub (52), underground hip hop (52), blues rock (51), breakbeat (51), glitch (51), power metal (51), field recording (50), groove metal (50), high energy rock (49), alternative pop (48), country rock (48), disco (48), post-metal (48), devotional (47), d-beat (45), gothic rock (43), industrial techno (43), chillout (42), euskal folk (42), nu jazz (42), rave (42), raw punk (42), electroacoustic (40), garage punk (40), folk pop (39), ambient electronic (38), bedroom pop (38), minimal techno (38), atmospheric (37), classic rock (37), jungle (37), poky (37), horror (36), infantil (36), krautrock (36), new wave (36), experimental rock (35), horror disco (34), neoclassical (34), hyperpop (33), trance (33), crossover (32), comedy (31), slowcore (31), fastcore (30), space rock (30), video game music (30), alternative metal (29), progressive metal (29), drone ambient (28), dubstep (28), instrumental hip-hop (28), old school (28), raggamuffin (28), vaporwave (28), atmospheric black metal (27), digicore (27), rap-metal (27), skate punk (27), sound system (27), synth punk (27), rocksteady (26), boom bap (25), flamenco (25), goregrind (25), instrumental rock (25), internetcore (25), swamp rock (25), uk garage (25), freak folk (24), digital reggae (23), powerviolence (23), anarcho punk (22), art rock (22), bossa nova (22), electronic rock (22), sampling (22), harsh noise (21), metalpunk (21), minimal house (21), swing (21), acoustic rock (20), cumbia (20), deathrock (20), glam rock (20), math rock (20), noise pop (20), reverbcore (20), jazz fusion (19), power electronics (19), southern rock (19), breakcore (18), industrial rock (18), melodic metal (18), orchestral (18), rockabilly (18), speed metal (18), afrobeat (17), celtic (17), dark folk (17), guaracha (17), musique concrete (17), raw black metal (17), uk 82 (17), alternative country (16), coldwave (16), experimental pop (16), jangle pop (16), nu metal (16), pagan metal (16), symphonic metal (16), chiptune (15), gothic metal (15), grime (15), instrumental reggae (15), neo crust (15), viking metal (15), acoustic pop (14), blackened doom (14), britpop (14), death doom metal (14), italo disco (14), occult rock (14), reggaeton (14), soft rock (14), 77 punk (13), afro (13), blackened punk (13), choral (13), folk metal (13), industrial metal (13), medieval (13), symphonic (13), chanson (12), freakbeat (12), funk rock (12), mpb (12), salsa (12), blackened crust (11), chamber pop (11), chillwave (11), dreampunk (11), ethereal (11), horror punk (11), postvore (11), psychobilly (11), skapunk (11), urban rock (11), a cappella (10), abstract hip-hop (10), berlin school (10), contemporary jazz (10), drill (10), melodic punk (10), no wave (10), otros géneros (10), bedroom rock (9), black death (9), dj (9), lovers rock (9), ritual ambient (9), trash rock (9), beatdown (8), blackgaze (8), drone doom (8), folk punk (8), gypsy jazz (8), hardcore techno (8), lo-fi hip-hop (8), mathcore (8), new beat (8), tribal (8), balearic (7), black thrash metal (7), dance-punk (7), latin jazz (7), lounge (7), neo-soul (7), pagan black metal (7), progressive house (7), psychedelic pop (7), pub rock (7), rumba (7), turntablism (7), boogie woogie (6), footwork (6), garage pop (6), groove death metal (6), jazz trio (6), minimal synth (6), smooth jazz (6), soul-jazz (6), surf pop (6), bluegrass (5), funk metal (5), gospel (5), indie punk (5), k pop (5), pop folk (5), pop jazz (5), proto-punk (5), punk rock alternative (5), rock'n'speed (5), samba (5), surf punk (5), tango (5)

### lugar (93 nodos)

lugar:euskal herria (1089), lugar:donostia (1080), lugar:iruñea (1025), lugar:gasteiz (600), lugar:bilbo (504), lugar:spain (501), lugar:zarautz (301), lugar:irun (124), lugar:france (117), lugar:getxo (107), lugar:madrid (96), lugar:barakaldo (82), lugar:santurtzi (79), lugar:gernika-lumo (67), lugar:bizkaia (66), lugar:hondarribia (66), lugar:errenteria (65), lugar:bermeo (62), lugar:nafarroa (60), lugar:arrasate (56), lugar:iparralde (52), lugar:gipuzkoa (51), lugar:united kingdom (51), lugar:leioa (49), lugar:portugalete (45), lugar:tolosa (45), lugar:barcelona (43), lugar:eibar (42), lugar:oiartzun (42), lugar:ondarroa (40), lugar:andoain (35), lugar:otros lugares (35), lugar:united states (35), lugar:oñati (34), lugar:hernani (31), lugar:hendaia (28), lugar:cantabria (27), lugar:afghanistan (25), lugar:argentina (25), lugar:laudio (25), lugar:zumaia (25), lugar:tutera (24), lugar:andalucia (23), lugar:azpeitia (22), lugar:mungia (22), lugar:baiona (20), lugar:lekeitio (20), lugar:ermua (19), lugar:sopela (19), lugar:bergara (18), lugar:mendaro (17), lugar:urretxu (17), lugar:mexico (16), lugar:germany (14), lugar:kanbo (13), lugar:amurrio (12), lugar:araba (12), lugar:basauri (12), lugar:karrantza (12), lugar:legazpi (12), lugar:lekunberri (12), lugar:zumarraga (12), lugar:bera (11), lugar:berriz (11), lugar:burgos (10), lugar:getaria (10), lugar:uruguay (10), lugar:zaldibia (10), lugar:hong kong (9), lugar:itsasu (9), lugar:japan (9), lugar:lasarte-oria (9), lugar:arrigorriaga (8), lugar:enkarterri (8), lugar:sestao (8), lugar:urnieta (8), lugar:antigua y barbuda (7), lugar:hazparne (7), lugar:markina-xemein (7), lugar:moreda araba (7), lugar:colombia (6), lugar:elgoibar (6), lugar:galdakao (6), lugar:ispaster (6), lugar:logroño (6), lugar:norway (6), lugar:sweden (6), lugar:villabona-amasa (6), lugar:beasain (5), lugar:burlata (5), lugar:italy (5), lugar:orio (5), lugar:thailand (5)

### otro (45 nodos)

otro:euskaraz (189), otro:diy (154), otro:en directo (131), otro:guitarra (70), otro:independiente (61), otro:underground (58), otro:voz (55), otro:piano (52), otro:castellano (48), otro:decada 80 (46), otro:digital (35), otro:versiones (35), otro:vinilo (31), otro:cassette (30), otro:vientos (29), otro:politica (27), otro:remix (25), otro:decada 90 (22), otro:maquinas (22), otro:año (20), otro:recopilatorio (18), otro:cello (17), otro:bateria (15), otro:copyleft (15), otro:teclados (15), otro:queer (13), otro:demo (12), otro:single (12), otro:vegan (12), otro:decada 70 (11), otro:occitan (11), otro:decada 60 (10), otro:formato (10), otro:cuerdas (9), otro:feminismo (8), otro:idioma (8), otro:percusion (7), otro:album (6), otro:antifa (6), otro:zanfona (6), otro:arpa (5), otro:violin (5), otro:época (5), otro:instrumento (4), otro:escena (1)

## Lo que cae en `resto`

3059 tags, 2228 discos con al menos uno. Los 40 más frecuentes (si alguno es un género, añadirlo a GENRE_TERMS o FULL_SYNONYMS):

bidehuts, massa confusa, eclectic reactions, ally morton, petruska records, label, music, musika, preqwal, sello, tony morton, wldv, symmatik, primavera sound, sonido muchacho, bass lee, belarri, kokoshca, aventuras de kirlian, ibon errazkin, le mans, matt o'brien, one man band, elefant records, mugre, xtreem music, lisabo, q ez da, senoid recordings, ballard, duo, retriever, trans, txomin larronde, clarty cat records, dut, munlet, arenna, bakarlaria, cujo

## Fusiones dudosas (para revisar)

Casos donde la regla podría estar uniendo cosas distintas: 707 tags marcados. Aquí los 180 con al menos 2 discos, ordenados por nº de discos; la lista completa (incluidos los de 1 disco) está en el campo `dudosas` del JSON.

| Tag | Discos | → Nodo | Motivo |
|---|---|---|---|
| alternative | 1023 | alternative rock | alternative a secas -> alternative rock |
| hip-hop/rap | 303 | hip hop | hip-hop/rap (umbrella de Bandcamp) -> hip hop |
| indie | 287 | indie rock | indie a secas -> indie rock |
| alternative rock | 271 | alternative rock | alternative (954 discos, umbrella de Bandcamp) se funde con alternative rock |
| indie rock | 246 | indie rock | indie (umbrella de Bandcamp) se funde con indie rock |
| electronica | 224 | electronic | electronica (en inglés puede ser un género propio) -> electronic |
| world | 213 | world music | world -> world music |
| doom | 127 | doom metal | doom -> doom metal |
| crust punk | 121 | crust | crust y crust punk se funden en un solo nodo |
| roots | 106 | roots reggae | roots -> roots reggae |
| garage | 97 | garage rock | garage -> garage rock (podría ser uk garage) |
| sludge | 94 | sludge metal | sludge -> sludge metal |
| stoner | 92 | stoner rock | stoner -> stoner rock |
| r&b/soul | 72 | r&b | r&b/soul (umbrella de Bandcamp) -> r&b |
| contemporary | 71 | contemporary classical | contemporary -> contemporary classical |
| trap | 71 | trap | trap (por umbral, cloud rap y autotune cuelgan aquí) |
| progressive | 64 | progressive rock | progressive a secas -> progressive rock |
| tropical | 51 | latin | tropical -> latin |
| dark | 50 | dark ambient | dark a secas -> dark ambient |
| soundscape | 46 | ambient | soundscape -> ambient |
| bumping | 34 | poky | bumping / hardbass / scouse house / bakalao / hard dance -> poky (escena makina) |
| hard dance | 34 | poky | hard dance -> poky |
| hardbass | 34 | poky | hardbass -> poky |
| scouse house | 34 | poky | scouse house -> poky |
| musica urbana | 31 | urban | urban / musica urbana como nodo propio |
| skinhead | 31 | oi! | skinhead (subcultura) -> oi! |
| acoustic guitar | 27 | acoustic | acoustic guitar -> acoustic |
| minimalism | 27 | minimal | minimalism (clásica) -> minimal (electrónica) |
| cinematic | 26 | soundtrack | cinematic -> soundtrack |
| heavy | 26 | heavy metal | heavy a secas -> heavy metal |
| euskal rock | 25 | rock | se ha quitado la parte de lugar/gentilicio |
| groove | 23 | funk | groove -> funk |
| rock alternativo | 22 | alternative rock | alternative (954 discos, umbrella de Bandcamp) se funde con alternative rock |
| death | 20 | death metal | death a secas -> death metal |
| post | 20 | post-punk | post a secas -> post punk |
| mod indie | 17 | indie rock | indie (umbrella de Bandcamp) se funde con indie rock |
| urban | 17 | urban | urban / musica urbana como nodo propio |
| trash | 16 | thrash metal | trash -> thrash metal (asumido como errata) |
| fuzz | 15 | garage rock | fuzz -> garage rock |
| melodic | 15 | melodic rock | melodic -> melodic rock |
| ibon errazkin | 12 | resto | se ha quitado la parte de lugar/gentilicio |
| rock alternative | 11 | alternative rock | alternative (954 discos, umbrella de Bandcamp) se funde con alternative rock |
| epic | 10 | power metal | epic -> power metal (podría ser soundtrack) |
| urban pop | 10 | urban | urban / musica urbana como nodo propio |
| autotune | 9 | trap | trap (por umbral, cloud rap y autotune cuelgan aquí) |
| reverb | 9 | reverbcore | reverb -> reverbcore |
| crustcore | 8 | crust | crustcore -> crust |
| euskal rap | 8 | rap | se ha quitado la parte de lugar/gentilicio |
| ramones | 8 | punk rock | nombre de grupo usado como tag -> punk rock |
| space | 8 | space rock | space -> space rock |
| alt rock | 7 | alternative rock | alternative (954 discos, umbrella de Bandcamp) se funde con alternative rock |
| alternativo | 7 | alternative rock | alternative (954 discos, umbrella de Bandcamp) se funde con alternative rock |
| black | 7 | black metal | black a secas -> black metal |
| classic | 7 | classic rock | classic -> classic rock |
| deep | 7 | deep house | deep -> deep house |
| basque rock alternative | 6 | alternative rock | se ha quitado la parte de lugar/gentilicio; alternative (954 discos, umbrella de Bandcamp) se funde con alternative rock |
| cloud rap | 6 | trap | trap (por umbral, cloud rap y autotune cuelgan aquí) |
| happy | 6 | pop | happy -> pop |
| trap music | 6 | trap | trap (por umbral, cloud rap y autotune cuelgan aquí) |
| trash metal | 6 | thrash metal | trash metal -> thrash metal (asumido como errata) |
| alternativa | 5 | alternative rock | alternative (954 discos, umbrella de Bandcamp) se funde con alternative rock |
| basque black metal | 5 | black metal | se ha quitado la parte de lugar/gentilicio |
| basque metal | 5 | metal | se ha quitado la parte de lugar/gentilicio |
| pixies | 5 | indie rock | nombre de grupo usado como tag -> indie rock |
| rock en español | 5 | rock | se ha quitado la parte de lugar/gentilicio |
| rock español | 5 | rock | se ha quitado la parte de lugar/gentilicio |
| songs | 5 | pop | songs / canciones -> pop |
| summer | 5 | pop | summer -> pop |
| urban music | 5 | urban | urban / musica urbana como nodo propio |
| 90s rock | 4 | alternative rock | alternative (954 discos, umbrella de Bandcamp) se funde con alternative rock |
| alternative hardcore | 4 | hardcore | alternativas: alternative rock; más de una palabra era nodo |
| alternative rock; laudio | 4 | alternative rock | alternative (954 discos, umbrella de Bandcamp) se funde con alternative rock |
| basque rock | 4 | rock | se ha quitado la parte de lugar/gentilicio |
| cold | 4 | coldwave | cold -> coldwave |
| contryrock | 4 | country rock | posible errata fusionada con 'country rock' |
| crossover thrash | 4 | thrash metal | alternativas: crossover; más de una palabra era nodo |
| dark industrial | 4 | industrial | alternativas: dark ambient; más de una palabra era nodo |
| emo indie | 4 | indie rock | alternativas: emo; más de una palabra era nodo |
| euzkadi electronic | 4 | electronic | se ha quitado la parte de lugar/gentilicio |
| experimental metal | 4 | metal | alternativas: experimental; más de una palabra era nodo |
| folktronica | 4 | electronic | alternativas: folk; raíz pegada separada; más de una palabra era nodo |
| horrorcore | 4 | hip hop | alternativas: hardcore; raíz pegada separada; más de una palabra era nodo |
| latin rock | 4 | rock | alternativas: latin; más de una palabra era nodo |
| melodic black metal | 4 | black metal | alternativas: melodic rock, metal; más de una palabra era nodo |
| pop en español | 4 | pop | se ha quitado la parte de lugar/gentilicio |
| pop rock en español | 4 | pop rock | se ha quitado la parte de lugar/gentilicio |
| rap español | 4 | rap | se ha quitado la parte de lugar/gentilicio |
| urbano | 4 | urban | urban / musica urbana como nodo propio |
| 80's hard rock | 3 | hard rock | alternativas: rock; más de una palabra era nodo |
| afterpunk | 3 | punk | raíz pegada separada |
| ambient black metal | 3 | black metal | alternativas: ambient, metal; más de una palabra era nodo |
| analcore | 3 | hardcore | raíz pegada separada |
| basque hardcore | 3 | hardcore | se ha quitado la parte de lugar/gentilicio |
| basque heavy metal | 3 | heavy metal | se ha quitado la parte de lugar/gentilicio |
| dark jazz | 3 | jazz | alternativas: dark ambient; más de una palabra era nodo |
| emocrust | 3 | crust | raíz pegada separada; más de una palabra era nodo |
| g-funk | 3 | hip hop | alternativas: funk; más de una palabra era nodo |
| harcore | 3 | hardcore | posible errata fusionada con 'hardcore' |
| indie electronic | 3 | electronic | alternativas: indie rock; más de una palabra era nodo |
| medieval black metal | 3 | black metal | alternativas: medieval, metal; más de una palabra era nodo |
| melodic hard rock | 3 | hard rock | alternativas: melodic rock, rock; más de una palabra era nodo |
| metal euskadi | 3 | metal | se ha quitado la parte de lugar/gentilicio |
| metal spain | 3 | metal | se ha quitado la parte de lugar/gentilicio |
| punk español | 3 | punk | se ha quitado la parte de lugar/gentilicio |
| rave punk | 3 | punk | alternativas: rave; más de una palabra era nodo |
| rock melodico | 3 | melodic rock | alternativas: rock; más de una palabra era nodo |
| 90's rock | 2 | alternative rock | alternative (954 discos, umbrella de Bandcamp) se funde con alternative rock |
| african pop | 2 | pop | alternativas: afro; más de una palabra era nodo |
| alternative rock pop | 2 | pop rock | alternativas: alternative rock, rock, pop; más de una palabra era nodo |
| alternativo en español | 2 | alternative rock | se ha quitado la parte de lugar/gentilicio; alternative (954 discos, umbrella de Bandcamp) se funde con alternative rock |
| anarcho-folk | 2 | folk punk | alternativas: folk; más de una palabra era nodo |
| baleapop | 2 | pop | raíz pegada separada |
| basque country rock & roll | 2 | rock & roll | se ha quitado la parte de lugar/gentilicio |
| basque pop | 2 | pop | se ha quitado la parte de lugar/gentilicio |
| basque pop-rock | 2 | pop rock | se ha quitado la parte de lugar/gentilicio |
| bass ambient | 2 | ambient | alternativas: bass music; más de una palabra era nodo |
| black sabbath | 2 | doom metal | nombre de grupo usado como tag -> doom metal |
| celtic rock | 2 | rock | alternativas: celtic; más de una palabra era nodo |
| chicago blues | 2 | blues | se ha quitado la parte de lugar/gentilicio |
| core | 2 | hardcore | core a secas -> hardcore |
| death industrial | 2 | industrial | alternativas: death metal; más de una palabra era nodo |
| easycore | 2 | hardcore | raíz pegada separada |
| ebm techno | 2 | techno | alternativas: ebm; más de una palabra era nodo |
| electro swing | 2 | swing | alternativas: electro; más de una palabra era nodo |
| emo rock | 2 | rock | alternativas: emo; más de una palabra era nodo |
| epic dungeon synth | 2 | dungeon synth | alternativas: power metal, synth; más de una palabra era nodo |
| experimetal | 2 | experimental | posible errata fusionada con 'experimental' |
| folktronic | 2 | folk | raíz pegada separada |
| funk soul | 2 | soul | alternativas: funk; más de una palabra era nodo |
| funky rock | 2 | rock | alternativas: funk; más de una palabra era nodo |
| garage pop rock | 2 | pop rock | alternativas: garage rock, pop, rock; más de una palabra era nodo |
| grunge metal | 2 | metal | alternativas: grunge; más de una palabra era nodo |
| hardcore pop punk | 2 | pop punk | alternativas: hardcore, pop, punk; más de una palabra era nodo |
| hardcore punk fastcore | 2 | fastcore | alternativas: hardcore, punk; más de una palabra era nodo |
| heavy blues rock | 2 | blues rock | alternativas: heavy metal, blues, rock; más de una palabra era nodo |
| horrorsynth | 2 | synth | raíz pegada separada; más de una palabra era nodo |
| indie electronic rock | 2 | electronic rock | alternativas: indie rock, electronic, rock; más de una palabra era nodo |
| indie lo-fi | 2 | lo-fi | alternativas: indie rock; más de una palabra era nodo |
| indietronica | 2 | indie rock | raíz pegada separada |
| industrial rock alternative | 2 | alternative rock | alternativas: industrial, rock; más de una palabra era nodo |
| jazz punk | 2 | punk | alternativas: jazz; más de una palabra era nodo |
| jazz-funk | 2 | funk | alternativas: jazz; más de una palabra era nodo |
| lofi dungeon synth | 2 | dungeon synth | alternativas: lo-fi, synth; más de una palabra era nodo |
| metal alternativo | 2 | alternative rock | alternativas: metal; más de una palabra era nodo |
| militant dungeon synth | 2 | dungeon synth | alternativas: synth; más de una palabra era nodo |
| modern rock | 2 | alternative rock | alternative (954 discos, umbrella de Bandcamp) se funde con alternative rock |
| motorpunk | 2 | punk | raíz pegada separada |
| musica garage bilbao | 2 | garage rock | se ha quitado la parte de lugar/gentilicio |
| música urbana | 2 | urban | urban / musica urbana como nodo propio |
| navecore | 2 | hardcore | raíz pegada separada |
| pinkpunk | 2 | punk | raíz pegada separada |
| pop punk punk rock | 2 | punk rock | alternativas: pop, punk, rock; más de una palabra era nodo |
| postjazz | 2 | jazz | raíz pegada separada; más de una palabra era nodo |
| protometal | 2 | metal | raíz pegada separada |
| psicocríticopunk | 2 | punk | raíz pegada separada |
| punk jazz | 2 | jazz | alternativas: punk; más de una palabra era nodo |
| punk vasco | 2 | punk | se ha quitado la parte de lugar/gentilicio |
| queer punk | 2 | punk | alternativas: hardcore; raíz pegada separada; más de una palabra era nodo |
| queercore | 2 | punk | alternativas: hardcore; raíz pegada separada; más de una palabra era nodo |
| rage against the machine | 2 | rap-metal | nombre de grupo usado como tag -> rap metal |
| rap en español | 2 | rap | se ha quitado la parte de lugar/gentilicio |
| ravecore | 2 | hardcore | raíz pegada separada; más de una palabra era nodo |
| riot folk | 2 | folk punk | alternativas: folk; más de una palabra era nodo |
| rock fusion | 2 | jazz fusion | alternativas: rock; más de una palabra era nodo |
| rock indie | 2 | indie rock | indie (umbrella de Bandcamp) se funde con indie rock |
| rock n f@#k$!'roll | 2 | rock & roll | posible errata fusionada con 'rock and roll' |
| rock roll punk-rock-stoner | 2 | stoner rock | alternativas: rock, punk; más de una palabra era nodo |
| rock sinfonico | 2 | rock | alternativas: symphonic; más de una palabra era nodo |
| sinthpop | 2 | synthpop | posible errata fusionada con 'synthpop' |
| sludgecore | 2 | hardcore | raíz pegada separada; más de una palabra era nodo |
| soul punk | 2 | punk | alternativas: soul; más de una palabra era nodo |
| spanish guitar | 2 | otro:guitarra | se ha quitado la parte de lugar/gentilicio |
| streepunk | 2 | street punk | posible errata fusionada con 'street punk' |
| synth core | 2 | post-hardcore | alternativas: hardcore; raíz pegada separada; más de una palabra era nodo |
| synthrock | 2 | rock | raíz pegada separada; más de una palabra era nodo |
| techno; downtempo; electro | 2 | electro | alternativas: techno, downtempo; más de una palabra era nodo |
| traditional jazz | 2 | jazz | alternativas: folk; más de una palabra era nodo |
| trap-fusión triste | 2 | trap | trap (por umbral, cloud rap y autotune cuelgan aquí) |
| trash death groove metal | 2 | groove metal | alternativas: thrash metal, death metal, funk, metal; más de una palabra era nodo |
| urbano latino | 2 | latin | alternativas: urban; más de una palabra era nodo |

