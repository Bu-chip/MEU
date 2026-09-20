# Auditoría: ubicaciones procedentes de cuentas multiartista

*Generado por `python3 scripts/multiartist_audit.py` (solo lectura). No cambia datos ni semántica.*

«Cuenta multiartista» = cuenta en `data/derived/labels.json` (índice heurístico de sellos: ≥2 artistas distintos o léxico de sello). Su ubicación en Bandcamp es la de la cuenta, no necesariamente la del grupo.

## Cifras

| # | Métrica | Releases | % de localizadas |
|---|---|---:|---:|
| 1 | Releases con ubicación resuelta (mapa por defecto) | 6587 | 100 % |
| 2 | Ubicación directa (Bandcamp en esta release; incluye manual: 0) | 5018 | 76.2 % |
| 3 | Inferidas por otra release/cuenta o por artista | 1569 | 23.8 % |
| 3a | · misma cuenta (same_account) | 1486 | 22.6 % |
| 3b | · mismo artista (artist_inferred; nunca desde cuentas multiartista) | 83 | 1.3 % |
| 4 | Inferidas que proceden de cuentas multiartista | 618 | 9.4 % |
| 4b | *Aparte:* directas cuya cuenta es multiartista (también ciudad de la cuenta) | 1358 | 20.6 % |
| 5 | Cuentas multiartista implicadas (inferidas) | 74 | |
| 5b | Cuentas multiartista implicadas (inferidas + directas) | 215 | |
| 8 | Mapa que desaparecería sin inferencias (escenario B) | 1569 | 23.8 % |
| 8b | Mapa que desaparecería sin nada que venga de cuentas multiartista (4 + 4b) | 1976 | 30.0 % |

## 6. Las 20 cuentas multiartista que más releases sitúan

| Cuenta | Releases situadas | vía misma cuenta | directas | Artistas distintos | Municipio(s) |
|---|---:|---:|---:|---:|---|
| `musexindustries` | 105 | 0 | 105 | 81 | Iruñea (105) |
| `zaratazarautz` | 98 | 1 | 97 | 95 | Zarautz (98) |
| `polygonnetwork` | 82 | 74 | 8 | 51 | Bilbo (82) |
| `breathingthecore` | 57 | 55 | 2 | 4 | Bilbo (57) |
| `eclecticreactionsrecords` | 53 | 47 | 6 | 48 | Bilbo (53) |
| `custom:crudobilbao.com` | 51 | 50 | 1 | 34 | Bilbo (51) |
| `petruskarecords` | 49 | 0 | 49 | 3 | Irun (49) |
| `orruadiskak` | 45 | 0 | 45 | 14 | Zarautz (45) |
| `theetherensemble` | 41 | 40 | 1 | 2 | Bilbo (41) |
| `muertematarrecords` | 40 | 2 | 38 | 35 | Santurtzi (40) |
| `raperosdeemaus` | 35 | 0 | 35 | 11 | Iruñea (35) |
| `wldv` | 32 | 28 | 4 | 2 | Bilbo (32) |
| `ekinmusic` | 31 | 0 | 31 | 7 | Donostia (31) |
| `timbamuziklab` | 29 | 0 | 29 | 19 | Donostia (29) |
| `inguma` | 27 | 0 | 27 | 23 | Donostia (27) |
| `clartycat` | 25 | 0 | 25 | 7 | Donostia (25) |
| `joanakaredmoon` | 23 | 0 | 23 | 6 | Iruñea (23) |
| `miusichole` | 22 | 21 | 1 | 3 | Bilbo (22) |
| `secretsocietychile` | 22 | 0 | 22 | 10 | Iruñea (22) |
| `zawpklem` | 22 | 21 | 1 | 14 | Bilbo (22) |

## 7. Municipios que más releases reciben por esta vía

| Municipio | Inferidas desde cuenta multiartista | Todo lo que viene de cuentas multiartista | Total en el mapa | % del municipio desde cuentas multiartista |
|---|---:|---:|---:|---:|
| Bilbo | 612 | 768 | 2469 | 31.1 % |
| Donostia | 0 | 357 | 1005 | 35.5 % |
| Iruñea | 0 | 298 | 925 | 32.2 % |
| Zarautz | 1 | 165 | 280 | 58.9 % |
| Gasteiz | 0 | 126 | 557 | 22.6 % |
| Santurtzi | 2 | 62 | 75 | 82.7 % |
| Irun | 0 | 61 | 113 | 54.0 % |
| Portugalete | 0 | 25 | 41 | 61.0 % |
| Andoain | 0 | 14 | 33 | 42.4 % |
| Kanbo | 0 | 13 | 13 | 100.0 % |
| Arrasate | 0 | 12 | 49 | 24.5 % |
| Ondarroa | 0 | 11 | 39 | 28.2 % |
| Itsasu | 0 | 9 | 9 | 100.0 % |
| Oiartzun | 0 | 8 | 35 | 22.9 % |
| Getxo | 0 | 7 | 93 | 7.5 % |

## Escenarios

| | A — actual (directas + inferidas) | B — conservador (solo directas/manual) | C — extra: B sin cuentas multiartista | D — extra: A sin inferencias desde cuentas multiartista |
|---|---:|---:|---:|---:|
| Releases localizadas | 6587 | 5018 | 3660 | 5969 |
| % del catálogo (7637) | 86.3 % | 65.7 % | 47.9 % | 78.2 % |
| Municipios visibles | 104 | 104 | 101 | 104 |

