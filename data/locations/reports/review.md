# Revisión manual de ubicaciones

*Generado por `python3 scripts/locations.py normalize`. No editar a mano: las decisiones van en `data/locations/rules.json` (`values`, `outside`, `place_overrides`) o en `data/locations/manual.json` (por release).*

Cada fila es un **texto crudo** tal como lo dio Bandcamp. `rel.` = releases del canónico con ese texto como observación directa; `cuentas` = cuentas de Bandcamp distintas que lo usan.

## Sin regla (¿municipio nuevo, barrio, errata?) — 0 valores, 0 releases

Ninguno.

## Topónimo del ámbito con país incoherente — 6 valores, 27 releases

| Texto crudo | rel. | obs. | cuentas | Motivo |
|---|---:|---:|---:|---|
| Navarre, Florida | 13 | 13 | 1 | región del ámbito con país «Florida» (nafarroa) |
| Pamplona, Colombia | 6 | 6 | 4 | topónimo del ámbito con país «Colombia» (irunea) |
| Irun, Nigeria | 5 | 5 | 2 | topónimo del ámbito con país «Nigeria» (irun) |
| Bayonne, New Jersey | 1 | 1 | 1 | topónimo del ámbito con país «New Jersey» (baiona) |
| Guernica, Argentina | 1 | 1 | 1 | topónimo del ámbito con país «Argentina» (gernika-lumo) |
| San Sebastián, Chile | 1 | 1 | 1 | topónimo del ámbito con país «Chile» (donostia) |

## Ambiguos — 1 valores, 1 releases

| Texto crudo | rel. | obs. | cuentas | Motivo |
|---|---:|---:|---:|---|
| PM | 1 | 1 | 1 | manual: posible código de provincia (Baleares); sin país ni municipio |

## Inválidos o improbables (regla manual) — 1 valores, 24 releases

| Texto crudo | rel. | obs. | cuentas | Motivo |
|---|---:|---:|---:|---|
| Afghanistan | 24 | 24 | 1 | manual: ubicación no literal: la usa solo la cuenta del sello navarro Mendeku Diskak (Orreaga 778, Cuero…); revisado 2026-09-19 |

## Fuera de Euskal Herria — 115 valores, 283 releases

