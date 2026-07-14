# MEU — Mapa Euskadi Underground

**La guía personal de [Queimada Circuit Records](https://queimadacircuitrecords.com) a
la música underground de Euskal Herria en Bandcamp.**

El MEU es un archivo curado a mano: una guía de una escena, no un filtro de calidad ni un
recomendador algorítmico. Ante la duda, un disco entra; solo se descarta lo clarísimamente
ajeno. Es una web estática, sin cuentas ni backend, que dirige el tráfico de vuelta a
Bandcamp — a comprar la música y apoyar a quien la hace.

## Estado

- **Catálogo:** 7.568 publicaciones · 3.572 artistas · 5.537 tags · 42 años.
- **Fuente de verdad:** [`data/bandcamp_bilbaotags_clean.json`](data/) — esquema estricto
  de **9 campos** por álbum: `id`, `artist`, `title`, `genre`, `year`, `tags`, `url`,
  `cover_url`, `album_id`. El CSV de origen no está versionado; **el JSON es la única
  fuente de verdad** y no se toca desde ningún proceso automático.
- **App:** migración a Vite + React **completa (F1→F4) y en producción**, conviviendo con
  el sitio vanilla hasta el cutover (F5, pendiente).

## Arquitectura

Arquitectura **estática, sin backend**, desplegada en GitHub Pages.

- El sitio **vanilla** (histórico) se publica en la raíz: `bu-chip.github.io/MEU/`.
- La **app Vite + React** vive en [`app/`](app/) y se despliega bajo `/MEU/v2/`. El
  workflow `deploy.yml` publica ambos en la rama `gh-pages` (vanilla en la raíz, build de
  Vite en `/v2/`), de modo que conviven durante la migración. El cutover final (destino
  definitivo y retirada/archivo del vanilla) es la fase **F5**, aún por decidir.
- Routing por **hash router** artesanal (`#/`, `#/archivo`, `#/disco/:id`). CSS propio
  contra design tokens; sin librerías de UI.

La app son **tres puertas a un mismo archivo**:

- **EXPLORAR** — muro tipográfico de descubrimiento (más discos / género al azar / año al
  azar), con portadas tratadas.
- **ARCHIVO** — índice de artistas + registro filtrable por facetas, con los filtros
  reflejados en la URL y una capa de alias de tags para la búsqueda.
- **FICHA** — página de disco con portada tratada, reproductor embebido de Bandcamp, tags
  clicables y discos similares por solape de tags.

## Datos y pipeline

Todo el saneamiento del catálogo pasa por [`scripts/pipeline.py`](scripts/), diseñado como
un conjunto de pasos **idempotentes** (re-ejecutar no cambia el resultado; probado byte a
byte). `validate()` exige exactamente los 9 campos. Cualquier cambio en los datos entra
por PR revisada, nunca por escritura automática sobre el canónico.

## Escalado y descubrimiento

El catálogo creció de Bilbao a toda Euskal Herria mediante un sistema de descubrimiento que
**propone candidatos vía Pull Request para revisión humana** — el robot propone, la
curación la decide una persona.

- El viejo sistema de páginas `/tag/` de Bandcamp dejó de funcionar; el descubrimiento se
  hace vía la API interna `discover_web`. El contrato (con su advertencia de posible
  caducidad de la API) está documentado en
  [`docs/scraping-method.md`](docs/scraping-method.md).
- Scripts: [`scripts/discover_tags.py`](scripts/), `research_tags.py`, `probe_tag_pages.py`.
  Workflows: `discover-tags.yml`, `research-tags.yml` (cron mensual + ejecución manual).
- El scraper escribe **solo** ficheros de candidatos (`data/candidates_YYYY-MM.json`),
  nunca el canónico. Deduplica por `album_id` + URL normalizada contra el catálogo y contra
  `rejected.json` (las URLs descartadas no se vuelven a proponer).

## Estructura del repo

```
data/     JSON canónico + ficheros de candidatos/descartes
app/      aplicación Vite + React (se despliega en /MEU/v2/)
scripts/  pipeline de datos y scrapers (Python, stdlib)
docs/     método de scraping, diagnósticos, historia del proyecto
design/   mockups HTML del sistema visual congelado
```

## Sistema visual

Congelado (decisión cerrada). Paper `#F2EFE8`, tinta `#111111`, lima `#A3E635` (solo en
interacción). Display: **Big Shoulders** (condensada, uppercase). Cuerpo: **IBM Plex
Mono**. Sin `border-radius`, sin sombras, sin emoji de color (solo glifos tipográficos o
SVG monocromo). Las portadas se muestran siempre tratadas (grayscale + contrast +
multiply), nunca como foto limpia. Los mockups de referencia están en [`design/`](design/).

## Cómo se trabaja

- **Diagnóstico-first:** toda tarea empieza con una fase de solo lectura que reporta y
  espera OK antes de escribir.
- **PRs pequeños y acotados**, un concern por PR, rama nueva explícita, **cero commits
  directos a main**.
- **Modelo estático innegociable:** nada de backend, cuentas, bases de datos ni SaaS.
- Toda la ejecución pasa por **GitHub Actions** y la web de GitHub (flujo de trabajo desde
  iPad, sin terminal local).

---

Un proyecto de **Queimada Circuit Records**. La historia completa del proyecto está en
[`docs/historia-meu.md`](docs/historia-meu.md).
