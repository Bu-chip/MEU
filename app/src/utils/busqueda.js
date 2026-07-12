import { GRUPOS_ALIAS } from '../data/tagAliases.js'

// Búsqueda del ARCHIVO: subcadena sobre un haystack precalculado por álbum
// (artista + título + género + año + tags — la extensión a tags es la que
// da terreno a los alias), insensible a mayúsculas y diacríticos.

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

const cache = new WeakMap()

function getHaystacks(archive) {
  let hay = cache.get(archive)
  if (hay) return hay
  hay = new Map()
  for (const a of archive.albums) {
    hay.set(
      a.id,
      normaliza(
        [a.artist, a.title, a.genre ?? '', a.year ?? '', a.tags.join(' ')].join(' '),
      ),
    )
  }
  cache.set(archive, hay)
  return hay
}

export function filtra(archive, { artista, genero, anio, tag, q }) {
  let rows = archive.albums
  if (artista) rows = rows.filter((r) => r.artist === artista)
  if (genero) rows = rows.filter((r) => r.genre === genero)
  if (anio) rows = rows.filter((r) => r.year === anio)
  if (tag) rows = rows.filter((r) => r.tags.includes(tag))
  if (q && q.trim()) {
    const { qn, equivalentes } = expandeConsulta(q)
    const hay = getHaystacks(archive)
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