| Texto crudo | rel. | obs. | cuentas | Motivo |
|---|---:|---:|---:|---|
| Madrid, Spain | 53 | 57 | 21 | lugar fuera del ámbito (lista controlada) |
| Barcelona, Spain | 19 | 20 | 16 | lugar fuera del ámbito (lista controlada) |
| Punta Del Este, Uruguay | 10 | 10 | 5 | fuera de ES/FR (Uruguay) |
| Zaragoza, Spain | 10 | 10 | 2 | lugar fuera del ámbito (lista controlada) |
| La Línea De La Concepción, Spain | 9 | 9 | 1 | lugar fuera del ámbito (lista controlada) |
| Buenos Aires, Argentina | 7 | 7 | 5 | fuera de ES/FR (Argentina) |
| Paris, France | 7 | 7 | 6 | lugar fuera del ámbito (lista controlada) |
| London, UK | 6 | 8 | 2 | fuera de ES/FR (UK) |
| Berlin, Germany | 5 | 6 | 5 | fuera de ES/FR (Germany) |
| Occitanie, France | 5 | 5 | 1 | lugar fuera del ámbito (lista controlada) |
| Santander, Spain | 5 | 5 | 3 | lugar fuera del ámbito (lista controlada) |
| Thailand | 5 | 5 | 1 | lugar fuera del ámbito (lista controlada) |
| Burgos, Spain | 4 | 5 | 1 | lugar fuera del ámbito (lista controlada) |
| Logroño, Spain | 4 | 4 | 2 | lugar fuera del ámbito (lista controlada) |
| Denmark | 3 | 5 | 2 | lugar fuera del ámbito (lista controlada) |
| Argentina | 3 | 3 | 2 | lugar fuera del ámbito (lista controlada) |
| Los Angeles, California | 3 | 3 | 3 | fuera de ES/FR (California) |
| Magallanes y la Antártica Chilen, Chile | 3 | 3 | 1 | fuera de ES/FR (Chile) |
| Oviedo, Spain | 3 | 3 | 3 | lugar fuera del ámbito (lista controlada) |
| Toulouse, France | 3 | 3 | 3 | lugar fuera del ámbito (lista controlada) |
| UK | 3 | 3 | 3 | lugar fuera del ámbito (lista controlada) |
| Seville, Spain | 2 | 6 | 2 | lugar fuera del ámbito (lista controlada) |
| Valencia, Spain | 2 | 5 | 3 | lugar fuera del ámbito (lista controlada) |
| Nantes, France | 2 | 3 | 2 | lugar fuera del ámbito (lista controlada) |
| Alto Paraná Department, Paraguay | 2 | 2 | 1 | fuera de ES/FR (Paraguay) |
| Belgium | 2 | 2 | 2 | lugar fuera del ámbito (lista controlada) |
| Brighton And Hove, UK | 2 | 2 | 2 | fuera de ES/FR (UK) |
| Castellón De La Plana, Spain | 2 | 2 | 2 | lugar fuera del ámbito (lista controlada) |
| Chiyoda, Japan | 2 | 2 | 1 | fuera de ES/FR (Japan) |
| Czech Republic | 2 | 2 | 1 | lugar fuera del ámbito (lista controlada) |
| La Plata, Argentina | 2 | 2 | 2 | fuera de ES/FR (Argentina) |
| New York, New York | 2 | 2 | 2 | fuera de ES/FR (New York) |
| Norfolk Island | 2 | 2 | 1 | lugar fuera del ámbito (lista controlada) |
| Pau, France | 2 | 2 | 2 | lugar fuera del ámbito (lista controlada) |
| Principado de Asturias, Spain | 2 | 2 | 1 | lugar fuera del ámbito (lista controlada) |
| San Francisco, California | 2 | 2 | 1 | fuera de ES/FR (California) |
| Stavanger, Norway | 2 | 2 | 1 | fuera de ES/FR (Norway) |
| Sweden | 2 | 2 | 2 | lugar fuera del ámbito (lista controlada) |
| Súa, Gabon | 2 | 2 | 1 | fuera de ES/FR (Gabon) |
| Trøndelag, Norway | 2 | 2 | 1 | fuera de ES/FR (Norway) |
| Vietnam | 2 | 2 | 1 | lugar fuera del ámbito (lista controlada) |
| Vigo, Spain | 2 | 2 | 1 | lugar fuera del ámbito (lista controlada) |
| El Bierzo, Spain | 1 | 4 | 1 | lugar fuera del ámbito (lista controlada) |
| Talavera De La Reina, Spain | 1 | 3 | 1 | lugar fuera del ámbito (lista controlada) |
| Italy | 1 | 2 | 1 | lugar fuera del ámbito (lista controlada) |
| Nashville, Tennessee | 1 | 2 | 1 | fuera de ES/FR (Tennessee) |
| Alexandria, Virginia | 1 | 1 | 1 | fuera de ES/FR (Virginia) |
| Alliance, Ohio | 1 | 1 | 1 | fuera de ES/FR (Ohio) |
| Andorra | 1 | 1 | 1 | lugar fuera del ámbito (lista controlada) |
| Angers, France | 1 | 1 | 1 | lugar fuera del ámbito (lista controlada) |
| Armenia | 1 | 1 | 1 | lugar fuera del ámbito (lista controlada) |
| Asturias, Spain | 1 | 1 | 1 | lugar fuera del ámbito (lista controlada) |
| Barcelona | 1 | 1 | 1 | lugar fuera del ámbito (lista controlada) |
| Bath, UK | 1 | 1 | 1 | fuera de ES/FR (UK) |
| Bogotá, Colombia | 1 | 1 | 1 | fuera de ES/FR (Colombia) |
| Bordeaux, France | 1 | 1 | 1 | lugar fuera del ámbito (lista controlada) |
| British Columbia | 1 | 1 | 1 | lugar fuera del ámbito (lista controlada) |
| Brussels, Belgium | 1 | 1 | 1 | fuera de ES/FR (Belgium) |
| Bucharest, Romania | 1 | 1 | 1 | fuera de ES/FR (Romania) |
| CT, Spain | 1 | 1 | 1 | lugar fuera del ámbito (lista controlada) |
| Caldwell, Idaho | 1 | 1 | 1 | fuera de ES/FR (Idaho) |
| D.F., Mexico | 1 | 1 | 1 | fuera de ES/FR (Mexico) |
| Don Benito, Spain | 1 | 1 | 1 | lugar fuera del ámbito (lista controlada) |
| Dubai, UAE | 1 | 1 | 1 | fuera de ES/FR (UAE) |
| Dublin, Ireland | 1 | 1 | 1 | fuera de ES/FR (Ireland) |
| El Mas De Flors, Spain | 1 | 1 | 1 | lugar fuera del ámbito (lista controlada) |
| Fukuoka, Japan | 1 | 1 | 1 | fuera de ES/FR (Japan) |
| Girona, Spain | 1 | 1 | 1 | lugar fuera del ámbito (lista controlada) |
| Goldendale, Washington | 1 | 1 | 1 | fuera de ES/FR (Washington) |
| Havana, Cuba | 1 | 1 | 1 | fuera de ES/FR (Cuba) |
| Helsinki, Finland | 1 | 1 | 1 | fuera de ES/FR (Finland) |
| Hong Kong | 1 | 1 | 1 | lugar fuera del ámbito (lista controlada) |
| Jonesboro, Arkansas | 1 | 1 | 1 | fuera de ES/FR (Arkansas) |
| La Frontera, Spain | 1 | 1 | 1 | lugar fuera del ámbito (lista controlada) |
| Liège, Belgium | 1 | 1 | 1 | fuera de ES/FR (Belgium) |
| Marseille, France | 1 | 1 | 1 | lugar fuera del ámbito (lista controlada) |
| Medina De Pomar, Spain | 1 | 1 | 1 | lugar fuera del ámbito (lista controlada) |
| Mexico City, Mexico | 1 | 1 | 1 | fuera de ES/FR (Mexico) |
| Milan, Italy | 1 | 1 | 1 | fuera de ES/FR (Italy) |
| Montreal, Québec | 1 | 1 | 1 | fuera de ES/FR (Québec) |
| Murrieta, California | 1 | 1 | 1 | fuera de ES/FR (California) |
| München, Germany | 1 | 1 | 1 | fuera de ES/FR (Germany) |
| Newcastle Upon Tyne, UK | 1 | 1 | 1 | fuera de ES/FR (UK) |
| Nigrán, Spain | 1 | 1 | 1 | lugar fuera del ámbito (lista controlada) |
| Novi Sad, Serbia | 1 | 1 | 1 | fuera de ES/FR (Serbia) |
| Oslo, Norway | 1 | 1 | 1 | fuera de ES/FR (Norway) |
| Pennsylvania | 1 | 1 | 1 | lugar fuera del ámbito (lista controlada) |
| Perth, Australia | 1 | 1 | 1 | fuera de ES/FR (Australia) |
| Portugal | 1 | 1 | 1 | lugar fuera del ámbito (lista controlada) |
| Pratdip, Spain | 1 | 1 | 1 | lugar fuera del ámbito (lista controlada) |
| Princeton, Illinois | 1 | 1 | 1 | fuera de ES/FR (Illinois) |
| Puerto Rico | 1 | 1 | 1 | lugar fuera del ámbito (lista controlada) |
| Salamanca, Spain | 1 | 1 | 1 | lugar fuera del ámbito (lista controlada) |
| Sankt Peterburg, Russian Federation | 1 | 1 | 1 | fuera de ES/FR (Russian Federation) |
| Santiago, Chile | 1 | 1 | 1 | fuera de ES/FR (Chile) |
| Sevilla, Spain | 1 | 1 | 1 | lugar fuera del ámbito (lista controlada) |
| Singapore | 1 | 1 | 1 | lugar fuera del ámbito (lista controlada) |
| Switzerland | 1 | 1 | 1 | lugar fuera del ámbito (lista controlada) |
| Tarragona, Spain | 1 | 1 | 1 | lugar fuera del ámbito (lista controlada) |
| Tbilisi, Georgia | 1 | 1 | 1 | fuera de ES/FR (Georgia) |
| Thessaloniki, Greece | 1 | 1 | 1 | fuera de ES/FR (Greece) |
| Tokyo, Japan | 1 | 1 | 1 | fuera de ES/FR (Japan) |
| Toreno, Spain | 1 | 1 | 1 | lugar fuera del ámbito (lista controlada) |
| Toronto, Ontario | 1 | 1 | 1 | fuera de ES/FR (Ontario) |
| Torrevieja, Spain | 1 | 1 | 1 | lugar fuera del ámbito (lista controlada) |
| Tours, France | 1 | 1 | 1 | lugar fuera del ámbito (lista controlada) |
| Ukraine | 1 | 1 | 1 | lugar fuera del ámbito (lista controlada) |
| Vancouver, British Columbia | 1 | 1 | 1 | fuera de ES/FR (British Columbia) |
| Varmland County, Sweden | 1 | 1 | 1 | fuera de ES/FR (Sweden) |
| Wallonia, Belgium | 1 | 1 | 1 | fuera de ES/FR (Belgium) |
| Washington, D.C. | 1 | 1 | 1 | fuera de ES/FR (D.C.) |
| Western Sahara | 1 | 1 | 1 | lugar fuera del ámbito (lista controlada) |
| Worcester, UK | 1 | 1 | 1 | fuera de ES/FR (UK) |
| Nice, France | 0 | 2 | 1 | lugar fuera del ámbito (lista controlada) |
| Brittany, France | 0 | 1 | 1 | lugar fuera del ámbito (lista controlada) |

