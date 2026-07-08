# FASE 0 — Diagnóstico y plan de migración a Vite + React

Fecha: 2026-07-08 · Rama: `claude/vite-react-migration-plan-gqbf43` · Sin código de app en esta fase.

Fuentes revisadas: `data/bandcamp_bilbaotags_clean.json` (canónico), `design/meu-explorar-v8-deriva.html`, `design/meu-archivo-v3-hibrido.html`, `design/meu-ficha-v1.html`, prototipo actual (`index.html` + `assets/`), workflow existente `scrape-covers.yml`.

---

## 1. Discrepancias mockups ↔ dataset canónico

### 1.1 Los mockups embeben un snapshot viejo del dataset

Los tres mockups llevan inlineado un JSON de **2.396 álbumes / 1.069 artistas**; el canónico tiene **2.364 / 1.064** (post-limpieza de géneros). Consecuencias:

- Los contadores de cabecera («2.396 releases · 1.069 artistas · 1990–2025») están hardcodeados. En la app deben **computarse del JSON en runtime**.
- El copy del botón GÉNERO AL AZAR («caes en uno de 276 estilos») también: sobre el canónico, el mismo criterio da otro número (ver 1.4).

### 1.2 El esquema de los mockups es anterior a las portadas

Los datasets embebidos usan `{a, t, y, g, u}` — **no existen `cover_url`, `album_id`, `tags` (salvo en FICHA) ni `id`**. Los mockups se diseñaron antes del scrape de portadas. Impacto por pantalla:

- **EXPLORAR:** el grid del mockup es **100 % tipográfico** — cuatro variantes de tile (`v-inicial`, `v-negra`, `v-titulo`, `v-split`) rotando en ciclo `i%8`, cero imágenes. El brief pide «tiles B/N con las portadas». No es contradicción (el mockup no pudo asumir portadas), pero **la composición del tile con portada no está especificada en ningún mockup** → decisión D5. Las cuatro variantes tipográficas son el fallback natural para los 27 álbumes sin cover.
- **FICHA:** el hueco de portada dice «PORTADA PENDIENTE · IRÁ TRATADA (THRESHOLD/DITHER)» y el footer: «siempre irá tratada, nunca foto limpia». El tratamiento exacto (threshold/dither real vs. grayscale CSS) es decisión D6.
- **FICHA:** el mockup **no tiene player embebido** — solo enlace «ESCUCHAR EN BANDCAMP ↗». El player por `album_id` que pide el brief no tiene sitio definido en el layout → decisión D7.

### 1.3 Huecos de datos que los mockups no contemplan

| Campo | Nulls/vacíos | Manejo en mockup | Riesgo |
|---|---|---|---|
| `year` | 23 | «s/f» | ninguno, resuelto |
| `genre` | 11 | «—» | ninguno, resuelto |
| `tags` | 30 (lista vacía) | n/a | **«cerca de esto» por solape de tags devuelve vacío** para 30 fichas (11 de ellas tampoco tienen género para un fallback) → propongo fallback: mismo artista → mismo género → azar |
| `url` | 16 | `href="#"` (silencioso) | tile/línea clicable que no lleva a nada |
| `cover_url` | 27 | n/a | fallback tipográfico en grid y ficha |
| `album_id` | 27 | n/a | sin player en ficha |

Solapes verificados: los 27 sin `cover_url` son exactamente los 27 sin `album_id`. De esos, **16 tampoco tienen `url`** — para ellos el fallback «enlace directo» de FICHA **no existe**: ni player, ni portada, ni enlace. Hay que definir ese estado (decisión D8). Los otros 11 sí tienen `url` y el fallback funciona.

### 1.4 «GÉNERO AL AZAR» no usa géneros: usa tags

En el mockup de EXPLORAR el botón sortea sobre `D.tagIndex`: **tags con ≥ 8 releases** (276 en el snapshot viejo; sobre el canónico son **272**). No sortea sobre el campo `genre` (25 valores). Es coherente con el copy («dungeon synth, horror disco, poky…» son tags, no géneros), pero conviene confirmar el criterio: umbral ≥ 8 recalculado dinámicamente, u otra cosa (decisión D9).

### 1.5 Faceta GÉNERO de ARCHIVO: el mockup asume 54 géneros, el canónico tiene 25

El mockup pinta `D.genres.slice(0,14)` (top-14 de 54). Tras la limpieza, el canónico tiene **25 géneros**. ¿Mostrar los 25 o mantener top-14? (decisión D10).

### 1.6 La búsqueda de ARCHIVO no busca en tags

