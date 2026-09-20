// Tests de la lógica del MAPA: `npm test` (node --test, sin dependencias).
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { parseRoute } from '../hooks/useHashRoute.js'
import { filtra } from './busqueda.js'
import {
  leeFiltrosMapa, hashMapa, preparaGeo, agrega, consultaMapa, rankingLugares,
  lift, sobrerrepresentados, resumenLugar, UBIC_DEFECTO, procedenciaDe, etiquetasPrioritarias,
  maxEtiquetas, encajaVista,
} from './mapa.js'

// Índice mínimo con la misma forma que data/locations/map_index.json.
const INDEX = {
  territories: ['Bizkaia', 'Gipuzkoa', 'Araba', 'Nafarroa', 'Iparralde'],
  types: ['direct', 'same_account', 'artist_inferred', 'manual', 'tag_hint', 'region_only', 'outside_scope', 'unresolved'],
  regions: [['euskal-herria', 'Euskal Herria', 'country', null]],
  grid: { top: 43.5, left: -3.5, cell_lat: 0.045, cell_lon: 0.06, rows: 2, cols: 2, cells: [] },
  places: [
    ['bilbo', 'Bilbo', 10, 5, 0, 'Bilbao'],
    ['zarautz', 'Zarautz', 20, 5, 1, 'Zarauz'],
    ['irunea', 'Iruñea', 30, 20, 3, 'Pamplona'],
  ],
  geo_tags: ['bilbao'],
  accounts: [['grupo', 0], ['sello', 1]],
  releases: {
    //     1  2  3  4  5  6  7  8  (2 = same_account desde cuenta multiartista)
    id: [1, 2, 3, 4, 5, 6, 7, 8],
    place: [0, 0, 1, 1, 2, -1, -1, 0],
    type: [0, 1, 0, 2, 0, 5, 6, 4],
    region: [-1, -1, -1, -1, -1, 0, -1, -1],
    flags: [0, 1, 0, 0, 0, 0, 0, 0],
    account: [0, 1, 0, 0, 0, 0, 0, 0],
  },
}

const alb = (id, artist, year, tags, genre = null) => ({ id, artist, title: 't' + id, year, tags, genre, url: '', album_id: id })
const ARCHIVE = {
  albums: [
    alb(1, 'Kaos', 2005, ['noise', 'bilbao']),
    alb(2, 'Kaos', 2011, ['noise']),
    alb(3, 'Zirt', 2008, ['hardcore', 'noise']),
    alb(4, 'Zart', 2015, ['ambient']),
    alb(5, 'Iru', 2009, ['hardcore']),
    alb(6, 'Region', 2010, ['noise']),
    alb(7, 'Fuera', 2012, ['noise']),
    alb(8, 'Pista', 2006, ['noise', 'bilbao']),
    alb(9, 'Nuevo', 2020, ['noise']), // no está en el índice: sin resolver
  ],
}
const geo = preparaGeo(INDEX)
const ruta = (hash) => parseRoute(hash)

test('rutas del mapa', () => {
  assert.deepEqual([ruta('#/mapa').page, ruta('#/mapa').lugar], ['mapa', null])
  const r = ruta('#/mapa/zarautz?tag=noise&desde=2005&hasta=2012')
  assert.equal(r.page, 'mapa')
  assert.equal(r.lugar, 'zarautz')
  const f = leeFiltrosMapa(r)
  assert.equal(f.tag, 'noise')
  assert.equal(f.desde, 2005)
  assert.equal(f.hasta, 2012)
  assert.equal(f.ubic, UBIC_DEFECTO)
  assert.equal(ruta('#/archivo').page, 'archivo', 'ARCHIVO no cambia')
  assert.equal(ruta('#/mapa/Mal Formado').page, 'explorar', 'un lugar no válido no inventa ruta')
})

