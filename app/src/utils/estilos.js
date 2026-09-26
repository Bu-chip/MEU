// Estilos: los nodos del mapa de fusión de tags (data/derived/tag_nodes.json,
// generado por scripts/tag_merge_map.py a partir del canónico; método en
// docs/tag-merge-map.md). Cada tag original de Bandcamp apunta a un nodo:
// «post-punk», «postpunk» y «post punk» son el mismo estilo; «rocka» y
// «rock vasco» caen en «rock»; los lugares van a «lugar:*» y formatos,
// idiomas e instrumentos a «otro:*». Lo que no es navegable (nombres de
// grupo, sellos, palabras sueltas) cae en «resto».
//
// Esta capa no muta data/ ni el archivo: los tags originales siguen en
// cada disco. Solo añade una lectura fusionada encima.
import { UMBRAL_ESTILOS } from './indices.js'

export const RESTO = 'resto'
export const OTROS_GENEROS = 'otros géneros'

// Nodos de un disco en el orden de sus tags, sin repetir y sin «resto».
// Un tag que el mapa no conoce (catálogo más nuevo que el mapa) se conserva
// tal cual como nodo propio: no se pierde, solo queda sin fusionar.
export function nodosDe(album, nodoDeTag) {
  const vistos = new Set()
  const out = []
  for (const tag of album.tags) {
    const id = nodoDeTag.get(tag) ?? tag
    if (id === RESTO || vistos.has(id)) continue
    vistos.add(id)
    out.push(id)
  }
  return out
}

// Construye los índices de estilos sobre el archivo cargado. Los recuentos
// se calculan aquí, no se leen del JSON, para que sigan vivos si el catálogo
// cambia antes de regenerar el mapa.
//   nodoDeTag  Map tag original → id de nodo
//   nodos      Map id → { id, grupo, padre }
//   nodoIndex  Map id → releases (cada disco una sola vez por nodo)
//   elegibles  ids de género con ≥ UMBRAL_ESTILOS releases, por frecuencia:
//              el universo de GÉNERO AL AZAR y de la faceta ESTILO
export function preparaEstilos(mapa, archive) {
  const nodoDeTag = new Map()
  const nodos = new Map()
  for (const n of mapa.nodos) {
    nodos.set(n.id, { id: n.id, grupo: n.grupo, padre: n.padre ?? null })
    for (const tag of n.tags) nodoDeTag.set(tag, n.id)
  }

  const nodoIndex = new Map()
  for (const album of archive.albums) {
    for (const id of nodosDe(album, nodoDeTag)) {
      const lista = nodoIndex.get(id)
      if (lista) lista.push(album)
      else nodoIndex.set(id, [album])
    }
  }

  const elegibles = [...nodoIndex.keys()]
    .filter(
      (id) =>
        nodos.get(id)?.grupo === 'genero' &&
        id !== OTROS_GENEROS &&
        nodoIndex.get(id).length >= UMBRAL_ESTILOS,
    )
    .sort((a, b) => nodoIndex.get(b).length - nodoIndex.get(a).length || a.localeCompare(b))

  return { nodoDeTag, nodos, nodoIndex, elegibles }
}

// ¿El disco cae en este estilo? Vale para cualquier nodo (género, lugar:*,
// otro:*) y para un tag desconocido (se compara tal cual).
export function tieneEstilo(album, estilo, nodoDeTag) {
  for (const tag of album.tags) {
    if ((nodoDeTag.get(tag) ?? tag) === estilo) return true
  }
  return false
}

// Texto visible de un nodo: sin el prefijo de grupo («lugar:bilbo» → «bilbo»).
export function etiqueta(id) {
  return String(id).replace(/^(lugar|otro):/, '')
}
