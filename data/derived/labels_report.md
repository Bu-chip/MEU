# Índice de sellos (derivado, read-only)

Dato derivado del subdominio de `url` en el canónico. Una cuenta entra en el índice por **cualquiera** de dos vías complementarias: **umbral** (>= 2 artistas distintos, el sello que publica a otros) o **léxico** (el account_id lleva un marcador fuerte de sello: `records`, `discos`, `diskak`...; caza al sello que se acredita a sí mismo). El léxico **amplía** la entrada, no filtra. Los flags MARCAN casos para revisión humana; **nunca descartan**.

## Totales

- Cuentas totales (con cuenta atribuible): **2588**
- **Candidatas a sello (total): 320**
- Candidatos **antes / después** de añadir la vía léxica: **244 → 320** (+76)
- Discos cubiertos por candidatas: **2405** de 7568 (**31.8%** del catálogo)
- Cuentas con dominio propio (`custom:`): **6**
- Huecos honestos (url vacía o `bandcamp.com`): **5**

### Desglose por origen de entrada

- `umbral` (solo por >= 2 artistas): **206**
- `ambos` (umbral **y** marcador léxico): **38**
- `lexico` (solo por marcador léxico; 1 cluster, antes invisibles): **76**

> Nota: las 76 entradas que entran **solo por léxico** (1 cluster) son **dos poblaciones distintas**, y conviene tratarlas aparte (detalle más abajo):
>
> - **14 auto-acreditadas**: el sello firma como artista (`mendekudiskak` → "Mendeku Diskak"). Aquí `posible_autocuenta` dispara y **es lo esperado**, no una alarma: es justo por lo que el umbral no las veía.
> - **62 con acto de nombre distinto**: el único artista no es el sello (`gondolinrecords` → "Lord Bakartia", `meyorecords` → "VULK"). No disparan `posible_autocuenta`. No es mala detección: es señal de que el scraper solo ha capturado **un acto** de ese sello (cobertura incompleta).
>
> `borde_2artistas` y `nombre_anidado` no aplican con un solo cluster.

Nota histórica: al endurecer la normalización de artistas los candidatos por umbral pasaron de 335 a 244 (dedup dura por clave `fold`).

### Recuento por flag (dentro de las candidatas)

- `borde_2artistas` (exactamente 2 artistas): **138**
- `posible_VA` (Various Artists / VA / V.A. / Various): **15**
- `nombre_anidado` (2 clusters, uno contenido en el otro; featurings/alias): **78**
- `posible_autocuenta` (id de cuenta ≈ nombre de un artista propio; tiene falsos positivos, revisión humana): **158**
- **Sin ningún flag** (sellos limpios): **113**

## Histograma: cuentas por nº de discos

| nº discos | nº cuentas |
| ---: | ---: |
| 1 | 1330 |
| 2 | 515 |
| 3 | 253 |
| 4 | 160 |
| 5 | 91 |
| 6 | 60 |
| 7 | 30 |
| 8 | 25 |
| 9 | 21 |
| 10 | 10 |
| 11 | 13 |
| 12 | 2 |
| 13 | 11 |
| 14 | 4 |
| 15 | 7 |
| 16 | 9 |
| 17 | 6 |
| 18 | 1 |
| 19 | 2 |
| 20 | 2 |
| 21 | 2 |
| 22 | 3 |
| 23 | 1 |
| 24 | 3 |
| 25 | 3 |
| 27 | 1 |
| 29 | 2 |
| 31 | 2 |
| 34 | 2 |
| 35 | 1 |
| 40 | 1 |
| 41 | 1 |
| 45 | 2 |
| 48 | 1 |
| 49 | 2 |
| 51 | 1 |
| 52 | 1 |
| 53 | 1 |
| 57 | 1 |
| 61 | 1 |
| 74 | 1 |
| 82 | 1 |
| 97 | 1 |
| 105 | 1 |

## Entran solo por léxico

Cuentas con un **solo** cluster de artista (no llegaban al umbral) que entran por llevar un marcador de sello en el account_id. Es el hallazgo principal de esta fase: **76** cuentas antes invisibles. Son **dos poblaciones distintas** (campo `lexico_subtipo` en labels.json). Tablas ordenadas por nº de discos.

### Auto-acreditadas — el sello firma como artista (14)

`posible_autocuenta` dispara y **es lo esperado**: es justo el caso que el umbral no veía. Sellos reales acreditados a su propio nombre.

