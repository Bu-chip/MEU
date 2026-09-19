# Auditoría previa — sección MAPA (fase 0)

*19 sep 2026 · rama `feat/mapa` · solo lectura: esta fase no cambia código ni datos.*

## 1. Estructura relevante del repo

| Pieza | Dónde | Notas |
|---|---|---|
| Catálogo canónico | `data/bandcamp_bilbaotags_clean.json` | `{albums, artists, tags, years}`; 7.568 álbumes con esquema estricto de **9 campos** (`id, artist, title, genre, year, tags, url, cover_url, album_id`). `id` = clave estable de la app (no contiguo); `album_id` = id de Bandcamp (99,8 % presente). |
| Validación/normalización | `scripts/pipeline.py` | `validate()` impone el esquema; `serialize()` fija el formato. Todo proceso que escriba el canónico pasa por aquí. |
| Descubrimiento | `scripts/discover_tags.py` + `.github/workflows/discover-tags.yml` | API `discover_web` → candidatos `data/candidates_YYYY-MM.json` = esquema canónico sin `id` **+ `band_location`, `source_tags`, `discovered_at`**. El workflow guarda estado en la rama `discovery-state` y abre un PR mensual `candidates/YYYY-MM`. |
| Merge de candidatos | `scripts/merge_candidates_2026_07.py` | Script *ad hoc* por oleada (no hay merge genérico). Construye la ficha con solo los 9 campos. |
| Tags | `pipeline.py` (`TAG_RENAMES`, `TAG_SPLITS`) en datos; `app/src/data/tagAliases.js` solo búsqueda | Los tags de lugar (`bilbao`, `donostia`, `vitoria gasteiz`…) conviven con los de género en `tags`. |
| Índice de sellos | `scripts/labels_index.py` → `data/derived/labels.json` | Cuenta de Bandcamp (subdominio) con ≥2 artistas o léxico de sello. Útil para saber cuándo la ubicación es la **del sello**. |
| Router | `app/src/hooks/useHashRoute.js` | Hash router artesanal: `#/`, `#/archivo?q&genero&anio&tag&artista`, `#/disco/:id`, `#/sobre`, `#/entrar`, `#/coleccion`. `navegar()` (con historial) y `reemplazar()` (sin historial). |
| Filtros | `app/src/utils/busqueda.js` (`filtra`, `ordena`, alias) + `app/src/utils/indices.js` (índices en memoria cacheados por WeakMap) | ARCHIVO: artista, género, año (uno solo), tag, texto libre con alias. |
| Navegación | `app/src/components/Puertas.jsx` | Dos puertas: EXPLORAR · ARCHIVO (+ marca de usuario). |
| Páginas | `app/src/pages/{Explorar,Archivo,Ficha,…}.jsx` | EXPLORAR es un muro de descubrimiento, ARCHIVO el índice/registro. |
| Carga de datos | `app/src/hooks/useArchive.js` | El JSON canónico se importa `?url` (asset hasheado) y se cachea a nivel de módulo. |
| Deploy | `.github/workflows/deploy.yml` | `npm ci && npm run build` en `app/`, `gen-stubs.mjs`, push forzado a `gh-pages`, CNAME `mapa.queimadacircuitrecords.com`. |
| Tests | — | **No hay infraestructura de tests** (ni Python ni JS). Solo `eslint`. |

## 2. Datos de ubicación que existen hoy

1. **`band_location` en candidatos.** Viene de la API `discover_web` (texto libre de Bandcamp: `"Zarautz, Spain"`). Es la ubicación de la **cuenta que publica** (grupo o sello), la que tiene *hoy*, sin fecha.
   - `data/candidates_2026-07.json` (en `main`): 5.483 candidatos; 5.181 releases del canónico casan por `album_id`.
   - Ramas `candidates/2026-08` (29) y `candidates/2026-09` (76): candidatos aún no fusionados.
   - Rama `discovery-state`: `discovery_state.json` con 45 `pending_fichas` (parciales con `band_location`).
2. **Tags geográficos** en el canónico: 4.295 releases llevan alguno (`vitoria gasteiz` 1.070, `iruña` 948, `donostia` 896…). Son **etiquetas del artista**, no residencia.
3. **Página del álbum**: `<span class="location secondaryText">Bilbao, Spain</span>` (verificado). En el JSON-LD, `byArtist.@id` vs `publisher.@id` permite saber si publica la cuenta del artista o otra (sello).
4. **Nada** de ubicación en el canónico ni en la app.

## 3. Dónde se pierde

