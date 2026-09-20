# MAPA — el archivo desde sus lugares

`#/mapa` es la segunda puerta al mismo archivo: **ARCHIVO** parte de releases, artistas y tags, y **MAPA** parte de lugares. Las dos vistas usan el mismo canónico y la misma función de filtrado (`app/src/utils/busqueda.js → filtra`).

## 1. De dónde vienen las ubicaciones

Solo hay una fuente automática: **Bandcamp**. Y lo que Bandcamp da es la ubicación de la **cuenta que publica** (grupo o sello), la actual y sin fecha.

| Fuente | Qué es | Dónde queda |
|---|---|---|
| `bandcamp_discover` | Campo `band_location` de la API `discover_web`, leído por `scripts/discover_tags.py` | `data/locations/observations/candidates_YYYY-MM.json` |
| `bandcamp_page` | `<span class="location">` de la ficha de un disco (o de la portada de la cuenta si sus discos ya no existen), leído por `scripts/locations.py scrape` | `data/locations/observations/bandcamp_pages.json` (+ caché en `data/locations/cache/bandcamp_pages.json`) |
| manual | Decisión humana | `data/locations/manual.json` |
| tag | Un tag del disco que coincide exactamente con un topónimo | Se calcula en la resolución como `tag_hint`; **nunca** se usa como ubicación por defecto |

Las **observaciones** guardan el texto crudo (`"Zarautz, Spain"`) sin normalizar, con fuente, cuenta, URL, fecha y procedencia. `value: null` significa «se consultó y no había ubicación». Es un hueco explícito, no falta de dato.

Las coordenadas vienen de **Wikidata**: P625 del municipio, identificado por su código INE (P772) o, para Iparralde, por pertenecer a la Communauté d'agglomération du Pays Basque. Están cacheadas en `data/locations/cache/gazetteer_wikidata.json`. Son un **punto representativo para dibujar**, no la ubicación física de nadie.

## 2. Capas de datos

```
data/locations/
  observations/*.json        1. evidencia cruda, un fichero por lote (sin conflictos entre PR)
  cache/gazetteer_wikidata.json   nomenclátor (municipios, núcleos, municipios disueltos)
  cache/bandcamp_pages.json       caché del scraper (ok / error / gone, reanudable)
  places.json                2. registro controlado de 684 municipios (id, nombre, alias, lat/lon, territorio, país, comarca reservada)
  rules.json                 2. reglas controladas: regiones, lugares fuera de ámbito, alias extra, decisiones por valor
  normalized.json            2. cada texto crudo → categoría (+ municipio) y cuántas releases lo usan
  manual.json                3. decisiones humanas por release o por cuenta
  resolutions.json           3. resolución por release del canónico con evidencia y contradicciones
  map_index.json             índice compacto para la app (~125 KB, referencias por id)
  reports/                   recover.md/json, review.md, audit.json
```

El canónico (`data/bandcamp_bilbaotags_clean.json`) **no se toca**: sigue con sus 9 campos.

### Categorías de normalización (por texto crudo)

| Categoría | Significa | Ejemplos |
|---|---|---|
| `resolved` | Municipio del registro, en su país | `Bilbao, Spain`, `Donostia San Sebastian, Spain`, `Cambo Les Bains, France` |
| `region_only` | Solo región, comarca o país: **nunca** se convierte en municipio | `Spain`, `France`, `Basque Country`, `PV, Spain`, `NC, Spain`, `Navarra, Spain`, `Enkarterri, Spain` |
| `ambiguous` | Podría ser varias cosas | `Getaria` sin país (Gipuzkoa o Guéthary), `AL, Spain` |
| `outside_scope` | Lugar real fuera de Euskal Herria (se conserva, no se dibuja) | `Madrid, Spain`, `Berlin, Germany` |
| `unexpected` | Topónimo del ámbito con un país incoherente | `Pamplona, Colombia`, `Irun, Nigeria`, `Navarre, Florida` |
| `invalid` | Valor no geográfico o improbable, por **regla manual** con nota | `Afghanistan` (sello navarro Mendeku Diskak) |
| `unresolved` | Sin regla: pendiente de revisar | — |

## 3. Qué significa cada `resolution_type`

Cada release del canónico tiene exactamente un tipo. Si hay varias evidencias, se elige por este orden y la que apunta a **otro** municipio queda en `conflicts`:

| Tipo | Significa | Procedencia en la app | ¿Sale en el mapa? |
|---|---|---|---|
| `manual` | Decisión humana (`manual.json`) | `d` directas | Sí |
| `direct` | Bandcamp, observado en **esta** release | `d` directas | Sí |
| `same_account` | Bandcamp, observado en **otra release de la misma cuenta**. En Bandcamp la ubicación es de la cuenta, así que es el mismo dato | `c` si la cuenta es de un solo artista; `m` si es una cuenta con varios artistas | `c` sí; `m` no (activable) |
| `artist_inferred` | Otras releases del **mismo artista** (clave `fold`) en cuentas que **no son sello**, todas en el mismo municipio. Si discrepan, no se infiere y queda `artist_disagreement` | `a` | Sí (desactivable) |
| `region_only` | Solo región o país | — | No: se cuenta |
| `outside_scope` | Fuera de Euskal Herria | — | No: se cuenta |
| `tag_hint` | Sin evidencia de Bandcamp; un único tag geográfico | `t` | No (activable) |
| `unresolved` | Nada útil, o evidencia descartada (`rejected_values`) | — | No: se cuenta |