| account_id | n_discos | artista único | marcador(es) |
| :--- | ---: | :--- | :--- |
| mendekudiskak | 24 | Mendeku Diskak | `diskak` |
| makramerecords | 21 | makrame records | `records`, `record` |
| zirikaturecords | 19 | Zirikatu Records | `records`, `record` |
| blackvoguerecords | 17 | BlackVogue Records | `records`, `record` |
| gatazkabasslabel | 5 | Gatazka Bass Label | `label` |
| produccionestudancas | 5 | Producciones Tudancas | `producciones` |
| slowdownrecords | 2 | Slow Down Records | `records`, `record` |
| ddtbanaketakbilbo | 1 | DDTbanaketak | `banaketak` |
| folcrecords | 1 | FOLC RECORDS | `records`, `record` |
| harrobirecords | 1 | Harrobi Records | `records`, `record` |
| kastillorecords | 1 | Kastillo Records | `records`, `record` |
| notomorrowrecords | 1 | No Tomorrow Records | `records`, `record` |
| plasticwoundrecords | 1 | Plastic Wound Records | `records`, `record` |
| psilocybina-records | 1 | Psilocybina Records | `records`, `record` |

### Con acto de nombre distinto — cobertura incompleta (62)

El único artista capturado no es el sello. No es mala detección: el scraper solo ha traído **un acto** de este sello, así que se ve como cuenta de un artista. Señal de **cobertura incompleta**, candidatos a re-scrapear.

| account_id | n_discos | artista único | marcador(es) |
| :--- | ---: | :--- | :--- |
| daimnicagrabaciones | 9 | DAIMÓNICA (Grabaciones) | `grabaciones` |
| hopeandfaithrecords | 7 | Hope & Faith Records | `records`, `record` |
| gbcrecords | 4 | GBC | `records`, `record` |
| cactuslabel | 3 | 20 Dedos | `label` |
| gondolinrecords | 2 | Lord Bakartia | `records`, `record` |
| nunatakrecords | 2 | Tipico Pero Cierto | `records`, `record` |
| augerecords | 1 | Yaw | `records`, `record` |
| batchrecords | 1 | Mitxu Nimaru | `records`, `record` |
| beatsaladrecords | 1 | N2OGU | `records`, `record` |
| colillarecords | 1 | Mármol / Nueva Generación | `records`, `record` |
| crapouletrecords | 1 | REPRESION | `records`, `record` |
| cruelnaturerecordings | 1 | AR Guda | `record`, `recordings`, `recording` |
| discoshumeantes | 1 | DHR-020 | `discos` |
| elsarecords | 1 | Andres Doñate | `records`, `record` |
| extralovelyrecords | 1 | lowveld | `records`, `record` |
| fatbirdrecordings | 1 | Dub Troubles feat. Tenor Youthman & Jah Rave | `record`, `recordings`, `recording` |
| flexidiscos | 1 | Cromosoma | `discos` |
| flooprecordings | 1 | RedWine House | `record`, `recordings`, `recording` |
| furiousrecords | 1 | Marmol | `records`, `record` |
| gaziarecords | 1 | XYZ | `records`, `record` |
| greencookierecords | 1 | The Bardulians | `records`, `record` |
| hangthedjrecords | 1 | The Brontës | `records`, `record` |
| holaediciones | 1 | Elbis Rever - Elsa de Alfonso - Joana Guerra | `ediciones` |
| homerecordsbe | 1 | Ialma, Manu Sabaté, Iñaki Plaza, Ciscu Cardona, Nicolas Scalliet | `records`, `record` |
| idealstaterecordings | 1 | miguel a. garcía . tomas gris . lee noyes | `record`, `recordings`, `recording` |
| intergalacticrecords | 1 | Ternura | `records`, `record` |
| isilyarecords | 1 | Sublime Solitude | `records`, `record` |
| kilkirrecords | 1 | PPR y DJ Dresss | `records`, `record` |
| killvinylrecords | 1 | Materia | `records`, `record` |
| kumbalenetlabel | 1 | ANDRES DIGITAL | `label` |
| lafamiliarevolucionrecords | 1 | HURACAN ROSE | `records`, `record` |
| lenorecords | 1 | Margalbeat | `records`, `record` |
| likidorecords | 1 | Louware | `records`, `record` |
| madschnauzerrecords | 1 | Addenda | `records`, `record` |
| mamavynilarecords | 1 | Gonorriaga & Bilintx | `records`, `record` |
| mawashiskinsrecords | 1 | Streetwise | `records`, `record` |
| meyorecords | 1 | VULK | `records`, `record` |
| mundiscos | 1 | Positive Hardcore | `discos` |
| musikagelarecords | 1 | Autumn | `records`, `record` |
| niunpeloderubiasrecords | 1 | Cordura | `records`, `record` |
| noaloharecords | 1 | Edu Errea | `records`, `record` |
| nortepuromusicrecords | 1 | Nolove, C.Manson | `records`, `record` |
| origamirecords | 1 | Grises | `records`, `record` |
| politburorecordingfiasco | 1 | LOS PANIKS | `record`, `recording` |
| quebrantarecords | 1 | CORDURA | `records`, `record` |
| remorserecords | 1 | Giant | `records`, `record` |
| reposerecords | 1 | Elffor | `records`, `record` |
| rockizarrecords | 1 | Trastorna2 | `records`, `record` |
| saturnorecords | 1 | LOS JAMBOS | `records`, `record` |
| sentenciarecords | 1 | Imbernon & Mikel Vega | `records`, `record` |
| smilingisnotacrimerecords | 1 | HARDCORE HITS CANCER BENEFIT | `records`, `record` |
| steadyriotrecords | 1 | Fire Cult | `records`, `record` |
| stonehengerecords | 1 | ASFIXIA / ANNUNAKI REVENGE | `records`, `record` |
| subspecieslabel | 1 | Various Artists | `label` |
| szenarecords | 1 | Álvaro Cano | `records`, `record` |
| taerecords | 1 | Tough Ain't Enough | `records`, `record` |
| tanukirecords | 1 | Ilia Belorukov, Alfredo Costa Monteiro, Miguel A. García | `records`, `record` |
| tayulrecords | 1 | Sonidero 13 + Miguel A. Garcia | `records`, `record` |
| theiarecords | 1 | Despeñaperros | `records`, `record` |
| throatruinerrecords | 1 | Palecoal | `records`, `record` |
| uglyandproudrecords | 1 | Vibora | `records`, `record` |
| urticariarecords | 1 | Allusion | `records`, `record` |

