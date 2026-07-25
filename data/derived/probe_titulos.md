# Sonda de artistas ocultos en el `title` (medición, read-only)

Fase de **medición pura**. Lee el canónico `data/bandcamp_bilbaotags_clean.json` y NO escribe ni corrige nada: mide qué cobertura tendrían unos patrones que sacarían al artista real de dentro del `title` cuando el sello se acredita a sí mismo como `artist`. La única salida es este informe. **No se ha extraído, corregido ni escrito ningún artista.**

Los patrones se miden por separado; cada título cae en **un solo** patrón (prioridad P1>P2>P3>P5>P4), así los recuentos particionan sin doble conteo. Antes de parsear se normalizan las comillas curvas a rectas y se descarta la cola de formato (7"/12"/LP/EP/Tape/Split...), porque la pulgada de `7"` es el mismo carácter que la comilla de cierre.

## Patrones y definición

| patrón | nombre | forma | ejemplo |
| :--- | :--- | :--- | :--- |
| P1 | `ref_guion_artista_comillas` | `-001- ARTISTA "Título" [formato]` | `-015- REVERTT "Bermeo Skinhead Hardcore" 7"` |
| P2 | `ref_alfanum_artista_comillas` | `ZR04 - ARTISTA "Título"` | `ZR04 - INZESTO "La Ciudad de los Muertos"` |
| P3 | `artista_comillas` | `ARTISTA "Título"` | `Ashtray Navigations "The Banian Tree"` |
| P4 | `artista_guion_titulo` | `ARTISTA - Título` | `Burial Hex - Pentecost` |
| P5 | `split` | `ARTISTA_A / ARTISTA_B Split [formato]` | `-086- REVERT / KOLPEKA Split 12"` |

## Cobertura por patrón

Títulos que casan con cada patrón (asignación por prioridad, sin doble conteo) y en cuántas cuentas distintas aparece.

| patrón | nombre | títulos | cuentas distintas |
| :--- | :--- | ---: | ---: |
| P1 | `ref_guion_artista_comillas` | 19 | 1 |
| P2 | `ref_alfanum_artista_comillas` | 22 | 3 |
| P3 | `artista_comillas` | 54 | 20 |
| P5 | `split` | 20 | 12 |
| P4 | `artista_guion_titulo` | 622 | 154 |
| **Σ** | **cualquier patrón** | **737** | — |

## Ejemplos reales por patrón

Título original → artista que se extraería. P5 muestra los dos artistas del split (multiartista: NO cuenta como extracción de un artista).

### P1 · `ref_guion_artista_comillas` — 19 títulos

| cuenta | título original | artista que se extraería |
| :--- | :--- | :--- |
| mendekudiskak | `-006- ORREAGA 778 "Bide Bakarra" LP` | ORREAGA 778 |
| mendekudiskak | `-010- ORREAGA 778 "Utrimque Roditur" 12"` | ORREAGA 778 |
| mendekudiskak | `-012- CUERO "Black Metal Skinheads" Promo Tape` | CUERO |
| mendekudiskak | `-013- CUERO "Todo Hierro" One-Sided 12"` | CUERO |
| mendekudiskak | `-014- IRMO "Demo 2019" 7"` | IRMO |
| mendekudiskak | `-015- REVERTT "Bermeo Skinhead Hardcore" 7"` | REVERTT |
| mendekudiskak | `-016- PURO ODIO "Demo 2018" One-Sided 12"` | PURO ODIO |
| mendekudiskak | `-018- CUERO "Cabezabota" 12"` | CUERO |

### P2 · `ref_alfanum_artista_comillas` — 22 títulos

| cuenta | título original | artista que se extraería |
| :--- | :--- | :--- |
| laagoniadevivir | `LADV166 - MÁRMOL "declaración total de guerra" LP` | MÁRMOL |
| laagoniadevivir | `LADV206 - OHIL "akorde beste orbain" LP` | OHIL |
| laagoniadevivir | `LADV60 - DESPEÑAPERROS "herejía" LP` | DESPEÑAPERROS |
| zirikaturecords | `ZR04 - INZESTO "La Ciudad de los Muertos"` | INZESTO |
| zirikaturecords | `ZR03 - LA SOGA DEL MUERTO "Luego vas tu!"` | LA SOGA DEL MUERTO |
| zirikaturecords | `ZR07 - AKAINAK "Jaungoikoa ta diru zakarra"` | AKAINAK |
| laagoniadevivir | `LADV39 - DIANA LAGARTO "st" LP` | DIANA LAGARTO |
| laagoniadevivir | `LADV45 - URA "st" 12"` | URA |