### Qué se dibuja por defecto: el «escenario D»

La resolución **no cambia** según lo que se dibuje: `resolutions.json` y la auditoría son siempre las mismas. Lo que cambia es qué entra en el mapa.

Por defecto entran `d + c + a` (**5.904 releases, 78 % del catálogo, 104 municipios**) y quedan fuera `m` (misma cuenta, pero con varios artistas) y `t` (pistas de tag). El motivo está medido en `data/locations/reports/multiartist-audit.md`:

- Incluirlo todo (escenario A) daba 6.522, pero 618 de esas ubicaciones venían de cuentas con varios artistas, casi todas en Bilbo (612): eran la ciudad del sello, no la del grupo.
- Quedarse solo con las directas (escenario B) daba 4.953, y hundía Bilbo de 2.440 a 941 por un artefacto del método: el scrapeo visitó **una ficha por cuenta**, así que el resto de releases de una cuenta de un solo artista quedaron como `same_account` siendo el mismo dato.
- El escenario D quita solo lo dudoso: Bilbo queda en 1.828.

Se activan en la propia página, en **Más filtros → Ubicaciones incluidas**, o por URL con `ubic` (por ejemplo `#/mapa?ubic=dcamt`). Al activarlas, el mapa dibuja con trazo discontinuo los municipios que **solo** tienen ese tipo de evidencia, y la línea de cobertura y el desplegable «Cobertura y metodología» actualizan sus cifras.

Otros campos de `resolutions.json`:
- `account_kind: label`: la cuenta está en el índice de sellos (`data/derived/labels.json`, heurístico: cuentas con varios artistas o léxico de sello). Su ubicación es **la de esa cuenta** y nunca se propaga a sus artistas.
- `tag_hints`: pistas de tag, siempre separadas.
- `checked_empty`: Bandcamp se consultó y no daba ubicación.
- `same_account_values`: resumen por valor de la evidencia de la cuenta.

## 4. Qué NO significa el mapa

- **No** es dónde vive o vivió nadie. Es la ubicación que Bandcamp da **hoy** a la cuenta que publica.
- **No** es una reconstrucción histórica. Filtrar 2005–2012 filtra *releases* publicadas esos años. El botón `▶ RECORRER` muestra «la distribución de las releases del archivo por año según las ubicaciones actualmente asociadas».
- **No** es precisión geográfica. El punto es el del municipio y la retícula de fondo (~5 km) es una silueta, no un catastro.
- **No** es un juicio sobre la escena. El tamaño es la cantidad **documentada en el archivo**, y el lift describe el archivo.
- Un disco publicado desde la cuenta de un sello aparece **en la ciudad del sello**. El panel del municipio indica cuántos vienen de cuentas con varios artistas.

Ojo con los códigos del selector de Bandcamp: `PV, Spain`, `NC, Spain` y `CT, Spain` son códigos ISO 3166-2 de comunidad autónoma (País Vasco, Navarra, Cataluña), no abreviaturas sueltas.

## 5. Regenerar los datos

```bash
# todo lo derivado, sin red (normaliza → resuelve → audita → índice del mapa)
python3 scripts/locations.py all

# tras un merge de candidatos (lo hace también el workflow mensual)
python3 scripts/locations.py ingest data/candidates_2026-10.json
python3 scripts/locations.py check        # falla si alguna ubicación se perdería

# reconstruir desde el histórico git local (idempotente)
python3 scripts/locations.py recover

# completar cuentas sin evidencia (red; ~1 petición/2 s, reanudable)
python3 scripts/locations.py scrape --dry-run
python3 scripts/locations.py scrape --budget 900

# refrescar el nomenclátor de Wikidata y el registro (red, ocasional)
python3 scripts/locations.py gazetteer
python3 scripts/locations.py places
```

Tests: `python3 -m unittest discover tests` (capa de datos) y `npm --prefix app test` (lógica del mapa). El workflow `Tests` los ejecuta en cada PR junto con la guardia `check`.

## 6. Añadir o corregir un municipio

- **Una grafía nueva de un municipio que ya existe** (`"Gernika"`): en `rules.json → place_overrides`, `{"gernika-lumo": {"aliases": ["Gernika"]}}`. Después, `places` + `all`.
- **Un barrio o núcleo** (`"Ereñotzu"` → Hernani): igual, como alias del municipio, con una `note`.
- **Un lugar fuera del ámbito** con país España/Francia (`"Logroño"`): añádelo a `rules.json → outside`.
- **Una región o comarca**: en `rules.json → regions`, con `level` y `territory`.
- **Un valor concreto que no hay que creerse** (`"Afghanistan"`): en `rules.json → values`, con `category` y una `note` que diga por qué y cuándo.
- **Una release o cuenta concreta**: en `manual.json → releases["<id>"]` o `accounts["<subdominio>"]`, con `{place, note, decided_at}` (o `place: null` + `category`). Manda sobre todo y queda como `manual`.
- **Coordenadas**: no se editan a mano. Salen de Wikidata. Si una está mal, se corrige en Wikidata y se vuelve a ejecutar `gazetteer`.