## Sellos candidatos (orden: nº artistas desc, nº discos desc, account_id asc)

| account_id | origen | n_discos | n_artistas | flags |
| :--- | :--- | ---: | ---: | :--- |
| zaratazarautz | umbral | 97 | 94 | posible_autocuenta |
| musexindustries | umbral | 105 | 81 | posible_VA |
| polygonnetwork | umbral | 82 | 51 | — |
| eclecticreactionsrecords | ambos | 53 | 48 | posible_VA |
| muertematarrecords | ambos | 40 | 35 | — |
| custom:crudobilbao.com | umbral | 51 | 33 | — |
| bidehuts | umbral | 52 | 24 | — |
| inguma | umbral | 27 | 23 | posible_VA |
| esnebidearecords | ambos | 34 | 20 | — |
| timbamuziklab | umbral | 29 | 18 | — |
| bangrecords | ambos | 20 | 18 | — |
| somniferumrec | umbral | 18 | 18 | — |
| bombbasshifi | umbral | 17 | 16 | — |
| forbiddencolours | umbral | 16 | 15 | — |
| zawpklem | umbral | 22 | 14 | posible_VA |
| bassleemusic | umbral | 16 | 14 | posible_autocuenta |
| orruadiskak | ambos | 45 | 13 | — |
| belarri | umbral | 13 | 13 | — |
| deepnas | umbral | 13 | 13 | — |
| ensemblesinkro | umbral | 20 | 12 | posible_autocuenta |
| raperosdeemaus | umbral | 35 | 11 | posible_autocuenta |
| secretsocietychile | umbral | 22 | 9 | posible_VA, posible_autocuenta |
| sustraidunyouths | umbral | 17 | 8 | posible_autocuenta |
| vyramed | umbral | 11 | 8 | — |
| discosbanana1 | ambos | 10 | 8 | posible_autocuenta |
| senoidrecordings | ambos | 10 | 8 | — |
| familyspreerecordings | ambos | 8 | 8 | posible_autocuenta |
| haziesporak | umbral | 8 | 8 | posible_VA |
| ekinmusic | umbral | 31 | 7 | — |
| clartycat | umbral | 25 | 7 | posible_VA |
| josebairazoki | umbral | 25 | 7 | posible_autocuenta |
| goxoa | umbral | 15 | 7 | — |
| untalasalsa | umbral | 11 | 7 | — |
| zaragozadesordenrecords | ambos | 11 | 7 | — |
| kristonzintak | ambos | 7 | 7 | — |
| javiersun | umbral | 17 | 6 | posible_autocuenta |
| rawsurfacerecords | ambos | 16 | 6 | — |
| camilomateo | umbral | 14 | 6 | posible_autocuenta |
| wolkokrots | umbral | 13 | 6 | posible_autocuenta |
| thetitanians | umbral | 9 | 6 | posible_autocuenta |
| tritonegrabaciones | ambos | 7 | 6 | — |
| grabacionesviscerales | ambos | 6 | 6 | — |
| ghettogunshotrecords | ambos | 13 | 5 | posible_autocuenta |
| alonereggaeshop | umbral | 10 | 5 | — |
| caballitorecords | ambos | 9 | 5 | — |
| edervxga | umbral | 9 | 5 | — |
| dungeonlordrecords | ambos | 8 | 5 | — |
| monocat7 | umbral | 8 | 5 | — |
| txiltxoko | umbral | 8 | 5 | posible_autocuenta |
| valdokmusic | umbral | 8 | 5 | posible_autocuenta |
| maukamusik | umbral | 7 | 5 | posible_autocuenta |
| unsound-methods | umbral | 5 | 5 | — |
| breathingthecore | umbral | 57 | 4 | posible_VA, posible_autocuenta |
| sergiozurutuza | umbral | 17 | 4 | posible_autocuenta |
| elcrack | umbral | 10 | 4 | posible_autocuenta |
| antoinebellanger | umbral | 9 | 4 | posible_autocuenta |
| raso | umbral | 6 | 4 | — |
| azkarzintak | ambos | 5 | 4 | — |
| discosdekirlian | ambos | 5 | 4 | posible_VA |
| kaliyugayouth | umbral | 5 | 4 | — |
| lavidaesunmus | umbral | 5 | 4 | — |
| chin-chinrecordsmundiales | ambos | 4 | 4 | — |
| crystalmine | umbral | 4 | 4 | — |
| dialectoperiferico | umbral | 4 | 4 | — |
| infrarecords | ambos | 4 | 4 | — |
| isuo | umbral | 4 | 4 | posible_autocuenta |
| sustraiakrecords | ambos | 4 | 4 | — |
| xedh | umbral | 4 | 4 | — |
| zulo8 | umbral | 4 | 4 | — |
| joanakaredmoon | umbral | 23 | 3 | posible_autocuenta |
| miusichole | umbral | 22 | 3 | — |
| enochsvision | umbral | 11 | 3 | posible_VA, posible_autocuenta |
| txarlyusher | umbral | 9 | 3 | posible_autocuenta |
| 25thcomingfire | umbral | 7 | 3 | posible_autocuenta |
| jamesroom | umbral | 7 | 3 | posible_autocuenta |
| maitelarburu | umbral | 6 | 3 | posible_autocuenta |
| poder | umbral | 6 | 3 | posible_autocuenta |
| sonidomuchacho | umbral | 6 | 3 | — |
| wilhelmusic | umbral | 6 | 3 | posible_autocuenta |
| antiguaybarbuda | umbral | 5 | 3 | posible_autocuenta |
| aterpe | umbral | 5 | 3 | posible_autocuenta |
| estricalla | umbral | 5 | 3 | posible_autocuenta |
| presidentetapes | ambos | 5 | 3 | — |
| shintoma | umbral | 5 | 3 | posible_autocuenta |
| thewrongcorner | umbral | 5 | 3 | posible_autocuenta |
| afrihooop | umbral | 4 | 3 | posible_autocuenta |
| discoswalden | ambos | 4 | 3 | posible_autocuenta |
| eliscasado | umbral | 4 | 3 | posible_autocuenta |
| elnebularecordings | ambos | 4 | 3 | posible_autocuenta |
| silikonanswerindustries | umbral | 4 | 3 | posible_autocuenta |
| withinthedarkwoods | umbral | 4 | 3 | — |
| ziztadarlantz | umbral | 4 | 3 | posible_autocuenta |
| brutalarratiarecords | ambos | 3 | 3 | posible_autocuenta |
| corsariosestudios | umbral | 3 | 3 | — |
| eduardozr | umbral | 3 | 3 | posible_autocuenta |
| elkarvinylcollection | umbral | 3 | 3 | posible_VA |
| gudaridubrecords | ambos | 3 | 3 | — |
| javip3z | umbral | 3 | 3 | — |
| kontra-k | umbral | 3 | 3 | posible_autocuenta |
| moimoicollectif | umbral | 3 | 3 | — |
| queimada-circuit-records | ambos | 3 | 3 | — |
| rolangarces | umbral | 3 | 3 | posible_autocuenta |
| samelevel | umbral | 3 | 3 | — |
| thecovenantband | umbral | 3 | 3 | posible_autocuenta |
| truthtown | umbral | 3 | 3 | — |
| yojimboi | umbral | 3 | 3 | — |
| petruskarecords | ambos | 49 | 2 | borde_2artistas, posible_autocuenta |
| theetherensemble | umbral | 41 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| wldv | umbral | 31 | 2 | borde_2artistas, posible_VA, posible_autocuenta |
| revolutionarybrothers | umbral | 17 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| laagoniadevivir | umbral | 15 | 2 | borde_2artistas, posible_autocuenta |
| glyyyydan | umbral | 14 | 2 | borde_2artistas |
| cosmichyrax | umbral | 13 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| kalekourdangak | umbral | 13 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| rivendel | umbral | 11 | 2 | borde_2artistas, posible_autocuenta |
| uyulala | umbral | 10 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| gravelbed | umbral | 9 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| keuagirretxea | umbral | 9 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| kultokultibo | umbral | 9 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| txomusika | umbral | 9 | 2 | borde_2artistas |
| angelocray | umbral | 8 | 2 | borde_2artistas, posible_autocuenta |
| elbisrever | umbral | 8 | 2 | borde_2artistas, posible_autocuenta |
| gussycanciones | umbral | 8 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| jonmusika | umbral | 8 | 2 | borde_2artistas, nombre_anidado |
| mondolava | umbral | 8 | 2 | borde_2artistas, posible_autocuenta |
| niacoyoteetachicotornado | umbral | 8 | 2 | borde_2artistas |
| juantxozeberioetxetxipia | umbral | 7 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| naveartificial | umbral | 7 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| phlgz | umbral | 7 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| drmugre | umbral | 6 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| gazlimbo | umbral | 6 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| janjodidaactitudnormal | umbral | 6 | 2 | borde_2artistas, posible_autocuenta |
| jimmybidaurreta | umbral | 6 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| juanortiz | umbral | 6 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| muyfellini | umbral | 6 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| obstetragrind | umbral | 6 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| passionfarolas | umbral | 6 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| samuelcano | umbral | 6 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| tartalomusic | umbral | 6 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| themussels | umbral | 6 | 2 | borde_2artistas |
| zarataselektion | umbral | 6 | 2 | borde_2artistas, posible_autocuenta |
| 12tribu | umbral | 5 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| 1991taldea | umbral | 5 | 2 | borde_2artistas |
| djyuju | umbral | 5 | 2 | borde_2artistas, posible_autocuenta |
| garazigorostiaga | umbral | 5 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| losrequesones | umbral | 5 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| nicolasceretti | umbral | 5 | 2 | borde_2artistas, posible_autocuenta |
| notokarrecords | ambos | 5 | 2 | borde_2artistas, posible_autocuenta |
| perlata | umbral | 5 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| sosharp | umbral | 5 | 2 | borde_2artistas |
| telmotrenor | umbral | 5 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| viborahc | umbral | 5 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| ziakhus | umbral | 5 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| costasmusic | umbral | 4 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| dexmusiccom | umbral | 4 | 2 | borde_2artistas |
| fatheralien | umbral | 4 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| flyshit | umbral | 4 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| hirugarrenbelarria | umbral | 4 | 2 | borde_2artistas, nombre_anidado |
| imago4 | umbral | 4 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| jabalinamusica | umbral | 4 | 2 | borde_2artistas |
| lasonrisametalica | umbral | 4 | 2 | borde_2artistas, posible_autocuenta |
| liot103 | umbral | 4 | 2 | borde_2artistas |
| losnerviosos | umbral | 4 | 2 | borde_2artistas, posible_autocuenta |
| surfinkaos | umbral | 4 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| veronicaolmos | umbral | 4 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| xabibasterra | umbral | 4 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| adamwoolf | umbral | 3 | 2 | borde_2artistas, posible_autocuenta |
| aitorrubio | umbral | 3 | 2 | borde_2artistas, posible_autocuenta |
| barbakorehc | umbral | 3 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| crownledge | umbral | 3 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| empireofdisease | umbral | 3 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| fustacello | umbral | 3 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| garon | umbral | 3 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| intoxikado | umbral | 3 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| jupiterjon | umbral | 3 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| kamorrah | umbral | 3 | 2 | borde_2artistas, posible_autocuenta |
| leilasix | umbral | 3 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| lodor | umbral | 3 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| lurrikararecords | ambos | 3 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| mktdiy | umbral | 3 | 2 | borde_2artistas |
| mondocanetaldea | umbral | 3 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| mryogo | umbral | 3 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| mvega | umbral | 3 | 2 | borde_2artistas, nombre_anidado |
| nokomplytaldea | umbral | 3 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| pomeray | umbral | 3 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| radixrecords | ambos | 3 | 2 | borde_2artistas |
| seriesnegras | umbral | 3 | 2 | borde_2artistas, nombre_anidado |
| showsaone | umbral | 3 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| sigeruban | umbral | 3 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| siracoel | umbral | 3 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| sunnywrightiv | umbral | 3 | 2 | borde_2artistas |
| wavyrootz | umbral | 3 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| ainaraortega | umbral | 2 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| aitorhuergo | umbral | 2 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| alfredadler | umbral | 2 | 2 | borde_2artistas |
| andreiklee | umbral | 2 | 2 | borde_2artistas, nombre_anidado |
| atta | umbral | 2 | 2 | borde_2artistas, nombre_anidado |
| ayosilver | umbral | 2 | 2 | borde_2artistas |
| benaranks | umbral | 2 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| bizarraetaberegitarrazaharra | umbral | 2 | 2 | borde_2artistas, posible_autocuenta |
| blackearthsindustriesrecords | ambos | 2 | 2 | borde_2artistas |
| brayanroman | umbral | 2 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| chillmafia | umbral | 2 | 2 | borde_2artistas |
| corvuscaelum | umbral | 2 | 2 | borde_2artistas, posible_autocuenta |
| cosmictentacles | umbral | 2 | 2 | borde_2artistas |
| cromrecords | ambos | 2 | 2 | borde_2artistas |
| dantzrecords | ambos | 2 | 2 | borde_2artistas, posible_VA |
| demokraziazero | umbral | 2 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| elsrramon | umbral | 2 | 2 | borde_2artistas, posible_autocuenta |
| erraldoirecords | ambos | 2 | 2 | borde_2artistas |
| hombremontana | umbral | 2 | 2 | borde_2artistas |
| hostoak | umbral | 2 | 2 | borde_2artistas, posible_autocuenta |
| humanosintentandolo | umbral | 2 | 2 | borde_2artistas, posible_autocuenta |
| iont | umbral | 2 | 2 | borde_2artistas, posible_autocuenta |
| isvkmyr | umbral | 2 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| jauja1 | umbral | 2 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| javiercpc | umbral | 2 | 2 | borde_2artistas |
| jgcproducciones | ambos | 2 | 2 | borde_2artistas |
| jonminer | umbral | 2 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| kalipotxo | umbral | 2 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| knekelput | umbral | 2 | 2 | borde_2artistas |
| ktcdomesticproductions | umbral | 2 | 2 | borde_2artistas |
| latxosa | umbral | 2 | 2 | borde_2artistas |
| lucindarecords | ambos | 2 | 2 | borde_2artistas |
| luzdeputas | umbral | 2 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| magmadam | umbral | 2 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| mikelirazabal | umbral | 2 | 2 | borde_2artistas, posible_autocuenta |
| monasteriodeculturarec | umbral | 2 | 2 | borde_2artistas |
| nigma | umbral | 2 | 2 | borde_2artistas, posible_VA |
| nooirax | umbral | 2 | 2 | borde_2artistas |
| onmusika | umbral | 2 | 2 | borde_2artistas, nombre_anidado |
| prismates | umbral | 2 | 2 | borde_2artistas, posible_autocuenta |
| repentinorecords | ambos | 2 | 2 | borde_2artistas |
| runawaylovers | umbral | 2 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| shibaritaldea | umbral | 2 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| sonaraccionesylugares | umbral | 2 | 2 | borde_2artistas, posible_autocuenta |
| sweattaste | umbral | 2 | 2 | borde_2artistas, nombre_anidado |
| themclovings | umbral | 2 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| thexbeats90 | umbral | 2 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| tibprod | umbral | 2 | 2 | borde_2artistas |
| tkuento | umbral | 2 | 2 | borde_2artistas, posible_autocuenta |
| uhinzine | umbral | 2 | 2 | borde_2artistas, posible_autocuenta |
| ulzion | umbral | 2 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| weareapeshello | umbral | 2 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| mendekudiskak | lexico | 24 | 1 | posible_autocuenta |
| makramerecords | lexico | 21 | 1 | posible_autocuenta |
| zirikaturecords | lexico | 19 | 1 | posible_autocuenta |
| blackvoguerecords | lexico | 17 | 1 | posible_autocuenta |
| daimnicagrabaciones | lexico | 9 | 1 | — |
| hopeandfaithrecords | lexico | 7 | 1 | — |
| gatazkabasslabel | lexico | 5 | 1 | posible_autocuenta |
| produccionestudancas | lexico | 5 | 1 | posible_autocuenta |
| gbcrecords | lexico | 4 | 1 | — |
| cactuslabel | lexico | 3 | 1 | — |
| gondolinrecords | lexico | 2 | 1 | — |
| nunatakrecords | lexico | 2 | 1 | — |
| slowdownrecords | lexico | 2 | 1 | posible_autocuenta |
| augerecords | lexico | 1 | 1 | — |
| batchrecords | lexico | 1 | 1 | — |
| beatsaladrecords | lexico | 1 | 1 | — |
| colillarecords | lexico | 1 | 1 | — |
| crapouletrecords | lexico | 1 | 1 | — |
| cruelnaturerecordings | lexico | 1 | 1 | — |
| ddtbanaketakbilbo | lexico | 1 | 1 | posible_autocuenta |
| discoshumeantes | lexico | 1 | 1 | — |
| elsarecords | lexico | 1 | 1 | — |
| extralovelyrecords | lexico | 1 | 1 | — |
| fatbirdrecordings | lexico | 1 | 1 | — |
| flexidiscos | lexico | 1 | 1 | — |
| flooprecordings | lexico | 1 | 1 | — |
| folcrecords | lexico | 1 | 1 | posible_autocuenta |
| furiousrecords | lexico | 1 | 1 | — |
| gaziarecords | lexico | 1 | 1 | — |
| greencookierecords | lexico | 1 | 1 | — |
| hangthedjrecords | lexico | 1 | 1 | — |
| harrobirecords | lexico | 1 | 1 | posible_autocuenta |
| holaediciones | lexico | 1 | 1 | — |
| homerecordsbe | lexico | 1 | 1 | — |
| idealstaterecordings | lexico | 1 | 1 | — |
| intergalacticrecords | lexico | 1 | 1 | — |
| isilyarecords | lexico | 1 | 1 | — |
| kastillorecords | lexico | 1 | 1 | posible_autocuenta |
| kilkirrecords | lexico | 1 | 1 | — |
| killvinylrecords | lexico | 1 | 1 | — |
| kumbalenetlabel | lexico | 1 | 1 | — |
| lafamiliarevolucionrecords | lexico | 1 | 1 | — |
| lenorecords | lexico | 1 | 1 | — |
| likidorecords | lexico | 1 | 1 | — |
| madschnauzerrecords | lexico | 1 | 1 | — |
| mamavynilarecords | lexico | 1 | 1 | — |
| mawashiskinsrecords | lexico | 1 | 1 | — |
| meyorecords | lexico | 1 | 1 | — |
| mundiscos | lexico | 1 | 1 | — |
| musikagelarecords | lexico | 1 | 1 | — |
| niunpeloderubiasrecords | lexico | 1 | 1 | — |
| noaloharecords | lexico | 1 | 1 | — |
| nortepuromusicrecords | lexico | 1 | 1 | — |
| notomorrowrecords | lexico | 1 | 1 | posible_autocuenta |
| origamirecords | lexico | 1 | 1 | — |
| plasticwoundrecords | lexico | 1 | 1 | posible_autocuenta |
| politburorecordingfiasco | lexico | 1 | 1 | — |
| psilocybina-records | lexico | 1 | 1 | posible_autocuenta |
| quebrantarecords | lexico | 1 | 1 | — |
| remorserecords | lexico | 1 | 1 | — |
| reposerecords | lexico | 1 | 1 | — |
| rockizarrecords | lexico | 1 | 1 | — |
| saturnorecords | lexico | 1 | 1 | — |
| sentenciarecords | lexico | 1 | 1 | — |
| smilingisnotacrimerecords | lexico | 1 | 1 | — |
| steadyriotrecords | lexico | 1 | 1 | — |
| stonehengerecords | lexico | 1 | 1 | — |
| subspecieslabel | lexico | 1 | 1 | posible_VA |
| szenarecords | lexico | 1 | 1 | — |
| taerecords | lexico | 1 | 1 | — |
| tanukirecords | lexico | 1 | 1 | — |
| tayulrecords | lexico | 1 | 1 | — |
| theiarecords | lexico | 1 | 1 | — |
| throatruinerrecords | lexico | 1 | 1 | — |
| uglyandproudrecords | lexico | 1 | 1 | — |
| urticariarecords | lexico | 1 | 1 | — |

