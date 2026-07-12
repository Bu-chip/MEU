import { useState, useRef, useEffect } from 'react'
import { getIndices } from '../utils/indices.js'
import { filtra, ordena, expandeConsulta, normaliza } from '../utils/busqueda.js'
import { formato } from '../utils/formato.js'
import { navegar, reemplazar, hashArchivo, parseRoute } from '../hooks/useHashRoute.js'
import { FichaBar } from '../components/FichaBar.jsx'
import './Archivo.css'

// Spec congelada: design/meu-archivo-v3-hibrido.html. En reposo, el archivo
// es el índice de sus artistas; cualquier gesto (buscar, filtrar, clicar un
// artista) abre el registro. Los filtros viven en la URL (#/archivo?…,
// esquema de Fase 0) para que sean compartibles y para que los tags de la
// FICHA (F4) tengan dónde aterrizar. La búsqueda cubre también los tags:
// ahí actúa la capa de alias.

const PAGE = 150
const FACETAS_GENERO = 14

function letraDe(nombre) {
  const ch = normaliza(nombre.trim().charAt(0)).toUpperCase()
  return /[A-Z]/.test(ch) ? ch : '#'
}

function IndiceArtistas({ artistas, onArtista }) {
  const bloques = []
  let actual = null
  for (const [nombre, cuenta] of artistas) {
    const letra = letraDe(nombre)
    if (!actual || actual.letra !== letra) {
      actual = { letra, filas: [] }
      bloques.push(actual)
    }
    actual.filas.push([nombre, cuenta])
  }
  return (
    <div className="indice">
      {/* la letra puede repetirse (# antes de la A y tras la Z): key posicional */}
      {bloques.map(({ letra, filas }, i) => (
        <div className="bloque" key={`${letra}-${i}`}>
          <div className="letra">{letra}</div>
          {filas.map(([nombre, cuenta]) => (
            <div className="fila" key={nombre} onClick={() => onArtista(nombre)}>
              <span className="nom">{nombre}</span>
              <span className="cnt">{cuenta}</span>
            </div>
          ))}
        </div>
      ))}
    </div>
  )
}

const COLUMNAS = [
  ['y', 'AÑO'],
  ['a', 'ARTISTA'],
  ['t', 'TÍTULO'],
  ['g', 'GÉNERO'],
]

