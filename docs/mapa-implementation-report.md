# Informe de implementación — sección MAPA

*19 sep 2026 · rama local `feat/mapa` sobre `main` (31ac507) · **sin push ni PR** hasta nueva orden.*

## Resumen

La ubicación de Bandcamp ya no se pierde: vive como **evidencia trazable fuera del canónico** (`data/locations/`), se normaliza contra un registro controlado de municipios y se resuelve por release conservando de dónde sale cada ubicación. Encima de esos datos hay una nueva puerta **MAPA** (`#/mapa`) que interroga el mismo archivo desde los lugares, con los mismos filtros que ARCHIVO.

**6.522 de 7.568 releases (86,2 %) aparecen en el mapa**, repartidas en 104 municipios. 6.439 (85,1 %) sin ninguna inferencia. Las 1.046 restantes se cuentan en la interfaz, no se esconden.

## Commits (en orden de fase)

| Commit | Fase | Contenido |
|---|---|---|
| `1cfc3e2` | 0 | `docs/mapa-audit.md`: auditoría del repo y del mapa vecino |
| `7f55e5a` | 1 | Observaciones fuera del canónico, `ingest`/`check`, gancho en `discover_tags.py`, workflow Tests |
| `424d1bb` | 2 | `recover` desde todo el histórico git local + informe |
| `c08a0f5` | 3–6 (código) | Scraper por cuenta, nomenclátor Wikidata, registro de lugares, normalización, resolución, auditoría, consultas, índice |
| `601764f` | 3–6 (datos) | Scrapeo de 630 cuentas, reglas revisadas, dataset y auditoría |
| `0a0e828` | 7–17 | Puerta MAPA, filtros compartidos, paneles, URLs, tests JS, documentación |
| `83af86f` | 19 | Correcciones de la revisión final (workflow, determinismo, derivados) |

## Archivos

**Nuevos**
- `scripts/locations.py` (CLI) y `scripts/locations_lib.py` (funciones puras).
- `tests/test_locations.py`: 24 tests con `unittest`.
- `data/locations/`: `observations/` (6 ficheros), `cache/` (nomenclátor + caché del scraper), `places.json`, `rules.json`, `manual.json`, `normalized.json`, `resolutions.json`, `map_index.json`, `reports/`. En total 6,3 MB; lo más pesado es `resolutions.json` (3,3 MB).
- `app/src/pages/Mapa.jsx`, `Mapa.css`, `app/src/utils/mapa.js`, `mapa.test.js` (8 tests), `app/src/hooks/useMapIndex.js`.
- `.github/workflows/tests.yml`.
- `docs/mapa-audit.md`, `docs/mapa-data-audit.md` (generado), `docs/mapa.md` y este informe.

**Modificados**
- `scripts/discover_tags.py`: registra observaciones en cada checkpoint.
- `scripts/merge_candidates_2026_07.py`: solo una nota en el docstring, no se vuelve a ejecutar.
- `.github/workflows/discover-tags.yml`: el PR mensual incluye su fichero de observaciones.
- `app/src/utils/busqueda.js`: `filtra()` gana `desde`/`hasta`, compartido por las dos vistas.
- `app/src/hooks/useHashRoute.js`: ruta `#/mapa[/:lugar]` y `desde`/`hasta` en `hashArchivo`.
- `app/src/pages/Archivo.jsx`: acepta `desde`/`hasta` con su chip.
- `app/src/components/Puertas.{jsx,css}`: tercera puerta y padding en móvil.
- `app/src/App.jsx`, `app/package.json` (`npm test`).
- `README.md`: MAPA, pipeline de ubicaciones y estructura. También corrige la sección de arquitectura, que seguía describiendo el sitio vanilla en la raíz y el cutover F5 como pendiente, cuando `deploy.yml` ya lo tenía hecho.

**Sin tocar:** el canónico `data/bandcamp_bilbaotags_clean.json` (9 campos), `deploy.yml` y el resto de páginas.

## Decisiones técnicas

1. **Evidencia → normalización → resolución → índice**, en ficheros separados:
   - La observación guarda el texto crudo, la fuente, la cuenta, la URL, la fecha y la procedencia. `value: null` es un hueco explícito.
   - Un fichero de observaciones por lote: los PR mensuales añaden el suyo sin conflictos de merge.