`scripts/merge_candidates_2026_07.py`, docstring punto 6 y `build_ficha()`: *«solo los 9 campos del esquema (band_location/source_tags/discovered_at se descartan)»*. El descubrimiento sí conserva el dato; el merge lo tira. El catálogo original (~2.390 releases anteriores a julio, scrapeado desde `/tag/bilbao`) nunca tuvo ubicación.

Riesgo inmediato: los PR abiertos #65 y #66 perderían sus ubicaciones igual en cuanto se escriba su script de merge.

## 4. Qué habrá que tocar

- **Nuevo**: `data/locations/` (evidencia → lugares → resolución → índice del mapa) y un CLI `scripts/locations.py` con subcomandos reproducibles.
- `scripts/discover_tags.py`: registrar observaciones al producir candidatos.
- `.github/workflows/discover-tags.yml`: añadir `data/locations/observations.json` a los commits de estado y de PR.
- `scripts/merge_candidates_2026_07.py`: nota de que las ubicaciones viajan fuera del canónico (no se re-ejecuta).
- App: `useHashRoute.js` (ruta `#/mapa`), `Puertas.jsx` (tercera puerta), `busqueda.js` (rango de años compartido), nueva página `Mapa.jsx` + utilidades puras testeables.
- Tests: `unittest` (stdlib) para Python y `node --test` para JS, sin dependencias nuevas.

## 5. Proyecto vecino: `~/Dev/archivo-historia-de-la-musica-electrónica`

Vista **MAPA DE ESCENAS** en `maqueta.html` (+ `ESPECIFICACION-UI.md`); la app React (`archivo-electronica/web`) aún no la implementa.

- **Representación**: SVG; el mundo es una **retícula de puntos cuadrados** generada desde cajas lon/lat (72×28 celdas de 5°), sin mapas vectoriales ni ficheros externos. Proyección equirectangular simple.
- **Escenas**: marcador cuadrado en su coordenada, tamaño = cantidad documentada (explícitamente *no* importancia). Rótulos visibles según haya sitio.
- **Navegación**: seis territorios con rótulo; clic amplía cambiando el `viewBox`; los marcadores se dividen por el factor de escala para no crecer; `← MUNDO` para volver. Blancos táctiles invisibles de 26 px.
- **Selección**: panel anclado al punto con líneas de vida; el resto baja al 13 %.
- **Temporal**: AÑO A AÑO con tira de años y `▶ RECORRER`.
- **Regla central**: opacidad = corroboración (1/2/3+ fuentes).
- **Sistema visual**: papel/tinta/lima, Big Shoulders + IBM Plex Mono, radio 0, sin sombras. Es el mismo sistema que el MEU (`app/src/styles/tokens.css`).

**Qué se reutiliza**: la retícula de puntos cuadrados, marcadores cuadrados con tamaño = cantidad documentada, `viewBox` + escala compensada, blancos táctiles, «el resto se atenúa» al seleccionar, el hueco declarado y las URLs por estado.

**Qué NO se copia**:
- La opacidad como fiabilidad: aquí la opacidad baja se leería como «pocos discos». La procedencia va en borde/patrón + controles explícitos.
- Las cajas lon/lat: a escala de Euskal Herria son demasiado burdas. La silueta se generará desde los propios núcleos de población del nomenclátor, así que la retícula representa exactamente el ámbito de datos.
- El código de manipulación de `innerHTML`: se reescribe en React.

## 6. Riesgos

1. **La ubicación de Bandcamp es de la cuenta, no del artista.** Un disco publicado por un sello lleva la ciudad del sello. Hay que marcarlo (índice de sellos + `byArtist`≠`publisher`) y no propagarlo al artista.
2. **Es ubicación actual y sin fecha.** Filtrar por año es válido, pero no es una reconstrucción de residencias.
3. **Texto libre sucio**: 216 variantes, grafías múltiples (Donostia ×5), regiones (`PV`, `Basque Country`), colisiones (`Irun, Nigeria`, `Pamplona, Colombia`, `Navarre, Florida`) y bromas (`Afghanistan`).
4. **Merge por `album_id`**: el merge de julio hizo que algunas fichas antiguas adoptaran el `album_id` del candidato. Casar por `album_id` y, de respaldo, por URL normalizada.
5. **Sin tests**: toda la lógica nueva va en módulos puros para poder testearla.
6. **Coordenadas**: no se inventan. Salen de Wikidata (P625) con QID trazable, cacheadas en el repo para que la regeneración sea offline.
7. **Peso**: el canónico pesa 4,6 MB. El índice del mapa debe referenciar por `id`, sin duplicar discos.