## Solo región, comarca o país (sin municipio) — 14 valores, 515 releases

| Texto crudo | rel. | obs. | cuentas | Motivo |
|---|---:|---:|---:|---|
| PV, Spain | 184 | 189 | 96 | el valor completo es una región (euskal-herria) |
| Basque Country, Spain | 117 | 117 | 34 | el valor completo es una región (euskal-herria) |
| Euskadi, Spain | 76 | 77 | 18 | el valor completo es una región (euskal-herria) |
| France | 73 | 76 | 12 | el valor completo es una región (france) |
| Spain | 35 | 42 | 22 | el valor completo es una región (spain) |
| Enkarterri, Spain | 6 | 6 | 3 | región/comarca, sin municipio (enkarterri) |
| Navarre, Spain | 6 | 6 | 4 | región/comarca, sin municipio (nafarroa) |
| PV | 5 | 5 | 3 | el valor completo es una región (euskal-herria) |
| Nafarroa, Spain | 4 | 4 | 2 | el valor completo es una región (nafarroa) |
| Aquitaine Limousin Poitou-Charen, France | 3 | 3 | 1 | región/comarca, sin municipio (nouvelle-aquitaine) |
| Arratia Nerbioi, Spain | 2 | 2 | 2 | región/comarca, sin municipio (arratia-nerbioi) |
| NC, Spain | 2 | 2 | 2 | el valor completo es una región (nafarroa) |
| Navarra, Spain | 1 | 1 | 1 | el valor completo es una región (nafarroa) |
| Nouvelle-Aquitaine, France | 1 | 1 | 1 | región/comarca, sin municipio (nouvelle-aquitaine) |

