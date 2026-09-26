import { useState, useEffect } from 'react'

// Router hash artesanal (patrón genre-explorer: deep-links por hash, sin
// librería). Esquema acordado en Fase 0:
//   #/                → EXPLORAR
//   #/archivo?q=…     → ARCHIVO con filtros compartibles
//   #/disco/:id       → FICHA (id del JSON como clave estable)
//   #/sobre           → SOBRE (texto fijo del proyecto)
//   #/proponer        → PROPONER (sugerir un disco/grupo/sello; sin backend)
//   #/entrar          → ENTRAR (login opcional; solo si hay Supabase)
//   #/coleccion       → COLECCIÓN (los guardados; pide sesión)
//   #/mapa[/:lugar]?… → MAPA con los mismos filtros que ARCHIVO + rango de
//                       años, territorio y procedencia (utils/mapa.js)
// Cualquier hash desconocido cae en EXPLORAR.
export function parseRoute(hash) {
  const raw = hash.replace(/^#/, '')
  const [path, query = ''] = raw.split('?')
  const params = new URLSearchParams(query)

  const disco = path.match(/^\/disco\/(\d+)$/)
  if (disco) return { page: 'disco', id: Number(disco[1]), params }
  if (path === '/archivo') return { page: 'archivo', id: null, params }
  const mapa = path.match(/^\/mapa(?:\/([a-z0-9-]+))?\/?$/)
  if (mapa) return { page: 'mapa', id: null, lugar: mapa[1] ?? null, params }
  if (path === '/sobre') return { page: 'sobre', id: null, params }
  if (path === '/proponer') return { page: 'proponer', id: null, params }
  if (path === '/entrar') return { page: 'entrar', id: null, params }
  if (path === '/coleccion') return { page: 'coleccion', id: null, params }
  return { page: 'explorar', id: null, params }
}

// Navegación con entrada en el historial (clicks discretos: facetas,
// artista, chips) — el botón atrás deshace el gesto.
export function navegar(hash) {
  window.location.hash = hash
}

// Sustitución sin entrada en el historial (tecleo en la búsqueda): la URL
// sigue siendo compartible pero atrás no repasa cada pulsación. Safari
// además ratelimita replaceState, de ahí el debounce en quien llama.
export function reemplazar(hash) {
  const url = new URL(window.location.href)
  url.hash = hash
  window.history.replaceState(null, '', url)
  window.dispatchEvent(new HashChangeEvent('hashchange'))
}

// Construye #/archivo?… con los filtros no vacíos (esquema de Fase 0).
// desde/hasta (rango de años) llegan sobre todo desde el MAPA («ver en
// archivo»): mismo filtro compartido en busqueda.filtra. `estilo` es un nodo
// del mapa de fusión de tags; `tag` sigue siendo el tag original exacto.
export function hashArchivo({ q, genero, anio, desde, hasta, tag, estilo, artista } = {}) {
  const params = new URLSearchParams()
  if (q && q.trim()) params.set('q', q.trim())
  if (genero) params.set('genero', genero)
  if (anio) params.set('anio', String(anio))
  if (desde) params.set('desde', String(desde))
  if (hasta) params.set('hasta', String(hasta))
  if (tag) params.set('tag', tag)
  if (estilo) params.set('estilo', estilo)
  if (artista) params.set('artista', artista)
  const qs = params.toString()
  return qs ? `#/archivo?${qs}` : '#/archivo'
}

export function useHashRoute() {
  const [hash, setHash] = useState(() => window.location.hash)

  useEffect(() => {
    const onChange = () => setHash(window.location.hash)
    window.addEventListener('hashchange', onChange)
    return () => window.removeEventListener('hashchange', onChange)
  }, [])

  return parseRoute(hash)
}
