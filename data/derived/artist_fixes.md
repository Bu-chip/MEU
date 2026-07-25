# Corrección de `artist` desde el `title` (sello auto-acreditado)

PR curado, **read-and-write** sobre el canónico. Reescribe **solo** el campo `artist` de filas donde el sello se acredita a sí mismo y el artista real está escondido en el `title`. **No** se toca el `title`, **no** se añaden campos, el esquema sigue siendo de 9. El sello no se pierde: es derivable del subdominio de `url`.

- **Filas propuestas: 59** (P1=19, P2=11, P3=29).
- Cuentas (sellos) afectadas: **5** — laagoniadevivir, makramerecords, mendekudiskak, notomorrowrecords, zirikaturecords.
- Artistas distintos recuperados: **41**.
- De esos, **ya existen** en el canónico por su cuenta (enlazables sello↔artista): **11**.

Solo se corrige P1/P2/P3 y solo cuando la cuenta es un sello reconocido por `labels_index` **y** el `artist` actual es el nombre del sello. Todo lo demás se lista en «Exclusiones» con su motivo. Columna `artist propuesto`: ✓existe = ese artista ya está en el canónico por su cuenta.

## Desglose: 95 títulos casan P1/P2/P3 → 59 corregidos

El sondeo apuntaba a ~95 filas por P1+P2+P3. Casan **95**; se corrigen **59**. La diferencia la explican **enteras** las exclusiones obligatorias (cada fila cae en un único motivo):

| # | exclusión | filas |
| :--- | :--- | ---: |
| ① artista extraído = Various Artists / VVAA | el artista extraído es Various Artists / VVAA | 0 |
| ② artista extraído vacío / 1-2 caracteres / solo dígitos-puntuación | el artista extraído es vacío, de 1-2 caracteres, o solo dígitos/puntuación | 2 |
| ③ artista extraído = nombre del sello | el artista extraído es igual al nombre del sello (no aporta) | 2 |
| ④a artist actual ≠ nombre de la cuenta (ya es artista real / código) | el artist actual no es el nombre de la cuenta (ya es un artista real o un código de catálogo) | 29 |
| ④b artist actual = cuenta, pero la cuenta no es un sello (banda) | el artist actual ya es un artista real: la cuenta no es un sello reconocido por labels_index (es la propia banda) | 3 |
| | **Σ exclusiones** | **36** |
| | **corregidas** | **59** |
| | **total P1+P2+P3** | **95** |

Reconciliación: **59 + 36 = 95**. Cuadra; no hay filas sin explicar.

## P1 · `-NNN- ARTISTA "Título" [formato]` — 19 filas

Referencia de catálogo numérica + comillas. El patrón más fiable.

### mendekudiskak (19)