### P3 · `artista_comillas` — 54 títulos

| cuenta | título original | artista que se extraería |
| :--- | :--- | :--- |
| thelongboards | `Moto Lube "A Tribute on 33rpm in Stereo"` | Moto Lube |
| zirikaturecords | `DISWAR "The World in flames"` | DISWAR |
| zirikaturecords | `DISWAR "Sounds of war"` | DISWAR |
| zirikaturecords | `AKAINAK "Bertsiolari"` | AKAINAK |
| zirikaturecords | `SKLEROSIS "Puto Asko"` | SKLEROSIS |
| zirikaturecords | `NEGRACALAVERA "Espérame en el coche"` | NEGRACALAVERA |
| zirikaturecords | `SENCILLOS & ELEGANTES "No mientas poleo"` | SENCILLOS & ELEGANTES |
| zirikaturecords | `SENCILLOS & ELEGANTES "Chabola Blues"` | SENCILLOS & ELEGANTES |

### P5 · `split` — 20 títulos

| cuenta | título original | artista que se extraería |
| :--- | :--- | :--- |
| ballardnoise | `HIPOXIA / BALLARD split` | HIPOXIA / BALLARD |
| phlgz | `Emaztegaiak / PHLGZ (Split)` | Emaztegaiak / PHLGZ |
| eclecticreactionsrecords | `ER024 Leun Dura / Neobot - Split` | ER024 Leun Dura / Neobot - |
| produccionestudancas | `Control de Plagas & Guillotina "Split" LP + CD / PT-04` | Control de Plagas & Guillotina "Split" LP + CD / PT-04 |
| drmugre | `DR MUGRE / TUNIKAH - TWIN SPLIT` | DR MUGRE / TUNIKAH - TWIN |
| ibanaranaindependent666 | `Extirpation / Karmaggedon (Split 2022)` | Extirpation / Karmaggedon (Split 2022) |
| ibanaranaindependent666 | `Scum / Betiraun (Split 2022)` | Scum / Betiraun (Split 2022) |
| ibanaranaindependent666 | `Scum / Mincer "Disciples of Human Extinction" (Split 2022)` | Scum / Mincer "Disciples of Human Extinction" (Split 2022) |

### P4 · `artista_guion_titulo` — 622 títulos

| cuenta | título original | artista que se extraería |
| :--- | :--- | :--- |
| wldv | `MUT001 WLDV - The Fifth Element` | MUT001 WLDV |
| nesket | `DJ NESKET FEAT. FINCHY & JENNY JONES - ALL IN (HARD DANCE MIX)` | DJ NESKET FEAT. FINCHY & JENNY JONES |
| bombbasshifi | `Ras Teo - Lumumba` | Ras Teo |
| nesket | `DEEJAY LAURA & DJ NESKET - NOTHING` | DEEJAY LAURA & DJ NESKET |
| polygonnetwork | `black insekt - future kill | polygon network [NW0074]` | black insekt |
| lordbakartia | `Priscilla's Dagger - I` | Priscilla's Dagger |
| eclecticreactionsrecords | `ER052 Intensidades Ortega - Deseo` | ER052 Intensidades Ortega |
| nesket | `DJ NESKET & DEEJAY LAURA - FOR THE MOMENT` | DJ NESKET & DEEJAY LAURA |

## Global

- Discos con un artista **extraíble y limpio** (P1-P4, tras control de calidad): **649** de 7568 (**8.6%** del catálogo).
- Artistas **distintos** que aparecerían (clave `fold`): **542**.
- De esos, **ya existen** en el canónico como artista por su cuenta (enlazables sello↔artista): **126**.
- Artistas que serían **completamente nuevos** en el mapa: **416**.

> Los P5 (split) se cuentan aparte y **no** entran en el recuento de un artista: producen dos o más y se tratan como ambiguos (sección de fallos).

### Artistas recuperados que YA existen por su cuenta (muestra)

Señal fuerte de que el sello y el artista se podrían enlazar: el nombre escondido en el `title` ya es un artista del mapa.