test('alias from/to al leer, desde/hasta al escribir, ida y vuelta estable', () => {
  const f = leeFiltrosMapa(ruta('#/mapa?tag=noise&from=2005&to=2012'))
  assert.deepEqual([f.desde, f.hasta], [2005, 2012])
  const h = hashMapa({ ...f, lugar: 'bilbo', territorio: 'Bizkaia', ubic: 'dcat' })
  assert.equal(h, '#/mapa/bilbo?tag=noise&desde=2005&hasta=2012&territorio=Bizkaia&ubic=dcat')
  assert.deepEqual(leeFiltrosMapa(ruta(h)), { ...f, lugar: 'bilbo', territorio: 'Bizkaia', ubic: 'dcat' })
  assert.equal(hashMapa({ ubic: UBIC_DEFECTO }), '#/mapa', 'la procedencia por defecto no ensucia la URL')
  assert.equal(hashMapa({ ubic: '' }), '#/mapa?ubic=-')
  assert.equal(leeFiltrosMapa(ruta('#/mapa?ubic=-')).ubic, '')
})

test('rango de años en el filtro compartido con ARCHIVO', () => {
  const ids = filtra(ARCHIVE, { desde: 2006, hasta: 2010 }).map((a) => a.id)
  assert.deepEqual(ids, [3, 5, 6, 8])
  assert.deepEqual(filtra(ARCHIVE, { anio: 2011 }).map((a) => a.id), [2], 'anio sigue igual')
})

test('procedencia: same_account se parte según la cuenta', () => {
  assert.equal(procedenciaDe(geo.rel.get(1)), 'd')
  assert.equal(procedenciaDe(geo.rel.get(2)), 'm', 'misma cuenta, pero multiartista')
  assert.equal(procedenciaDe(geo.rel.get(4)), 'a')
  assert.equal(procedenciaDe(geo.rel.get(8)), 't')
  assert.equal(procedenciaDe(geo.rel.get(6)), null)
})

test('escenario D por defecto: fuera lo inferido desde cuentas multiartista', () => {
  const { porLugar, cuenta } = agrega(ARCHIVE.albums, geo)
  assert.equal(UBIC_DEFECTO, 'dca')
  assert.deepEqual(porLugar.get(0).map((a) => a.id), [1], 'la 2 (cuenta multiartista) no entra')
  assert.equal(cuenta.localizadas, 4)
  assert.equal(cuenta.m, 1, 'contada aunque no se pinte')
  assert.equal(cuenta.t, 1)
  assert.equal(cuenta.excluidas, 2)
  assert.equal(cuenta.region_only, 1)
  assert.equal(cuenta.outside_scope, 1)
  assert.equal(cuenta.unresolved, 1, 'una release que falta en el índice cuenta como sin resolver')
  assert.equal(cuenta.sinMunicipio, 3)
  assert.equal(cuenta.localizadas + cuenta.fuera, ARCHIVE.albums.length, 'nada se pierde sin contar')
})

test('agregación: activar multiartista y pistas de tag, quitar inferidas, territorio', () => {
  let r = agrega(ARCHIVE.albums, geo, { ubic: 'dcamt' })
  assert.deepEqual(r.porLugar.get(0).map((a) => a.id), [1, 2, 8])
  assert.equal(r.cuenta.excluidas, 0)
  r = agrega(ARCHIVE.albums, geo, { ubic: 'd' })
  assert.equal(r.cuenta.excluidas, 3, 'misma cuenta, multiartista y artista fuera, pero contadas')
  r = agrega(ARCHIVE.albums, geo, { territorio: 'Gipuzkoa' })
  assert.deepEqual([...r.porLugar.keys()], [1])
  assert.equal(r.cuenta.otroTerritorio, 2)
})

test('etiquetas: capitales primero, luego densidad, con tope', () => {
  const marcas = [
    { lugar: { id: 'bilbo' }, n: 100 },
    { lugar: { id: 'donostia' }, n: 80 },
    { lugar: { id: 'zarautz' }, n: 50 },
    { lugar: { id: 'irun' }, n: 40 },
    { lugar: { id: 'bermeo' }, n: 5 },
  ]
  assert.deepEqual(etiquetasPrioritarias(marcas, { max: 3 }).map((m) => m.lugar.id),
    ['bilbo', 'donostia', 'zarautz'])
  assert.deepEqual(etiquetasPrioritarias(marcas, { max: 2, seleccion: 'bermeo' }).map((m) => m.lugar.id),
    ['bermeo', 'bilbo'], 'lo seleccionado siempre se rotula')
  assert.deepEqual(etiquetasPrioritarias(marcas, { max: 2, hover: 'irun' }).map((m) => m.lugar.id),
    ['irun', 'bilbo'])
  assert.equal(etiquetasPrioritarias(marcas, { max: 9 }).length, 5)
})

