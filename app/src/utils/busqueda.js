import { GRUPOS_ALIAS } from '../data/tagAliases.js'
import { nodosDe, tieneEstilo } from './estilos.js'

// Búsqueda del ARCHIVO: subcadena sobre un haystack precalculado por álbum
// (artista + título + género + año + tags — la extensión a tags es la que
// da terreno a los alias), insensible a mayúsculas y diacríticos. Si hay
// estilos cargados (mapa de fusión), el haystack lleva también los nodos
// del disco: «post punk» encuentra lo etiquetado «postpunk».

export function normaliza(s) {
  return String(s ?? '')
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
}

// variante normalizada → resto de variantes de su grupo
const ALIAS = new Map()
for (const grupo of GRUPOS_ALIAS) {
  for (const variante of grupo) {
    ALIAS.set(
      normaliza(variante),
      grupo.filter((v) => v !== variante).map(normaliza),
    )
  }
}

// La expansión solo se dispara con igualdad exacta entre la consulta y una
// variante (conservador): «dnb» expande, «dn» no.
export function expandeConsulta(q) {
  const qn = normaliza(q.trim())
  return { qn, equivalentes: ALIAS.get(qn) ?? [] }
}

// archive → { sin: haystacks solo con tags, con: haystacks con nodos }
const cache = new WeakMap()

function getHaystacks(archive, estilos) {
  let porArchivo = cache.get(archive)
  if (!porArchivo) {
    porArchivo = {}
    cache.set(archive, porArchivo)
  }
  const clave = estilos ? 'con' : 'sin'
  if (porArchivo[clave]) return porArchivo[clave]
  const hay = new Map()
  for (const a of archive.albums) {
    const partes = [a.artist, a.title, a.genre ?? '', a.year ?? '', a.tags.join(' ')]
    if (estilos) {
      // el nodo tal cual y sin guiones («post-punk» → «post punk»)
      for (const id of nodosDe(a, estilos.nodoDeTag)) partes.push(id, id.replace(/-/g, ' '))
    }
    hay.set(a.id, normaliza(partes.join(' ')))
  }
  porArchivo[clave] = hay
  return hay
}

// Filtros compartidos por ARCHIVO y MAPA (misma semántica en ambas vistas).
// `desde`/`hasta` acotan por año de publicación, inclusivos; las releases
// sin año quedan fuera en cuanto hay rango, igual que con `anio`.
// `tag` es igualdad exacta con un tag original; `estilo` es un nodo del mapa
// de fusión (todos los discos cuyos tags caen en él). Sin `estilos` cargados
// aún, `estilo` degrada a igualdad exacta.
export function filtra(archive, { artista, genero, anio, desde, hasta, tag, estilo, q }, estilos = null) {
  let rows = archive.albums
  if (artista) rows = rows.filter((r) => r.artist === artista)
  if (genero) rows = rows.filter((r) => r.genre === genero)
  if (anio) rows = rows.filter((r) => r.year === anio)
  if (desde) rows = rows.filter((r) => r.year && r.year >= desde)
  if (hasta) rows = rows.filter((r) => r.year && r.year <= hasta)
  if (tag) rows = rows.filter((r) => r.tags.includes(tag))
  if (estilo) {
    rows = estilos
      ? rows.filter((r) => tieneEstilo(r, estilo, estilos.nodoDeTag))
      : rows.filter((r) => r.tags.includes(estilo))
  }
  if (q && q.trim()) {
    const { qn, equivalentes } = expandeConsulta(q)
    const hay = getHaystacks(archive, estilos)
    rows = rows.filter((r) => {
      const h = hay.get(r.id)
      return h.includes(qn) || equivalentes.some((v) => h.includes(v))
    })
  }
  return rows
}

export function ordena(rows, sortK, sortAsc) {
  const campo = { y: 'year', a: 'artist', t: 'title', g: 'genre' }[sortK]
  return [...rows].sort((A, B) => {
    if (sortK === 'y') {
      const a = A.year || 0
      const b = B.year || 0
      return sortAsc ? a - b : b - a
    }
    const a = (A[campo] || '').toLowerCase()
    const b = (B[campo] || '').toLowerCase()
    return sortAsc ? a.localeCompare(b) : b.localeCompare(a)
  })
}
