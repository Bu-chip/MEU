# Método de scraping de Bandcamp — MEU

Documento de replicabilidad: qué canales de Bandcamp funcionan para
descubrir y fichar releases, verificado empíricamente por el sondeo GATE
de la Fase 2 de expansión del catálogo (`scripts/probe_tag_pages.py`,
**12 de julio de 2026**, runs de Actions 29197223469 / 29197367346 /
29197512210, 23 requests en total a 1 req/2s con User-Agent de
navegador desde runners de GitHub).

> **Advertencia de caducidad**: `discover_web` es una API interna de
> Bandcamp, sin contrato público ni versionado garantizado. Puede
> cambiar o desaparecer sin aviso, igual que le pasó al sistema de tags
> clásico (abajo). Todo scraper debe fallar ruidosamente (log claro,
> exit limpio, sin reintentos ciegos) si la forma de la respuesta deja
> de coincidir, y este documento debe actualizarse con cada cambio
> observado.

## Lo que ya NO funciona (verificado 2026-07)

- **`bandcamp.com/tag/<slug>`**: redirige (302) a
  `bandcamp.com/discover/<slug>`. Las páginas de hub de tag con
  `<div id="pagedata" data-blob="...">` ya no existen.
- **`POST bandcamp.com/api/hub/2/dig_deeper`**: responde
  `{error, error_message}`. El endpoint de paginación de los hubs está
  retirado.
- **Todo el HTML de `bandcamp.com`** (www: `/discover/*`, `/search?q=`)
  sirve un shell anti-bot **"Client Challenge"** de ~3 KB que exige
  ejecutar JavaScript. La búsqueda clásica — el canal del que salió el
  dataset original, reconocible por la cola `?from=search&search_sig=`
  de sus URLs — está muerta como canal de scraping sin navegador.

## Canal vivo 1: API del Discover (descubrimiento por tag)

`POST https://bandcamp.com/api/discover/1/discover_web` — responde JSON
sin desafío ni autenticación (mismos headers de navegador que el resto).

Body verificado:

```json
{
    "tag_norm_names": ["bilbao"],
    "include_result_types": ["a", "s"],
    "category_id": 0,
    "geoname_id": 0,
    "slice": "new",
    "cursor": "*",
    "size": 20
}
```

- `tag_norm_names`: el slug del tag. **La ñ funciona tal cual**
  (`"iruña"` devuelve resultados; no hace falta transliterar).
- `slice`: `"new"` ordena por fecha de publicación descendente (el
  adecuado para pasadas incrementales).
- `cursor`: `"*"` para la primera página; después, el valor `cursor` de
  la respuesta anterior. Paginación verificada (20 items/página con
  `size: 20`, sin repeticiones entre páginas).

Respuesta (claves top-level): `results`, `result_count` (total del tag),
`batch_result_count`, `cursor`, `discover_spec_id`,
`is_following_discover_spec`.

Mapeo de cada item de `results` a nuestro esquema:

| Campo Bandcamp | Campo MEU | Nota |
|---|---|---|
| `item_url` | `url` | cortar `?from=discover_page` (step `clean_urls`) |
| `item_id` | `album_id` | mismo id que `bc-page-properties` de la ficha |
| `band_name` | `artist` | `album_artist` puede afinarlo si no es null |
| `title` | `title` | |
| `release_date` | `year` | `"2026-07-09 20:32:40 UTC"` → año |
| `primary_image.image_id` | `cover_url` | derivable: `https://f4.bcbits.com/img/a{image_id}_5.jpg` (verificado: coincide con el `og:image` de la ficha) |
| `band_location` | — | señal anti-falsos-positivos territoriales; no está en el esquema canónico pero se guarda en los candidatos |
| `item_type` | — | `a` = album, `t` = track; `include_result_types` `"s"` cubre singles |

Lo que el listado **no** da: la lista de tags del álbum ni el género
textual (`band_genre_id` es numérico y del artista, no del release).
Para tags hay que visitar la ficha.

**El listado por tag no es exhaustivo** (verificado el 2026-09-26). La
cuenta `fontso` (Bilbao) publica 9 álbumes; los 9 llevan el tag
`Bilbao` en su ficha, pero el canónico solo tenía uno, y el tag
`bilbao` figura como agotado en `discovery_state.json` (146 páginas).
El listado de `discover_web` para un tag omite releases que sí lo
llevan; no sabemos con qué criterio. Por eso existe el canal 3.