El mockup filtra por `artista | título | género | año` — su dataset embebido ni siquiera lleva tags. La **capa de alias de tags** del brief implica búsqueda sobre tags. Hay que decidir el alcance: ¿la búsqueda libre incluye tags (con expansión de alias), o los alias solo aplican al filtro por tag que llega desde los chips de FICHA? (decisión D11). Y necesito la tabla de alias o criterios para redactar un borrador (decisión D12).

### 1.7 Menores (sin decisión, se resuelven en implementación)

- El nav tiene «sobre el proyecto» sin destino en los tres mockups → decisión D15 (mínima).
- La mini-ficha inferior de EXPLORAR/ARCHIVO es un stub («FICHA → aprobada, ver meu-ficha-v1»): en la app el click en tile/línea **navega a la ruta FICHA** — asumo que la barra inferior desaparece, salvo que quieras conservarla como preview intermedio.
- Orden por defecto del ledger: año descendente, click en cabecera alterna asc/desc y cambia de columna — replicable tal cual.
- Paginación del ledger: bloques de 150 + «mostrar más (N restantes)» — replicable tal cual.
- Índice alfabético: letra inicial normalizada (NFD, sin diacríticos), no-ASCII → «#» (11 artistas caen en «#»). Replicable tal cual.

---

## 2. Estructura del proyecto Vite propuesta

### 2.1 Árbol de carpetas

La app vive en `app/` para no tocar el prototipo actual (raíz) durante la migración:

```
MEU/
├── index.html, assets/, data/, scripts/, design/   ← intactos (prototipo + canónico)
├── app/                          ← nueva app Vite + React
│   ├── index.html
│   ├── vite.config.js            ← base configurable, acceso a ../data
│   ├── package.json
│   ├── .eslintrc / eslint.config.js
│   ├── public/
│   │   └── fonts/                ← woff2 self-hosted (si D13 = self-host)
│   └── src/
│       ├── main.jsx
│       ├── App.jsx               ← router + layout común (header, puertas, firma)
│       ├── styles/
│       │   ├── tokens.css        ← custom properties congeladas (papel/tinta/lima, fuentes)
│       │   └── base.css          ← reset (box-sizing, border-radius:0, ::selection)
│       ├── lib/
│       │   ├── data.js           ← carga del JSON + derivaciones memoizadas
│       │   │                        (contadores, índice de artistas, tagIndex ≥8,
│       │   │                         índice de búsqueda)
│       │   ├── aliases.js        ← tabla de alias de tags + expansión de queries
│       │   ├── random.js         ← shuffle, muroLibre (variedad por género), azar
│       │   ├── similares.js      ← solape de tags + cascada de fallbacks
│       │   └── covers.js         ← rewrite de tamaños bcbits + detección de fallback
│       ├── components/           ← Tile (5 variantes), Ledger, Facetas, Chips,
│       │                            PlayerEmbed, Portada, MiniFicha…
│       └── pages/
│           ├── Explorar.jsx
│           ├── Archivo.jsx
│           └── Ficha.jsx
└── .github/workflows/
    ├── scrape-covers.yml         ← existente, no se toca
    ├── ci.yml                    ← nuevo: lint + build en cada PR
    └── deploy-pages.yml          ← nuevo: build + composición + deploy a Pages
```

Cada pantalla mapea 1:1 a su mockup; la lógica de datos vive en `lib/` como funciones puras (testeables sin DOM).

### 2.2 Routing: hash router

**Sí, hash router.** GitHub Pages no permite rewrites de servidor; con history router los deep links (`/ficha/123` recargado o compartido) darían 404 salvo el hack de `404.html`, que es frágil y ensucia analytics. Con hash router:

- `#/` → EXPLORAR (entrada)
- `#/archivo` → ARCHIVO, con estado de filtros en query (`#/archivo?q=…&genero=…&año=…&artista=…&tag=…`) para que cualquier vista filtrada sea enlazable — necesario porque los chips de tags de FICHA enlazan a ARCHIVO filtrado
- `#/ficha/:id` → FICHA (usa el campo `id` del canónico, que es estable)

Implementación: `react-router-dom` con `HashRouter` (estándar, aburrido, mantenido) o un router propio de ~40 líneas si prefieres cero dependencias más allá de React (decisión D3).

### 2.3 Carga del JSON: fetch de asset con hash, sin copiar el archivo

Ni import estático (metería 1,4 MB en el bundle JS, bloqueando parse), ni fetch de ruta fija en `public/` (sin cache-busting). Propuesta:

```js
// lib/data.js
import dataUrl from '../../../data/bandcamp_bilbaotags_clean.json?url'
```

