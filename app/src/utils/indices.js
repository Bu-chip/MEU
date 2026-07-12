// Índices en memoria derivados del archivo canónico. Se construyen una
// sola vez por sesión (el objeto archive está cacheado a nivel de módulo
// en useArchive, así que el WeakMap equivale a un singleton perezoso).

// Decisión 8 de Fase 0: universo de GÉNERO AL AZAR = tags con ≥8 releases,
// recalculado en runtime (el «276 estilos» del mockup era del dataset viejo).
export const UMBRAL_ESTILOS = 8

const cache = new WeakMap()

export function getIndices(archive) {
  let idx = cache.get(archive)
  if (idx) return idx

  const tagIndex = new Map()
  for (const album of archive.albums) {
    for (const tag of album.tags) {
      const lista = tagIndex.get(tag)
      if (lista) lista.push(album)
      else tagIndex.set(tag, [album])
    }
  }

  const tagsElegibles = [...tagIndex.keys()].filter(
    (tag) => tagIndex.get(tag).length >= UMBRAL_ESTILOS,
  )

  // Índice de artistas del ARCHIVO: [nombre, nº releases], ordenado como
  // el mockup (case-insensitive), no como archive.artists (orden bruto
  // por codepoint, que separa mayúsculas de minúsculas).
  const conteoArtistas = new Map()
  for (const album of archive.albums) {
    conteoArtistas.set(album.artist, (conteoArtistas.get(album.artist) ?? 0) + 1)
  }
  const artistas = [...conteoArtistas.entries()].sort((x, y) =>
    x[0].toLowerCase().localeCompare(y[0].toLowerCase()),
  )

  // Facetas de género: [género, nº releases] por frecuencia (los null fuera).
  const conteoGeneros = new Map()
  for (const album of archive.albums) {
    if (album.genre) {
      conteoGeneros.set(album.genre, (conteoGeneros.get(album.genre) ?? 0) + 1)
    }
  }
  const generos = [...conteoGeneros.entries()].sort((x, y) => y[1] - x[1])

  // Los id del archivo son estables y únicos pero NO contiguos (0..2395
  // con 32 huecos de bajas históricas): Map, nunca índice de array.
  const byId = new Map(archive.albums.map((a) => [a.id, a]))

  idx = { tagIndex, tagsElegibles, artistas, generos, byId }
  cache.set(archive, idx)
  return idx
}
