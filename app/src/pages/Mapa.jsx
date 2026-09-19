import { useState, useRef, useEffect, useMemo } from 'react'
import { getIndices } from '../utils/indices.js'
import { formato } from '../utils/formato.js'
import { navegar, reemplazar, parseRoute, hashArchivo } from '../hooks/useHashRoute.js'
import { useMapIndex } from '../hooks/useMapIndex.js'
import { FichaBar } from '../components/FichaBar.jsx'
import {
  PROCEDENCIAS, TIPOS_FIABLES, leeFiltrosMapa, hashMapa, preparaGeo, consultaCacheada,
  rankingLugares, resumenLugar, tagsPrincipales, sobrerrepresentados,
} from '../utils/mapa.js'
import './Archivo.css'
import './Mapa.css'

// MAPA: la segunda puerta al mismo archivo. ARCHIVO parte de releases,
// artistas y tags; MAPA parte de lugares. Usa los MISMOS filtros (texto con
// alias, género, tag, artista, años) y el índice geográfico precalculado
// (data/locations/map_index.json). Referencia visual: la retícula de puntos
// cuadrados del «mapa de escenas» del archivo de música electrónica,
// adaptada: aquí la unidad es el municipio y la procedencia NUNCA se
// codifica con opacidad (se leería como «pocos discos»).

const ANCHO_NOMINAL = 720 // px supuestos hasta medir el lienzo
const LADO_MIN = 6
const LADO_MAX = 34
const FACETAS_GENERO = 14
const PAGINA = 60

const CODIGO_TIPO = {
  direct: ['D', 'directa: Bandcamp, esta release'],
  manual: ['M', 'decisión manual'],
  same_account: ['C', 'misma cuenta de Bandcamp'],
  artist_inferred: ['A', 'inferida por artista'],
  tag_hint: ['T', 'solo pista de tag'],
}

function cajaDe(cells, pad = 1) {
  let [c0, r0, c1, r1] = [Infinity, Infinity, -Infinity, -Infinity]
  for (const [c, r] of cells) {
    c0 = Math.min(c0, c)
    r0 = Math.min(r0, r)
    c1 = Math.max(c1, c)
    r1 = Math.max(r1, r)
  }
  return [c0 - pad, r0 - pad, c1 - c0 + 1 + 2 * pad, r1 - r0 + 1 + 2 * pad]
}

// Etiquetas: de mayor a menor, se descarta la que pisa a otra ya puesta.
// Visibles «según haya sitio, no según importancia» (spec del mapa vecino).
function colocaEtiquetas(items, upx, vb) {
  const puestas = []
  const cajas = []
  const solapa = (a, b) => a[0] < b[0] + b[2] && a[0] + a[2] > b[0] && a[1] < b[1] + b[3] && a[1] + a[3] > b[1]
  const marcas = items.map((o) => [o.x - o.lado / 2, o.y - o.lado / 2, o.lado, o.lado])
  for (const it of items) {
    const w = (it.name.length * 6.2 + 4) * upx
    const h = 11 * upx
    const m = 3 * upx
    // derecha, izquierda, arriba, abajo: la primera que no pisa nada
    const candidatas = [
      [it.x + it.lado / 2 + m, it.y - h / 2],
      [it.x - it.lado / 2 - m - w, it.y - h / 2],
      [it.x - w / 2, it.y - it.lado / 2 - m - h],
      [it.x - w / 2, it.y + it.lado / 2 + m],
    ]
    const libre = candidatas
      .map(([x, y]) => [x, y, w, h])
      .find(
        (c) =>
          c[0] >= vb[0] &&
          c[0] + c[2] <= vb[0] + vb[2] &&
          c[1] >= vb[1] &&
          c[1] + c[3] <= vb[1] + vb[3] &&
          !cajas.some((b) => solapa(c, b)) &&
          !marcas.some((b, j) => items[j] !== it && solapa(c, b)),
      )
    if (!libre) continue
    cajas.push(libre)
    puestas.push({ ...it, lx: libre[0] + 2 * upx, ly: libre[1] + h - 3 * upx })
  }
  return puestas
}