| id | album_id | artist actual | artist propuesto | patrón | title original |
| ---: | ---: | :--- | :--- | :--- | :--- |
| 5478 | 2472669811 | Mendeku Diskak | **ORREAGA 778** ✓existe | P1 | `-006- ORREAGA 778 "Bide Bakarra" LP` |
| 5479 | 1783731450 | Mendeku Diskak | **ORREAGA 778** ✓existe | P1 | `-010- ORREAGA 778 "Utrimque Roditur" 12"` |
| 5480 | 730948944 | Mendeku Diskak | **CUERO** ✓existe | P1 | `-012- CUERO "Black Metal Skinheads" Promo Tape` |
| 5481 | 812332580 | Mendeku Diskak | **CUERO** ✓existe | P1 | `-013- CUERO "Todo Hierro" One-Sided 12"` |
| 5482 | 3543199601 | Mendeku Diskak | **IRMO** | P1 | `-014- IRMO "Demo 2019" 7"` |
| 5483 | 745737432 | Mendeku Diskak | **REVERTT** ✓existe | P1 | `-015- REVERTT "Bermeo Skinhead Hardcore" 7"` |
| 5484 | 3788327811 | Mendeku Diskak | **PURO ODIO** | P1 | `-016- PURO ODIO "Demo 2018" One-Sided 12"` |
| 5485 | 1082242734 | Mendeku Diskak | **CUERO** ✓existe | P1 | `-018- CUERO "Cabezabota" 12"` |
| 5486 | 339304327 | Mendeku Diskak | **STA. CRUZ** | P1 | `-019- STA. CRUZ "s/t" 7"` |
| 5487 | 1344621543 | Mendeku Diskak | **KOLPEKA** ✓existe | P1 | `-022- KOLPEKA "Demo" Cassette` |
| 5489 | 2438428691 | Mendeku Diskak | **OGRO** | P1 | `-026- OGRO "s/t" Cassette` |
| 5491 | 1108578173 | Mendeku Diskak | **KOLPEKA** ✓existe | P1 | `-034- KOLPEKA "Amorruz Beteta" Flexi 7"` |
| 5492 | 3479794094 | Mendeku Diskak | **ARESI** | P1 | `-035- ARESI "s/t" Cassette` |
| 5494 | 3385425813 | Mendeku Diskak | **REVERTT** ✓existe | P1 | `-042- REVERTT "Euskal Hardcorra" 12"` |
| 5495 | 2836497669 | Mendeku Diskak | **OGRO** | P1 | `-052- OGRO "La Marcha" 12"` |
| 5496 | 2314663325 | Mendeku Diskak | **ZIKIN** ✓existe | P1 | `-078- ZIKIN "Bala Galdua Zure Buru Galduan" 12"` |
| 5498 | 2228519303 | Mendeku Diskak | **BELLUM** ✓existe | P1 | `-092- BELLUM "Gure Gerra" 12"` |
| 5499 | 308736977 | Mendeku Diskak | **ARESI** | P1 | `-096- ARESI "Aurrera Beti" 12"` |
| 5500 | 2596380399 | Mendeku Diskak | **ZIKIN** ✓existe | P1 | `-105- ZIKIN "Zatitxu" 7"` |

## P2 · `ALNUM - ARTISTA "Título"` — 11 filas

Referencia alfanumérica (ZR04, LADV166...) + comillas. Fiable.

### laagoniadevivir (4)

| id | album_id | artist actual | artist propuesto | patrón | title original |
| ---: | ---: | :--- | :--- | :--- | :--- |
| 4988 | 444668900 | La Agonía de Vivir | **CULT OF MISERY** ✓existe | P2 | `LADV121 - CULT OF MISERY "together to hell" LP` |
| 4989 | 3684279036 | La Agonía de Vivir | **BANANAS** ✓existe | P2 | `LADV164 - BANANAS "garun ta eztarri" LP` |
| 4991 | 1887047991 | La Agonía de Vivir | **COMIC SANS** ✓existe | P2 | `LADV183 - COMIC SANS "éramos felices y no lo sabíamos" LP` |
| 4992 | 847040140 | La Agonía de Vivir | **YAW** ✓existe | P2 | `LADV19 - YAW "malda" LP` |

### zirikaturecords (7)

| id | album_id | artist actual | artist propuesto | patrón | title original |
| ---: | ---: | :--- | :--- | :--- | :--- |
| 976 | 3531708248 | Zirikatu Records | **INZESTO** | P2 | `ZR04 - INZESTO "La Ciudad de los Muertos"` |
| 1138 | 422707794 | Zirikatu Records | **LA SOGA DEL MUERTO** | P2 | `ZR03 - LA SOGA DEL MUERTO "Luego vas tu!"` |
| 1150 | 582239498 | Zirikatu Records | **AKAINAK** | P2 | `ZR07 - AKAINAK "Jaungoikoa ta diru zakarra"` |
| 1291 | 4068904463 | Zirikatu Records | **AKAINAK** | P2 | `ZR05 - AKAINAK "Zortziko Txikia"` |
| 1346 | 1296275320 | Zirikatu Records | **INZESTO** | P2 | `ZR02 - INZESTO "Ciencia y Terror" (Single)` |
| 1347 | 1193250640 | Zirikatu Records | **INZESTO** | P2 | `ZR01 - INZESTO "2005-2006"` |
| 1778 | 4118836290 | Zirikatu Records | **SERES NOCTURNOS MUERTOS DIURNOS** | P2 | `ZR06 - SERES NOCTURNOS MUERTOS DIURNOS "Los tiempos del todo o nada"` |

