# Historia del MEU — Mapa Euskadi Underground

> **Qué es este documento.** Una crónica reconstruida del proyecto MEU a partir del
> histórico de conversaciones dentro de este Project. Cuenta cómo se construyó, qué
> decisiones se tomaron y por qué, y en qué estado quedó (jul 2026).
>
> **Método y fiabilidad.** Marco con `[FIRME]` lo que está anclado a un dato duro
> (nº de PR, recuento medido, decisión registrada) y con `[RECONSTRUCCIÓN]` lo que
> infiero del contexto (sobre todo fechas y detalles de la etapa pre-julio, donde los
> timestamps del histórico no coinciden con la fecha real del trabajo). La fuente de
> verdad viva del proyecto sigue siendo Notion ("MEU - Mapa Euskadi Underground") y el
> repo `Bu-chip/MEU`; esto es el relato, no el estado operativo.

---

## 0. El ecosistema donde nace

El MEU no aparece solo: es una de las tres piezas del universo **Queimada Circuit
Records (QCR)**, el sello y paraguas cultural de Miguel. Las otras dos:

- **Random Genre Explorer (RGE / genre-explorer)** — explorador de ~5.453 microgéneros
  congelados de EveryNoise, con preview de Deezer y cascada Last.fm→Deezer→iTunes.
  Vive en `genres.queimadacircuitrecords.com`. `[FIRME]`
- El propio sello QCR y su web, con una sección `04_LAB` pensada como escaparate de
  proyectos. `[FIRME]`

La relación entre RGE y MEU se formuló pronto como un paralelismo que se ha mantenido
como brújula: **el genre-explorer es el mapa del mundo; el MEU es la guía de casa.**
`[FIRME]` El RGE es colorista porque su dato lo es (cada género trae su color de
EveryNoise); el MEU sería casi monocromo porque su identidad es otra.

Detrás de todo hay un ángulo académico real, no postureo: Miguel es doctorando en
filosofía (sesgos antropocéntricos / marcos computacionales), y el MEU es también un
caso de estudio de esos sesgos. El congreso **KISMIF** (Oporto, cultura DIY y escenas
underground) quedó fichado como sitio donde presentarlo como ponencia. `[FIRME]`

---

## 1. Prehistoria: el BUE (Bilbao Underground Explorer) `[RECONSTRUCCIÓN de fechas]`

El MEU es la evolución de un proyecto anterior, el **BUE (Bilbao Underground
Explorer)**. Su génesis fue artesanal y es importante porque explica por qué el JSON es
sagrado:

- Miguel **copió a mano** todos los álbumes de la etiqueta `bilbao` de Bandcamp. `[FIRME]`
- Los **limpió con un script de Python** quedándose con álbum, artista y género
  principal → **~2.390 entradas**. Luego hizo una segunda vuelta para sacar más datos
  por artista (especialmente fechas). `[FIRME]`
- El CSV original y el script de transformación **nunca se versionaron**. Por eso, desde
  entonces, **el JSON es la única fuente de verdad** — no hay a qué volver. `[FIRME]`

La primera encarnación web del BUE se montó con **Google Antigravity**, con una estética
**terminal/Matrix (verde sobre negro)** y elementos interactivos en coral, desplegada en
GitHub Pages. En esa etapa se intentó por primera vez scrapear portadas de Bandcamp y
**se abandonó por los 403** (protección anti-bot). `[FIRME]` Ese fracaso dejó la lección
que luego resultó clave: los 403 vienen de las máquinas locales, no necesariamente de
los runners de GitHub.

**El giro conceptual (≈30 abril 2026).** Miguel decidió que el proyecto dejaba de ser
hobby: pasaba a ser **pieza candidata a curro vía financiación pública vasca** (Eremuak,
BBK, Diputación de Bizkaia, BilbaoArte, Etxepare) y cambiaba de escala — de Bilbao a toda
Euskadi. Ahí nace el nombre **Mapa Euskadi Underground (MEU)**. Planificó para mayo una
sesión de rediseño *conceptual* con una regla en negrita: nada de código ni diseño hasta
cerrar narrativa + financiación, "si se entra a código se contamina". Esa sesión quedó en
pausa meses (tesis, bolos, Cirkolepsia) hasta julio. `[FIRME]`