// Ancho real del lienzo: los tamaños (marcas, etiquetas, blancos táctiles)
// se fijan en píxeles de pantalla, no en unidades del mapa.
function useCaja(ref) {
  const [caja, setCaja] = useState(null)
  useEffect(() => {
    const el = ref.current
    if (!el || typeof ResizeObserver === 'undefined') return
    const ro = new ResizeObserver(([e]) => {
      const { width, height } = e.contentRect
      if (width > 0 && height > 0) setCaja({ w: width, h: height })
    })
    ro.observe(el)
    return () => ro.disconnect()
  }, [ref])
  return caja
}

function Lienzo({ geo, lugares, maxN, lugarSel, territorio, filtrado, onLugar, onTerritorio }) {
  const [hover, setHover] = useState(null)
  const svgRef = useRef(null)
  const caja = useCaja(svgRef)
  const grid = geo.grid
  const vb = useMemo(() => {
    const cells = territorio
      ? grid.cells.filter(([, , t]) => geo.territories[t] === territorio)
      : grid.cells
    return cajaDe(cells.length ? cells : grid.cells)
  }, [grid, geo.territories, territorio])
  // Unidades de mapa por píxel: el viewBox se encaja (meet) en la caja
  // real del SVG, así que manda la dimensión más restrictiva (max-height).
  const upx = caja ? Math.max(vb[2] / caja.w, vb[3] / caja.h) : vb[2] / ANCHO_NOMINAL
  // Lado máximo proporcional al lienzo (en móvil, un Bilbo de 34 px tapa
  // media Bizkaia). Escala de raíz: el área es proporcional a las releases.
  const ladoMax = Math.min(LADO_MAX, Math.max(18, (vb[2] / upx) * 0.05))
  const lado = (n) => (n > 0 ? (LADO_MIN + (ladoMax - LADO_MIN) * Math.sqrt(n / maxN)) * upx : 0)

  // Rótulos de territorio en la vista completa (centroide de sus celdas).
  const rotulos = useMemo(() => {
    if (territorio) return []
    return geo.territories.map((name, t) => {
      const cs = grid.cells.filter((c) => c[2] === t)
      const x = cs.reduce((s, c) => s + c[0], 0) / cs.length + 0.5
      const y = cs.reduce((s, c) => s + c[1], 0) / cs.length + 0.5
      return { name, x, y }
    })
  }, [grid, geo.territories, territorio])

  const marcas = lugares
    .filter((l) => !territorio || l.lugar.territorio === territorio)
    .map((l) => ({ ...l, x: l.lugar.x, y: l.lugar.y, name: l.lugar.name, lado: lado(l.n), ladoBase: lado(l.nBase) }))
  const etiquetas = colocaEtiquetas(
    [...marcas].filter((m) => m.n > 0).sort((a, b) => b.n - a.n),
    upx,
    vb,
  )
  const hov = hover && marcas.find((m) => m.lugar.id === hover)

  return (
    <div className="lienzo">
      <svg
        ref={svgRef}
        viewBox={vb.join(' ')}
        role="img"
        aria-label={`Mapa de Euskal Herria${territorio ? ' · ' + territorio : ''} con los municipios del archivo`}
      >
        <g className="reticula">
          {grid.cells.map(([c, r, t]) => (
            <rect
              key={`${c}-${r}`}
              x={c + 0.16}
              y={r + 0.16}
              width={0.68}
              height={0.68}
              className={`celda${territorio && geo.territories[t] !== territorio ? ' fuera' : ''}`}
              onClick={() => onTerritorio(geo.territories[t])}
            />
          ))}
        </g>
        {rotulos.map((r) => (
          <text
            key={r.name}
            x={r.x}
            y={r.y}
            className="rotulo-territorio"
            fontSize={20 * upx}
            onClick={() => onTerritorio(r.name)}
          >
            {r.name.toUpperCase()}
          </text>
        ))}
        {filtrado &&
          marcas
            .filter((m) => m.nBase > 0)
            .map((m) => (
              <rect
                key={'b' + m.lugar.id}
                className="fantasma"
                x={m.x - m.ladoBase / 2}
                y={m.y - m.ladoBase / 2}
                width={m.ladoBase}
                height={m.ladoBase}
                strokeWidth={1 * upx}
              />
            ))}
        {marcas
          .filter((m) => m.n > 0)
          .sort((a, b) => b.n - a.n)
          .map((m) => (
            <rect
              key={m.lugar.id}
              className={
                'marca' +
                (m.soloInferida ? ' inferida' : '') +
                (lugarSel === m.lugar.id ? ' sel' : '') +
                (hover === m.lugar.id ? ' hov' : '')
              }
              x={m.x - m.lado / 2}
              y={m.y - m.lado / 2}
              width={m.lado}
              height={m.lado}
              strokeWidth={(lugarSel === m.lugar.id ? 2.5 : 1.2) * upx}
              strokeDasharray={m.soloInferida ? `${2 * upx} ${1.5 * upx}` : undefined}
            />
          ))}
        {etiquetas.map((e) => (
          <text
            key={'t' + e.lugar.id}
            x={e.lx}
            y={e.ly}
            className={'etiqueta' + (lugarSel === e.lugar.id ? ' sel' : '')}
            fontSize={11 * upx}
          >
            {e.name}
          </text>
        ))}
        {/* Blancos táctiles invisibles (≥ 26 px) por encima de todo. */}
        {marcas
          .filter((m) => m.n > 0 || lugarSel === m.lugar.id)
          .map((m) => {
            const t = Math.max(26 * upx, m.lado)
            return (
              <rect
                key={'h' + m.lugar.id}
                className="blanco"
                x={m.x - t / 2}
                y={m.y - t / 2}
                width={t}
                height={t}
                onMouseEnter={() => setHover(m.lugar.id)}
                onMouseLeave={() => setHover(null)}
                onClick={() => onLugar(m.lugar.id)}
              >
                <title>{`${m.name}: ${formato(m.n)} releases`}</title>
              </rect>
            )
          })}
      </svg>
      {hov && (
        <div className="tip" aria-hidden="true">
          <b>{hov.name}</b> {formato(hov.n)} releases
          {filtrado && hov.nBase !== hov.n ? ` de ${formato(hov.nBase)}` : ''}
        </div>
      )}
      <div className="leyenda">
        <span>
          <i className="lg-marca" /> tamaño = releases del archivo
        </span>
        <span>
          <i className="lg-inferida" /> solo ubicación inferida
        </span>
        {filtrado && (
          <span>
            <i className="lg-fantasma" /> total sin filtros
          </span>
        )}
        {territorio && (
          <button className="lg-volver" onClick={() => onTerritorio(null)}>
            ← EUSKAL HERRIA
          </button>
        )}
      </div>
    </div>
  )
}