| artista (fold) | display de la extracción |
| :--- | :--- |
| `0n4b` | 0N4B |
| `555kables` | 555 Kables |
| `6siss` | 6siss |
| `abi` | ABI |
| `addobscurae` | add obscurae |
| `afosagace` | AFO&SAGACE |
| `alkupera` | Alkuperä |
| `ama` | Ama |
| `ancientemblem` | ANCIENT EMBLEM |
| `andreydetochkin` | andrey detochkin |
| `antiamuinosunegretachaska` | Antía Muíño & SÜNE & GRETA CH'ASKA |
| `arakajun` | Arakajun |
| `artrosis` | ARTROSIS |
| `aso` | ASO |
| `auralresearch` | aural research |
| `automatisme` | automatisme |
| `baiucaizaro` | Baiuca & IZARO |
| `bananas` | BANANAS |
| `bariri` | BARIRI |
| `bellum` | BELLUM |
| … | (+106 más) |

## Cuentas más afectadas

Cuentas ordenadas por nº de títulos que casan con algún patrón. El `% casa` sobre el total de títulos de la cuenta es lo que dice si un sello es **parseable** o no. `limpios` = extracciones que pasan el control de calidad.

| cuenta | discos | casan | % casa | limpios | P1 | P2 | P3 | P4 | P5 |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| polygonnetwork | 82 | 82 | 100% | 82 | 0 | 0 | 0 | 82 | 0 |
| eclecticreactionsrecords | 53 | 46 | 87% | 45 | 0 | 0 | 0 | 45 | 1 |
| theetherensemble | 41 | 39 | 95% | 39 | 0 | 0 | 0 | 39 | 0 |
| wldv | 31 | 31 | 100% | 11 | 0 | 0 | 0 | 31 | 0 |
| petruskarecords | 49 | 28 | 57% | 26 | 0 | 0 | 0 | 26 | 2 |
| inguma | 27 | 27 | 100% | 27 | 0 | 0 | 0 | 27 | 0 |
| alternativedmusic | 25 | 24 | 96% | 24 | 0 | 0 | 0 | 24 | 0 |
| secretsocietychile | 22 | 22 | 100% | 21 | 0 | 0 | 0 | 22 | 0 |
| mendekudiskak | 24 | 21 | 88% | 19 | 19 | 0 | 0 | 0 | 2 |
| makramerecords | 21 | 21 | 100% | 20 | 0 | 0 | 17 | 4 | 0 |
| clartycat | 25 | 19 | 76% | 19 | 0 | 0 | 0 | 19 | 0 |
| zirikaturecords | 19 | 19 | 100% | 19 | 0 | 7 | 12 | 0 | 0 |
| mikelrnieto | 15 | 14 | 93% | 14 | 0 | 0 | 0 | 14 | 0 |
| nesket | 34 | 12 | 35% | 12 | 0 | 0 | 0 | 12 | 0 |
| bombbasshifi | 17 | 12 | 71% | 12 | 0 | 0 | 0 | 12 | 0 |
| izarbeltzliburua | 16 | 12 | 75% | 12 | 0 | 0 | 0 | 12 | 0 |
| laagoniadevivir | 15 | 12 | 80% | 11 | 0 | 12 | 0 | 0 | 0 |
| musexindustries | 105 | 8 | 8% | 8 | 0 | 0 | 0 | 8 | 0 |
| enochsvision | 11 | 8 | 73% | 8 | 0 | 0 | 0 | 8 | 0 |
| zaragozadesordenrecords | 11 | 8 | 73% | 8 | 0 | 0 | 0 | 8 | 0 |
| yakovlev42 | 8 | 8 | 100% | 0 | 0 | 0 | 0 | 8 | 0 |
| thetitanians | 9 | 7 | 78% | 5 | 0 | 0 | 0 | 7 | 0 |
| hopeandfaithrecords | 7 | 7 | 100% | 7 | 0 | 0 | 0 | 7 | 0 |
| ibanaranaindependent666 | 61 | 6 | 10% | 3 | 0 | 0 | 0 | 3 | 3 |
| kristonzintak | 7 | 6 | 86% | 5 | 0 | 0 | 5 | 0 | 1 |
| bonzosfsr | 6 | 6 | 100% | 6 | 0 | 0 | 0 | 6 | 0 |
| raso | 6 | 6 | 100% | 6 | 0 | 0 | 0 | 6 | 0 |
| grabacionesviscerales | 6 | 5 | 83% | 4 | 0 | 0 | 4 | 1 | 0 |
| gatazkabasslabel | 5 | 5 | 100% | 5 | 0 | 0 | 0 | 5 | 0 |
| familyspreerecordings | 8 | 4 | 50% | 4 | 0 | 0 | 0 | 4 | 0 |

