// «CERCA DE ESTE»: vecinos por tags compartidos, calculados al vuelo por
// ficha (2.364 × ~6 tags: coste despreciable, nada que precomputar).
// Orden del mockup: solapamiento desc y, a igualdad, año asc (s/f primero).
export function similares(albums, album, n = 8) {
  const propios = new Set(album.tags)
  const candidatos = []
  for (const otro of albums) {
    if (otro.id === album.id) continue
    let ov = 0
    for (const tag of otro.tags) {
      if (propios.has(tag)) ov++
    }
    if (ov > 0) candidatos.push([otro, ov])
  }
  candidatos.sort((A, B) => B[1] - A[1] || (A[0].year || 0) - (B[0].year || 0))
  return candidatos.slice(0, n)
}