function Procedencia({ porTipo, total, sello }) {
  const tramos = ['direct', 'manual', 'same_account', 'artist_inferred', 'tag_hint'].filter((t) => porTipo[t])
  return (
    <div className="procedencia">
      <div className="barra" role="img" aria-label="procedencia de las ubicaciones">
        {tramos.map((t) => (
          <span
            key={t}
            className={'tramo tp-' + t}
            style={{ width: `${(100 * porTipo[t]) / total}%` }}
            title={`${CODIGO_TIPO[t][1]}: ${porTipo[t]}`}
          />
        ))}
      </div>
      <ul>
        {tramos.map((t) => (
          <li key={t}>
            <i className={'tp-' + t} /> {CODIGO_TIPO[t][1]} <b>{formato(porTipo[t])}</b>
          </li>
        ))}
      </ul>
      {sello > 0 && (
        <p className="nota">
          {formato(sello)} publicadas desde cuentas con varios artistas (probables sellos): su
          ubicación es la de esa cuenta, no necesariamente la del grupo.
        </p>
      )}
    </div>
  )
}

function ListaReleases({ rows, geo, onRelease }) {
  const [n, setN] = useState(PAGINA)
  const orden = useMemo(
    () => [...rows].sort((a, b) => (b.year || 0) - (a.year || 0) || a.artist.localeCompare(b.artist)),
    [rows],
  )
  return (
    <div className="releases">
      {orden.slice(0, n).map((a) => {
        const [code, ayuda] = CODIGO_TIPO[geo.rel.get(a.id)?.type] ?? ['?', 'sin resolver']
        return (
          <div className="rel" key={a.id} onClick={() => onRelease(a)}>
            <span className="y">{a.year || 's/f'}</span>
            <span className="ar">{a.artist}</span>
            <span className="ti">{a.title}</span>
            <span className="tp" title={ayuda}>
              {code}
            </span>
          </div>
        )
      })}
      {orden.length > n && (
        <button className="vermas" onClick={() => setN((x) => x + PAGINA)}>
          mostrar más ({orden.length - n} restantes)
        </button>
      )}
    </div>
  )
}

