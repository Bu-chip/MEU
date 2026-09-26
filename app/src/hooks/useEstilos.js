import { useState, useEffect, useMemo } from 'react'
import { preparaEstilos } from '../utils/estilos.js'
// Índice de estilos precalculado (scripts/tag_merge_map.py): ~110 KB, los
// nodos del mapa de fusión con sus tags. Se importa como asset (hash de
// contenido) y se descarga una vez por sesión, igual que useArchive.
import nodesUrl from '../../../data/derived/tag_nodes.json?url'

let cached = null
// Índices por archivo (WeakMap ≈ singleton perezoso, como getIndices).
const preparados = new WeakMap()

// Devuelve { estilos, error }: estilos es null hasta que llegan el mapa y el
// archivo; después, los índices de utils/estilos.preparaEstilos.
export function useEstilos(archive) {
  const [mapa, setMapa] = useState(cached)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (cached) return
    fetch(nodesUrl)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json()
      })
      .then((data) => {
        cached = data
        setMapa(data)
      })
      .catch((err) => setError(err.message))
  }, [])

  const estilos = useMemo(() => {
    if (!mapa || !archive) return null
    let est = preparados.get(archive)
    if (!est) {
      est = preparaEstilos(mapa, archive)
      preparados.set(archive, est)
    }
    return est
  }, [mapa, archive])

  return { estilos, error }
}
