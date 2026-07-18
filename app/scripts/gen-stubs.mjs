// Stubs de compartir (F6): una página estática mínima por disco en
// <outdir>/d/:id/index.html cuyo único cometido es que el crawler de
// previews (WhatsApp, iMessage, Telegram, …) lea og:tags propios del
// disco; el humano es redirigido a la ficha real (#/disco/:id).
//
// Convive con el hash router sin tocarlo: la app no enlaza a /d/:id/,
// solo el botón COMPARTIR de la FICHA entrega esa URL. Se ejecuta desde
// deploy.yml tras el rsync del build ("Assemble site"); no forma parte
// del build de Vite ni del dev local.
//
// Determinista e idempotente: la única entrada es el JSON canónico y la
// plantilla es fija (sin timestamps ni aleatoriedad), así que re-ejecutar
// produce bytes idénticos. Los stubs huérfanos de discos dados de baja
// desaparecen solos: el publish hace push --force de un árbol nuevo.
//
// Uso: node app/scripts/gen-stubs.mjs <outdir>

import { mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

// Dominio hardcodeado: los og:tags absolutos son para el crawler en
// producción; un origin de dev aquí no tiene sentido.
const DOMINIO = 'https://mapa.queimadacircuitrecords.com'
const OG_FALLBACK = `${DOMINIO}/og.png` // el og global, 1200×630

// El JSON canónico (data/, única fuente de verdad) vive fuera de app/,
// igual que en useArchive.js.
const CANONICO = resolve(
  dirname(fileURLToPath(import.meta.url)),
  '../../data/bandcamp_bilbaotags_clean.json',
)

// 556 registros llevan & < > " en artist/title/genre: escapado obligatorio
// antes de interpolar en atributos o texto.
function esc(s) {
  return String(s)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
}

// género · año · desde el Mapa — omitiendo los tramos null (45 sin
// género, 23 sin año) en vez de rellenar con marcadores.
function descripcion(album) {
  return [album.genre, album.year, 'desde el Mapa Euskadi Underground']
    .filter(Boolean)
    .join(' · ')
}

// Head calcado del index.html de la app (charset, viewport, lang) pero sin
// fuentes ni favicon: el humano ve esta página <100ms antes del replace y
// el crawler solo quiere los meta. noindex,follow: la URL indexable es la
// ficha, el stub es solo transporte de og:tags.
function stub(album) {
  const url = `${DOMINIO}/d/${album.id}/`
  const titulo = `${esc(album.artist)} — ${esc(album.title)}`
  const desc = esc(descripcion(album))
  const [img, w, h] = album.cover_url
    ? [esc(album.cover_url), 700, 700] // la _5 canónica, sin tratar (el grayscale es CSS)
    : [OG_FALLBACK, 1200, 630] // los 15 sin portada llevan el og global
  return `<!doctype html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>${titulo} · MAPA EUSKADI UNDERGROUND</title>
    <meta name="description" content="${desc}" />
    <meta name="robots" content="noindex,follow" />
    <link rel="canonical" href="${url}" />
    <meta property="og:type" content="music.album" />
    <meta property="og:title" content="${titulo}" />
    <meta property="og:description" content="${desc}" />
    <meta property="og:url" content="${url}" />
    <meta property="og:image" content="${img}" />
    <meta property="og:image:width" content="${w}" />
    <meta property="og:image:height" content="${h}" />
    <meta name="twitter:card" content="summary_large_image" />
    <script>location.replace('/#/disco/${album.id}')</script>
  </head>
  <body>
    <noscript><a href="/#/disco/${album.id}">${titulo} en el Mapa Euskadi Underground</a></noscript>
  </body>
</html>
`
}

const outdir = process.argv[2]
if (!outdir) {
  console.error('uso: node app/scripts/gen-stubs.mjs <outdir>')
  process.exit(1)
}

const { albums } = JSON.parse(readFileSync(CANONICO, 'utf8'))

for (const album of albums) {
  // El id es el nombre del directorio: solo enteros del canónico, nunca
  // texto que pueda escaparse del outdir.
  if (!Number.isInteger(album.id) || album.id < 0) {
    throw new Error(`id inválido en el canónico: ${JSON.stringify(album.id)}`)
  }
  const dir = join(outdir, 'd', String(album.id))
  mkdirSync(dir, { recursive: true })
  writeFileSync(join(dir, 'index.html'), stub(album))
}

console.log(`gen-stubs: ${albums.length} stubs en ${join(outdir, 'd')}/`)
