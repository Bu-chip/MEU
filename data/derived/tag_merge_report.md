# Mapa de fusión de tags — informe

Generado por `scripts/tag_merge_map.py` a partir de `data/bandcamp_bilbaotags_clean.json`. El mapa completo está en `data/derived/tag_merge_map.json`; el método, en `docs/tag-merge-map.md`.

## Resumen

| | |
|---|---|
| Discos | 7637 |
| Tags distintos (antes) | 5575 |
| Nodos navegables (después) | 452 |
| &nbsp;&nbsp;· genero | 319 |
| &nbsp;&nbsp;· lugar | 88 |
| &nbsp;&nbsp;· otro | 45 |
| Umbral de microgénero (MIN_DISCOS) | 5 |
| Tags en `resto` (sin nodo navegable) | 2979 |
| Discos cuyos tags caen todos en `resto` | 2 |

Grupos: `genero` (sin prefijo), `lugar:*` (aparte, nunca se funde con géneros), `otro:*` (formato, idioma, instrumento, escena, época) y `resto` (nombres de grupo, sellos, palabras sueltas: se conservan en el mapa pero no son nodo).

## Los 50 nodos más grandes

| # | Nodo | Grupo | Padre | Discos | Tags fusionados | Ejemplos de tags |
|---|---|---|---|---|---|---|
| 1 | rock | genero |  | 2048 | 97 | rock, euskal rock, oz rock, eclectic rock, spanish rock, power trio … |
| 2 | electronic | genero |  | 1611 | 19 | electronic, electronica, electronic music, electronics, euzkadi electronic, folktronica … |
| 3 | punk | genero | rock | 1378 | 88 | punk, neopunk, political punk, political punk rock, egg punk, pathetic punk … |
| 4 | alternative rock | genero | rock | 1108 | 27 | alternative, alternative rock, rock alternativo, alt rock, alternativo, basque rock alternative … |
| 5 | metal | genero | rock | 1074 | 49 | metal, extreme metal, modern metal, extreme music, extreme underground sounds, spanish metal … |
| 6 | lugar:euskal herria | lugar |  | 1070 | 26 | basque country, euskal herria, basque, basque music, euskadi, euskal musika … |
| 7 | lugar:donostia | lugar | lugar:gipuzkoa | 1033 | 7 | donostia, donostia san sebastián, donostia / san sebastián, donosti, san sebastian, donosti sound … |
| 8 | lugar:iruñea | lugar | lugar:nafarroa | 969 | 4 | iruña, iruñea, beruna, pamplona sound |
| 9 | experimental | genero |  | 953 | 19 | experimental, experiemental, non-conventional, eclectic, eklektrik, experimental muzak … |
| 10 | pop | genero |  | 850 | 73 | pop, spanish pop, pop radical, brioche pop, amor, happy … |
| 11 | techno | genero | electronic | 696 | 28 | techno, trance electro techno, deep techno, techno and variations, dark techno, leftfield techno … |
| 12 | hardcore | genero | punk | 676 | 50 | hardcore, hxc, hc, h.c., alternative hardcore, basque hardcore … |
| 13 | ambient | genero | electronic | 667 | 25 | ambient, soundscape, sound textures, infinite loops, soundscapes, ambient. … |
| 14 | lugar:gasteiz | lugar | lugar:araba | 571 | 3 | vitoria gasteiz, gasteiz, vitoria |
| 15 | punk rock | genero | rock | 528 | 21 | punk rock, punk-rock, ramones, hyper-energetic, pop punk punk rock, punk 'n' roll … |
| 16 | lugar:spain | lugar |  | 495 | 10 | spain, zaragoza, españa, mallorca, valencia, toledo … |
| 17 | indie rock | genero | rock | 456 | 15 | indie, indie rock, mod indie, pixies, emo indie, indie rock. … |
| 18 | folk | genero |  | 441 | 45 | folk, traditional, traditional music, traditional folk, folclore, herri&b … |
| 19 | house | genero | electronic | 431 | 26 | house, house music, housemusic, 90s house, classic house, rally house … |
| 20 | hip hop | genero |  | 386 | 21 | hip-hop/rap, hip hop, rap & hip-hop, africanhiphop, afrihooop, horrorcore … |
| 21 | reggae | genero |  | 376 | 14 | reggae, reagge, 80s reggae, digi reggae, early reggae, electronic reggae … |
| 22 | lugar:bilbo | lugar | lugar:bizkaia | 370 | 6 | bilbao, bilbo, crudobilbao, bilbaomusikak, bilbo zaharra, bilbao. |
| 23 | noise | genero | experimental | 340 | 24 | noise, ruido, white noise, italo noise, devotional noise, zarata … |
| 24 | post-punk | genero | punk | 334 | 6 | post-punk, post, after punk, post punk., post-music, post-punk revival |
| 25 | rock & roll | genero | rock | 311 | 17 | rock & roll, rock and roll, rock'n'roll, r&r, rock 'n' roll, basque country rock & roll … |
| 26 | hardcore punk | genero | hardcore | 310 | 9 | hardcore punk, punk hardcore, youth crew, punk rock hardcore, raw hardcore, blackened hardcore punk … |
| 27 | death metal | genero | metal | 294 | 15 | death metal, death, oldschool death metal, death and roll, thrash death, black ov death … |
| 28 | black metal | genero | metal | 288 | 26 | black metal, black, blackened, basque black metal, melodic black metal, ambient black metal … |
| 29 | dark ambient | genero | ambient | 286 | 7 | dark ambient, dark, dark ambient noise, dark ambient drone, dark ambient music, dark emo cowboy sexy dream … |
| 30 | lugar:zarautz | lugar | lugar:gipuzkoa | 284 | 1 | zarautz |
| 31 | acoustic | genero | folk | 274 | 15 | acoustic, acoustic guitar, acustico, acustica, acoustic guitar solo, acustic … |
| 32 | pop rock | genero | rock | 273 | 12 | pop rock, pop rock en español, basque pop-rock, garage pop rock, rock pop, alternative pop rock … |
| 33 | world music | genero | folk | 268 | 19 | world, world music, world beats, arabic, ethnic, world groove … |
| 34 | crust | genero | hardcore punk | 255 | 12 | crust, crust punk, crustcore, hardcore crust, stenchcore, emocrust … |
| 35 | dub | genero | reggae | 248 | 21 | dub, rub a dub, dubwise, uk dub, dub noir, lo-end dub … |
| 36 | rap | genero | hip hop | 246 | 27 | rap, euskal rap, rap alternative, rap español, rap latino, spanish rap … |
| 37 | electro | genero | electronic | 241 | 12 | electro, electro techno, electro electrobass breaks bass, electro glam, ghettotech, bounce … |
| 38 | grindcore | genero | hardcore | 234 | 8 | grindcore, grind, deathgrind, noisecore, brutal death grind, grind core … |
| 39 | soundtrack | genero | instrumental | 224 | 17 | soundtrack, cinematic, bso, documentary music, film score, ost … |
| 40 | doom metal | genero | metal | 215 | 12 | doom, doom metal, funeral doom, black sabbath, drone funeral doom, drone doom metal … |
| 41 | post-hardcore | genero | hardcore | 215 | 4 | post-hardcore, synth core, post-hc, synthcore |
| 42 | jazz | genero |  | 205 | 30 | jazz, dark jazz, bebop, jazz., postjazz, punk jazz … |
| 43 | industrial | genero | experimental | 199 | 9 | industrial, industria, post-industrial, dark industrial, rhythmic noise, abstract industrial … |
| 44 | hard rock | genero | rock | 197 | 17 | hard rock, heavy rock, hardrock, rock metal, 70s hard rock, hard rock-hard blues … |
| 45 | otro:euskaraz | otro | otro:idioma | 187 | 4 | euskara, euskera, euskaraz, euskaldun |
| 46 | post-rock | genero | rock | 184 | 6 | post-rock, ambient rock, post-folk, post rock instrumental, instrumental-post-rock, cinematic post rock |
| 47 | funk | genero | soul | 178 | 20 | funk, groove, funky, intrumental funk, funk rythm & blues, funk. … |
| 48 | roots reggae | genero | reggae | 175 | 10 | roots, roots reggae, reggae roots, conscious music, jah music, roots reggae dub … |
| 49 | instrumental | genero |  | 169 | 9 | instrumental, instrumentals, instrumental guitar, almost instrumental, guitar instrumental, lofi instrumental … |
| 50 | psychedelic | genero |  | 169 | 17 | psychedelic, psicodelia, psych, psicodelic, trippy, psicodelico … |

