import { useState, useEffect } from 'react'
// El JSON canónico (data/, única fuente de verdad) se importa como asset:
// Vite lo emite en dist/assets con hash de contenido, sin duplicarlo en el
// repo. Un solo fetch por sesión, caché a nivel de módulo compartida por
// todas las pantallas (patrón useGenres de genre-explorer).
import dataUrl from '../../../data/bandcamp_bilbaotags_clean.json?url'

let cached = null

export function useArchive() {
  const [archive, setArchive] = useState(cached)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (cached) return

    fetch(dataUrl)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json()
      })
      .then((data) => {
        cached = data
        setArchive(data)
      })
      .catch((err) => setError(err.message))
  }, [])

  return { archive, error }
}
