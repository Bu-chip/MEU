import { useState, useEffect } from 'react'

// Router hash artesanal (patrón genre-explorer: deep-links por hash, sin
// librería). Esquema acordado en Fase 0:
//   #/                → EXPLORAR
//   #/archivo?q=…     → ARCHIVO con filtros compartibles
//   #/disco/:id       → FICHA (id del JSON como clave estable)
// Cualquier hash desconocido cae en EXPLORAR.
export function parseRoute(hash) {
  const raw = hash.replace(/^#/, '')
  const [path, query = ''] = raw.split('?')
  const params = new URLSearchParams(query)

  const disco = path.match(/^\/disco\/(\d+)$/)
  if (disco) return { page: 'disco', id: Number(disco[1]), params }
  if (path === '/archivo') return { page: 'archivo', id: null, params }
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
export function hashArchivo({ q, genero, anio, tag, artista } = {}) {
  const params = new URLSearchParams()
  if (q && q.trim()) params.set('q', q.trim())
  if (genero) params.set('genero', genero)
  if (anio) params.set('anio', String(anio))
  if (tag) params.set('tag', tag)
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