## P3 · `ARTISTA "Título"` — 29 filas

**⚠ LA QUE MÁS REVISIÓN NECESITA.** Sin referencia de catálogo delante: solo las comillas separan artista y título, sobre más cuentas y con más superficie de error. Revisar fila a fila.

### makramerecords (16)

| id | album_id | artist actual | artist propuesto | patrón | title original |
| ---: | ---: | :--- | :--- | :--- | :--- |
| 5345 | 3144945232 | makrame records | **Ashtray Navigations** | P3 | `Ashtray Navigations "The Banian Tree"` |
| 5347 | 3832546990 | makrame records | **Aum Sahib** | P3 | `Aum Sahib "The Formula of Atavistic Resurgence"` |
| 5348 | 1278253290 | makrame records | **Baldruin** | P3 | `Baldruin "Aufbruch"` |
| 5349 | 3957246561 | makrame records | **Bolide** | P3 | `Bolide "The Last Thoughts of an Aqua Sabbat"` |
| 5351 | 1718204425 | makrame records | **Flamingo Creatures** | P3 | `Flamingo Creatures "Auf Der Diesseits Jenseits Grenze"` |
| 5354 | 2525746403 | makrame records | **J.Collin** | P3 | `J.Collin "Albert Road Room Odorisor"` |
| 5355 | 2027424330 | makrame records | **John Jasnoch & Charlie Collins** | P3 | `John Jasnoch & Charlie Collins "Sometimes We Play This Music"` |
| 5356 | 3772909789 | makrame records | **Keijo** | P3 | `Keijo "Keep Your Eye On"` |
| 5357 | 2747101219 | makrame records | **Mike & Cara Gangloff** | P3 | `Mike & Cara Gangloff  "A Domestic Art"` |
| 5358 | 3542484755 | makrame records | **Pan del Indio** | P3 | `Pan del Indio "Un Disco"` |
| 5359 | 473441715 | makrame records | **Parashi** | P3 | `Parashi "Order of progression"` |
| 5360 | 1338372223 | makrame records | **Part Wild Horses Mane On Both Sides** | P3 | `Part Wild Horses Mane On Both Sides "Fuck Off Massive Onion"` |
| 5361 | 3604757740 | makrame records | **Schrein** | P3 | `Schrein "Afternoon Shadows"` |
| 5362 | 3079718428 | makrame records | **Tulasi** | P3 | `Tulasi "Exotic Cocktail Party"` |
| 5363 | 2218362255 | makrame records | **Uton** | P3 | `Uton "Say Hello to the Butterflies"` |
| 5364 | 3106732376 | makrame records | **Vlubä** | P3 | `Vlubä "Syzygy Drowsy"` |

### notomorrowrecords (1)

| id | album_id | artist actual | artist propuesto | patrón | title original |
| ---: | ---: | :--- | :--- | :--- | :--- |
| 5958 | 3741716926 | No Tomorrow Records | **NUEVO CATECISMO CATÓLICO** | P3 | `NUEVO CATECISMO CATÓLICO "Generación Perdida"` |

### zirikaturecords (12)

