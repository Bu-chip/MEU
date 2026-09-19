// Lógica pura de la vista MAPA (sin React, testeable con `node --test`).
//
// El MAPA no tiene filtros propios: aplica los MISMOS de ARCHIVO
// (busqueda.filtra: texto con alias, género, tag, artista, años) y después
// agrupa el resultado por municipio con el índice geográfico precalculado
// en build (data/locations/map_index.json, scripts/locations.py build).
//
// Lo que el mapa NO afirma: la ubicación es la que Bandcamp da hoy a la
// cuenta que publica (grupo o sello). Filtrar por año filtra releases, no
// reconstruye dónde vivía nadie ese año.

import { filtra } from './busqueda.js'

// Procedencias activables. Cada código agrupa tipos de resolución.
// `manual` va con las directas: es una decisión humana verificada.
export const PROCEDENCIAS = [
  { code: 'd', tipos: ['direct', 'manual'], label: 'directas', ayuda: 'Bandcamp, esta release (o decisión manual)' },
  { code: 'c', tipos: ['same_account'], label: 'misma cuenta', ayuda: 'Bandcamp, otra release de la misma cuenta' },
  { code: 'a', tipos: ['artist_inferred'], label: 'inferidas por artista', ayuda: 'el mismo artista en su propia cuenta' },
  { code: 't', tipos: ['tag_hint'], label: 'pistas de tag', ayuda: 'solo un tag geográfico: la más débil' },
]
export const UBIC_DEFECTO = 'dca'
export const TIPOS_FIABLES = new Set(['direct', 'manual', 'same_account'])

const normUbic = (s) =>
  PROCEDENCIAS.map((p) => p.code)
    .filter((c) => (s ?? UBIC_DEFECTO).includes(c))
    .join('')

// ── URL ────────────────────────────────────────────────────────────────
// #/mapa[/<lugar>]?q&genero&tag&artista&desde&hasta&territorio&ubic
// Se aceptan también from/to (alias en inglés) al leer; se escribe desde/hasta.

const anio = (v) => {
  const n = Number(v)
  return Number.isInteger(n) && n > 1900 && n < 2100 ? n : null
}

export function leeFiltrosMapa(route) {
  const p = route.params
  return {
    lugar: route.lugar ?? null,
    q: p.get('q') ?? '',
    genero: p.get('genero'),
    tag: p.get('tag'),
    artista: p.get('artista'),
    desde: anio(p.get('desde') ?? p.get('from')),
    hasta: anio(p.get('hasta') ?? p.get('to')),
    territorio: p.get('territorio'),
    ubic: normUbic(p.get('ubic')),
  }
}

export function hashMapa({ lugar, q, genero, tag, artista, desde, hasta, territorio, ubic } = {}) {
  const params = new URLSearchParams()
  if (q && q.trim()) params.set('q', q.trim())
  if (genero) params.set('genero', genero)
  if (tag) params.set('tag', tag)
  if (artista) params.set('artista', artista)
  if (desde) params.set('desde', String(desde))
  if (hasta) params.set('hasta', String(hasta))
  if (territorio) params.set('territorio', territorio)
  const u = normUbic(ubic)
  if (u !== UBIC_DEFECTO) params.set('ubic', u || '-')
  const qs = params.toString()
  const path = lugar ? `#/mapa/${lugar}` : '#/mapa'
  return qs ? `${path}?${qs}` : path
}

// ── Índice geográfico ─────────────────────────────────────────────────
// Se expande una vez por sesión (WeakMap sobre el objeto cargado):
// Map id → {place, type, region, flags} y lugares con su índice.

const cacheGeo = new WeakMap()

export function preparaGeo(index) {
  let geo = cacheGeo.get(index)
  if (geo) return geo
  const places = index.places.map(([id, name, x, y, t, alt], i) => ({
    i, id, name, x, y, territorio: index.territories[t], alt,
  }))
  const r = index.releases
  const rel = new Map()
  for (let k = 0; k < r.id.length; k++) {
    rel.set(r.id[k], {
      place: r.place[k],
      type: index.types[r.type[k]],
      region: r.region[k] >= 0 ? index.regions[r.region[k]] : null,
      flags: r.flags[k],
    })
  }
  geo = {
    places,
    placeById: new Map(places.map((p) => [p.id, p])),
    rel,
    grid: index.grid,
    territories: index.territories,
    geoTags: new Set(index.geo_tags ?? []),
  }
  cacheGeo.set(index, geo)
  return geo
}

// ── Agregación ────────────────────────────────────────────────────────

