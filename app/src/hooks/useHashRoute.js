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

export function useHashRoute() {
  const [hash, setHash] = useState(() => window.location.hash)

  useEffect(() => {
    const onChange = () => setHash(window.location.hash)
    window.addEventListener('hashchange', onChange)
    return () => window.removeEventListener('hashchange', onChange)
  }, [])

  return parseRoute(hash)
}
