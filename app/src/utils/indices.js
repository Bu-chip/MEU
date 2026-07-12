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

  idx = { tagIndex, tagsElegibles }
  cache.set(archive, idx)
  return idx
}