export function Archivo({ route, archive }) {
  const params = route.params
  const filtros = {
    q: params.get('q') ?? '',
    genero: params.get('genero'),
    anio: params.get('anio') ? Number(params.get('anio')) : null,
    tag: params.get('tag'),
    artista: params.get('artista'),
  }

  // La caja de búsqueda responde al instante en local y persiste a la URL
  // con debounce (replaceState va ratelimitado en Safari). Si la q de la
  // URL cambia desde fuera (atrás, chip, reset), se adopta en render.
  const [qLocal, setQLocal] = useState(filtros.q)
  const [qUrlPrevia, setQUrlPrevia] = useState(filtros.q)
  if (filtros.q !== qUrlPrevia) {
    setQUrlPrevia(filtros.q)
    setQLocal(filtros.q)
  }
  const debounce = useRef(null)
  const qVigente = useRef(qLocal)
  useEffect(() => {
    qVigente.current = qLocal
  })
  useEffect(() => () => clearTimeout(debounce.current), [])

  const [sort, setSort] = useState({ k: 'y', asc: false })
  const [page, setPage] = useState(0)
  const [seleccion, setSeleccion] = useState(null)

  // El paginado vuelve a 0 cuando cambia cualquier filtro u orden.
  const claveFiltros = JSON.stringify([filtros, qLocal, sort])
  const [clavePrevia, setClavePrevia] = useState(claveFiltros)
  if (claveFiltros !== clavePrevia) {
    setClavePrevia(claveFiltros)
    setPage(0)
  }

  if (!archive) {
    return <p className="cargando">cargando archivo…</p>
  }

  const idx = getIndices(archive)
  const efectivos = { ...filtros, q: qLocal }
  const activo = Boolean(
    qLocal.trim() || filtros.genero || filtros.anio || filtros.tag || filtros.artista,
  )

  const escribeQ = (valor) => {
    setQLocal(valor)
    clearTimeout(debounce.current)
    debounce.current = setTimeout(() => {
      // Solo persiste si la consulta sigue vigente, y sobre los filtros
      // que haya en la URL AHORA (no los del closure): una navegación
      // durante la espera no debe ser pisada por un tecleo anterior.
      if (qVigente.current !== valor) return
      const p = parseRoute(window.location.hash).params
      reemplazar(
        hashArchivo({
          q: valor,
          genero: p.get('genero'),
          anio: p.get('anio'),
          tag: p.get('tag'),
          artista: p.get('artista'),
        }),
      )
    }, 300)
  }
  // Toda navegación discreta cancela el debounce pendiente de la búsqueda:
  // si no, un tecleo reciente resucitaría su q por encima del nuevo estado.
  const aplica = (cambios) => {
    clearTimeout(debounce.current)
    navegar(hashArchivo({ ...efectivos, ...cambios }))
  }
  const reset = () => {
    clearTimeout(debounce.current)
    navegar(hashArchivo({}))
  }

  const rows = activo ? ordena(filtra(archive, efectivos), sort.k, sort.asc) : []
  const upto = Math.min(rows.length, (page + 1) * PAGE)
  const { equivalentes } = expandeConsulta(qLocal)

  const chips = []
  if (filtros.artista) chips.push(['artista: ' + filtros.artista, { artista: null }])
  if (filtros.genero) chips.push(['género: ' + filtros.genero, { genero: null }])
  if (filtros.anio) chips.push(['año: ' + filtros.anio, { anio: null }])
  if (filtros.tag) chips.push(['tag: ' + filtros.tag, { tag: null }])
  if (qLocal.trim()) {
    const eq = equivalentes.length ? ' ≈ ' + equivalentes.join(' · ') : ''
    chips.push(['«' + qLocal.trim() + '»' + eq, { q: '' }])
  }

  return (
    <>
      <div className="busca">
        <label htmlFor="q">BUSCAR</label>
        <input
          id="q"
          type="text"
          autoComplete="off"
          spellCheck="false"
          placeholder="artista, título, género, año, tag…"
          value={qLocal}
          onChange={(e) => escribeQ(e.target.value)}
        />
        <span className="n">{activo ? `${rows.length} releases` : ''}</span>
      </div>

      <div className="facetas">
        <div className="faceta">
          <span className="flbl">GÉNERO</span>
          {idx.generos.slice(0, FACETAS_GENERO).map(([g, c]) => (
            <button
              key={g}
              className={filtros.genero === g ? 'on' : ''}
              onClick={() => aplica({ genero: filtros.genero === g ? null : g })}
            >
              {g}
              <span className="c">{c}</span>
            </button>
          ))}
        </div>
        <div className="faceta">
          <span className="flbl">AÑO</span>
          {[...archive.years].reverse().map((y) => (
            <button
              key={y}
              className={filtros.anio === y ? 'on' : ''}
              onClick={() => aplica({ anio: filtros.anio === y ? null : y })}
            >
              {y}
            </button>
          ))}
        </div>
      </div>

      {activo && (
        <div className="estado">
          <button className="volver" onClick={reset}>
            ← ÍNDICE
          </button>
          <span className="chips">
            {chips.map(([label, limpia]) => (
              <span className="chip" key={label} onClick={() => aplica(limpia)}>
                {label} <b>×</b>
              </span>
            ))}
          </span>
          <span className="nn">{rows.length} releases</span>
        </div>
      )}

      {!activo && <IndiceArtistas artistas={idx.artistas} onArtista={(a) => aplica({ artista: a })} />}

      {activo && (
        <div className="registro">
          <div className="reg-head">
            {COLUMNAS.map(([k, label]) => (
              <span
                key={k}
                className={sort.k === k ? 'sorted' + (sort.asc ? ' asc' : '') : ''}
                onClick={() =>
                  setSort((s) => (s.k === k ? { k, asc: !s.asc } : { k, asc: k !== 'y' }))
                }
              >
                {label}
              </span>
            ))}
          </div>
          <div>
            {rows.slice(0, upto).map((r) => (
              <div className="linea" key={r.id} onClick={() => setSeleccion(r)}>
                <span className="y">{r.year || 's/f'}</span>
                <span className="ar">{r.artist}</span>
                <span className="ti">{r.title}</span>
                <span className="ge">{r.genre || '—'}</span>
              </div>
            ))}
          </div>
          {rows.length > upto && (
            <button className="vermas" onClick={() => setPage((p) => p + 1)}>
              mostrar más ({rows.length - upto} restantes)
            </button>
          )}
        </div>
      )}

      <footer className="pie">
        en reposo, el archivo es el índice de sus {formato(idx.artistas.length)}{' '}
        artistas · cualquier gesto (buscar, filtrar género/año, clicar un artista) abre el
        registro con las líneas reales · ← ÍNDICE o quitar los filtros devuelve al reposo ·
        click en línea = ficha
      </footer>

      <FichaBar album={seleccion} onCerrar={() => setSeleccion(null)} />
    </>
  )
}