function PanelLugar({ lugar, rows, nBase, filtrado, geo, idx, total, aplica, onRelease }) {
  const r = resumenLugar(rows, geo)
  const principales = tagsPrincipales(rows, { excluir: geo.geoTags })
  const sobre = sobrerrepresentados(rows, idx.tagIndex, total, { excluir: geo.geoTags })
  return (
    <div className="panel-lugar">
      <button className="volver" onClick={() => aplica({ lugar: null })}>
        ← TODOS LOS LUGARES
      </button>
      <h2>{lugar.name}</h2>
      <p className="sub">
        {lugar.alt ? lugar.alt + ' · ' : ''}
        {lugar.territorio}
      </p>
      <p className="cifras">
        <b>{formato(r.releases)}</b> releases · <b>{formato(r.artistas.length)}</b> artistas
        {r.anios && (
          <>
            {' '}
            · <b>{r.anios[0] === r.anios[1] ? r.anios[0] : `${r.anios[0]}–${r.anios[1]}`}</b>
          </>
        )}
      </p>
      {filtrado && (
        <p className="nota">con los filtros activos · sin filtros: {formato(nBase)} releases</p>
      )}
      {r.releases === 0 ? (
        <p className="vacio">Ninguna release de {lugar.name} cumple los filtros activos.</p>
      ) : (
        <>
          <h3>DE DÓNDE SALE LA UBICACIÓN</h3>
          <Procedencia porTipo={r.porTipo} total={r.releases} sello={r.sello} />

          <h3>TAGS PRINCIPALES</h3>
          <div className="tags">
            {principales.map(([t, n]) => (
              <button key={t} onClick={() => aplica({ tag: t })}>
                {t} <span className="c">{n}</span>
              </button>
            ))}
          </div>

          <h3>SOBRERREPRESENTADOS RESPECTO AL ARCHIVO</h3>
          {sobre.length ? (
            <table className="lift">
              <tbody>
                {sobre.map(([t, n, x]) => (
                  <tr key={t} onClick={() => aplica({ tag: t })}>
                    <td className="t">{t}</td>
                    <td className="x">×{x.toFixed(1)}</td>
                    <td className="n">{n}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="vacio">Pocas releases para comparar (mínimo 3 por tag).</p>
          )}
          <p className="nota">
            ×2,0 = el tag aparece en proporción el doble que en todo el archivo. Mínimo 3 releases
            aquí y 10 en el archivo; los tags de lugar no cuentan. Describe el archivo, no la
            escena.
          </p>

          <h3>ARTISTAS · {formato(r.artistas.length)}</h3>
          <div className="artistas">
            {r.artistas.slice(0, 40).map((a) => (
              <button key={a.nombre} onClick={() => aplica({ artista: a.nombre })}>
                {a.nombre}
                {a.n > 1 && <span className="c">{a.n}</span>}
              </button>
            ))}
            {r.artistas.length > 40 && <span className="mas">+{r.artistas.length - 40}</span>}
          </div>

          <h3>RELEASES</h3>
          <ListaReleases key={lugar.id} rows={rows} geo={geo} onRelease={onRelease} />
        </>
      )}
    </div>
  )
}

function Ranking({ lugares, onLugar, conLift, maxN }) {
  return (
    <table className="ranking">
      <tbody>
        {lugares.map((l) => (
          <tr key={l.lugar.id} onClick={() => onLugar(l.lugar.id)}>
            <td className="nom">{l.lugar.name}</td>
            <td className="bar">
              <span style={{ width: `${(100 * l.n) / maxN}%` }} />
            </td>
            <td className="n">{formato(l.n)}</td>
            {conLift && <td className="x">×{l.lift.toFixed(1)}</td>}
          </tr>
        ))}
      </tbody>
    </table>
  )
}

// Lift del tag por municipio, comparando con los MISMOS filtros salvo el
// tag: (releases del lugar con el tag / releases del lugar) ÷ (releases
// con el tag / releases), todo dentro de años/género/texto activos.
function PanelTag({ tag, lugares, idx, geo, sinTag, nConTag, onLugar }) {
  const nTag = idx.tagIndex.get(tag)?.length ?? 0
  const localizadas = lugares.reduce((s, l) => s + l.n, 0)
  const totalSinTag = sinTag.rows.length
  const conLift = lugares.map((l) => {
    const nb = sinTag.porLugar.get(l.lugar.i)?.length ?? 0
    const x = nb && nConTag && totalSinTag ? l.n / nb / (nConTag / totalSinTag) : 0
    return { ...l, lift: x }
  })
  return (
    <div className="panel-tag">
      <p className="kicker">TAG</p>
      <h2>{tag}</h2>
      <p className="cifras">
        <b>{formato(nTag)}</b> releases en el archivo · <b>{formato(localizadas)}</b> localizadas
        con los filtros activos en <b>{lugares.length}</b> municipios
      </p>
      {geo.geoTags.has(tag) && (
        <p className="nota">Este tag es un topónimo: su reparto dice dónde se etiqueta, no dónde está nadie.</p>
      )}
      <Ranking lugares={conLift.slice(0, 40)} onLugar={onLugar} conLift maxN={conLift[0]?.n || 1} />
      <p className="nota">
        ×lift = proporción del tag entre las releases del municipio frente a su proporción en el
        archivo, con los mismos filtros (años, género, búsqueda). Con pocas releases es poco
        estable. Describe el archivo, no la escena.
      </p>
    </div>
  )
}

function PanelGeneral({ lugares, cuenta, onLugar }) {
  const porTerritorio = new Map()
  for (const l of lugares) porTerritorio.set(l.lugar.territorio, (porTerritorio.get(l.lugar.territorio) ?? 0) + l.n)
  return (
    <div className="panel-general">
      <p className="kicker">LUGARES</p>
      <p className="cifras">
        <b>{formato(cuenta.localizadas)}</b> releases en <b>{lugares.length}</b> municipios
      </p>
      <div className="territorios">
        {[...porTerritorio.entries()]
          .sort((a, b) => b[1] - a[1])
          .map(([t, n]) => (
            <span key={t}>
              {t} <b>{formato(n)}</b>
            </span>
          ))}
      </div>
      <Ranking lugares={lugares.slice(0, 30)} onLugar={onLugar} maxN={lugares[0]?.n || 1} />
      {lugares.length > 30 && <p className="nota">+{lugares.length - 30} municipios en el mapa</p>}
    </div>
  )
}

function Contadores({ cuenta, territorio }) {
  const partes = [
    ['region_only', 'solo región o país'],
    ['outside_scope', 'fuera de Euskal Herria'],
    ['unresolved', 'sin resolver'],
    ['tag_hint', 'solo pista de tag (ocultas)'],
  ].filter(([k]) => cuenta[k])
  return (
    <div className="contadores" aria-live="polite">
      <span className="loc">
        <b>{formato(cuenta.localizadas)}</b> releases localizadas
      </span>
      <span className="sin">
        <b>{formato(cuenta.sinMunicipio)}</b> sin municipio resoluble
        {partes.length > 0 && ': '}
        {partes.map(([k, label], i) => (
          <span key={k}>
            {i > 0 && ' · '}
            {formato(cuenta[k])} {label}
          </span>
        ))}
      </span>
      {cuenta.ocultasProcedencia > 0 && (
        <span className="sin">{formato(cuenta.ocultasProcedencia)} ocultas por procedencia</span>
      )}
      {territorio && cuenta.otroTerritorio > 0 && (
        <span className="sin">
          {formato(cuenta.otroTerritorio)} en otros territorios
        </span>
      )}
    </div>
  )
}

export function Mapa({ route, archive }) {
  const { index, error } = useMapIndex()
  const filtros = leeFiltrosMapa(route)

  // Búsqueda: mismo patrón que ARCHIVO (local al instante, URL con debounce).
  const [qLocal, setQLocal] = useState(filtros.q)
  const [qPrevia, setQPrevia] = useState(filtros.q)
  if (filtros.q !== qPrevia) {
    setQPrevia(filtros.q)
    setQLocal(filtros.q)
  }
  const debounce = useRef(null)
  const qVigente = useRef(qLocal)
  useEffect(() => {
    qVigente.current = qLocal
  })
  useEffect(() => () => clearTimeout(debounce.current), [])

  const [tagLocal, setTagLocal] = useState(filtros.tag ?? '')
  const [tagPrevio, setTagPrevio] = useState(filtros.tag)
  if (filtros.tag !== tagPrevio) {
    setTagPrevio(filtros.tag)
    setTagLocal(filtros.tag ?? '')
  }

  const [seleccion, setSeleccion] = useState(null)
  const [recorriendo, setRecorriendo] = useState(false)

  const efectivos = { ...filtros, q: qLocal }
  const geo = index ? preparaGeo(index) : null
  // Consultas cacheadas por clave de filtros (sin el lugar: abrir un
  // municipio no recalcula nada). La línea base, sin filtros y con la misma
  // procedencia, fija la escala absoluta y los fantasmas.
  const consulta = archive && geo ? consultaCacheada(archive, geo, { ...efectivos, lugar: null }) : null
  const base = archive && geo ? consultaCacheada(archive, geo, { ubic: filtros.ubic }) : null

  // Recorrido temporal: avanza desde/hasta año a año sin llenar el historial.
  useEffect(() => {
    if (!recorriendo || !archive) return
    const years = archive.years
    const t = setInterval(() => {
      const f = leeFiltrosMapa(parseRoute(window.location.hash))
      const y = f.desde && f.desde === f.hasta ? f.desde + 1 : years[0]
      if (y > years[years.length - 1]) {
        setRecorriendo(false)
        return
      }
      reemplazar(hashMapa({ ...f, desde: y, hasta: y }))
    }, 750)
    return () => clearInterval(t)
  }, [recorriendo, archive])

  const aplica = (cambios) => {
    clearTimeout(debounce.current)
    setRecorriendo(false)
    navegar(hashMapa({ ...efectivos, ...cambios }))
  }

  useEffect(() => {
    const onKey = (e) => {
      if (e.key !== 'Escape' || seleccion) return
      const f = leeFiltrosMapa(parseRoute(window.location.hash))
      if (f.lugar) navegar(hashMapa({ ...f, lugar: null }))
      else if (f.territorio) navegar(hashMapa({ ...f, territorio: null }))
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [seleccion])

  if (error) return <p className="error-datos">error al cargar el mapa: {error}</p>
  if (!archive || !consulta || !base) return <p className="cargando">cargando mapa…</p>

  const idx = getIndices(archive)
  const total = archive.albums.length
  const { porLugar, cuenta } = consulta
  const filtrado = Boolean(
    qLocal.trim() || filtros.genero || filtros.tag || filtros.artista || filtros.desde || filtros.hasta,
  )
  const maxN = Math.max(1, ...[...base.porLugar.values()].map((r) => r.length))

  const lugares = geo.places.map((lugar) => {
    const rows = porLugar.get(lugar.i) ?? []
    return {
      lugar,
      rows,
      n: rows.length,
      nBase: base.porLugar.get(lugar.i)?.length ?? 0,
      soloInferida: rows.length > 0 && !rows.some((a) => TIPOS_FIABLES.has(geo.rel.get(a.id).type)),
    }
  })
  const ranking = rankingLugares(porLugar, geo)
  const lugarSel = filtros.lugar ? geo.placeById.get(filtros.lugar) : null

  const escribeQ = (valor) => {
    setQLocal(valor)
    clearTimeout(debounce.current)
    debounce.current = setTimeout(() => {
      if (qVigente.current !== valor) return
      const f = leeFiltrosMapa(parseRoute(window.location.hash))
      reemplazar(hashMapa({ ...f, q: valor }))
    }, 300)
  }
  const eligeTag = (valor) => {
    setTagLocal(valor)
    const t = valor.trim().toLowerCase()
    if (idx.tagIndex.has(t)) aplica({ tag: t })
  }
  const alternaUbic = (code) => {
    const u = filtros.ubic.includes(code) ? filtros.ubic.replace(code, '') : filtros.ubic + code
    aplica({ ubic: u })
  }
  const anios = archive.years

  const chips = []
  if (filtros.artista) chips.push(['artista: ' + filtros.artista, { artista: null }])
  if (filtros.genero) chips.push(['género: ' + filtros.genero, { genero: null }])
  if (filtros.tag) chips.push(['tag: ' + filtros.tag, { tag: null }])
  if (filtros.desde || filtros.hasta) {
    const r = filtros.desde === filtros.hasta ? filtros.desde : `${filtros.desde ?? '…'}–${filtros.hasta ?? '…'}`
    chips.push(['años: ' + r, { desde: null, hasta: null }])
  }
  if (filtros.territorio) chips.push(['territorio: ' + filtros.territorio, { territorio: null }])
  if (qLocal.trim()) chips.push(['«' + qLocal.trim() + '»', { q: '' }])

  let panel
  if (filtros.lugar && !lugarSel) {
    panel = (
      <div className="panel-lugar">
        <button className="volver" onClick={() => aplica({ lugar: null })}>
          ← TODOS LOS LUGARES
        </button>
        <p className="vacio">No hay ningún municipio «{filtros.lugar}» en el archivo.</p>
      </div>
    )
  } else if (lugarSel) {
    panel = (
      <PanelLugar
        lugar={lugarSel}
        rows={porLugar.get(lugarSel.i) ?? []}
        nBase={base.porLugar.get(lugarSel.i)?.length ?? 0}
        filtrado={filtrado}
        geo={geo}
        idx={idx}
        total={total}
        aplica={aplica}
        onRelease={setSeleccion}
      />
    )
  } else if (filtros.tag) {
    panel = (
      <PanelTag
        tag={filtros.tag}
        lugares={ranking}
        idx={idx}
        geo={geo}
        sinTag={consultaCacheada(archive, geo, { ...efectivos, tag: null, lugar: null })}
        nConTag={consulta.rows.length}
        onLugar={(id) => aplica({ lugar: id })}
      />
    )
  } else {
    panel = <PanelGeneral lugares={ranking} cuenta={cuenta} onLugar={(id) => aplica({ lugar: id })} />
  }

  return (
    <div className="mapa">
      <div className="busca">
        <label htmlFor="mq">BUSCAR</label>
        <input
          id="mq"
          type="text"
          autoComplete="off"
          spellCheck="false"
          placeholder="artista, título, género, año, tag…"
          value={qLocal}
          onChange={(e) => escribeQ(e.target.value)}
        />
        <label htmlFor="mtag">TAG</label>
        <input
          id="mtag"
          className="tag-input"
          type="text"
          list="mapa-tags"
          autoComplete="off"
          spellCheck="false"
          placeholder="noise, hardcore…"
          value={tagLocal}
          onChange={(e) => eligeTag(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && eligeTag(tagLocal)}
        />
        <datalist id="mapa-tags">
          {idx.tagsElegibles.map((t) => (
            <option key={t} value={t} />
          ))}
        </datalist>
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
          <span className="flbl">TERRITORIO</span>
          {geo.territories.map((t) => (
            <button
              key={t}
              className={filtros.territorio === t ? 'on' : ''}
              onClick={() => aplica({ territorio: filtros.territorio === t ? null : t, lugar: null })}
            >
              {t}
            </button>
          ))}
        </div>
        <div className="faceta anios">
          <span className="flbl">AÑOS</span>
          <label>
            desde{' '}
            <select value={filtros.desde ?? ''} onChange={(e) => aplica({ desde: e.target.value ? Number(e.target.value) : null })}>
              <option value="">—</option>
              {anios.map((y) => (
                <option key={y} value={y}>
                  {y}
                </option>
              ))}
            </select>
          </label>
          <label>
            hasta{' '}
            <select value={filtros.hasta ?? ''} onChange={(e) => aplica({ hasta: e.target.value ? Number(e.target.value) : null })}>
              <option value="">—</option>
              {anios.map((y) => (
                <option key={y} value={y}>
                  {y}
                </option>
              ))}
            </select>
          </label>
          <button
            className={'recorrer' + (recorriendo ? ' on' : '')}
            onClick={() => setRecorriendo((v) => !v)}
            title="distribución de las releases del archivo por año según las ubicaciones actualmente asociadas"
          >
            {recorriendo ? '■ PARAR' : '▶ RECORRER'}
          </button>
          <span className="aviso">
            el año es el de la release; la ubicación es la actual de la cuenta en Bandcamp
          </span>
        </div>
        <div className="faceta ubic">
          <span className="flbl">UBICACIONES</span>
          {PROCEDENCIAS.map((p) => (
            <label key={p.code} title={p.ayuda}>
              <input
                type="checkbox"
                checked={filtros.ubic.includes(p.code)}
                onChange={() => alternaUbic(p.code)}
              />
              {p.label}
            </label>
          ))}
        </div>
      </div>

      {chips.length > 0 && (
        <div className="estado">
          <button className="volver" onClick={() => aplica({ q: '', genero: null, tag: null, artista: null, desde: null, hasta: null, territorio: null })}>
            ← TODO
          </button>
          <span className="chips">
            {chips.map(([label, limpia]) => (
              <span className="chip" key={label} onClick={() => aplica(limpia)}>
                {label} <b>×</b>
              </span>
            ))}
          </span>
          <a
            className="al-archivo"
            href={hashArchivo({ q: qLocal, genero: filtros.genero, tag: filtros.tag, artista: filtros.artista, desde: filtros.desde, hasta: filtros.hasta })}
          >
            VER EN ARCHIVO →
          </a>
        </div>
      )}

      <Contadores cuenta={cuenta} territorio={filtros.territorio} />

      <div className="mapa-cuerpo">
        <Lienzo
          geo={geo}
          lugares={lugares}
          maxN={maxN}
          lugarSel={lugarSel?.id}
          territorio={filtros.territorio}
          filtrado={filtrado}
          onLugar={(id) => aplica({ lugar: id === filtros.lugar ? null : id })}
          onTerritorio={(t) => aplica({ territorio: t, lugar: null })}
        />
        <aside className="mapa-panel">{panel}</aside>
      </div>

      <footer className="pie">
        el mapa describe asociaciones geográficas del archivo, no la residencia de nadie: la
        ubicación es la que Bandcamp da hoy a la cuenta que publica (grupo o sello), situada en el
        punto representativo de su municipio · las regiones, lo que queda fuera de Euskal Herria y
        lo no resuelto se cuentan arriba, no se dibujan · esc = subir un nivel · click en release =
        ficha
      </footer>

      <FichaBar album={seleccion} onCerrar={() => setSeleccion(null)} />
    </div>
  )
}