### `geoname_id`: filtro por ubicación, probado y descartado

El body acepta `geoname_id` (el id de GeoNames que usa el filtro de
ubicación del Discover). El id de un lugar se obtiene de
`POST https://bandcamp.com/api/location/1/geoname_search` con
`{"q": "Bilbao", "n": 5, "geocoder_fallback": true}` → Bilbao es
`3128026`. Sondeo del 2026-09-26 con `tag_norm_names: []` y
`geoname_id: 3128026`:

- `result_count: 281` (paginado entero), de solo **86 cuentas**, cuando
  el canónico ubica 772 cuentas en Bilbo. Con `tag_norm_names:
  ["bilbao"]` y el mismo geoname salen 273; sin geoname, 2.666.
- El más reciente es de 2026-05, cuando el tag `bilbao` tiene discos de
  2026-09 con `band_location` «Bilbao, Spain».
- Devuelve merch (`item_type: "p"`) pese a `include_result_types:
  ["a", "s"]`.
- Contra el canónico: 276 ya estaban, 2 estaban rechazados y los 3
  restantes eran camisetas. **Cero discos nuevos.**

El índice por ubicación del Discover cubre una fracción pequeña y
sesgada de las cuentas; no sirve como canal de descubrimiento.

## Canal vivo 2: fichas de álbum (metadatos completos)

Las páginas `https://<artista>.bandcamp.com/album/<slug>` **no** están
tras el Client Challenge (verificado en una ficha veterana del canónico
y en una publicada en 2026). El método de `scripts/scrape_covers.py`
sigue vigente:

- `<meta property="og:image">` → `cover_url`.
- `<meta name="bc-page-properties">` → JSON con `item_id` (= `album_id`)
  e `item_type`.
- Tags visibles: `<a class="tag" href="...">nombre</a>` — incluyen los
  territoriales; el último suele ser la location del artista con
  mayúscula inicial (p. ej. `Bilbao`, `Zarautz`).
- Fecha: texto `released <Month> <D>, <YYYY>` en la página.
- `data-tralbum="..."` sigue presente (JSON completo del release,
  fuente alternativa si las metas cambiaran).

## Canal vivo 3: discografía de una cuenta (`/music`)

`https://<cuenta>.bandcamp.com/music` (o `https://<dominio>/music` en
cuentas con dominio propio) no está tras el Client Challenge (verificado
el 2026-09-26 en cinco cuentas de Bilbo y una de dominio propio). Lo usa
`scripts/discover_accounts.py`:

- Rejilla: `<li data-item-id="album-<id>">` / `"track-<id>"` con un
  `<a href="/album/<slug>">` dentro. En cuentas de sello el `href` puede
  ser absoluto hacia el subdominio del grupo, con `?label=…&tab=music`.
- Discografías largas: el resto de la rejilla viaja en
  `data-client-items="…"` (JSON con `id`, `type`, `page_url`, `title`).
- Cuenta de un solo lanzamiento: `/music` sirve directamente la ficha;
  se reconoce por `bc-page-properties` + `og:url`.
- Ubicación de la cuenta: `<span class="location …">Bilbao, Spain</span>`.
- En la ficha, `data-tralbum` da `artist`, `current.title` y
  `current.release_date` (`"14 Feb 1998 00:00:00 GMT"`).

Solo se proponen álbumes: el canónico no tiene temas sueltos
(`/track/`), que se cuentan en el estado pero no entran.

## Condiciones operativas (sin cambios desde el scrape de portadas)

- User-Agent de navegador de escritorio: los UA por defecto de
  urllib/requests reciben 403.
- Rate limit **1 request / 1,5–2 s** y presupuesto explícito de
  requests por pasada; concurrency group compartido entre workflows
  para que nunca haya dos scrapes simultáneos.
- Desde runners de GitHub Actions no se observó ningún bloqueo con
  estas condiciones. Desde otros orígenes (p. ej. fetchers de
  datacenter identificados como bots) Bandcamp devuelve 403.

## Canario

`scripts/probe_tag_pages.py` (workflow `probe-tag-pages.yml`,
`workflow_dispatch`, ≤10 requests) verifica en ~1 minuto si el Client
Challenge se ha extendido a la API del Discover o a las fichas de
álbum. Ejecutarlo antes de cualquier pasada grande y ante cualquier
racha de errores inexplicada del scraper.