## Nodos por grupo

### genero (319 nodos)

rock (2048), electronic (1611), punk (1378), alternative rock (1108), metal (1074), experimental (953), pop (850), techno (696), hardcore (676), ambient (667), punk rock (528), indie rock (456), folk (441), house (431), hip hop (386), reggae (376), noise (340), post-punk (334), rock & roll (311), hardcore punk (310), death metal (294), black metal (288), dark ambient (286), acoustic (274), pop rock (273), world music (268), crust (255), dub (248), rap (246), electro (241), grindcore (234), soundtrack (224), doom metal (215), post-hardcore (215), jazz (205), industrial (199), hard rock (197), post-rock (184), funk (178), roots reggae (175), instrumental (169), psychedelic (169), minimal (167), experimental electronic (163), drone (161), indie pop (159), free improvisation (158), latin (158), blues (156), soul (155), tech house (154), idm (152), progressive rock (152), singer-songwriter (152), garage rock (147), dance (141), thrash metal (141), oi! (131), stoner rock (131), deathcore (127), heavy metal (127), lo-fi (127), classical (124), pop punk (124), djent (122), abstract (120), metalcore (120), r&b (117), synthpop (114), grunge (113), synth (108), emo (102), folk rock (99), beats (98), sludge metal (98), steppa (97), contemporary classical (96), dub techno (92), country (89), deep house (87), trap (86), brutal death metal (85), dungeon synth (84), avant-garde (79), downtempo (79), dream pop (74), free jazz (73), surf rock (72), screamo (71), ska (70), spoken word (70), ebm (69), new age (67), synthwave (67), power pop (64), sound art (64), slam (63), dancehall (62), hard techno (62), bass music (61), dub reggae (61), melodic hardcore (59), noise rock (59), americana (58), drum & bass (58), melodic death metal (58), urban (57), psychedelic rock (56), shoegaze (54), acid (53), melodic rock (53), trip hop (53), electro dub (52), indie folk (51), street punk (51), underground hip hop (51), breakbeat (50), field recording (50), glitch (50), blues rock (48), darkwave (48), disco (48), groove metal (48), country rock (47), high energy rock (47), post-metal (47), power metal (45), d-beat (43), industrial techno (43), euskal folk (42), gothic rock (42), alternative pop (41), chillout (41), nu jazz (41), rave (41), raw punk (41), devotional (40), electroacoustic (40), ambient electronic (37), folk pop (37), garage punk (37), jungle (37), minimal techno (37), poky (37), atmospheric (36), horror (36), infantil (36), bedroom pop (35), krautrock (35), horror disco (34), neoclassical (34), classic rock (33), crossover (32), experimental rock (32), hyperpop (32), new wave (32), trance (32), slowcore (31), comedy (30), fastcore (30), space rock (30), video game music (30), progressive metal (29), dubstep (28), instrumental hip-hop (28), raggamuffin (28), alternative metal (27), atmospheric black metal (27), sound system (27), digicore (26), drone ambient (26), rocksteady (26), flamenco (25), goregrind (25), instrumental rock (25), old school (25), synth punk (25), uk garage (25), boom bap (24), internetcore (24), swamp rock (24), rap-metal (23), skate punk (23), vaporwave (23), anarcho punk (22), art rock (22), bossa nova (22), digital reggae (22), powerviolence (22), sampling (22), deathrock (20), math rock (20), minimal house (20), noise pop (20), swing (20), cumbia (19), glam rock (19), jazz fusion (19), metalpunk (19), southern rock (19), acoustic rock (18), breakcore (18), freak folk (18), harsh noise (18), industrial rock (18), orchestral (18), reverbcore (18), afrobeat (17), raw black metal (17), rockabilly (17), uk 82 (17), celtic (16), coldwave (16), melodic metal (16), musique concrete (16), pagan metal (16), speed metal (16), symphonic metal (16), alternative country (15), chiptune (15), dark folk (15), electronic rock (15), experimental pop (15), grime (15), guaracha (15), instrumental reggae (15), neo crust (15), viking metal (15), acoustic pop (14), blackened doom (14), gothic metal (14), italo disco (14), jangle pop (14), nu metal (14), occult rock (14), reggaeton (14), soft rock (14), 77 punk (13), blackened punk (13), choral (13), death doom metal (13), folk metal (13), industrial metal (13), medieval (13), power electronics (13), symphonic (13), afro (12), chanson (12), mpb (12), britpop (11), chamber pop (11), chillwave (11), dreampunk (11), ethereal (11), funk rock (11), horror punk (11), postvore (11), psychobilly (11), salsa (11), a cappella (10), abstract hip-hop (10), berlin school (10), blackened crust (10), contemporary jazz (10), drill (10), freakbeat (10), no wave (10), otros géneros (10), bedroom rock (9), dj (9), lovers rock (9), melodic punk (9), ritual ambient (9), trash rock (9), black death (8), blackgaze (8), drone doom (8), gypsy jazz (8), hardcore techno (8), lo-fi hip-hop (8), mathcore (8), new beat (8), urban rock (8), balearic (7), black thrash metal (7), folk punk (7), latin jazz (7), lounge (7), neo-soul (7), pagan black metal (7), progressive house (7), psychedelic pop (7), pub rock (7), rumba (7), ska punk (7), tribal (7), turntablism (7), beatdown (6), boogie woogie (6), dance-punk (6), footwork (6), garage pop (6), groove death metal (6), jazz trio (6), minimal synth (6), smooth jazz (6), soul-jazz (6), surf pop (6), bluegrass (5), gospel (5), indie punk (5), k pop (5), pop folk (5), pop jazz (5), proto-punk (5), rock'n'speed (5), samba (5), surf punk (5), tango (5)