| id | album_id | artist actual | artist propuesto | patrón | title original |
| ---: | ---: | :--- | :--- | :--- | :--- |
| 1288 | 1742743658 | Zirikatu Records | **DISWAR** | P3 | `DISWAR "The World in flames"` |
| 1289 | 3574892927 | Zirikatu Records | **DISWAR** | P3 | `DISWAR "Sounds of war"` |
| 1737 | 3290960721 | Zirikatu Records | **AKAINAK** | P3 | `AKAINAK "Bertsiolari"` |
| 1764 | 3071999578 | Zirikatu Records | **SKLEROSIS** | P3 | `SKLEROSIS "Puto Asko"` |
| 1848 | 1027867036 | Zirikatu Records | **NEGRACALAVERA** ✓existe | P3 | `NEGRACALAVERA "Espérame en el coche"` |
| 1861 | 2263377876 | Zirikatu Records | **SENCILLOS & ELEGANTES** | P3 | `SENCILLOS & ELEGANTES "No mientas poleo"` |
| 1862 | 485099267 | Zirikatu Records | **SENCILLOS & ELEGANTES** | P3 | `SENCILLOS & ELEGANTES "Chabola Blues"` |
| 1876 | 935692927 | Zirikatu Records | **AKAINAK** | P3 | `AKAINAK "DEMO Enero 2020"` |
| 1913 | 672174196 | Zirikatu Records | **INSOLVENTES** | P3 | `INSOLVENTES "Insolventes"` |
| 1914 | 70538154 | Zirikatu Records | **INSOLVENTES** | P3 | `INSOLVENTES "Vertido Rockactivo"` |
| 1916 | 2004533955 | Zirikatu Records | **SKLEROSIS** | P3 | `SKLEROSIS "Kaput"` |
| 1917 | 1741568727 | Zirikatu Records | **SKLEROSIS** | P3 | `SKLEROSIS "Volkete"` |

## Exclusiones — 36 filas que casan P1/P2/P3 pero NO se corrigen

Todo lo que un patrón casa pero un gate rechaza, con su motivo. Un patrón con cobertura pero con ruido es peor que poco y limpio: aquí se ve el ruido que se deja fuera a propósito.

### el artista extraído es vacío, de 1-2 caracteres, o solo dígitos/puntuación — 2

| id | cuenta | artist actual | se extraería | patrón | title original |
| ---: | :--- | :--- | :--- | :--- | :--- |
| 4474 | inocua | inocua | EP | P3 | `EP "Volar"` |
| 5365 | makramerecords | makrame records | Ø+yn | P3 | `Ø+yn "Barraskiloaren Etxean Dantzan"` |

### el artista extraído es igual al nombre del sello (no aporta) — 2

| id | cuenta | artist actual | se extraería | patrón | title original |
| ---: | :--- | :--- | :--- | :--- | :--- |
| 5233 | losretumbes | LOS RETUMBES | LOS RETUMBES | P3 | `LOS RETUMBES "EL REGRESO"` |
| 7312 | voltaia | VOLTAIA | VOLTAIA | P3 | `VOLTAIA "Erortzen"` |

### el artist actual no es el nombre de la cuenta (ya es un artista real o un código de catálogo) — 29