## Sin flags (sellos limpios, menos revisión)

Candidatas que no disparan ninguna bandera: los sellos más claros.

| account_id | n_discos | n_artistas |
| :--- | ---: | ---: |
| polygonnetwork | 82 | 51 |
| muertematarrecords | 40 | 35 |
| custom:crudobilbao.com | 51 | 33 |
| bidehuts | 52 | 24 |
| esnebidearecords | 34 | 20 |
| timbamuziklab | 29 | 18 |
| bangrecords | 20 | 18 |
| somniferumrec | 18 | 18 |
| bombbasshifi | 17 | 16 |
| forbiddencolours | 16 | 15 |
| orruadiskak | 45 | 13 |
| belarri | 13 | 13 |
| deepnas | 13 | 13 |
| vyramed | 11 | 8 |
| senoidrecordings | 10 | 8 |
| ekinmusic | 31 | 7 |
| goxoa | 15 | 7 |
| untalasalsa | 11 | 7 |
| zaragozadesordenrecords | 11 | 7 |
| kristonzintak | 7 | 7 |
| rawsurfacerecords | 16 | 6 |
| tritonegrabaciones | 7 | 6 |
| grabacionesviscerales | 6 | 6 |
| alonereggaeshop | 10 | 5 |
| caballitorecords | 9 | 5 |
| edervxga | 9 | 5 |
| dungeonlordrecords | 8 | 5 |
| monocat7 | 8 | 5 |
| unsound-methods | 5 | 5 |
| raso | 6 | 4 |
| azkarzintak | 5 | 4 |
| kaliyugayouth | 5 | 4 |
| lavidaesunmus | 5 | 4 |
| chin-chinrecordsmundiales | 4 | 4 |
| crystalmine | 4 | 4 |
| dialectoperiferico | 4 | 4 |
| infrarecords | 4 | 4 |
| sustraiakrecords | 4 | 4 |
| xedh | 4 | 4 |
| zulo8 | 4 | 4 |
| miusichole | 22 | 3 |
| sonidomuchacho | 6 | 3 |
| presidentetapes | 5 | 3 |
| withinthedarkwoods | 4 | 3 |
| corsariosestudios | 3 | 3 |
| gudaridubrecords | 3 | 3 |
| javip3z | 3 | 3 |
| moimoicollectif | 3 | 3 |
| queimada-circuit-records | 3 | 3 |
| samelevel | 3 | 3 |
| truthtown | 3 | 3 |
| yojimboi | 3 | 3 |
| daimnicagrabaciones | 9 | 1 |
| hopeandfaithrecords | 7 | 1 |
| gbcrecords | 4 | 1 |
| cactuslabel | 3 | 1 |
| gondolinrecords | 2 | 1 |
| nunatakrecords | 2 | 1 |
| augerecords | 1 | 1 |
| batchrecords | 1 | 1 |
| beatsaladrecords | 1 | 1 |
| colillarecords | 1 | 1 |
| crapouletrecords | 1 | 1 |
| cruelnaturerecordings | 1 | 1 |
| discoshumeantes | 1 | 1 |
| elsarecords | 1 | 1 |
| extralovelyrecords | 1 | 1 |
| fatbirdrecordings | 1 | 1 |
| flexidiscos | 1 | 1 |
| flooprecordings | 1 | 1 |
| furiousrecords | 1 | 1 |
| gaziarecords | 1 | 1 |
| greencookierecords | 1 | 1 |
| hangthedjrecords | 1 | 1 |
| holaediciones | 1 | 1 |
| homerecordsbe | 1 | 1 |
| idealstaterecordings | 1 | 1 |
| intergalacticrecords | 1 | 1 |
| isilyarecords | 1 | 1 |
| kilkirrecords | 1 | 1 |
| killvinylrecords | 1 | 1 |
| kumbalenetlabel | 1 | 1 |
| lafamiliarevolucionrecords | 1 | 1 |
| lenorecords | 1 | 1 |
| likidorecords | 1 | 1 |
| madschnauzerrecords | 1 | 1 |
| mamavynilarecords | 1 | 1 |
| mawashiskinsrecords | 1 | 1 |
| meyorecords | 1 | 1 |
| mundiscos | 1 | 1 |
| musikagelarecords | 1 | 1 |
| niunpeloderubiasrecords | 1 | 1 |
| noaloharecords | 1 | 1 |
| nortepuromusicrecords | 1 | 1 |
| origamirecords | 1 | 1 |
| politburorecordingfiasco | 1 | 1 |
| quebrantarecords | 1 | 1 |
| remorserecords | 1 | 1 |
| reposerecords | 1 | 1 |
| rockizarrecords | 1 | 1 |
| saturnorecords | 1 | 1 |
| sentenciarecords | 1 | 1 |
| smilingisnotacrimerecords | 1 | 1 |
| steadyriotrecords | 1 | 1 |
| stonehengerecords | 1 | 1 |
| szenarecords | 1 | 1 |
| taerecords | 1 | 1 |
| tanukirecords | 1 | 1 |
| tayulrecords | 1 | 1 |
| theiarecords | 1 | 1 |
| throatruinerrecords | 1 | 1 |
| uglyandproudrecords | 1 | 1 |
| urticariarecords | 1 | 1 |

## Dominios propios (`custom:`)

| account_id | n_discos | n_artistas |
| :--- | ---: | ---: |
| custom:crudobilbao.com | 51 | 33 |
| custom:ekiza.com | 5 | 1 |
| custom:attemptfactory.com | 1 | 1 |
| custom:music.therodeoidiotengine.com | 1 | 1 |
| custom:wavememory.net | 1 | 1 |
| custom:zeromoon.com | 1 | 1 |

## Huecos honestos (URLs sin subdominio)

Discos cuya `url` está vacía o es exactamente `bandcamp.com`: no se pueden atribuir a una cuenta. Se listan aparte, no rompen el pipeline.

| id | artist | title | url |
| ---: | :--- | :--- | :--- |
| 234 | Elena Setién, GranDays & Xabier Erkizia | Mirande | — |
| 1257 | MaBy Kerwin | Lofi Ninja | — |
| 1538 | Monday Potions | Monday Potions - Sea Green | — |
| 1539 | Monday Potions | Monday Potions - Floral White | — |
| 1630 | J. Bilbao | All Life - Bizi Guztia | — |