## Casos que fallan o son ambiguos

Un patrón con mucha cobertura pero mucho ruido es PEOR que uno con poca y limpia. Esta sección lo hace visible.

### Cuentas sin artista extraíble

Cuentas con varios discos donde **ningún** título casa con un patrón: el artista no está escondido en el `title` (títulos tipo "Diva EP", "Best Of…"). Extraer aquí sería inventar. Umbral: ≥ 5 discos, 0 casan.

| cuenta | discos | casan |
| :--- | ---: | ---: |
| urbanxtrm | 74 | 0 |
| bidehuts | 52 | 0 |
| love-evolmusic | 49 | 0 |
| orruadiskak | 45 | 0 |
| raperosdeemaus | 35 | 0 |
| esnebidearecords | 34 | 0 |
| ekinmusic | 31 | 0 |
| timbamuziklab | 29 | 0 |
| josebairazoki | 25 | 0 |
| baliodute | 24 | 0 |
| jmaaonline | 24 | 0 |
| joanakaredmoon | 23 | 0 |
| zawpklem | 22 | 0 |
| bizitzakaotikoa | 21 | 0 |
| bangrecords | 20 | 0 |
| chicoychica | 19 | 0 |
| somniferumrec | 18 | 0 |
| blackvoguerecords | 17 | 0 |
| javiersun | 17 | 0 |
| arvalastra | 16 | 0 |

### Comillas que NO separan artista

Títulos con `"` donde delante NO hay un artista que extraer: el disco entero va entrecomillado, las comillas están dentro del nombre, o —el caso dominante en el catálogo— el `7"`/`12"` va como **prefijo de formato al inicio** (`7" Hotter The Battle`), no como pulgada de cierre. Parsear por comillas aquí daría artista vacío o basura.

| cuenta | título original |
| :--- | :--- |
| alonereggaeshop | `7" Hotter The Battle` |
| alonereggaeshop | `7" Words Of My Mouth` |
| bassleemusic | `7" Enlightenment` |
| alonereggaeshop | `7" Live not for Vanity pt. II` |
| bassleemusic | `7" Winds of Change` |
| alonereggaeshop | `7" Life is Free` |
| bassleemusic | `12" Earl Zero, Bass Lee, Kenny Knotts, Roberto Sánchez - Fire In The City / Love & Glory` |
| alonereggaeshop | `7" East Bound` |

### Splits y recopilatorios (varios artistas en un título)

P5 casa **20** títulos con ' / ' **y** keyword `Split`. Producen 2+ artistas: no son una extracción de un artista. El propio P5 tiene **falsos positivos** cuando `Split` es parte del título entrecomillado o el ' / ' separa una referencia de catálogo (p. ej. `... "Split" LP + CD / PT-04`), por eso se marca para tratar aparte, no para extraer. Además hay formas que NO casan P5 y quedan ambiguas:

**' / ' sin keyword `Split`** (posible split o recopilación sin marcar; también letras con barra):

| cuenta | patrón | título original | artista que se extraería |
| :--- | :--- | :--- | :--- |
| eclecticreactionsrecords | P4 | `ER044 Valerio Tricoli / Werner Dafeldecker / Mattin - Le Diable probablement` |  |
| bombbasshifi | P4 | `Jah Marnyah - Never Give Up / Solo Banton - Serious Days` |  |
| bombbasshifi | P4 | `King Kong - Some A Dem Say / Lone Ranger - Jah A Me Saviour` |  |
| bombbasshifi | P4 | `Horace Martin - Dem Just a Push Me / Sammy Gold - Greatest Sound` |  |
| eclecticreactionsrecords | P4 | `ER037 Miguel A. Garcia & Garazi Navas - Aleph / Illuminatus` |  |
| bombbasshifi | P4 | `Echo Ranks - Weh Dem A Go Run / Linval Thompson - Country Living` |  |
| bombbasshifi | P4 | `Errol Bellot - Government / Sammy Gold - Gunman City` |  |
| bombbasshifi | P4 | `Sandeeno - Silent River / Ras Telford - Sabotage` |  |