### lugar (88 nodos)

lugar:euskal herria (1070), lugar:donostia (1033), lugar:iruñea (969), lugar:gasteiz (571), lugar:spain (495), lugar:bilbo (370), lugar:zarautz (284), lugar:irun (123), lugar:france (117), lugar:getxo (104), lugar:madrid (95), lugar:santurtzi (78), lugar:barakaldo (72), lugar:bizkaia (65), lugar:gernika-lumo (64), lugar:errenteria (63), lugar:hondarribia (63), lugar:bermeo (57), lugar:arrasate (55), lugar:gipuzkoa (55), lugar:nafarroa (54), lugar:iparralde (52), lugar:leioa (49), lugar:united kingdom (48), lugar:portugalete (45), lugar:barcelona (42), lugar:oiartzun (42), lugar:tolosa (41), lugar:ondarroa (39), lugar:eibar (37), lugar:andoain (35), lugar:otros lugares (35), lugar:united states (35), lugar:oñati (32), lugar:hernani (31), lugar:hendaia (28), lugar:cantabria (27), lugar:afghanistan (25), lugar:laudio (25), lugar:zumaia (24), lugar:andalucia (23), lugar:tutera (22), lugar:azpeitia (21), lugar:argentina (20), lugar:baiona (20), lugar:lekeitio (20), lugar:bergara (18), lugar:ermua (18), lugar:mungia (17), lugar:mexico (16), lugar:germany (14), lugar:kanbo (13), lugar:mendaro (13), lugar:amurrio (12), lugar:araba (12), lugar:karrantza (12), lugar:zumarraga (12), lugar:berriz (11), lugar:sopela (11), lugar:urretxu (11), lugar:basauri (10), lugar:bera (10), lugar:burgos (10), lugar:getaria (10), lugar:uruguay (10), lugar:hong kong (9), lugar:itsasu (9), lugar:arrigorriaga (8), lugar:enkarterri (8), lugar:japan (8), lugar:lasarte-oria (8), lugar:legazpi (8), lugar:antigua y barbuda (7), lugar:hazparne (7), lugar:urnieta (7), lugar:colombia (6), lugar:galdakao (6), lugar:ispaster (6), lugar:logroño (6), lugar:norway (6), lugar:sestao (6), lugar:sweden (6), lugar:burlata (5), lugar:italy (5), lugar:lekunberri (5), lugar:orio (5), lugar:thailand (5), lugar:villabona-amasa (5)