2. **La ubicación de Bandcamp es de la cuenta que publica.** Por eso el scraper visita **una ficha por cuenta**: 638 peticiones en vez de 1.414. El resto de releases de la cuenta quedan como `same_account`, un tipo propio y no confundido con `direct`.
3. **Los sellos no contaminan a los artistas.** Una cuenta del índice de sellos nunca propaga su ubicación al artista. `artist_inferred` exige unanimidad entre las cuentas propias del artista.
4. **Los tags nunca ubican por defecto.** Son `tag_hint`, se activan con un control explícito, y si apuntan a otro municipio se registran como contradicción.
5. **Registro de lugares desde Wikidata**, con QID y código INE/INSEE trazables:
   - Iparralde = las 158 comunas de la Communauté d'agglomération du Pays Basque.
   - Los nombres oficiales bilingües se generan (eu+es).
   - Los núcleos y municipios disueltos son alias del vigente.
   - Un nombre oficial nunca se pierde por un núcleo homónimo, y los homónimos entre países se desempatan por país (Getaria / Guéthary).
6. **Categorías explícitas por texto crudo**, con reglas en `rules.json`:
   - Incluye los códigos ISO 3166-2 del selector de Bandcamp: `PV`, `NC` (Navarra), `CT`.
   - Las colisiones (`Pamplona, Colombia`, `Navarre, Florida`) son `unexpected`, nunca aceptadas.
7. **Mapa sin cartografía comercial.** Es una retícula de celdas de ~5 km generada en build desde los núcleos del nomenclátor, así que es la silueta del ámbito de datos. Lo que se reutiliza del mapa de escenas vecino:
   - marcadores cuadrados con tamaño = cantidad documentada;
   - zoom por territorio con marcadores a tamaño de pantalla constante;
   - blancos táctiles de 26 px;
   - atenuación del resto al seleccionar.

   Lo que **no** se reutiliza: su regla «opacidad = corroboración». Aquí la procedencia va en el relleno (sólido, rayado, punteado, hueco) y en los controles de UBICACIONES.
8. **Escala absoluta.** El tamaño se calcula contra el máximo sin filtros, así un cuadrado significa lo mismo con cualquier filtro. Un «fantasma» muestra el total sin filtros.
9. **Misma lógica en Python y JS.** El lift y sus umbrales (3 en el lugar, 10 en el archivo, sin topónimos) son idénticos en `locations_lib.py` y `mapa.js`: comprobado con Zarautz, ×26,3 en los dos.
10. **Rendimiento.**
    - El índice (125 KB) se precalcula en build y referencia por id, sin duplicar discos. Solo se descarga al abrir MAPA.
    - `preparaGeo` se expande una vez por sesión y las consultas se cachean por clave de filtros (LRU de 40).
    - Filtrar 7.568 releases es lineal y sin recomputar al abrir un municipio.
11. **Derivados deterministas y comprobados en CI.** Salen idénticos con distintos `PYTHONHASHSEED`. Solo dependen del canónico y de las reglas, así que un PR de candidatos no los desactualiza; se regeneran al fusionar.

## Métricas del dataset

| | Releases | % |
|---|---:|---:|
| direct | 4.953 | 65,4 |
| same_account | 1.486 | 19,6 |
| artist_inferred | 83 | 1,1 |
| manual | 0 | 0 |
| region_only | 558 | 7,4 |
| outside_scope | 286 | 3,8 |
| tag_hint (oculto por defecto) | 36 | 0,5 |
| unresolved | 166 | 2,2 |

- **Por territorio:** Bizkaia 3.003, Gipuzkoa 1.894, Nafarroa 961, Araba 586, Iparralde 78.
- **Región sin municipio:** «Euskal Herria / Basque Country / PV» 421, France 73, Spain 37, Nafarroa 13, comarcas 10, Nouvelle-Aquitaine 4.
- **Sin resolver (166):** 141 porque Bandcamp no da ubicación, 22 con evidencia descartada y 3 sin evidencia.
- **Contradicciones:** 33 releases, todas por tags que apuntan a otro municipio.
- **Cuentas con varios artistas** (probables sellos): sitúan 2.026 releases. En Bilbo son 638 de 1.725.
- **Recuperación sin red (fase 2):** 5.181 releases con ubicación directa, 0 contradicciones entre versiones históricas.
- **Scrapeo (fase 3):** 630 cuentas; 621 con ubicación, 10 sin ella, 8 fichas retiradas que se resolvieron por la portada de la cuenta.

## Verificación hecha