// Reparte releases ya filtradas entre municipios y huecos. Cuenta todo:
// nada se oculta sin decirlo.
export function agrega(rows, geo, { ubic = UBIC_DEFECTO, territorio = null } = {}) {
  const activos = new Set(PROCEDENCIAS.filter((p) => ubic.includes(p.code)).flatMap((p) => p.tipos))
  const porLugar = new Map()
  const cuenta = {
    filtradas: rows.length,
    localizadas: 0,
    otroTerritorio: 0,
    ocultasProcedencia: 0,
    region_only: 0,
    outside_scope: 0,
    unresolved: 0,
    tag_hint: 0,
  }
  for (const a of rows) {
    const g = geo.rel.get(a.id)
    const type = g?.type ?? 'unresolved'
    if (g && g.place >= 0) {
      if (!activos.has(type)) {
        if (type === 'tag_hint') cuenta.tag_hint++
        else cuenta.ocultasProcedencia++
        continue
      }
      const p = geo.places[g.place]
      if (territorio && p.territorio !== territorio) {
        cuenta.otroTerritorio++
        continue
      }
      cuenta.localizadas++
      const lista = porLugar.get(g.place)
      if (lista) lista.push(a)
      else porLugar.set(g.place, [a])
    } else if (type === 'region_only' || type === 'outside_scope') {
      cuenta[type]++
    } else {
      cuenta.unresolved++
    }
  }
  cuenta.sinMunicipio = cuenta.region_only + cuenta.outside_scope + cuenta.unresolved + cuenta.tag_hint
  return { porLugar, cuenta }
}

export function rankingLugares(porLugar, geo) {
  return [...porLugar.entries()]
    .map(([i, rows]) => ({ lugar: geo.places[i], n: rows.length, rows }))
    .sort((x, y) => y.n - x.n || x.lugar.name.localeCompare(y.lugar.name))
}

// ── Métricas del panel ────────────────────────────────────────────────

// Sobrerrepresentación de un tag en un conjunto respecto al archivo entero:
// (con el tag en el lugar / releases del lugar) ÷ (con el tag en el
// archivo / releases del archivo). Misma métrica y umbrales que
// scripts/locations_lib.py (MIN_LOCAL, MIN_GLOBAL).
export const MIN_LOCAL = 3
export const MIN_GLOBAL = 10

export function lift(nLugar, totalLugar, nGlobal, totalGlobal) {
  if (!totalLugar || !nGlobal || !totalGlobal) return 0
  return nLugar / totalLugar / (nGlobal / totalGlobal)
}

function cuentaTags(rows, excluir) {
  const c = new Map()
  for (const a of rows) {
    for (const t of new Set(a.tags)) {
      if (excluir?.has(t)) continue
      c.set(t, (c.get(t) ?? 0) + 1)
    }
  }
  return c
}

export function tagsPrincipales(rows, { limite = 8, excluir } = {}) {
  return [...cuentaTags(rows, excluir).entries()]
    .sort((x, y) => y[1] - x[1] || x[0].localeCompare(y[0]))
    .slice(0, limite)
}

// tagIndex: Map tag → releases del archivo (getIndices).
export function sobrerrepresentados(rows, tagIndex, totalGlobal, { limite = 8, excluir, minLocal = MIN_LOCAL, minGlobal = MIN_GLOBAL } = {}) {
  const out = []
  for (const [t, n] of cuentaTags(rows, excluir)) {
    const nGlobal = tagIndex.get(t)?.length ?? 0
    if (n < minLocal || nGlobal < minGlobal) continue
    out.push([t, n, lift(n, rows.length, nGlobal, totalGlobal)])
  }
  return out.sort((x, y) => y[2] - x[2] || y[1] - x[1] || x[0].localeCompare(y[0])).slice(0, limite)
}

const fold = (s) =>
  String(s ?? '')
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]/g, '')

export function resumenLugar(rows, geo) {
  const porTipo = {}
  let sello = 0
  let min = null
  let max = null
  const artistas = new Map()
  for (const a of rows) {
    const g = geo.rel.get(a.id)
    porTipo[g.type] = (porTipo[g.type] ?? 0) + 1
    if (g.flags & 1) sello++
    if (a.year) {
      min = min === null ? a.year : Math.min(min, a.year)
      max = max === null ? a.year : Math.max(max, a.year)
    }
    const k = fold(a.artist)
    const prev = artistas.get(k)
    if (prev) prev.n++
    else artistas.set(k, { nombre: a.artist, n: 1 })
  }
  return {
    releases: rows.length,
    artistas: [...artistas.values()].sort((x, y) => y.n - x.n || x.nombre.localeCompare(y.nombre)),
    anios: min === null ? null : [min, max],
    porTipo,
    sello,
  }
}

// Aplica los filtros compartidos + agrega. Punto único que usan la página
// y los tests.
export function consultaMapa(archive, geo, filtros) {
  const rows = filtra(archive, filtros)
  return { rows, ...agrega(rows, geo, filtros) }
}

// Caché de consultas por archivo (patrón de getIndices): mover el mapa,
// abrir un municipio o volver atrás no recalcula filtros ya vistos. LRU
// pequeño: cada entrada son referencias a releases, no copias.
const cacheConsultas = new WeakMap()
const MAX_CONSULTAS = 40

export function consultaCacheada(archive, geo, filtros) {
  let m = cacheConsultas.get(archive)
  if (!m) {
    m = new Map()
    cacheConsultas.set(archive, m)
  }
  const k = JSON.stringify(filtros)
  let r = m.get(k)
  if (r) return r
  r = consultaMapa(archive, geo, filtros)
  m.set(k, r)
  if (m.size > MAX_CONSULTAS) m.delete(m.keys().next().value)
  return r
}
