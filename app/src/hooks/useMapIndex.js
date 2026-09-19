import { useState, useEffect } from 'react'
// Índice geográfico precalculado en build (scripts/locations.py build):
// ~125 KB, referencias por id del canónico, sin duplicar discos. Se importa
// como asset (hash de contenido) y solo se descarga al abrir el MAPA; una
// vez por sesión, igual que useArchive.
import indexUrl from '../../../data/locations/map_index.json?url'

let cached = null

export function useMapIndex() {
  const [index, setIndex] = useState(cached)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (cached) return
    fetch(indexUrl)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json()
      })
      .then((data) => {
        cached = data
        setIndex(data)
      })
      .catch((err) => setError(err.message))
  }, [])

  return { index, error }
}
