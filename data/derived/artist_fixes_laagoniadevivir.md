# Corrección manual — `laagoniadevivir` (grafía «La Agonía Vivir», sin "de")

Excepción explícita y cerrada para **una** cuenta. El sello `laagoniadevivir` se acredita con dos grafías; la variante «La Agonía de Vivir» ya se corrigió en su PR (foldaba al subdominio). Esta variante «La Agonía Vivir» (sin "de") **no** folda, así que la corrección automática la dejó fuera a propósito. Aquí se corrigen esas **8 filas a mano**, sin ampliar ni tocar la lógica de `scripts/fix_artist_from_title.py`. Mismo patrón P2: `LADV### - ARTISTA "Título" [formato]`. Solo cambia el campo `artist`.

- Filas de la excepción: **8** (todas de `laagoniadevivir`, patrón P2).
- Aplicadas en esta ejecución: **8**.

| id | album_id | artist actual | artist propuesto | patrón | title original |
| ---: | ---: | :--- | :--- | :--- | :--- |
| 146 | 3043169698 | La Agonía Vivir | **MÁRMOL** | P2 | `LADV166 - MÁRMOL "declaración total de guerra" LP` |
| 163 | 3399851741 | La Agonía Vivir | **OHIL** | P2 | `LADV206 - OHIL "akorde beste orbain" LP` |
| 909 | 3233000682 | La Agonía Vivir | **DESPEÑAPERROS** | P2 | `LADV60 - DESPEÑAPERROS "herejía" LP` |
| 1151 | 1232650862 | La Agonía Vivir | **DIANA LAGARTO** | P2 | `LADV39 - DIANA LAGARTO "st" LP` |
| 1156 | 2233289320 | La Agonía Vivir | **URA** | P2 | `LADV45 - URA "st" 12"` |
| 1258 | 3729234297 | La Agonía Vivir | **1991** | P2 | `LADV46 - 1991 "st" 12"` |
| 1355 | 262980317 | La Agonía Vivir | **ANCIENT EMBLEM** | P2 | `LADV38 - ANCIENT EMBLEM "throne with no god" LP` |
| 1356 | 3400350081 | La Agonía Vivir | **DESPEÑAPERROS** | P2 | `LADV16 - DESPEÑAPERROS "el foso" 7"` |

