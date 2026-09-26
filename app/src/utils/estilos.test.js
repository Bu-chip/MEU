// Tests de la capa de estilos (mapa de fusión de tags): `npm test`.
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { preparaEstilos, nodosDe, tieneEstilo, etiqueta, RESTO, OTROS_GENEROS } from './estilos.js'
import { filtra } from './busqueda.js'
import { hashArchivo, parseRoute } from '../hooks/useHashRoute.js'
import { UMBRAL_ESTILOS } from './indices.js'

// Misma forma que data/derived/tag_nodes.json (scripts/tag_merge_map.py).
const MAPA = {
  nodos: [
    { id: 'rock', grupo: 'genero', padre: null, discos: 0, tags: ['rock', 'rocka', 'rock vasco'] },
    { id: 'post-punk', grupo: 'genero', padre: 'punk', discos: 0, tags: ['post-punk', 'postpunk', 'post punk'] },
    { id: 'punk', grupo: 'genero', padre: 'rock', discos: 0, tags: ['punk'] },
    { id: OTROS_GENEROS, grupo: 'genero', padre: null, discos: 0, tags: ['bolero tech'] },
    { id: 'lugar:bilbo', grupo: 'lugar', padre: 'lugar:bizkaia', discos: 0, tags: ['bilbao', 'bilbo'] },
    { id: 'otro:cassette', grupo: 'otro', padre: 'otro:formato', discos: 0, tags: ['cassette', 'tape'] },
    { id: RESTO, grupo: RESTO, padre: null, discos: 0, tags: ['kokoshca'] },
  ],
}

const alb = (id, tags, extra = {}) => ({
  id, artist: 'A' + id, title: 'T' + id, year: 2000 + id, genre: null, tags, url: '', album_id: id, ...extra,
})
const N = UMBRAL_ESTILOS
const ARCHIVE = {
  albums: [
    alb(1, ['rock', 'rocka', 'bilbao', 'kokoshca']),          // rock una sola vez
    alb(2, ['rock vasco', 'postpunk', 'cassette']),
    alb(3, ['post punk', 'punk', 'tape']),
    alb(4, ['post-punk', 'bilbo']),
    alb(5, ['bolero tech', 'tag desconocido']),
    ...Array.from({ length: N }, (_, i) => alb(10 + i, ['rock'])), // rock llega al umbral
  ],
}

test('nodosDe: sin repetir, sin resto, desconocidos tal cual', () => {
  const { nodoDeTag } = preparaEstilos(MAPA, ARCHIVE)
  assert.deepEqual(nodosDe(ARCHIVE.albums[0], nodoDeTag), ['rock', 'lugar:bilbo'])
  assert.deepEqual(nodosDe(ARCHIVE.albums[1], nodoDeTag), ['rock', 'post-punk', 'otro:cassette'])
  assert.deepEqual(nodosDe(ARCHIVE.albums[4], nodoDeTag), [OTROS_GENEROS, 'tag desconocido'])
})

test('preparaEstilos: índice por nodo con cada disco una vez', () => {
  const est = preparaEstilos(MAPA, ARCHIVE)
  assert.equal(est.nodoIndex.get('rock').length, 2 + N)
  assert.deepEqual(est.nodoIndex.get('post-punk').map((a) => a.id), [2, 3, 4])
  assert.deepEqual(est.nodoIndex.get('lugar:bilbo').map((a) => a.id), [1, 4])
  assert.equal(est.nodoIndex.has(RESTO), false)
  assert.equal(est.nodos.get('post-punk').padre, 'punk')
})

test('elegibles: solo género, sobre el umbral, sin «otros géneros»', () => {
  const est = preparaEstilos(MAPA, ARCHIVE)
  assert.deepEqual(est.elegibles, ['rock'])
  const masPostPunk = {
    albums: [...ARCHIVE.albums, ...Array.from({ length: N }, (_, i) => alb(50 + i, ['postpunk', 'bilbao', 'cassette']))],
  }
  const est2 = preparaEstilos(MAPA, masPostPunk)
  assert.deepEqual(est2.elegibles, ['post-punk', 'rock']) // por frecuencia: post-punk 3+N > rock 2+N
  assert.equal(est2.elegibles.includes('lugar:bilbo'), false)
  assert.equal(est2.elegibles.includes('otro:cassette'), false)
})

test('tieneEstilo y etiqueta', () => {
  const { nodoDeTag } = preparaEstilos(MAPA, ARCHIVE)
  assert.equal(tieneEstilo(ARCHIVE.albums[1], 'rock', nodoDeTag), true)
  assert.equal(tieneEstilo(ARCHIVE.albums[1], 'punk', nodoDeTag), false)
  assert.equal(tieneEstilo(ARCHIVE.albums[4], 'tag desconocido', nodoDeTag), true)
  assert.equal(etiqueta('lugar:bilbo'), 'bilbo')
  assert.equal(etiqueta('otro:cassette'), 'cassette')
  assert.equal(etiqueta('post-punk'), 'post-punk')
})

test('filtra por estilo: todos los discos del nodo; sin mapa degrada a tag exacto', () => {
  const est = preparaEstilos(MAPA, ARCHIVE)
  const ids = (rows) => rows.map((r) => r.id)
  assert.deepEqual(ids(filtra(ARCHIVE, { estilo: 'post-punk' }, est)), [2, 3, 4])
  assert.deepEqual(ids(filtra(ARCHIVE, { estilo: 'post-punk' })), [4]) // solo el tag literal
  assert.deepEqual(ids(filtra(ARCHIVE, { tag: 'post-punk' }, est)), [4]) // tag = exacto, con o sin mapa
  assert.deepEqual(ids(filtra(ARCHIVE, { estilo: 'lugar:bilbo' }, est)), [1, 4])
  assert.deepEqual(ids(filtra(ARCHIVE, { estilo: 'rock', anio: 2002 }, est)), [2])
})

test('la búsqueda libre encuentra por nodo cuando hay mapa', () => {
  const est = preparaEstilos(MAPA, ARCHIVE)
  const ids = (rows) => rows.map((r) => r.id)
  assert.deepEqual(ids(filtra(ARCHIVE, { q: 'post punk' }, est)), [2, 3, 4]) // «postpunk» también
  assert.deepEqual(ids(filtra(ARCHIVE, { q: 'post punk' })), [3]) // sin mapa: subcadena literal
  assert.deepEqual(ids(filtra(ARCHIVE, { q: 'rocka' }, est)), [1]) // el tag original sigue ahí
})

test('hashArchivo lleva estilo y la ruta lo devuelve', () => {
  const h = hashArchivo({ estilo: 'post-punk', anio: 2003 })
  assert.equal(h, '#/archivo?anio=2003&estilo=post-punk')
  assert.equal(parseRoute(h).params.get('estilo'), 'post-punk')
  assert.equal(hashArchivo({ tag: 'rocka' }), '#/archivo?tag=rocka')
})
