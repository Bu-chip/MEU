# Índice de sellos — Fase 1 (derivado, read-only)

Dato derivado del subdominio de `url` en el canónico. Un **sello candidato** es una cuenta con **>= 2 artistas distintos** (matiz A, sin más filtros). Los flags MARCAN casos para revisión humana; **nunca descartan**.

## Totales

- Cuentas totales (con cuenta atribuible): **2588**
- Candidatas a sello (>= 2 artistas): **244**
- Candidatos **antes / después** de endurecer la normalización: **335 → 244** (−91)
- Discos cubiertos por candidatas: **2222** de 7568 (**29.4%** del catálogo)
- Cuentas con dominio propio (`custom:`): **6**
- Huecos honestos (url vacía o `bandcamp.com`): **5**

### Recuento por flag (dentro de las candidatas)

- `borde_2artistas` (exactamente 2 artistas): **138**
- `posible_VA` (Various Artists / VA / V.A. / Various): **11**
- `nombre_anidado` (2 clusters, uno contenido en el otro; featurings/alias): **78**
- `posible_autocuenta` (id de cuenta ≈ nombre de un artista propio; tiene falsos positivos, revisión humana): **144**
- **Sin ningún flag** (sellos limpios): **54**

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

## Sellos candidatos (orden: nº artistas desc, nº discos desc, account_id asc)

