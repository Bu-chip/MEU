import { useState, useRef, useEffect, useMemo } from 'react'
import { getIndices } from '../utils/indices.js'
import { formato } from '../utils/formato.js'
import { navegar, reemplazar, parseRoute, hashArchivo } from '../hooks/useHashRoute.js'
import { useMapIndex } from '../hooks/useMapIndex.js'
import { FichaBar } from '../components/FichaBar.jsx'
import {
  PROCEDENCIAS, UBIC_DEFECTO, leeFiltrosMapa, hashMapa, preparaGeo, consultaCacheada,
  rankingLugares, resumenLugar, tagsPrincipales, sobrerrepresentados, procedenciaDe,
  etiquetasPrioritarias,
} from '../utils/mapa.js'
import './Mapa.css'

// MAPA: la segunda puerta al mismo archivo. ARCHIVO parte de releases,
// artistas y tags; MAPA parte de lugares. Usa los MISMOS filtros que ARCHIVO
// y el índice geográfico precalculado (data/locations/map_index.json).
//
// Jerarquía de la página: la tarea es explorar el archivo por lugares, así
// que el mapa manda. Divulgación progresiva: lo esencial primero, el detalle
// al seleccionar, la metodología plegada.
//   cabecera compacta · una línea de filtros · una línea de cobertura ·
//   mapa (≈65 %) + panel de contexto (≈35 %)
//
// Referencia visual: la retícula de puntos cuadrados del «mapa de escenas»
// del archivo de música electrónica. Aquí la unidad es el municipio y la
// procedencia NO se codifica con opacidad (se leería como «pocos discos»).

const ANCHO_NOMINAL = 720 // px supuestos hasta medir el lienzo
const LADO_MIN = 5
const LADO_MAX = 30
const PAGINA = 40
const TAGS_VISIBLES = 6
const RELEASES_VISIBLES = 4
const ETIQUETAS_MUNDO = 7 // rótulos en la vista de Euskal Herria
const ETIQUETAS_TERRITORIO = 18