### otro (45 nodos)

otro:euskaraz (187), otro:diy (139), otro:en directo (129), otro:guitarra (63), otro:independiente (61), otro:underground (56), otro:voz (54), otro:piano (51), otro:castellano (43), otro:decada 80 (39), otro:digital (35), otro:vinilo (31), otro:cassette (30), otro:vientos (29), otro:politica (27), otro:versiones (24), otro:decada 90 (21), otro:maquinas (21), otro:año (20), otro:remix (20), otro:recopilatorio (18), otro:cello (17), otro:copyleft (15), otro:bateria (14), otro:teclados (14), otro:queer (13), otro:demo (12), otro:single (12), otro:decada 70 (11), otro:occitan (11), otro:vegan (11), otro:decada 60 (10), otro:formato (10), otro:cuerdas (9), otro:feminismo (8), otro:idioma (8), otro:percusion (7), otro:album (6), otro:antifa (6), otro:zanfona (6), otro:arpa (5), otro:violin (5), otro:época (5), otro:instrumento (4), otro:escena (1)

## Lo que cae en `resto`

2979 tags, 2127 discos con al menos uno. Los 40 más frecuentes (si alguno es un género, añadirlo a GENRE_TERMS o FULL_SYNONYMS):

bidehuts, eclectic reactions, massa confusa, ally morton, petruska records, label, music, musika, sello, preqwal, tony morton, wldv, symmatik, belarri, kokoshca, primavera sound, sonido muchacho, aventuras de kirlian, bass lee, ibon errazkin, le mans, matt o'brien, one man band, elefant records, mugre, xtreem music, lisabo, senoid recordings, ballard, retriever, txomin larronde, clarty cat records, duo, dut, munlet, arenna, bakarlaria, cujo, family, jackie purver