**Ojo al leer B.** `same_account` no es una inferencia débil: Bandcamp localiza la *cuenta*, así que en una cuenta de un solo artista es el mismo dato que `direct`. En el catálogo original de Bilbao se visitó **una ficha por cuenta** (fase 3), así que el resto de releases de cada cuenta quedaron como `same_account`: B castiga sobre todo ese artefacto de método, no evidencia peor. D quita solo lo realmente dudoso.

| Municipio | same_account (cuenta de un artista) | same_account (cuenta multiartista) |
|---|---:|---:|
| Bilbo | 857 | 612 |
| Donostia | 4 | 0 |
| Gernika-Lumo | 2 | 0 |
| Irulegi | 1 | 0 |
| Bera | 1 | 0 |
| Sopela | 1 | 0 |

### Top 15 municipios

| # | A | B | C | D |
|---:|---|---|---|---|
| 1 | Bilbo 2469 | Donostia 987 | Bilbo 814 | Bilbo 1857 |
| 2 | Donostia 1005 | Bilbo 970 | Donostia 630 | Donostia 1005 |
| 3 | Iruñea 925 | Iruñea 907 | Iruñea 609 | Iruñea 925 |
| 4 | Gasteiz 557 | Gasteiz 550 | Gasteiz 424 | Gasteiz 557 |
| 5 | Zarautz 280 | Zarautz 279 | Zarautz 115 | Zarautz 279 |
| 6 | Irun 113 | Irun 113 | Getxo 84 | Irun 113 |
| 7 | Getxo 93 | Getxo 91 | Hondarribia 59 | Getxo 93 |
| 8 | Santurtzi 75 | Santurtzi 73 | Barakaldo 55 | Santurtzi 73 |
| 9 | Hondarribia 59 | Hondarribia 59 | Errenteria 53 | Hondarribia 59 |
| 10 | Errenteria 58 | Errenteria 58 | Irun 52 | Errenteria 58 |
| 11 | Barakaldo 56 | Barakaldo 55 | Leioa 48 | Barakaldo 56 |
| 12 | Arrasate 49 | Arrasate 48 | Bermeo 41 | Arrasate 49 |
| 13 | Leioa 48 | Leioa 48 | Gernika-Lumo 39 | Leioa 48 |
| 14 | Gernika-Lumo 43 | Bermeo 41 | Arrasate 36 | Gernika-Lumo 43 |
| 15 | Bermeo 43 | Portugalete 41 | Eibar 34 | Bermeo 43 |

### Mayores diferencias A → B (releases que se pierden)

| Municipio | A | B | Pierde | % que conserva | Cuota del mapa A → B |
|---|---:|---:|---:|---:|---|
| Bilbo | 2469 | 970 | 1499 | 39.3 % | 37.5 % → 19.3 % |
| Donostia | 1005 | 987 | 18 | 98.2 % | 15.3 % → 19.7 % |
| Iruñea | 925 | 907 | 18 | 98.1 % | 14.0 % → 18.1 % |
| Gasteiz | 557 | 550 | 7 | 98.7 % | 8.5 % → 11.0 % |
| Gernika-Lumo | 43 | 39 | 4 | 90.7 % | 0.7 % → 0.8 % |
| Laudio | 22 | 19 | 3 | 86.4 % | 0.3 % → 0.4 % |
| Eibar | 37 | 34 | 3 | 91.9 % | 0.6 % → 0.7 % |
| Sopela | 11 | 9 | 2 | 81.8 % | 0.2 % → 0.2 % |
| Santurtzi | 75 | 73 | 2 | 97.3 % | 1.1 % → 1.5 % |
| Getxo | 93 | 91 | 2 | 97.8 % | 1.4 % → 1.8 % |
| Bermeo | 43 | 41 | 2 | 95.3 % | 0.7 % → 0.8 % |
| Hernani | 32 | 30 | 2 | 93.8 % | 0.5 % → 0.6 % |
| Lekeitio | 17 | 15 | 2 | 88.2 % | 0.3 % → 0.3 % |
| Irulegi | 2 | 1 | 1 | 50.0 % | 0.0 % → 0.0 % |
| Zarautz | 280 | 279 | 1 | 99.6 % | 4.3 % → 5.6 % |

### Cambios radicales de peso

Municipios con ≥10 releases en A que conservan menos de la mitad en B:

- **Bilbo**: 2469 → 970 (39.3 %)

Municipios que desaparecen del todo en B: 0

### ¿Concentraciones que vienen sobre todo de una cuenta multiartista?

Municipios (≥20 releases en A) donde una sola cuenta multiartista aporta ≥25 % de sus releases:

| Municipio | Releases A | Cuenta | Releases de esa cuenta | % | Artistas distintos en la cuenta |
|---|---:|---|---:|---:|---:|
| Santurtzi | 75 | `muertematarrecords` | 40 | 53.3 % | 35 |
| Irun | 113 | `petruskarecords` | 49 | 43.4 % | 2 |
| Andoain | 33 | `camilomateo` | 14 | 42.4 % | 6 |
| Portugalete | 41 | `goxoa` | 15 | 36.6 % | 7 |
| Zarautz | 280 | `zaratazarautz` | 98 | 35.0 % | 95 |
| Santurtzi | 75 | `bangrecords` | 20 | 26.7 % | 18 |