const CODIGO_PROC = {
  d: ['D', 'directa: Bandcamp, en esta release'],
  c: ['C', 'misma cuenta de Bandcamp (un artista)'],
  a: ['A', 'inferida por el mismo artista'],
  m: ['M', 'misma cuenta, con varios artistas'],
  t: ['T', 'solo pista de un tag'],
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

// Coloca los rótulos ya priorizados: cada uno prueba derecha, izquierda,
// arriba y abajo, y se descarta si no cabe sin pisar nada.
function colocaEtiquetas(items, upx, vb) {
  const puestas = []
  const cajas = []
  const solapa = (a, b) => a[0] < b[0] + b[2] && a[0] + a[2] > b[0] && a[1] < b[1] + b[3] && a[1] + a[3] > b[1]
  const marcas = items.map((o) => [o.x - o.lado / 2, o.y - o.lado / 2, o.lado, o.lado])
  for (const it of items) {
    const w = (it.name.length * 6.2 + 4) * upx
    const h = 11 * upx
    const m = 3 * upx
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

// Caja real del SVG: los tamaños se fijan en píxeles de pantalla.
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

function Lienzo({ geo, lugares, maxN, lugarSel, territorio, filtrado, debiles, onLugar, onTerritorio }) {
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
  const upx = caja ? Math.max(vb[2] / caja.w, vb[3] / caja.h) : vb[2] / ANCHO_NOMINAL
  const ladoMax = Math.min(LADO_MAX, Math.max(16, (vb[2] / upx) * 0.045))
  const lado = (n) => (n > 0 ? (LADO_MIN + (ladoMax - LADO_MIN) * Math.sqrt(n / maxN)) * upx : 0)

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
  // Densidad de rótulos por contexto: pocos en la vista general, más al
  // ampliar a un territorio; lo seleccionado y lo apuntado, siempre.
  const etiquetas = colocaEtiquetas(
    etiquetasPrioritarias(marcas, {
      max: territorio ? ETIQUETAS_TERRITORIO : ETIQUETAS_MUNDO,
      seleccion: lugarSel,
      hover,
    }),
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
        {/* Territorios: orientación de fondo, nunca texto que compita. */}
        {rotulos.map((r) => (
          <text
            key={r.name}
            x={r.x}
            y={r.y}
            className="rotulo-territorio"
            fontSize={16 * upx}
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
                // La procedencia solo se dibuja si se han activado datos
                // débiles; si no, el mapa general no la codifica.
                (debiles && m.soloDebil ? ' debil' : '') +
                (lugarSel === m.lugar.id ? ' sel' : '') +
                (hover === m.lugar.id ? ' hov' : '')
              }
              x={m.x - m.lado / 2}
              y={m.y - m.lado / 2}
              width={m.lado}
              height={m.lado}
              strokeWidth={(lugarSel === m.lugar.id ? 2.5 : 1) * upx}
              strokeDasharray={debiles && m.soloDebil ? `${2 * upx} ${1.5 * upx}` : undefined}
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
          <b>{hov.name}</b> {formato(hov.n)}
          {filtrado && hov.nBase !== hov.n ? ` de ${formato(hov.nBase)}` : ''}
        </div>
      )}
      <div className="leyenda">
        <span>
          <i className="lg-grande" />
          <i className="lg-peque" /> tamaño = releases
        </span>
        {debiles && (
          <span>
            <i className="lg-debil" /> solo ubicación débil
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

// ── Panel de contexto ─────────────────────────────────────────────────

function Seccion({ titulo, cuenta, abierta, onAbrir, children }) {
  return (
    <div className={'seccion' + (abierta ? ' abierta' : '')}>
      <button className="cab-seccion" onClick={onAbrir} aria-expanded={abierta}>
        <span className="tit">{titulo}</span>
        {cuenta != null && <span className="n">{formato(cuenta)}</span>}
        <span className="ind">{abierta ? '−' : '+'}</span>
      </button>
      {abierta && <div className="cuerpo-seccion">{children}</div>}
    </div>
  )
}

function ListaReleases({ rows, geo, onRelease, limite }) {
  const [n, setN] = useState(limite)
  const orden = useMemo(
    () => [...rows].sort((a, b) => (b.year || 0) - (a.year || 0) || a.artist.localeCompare(b.artist)),
    [rows],
  )
  return (
    <div className="releases">
      {orden.slice(0, n).map((a) => {
        const [code, ayuda] = CODIGO_PROC[procedenciaDe(geo.rel.get(a.id))] ?? ['?', 'sin resolver']
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
        <button className="enlace" onClick={() => setN((x) => x + PAGINA)}>
          ver más ({formato(orden.length - n)}) →
        </button>
      )}
    </div>
  )
}

function PanelLugar({ lugar, rows, nBase, filtrado, geo, idx, total, filtros, aplica, onRelease }) {
  const [abierta, setAbierta] = useState(null)
  const [todosTags, setTodosTags] = useState(false)
  const r = resumenLugar(rows, geo)
  const excluir = geo.geoTags
  const principales = tagsPrincipales(rows, { excluir, limite: todosTags ? 40 : TAGS_VISIBLES })
  const sobre = sobrerrepresentados(rows, idx.tagIndex, total, { excluir })
  const abrir = (k) => setAbierta((a) => (a === k ? null : k))

  return (
    <div className="panel panel-lugar">
      <div className="panel-cab">
        <button className="volver" onClick={() => aplica({ lugar: null })} title="quitar la selección">
          ←
        </button>
        <div>
          <h2>{lugar.name}</h2>
          <p className="sub">
            {lugar.territorio}
            {lugar.alt ? ' · ' + lugar.alt : ''}
          </p>
        </div>
      </div>

      {r.releases === 0 ? (
        <p className="vacio">Ninguna release de {lugar.name} cumple los filtros activos.</p>
      ) : (
        <>
          <p className="cifras">
            <b>{formato(r.releases)}</b> releases · <b>{formato(r.artistas.length)}</b> artistas
            {r.anios && <> · {r.anios[0] === r.anios[1] ? r.anios[0] : `${r.anios[0]}—${r.anios[1]}`}</>}
          </p>
          {filtrado && <p className="nota">con los filtros activos · sin filtros: {formato(nBase)}</p>}

          <h3>TAGS PRINCIPALES</h3>
          <p className="tags">
            {principales.map(([t], i) => (
              <span key={t}>
                {i > 0 && <span className="sep"> · </span>}
                <button className={filtros.tag === t ? 'on' : ''} onClick={() => aplica({ tag: t })}>
                  {t}
                </button>
              </span>
            ))}
            {!todosTags && principales.length >= TAGS_VISIBLES && (
              <>
                {' '}
                <button className="enlace" onClick={() => setTodosTags(true)}>
                  ver todos
                </button>
              </>
            )}
          </p>

          <h3>ÚLTIMOS RELEASES</h3>
          <ListaReleases rows={rows} geo={geo} onRelease={onRelease} limite={RELEASES_VISIBLES} />

          <div className="secciones">
            <Seccion titulo="Artistas" cuenta={r.artistas.length} abierta={abierta === 'art'} onAbrir={() => abrir('art')}>
              <p className="lista-en-linea">
                {r.artistas.slice(0, 200).map((a, i) => (
                  <span key={a.nombre}>
                    {i > 0 && <span className="sep"> · </span>}
                    <button onClick={() => aplica({ artista: a.nombre })}>{a.nombre}</button>
                    {a.n > 1 && <span className="c">{a.n}</span>}
                  </span>
                ))}
              </p>
            </Seccion>

            <Seccion titulo="Releases" cuenta={r.releases} abierta={abierta === 'rel'} onAbrir={() => abrir('rel')}>
              <ListaReleases rows={rows} geo={geo} onRelease={onRelease} limite={PAGINA} />
              <a
                className="enlace"
                href={hashArchivo({
                  q: filtros.q,
                  genero: filtros.genero,
                  tag: filtros.tag,
                  artista: filtros.artista,
                  desde: filtros.desde,
                  hasta: filtros.hasta,
                })}
              >
                ver estos filtros en ARCHIVO →
              </a>
            </Seccion>

            <Seccion titulo="Sellos y cuentas" cuenta={r.cuentas.length} abierta={abierta === 'sel'} onAbrir={() => abrir('sel')}>
              <table className="tabla">
                <tbody>
                  {r.cuentas.slice(0, 30).map((c) => (
                    <tr key={c.id}>
                      <td className="t">
                        {c.id.replace(/^custom:/, '')}
                        {c.sello && (
                          <span className="marca-sello" title="cuenta con varios artistas (probable sello)">
                            {' '}
                            ▪
                          </span>
                        )}
                      </td>
                      <td className="n">{c.n}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <p className="nota">▪ cuenta con varios artistas: su ubicación es la de la cuenta.</p>
            </Seccion>

            <Seccion titulo="Estadísticas" abierta={abierta === 'est'} onAbrir={() => abrir('est')}>
              <p className="titulillo">MÁS CARACTERÍSTICOS</p>
              {sobre.length ? (
                <table className="tabla">
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
                <p className="nota">Pocas releases para comparar (mínimo 3 por tag).</p>
              )}
              <p className="nota">
                Proporción del tag aquí frente a su proporción en todo el archivo (mínimo 3
                releases aquí y 10 en el archivo; los tags de lugar no cuentan). Es una relación
                dentro del archivo, no una caracterización del municipio.
              </p>
            </Seccion>

            <Seccion titulo="Procedencia" abierta={abierta === 'proc'} onAbrir={() => abrir('proc')}>
              <table className="tabla">
                <tbody>
                  {PROCEDENCIAS.filter((p) => r.porProcedencia[p.code]).map((p) => (
                    <tr key={p.code}>
                      <td className="t" title={p.ayuda}>
                        {p.label}
                      </td>
                      <td className="n">{formato(r.porProcedencia[p.code])}</td>
                    </tr>
                  ))}
                  {r.sello > 0 && (
                    <tr>
                      <td className="t">desde cuentas con varios artistas</td>
                      <td className="n">{formato(r.sello)}</td>
                    </tr>
                  )}
                  {r.conflictos > 0 && (
                    <tr>
                      <td className="t">con evidencia contradictoria</td>
                      <td className="n">{formato(r.conflictos)}</td>
                    </tr>
                  )}
                </tbody>
              </table>
              <p className="nota">
                La ubicación es la que Bandcamp da hoy a la cuenta que publica, que puede ser un
                sello. No es la residencia de nadie ni una reconstrucción histórica.
              </p>
            </Seccion>
          </div>
        </>
      )}
    </div>
  )
}

function Ranking({ lugares, onLugar, maxN, conLift }) {
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

function PanelTag({ tag, lugares, geo, sinTag, nConTag, nLocalizadas, onLugar }) {
  const [n, setN] = useState(8)
  const totalSinTag = sinTag.rows.length
  const conLift = lugares.map((l) => {
    const nb = sinTag.porLugar.get(l.lugar.i)?.length ?? 0
    return { ...l, lift: nb && nConTag && totalSinTag ? l.n / nb / (nConTag / totalSinTag) : 0 }
  })
  return (
    <div className="panel panel-tag">
      <p className="kicker">DÓNDE APARECE</p>
      <h2>{tag}</h2>
      <p className="cifras">
        <b>{formato(nLocalizadas)}</b> releases localizadas · <b>{lugares.length}</b> municipios
      </p>
      {geo.geoTags.has(tag) && (
        <p className="nota">Este tag es un topónimo: dice dónde se etiqueta, no dónde está nadie.</p>
      )}
      <h3>MÁS PRESENCIA</h3>
      <Ranking lugares={conLift.slice(0, n)} onLugar={onLugar} maxN={conLift[0]?.n || 1} conLift />
      {conLift.length > n && (
        <button className="enlace" onClick={() => setN(conLift.length)}>
          ver todos ({conLift.length - n}) →
        </button>
      )}
      <p className="nota">
        ×: proporción del tag en el municipio frente a su proporción en el archivo, con los mismos
        filtros. Con pocas releases es poco estable.
      </p>
    </div>
  )
}

function PanelVacio({ lugares, cuenta, onLugar }) {
  const [ver, setVer] = useState(false)
  return (
    <div className="panel panel-vacio">
      <p className="intro">Explora el archivo por lugar.</p>
      <p className="cifras">
        <b>{formato(lugares.length)}</b> municipios · <b>{formato(cuenta.localizadas)}</b> releases
        visibles
      </p>
      <p className="nota">Selecciona un municipio en el mapa.</p>
      {ver ? (
        <>
          <h3>MÁS RELEASES</h3>
          <Ranking lugares={lugares.slice(0, 25)} onLugar={onLugar} maxN={lugares[0]?.n || 1} />
        </>
      ) : (
        <button className="enlace" onClick={() => setVer(true)}>
          ver ranking de municipios →
        </button>
      )}
    </div>
  )
}

// ── Filtros ───────────────────────────────────────────────────────────

function Menu({ id, titulo, valor, abierto, setAbierto, children, ancho }) {
  const activo = Boolean(valor)
  return (
    <div className={'menu' + (abierto === id ? ' abierto' : '')}>
      <button
        className={'disparador' + (activo ? ' on' : '')}
        onClick={() => setAbierto(abierto === id ? null : id)}
        aria-expanded={abierto === id}
      >
        {activo ? valor : titulo} <span className="flecha">▾</span>
      </button>
      {abierto === id && (
        <div className="menu-panel" style={ancho ? { width: ancho } : undefined}>
          {children}
        </div>
      )}
    </div>
  )
}

export function Mapa({ route, archive }) {
  const { index, error } = useMapIndex()
  const filtros = leeFiltrosMapa(route)

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

  const [abierto, setAbierto] = useState(null)
  const [metodologia, setMetodologia] = useState(false)
  const [seleccion, setSeleccion] = useState(null)
  const [recorriendo, setRecorriendo] = useState(false)
  const barraRef = useRef(null)

  // Los menús se cierran al pinchar fuera (Esc se gestiona más abajo).
  useEffect(() => {
    if (!abierto) return
    const fuera = (e) => {
      if (!barraRef.current?.contains(e.target)) setAbierto(null)
    }
    document.addEventListener('mousedown', fuera)
    return () => document.removeEventListener('mousedown', fuera)
  }, [abierto])

  const efectivos = { ...filtros, q: qLocal }
  const geo = index ? preparaGeo(index) : null
  const consulta = archive && geo ? consultaCacheada(archive, geo, { ...efectivos, lugar: null }) : null
  const base = archive && geo ? consultaCacheada(archive, geo, { ubic: filtros.ubic }) : null

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

  useEffect(() => {
    const onKey = (e) => {
      if (e.key !== 'Escape' || seleccion) return
      if (abierto) {
        setAbierto(null)
        return
      }
      const f = leeFiltrosMapa(parseRoute(window.location.hash))
      if (f.lugar) navegar(hashMapa({ ...f, lugar: null }))
      else if (f.territorio) navegar(hashMapa({ ...f, territorio: null }))
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [seleccion, abierto])

  if (error) return <p className="error-datos">error al cargar el mapa: {error}</p>
  if (!archive || !consulta || !base) return <p className="cargando">cargando mapa…</p>

  const idx = getIndices(archive)
  const total = archive.albums.length
  const { porLugar, cuenta } = consulta
  const filtrado = Boolean(
    qLocal.trim() || filtros.genero || filtros.tag || filtros.artista || filtros.desde || filtros.hasta,
  )
  const maxN = Math.max(1, ...[...base.porLugar.values()].map((r) => r.length))
  const debiles = filtros.ubic.includes('m') || filtros.ubic.includes('t')

  const lugares = geo.places.map((lugar) => {
    const rows = porLugar.get(lugar.i) ?? []
    return {
      lugar,
      rows,
      n: rows.length,
      nBase: base.porLugar.get(lugar.i)?.length ?? 0,
      soloDebil:
        rows.length > 0 && rows.every((a) => 'mt'.includes(procedenciaDe(geo.rel.get(a.id)) ?? 'x')),
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
  const aplica = (cambios) => {
    clearTimeout(debounce.current)
    setRecorriendo(false)
    setAbierto(null)
    navegar(hashMapa({ ...efectivos, ...cambios }))
  }
  const alternaUbic = (code) => {
    aplica({ ubic: filtros.ubic.includes(code) ? filtros.ubic.replace(code, '') : filtros.ubic + code })
  }
  const anios = archive.years

  const rangoAnios =
    filtros.desde || filtros.hasta
      ? filtros.desde === filtros.hasta
        ? String(filtros.desde)
        : `${filtros.desde ?? '…'}–${filtros.hasta ?? '…'}`
      : null

  // Chips: qué está filtrando ahora mismo, sin tener que abrir los menús.
  const chips = []
  if (filtros.artista) chips.push(['artista: ' + filtros.artista, { artista: null }])
  if (filtros.genero) chips.push([filtros.genero, { genero: null }])
  if (filtros.tag) chips.push([filtros.tag, { tag: null }])
  if (rangoAnios) chips.push([rangoAnios, { desde: null, hasta: null }])
  if (filtros.territorio) chips.push([filtros.territorio, { territorio: null }])
  if (qLocal.trim()) chips.push(['«' + qLocal.trim() + '»', { q: '' }])
  for (const p of PROCEDENCIAS) {
    const puesto = filtros.ubic.includes(p.code)
    if (puesto !== UBIC_DEFECTO.includes(p.code)) {
      chips.push([
        (puesto ? '+ ' : '− ') + p.label,
        { ubic: puesto ? filtros.ubic.replace(p.code, '') : filtros.ubic + p.code },
      ])
    }
  }

  let panel
  if (filtros.lugar && !lugarSel) {
    panel = (
      <div className="panel">
        <p className="vacio">No hay ningún municipio «{filtros.lugar}» en el archivo.</p>
        <button className="enlace" onClick={() => aplica({ lugar: null })}>
          ← todos los lugares
        </button>
      </div>
    )
  } else if (lugarSel) {
    panel = (
      <PanelLugar
        key={lugarSel.id}
        lugar={lugarSel}
        rows={porLugar.get(lugarSel.i) ?? []}
        nBase={base.porLugar.get(lugarSel.i)?.length ?? 0}
        filtrado={filtrado}
        geo={geo}
        idx={idx}
        total={total}
        filtros={efectivos}
        aplica={aplica}
        onRelease={setSeleccion}
      />
    )
  } else if (filtros.tag) {
    panel = (
      <PanelTag
        tag={filtros.tag}
        lugares={ranking}
        geo={geo}
        sinTag={consultaCacheada(archive, geo, { ...efectivos, tag: null, lugar: null })}
        nConTag={consulta.rows.length}
        nLocalizadas={cuenta.localizadas}
        onLugar={(id) => aplica({ lugar: id })}
      />
    )
  } else {
    panel = <PanelVacio lugares={ranking} cuenta={cuenta} onLugar={(id) => aplica({ lugar: id })} />
  }

  return (
    // Las clases dicen qué filas hay sobre el mapa: el alto del cuerpo se
    // ajusta para que mapa + panel sigan cabiendo sin scroll.
    <div className={'mapa' + (chips.length ? ' con-chips' : '') + (metodologia ? ' con-metodologia' : '')}>
      <div className="barra" ref={barraRef}>
        <input
          className="buscar"
          type="text"
          autoComplete="off"
          spellCheck="false"
          placeholder="buscar artista, título, tag…"
          value={qLocal}
          onChange={(e) => escribeQ(e.target.value)}
          aria-label="buscar"
        />

        <Menu id="genero" titulo="Género" valor={filtros.genero ?? filtros.tag} abierto={abierto} setAbierto={setAbierto} ancho={300}>
          <label className="campo">
            tag
            <input
              type="text"
              list="mapa-tags"
              defaultValue={filtros.tag ?? ''}
              placeholder="noise, hardcore…"
              onChange={(e) => {
                const t = e.target.value.trim().toLowerCase()
                if (idx.tagIndex.has(t)) aplica({ tag: t })
              }}
            />
          </label>
          <datalist id="mapa-tags">
            {idx.tagsElegibles.map((t) => (
              <option key={t} value={t} />
            ))}
          </datalist>
          <div className="opciones">
            {idx.generos.slice(0, 24).map(([g, c]) => (
              <button
                key={g}
                className={filtros.genero === g ? 'on' : ''}
                onClick={() => aplica({ genero: filtros.genero === g ? null : g })}
              >
                {g} <span className="c">{c}</span>
              </button>
            ))}
          </div>
        </Menu>

        <Menu id="territorio" titulo="Territorio" valor={filtros.territorio} abierto={abierto} setAbierto={setAbierto}>
          <div className="opciones">
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
        </Menu>

        <Menu id="anios" titulo="Años" valor={rangoAnios} abierto={abierto} setAbierto={setAbierto} ancho={260}>
          <div className="filas">
            <label className="campo">
              desde
              <select
                value={filtros.desde ?? ''}
                onChange={(e) => aplica({ desde: e.target.value ? Number(e.target.value) : null })}
              >
                <option value="">—</option>
                {anios.map((y) => (
                  <option key={y} value={y}>
                    {y}
                  </option>
                ))}
              </select>
            </label>
            <label className="campo">
              hasta
              <select
                value={filtros.hasta ?? ''}
                onChange={(e) => aplica({ hasta: e.target.value ? Number(e.target.value) : null })}
              >
                <option value="">—</option>
                {anios.map((y) => (
                  <option key={y} value={y}>
                    {y}
                  </option>
                ))}
              </select>
            </label>
            <button className={'accion' + (recorriendo ? ' on' : '')} onClick={() => setRecorriendo((v) => !v)}>
              {recorriendo ? '■ parar' : '▶ recorrer año a año'}
            </button>
            <p className="nota">
              El año es el de la release; la ubicación es la actual de la cuenta en Bandcamp.
            </p>
          </div>
        </Menu>

        <Menu id="mas" titulo="Más filtros" abierto={abierto} setAbierto={setAbierto} ancho={340}>
          <div className="filas">
            <p className="titulillo">UBICACIONES INCLUIDAS</p>
            {PROCEDENCIAS.map((p) => (
              <label key={p.code} className="check">
                <input type="checkbox" checked={filtros.ubic.includes(p.code)} onChange={() => alternaUbic(p.code)} />
                <span>
                  {p.label}
                  <span className="ayuda">{p.ayuda}</span>
                </span>
              </label>
            ))}
            <p className="nota">
              Por defecto quedan fuera las inferencias desde cuentas con varios artistas (probables
              sellos) y las pistas de tag. Los datos no se borran: esto solo decide qué se dibuja.
            </p>
          </div>
        </Menu>
      </div>

      {chips.length > 0 && (
        <div className="chips">
          {chips.map(([label, limpia]) => (
            <button className="chip" key={label} onClick={() => aplica(limpia)}>
              {label} <b>×</b>
            </button>
          ))}
          <button
            className="chip limpiar"
            onClick={() =>
              aplica({
                q: '',
                genero: null,
                tag: null,
                artista: null,
                desde: null,
                hasta: null,
                territorio: null,
                ubic: UBIC_DEFECTO,
              })
            }
          >
            limpiar
          </button>
          <a
            className="al-archivo"
            href={hashArchivo({
              q: qLocal,
              genero: filtros.genero,
              tag: filtros.tag,
              artista: filtros.artista,
              desde: filtros.desde,
              hasta: filtros.hasta,
            })}
          >
            ver en ARCHIVO →
          </a>
        </div>
      )}

      <div className="cobertura">
        <span>
          <b>{formato(cuenta.localizadas)}</b> releases localizadas · <b>{ranking.length}</b>{' '}
          municipios
        </span>
        <button className="enlace" onClick={() => setMetodologia((v) => !v)} aria-expanded={metodologia}>
          Cobertura y metodología {metodologia ? '↑' : '→'}
        </button>
      </div>

      {metodologia && (
        <div className="metodologia">
          <div className="cols">
            <div>
              <p className="titulillo">DIBUJADAS · {formato(cuenta.localizadas)}</p>
              <ul>
                {PROCEDENCIAS.filter((p) => filtros.ubic.includes(p.code) && cuenta[p.code]).map((p) => (
                  <li key={p.code}>
                    {p.label} <b>{formato(cuenta[p.code])}</b>
                  </li>
                ))}
                {filtros.territorio && cuenta.otroTerritorio > 0 && (
                  <li>
                    en otros territorios <b>{formato(cuenta.otroTerritorio)}</b>
                  </li>
                )}
              </ul>
            </div>
            <div>
              <p className="titulillo">EXCLUIDAS AHORA · {formato(cuenta.excluidas)}</p>
              <ul>
                {PROCEDENCIAS.filter((p) => !filtros.ubic.includes(p.code) && cuenta[p.code]).map((p) => (
                  <li key={p.code}>
                    {p.label} <b>{formato(cuenta[p.code])}</b>{' '}
                    <button className="enlace" onClick={() => alternaUbic(p.code)}>
                      incluir
                    </button>
                  </li>
                ))}
                {cuenta.excluidas === 0 && <li>ninguna</li>}
              </ul>
            </div>
            <div>
              <p className="titulillo">SIN MUNICIPIO · {formato(cuenta.sinMunicipio)}</p>
              <ul>
                <li>
                  solo región o país <b>{formato(cuenta.region_only)}</b>
                </li>
                <li>
                  fuera de Euskal Herria <b>{formato(cuenta.outside_scope)}</b>
                </li>
                <li>
                  sin resolver <b>{formato(cuenta.unresolved)}</b>
                </li>
              </ul>
            </div>
          </div>
          <p className="nota">
            La ubicación es la que Bandcamp da hoy a la cuenta que publica (grupo o sello), situada
            en el punto representativo de su municipio: es una asociación geográfica del archivo, no
            la residencia de nadie. Por defecto no se dibujan las inferencias desde cuentas con
            varios artistas ni las pistas de tag; se activan en «Más filtros». Detalle en
            docs/mapa.md.
          </p>
        </div>
      )}

      <div className="mapa-cuerpo">
        <Lienzo
          geo={geo}
          lugares={lugares}
          maxN={maxN}
          lugarSel={lugarSel?.id}
          territorio={filtros.territorio}
          filtrado={filtrado}
          debiles={debiles}
          onLugar={(id) => aplica({ lugar: id === filtros.lugar ? null : id })}
          onTerritorio={(t) => aplica({ territorio: t, lugar: null })}
        />
        <aside className="mapa-panel">{panel}</aside>
      </div>

      <FichaBar album={seleccion} onCerrar={() => setSeleccion(null)} />
    </div>
  )
}