Vite empaqueta el archivo canónico **desde `data/` directamente** (fuera del root de la app, permitido vía `server.fs.allow`) como asset con hash en el nombre → cacheable para siempre, se invalida solo cuando el canónico cambia, y **una única fuente de verdad sin copias en el repo**. Se hace `fetch(dataUrl)` una vez en el bootstrap, se derivan en memoria los índices (artistas, tagIndex, contadores, índice de búsqueda con alias) y se sirve todo por contexto de React. 2.364 registros se derivan en < 10 ms; no hace falta pre-generar nada en build.

El JSON gzipeado ronda ~250 KB por el wire (Pages sirve gzip/brotli). Estado de carga: pantalla vacía con tokens (papel/tinta) hasta resolver — sin spinner decorado, coherente con la estética.

### 2.4 Imágenes bcbits: rewrite de tamaño + lazy obligatorio

Las 2.337 `cover_url` son `https://f4.bcbits.com/img/aXXXX_5.jpg` (700×700, ~50-120 KB cada una). Un muro de 60 tiles a `_5` serían varios MB. Bandcamp expone variantes por sufijo; estrategia:

- **Grid EXPLORAR:** rewrite cliente `_5.jpg → _2.jpg` (350×350) — suficiente para tiles de ~120-180 px incluso en retina 2×.
- **Portada FICHA:** `_5.jpg` tal cual (slot de hasta 420 px, retina cubierta).
- Todos los `<img>` con `loading="lazy"`, `decoding="async"`, `width`/`height` fijos (el tile ya es `aspect-ratio:1/1`, cero layout shift).
- B/N: `filter: grayscale(1) contrast(1.15)` como base (decisión D6 para dither real).
- Fallback `onError` → variante tipográfica del tile (cubre los 27 sin cover y cualquier 404 futuro de bcbits).
- Riesgo asumido: hotlinking a CDN de terceros. Hoy bcbits no restringe referer; si algún día lo hace, el fallback tipográfico degrada con dignidad. El workflow `scrape-covers.yml` ya existe para refrescar URLs muertas.

### 2.5 Player de FICHA

Formato iframe oficial:

```
https://bandcamp.com/EmbeddedPlayer/album={album_id}/size=small/bgcol=f2efe8/linkcol=111111/transparent=true/
```

(el player admite `bgcol`/`linkcol` en hex — se alinea con los tokens; variante `size=large` lleva artwork y tracklist). Cascada: `album_id` → player; sin `album_id` pero con `url` → solo acción primaria «ESCUCHAR EN BANDCAMP ↗»; sin ninguno (16 casos) → estado D8. El iframe se monta solo al entrar en la ficha y con `loading="lazy"`.

---

## 3. Deploy a GitHub Pages y convivencia con el sitio actual

Asunción a confirmar: Pages sirve hoy desde rama `main` / raíz (deploy-from-branch). El plan requiere cambiar la fuente a **GitHub Actions** en Settings → Pages (decisión D2).

### 3.1 Durante la migración: un artefacto, dos sitios

Pages solo sirve un artefacto, así que el workflow **compone** ambos:

```yaml
# deploy-pages.yml (esquema)
on:
  push: { branches: [main] }
  workflow_dispatch:
jobs:
  build:
    - checkout
    - setup-node 22 + cache npm
    - cd app && npm ci && npm run lint && npm run build   # base=/MEU/v2/
    - mkdir _site
    - cp index.html _site/ && cp -r assets data _site/    # prototipo actual → raíz
    - cp -r app/dist _site/v2/                            # app nueva → /MEU/v2/
    - touch _site/.nojekyll
    - upload-pages-artifact (_site)
  deploy:
    - actions/deploy-pages
```

- El sitio actual sigue en `https://bu-chip.github.io/MEU/` sin cambios visibles.
- La app nueva se prueba en `https://bu-chip.github.io/MEU/v2/` fase a fase.
- `base` de Vite parametrizada por env (`/MEU/v2/` ahora, `/MEU/` al cutover) — con hash router no hay más ajuste que ese.
- El `scrape-covers.yml` existente sigue commiteando a `data/`; cada merge a `main` redespliega ambos sitios con el JSON fresco.

### 3.2 Cutover (después de Fase 4, con tu OK)

Un solo cambio en el workflow: la app compila con `base=/MEU/` y se copia a la raíz de `_site`; el prototipo se retira (o se archiva en `/legacy/` un tiempo). Las URLs con hash (`/MEU/#/ficha/123`) no cambian de forma entre `/v2/` y raíz salvo el prefijo.

