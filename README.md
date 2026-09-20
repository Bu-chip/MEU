# MEU — Mapa Euskadi Underground

**La guía personal de [Queimada Circuit Records](https://queimadacircuitrecords.com) a
la música underground de Euskal Herria en Bandcamp.**

El MEU es un archivo curado a mano: una guía de una escena, no un filtro de calidad ni un
recomendador algorítmico. Ante la duda, un disco entra; solo se descarta lo clarísimamente
ajeno. Es una web estática, sin cuentas ni backend, que dirige el tráfico de vuelta a
Bandcamp — a comprar la música y apoyar a quien la hace.

## Estado

- **Catálogo:** 7.637 publicaciones · 3.634 artistas · 5.575 tags · 44 años.
- **Fuente de verdad:** [`data/bandcamp_bilbaotags_clean.json`](data/) — esquema estricto
  de **9 campos** por álbum: `id`, `artist`, `title`, `genre`, `year`, `tags`, `url`,
  `cover_url`, `album_id`. El CSV de origen no está versionado; **el JSON es la única
  fuente de verdad** y no se toca desde ningún proceso automático.
- **App:** Vite + React en producción en la raíz de
  [mapa.queimadacircuitrecords.com](https://mapa.queimadacircuitrecords.com) (cutover F5
  hecho: el sitio vanilla salió del deploy; su fuente sigue en `main`, reversible).
- **Ubicaciones:** capa separada del canónico en [`data/locations/`](data/locations/). Ver
  [`docs/mapa.md`](docs/mapa.md) y la auditoría viva en
  [`docs/mapa-data-audit.md`](docs/mapa-data-audit.md).

## Arquitectura

Arquitectura **estática, sin backend**, desplegada en GitHub Pages. El workflow
`deploy.yml` compila `app/` y publica el build en la rama `gh-pages` con el CNAME del
dominio propio.

- Routing por **hash router** artesanal (`#/`, `#/archivo`, `#/mapa`, `#/disco/:id`). CSS
  propio contra design tokens; sin librerías de UI ni de mapas.

La app son **cuatro puertas a un mismo archivo**:

- **EXPLORAR**: muro tipográfico de descubrimiento (más discos, género al azar, año al
  azar), con portadas tratadas.
- **ARCHIVO**: índice de artistas y registro filtrable por facetas, con los filtros
  reflejados en la URL y una capa de alias de tags para la búsqueda.
- **MAPA**: el mismo archivo interrogado desde los lugares. Municipios de Euskal Herria
  sobre una retícula de puntos cuadrados, con los mismos filtros que ARCHIVO más rango de
  años, territorio y procedencia de la ubicación. El mapa domina la página y el detalle
  aparece por capas: panel de municipio (cifras, tags, releases y secciones plegadas de
  artistas, sellos, estadísticas y procedencia) y panel de tag (reparto por municipio).
  Por defecto dibuja el **escenario D** (5.969 releases): fuera las inferencias desde
  cuentas con varios artistas y las pistas de tag, activables en «Más filtros». Ver
  [`docs/mapa.md`](docs/mapa.md).
- **FICHA**: página de disco con portada tratada, reproductor embebido de Bandcamp, tags
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
- El scraper escribe **solo** ficheros de revisión de candidatos bajo `data/` (p.ej.
  `revision_2026-07.json`), nunca el canónico; la lista de tags a rastrear vive en
  `data/tag_candidates.json`. Deduplica por `album_id` + URL normalizada contra el catálogo
  y contra `rejected.json` (las URLs descartadas no se vuelven a proponer).

## Ubicaciones y MAPA

La ubicación de Bandcamp (`band_location`) se usaba solo como filtro durante el
descubrimiento y se perdía en el merge al canónico. Ahora vive **fuera del canónico**, en
capas separadas (evidencia → normalización → resolución → índice del mapa), todas
reproducibles con [`scripts/locations.py`](scripts/locations.py):

| Comando | Qué hace |
|---|---|
| `ingest FICHERO` / `check` | Registra el `band_location` de un fichero de candidatos como observación; la guardia falla si alguno se perdería (también en CI). |
| `recover` | Reconstruye observaciones desde todo el histórico git local. |
| `scrape` | Visita una ficha por cuenta sin evidencia (ritmo y presupuesto del scraper). |
| `gazetteer` / `places` | Nomenclátor de Wikidata y registro controlado de municipios. |
| `normalize` / `resolve` / `audit` / `build` / `all` | Categorías por texto crudo, resolución trazable por release, auditoría e índice del mapa. |
| `query --place X` / `--tag Y` | Cruces municipio × tag desde la terminal. |

**Limitaciones:**
- La ubicación es la **actual** de la **cuenta que publica** (grupo o sello), no la
  residencia histórica de nadie.
- La unidad es el municipio, dibujado en un punto representativo.
- Lo que solo dice «Basque Country», lo que está fuera de Euskal Herria y lo no resuelto se
  cuenta pero no se dibuja.

Tests: `python3 -m unittest discover tests` y `npm --prefix app test` (workflow `Tests`).

## Estructura del repo

```
data/            JSON canónico + ficheros de candidatos/descartes
data/locations/  ubicaciones: observaciones, registro de lugares, reglas, resolución, índice del mapa
app/             aplicación Vite + React (se despliega en la raíz del dominio)
scripts/         pipeline de datos y scrapers (Python, stdlib)
tests/           tests de la capa de ubicaciones (unittest)
docs/            método de scraping, mapa, auditorías, historia del proyecto
design/          mockups HTML del sistema visual congelado
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