| account_id | n_discos | n_artistas | flags |
| :--- | ---: | ---: | :--- |
| zaratazarautz | 97 | 94 | posible_autocuenta |
| musexindustries | 105 | 81 | posible_VA |
| polygonnetwork | 82 | 51 | — |
| eclecticreactionsrecords | 53 | 48 | — |
| muertematarrecords | 40 | 35 | — |
| custom:crudobilbao.com | 51 | 33 | — |
| bidehuts | 52 | 24 | — |
| inguma | 27 | 23 | posible_VA |
| esnebidearecords | 34 | 20 | — |
| timbamuziklab | 29 | 18 | — |
| bangrecords | 20 | 18 | — |
| somniferumrec | 18 | 18 | — |
| bombbasshifi | 17 | 16 | — |
| forbiddencolours | 16 | 15 | — |
| zawpklem | 22 | 14 | posible_VA |
| bassleemusic | 16 | 14 | posible_autocuenta |
| orruadiskak | 45 | 13 | — |
| belarri | 13 | 13 | — |
| deepnas | 13 | 13 | — |
| ensemblesinkro | 20 | 12 | posible_autocuenta |
| raperosdeemaus | 35 | 11 | posible_autocuenta |
| secretsocietychile | 22 | 9 | posible_VA, posible_autocuenta |
| sustraidunyouths | 17 | 8 | posible_autocuenta |
| vyramed | 11 | 8 | — |
| discosbanana1 | 10 | 8 | posible_autocuenta |
| senoidrecordings | 10 | 8 | — |
| familyspreerecordings | 8 | 8 | posible_autocuenta |
| haziesporak | 8 | 8 | posible_VA |
| ekinmusic | 31 | 7 | — |
| clartycat | 25 | 7 | posible_VA |
| josebairazoki | 25 | 7 | posible_autocuenta |
| goxoa | 15 | 7 | — |
| untalasalsa | 11 | 7 | — |
| zaragozadesordenrecords | 11 | 7 | — |
| kristonzintak | 7 | 7 | — |
| javiersun | 17 | 6 | posible_autocuenta |
| rawsurfacerecords | 16 | 6 | — |
| camilomateo | 14 | 6 | posible_autocuenta |
| wolkokrots | 13 | 6 | posible_autocuenta |
| thetitanians | 9 | 6 | posible_autocuenta |
| tritonegrabaciones | 7 | 6 | — |
| grabacionesviscerales | 6 | 6 | — |
| ghettogunshotrecords | 13 | 5 | posible_autocuenta |
| alonereggaeshop | 10 | 5 | — |
| caballitorecords | 9 | 5 | — |
| edervxga | 9 | 5 | — |
| dungeonlordrecords | 8 | 5 | — |
| monocat7 | 8 | 5 | — |
| txiltxoko | 8 | 5 | posible_autocuenta |
| valdokmusic | 8 | 5 | posible_autocuenta |
| maukamusik | 7 | 5 | posible_autocuenta |
| unsound-methods | 5 | 5 | — |
| breathingthecore | 57 | 4 | posible_VA, posible_autocuenta |
| sergiozurutuza | 17 | 4 | posible_autocuenta |
| elcrack | 10 | 4 | posible_autocuenta |
| antoinebellanger | 9 | 4 | posible_autocuenta |
| raso | 6 | 4 | — |
| azkarzintak | 5 | 4 | — |
| discosdekirlian | 5 | 4 | — |
| kaliyugayouth | 5 | 4 | — |
| lavidaesunmus | 5 | 4 | — |
| chin-chinrecordsmundiales | 4 | 4 | — |
| crystalmine | 4 | 4 | — |
| dialectoperiferico | 4 | 4 | — |
| infrarecords | 4 | 4 | — |
| isuo | 4 | 4 | posible_autocuenta |
| sustraiakrecords | 4 | 4 | — |
| xedh | 4 | 4 | — |
| zulo8 | 4 | 4 | — |
| joanakaredmoon | 23 | 3 | posible_autocuenta |
| miusichole | 22 | 3 | — |
| enochsvision | 11 | 3 | posible_VA, posible_autocuenta |
| txarlyusher | 9 | 3 | posible_autocuenta |
| 25thcomingfire | 7 | 3 | posible_autocuenta |
| jamesroom | 7 | 3 | posible_autocuenta |
| maitelarburu | 6 | 3 | posible_autocuenta |
| poder | 6 | 3 | posible_autocuenta |
| sonidomuchacho | 6 | 3 | — |
| wilhelmusic | 6 | 3 | posible_autocuenta |
| antiguaybarbuda | 5 | 3 | posible_autocuenta |
| aterpe | 5 | 3 | posible_autocuenta |
| estricalla | 5 | 3 | posible_autocuenta |
| presidentetapes | 5 | 3 | — |
| shintoma | 5 | 3 | posible_autocuenta |
| thewrongcorner | 5 | 3 | posible_autocuenta |
| afrihooop | 4 | 3 | posible_autocuenta |
| discoswalden | 4 | 3 | posible_autocuenta |
| eliscasado | 4 | 3 | posible_autocuenta |
| elnebularecordings | 4 | 3 | posible_autocuenta |
| silikonanswerindustries | 4 | 3 | posible_autocuenta |
| withinthedarkwoods | 4 | 3 | — |
| ziztadarlantz | 4 | 3 | posible_autocuenta |
| brutalarratiarecords | 3 | 3 | posible_autocuenta |
| corsariosestudios | 3 | 3 | — |
| eduardozr | 3 | 3 | posible_autocuenta |
| elkarvinylcollection | 3 | 3 | posible_VA |
| gudaridubrecords | 3 | 3 | — |
| javip3z | 3 | 3 | — |
| kontra-k | 3 | 3 | posible_autocuenta |
| moimoicollectif | 3 | 3 | — |
| queimada-circuit-records | 3 | 3 | — |
| rolangarces | 3 | 3 | posible_autocuenta |
| samelevel | 3 | 3 | — |
| thecovenantband | 3 | 3 | posible_autocuenta |
| truthtown | 3 | 3 | — |
| yojimboi | 3 | 3 | — |
| petruskarecords | 49 | 2 | borde_2artistas, posible_autocuenta |
| theetherensemble | 41 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| wldv | 31 | 2 | borde_2artistas, posible_autocuenta |
| revolutionarybrothers | 17 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| laagoniadevivir | 15 | 2 | borde_2artistas, posible_autocuenta |
| glyyyydan | 14 | 2 | borde_2artistas |
| cosmichyrax | 13 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| kalekourdangak | 13 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| rivendel | 11 | 2 | borde_2artistas, posible_autocuenta |
| uyulala | 10 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| gravelbed | 9 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| keuagirretxea | 9 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| kultokultibo | 9 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| txomusika | 9 | 2 | borde_2artistas |
| angelocray | 8 | 2 | borde_2artistas, posible_autocuenta |
| elbisrever | 8 | 2 | borde_2artistas, posible_autocuenta |
| gussycanciones | 8 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| jonmusika | 8 | 2 | borde_2artistas, nombre_anidado |
| mondolava | 8 | 2 | borde_2artistas, posible_autocuenta |
| niacoyoteetachicotornado | 8 | 2 | borde_2artistas |
| juantxozeberioetxetxipia | 7 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| naveartificial | 7 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| phlgz | 7 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| drmugre | 6 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| gazlimbo | 6 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| janjodidaactitudnormal | 6 | 2 | borde_2artistas, posible_autocuenta |
| jimmybidaurreta | 6 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| juanortiz | 6 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| muyfellini | 6 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| obstetragrind | 6 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| passionfarolas | 6 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| samuelcano | 6 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| tartalomusic | 6 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| themussels | 6 | 2 | borde_2artistas |
| zarataselektion | 6 | 2 | borde_2artistas, posible_autocuenta |
| 12tribu | 5 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| 1991taldea | 5 | 2 | borde_2artistas |
| djyuju | 5 | 2 | borde_2artistas, posible_autocuenta |
| garazigorostiaga | 5 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| losrequesones | 5 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| nicolasceretti | 5 | 2 | borde_2artistas, posible_autocuenta |
| notokarrecords | 5 | 2 | borde_2artistas, posible_autocuenta |
| perlata | 5 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| sosharp | 5 | 2 | borde_2artistas |
| telmotrenor | 5 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| viborahc | 5 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| ziakhus | 5 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| costasmusic | 4 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| dexmusiccom | 4 | 2 | borde_2artistas |
| fatheralien | 4 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| flyshit | 4 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| hirugarrenbelarria | 4 | 2 | borde_2artistas, nombre_anidado |
| imago4 | 4 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| jabalinamusica | 4 | 2 | borde_2artistas |
| lasonrisametalica | 4 | 2 | borde_2artistas, posible_autocuenta |
| liot103 | 4 | 2 | borde_2artistas |
| losnerviosos | 4 | 2 | borde_2artistas, posible_autocuenta |
| surfinkaos | 4 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| veronicaolmos | 4 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| xabibasterra | 4 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| adamwoolf | 3 | 2 | borde_2artistas, posible_autocuenta |
| aitorrubio | 3 | 2 | borde_2artistas, posible_autocuenta |
| barbakorehc | 3 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| crownledge | 3 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| empireofdisease | 3 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| fustacello | 3 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| garon | 3 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| intoxikado | 3 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| jupiterjon | 3 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| kamorrah | 3 | 2 | borde_2artistas, posible_autocuenta |
| leilasix | 3 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| lodor | 3 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| lurrikararecords | 3 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| mktdiy | 3 | 2 | borde_2artistas |
| mondocanetaldea | 3 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| mryogo | 3 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| mvega | 3 | 2 | borde_2artistas, nombre_anidado |
| nokomplytaldea | 3 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| pomeray | 3 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| radixrecords | 3 | 2 | borde_2artistas |
| seriesnegras | 3 | 2 | borde_2artistas, nombre_anidado |
| showsaone | 3 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| sigeruban | 3 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| siracoel | 3 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| sunnywrightiv | 3 | 2 | borde_2artistas |
| wavyrootz | 3 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| ainaraortega | 2 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| aitorhuergo | 2 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| alfredadler | 2 | 2 | borde_2artistas |
| andreiklee | 2 | 2 | borde_2artistas, nombre_anidado |
| atta | 2 | 2 | borde_2artistas, nombre_anidado |
| ayosilver | 2 | 2 | borde_2artistas |
| benaranks | 2 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| bizarraetaberegitarrazaharra | 2 | 2 | borde_2artistas, posible_autocuenta |
| blackearthsindustriesrecords | 2 | 2 | borde_2artistas |
| brayanroman | 2 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| chillmafia | 2 | 2 | borde_2artistas |
| corvuscaelum | 2 | 2 | borde_2artistas, posible_autocuenta |
| cosmictentacles | 2 | 2 | borde_2artistas |
| cromrecords | 2 | 2 | borde_2artistas |
| dantzrecords | 2 | 2 | borde_2artistas, posible_VA |
| demokraziazero | 2 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| elsrramon | 2 | 2 | borde_2artistas, posible_autocuenta |
| erraldoirecords | 2 | 2 | borde_2artistas |
| hombremontana | 2 | 2 | borde_2artistas |
| hostoak | 2 | 2 | borde_2artistas, posible_autocuenta |
| humanosintentandolo | 2 | 2 | borde_2artistas, posible_autocuenta |
| iont | 2 | 2 | borde_2artistas, posible_autocuenta |
| isvkmyr | 2 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| jauja1 | 2 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| javiercpc | 2 | 2 | borde_2artistas |
| jgcproducciones | 2 | 2 | borde_2artistas |
| jonminer | 2 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| kalipotxo | 2 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| knekelput | 2 | 2 | borde_2artistas |
| ktcdomesticproductions | 2 | 2 | borde_2artistas |
| latxosa | 2 | 2 | borde_2artistas |
| lucindarecords | 2 | 2 | borde_2artistas |
| luzdeputas | 2 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| magmadam | 2 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| mikelirazabal | 2 | 2 | borde_2artistas, posible_autocuenta |
| monasteriodeculturarec | 2 | 2 | borde_2artistas |
| nigma | 2 | 2 | borde_2artistas, posible_VA |
| nooirax | 2 | 2 | borde_2artistas |
| onmusika | 2 | 2 | borde_2artistas, nombre_anidado |
| prismates | 2 | 2 | borde_2artistas, posible_autocuenta |
| repentinorecords | 2 | 2 | borde_2artistas |
| runawaylovers | 2 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| shibaritaldea | 2 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| sonaraccionesylugares | 2 | 2 | borde_2artistas, posible_autocuenta |
| sweattaste | 2 | 2 | borde_2artistas, nombre_anidado |
| themclovings | 2 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| thexbeats90 | 2 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| tibprod | 2 | 2 | borde_2artistas |
| tkuento | 2 | 2 | borde_2artistas, posible_autocuenta |
| uhinzine | 2 | 2 | borde_2artistas, posible_autocuenta |
| ulzion | 2 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |
| weareapeshello | 2 | 2 | borde_2artistas, nombre_anidado, posible_autocuenta |

## Sin flags (sellos limpios, menos revisión)

Candidatas que no disparan ninguna bandera: los sellos más claros.

| account_id | n_discos | n_artistas |
| :--- | ---: | ---: |
| polygonnetwork | 82 | 51 |
| eclecticreactionsrecords | 53 | 48 |
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
| discosdekirlian | 5 | 4 |
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