- `python3 -m unittest discover tests`: 24 OK. `npm test`: 8 OK. `npm run lint`: limpio. `npm run build`: OK.
- **Simulación del CI sobre un worktree limpio:** tests, guardia `check`, `locations.py all` + `git diff --exit-code` sin cambios, `npm ci`, tests, lint y build.
- **Simulación del deploy:** `rsync` + `gen-stubs.mjs` → 7.568 stubs y `map_index-*.json` en assets. Sitio servido en local: MAPA, EXPLORAR, ARCHIVO y FICHA sin errores de consola. El único ruido es el beacon de Cloudflare, bloqueado por CORS en localhost, que ya existía.
- **Guardia con merges simulados:**
  - Llegada de `candidates_2026-09.json` (PR #66): pasa.
  - Un fichero nuevo sin ingerir: falla.
  - Tras `ingest`: pasa.
- **Navegador:**
  - Rutas directas `#/mapa`, `#/mapa/zarautz`, `?tag=noise&desde=2005&hasta=2012` y `?territorio=Gipuzkoa`.
  - Clic en marcador → URL; atrás y adelante; recarga.
  - Recorrido año a año sin llenar el historial.
  - Mini-ficha con reproductor.
  - «VER EN ARCHIVO» conserva los filtros (tag + años → 21 releases en ARCHIVO).
  - Móvil de 375 px sin desbordamiento horizontal.
- **Cifras de la interfaz = auditoría:** 6.522 localizadas; 1.046 sin municipio = 558 + 286 + 166 + 36; `noise` 314 → 265 localizadas en 11 municipios, igual en la UI que en `query`.

## Limitaciones restantes

- **Es ubicación actual de la cuenta, no del artista ni de su época.** Está documentado en la interfaz (pie, aviso de AÑOS, nota de cuentas con varios artistas) y en `docs/mapa.md`.
- **El índice de sellos es heurístico.** Cuentas con ≥2 artistas incluye splits y recopilatorios de grupos. Por eso la interfaz dice «probables sellos».
- **Sin uso todavía:** el scraper guarda `publisher_differs_from_artist` (JSON-LD `byArtist` ≠ `publisher`), pero la resolución aún no lo usa.
- **El lift con pocas releases es inestable** (×100 con 3 discos). Los umbrales lo limitan; la nota del panel lo advierte.
- **Iparralde:** solo 78 releases. El catálogo nació en Bilbao y la oleada 2 de Iparralde sigue en cola.
- **La FICHA de un disco no muestra aún su ubicación ni su procedencia.** Está en `resolutions.json` y en el panel del municipio (código D/C/A/T por release).
- **`resolutions.json` pesa 3,3 MB** en el repo. No lo carga la app: es para trazabilidad.

## Pendiente de revisión manual

Detalle completo en `data/locations/reports/review.md`.
- **`unexpected` (27 releases):** `Navarre, Florida` (13, una cuenta), `Pamplona, Colombia` (6), `Irun, Nigeria` (5), `Guernica, Argentina`, `San Sebastián, Chile`, `Bayonne, New Jersey`. Algunas pueden ser errores del selector de Bandcamp de grupos vascos; se deciden en `manual.json` por cuenta.
- **`invalid`:** `Afghanistan` (24 releases, sello Mendeku Diskak). ¿Asignarle Iruñea por cuenta? Hace falta confirmarlo.
- **`region_only` (558):** sobre todo cuentas con `Basque Country`/`PV`. Son candidatas a decisión por cuenta si se conoce el municipio.
- **`outside_scope` (286):** la lista incluye países sueltos que pueden no ser literales (Thailand, Western Sahara, Norfolk Island, Kiribati…).
- **Contradicciones por tag (33):** en `resolutions.json`, campo `conflicts`.

## Al fusionar los PR de candidatos #65/#66

Sus observaciones ya están en `data/locations/observations/candidates_2026-0{8,9}.json`. Tras su script de merge al canónico hay que ejecutar `python3 scripts/locations.py all` y commitear. Si no se hace, el workflow Tests lo marca («derivados desactualizados»).

## Propuestas para una fase futura

1. **Ubicación y procedencia en la FICHA** de cada disco, con enlace «ver en el mapa».
2. **Faceta `lugar` en ARCHIVO**, para cerrar el círculo archivo ↔ mapa con los mismos parámetros.
3. **Usar `byArtist`/`publisher`** en la resolución y **scrapear las cuentas propias de artistas** publicados por sellos, para sustituir ubicaciones de sello por la del grupo cuando exista.
4. **Comarcas** (`places.json → comarca` está reservado) y un nivel de zoom intermedio.
5. **Workflow periódico de `scrape`** para cuentas nuevas tras cada merge, con el mismo presupuesto.
6. **Mini-herramienta de revisión** que genere entradas de `manual.json` desde `review.md`.