## 7. Revisar casos ambiguos

`data/locations/reports/review.md` lista cada texto crudo que no es `resolved`, con cuántas releases y cuentas lo usan y por qué quedó así, y al final todos los resueltos agrupados por municipio para revisarlos de un vistazo. `docs/mapa-data-audit.md` resume los tipos de resolución, las contradicciones y los valores descartados.

## 8. La página

La tarea de `#/mapa` es explorar el archivo por lugares, así que el mapa domina y el resto aparece por capas:

- **Cabecera compacta** (solo en esta vista) y las tres puertas EXPLORAR · ARCHIVO · MAPA.
- **Una línea de filtros**: búsqueda, `Género` (con el campo de tag), `Territorio`, `Años` (con el recorrido año a año) y `Más filtros` (procedencias). Debajo, los **chips** de lo que esté filtrando.
- **Una línea de cobertura**: `N releases localizadas · N municipios`, con «Cobertura y metodología →», que despliega el desglose completo: qué se dibuja, qué queda excluido ahora (con enlace para incluirlo) y qué no tiene municipio.
- **Mapa (≈65 %) + panel de contexto (≈35 %)**, ambos del alto de la ventana: entran sin scroll.
- **Rótulos por densidad**: en la vista general solo las capitales y los municipios más densos que quepan (7); al ampliar a un territorio, hasta 18. Lo seleccionado y lo apuntado se rotulan siempre. Los territorios son orientación de fondo.
- **Panel de municipio**: nombre, territorio, cifras, 6 tags y 4 releases. El resto (Artistas, Releases, Sellos y cuentas, Estadísticas, Procedencia) vive en secciones plegadas.
- **El lima** solo marca selección y filtro activo.

### Móvil (≤ 760 px): modo propio, no la versión encogida

- **Cabecera en una línea** y filtros como fila de botones deslizable: `Buscar`, `Género`, `Territorio`, `Años`, `Más filtros`. La búsqueda también es un desplegable, para no comerse una fila entera.
- **Mapa acotado** (unos 46 vh, con tope de 52 vh) que sirve para orientar y seleccionar: **se desplaza con un dedo, se acerca con dos** y tiene botones `+`, `−` y `⟲` (vuelve a la vista completa). El municipio seleccionado lleva cuadrado lima y un anillo, para localizarlo de un vistazo.
- **Rótulos mínimos**: en la vista general solo Bilbo, Donostia, Gasteiz, Iruñea y Baiona; al acercar o entrar en un territorio aparecen más (hasta 14). Los blancos táctiles son de 34 px.
- **Hoja inferior** con tres estados: *asomada* (una línea que resume qué hay debajo), *media* (se abre sola al tocar un municipio, con el mapa aún visible) y *expandida*. Se arrastra o se toca el tirador; en expandida, tocarlo vuelve a plegar.
- **Modo `Mapa | Lista`**: el mismo ranking de municipios con los filtros activos, para no depender de tocar cuadrados pequeños.
- **«Cómo leer el mapa»** abre la cobertura y la metodología como capa, sin empujar el mapa.

## 9. Cómo se cruzan mapa y tags

- Los filtros son los de ARCHIVO: texto (con alias de tags), género, tag, artista y años (`desde`/`hasta`, compartidos con ARCHIVO). El mapa añade territorio y procedencia.
- Con un **tag** activo, cada municipio muestra solo sus releases con ese tag. El cuadro fantasma indica su total sin filtros, y el panel ordena los municipios por releases con el tag y su **lift**.
- En un **municipio**, «sobrerrepresentados» compara con el archivo entero: `lift = (releases del lugar con el tag / releases del lugar) ÷ (releases del archivo con el tag / releases del archivo)`. Exige al menos 3 releases en el lugar y 10 en el archivo, y excluye los tags que son topónimos. Es la misma métrica en `scripts/locations_lib.py` y `app/src/utils/mapa.js`.
- Consultas por terminal: `python3 scripts/locations.py query --place zarautz` y `--tag noise`.

## URLs

```
#/mapa
#/mapa/zarautz
#/mapa?tag=noise
#/mapa?tag=noise&desde=2005&hasta=2012     (también se aceptan from/to)
#/mapa?territorio=Gipuzkoa&genero=electronic
#/mapa?ubic=dcamt                          (d directas · c misma cuenta (un artista) ·
                                            a por artista · m cuenta multiartista · t pista de tag;
                                            por defecto dca)
```

Recargar conserva la vista, y atrás/adelante recorren los cambios. Esc sube un nivel: municipio → territorio → Euskal Herria.