## Resueltos a municipio — 104 municipios

| Municipio | Territorio | Textos crudos (releases) |
|---|---|---|
| Donostia (`donostia`) | Gipuzkoa | Donostia San Sebastian, Spain (479); San Sebastián, Spain (370); Donostia San Sebastián, Spain (68); Donostia / San Sebastián, Spain (48); Donostia, Spain (18); Donostia (4) |
| Bilbo (`bilbo`) | Bizkaia | Bilbao, Spain (940); Bilbo, Spain (29); Bilbao (1) |
| Iruñea (`irunea`) | Nafarroa | Pamplona, Spain (905); Iruña, Spain (2) |
| Gasteiz (`gasteiz`) | Araba | Vitoria Gasteiz, Spain (538); Vitoria, Spain (12) |
| Zarautz (`zarautz`) | Gipuzkoa | Zarautz, Spain (279) |
| Irun (`irun`) | Gipuzkoa | Irun, Spain (107); Irún, Spain (6) |
| Getxo (`getxo`) | Bizkaia | Getxo, Spain (91) |
| Santurtzi (`santurtzi`) | Bizkaia | Santurtzi, Spain (73) |
| Hondarribia (`hondarribia`) | Gipuzkoa | Hondarribia, Spain (59) |
| Errenteria (`errenteria`) | Gipuzkoa | Errenteria, Spain (58) |
| Barakaldo (`barakaldo`) | Bizkaia | Barakaldo, Spain (55) |
| Arrasate (`arrasate`) | Gipuzkoa | Arrasate, Spain (48) |
| Leioa (`leioa`) | Bizkaia | Leioa, Spain (48) |
| Bermeo (`bermeo`) | Bizkaia | Bermeo, Spain (41) |
| Portugalete (`portugalete`) | Bizkaia | Portugalete, Spain (41) |
| Gernika-Lumo (`gernika-lumo`) | Bizkaia | Guernica, Spain (28); Gernika Lumo, Spain (11) |
| Ondarroa (`ondarroa`) | Bizkaia | Ondarroa, Spain (39) |
| Oiartzun (`oiartzun`) | Gipuzkoa | Oiartzun, Spain (35) |
| Eibar (`eibar`) | Gipuzkoa | Eibar, Spain (34) |
| Tolosa (`tolosa`) | Gipuzkoa | Tolosa, Spain (34) |
| Andoain (`andoain`) | Gipuzkoa | Andoain, Spain (33) |
| Hernani (`hernani`) | Gipuzkoa | Hernani, Spain (29); Ereñotzu, Spain (1) |
| Oñati (`onati`) | Gipuzkoa | Oñati, Spain (29) |
| Tutera (`tutera`) | Nafarroa | Tudela, Spain (22) |
| Zumaia (`zumaia`) | Gipuzkoa | Zumaia, Spain (22) |
| Laudio (`laudio`) | Araba | Laudio, Spain (19) |
| Azpeitia (`azpeitia`) | Gipuzkoa | Azpeitia, Spain (18) |
| Bergara (`bergara`) | Gipuzkoa | Bergara, Spain (16) |
| Ermua (`ermua`) | Bizkaia | Ermua, Spain (16) |
| Mungia (`mungia`) | Bizkaia | Mungia, Spain (16) |
| Lekeitio (`lekeitio`) | Bizkaia | Lekeitio, Spain (15) |
| Baiona (`baiona`) | Iparralde | Bayonne, France (14) |
| Kanbo (`kanbo`) | Iparralde | Cambo Les Bains, France (13) |
| Hendaia (`hendaia`) | Iparralde | Hendaye, France (13) |
| Amurrio (`amurrio`) | Araba | Amurrio, Spain (12) |
| Berriz (`berriz`) | Bizkaia | Berriz, Spain (11) |
| Mendaro (`mendaro`) | Gipuzkoa | Mendaro, Spain (11) |
| Basauri (`basauri`) | Bizkaia | Basauri, Spain (10) |
| Itsasu (`itsasu`) | Iparralde | Itxassou, France (9) |
| Sopela (`sopela`) | Bizkaia | Sopelana, Spain (9) |
| Zumarraga (`zumarraga`) | Gipuzkoa | Zumarraga, Spain (9) |
| Arrigorriaga (`arrigorriaga`) | Bizkaia | Arrigorriaga, Spain (8) |
| Legazpi (`legazpi`) | Gipuzkoa | Legazpi, Spain (8) |
| Urretxu (`urretxu`) | Gipuzkoa | Urretxu, Spain (8) |
| Bera (`bera`) | Nafarroa | Bera, Spain (7) |
| Hazparne (`hazparne`) | Iparralde | Hasparren, France (7) |
| Galdakao (`galdakao`) | Bizkaia | Galdakao, Spain (6) |
| Ispaster (`ispaster`) | Bizkaia | Ispaster, Spain (6) |
| Lasarte-Oria (`lasarte-oria`) | Gipuzkoa | Lasarte Oria, Spain (6) |
| Sestao (`sestao`) | Bizkaia | Sestao, Spain (6) |
| Getaria (`getaria-gipuzkoa`) | Gipuzkoa | Getaria, Spain (5) |
| Lekunberri (`lekunberri-nafarroa`) | Nafarroa | Lekunberri, Spain (5) |
| Orio (`orio`) | Gipuzkoa | Orio, Spain (5) |
| Urnieta (`urnieta`) | Gipuzkoa | Urnieta, Spain (5) |
| Villabona-Amasa (`villabona-amasa`) | Gipuzkoa | Villabona, Spain (5) |
| Abadiño (`abadino`) | Bizkaia | Abadiño, Spain (4) |
| Elortzibar (`elortzibar`) | Nafarroa | Noáin, Navarra, Spain (4) |
| Donibane Lohizune (`donibane-lohizune`) | Iparralde | Saint Jean De Luz, France (4) |
| Azkoitia (`azkoitia`) | Gipuzkoa | Azkoitia, Spain (3) |
| Biarritz (`biarritz`) | Iparralde | Biarritz, France (3) |
| Maule-Lextarre (`maule-lextarre`) | Iparralde | Mauléon Licharre, France (3) |
| Moreda Araba (`moreda-araba`) | Araba | Moreda De Alava, Spain (3) |
| Zaldibar (`zaldibar`) | Bizkaia | Zaldibar, Spain (3) |
| Azkaine (`azkaine`) | Iparralde | Ascain, France (2) |
| Beasain (`beasain`) | Gipuzkoa | Beasain, Spain (2) |
| Durango (`durango`) | Bizkaia | Durango, Spain (2) |
| Elgoibar (`elgoibar`) | Gipuzkoa | Elgoibar, Spain (2) |
| Elorrio (`elorrio`) | Bizkaia | Elorrio, Spain (2) |
| Eskoriatza (`eskoriatza`) | Gipuzkoa | Eskoriatza, Spain (2) |
| Deba (`deba`) | Gipuzkoa | Itziar, Spain (2) |
| Bastida (`bastida-iparralde`) | Iparralde | La Bastide Clairence, France (2) |
| Martzilla (`martzilla`) | Nafarroa | Marcilla, Spain (2) |
| Otxandio (`otxandio`) | Bizkaia | Otxandio, Spain (2) |
| Baigorri (`baigorri`) | Iparralde | Saint étienne De Baïgorry, France (2) |
| Soraluze (`soraluze`) | Gipuzkoa | Soraluze Placencia De Las Armas, Spain (1); Soraluze, Spain (1) |
| Suhuskune (`suhuskune`) | Iparralde | Suhescun, France (2) |
| Zaldibia (`zaldibia`) | Gipuzkoa | Zaldibia, Spain (2) |
| Zestoa (`zestoa`) | Gipuzkoa | Zestoa, Spain (2) |
| Ainhize-Monjolose (`ainhize-monjolose`) | Iparralde | Ainhice Mongelos, France (1) |
| Altsasu (`altsasu`) | Nafarroa | Alsasua – Altsasu, Spain (1) |
| Zornotza (`zornotza`) | Bizkaia | Amorebieta, Spain (1) |
| Angelu (`angelu`) | Iparralde | Anglet, France (1) |
| Aramaio (`aramaio`) | Araba | Aramaio, Spain (1) |
| Arellano (`arellano`) | Nafarroa | Arellano, Spain (1) |
| Aretxabaleta (`aretxabaleta`) | Gipuzkoa | Aretxabaleta, Spain (1) |
| Berango (`berango`) | Bizkaia | Berango, Spain (1) |
| Burlata (`burlata`) | Nafarroa | Burlada, Spain (1) |
| Erandio (`erandio`) | Bizkaia | Erandio, Spain (1) |
| Lizarra (`lizarra`) | Nafarroa | Estella, Spain (1) |
| Irulegi (`irulegi`) | Iparralde | Irouléguy, France (1) |
| Legorreta (`legorreta`) | Gipuzkoa | Legorreta, Spain (1) |
| Legutio (`legutio`) | Araba | Legutio, Spain (1) |
| Markina-Xemein (`markina-xemein`) | Bizkaia | Markina Xemein, Spain (1) |
| Mundaka (`mundaka`) | Bizkaia | Mundaka, Spain (1) |
| Mutriku (`mutriku`) | Gipuzkoa | Mutriku, Spain (1) |
| Donibane Garazi (`donibane-garazi`) | Iparralde | Saint Jean Pied De Port, France (1) |
| San Adrián (`san-adrian`) | Nafarroa | San Adrián, Spain (1) |
| Tafalla (`tafalla`) | Nafarroa | Tafalla, Spain (1) |
| Untzue (`untzue`) | Nafarroa | Unzué, Spain (1) |
| Urdazubi (`urdazubi`) | Nafarroa | Urdazubi/Urdax, Spain (1) |
| Usurbil (`usurbil`) | Gipuzkoa | Usurbil, Spain (1) |
| Trapagaran (`trapagaran`) | Bizkaia | Valle De Trápaga Trapagaran, Spain (1) |
| Zaratamo (`zaratamo`) | Bizkaia | Zaratamo, Spain (1) |
| Zizur Nagusia (`zizur-nagusia`) | Nafarroa | Zizur Mayor, Spain (1) |