---

## 2. Julio 2026: la semana en que el MEU cobró vida

Casi todo el MEU actual se construyó en una ráfaga de sesiones entre el **5 y el 13 de
julio de 2026**. `[FIRME, por timestamps]` Lo narro por bloques temáticos, que además
fueron más o menos el orden real.

### 2.1 · Sesión conceptual: qué es el MEU (5 jul) `[FIRME]`

Se desbloqueó por fin la sesión pendiente desde mayo, y salió la definición que gobierna
todo lo demás:

> **El MEU es la guía personal de QCR a la música underground de Euskadi.**
> Auténtico primero; presentable ante instituciones como *consecuencia*, no al revés.

Decisión de fondo: **las convocatorias de financiación quedan aparcadas, no dirigiendo el
diseño.** Una web "hermana pequeña del explorer" vende peor a una institución que un
proyecto con voz propia — así que la identidad propia se refuerza, pero por criterio, no
por la subvención.

En la misma sesión, **auditoría técnica** (Claude Code, solo lectura) que reveló el
estado real del repo: pipeline huérfano (CSV origen perdido, JSON canónico), 39 géneros
corruptos, ~35 releases duplicados, ~41 artistas duplicados por capitalización, y ~400 KB
de parámetros de tracking de Bandcamp en las URLs. Primer PR de limpieza —
`scripts/pipeline.py` con paso `clean_urls` — mergeado como **PR #5**, ahorrando 418 KB
(26%). `[FIRME]`

**Arquitectura decidida** repasando referentes (NTS, Boomkat, UbuWeb, Monoskop, Dublab,
Discover Quickly, CARI, Fonts in Use): **dos puertas a un mismo archivo** →
**EXPLORAR** (ADN Discover Quickly/Boomkat: descubrimiento) + **ARCHIVO** (ADN
Monoskop/UbuWeb: denso, textual), ambas llevando a la misma **FICHA** de disco. La
dirección estética inicial se llamó *"xerox que arde"* (base fotocopia B/N con quemazos
de color ácido). Un intento de re-estilar la UI vanilla solo con CSS se descartó como
camino equivocado. `[FIRME]`

### 2.2 · Sistema visual: el sprint de diseño (5 jul) `[FIRME]`

Sesión de diseño puro: **seis versiones de EXPLORAR, tres de ARCHIVO, una de FICHA**,
todas con datos reales del JSON en vivo. De aquí salió el sistema visual **congelado**:

**Tokens (firmes, no re-debatir):**
- Papel `#F2EFE8` · Tinta `#111111` · Lima QCR `#A3E635` (solo interacción).
- La lima fue un **override consciente** de una prohibición previa de color: se adopta
  como puente de marca hacia `queimadacircuitrecords.com`.
- Display: **Big Shoulders** (grotesca condensada, 700–900, uppercase).
- Cuerpo: **IBM Plex Mono**.
- **Sin border-radius, sin sombras, sin simular texturas por CSS.**

**Reglas de interacción de EXPLORAR:**
- **MÁS DISCOS** (rebaraja 60 discos con variedad de género garantizada),
  **GÉNERO AL AZAR** (cae en uno de los ~276 tags con ≥8 discos), **AÑO AL AZAR**
  (1990–2025). Género y año **no se combinan** — combinar es trabajo del ARCHIVO.
- **Sin buscador** en EXPLORAR: quien quiere buscar, va a ARCHIVO.

**ARCHIVO:** índice alfabético de artistas en reposo → registro filtrable/ordenable en
cuanto se toca cualquier faceta (búsqueda, género, año, artista), con chips de filtro
activo y retorno al índice.