| id | cuenta | artist actual | se extraería | patrón | title original |
| ---: | :--- | :--- | :--- | :--- | :--- |
| 2476 | afrihooop | Balvada Dieng | Wellcome 2 My Mbedd | P3 | `Wellcome 2 My Mbedd "The Net Tape"` |
| 2880 | barraks | Barraks Promotion | Keziah | P2 | `BP004 - Keziah "The Ocean Is Not Silent" (EP)` |
| 2881 | barraks | Barraks Promotion | Chivo | P2 | `BP005 - Chivo "Waiting For So Long"` |
| 2882 | barraks | Barraks Promotion | R.O.L.F. | P2 | `BP006 - R.O.L.F. "Taró de Muerto"` |
| 3499 | detachedhc | Detached | DEMOS 2018 | P3 | `DEMOS 2018 "Denial Of Dualism"` |
| 3552 | discoshumeantes | DHR-020 | Los Steaks | P3 | `Los Steaks "Something Special"` |
| 4100 | grabacionesviscerales | Build Me A Bomb | BUILD ME A BOMB | P3 | `BUILD ME A BOMB “Pasión por la autodestrucción”` |
| 4102 | grabacionesviscerales | ROUSE | ROUSE | P3 | `ROUSE “Deep Inside + Early Recordings & Unreleased Stuff”` |
| 4103 | grabacionesviscerales | Troners | TRONERS | P3 | `TRONERS "Troners"` |
| 4105 | grabacionesviscerales | Varios artistas | VV/AA | P3 | `VV/AA "Tributo a Subterranean Kids"` |
| 4157 | hangthedjrecords | The Brontës | The Brontës | P3 | `The Brontës "Que la tierra te sea leve"` |
| 4244 | hombremontana | Bayou La Batre | HM-022 | P3 | `HM-022 "Argilun"` |
| 4950 | kristonzintak | KZ-006 | Erroma | P3 | `Erroma "s/t" LP` |
| 4952 | kristonzintak | KZ-002 | Keep Diggin | P3 | `Keep Diggin "Demo" k7` |
| 4953 | kristonzintak | KZ-003 | Los Santos | P3 | `Los Santos "Santuak" k7` |
| 4954 | kristonzintak | KZ-004 | Paz Vegan | P3 | `Paz Vegan "MMVII" k7` |
| 4956 | kristonzintak | KZ-005 | Twin Wolf | P3 | `Twin Wolf "s/t" k7` |
| 146 | laagoniadevivir | La Agonía Vivir | MÁRMOL | P2 | `LADV166 - MÁRMOL "declaración total de guerra" LP` |
| 163 | laagoniadevivir | La Agonía Vivir | OHIL | P2 | `LADV206 - OHIL "akorde beste orbain" LP` |
| 909 | laagoniadevivir | La Agonía Vivir | DESPEÑAPERROS | P2 | `LADV60 - DESPEÑAPERROS "herejía" LP` |
| 1151 | laagoniadevivir | La Agonía Vivir | DIANA LAGARTO | P2 | `LADV39 - DIANA LAGARTO "st" LP` |
| 1156 | laagoniadevivir | La Agonía Vivir | URA | P2 | `LADV45 - URA "st" 12"` |
| 1258 | laagoniadevivir | La Agonía Vivir | 1991 | P2 | `LADV46 - 1991 "st" 12"` |
| 1355 | laagoniadevivir | La Agonía Vivir | ANCIENT EMBLEM | P2 | `LADV38 - ANCIENT EMBLEM "throne with no god" LP` |
| 1356 | laagoniadevivir | La Agonía Vivir | DESPEÑAPERROS | P2 | `LADV16 - DESPEÑAPERROS "el foso" 7"` |
| 6715 | somoscrap | CRAP | CRAP | P3 | `CRAP "ep"` |
| 6830 | taerecords | Tough Ain't Enough | VIETCONG 68 | P3 | `VIETCONG 68 "Como Debe Ser!"` |
| 7395 | xxltrio | XXL | Day by day | P3 | `Day by day "1996"` |
| 7568 | zintzilik | zintzilik irratia | M.D.C. | P3 | `M.D.C. "Euskal Herrian zuzen zuzenean"` |

### el artist actual ya es un artista real: la cuenta no es un sello reconocido por labels_index (es la propia banda) — 3

| id | cuenta | artist actual | se extraería | patrón | title original |
| ---: | :--- | :--- | :--- | :--- | :--- |
| 2466 | adrenalized | Adrenalized | Tales From The Last Generation DIGITAL VERSION | P3 | `Tales From The Last Generation DIGITAL VERSION "GUITAR PRO TABS"` |
| 2599 | ancientsettlers | Ancient Settlers | Our Last Eclipse | P3 | `Our Last Eclipse "The Settlers Saga Pt.1"` |
| 837 | thelongboards | The Longboards | Moto Lube | P3 | `Moto Lube "A Tribute on 33rpm in Stereo"` |

## Artistas recuperados que YA existen por su cuenta

Base del enlace sello↔artista: el nombre escondido en el `title` ya es un artista del mapa. (En el sondeo global salían 126 enlazables sobre P1-P4; aquí, solo P1-P3 y solo sellos auto-acreditados.)

| artista (fold) |
| :--- |
| `bananas` |
| `bellum` |
| `comicsans` |
| `cuero` |
| `cultofmisery` |
| `kolpeka` |
| `negracalavera` |
| `orreaga778` |
| `revertt` |
| `yaw` |
| `zikin` |