### 3.3 CI de PRs (guardarraíl)

`ci.yml` en cada PR: `npm ci && npm run lint && npm run build`. Sin build verde no se mergea. El deploy solo corre en `main`, así que ninguna fase toca producción hasta su merge aprobado.

---

## 4. Decisiones que necesito antes de implementar

Con recomendación marcada; donde no contestes, aplico la recomendación.

| # | Decisión | Opciones | Recomendación |
|---|---|---|---|
| **D1** | Ubicación de la app | `app/` conviviendo con prototipo · reemplazo directo en raíz | `app/` + composición en deploy |
| **D2** | Fuente de Pages | Cambiar a «GitHub Actions» en Settings (acción tuya, 1 min) · seguir deploy-from-branch commiteando `dist/` | **Actions** — commitear builds al repo es ruido |
| **D3** | Router | `react-router-dom` (HashRouter) · router propio ~40 líneas | react-router-dom |
| **D4** | Lenguaje | TypeScript · JavaScript | TypeScript (el esquema del álbum tipado paga solo) |
| **D5** | Tile de EXPLORAR con portadas | (a) 100 % portadas B/N, tipográfico solo como fallback de los 27 sin cover · (b) portadas intercaladas con variantes tipográficas como ritmo visual (eco del ciclo `i%8` del mockup) | **(b)** — conserva la identidad del mockup y absorbe los fallbacks sin que canten |
| **D6** | Tratamiento B/N de portadas | CSS `grayscale+contrast` · threshold/dither real por canvas (fiel al aviso del mockup, más coste) | CSS en Fase 2; evaluar dither en Fase 4 con portadas reales delante |
| **D7** | Player en FICHA | (a) `size=large` con artwork ocupando el slot de portada · (b) portada tratada en su slot + player `size=small` (barra 42 px) bajo la metaline | **(b)** — la portada tratada es pieza visual del layout; el player grande duplicaría artwork sin tratar |
| **D8** | Los 16 sin `url` ni `album_id` ni cover | Mostrarlos con estado «sin enlace» honesto · excluirlos de azar/grid | Mostrarlos — el archivo es el archivo |
| **D9** | Pool de GÉNERO AL AZAR | Tags con ≥ 8 releases dinámico (hoy 272) · umbral distinto · lista curada | Umbral ≥ 8 dinámico, copy con número computado |
| **D10** | Faceta GÉNERO en ARCHIVO | Los 25 géneros del canónico · top-14 fiel al mockup | Los 25 — ya están limpios, que se vean |
| **D11** | Alcance de los alias | Búsqueda libre incluye tags con expansión de alias · alias solo en filtro por tag (chips de FICHA) | Ambos: búsqueda libre matchea tags expandidos, filtro por tag también expande |
| **D12** | Tabla de alias | La redactas tú · propongo borrador (toponimia: bilbo↔bilbao, euskadi↔basque country↔país vasco, donostia↔san sebastián, gasteiz↔vitoria…) y la validas en la PR de Fase 3 | Borrador mío + tu validación |
| **D13** | Fuentes | Google Fonts CDN (como mockups) · woff2 self-hosted en `public/fonts` | Self-host — quita dependencia externa y ~300 ms de render |
| **D14** | Contadores de cabecera | Dinámicos del JSON (2.364/1.064) · hardcode del mockup | Dinámicos (asumo sí salvo veto) |
| **D15** | «sobre el proyecto» | Ruta propia `#/sobre` con texto tuyo · fuera de scope por ahora | Fuera de scope; el enlace queda inerte hasta que haya texto |

---

## 5. Fases siguientes (recordatorio del contrato)

| Fase | Rama | Alcance | Requiere |
|---|---|---|---|
| 1 | `feat/vite-fase-1` | Scaffolding Vite + tokens.css + layout común + deploy `/v2/` con página vacía | OK a D1–D4, D13; cambio de Settings si D2=Actions |
| 2 | `feat/vite-fase-2` | EXPLORAR completo (muro, 3 mandos, banda de estado, tiles con portada) | OK a D5, D6, D9, D14 |
| 3 | `feat/vite-fase-3` | ARCHIVO (índice, ledger, facetas, orden, paginación) + capa de alias | OK a D10, D11, D12 |
| 4 | `feat/vite-fase-4` | FICHA (player, portada, tags, similares, azar, retornos) + cutover propuesto | OK a D7, D8 |

Guardarraíles vigentes en todas: cero commits a `main`, PR por fase con tu OK previo, build+lint verdes antes de push, el JSON canónico no se toca, cero librerías de UI (CSS propio contra tokens).