## Fusiones dudosas (para revisar)

Casos donde la regla podría estar uniendo cosas distintas: 696 tags marcados. Aquí los 170 con al menos 2 discos, ordenados por nº de discos; la lista completa (incluidos los de 1 disco) está en el campo `dudosas` del JSON.

| Tag | Discos | → Nodo | Motivo |
|---|---|---|---|
| alternative | 954 | alternative rock | alternative a secas -> alternative rock |
| hip-hop/rap | 294 | hip hop | hip-hop/rap (umbrella de Bandcamp) -> hip hop |
| indie | 252 | indie rock | indie a secas -> indie rock |
| alternative rock | 245 | alternative rock | alternative (954 discos, umbrella de Bandcamp) se funde con alternative rock |
| indie rock | 221 | indie rock | indie (umbrella de Bandcamp) se funde con indie rock |
| electronica | 219 | electronic | electronica (en inglés puede ser un género propio) -> electronic |
| world | 205 | world music | world -> world music |
| crust punk | 121 | crust | crust y crust punk se funden en un solo nodo |
| doom | 117 | doom metal | doom -> doom metal |
| roots | 106 | roots reggae | roots -> roots reggae |
| garage | 89 | garage rock | garage -> garage rock (podría ser uk garage) |
| sludge | 85 | sludge metal | sludge -> sludge metal |
| stoner | 81 | stoner rock | stoner -> stoner rock |
| r&b/soul | 72 | r&b | r&b/soul (umbrella de Bandcamp) -> r&b |
| contemporary | 71 | contemporary classical | contemporary -> contemporary classical |
| trap | 70 | trap | trap (por umbral, cloud rap y autotune cuelgan aquí) |
| progressive | 63 | progressive rock | progressive a secas -> progressive rock |
| tropical | 51 | latin | tropical -> latin |
| dark | 50 | dark ambient | dark a secas -> dark ambient |
| soundscape | 45 | ambient | soundscape -> ambient |
| bumping | 34 | poky | bumping / hardbass / scouse house / bakalao / hard dance -> poky (escena makina) |
| hard dance | 34 | poky | hard dance -> poky |
| hardbass | 34 | poky | hardbass -> poky |
| scouse house | 34 | poky | scouse house -> poky |
| musica urbana | 31 | urban | urban / musica urbana como nodo propio |
| skinhead | 31 | oi! | skinhead (subcultura) -> oi! |
| cinematic | 26 | soundtrack | cinematic -> soundtrack |
| minimalism | 26 | minimal | minimalism (clásica) -> minimal (electrónica) |
| euskal rock | 25 | rock | se ha quitado la parte de lugar/gentilicio |
| heavy | 25 | heavy metal | heavy a secas -> heavy metal |
| acoustic guitar | 24 | acoustic | acoustic guitar -> acoustic |
| groove | 20 | funk | groove -> funk |
| death | 18 | death metal | death a secas -> death metal |
| post | 18 | post-punk | post a secas -> post punk |
| rock alternativo | 18 | alternative rock | alternative (954 discos, umbrella de Bandcamp) se funde con alternative rock |
| mod indie | 17 | indie rock | indie (umbrella de Bandcamp) se funde con indie rock |
| urban | 17 | urban | urban / musica urbana como nodo propio |
| fuzz | 15 | garage rock | fuzz -> garage rock |
| trash | 15 | thrash metal | trash -> thrash metal (asumido como errata) |
| melodic | 14 | melodic rock | melodic -> melodic rock |
| ibon errazkin | 12 | resto | se ha quitado la parte de lugar/gentilicio |
| urban pop | 10 | urban | urban / musica urbana como nodo propio |
| autotune | 9 | trap | trap (por umbral, cloud rap y autotune cuelgan aquí) |
| epic | 9 | power metal | epic -> power metal (podría ser soundtrack) |
| reverb | 9 | reverbcore | reverb -> reverbcore |
| crustcore | 8 | crust | crustcore -> crust |
| euskal rap | 8 | rap | se ha quitado la parte de lugar/gentilicio |
| space | 8 | space rock | space -> space rock |
| classic | 7 | classic rock | classic -> classic rock |
| deep | 7 | deep house | deep -> deep house |
| ramones | 7 | punk rock | nombre de grupo usado como tag -> punk rock |
| alt rock | 6 | alternative rock | alternative (954 discos, umbrella de Bandcamp) se funde con alternative rock |
| alternativo | 6 | alternative rock | alternative (954 discos, umbrella de Bandcamp) se funde con alternative rock |
| basque rock alternative | 6 | alternative rock | se ha quitado la parte de lugar/gentilicio; alternative (954 discos, umbrella de Bandcamp) se funde con alternative rock |
| black | 6 | black metal | black a secas -> black metal |
| cloud rap | 6 | trap | trap (por umbral, cloud rap y autotune cuelgan aquí) |
| happy | 6 | pop | happy -> pop |
| rock alternative | 6 | alternative rock | alternative (954 discos, umbrella de Bandcamp) se funde con alternative rock |
| trap music | 6 | trap | trap (por umbral, cloud rap y autotune cuelgan aquí) |
| trash metal | 6 | thrash metal | trash metal -> thrash metal (asumido como errata) |
| alternativa | 5 | alternative rock | alternative (954 discos, umbrella de Bandcamp) se funde con alternative rock |
| basque black metal | 5 | black metal | se ha quitado la parte de lugar/gentilicio |
| pixies | 5 | indie rock | nombre de grupo usado como tag -> indie rock |
| rock en español | 5 | rock | se ha quitado la parte de lugar/gentilicio |
| rock español | 5 | rock | se ha quitado la parte de lugar/gentilicio |
| songs | 5 | pop | songs / canciones -> pop |
| summer | 5 | pop | summer -> pop |
| urban music | 5 | urban | urban / musica urbana como nodo propio |
| 90s rock | 4 | alternative rock | alternative (954 discos, umbrella de Bandcamp) se funde con alternative rock |
| alternative hardcore | 4 | hardcore | alternativas: alternative rock; más de una palabra era nodo |
| alternative rock;  laudio | 4 | alternative rock | alternative (954 discos, umbrella de Bandcamp) se funde con alternative rock |
| basque metal | 4 | metal | se ha quitado la parte de lugar/gentilicio |
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
| afterpunk | 3 | punk | raíz pegada separada |
| ambient black metal | 3 | black metal | alternativas: ambient, metal; más de una palabra era nodo |
| basque hardcore | 3 | hardcore | se ha quitado la parte de lugar/gentilicio |
| basque heavy metal | 3 | heavy metal | se ha quitado la parte de lugar/gentilicio |
| dark jazz | 3 | jazz | alternativas: dark ambient; más de una palabra era nodo |
| emocrust | 3 | crust | raíz pegada separada; más de una palabra era nodo |
| funk metal | 3 | metal | alternativas: funk; más de una palabra era nodo |
| g-funk | 3 | hip hop | alternativas: funk; más de una palabra era nodo |
| harcore | 3 | hardcore | posible errata fusionada con 'hardcore' |
| indie electronic | 3 | electronic | alternativas: indie rock; más de una palabra era nodo |
| medieval black metal | 3 | black metal | alternativas: medieval, metal; más de una palabra era nodo |
| metal euskadi | 3 | metal | se ha quitado la parte de lugar/gentilicio |
| punk español | 3 | punk | se ha quitado la parte de lugar/gentilicio |
| 90's rock | 2 | alternative rock | alternative (954 discos, umbrella de Bandcamp) se funde con alternative rock |
| alternativo en español | 2 | alternative rock | se ha quitado la parte de lugar/gentilicio; alternative (954 discos, umbrella de Bandcamp) se funde con alternative rock |
| anarcho-folk | 2 | folk punk | alternativas: folk; más de una palabra era nodo |
| baleapop | 2 | pop | raíz pegada separada |
| basque country rock & roll | 2 | rock & roll | se ha quitado la parte de lugar/gentilicio |
| basque pop | 2 | pop | se ha quitado la parte de lugar/gentilicio |
| basque pop-rock | 2 | pop rock | se ha quitado la parte de lugar/gentilicio |
| bass ambient | 2 | ambient | alternativas: bass music; más de una palabra era nodo |
| black sabbath | 2 | doom metal | nombre de grupo usado como tag -> doom metal |
| core | 2 | hardcore | core a secas -> hardcore |
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
| indie lo-fi | 2 | lo-fi | alternativas: indie rock; más de una palabra era nodo |
| indie rock. | 2 | indie rock | indie (umbrella de Bandcamp) se funde con indie rock |
| indietronica | 2 | indie rock | raíz pegada separada |
| industrial rock alternative | 2 | alternative rock | alternativas: industrial, rock; más de una palabra era nodo |
| jazz punk | 2 | punk | alternativas: jazz; más de una palabra era nodo |
| jazz-funk | 2 | funk | alternativas: jazz; más de una palabra era nodo |
| lofi dungeon synth | 2 | dungeon synth | alternativas: lo-fi, synth; más de una palabra era nodo |
| melodic hard rock | 2 | hard rock | alternativas: melodic rock, rock; más de una palabra era nodo |
| metal alternativo | 2 | alternative rock | alternativas: metal; más de una palabra era nodo |
| metal spain. | 2 | metal | se ha quitado la parte de lugar/gentilicio |
| militant dungeon synth | 2 | dungeon synth | alternativas: synth; más de una palabra era nodo |
| modern rock | 2 | alternative rock | alternative (954 discos, umbrella de Bandcamp) se funde con alternative rock |
| motorpunk | 2 | punk | raíz pegada separada |
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
| rave punk | 2 | punk | alternativas: rave; más de una palabra era nodo |
| ravecore | 2 | hardcore | raíz pegada separada; más de una palabra era nodo |
| riot folk | 2 | folk punk | alternativas: folk; más de una palabra era nodo |
| rock fusion | 2 | jazz fusion | alternativas: rock; más de una palabra era nodo |
| rock indie | 2 | indie rock | indie (umbrella de Bandcamp) se funde con indie rock |
| rock melodico | 2 | melodic rock | alternativas: rock; más de una palabra era nodo |
| rock n f@#k$!'roll | 2 | rock & roll | posible errata fusionada con 'rock and roll' |
| rock roll punk-rock-stoner | 2 | stoner rock | alternativas: rock, punk; más de una palabra era nodo |
| rock sinfonico | 2 | rock | alternativas: symphonic; más de una palabra era nodo |
| sludgecore | 2 | hardcore | raíz pegada separada; más de una palabra era nodo |
| soul punk | 2 | punk | alternativas: soul; más de una palabra era nodo |
| spanish guitar | 2 | otro:guitarra | se ha quitado la parte de lugar/gentilicio |
| streepunk | 2 | street punk | posible errata fusionada con 'street punk' |
| synth core | 2 | post-hardcore | alternativas: hardcore; raíz pegada separada; más de una palabra era nodo |
| synthrock | 2 | rock | raíz pegada separada; más de una palabra era nodo |
| traditional jazz | 2 | jazz | alternativas: folk; más de una palabra era nodo |
| trap-fusión triste | 2 | trap | trap (por umbral, cloud rap y autotune cuelgan aquí) |
| urbano latino | 2 | latin | alternativas: urban; más de una palabra era nodo |

