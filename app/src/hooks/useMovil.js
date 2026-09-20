import { useState, useEffect } from 'react'

// MAPA tiene modo móvil propio (mapa acotado + hoja inferior), no una
// versión encogida del de escritorio: hace falta saberlo en JS, no solo en
// CSS. El umbral es el mismo que el de Mapa.css.
export const ANCHO_MOVIL = 760

export function useMovil(ancho = ANCHO_MOVIL) {
  const consulta = `(max-width: ${ancho}px)`
  const [movil, setMovil] = useState(
    () => typeof window !== 'undefined' && window.matchMedia(consulta).matches,
  )
  useEffect(() => {
    const mq = window.matchMedia(consulta)
    const cambia = (e) => setMovil(e.matches)
    mq.addEventListener('change', cambia)
    return () => mq.removeEventListener('change', cambia)
  }, [consulta])
  return movil
}
