// Tests de «CERCA DE ESTE»: `npm test`.
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { similares } from './similares.js'

const alb = (id, year, tags) => ({ id, year, tags })
const A = alb(1, 2010, ['rock', 'rocka', 'kokoshca'])
const B = alb(2, 2005, ['rock', 'punk'])          // rock en común
const C = alb(3, 2001, ['rocka', 'kokoshca'])     // rocka + kokoshca en común (crudo), rock (nodo)
const D = alb(4, 2020, ['punk'])                  // nada
const ALBUMS = [A, B, C, D]

test('sin mapa: tags crudos', () => {
  const s = similares(ALBUMS, A)
  assert.deepEqual(s.map(([o, ov]) => [o.id, ov]), [[3, 2], [2, 1]])
})

test('con mapa: estilos, sin resto, cada nodo una vez', () => {
  const nodoDeTag = new Map([['rock', 'rock'], ['rocka', 'rock'], ['punk', 'punk'], ['kokoshca', 'resto']])
  const s = similares(ALBUMS, A, 8, nodoDeTag)
  // B y C comparten solo «rock» (1 estilo); a igualdad, año asc: C (2001) antes que B (2005)
  assert.deepEqual(s.map(([o, ov]) => [o.id, ov]), [[3, 1], [2, 1]])
})