**`Split w/ …`** (colaboración sin el segundo artista dentro del título):

| cuenta | título original |
| :--- | :--- |
| lordbakartia | `Split w/ Moonrise Kingdom` |
| lordbakartia | `Split w/ Lehman` |
| lordbakartia | `Split w/ Amargor` |
| obstetragrind | `Split w/ Mutilated Judge` |
| 1991taldea | `split w/Sierra Nevada 7"` |
| 1991taldea | `split w/Vértigo 7"` |
| kamorrah | `Split w/ Diswar` |
| lordbakartia | `Split w/ Basque artists` |

### Extracciones basura (control de calidad)

Extracciones que un patrón SÍ produce pero que el control de calidad rechaza. Son el ruido que restaría fiabilidad si se extrajera a ciegas.

#### 1-2 caracteres (8 ejemplos mostrados)

| cuenta | patrón | título original | artista que se extraería |
| :--- | :--- | :--- | :--- |
| iikrisgm | P4 | `I - IV` | I |
| elcrack | P4 | `b - 2020` | b |
| garimbarekords | P4 | `EP - SKA Vol 1` | EP |
| grabacionesviscerales | P4 | `GO! - Impact` | GO! |
| inocua | P3 | `EP "Volar"` | EP |
| makramerecords | P3 | `Ø+yn "Barraskiloaren Etxean Dantzan"` | Ø+yn |
| secretsocietychile | P4 | `VA - Sheep EP` | VA |
| toriitaldea | P4 | `EP - Bi` | EP |

#### coincide con el propio sello (autocuenta) (8 ejemplos mostrados)

| cuenta | patrón | título original | artista que se extraería |
| :--- | :--- | :--- | :--- |
| wldv | P4 | `WLDV - A Demon Among Us` | WLDV |
| wldv | P4 | `WLDV - Blood Ceremony EP` | WLDV |
| wldv | P4 | `WLDV - Val And the Thief EP` | WLDV |
| wldv | P4 | `WLDV - Bewitched EP` | WLDV |
| wldv | P4 | `WLDV - Primigenium EP` | WLDV |
| wldv | P4 | `WLDV - Bloodlust Dominion EP` | WLDV |
| wldv | P4 | `WLDV - From The Vault` | WLDV |
| wldv | P4 | `WLDV - Black XX Plague EP` | WLDV |

#### solo números (8 ejemplos mostrados)

| cuenta | patrón | título original | artista que se extraería |
| :--- | :--- | :--- | :--- |
| laagoniadevivir | P2 | `LADV46 - 1991 "st" 12"` | 1991 |
| 6jerseys | P4 | `333 - Tres tristes trans` | 333 |
| tu-k | P4 | `21 22 - 11` | 21 22 |
| yakovlev42 | P4 | `2016 - Streetpunk Antifa` | 2016 |
| yakovlev42 | P4 | `2017 - La pesadilla continúa` | 2017 |
| yakovlev42 | P4 | `2018 - Secuestro Express` | 2018 |
| yakovlev42 | P4 | `2019 - Antolatu, borrokatu, egin!` | 2019 |
| yakovlev42 | P4 | `2020 - Vuestro Pecado` | 2020 |

## Lectura honesta de fiabilidad

- **P1 / P2** (`-NNN-` / `ALNUM -` + comillas): las más fiables. La referencia de catálogo delante y las comillas alrededor del título dejan el artista sin ambigüedad. Cobertura baja pero limpia.
- **P3** (`ARTISTA "Título"`): fiable cuando las comillas separan de verdad; el riesgo es el título que va TODO entrecomillado (artista vacío), ya filtrado por el control de calidad.
- **P4** (`ARTISTA - Título`): el más **ruidoso**. El guion aparece en títulos normales; parte de lo que casa no es artista-título. Mirar la columna `limpios` vs `casan` por cuenta antes de fiarse.
- **P5** (`split`): NO es extracción de un artista; marca discos multiartista para tratar aparte. El ' / ' sin `Split` queda fuera a propósito (demasiado ruido de letras con barra).

> Recordatorio de guardarraíl: si estos números salen muy distintos de lo esperado, manda el dato, no se ajustan los patrones para que quede bonito.

