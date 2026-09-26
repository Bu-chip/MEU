// «CERCA DE ESTE»: vecinos por estilos compartidos, calculados al vuelo por
// ficha (7.600 × ~6 tags: coste despreciable, nada que precomputar).
// Con el mapa de fusión cargado (nodoDeTag) se comparan nodos, no tags
// crudos: «rocka» y «rock» cuentan como un solo estilo en común, y los
// tags de «resto» (nombres de grupo, sellos) no acercan a nadie. Sin mapa,
// tags crudos tal cual.
// Orden del mockup: solapamiento desc y, a igualdad, año asc (s/f primero).
import { nodosDe } from './estilos.js'

export function similares(albums, album, n = 8, nodoDeTag = null) {
  const claves = (a) => (nodoDeTag ? nodosDe(a, nodoDeTag) : a.tags)
  const propios = new Set(claves(album))
  const candidatos = []
  for (const otro of albums) {
    if (otro.id === album.id) continue
    let ov = 0
    for (const k of claves(otro)) {
      if (propios.has(k)) ov++
    }
    if (ov > 0) candidatos.push([otro, ov])
  }
  candidatos.sort((A, B) => B[1] - A[1] || (A[0].year || 0) - (B[0].year || 0))
  return candidatos.slice(0, n)
}