test('filtros combinados: tag + años + territorio', () => {
  const r = consultaMapa(ARCHIVE, geo, { tag: 'noise', desde: 2005, hasta: 2012, ubic: UBIC_DEFECTO })
  assert.deepEqual(r.rows.map((a) => a.id), [1, 2, 3, 6, 7, 8])
  const rank = rankingLugares(r.porLugar, geo).map((x) => [x.lugar.id, x.n])
  assert.deepEqual(rank, [['bilbo', 1], ['zarautz', 1]])
  const g = consultaMapa(ARCHIVE, geo, { tag: 'hardcore', territorio: 'Nafarroa', ubic: UBIC_DEFECTO })
  assert.deepEqual([...g.porLugar.values()].flat().map((a) => a.id), [5])
})

test('densidad de etiquetas por contexto', () => {
  assert.equal(maxEtiquetas({ movil: true }), 5, 'en móvil, vista general: solo las capitales')
  assert.ok(maxEtiquetas({ movil: true, zoom: 3 }) > 5, 'al acercar, más rótulos')
  assert.ok(maxEtiquetas({ movil: true, territorio: 'Gipuzkoa', zoom: 2 }) > maxEtiquetas({ movil: true, zoom: 2 }))
  assert.equal(maxEtiquetas({}), 7)
  assert.equal(maxEtiquetas({ territorio: 'Gipuzkoa' }), 18)
  assert.ok(maxEtiquetas({ movil: true, zoom: 8 }) <= 14, 'con tope')
})

test('zoom y desplazamiento encajados en el mapa', () => {
  const base = [0, 0, 100, 80]
  assert.deepEqual(encajaVista(base, { k: 1 }), base, 'sin zoom, la vista completa')
  assert.deepEqual(encajaVista(base, { k: 2, cx: 50, cy: 40 }), [25, 20, 50, 40])
  assert.deepEqual(encajaVista(base, { k: 2, cx: -100, cy: -100 }), [0, 0, 50, 40], 'no se sale por arriba')
  assert.deepEqual(encajaVista(base, { k: 2, cx: 999, cy: 999 }), [50, 40, 50, 40], 'ni por abajo')
  assert.deepEqual(encajaVista(base, { k: 0.2 }), base, 'no se aleja más que el mapa entero')
  const z = encajaVista(base, { k: 99, cx: 50, cy: 40 })
  assert.equal(z[2], 100 / 8, 'zoom con tope')
})

test('lift y sobrerrepresentados con umbrales', () => {
  assert.equal(lift(10, 100, 50, 5000), 10)
  assert.equal(lift(1, 0, 1, 1), 0)
  const tagIndex = new Map([['noise', new Array(20)], ['raro', new Array(3)], ['bilbao', new Array(20)]])
  const rows = [
    { tags: ['noise', 'raro', 'bilbao'] }, { tags: ['noise', 'raro', 'bilbao'] },
    { tags: ['noise', 'raro', 'bilbao'] }, { tags: [] },
  ]
  const s = sobrerrepresentados(rows, tagIndex, 100, { excluir: new Set(['bilbao']) })
  assert.deepEqual(s.map((x) => x[0]), ['noise'], 'raro no llega a 10 en el archivo; bilbao es topónimo')
  assert.equal(s[0][2], 3.75)
})

test('resumen de municipio: procedencia, sellos y artistas', () => {
  const r = resumenLugar([ARCHIVE.albums[0], ARCHIVE.albums[1]], geo)
  assert.equal(r.releases, 2)
  assert.deepEqual(r.anios, [2005, 2011])
  assert.deepEqual(r.porTipo, { direct: 1, same_account: 1 })
  assert.deepEqual(r.porProcedencia, { d: 1, m: 1 })
  assert.equal(r.sello, 1)
  assert.deepEqual(r.artistas, [{ nombre: 'Kaos', n: 2 }])
  assert.deepEqual(r.cuentas, [{ id: 'grupo', sello: false, n: 1 }, { id: 'sello', sello: true, n: 1 }])
})
