# Recuperación de ubicaciones (fase 2)

*Generado por `python3 scripts/locations.py recover`. No editar a mano.*

Fuentes: ficheros `data/candidates_*.json` del árbol y todas sus versiones en el histórico git local (ramas locales y remote-tracking, incluidas `candidates/2026-08`, `candidates/2026-09` y `discovery-state`). Los valores se guardan **sin normalizar**.

| Métrica | Valor |
|---|---:|
| Releases del canónico | 7568 |
| Con ubicación directa (Bandcamp, esta release) | 5181 |
| Consultadas sin ubicación (valor vacío) | 124 |
| Sin ninguna información | 2263 |
| Artistas (clave fold) con alguna ubicación | 2466 / 3422 |
| Valores únicos (releases del canónico) | 216 |
| Valores únicos (todas las observaciones) | 240 |
| Releases con valores contradictorios | 0 |
| Cuentas con más de un valor | 0 |
| Claves de release con observación (incl. candidatos pendientes) | 5605 |

## Fuentes leídas

| Procedencia | Fichero de observaciones | Obs. | Con valor |
|---|---|---:|---:|
| `data/candidates_2026-07.json` | `candidates_2026-07.json` | 5483 | 5352 |
| `git:7cff6af83c:data/candidates_2026-07.json` | `candidates_2026-07.json` | 5483 | 5352 |
| `git:7cff6af83c:data/candidates_2026-09.json` | `candidates_2026-09.json` | 76 | 70 |
| `git:0b54208369:data/candidates_2026-08.json` | `candidates_2026-08.json` | 29 | 28 |
| `git:0b54208369:data/discovery_state.json` | `discovery_state_pending.json` | 45 | 1 |
| `git:7f9e7f9309:data/discovery_state.json` | `discovery_state_pending.json` | 45 | 1 |
| `git:06683c45b9:data/discovery_state.json` | `discovery_state_pending.json` | 45 | 1 |
| `git:98f6b3ea7e:data/discovery_state.json` | `discovery_state_pending.json` | 45 | 1 |
| `git:0fbb0741fd:data/discovery_state.json` | `discovery_state_pending.json` | 45 | 1 |
| `git:46cfbfe284:data/candidates_2026-07.json` | `candidates_2026-07.json` | 4954 | 4827 |
| `git:099099e4ac:data/discovery_state.json` | `discovery_state_pending.json` | 574 | 526 |
| `git:cec6971c02:data/candidates_2026-07.json` | `candidates_2026-07.json` | 4206 | 4085 |
| `git:dce291f90c:data/discovery_state.json` | `discovery_state_pending.json` | 1322 | 1268 |
| `git:a38f414b51:data/candidates_2026-07.json` | `candidates_2026-07.json` | 3448 | 3340 |
| `git:ff8d81bdb6:data/discovery_state.json` | `discovery_state_pending.json` | 2080 | 2013 |
| `git:86eca2fa4d:data/candidates_2026-07.json` | `candidates_2026-07.json` | 2680 | 2577 |
| `git:faa979a0be:data/discovery_state.json` | `discovery_state_pending.json` | 2848 | 2776 |
| `git:af8e83acee:data/candidates_2026-07.json` | `candidates_2026-07.json` | 1905 | 1810 |
| `git:e01962a51f:data/discovery_state.json` | `discovery_state_pending.json` | 3622 | 3542 |
| `git:a770d03526:data/candidates_2026-07.json` | `candidates_2026-07.json` | 1123 | 1035 |
| `git:6ac84e3af6:data/discovery_state.json` | `discovery_state_pending.json` | 4404 | 4317 |
| `git:640106cace:data/candidates_2026-07.json` | `candidates_2026-07.json` | 332 | 317 |
| `git:e6f13fc802:data/discovery_state.json` | `discovery_state_pending.json` | 5195 | 5035 |
| `git:d7907c783c:data/candidates_smoke.json` | `candidates_smoke.json` | 12 | 12 |

## Releases con valores contradictorios

Ninguna.

## Cuentas con más de un valor

Ninguna.

## Valores más frecuentes (releases del canónico)

| Valor crudo | Releases |
|---|---:|
| Pamplona, Spain | 891 |
| Vitoria Gasteiz, Spain | 529 |
| Donostia San Sebastian, Spain | 474 |
| San Sebastián, Spain | 369 |
| Bilbao, Spain | 358 |
| Zarautz, Spain | 278 |
| PV, Spain | 181 |
| Basque Country, Spain | 117 |
| Irun, Spain | 107 |
| Getxo, Spain | 91 |
| Euskadi, Spain | 76 |
| France | 73 |
| Santurtzi, Spain | 73 |
| Donostia San Sebastián, Spain | 68 |
| Hondarribia, Spain | 59 |
| Errenteria, Spain | 58 |
| Barakaldo, Spain | 55 |
| Madrid, Spain | 50 |
| Arrasate, Spain | 48 |
| Leioa, Spain | 48 |
| Donostia / San Sebastián, Spain | 47 |
| Bermeo, Spain | 41 |
| Portugalete, Spain | 40 |
| Ondarroa, Spain | 39 |
| Oiartzun, Spain | 35 |
| Eibar, Spain | 34 |
| Tolosa, Spain | 34 |
| Andoain, Spain | 33 |
| Spain | 29 |
| Oñati, Spain | 29 |
| Hernani, Spain | 29 |
| Bilbo, Spain | 29 |
| Guernica, Spain | 28 |
| Afghanistan | 24 |
| Zumaia, Spain | 22 |
| Tudela, Spain | 22 |
| Laudio, Spain | 18 |
| Azpeitia, Spain | 18 |
| Donostia, Spain | 18 |
| Bergara, Spain | 16 |