**Decisiones-carácter y sus vetos:**
- Se rechazó **"OTRA TIRADA"** como etiqueta de botón (connotación de casino) → *MÁS DISCOS*.
- Se rechazó un **selector fijo de géneros** (encasillamiento) → drops de género aleatorios.
- Se rechazó el **emoji de reloj de arena ⌛** porque **renderiza en color en el iPad y
  rompe la paleta B/N** → glifos de dado (⚁). De aquí sale la **regla de sistema:
  solo glifos tipográficos, nunca emoji de color; SVG monocromo si no hay glifo.** `[FIRME]`

También aquí se fijó que el scrape de portadas extrajera **`album_id` en la misma pasada
que `og:image`**, para poder usar el **reproductor embebido oficial de Bandcamp** en la
FICHA (se descartaron APIs de streaming de terceros por insuficientes para catálogo
underground local). `[FIRME]`

### 2.3 · Limpieza de datos: tres PRs (5 jul) `[FIRME]`

- **PR A (#6)** — 39 géneros corruptos por un *row-shift bug* del pipeline CSV original →
  26 corregidos, 13 a `null`, con guardas de null en `app.js`.
- **PR B (#7)** — dedupe: 30 fusiones de release, 41 grupos de renombrado de artista.
  Miguel **vetó** la fusión `Judy`/`judy` por falta de evidencia de ser la misma persona.
  Recuento tras PR B: **2.364 álbumes, 1.064 artistas, 2.281 tags, 33 años.**
- **PR C (#8)** — normalización de tags: topónimos vascos a forma euskera (`bilbo`,
  `donostia`, `gasteiz`, `euskal herria`); política **conservadora entre clusters** (no
  fusionar entre idiomas/familias léxicas — `dnb`/`drum & bass`, `rock & roll`/`rock'n'roll`
  se dejan para la **capa de alias de búsqueda** de la migración); basura fuera; caracteres
  invisibles limpiados.

Patrón que se consolidó aquí y quedó como contrato: **PRs pequeños e idempotentes con
tablas de lookup explícitas y locks de valor esperado** (el patrón `GENRE_FIXES` de PR A).
Miguel pilló una discrepancia en el recuento que reportó Claude Code (28+11 vs. los 26+13
acordados) antes de mergear — señal de que la revisión humana funciona. `[FIRME]`

### 2.4 · Portadas y fusión al canónico (8 jul, sesión nocturna hasta ~4:30) `[FIRME]`

- **Scraper de portadas** `scripts/scrape_covers.py` (stdlib puro, User-Agent de
  navegador, delay 1,5–2 s, checkpoints atómicos cada 25 ítems, reanudable) + workflow
  `scrape-covers.yml` (`workflow_dispatch` con inputs `limit` y `push_branch`).
- **Test de 20: 20/20 sin un solo 403.** Se confirmó que el UA de navegador desde los
  **runners de GitHub** pasa el filtro anti-bot → el fantasma de dic. 2025 exorcizado.
- **Pasada completa (~1h32): 2.337/2.348 OK (99,5 %).** 11 errores `http_404` (álbumes
  borrados de Bandcamp) + 16 sin URL. Duda resuelta empíricamente: los 53 releases en
  dominio custom (crudobilbao.com, wavememory.net, zeromoon.com) resultaron ser Bandcamp
  con dominio propio — pasaron todos.
- Cada ítem trae `cover_url` (og:image, `f4.bcbits.com`, sufijo de tamaño intercambiable
  para derivar thumbnails sin re-scrapear) + `album_id` + `item_type` ("a").
- **Fusión al canónico**: paso idempotente `step_merge_covers` (**PR #10**), no-op si
  falta `covers.json`; añade `cover_url` (string|null) y `album_id` (int|null) a los 2.364
  álbumes → 2.337 con datos, 27 null. Luego **`validate()` endurecido a exactamente 9
  campos (PR #11)**, con idempotencia demostrada byte a byte.

Incidente notable de esta sesión: el prompt de merge se mandó **por error al repo
equivocado** (`genre-explorer` en vez de MEU) y el agente **paró y reportó** en vez de
seguir. Miguel lo señaló como el comportamiento correcto — quedó como patrón. `[FIRME]`

### 2.5 · La migración Vite+React: F0→F5 `[FIRME]`

El vanilla viejo era un buscador que no estaba *vivo*. La migración lo convirtió en las
tres puertas del sistema visual congelado. Se hizo con **phase gates** (una PR + OK
explícito por fase):

- **F0 (diagnóstico, solo lectura)** — el agente leyó el repo de verdad y levantó
  contradicciones legítimas: los mockups no tenían ni una imagen y la FICHA era anterior
  al scrape. Salieron **8 decisiones**, entre ellas:
  - EXPLORAR **100 % tipográfico** (las portadas viven en FICHA; meter portadas al muro
    sería reabrir el diseño en mitad de la migración).
  - Player Bandcamp `size=large` con tracklist, **click-para-cargar** bajo las acciones
    (evita llamar a bandcamp.com en cada ficha).
  - **Hash router artesanal** (`#/`, `#/archivo?…`, `#/disco/:id`), ~30 líneas.
  - **Deploy híbrido** (opción A, `gh-pages`): el vanilla convive en `/MEU/` y lo nuevo en
    `/MEU/v2/` hasta el cutover.
  - **Alias de tags solo-búsqueda** (jungle fuera del grupo dnb; lista semilla a aprobar
    en F3).
  - **CSS puro** contra tokens, cero librerías de UI (nada de Tailwind/shadcn/framer-motion).
- **F1 (PR #12)** — scaffolding Vite+React 19, tokens, esqueleto, router hash, workflow de
  deploy híbrido. Validado en producción: vanilla byte-idéntico en `/MEU/` + esqueleto vivo
  en `/MEU/v2/` con Big Shoulders correcta.
- **F2 (PR #13)** — **EXPLORAR**: muro de 60 tiles, GÉNERO/AÑO AL AZAR, mini-ficha.
- **F3 (PR #14)** — **ARCHIVO**: índice, registro filtrable, facetas, filtros en la URL,
  capa de alias de tags (5 grupos aprobados).
- **F4 (PR #15)** — **FICHA**: portada tratada, player Bandcamp, 3 poblaciones, tags
  clicables, similares por solape de tags.
- **Pulido**: player autocarga en FICHA + player small en mini-ficha (**PR #16**);
  mini-ficha compacta, player en línea/apilado según ancho (**PR #17**); portadas
  **tratadas** (grayscale+contrast+multiply) en el muro de EXPLORAR (**PRs #18, #19**).

Aquí se consolidó la **regla de portadas**: en el muro nunca aparecen limpias, siempre
tratadas (grayscale+contrast+multiply) — la "retícula de carátulas". La foto limpia solo
se ve, tratada, en la FICHA. `[FIRME]`

- **F5 · Cutover (pendiente).** Se está rumiando, no urge: destino final (¿raíz
  `bu-chip.github.io/MEU/` o subdominio `meu.queimadacircuitrecords.com`?) y qué hacer con
  el vanilla (¿a `/v1/` archivado o retirado?). `[FIRME que está pendiente]`

### 2.6 · El escalado a Euskal Herria (12–13 jul) `[FIRME]`

El paso de "catálogo de Bilbao" a "catálogo de Euskal Herria". Dos hallazgos lo
gobernaron:

**Hallazgo técnico: `/tag/` ha muerto.** El viejo sistema de páginas `/tag/` de Bandcamp
ya no sirve; el descubrimiento se hace vía la **API interna `discover_web`** (POST con
paginación por cursor). Devuelve por ítem un campo **`location` / `band_location`** que es
el arma anti-colisión principal. El contrato quedó documentado en
`docs/scraping-method.md`.

**Investigación de tags.** Miguel llegó con medidas reales de `result_count` de siete
tags (bilbao 2.621; euskal-herria 385; euskadi 363; basque 188; donostia 61; iruña 41;
gasteiz 27), que revelaron dos cosas: Bilbao concentra casi todo el volumen, y los tags de
capital son sorprendentemente pequeños → **las variantes de grafía y los municipios
pequeños son críticos**. Sobre eso se razonó una lista candidata amplia:

- **~200 tags pensados** (CSV `meu_tags_candidatos.csv`: 145 Tier A / 44 Tier B /
  11 Tier C), estructurados por variantes de grafía, cobertura geográfica de los cuatro
  territorios CAV + Navarra (+ Iparralde diferido), tags de identidad (`euskal-musika`,
  `euskaraz`…) y compuestos género-lugar (`bilbocore`, `donosti-sound`).
- Principio explícito de la fase de medición: **recall sobre precisión** — el coste
  marginal por tag candidato es una llamada API, así que se mide ancho y se filtra
  después. El `location` filtra los falsos positivos automáticamente.
- Tras medir los que faltaban → **lista cerrada de ~107 tags**, cada uno con volumen real
  y veredicto auditado (cero corazonadas). **Fuera por colisión**: `vitoria` (Vitória
  Brasil), `durango`, `donosti`, `vasco` (nombre propio), `basque-country-rock-&-roll`
  (0 resultados; el `&` no sobrevive a la normalización).
- Matiz Iparralde: `basquemusic` y `euskalmusika` traen contenido de Iparralde → **entran
  a la lista pero su material se filtra por `band_location` a CAV+Navarra en esta oleada**;
  lo claramente de Iparralde (Baiona, etc.) va a `rejected` o a la cola `oleada-2`.

**El scraper de descubrimiento** (rama `claude/euskadi-catalog-expansion`): `discover_web`
+ cursor → **dedupe por `album_id` + URL normalizada** contra el canónico y contra
`rejected.json` → ficha solo para candidatos nuevos → normalización vía pipeline →
`data/candidates_YYYY-MM.json` (**nunca** el canónico) → **PR con tabla legible agrupada
por tag de origen, con columna `band_location`**. Presupuesto ~900 req/run, 1 req/2 s,
reanudable por checkpoint, idempotente. Un *canary probe* vigila el Client Challenge de
Bandcamp. Workflow mensual (**PR #21**): cron día 3 + `workflow_dispatch` manual;
sin-novedad-sin-PR.

**El resultado.** El backfill de la oleada 1 (los 107 tags, ~9.600 resultados → 4-8
pasadas manuales desde Actions, cada una actualizando el mismo PR del mes) llevó el
catálogo de **2.364 a 7.568 discos (×3,2)**, con ~5.537 tags únicos. `[FIRME]`

> **Nota sobre nº de PR de candidatos.** El histórico es consistente en el ×3,2 → 7.568 y
> en que **el canónico solo se toca vía PR de candidatos que revisa Miguel**. Sobre la
> numeración exacta hay una pequeña ambigüedad: en el histórico aparece la mención de
> mergear el **PR #24** (ficheros de diagnóstico) y el sistema de candidatos mensual
> (rama `candidates/2026-07`). El estado operativo exacto (qué PR de candidatos está
> abierto y su recuento) conviene confirmarlo en Notion/GitHub, no aquí. `[RECONSTRUCCIÓN]`

### 2.7 · El hallazgo de rebote: explorador de microgéneros (13 jul) `[FIRME]`

Buscando subir unas portadas, se descubrió que el campo `tags` del catálogo ampliado es un
**atlas de microgéneros** al estilo EveryNoise/genre-explorer, pero con **un grupo vasco
real y reproducible detrás de cada nodo**. Los números medidos:

- **~700 microgéneros con ≥3 discos reproducibles**; ~350 con ≥10. (EveryNoise cubre el
  planeta con ~6.000; que una sola escena regional sostenga 350-700 nodos es densidad
  brutal.)
- **99,8 % de discos con `album_id`** (reproducibles).
- Joyas: **poky/bumping/hardbass** (makina vasca, microgénero regional genuino), **Rock
  Radical Vasco/RRV**, raíz (**trikitixa, txalaparta, alboka, bertsolaritza**), y
  microgéneros de internet inesperados (dreampunk, medicalcore, hexd, postvore,
  deathdream).
- Cuello de botella acotado y mecánico: **normalización/fusión de tags** antes de montar
  nada (crust/crust punk/crustcore = 1 nodo; erratas con volumen; basura compuesta). Un
  mapa de fusión baja ~700 → 400-500 nodos limpios.
- Material ya generado (rama `claude/meu-tags-diagnostic`):
  `docs/diagnostico-tags-2026-07.md` + `data/tag_buckets_2026-07.json` (los 5.537 tags
  clasificados).

Concepto: **la tercera pieza del ecosistema QCR.** genre-explorer = mapa del mundo /
MEU = guía de casa / **esto = mapa sonoro microgénero de la escena vasca.** Mismo ADN que
el genre-explorer (navegar por género + preview al vuelo) pero alimentado por Bandcamp
vasco. Implementación: futura, sin prisa. **El suelo está medido y firme.**

---

## 3. Ideas aparcadas (y por qué) `[FIRME]`

- **Cuentas de usuario / login / capa social** (referencia: lazyrecords.app). Rompe el
  modelo estático (GitHub Pages, cero servidor, cero mantenimiento): pide backend + BBDD +
  auth + moderación + almacenamiento. Choca con el principio de "nada de SaaS ni cosas que
  requieran mantenimiento". Ya estaba aparcado en el backlog viejo con buen criterio.
  *Apunte útil*: para "que la gente proponga discos" quizá **no hace falta backend** — el
  mismo patrón del scraper (formulario → PR → Miguel aprueba) sirve, y sigue siendo
  estático.
- **Inscripción de artistas** (subir portada/datos sin pasar por Bandcamp). Mismo motivo:
  requiere infraestructura. Aparcado.
- **Continuidad perfecta del player** (tocar tile → suena; ir a ficha → sigue por donde
  ibas). **Límite técnico duro**: el embed oficial de Bandcamp es un iframe que **no se
  controla desde fuera**; al navegar mini-ficha→ficha el iframe se recrea y arranca de
  cero. La única alternativa (reproducir mp3 propios) ya está descartada para el MEU
  (Bandcamp no da API de previews, y scrapear audio va contra el espíritu de dirigir
  tráfico a Bandcamp). → El **autoplay** se puede mejorar; la **continuidad exacta, no**.
- **Financiación pública** (Eremuak, BBK, Diputación, BilbaoArte, Etxepare). No abandonada,
  pero **aparcada como motor**: no dirige el diseño. El proyecto es auténtico primero.
- **Puente MIDI/Digitakt** (Web MIDI o python-rtmidi para generar patrones). Idea viva,
  fichada, conectada a la estética de **555 Kables** — pero es de otro carril, no del MEU.

---

## 4. Estado al cierre de esta crónica (jul 2026)

- **Datos**: cerrados y blindados. Limpieza (PRs #6–#8), portadas+album_id (99,5 %), merge
  (PR #10) y `validate()` a 9 campos exactos (PR #11). `[FIRME]`
- **App**: migración **F1→F4 en producción** en `/MEU/v2/` (tres puertas vivas), más pulido
  (#16–#19). **Falta el cutover F5.** `[FIRME]`
- **Escalado**: **completo para la oleada 1** — catálogo **×3,2 → 7.568 discos**, sistema
  de descubrimiento mensual autónomo (cron día 3 + dispatch manual). El robot propone vía
  PR de candidatos; **el canónico jamás se toca automáticamente**. Iparralde = oleada 2. `[FIRME]`
- **Curación**: el trabajo de comisario de verdad — revisar los PR de candidatos disco a
  disco, borrar lo que no encaje y apuntar sus URLs en `rejected.json` — es ahora la acción
  principal pendiente. Criterio **maximalista**: ante la duda, entra; solo fuera lo
  clarísimamente ajeno. `[FIRME]`
- **Explorador de microgéneros**: idea con suelo firme y datos medidos; implementación
  futura. `[FIRME]`
- **Notion**: dos páginas — **"MEU - Mapa Euskadi Underground"** (la viva, de trabajo) y
  **"MEU (archivo)"** (baúl histórico con las subpáginas). `[FIRME]`
- **Backlog técnico menor**: actualizar `actions/checkout@v4` y `setup-node@v4` (aviso de
  Node 20 deprecated). `[FIRME]`

---

## 5. Decisiones clave y su porqué (no re-debatir)

1. **El JSON canónico jamás se toca desde procesos automáticos.** El scraper solo escribe
   ficheros de candidatos; nada entra sin PR revisado por Miguel. *Porque* el CSV original
   se perdió y el JSON es la única fuente de verdad — corromperlo no tiene deshacer.
2. **Robot propone, Miguel dispone.** El pipeline es un sistema de *propuesta*, no
   autónomo. *Porque* el valor del MEU es la curación humana, no el volumen.
3. **Criterio maximalista.** Ante la duda, un disco entra; solo se descarta lo clarísimamente
   ajeno (extranjero sin ningún vínculo vasco). *Porque* es una guía de una escena, no un
   filtro de calidad.
4. **Diagnóstico-first (Fase 1 solo lectura → OK → Fase 2 escribe).** Patrón duro, no
   opcional. *Porque* mide antes de comprometer y evita que el agente rompa cosas.
5. **PRs pequeños y acotados, un concern por PR, rama nueva explícita, CERO commits a
   main.** Miguel mergea y hace smoke-test en el iPad como verificación final. *Porque*
   mantiene el historial limpio y reversible.
6. **Idempotencia como contrato.** Los pasos del pipeline deben poder re-ejecutarse sin
   daño (probado con sha256 idénticos). *Porque* desde iPad todo se relanza vía Actions.
7. **Modelo estático innegociable.** Nada de backend, cuentas, BBDD ni SaaS. *Porque* el
   proyecto debe sostenerse solo, sin mantenimiento constante ni costes de servidor.
8. **Sistema visual congelado.** Papel `#F2EFE8` / tinta `#111111` / lima `#A3E635` (solo
   interacción); Big Shoulders (display, uppercase) + IBM Plex Mono (cuerpo); sin
   border-radius, sombras ni texturas CSS.
9. **Nunca emoji de color en la UI.** Solo glifos tipográficos o SVG monocromo. *Porque*
   el color rompe la paleta B/N y en el iPad renderiza en color.
10. **Portadas SIEMPRE tratadas** (grayscale+contrast+multiply), nunca foto limpia en el
    muro. *Porque* es lo que hace del EXPLORAR una pieza propia y no un grid de tienda.
11. **`discover_web`, no `/tag/`.** El sistema de tags viejo de Bandcamp murió; el
    endpoint interno con paginación por cursor es el correcto, y su campo `location` es el
    anti-colisión.
12. **iPad sin terminal.** Toda ejecución pasa por GitHub Actions, Claude Code y la web de
    GitHub / dashboard de Cloudflare. Ninguna solución puede asumir terminal local.
13. **Notion: prepend/append de secciones datadas**, nunca editar bloques en sitio
    (`update_content` con `old_str`/`new_str` es frágil por caracteres invisibles).

---

*Fin de la crónica. Reconstruida desde el histórico del Project; el estado operativo vive
en Notion ("MEU - Mapa Euskadi Underground") y en `Bu-chip/MEU`.*
