import { useState, useMemo } from 'react'
import { getIndices } from '../utils/indices.js'
import { shuffle, muroLibre, alAzarDistinto, TAM_MURO } from '../utils/azar.js'
import { FichaBar } from '../components/FichaBar.jsx'
import { miniatura } from '../utils/portadas.js'
import './Explorar.css'

// Spec congelada: design/meu-explorar-v8-deriva.html. Tres mandos de
// deriva, mini-ficha inferior como destino del click. El estado del
// muro es efímero: no va a la URL. Enmienda aprobada a la decisión 1:
// v-portada con el mismo tratamiento .tratada de la FICHA; el muro se
// lee como retícula de carátulas con la tipografía de contrapunto.

// Proporción de v-portada en el muro: 9/17 ≈ la mitad (~28-31 covers
// de 60, descontando los discos sin cover_url, que siempre caen
// tipográficos). Afinar es tocar solo esta fracción (6/17 ≈ un tercio,
// 11/17 ≈ dos tercios…), pero MANTENER el denominador impar y primo:
// la retícula tiene 3-16 columnas según el ancho y con un ratio de
// vuelta par (1/2 exacto, 1/4…) el patrón se alinea con las columnas
// y salen rayas verticales de portadas.
const RATIO_PORTADA = 9 / 17

// Rotación tipográfica del mockup: ocupa los huecos que deja v-portada.
const TIPOGRAFICAS = [
  'v-inicial', 'v-negra', 'v-titulo', 'v-inicial',
  'v-split', 'v-negra', 'v-inicial', 'v-titulo',
]

// Variante por posición en el muro: v-portada repartida al RATIO_PORTADA
// (acumulador tipo Bresenham), el resto recorre la rotación tipográfica
// sin saltarse ninguna.
function varianteEn(i) {
  const previas = Math.floor(i * RATIO_PORTADA)
  if (Math.floor((i + 1) * RATIO_PORTADA) > previas) return 'v-portada'
  return TIPOGRAFICAS[(i - previas) % TIPOGRAFICAS.length]
}

// Sustitutas tipográficas para los discos sin cover_url (27) o con la
// imagen rota: estables por disco para que regenerar el muro no baile.
const RESERVAS = ['v-inicial', 'v-negra', 'v-titulo', 'v-split']

function Tile({ album, variante, onAbrir }) {
  const [rota, setRota] = useState(false)
  if (variante === 'v-portada' && (!album.cover_url || rota)) {
    variante = RESERVAS[album.id % RESERVAS.length]
  }
  const inicial = (album.artist || '?').trim().charAt(0).toUpperCase()
  const metaGY = (album.genre || '') + (album.year ? ' · ' + album.year : '')

  return (
    <div
      className={`tile ${variante}`}
      tabIndex={0}
      onClick={onAbrir}
      onKeyDown={(e) => {
        if (e.key === 'Enter') onAbrir()
      }}
    >
      {variante === 'v-negra' && <div className="tt">{album.title}</div>}
      {variante === 'v-inicial' && (
        <>
          <div className="ini">{inicial}</div>
          <div className="aa">{album.artist}</div>
        </>
      )}
      {variante === 'v-split' && (
        <>
          <div className="top">{album.artist}</div>
          <div className="bot">{album.title}</div>
        </>
      )}
      {variante === 'v-titulo' && <div className="big">{album.title}</div>}
      {variante === 'v-portada' && (
        <>
          <img
            className="tratada"
            src={miniatura(album.cover_url)}
            alt=""
            loading="lazy"
            decoding="async"
            onError={() => setRota(true)}
          />
          <div className="pa">{album.artist}</div>
        </>
      )}
      <div className="meta">
        <div>
          <div className="a">{album.artist}</div>
          <div className="t">{album.title}</div>
        </div>
        <div className="g">
          <span>{metaGY}</span>
          <span className="play">▶</span>
        </div>
      </div>
    </div>
  )
}

export function Explorar({ archive }) {
  // modo: null = deriva libre | {tipo:'tag'|'anio', valor, total}
  const [modo, setModo] = useState(null)
  // Muro inicial sembrado una vez por archivo; los mandos lo sustituyen.
  const semilla = useMemo(() => archive && muroLibre(archive.albums), [archive])
  const [regenerado, setMuro] = useState(null)
  const muro = regenerado ?? semilla
  const [seleccion, setSeleccion] = useState(null)

  const idx = archive ? getIndices(archive) : null
  const years = archive?.years ?? []

  if (!archive) {
    return <p className="cargando">cargando archivo…</p>
  }

  const masDiscos = () => {
    if (modo?.tipo === 'tag') {
      setMuro(shuffle(idx.tagIndex.get(modo.valor)).slice(0, TAM_MURO))
    } else if (modo?.tipo === 'anio') {
      setMuro(shuffle(archive.albums.filter((a) => a.year === modo.valor)).slice(0, TAM_MURO))
    } else {
      setMuro(muroLibre(archive.albums))
    }
  }

  const generoAzar = () => {
    const tag = alAzarDistinto(idx.tagsElegibles, modo?.tipo === 'tag' ? modo.valor : null)
    const releases = idx.tagIndex.get(tag)
    setModo({ tipo: 'tag', valor: tag, total: releases.length })
    setMuro(shuffle(releases).slice(0, TAM_MURO))
  }

  const anioAzar = () => {
    const anio = alAzarDistinto(years, modo?.tipo === 'anio' ? modo.valor : null)
    const releases = archive.albums.filter((a) => a.year === anio)
    setModo({ tipo: 'anio', valor: anio, total: releases.length })
    setMuro(shuffle(releases).slice(0, TAM_MURO))
  }

  const derivaLibre = () => {
    setModo(null)
    setMuro(muroLibre(archive.albums))
  }

  return (
    <>
      <div className="mandos">
        <div className="fila-botones">
          <button className="mando" id="m-discos" onClick={masDiscos}>
            ⟳ MÁS DISCOS
            <span className="sub">rehace el muro · {TAM_MURO} al azar</span>
          </button>
          <button className="mando" onClick={generoAzar}>
            ⚄ GÉNERO AL AZAR
            <span className="sub">caes en uno de {idx.tagsElegibles.length} estilos</span>
          </button>
          <button className="mando" onClick={anioAzar}>
            ⚁ AÑO AL AZAR
            <span className="sub">
              caes entre {years[0]} y {years[years.length - 1]}
            </span>
          </button>
          <span className="archivo-link">
            ¿buscas algo concreto? <a href="#/archivo">ARCHIVO →</a>
          </span>
        </div>
        <div className="donde">
          {modo ? (
            <>
              <span className="donde-pre">has caído en</span>
              <span className="tagname">{modo.valor}</span>
              <span className="donde-n">
                {modo.total} {modo.total === 1 ? 'release' : 'releases'}
              </span>
              <button className="salir" onClick={derivaLibre}>
                × deriva libre
              </button>
            </>
          ) : (
            <span className="donde-libre">deriva libre · archivo entero</span>
          )}
        </div>
      </div>

      <div className="grid">
        {(muro ?? []).map((album, i) => (
          <Tile
            key={album.id}
            album={album}
            variante={varianteEn(i)}
            onAbrir={() => setSeleccion(album)}
          />
        ))}
      </div>

      <footer className="pie">
        MÁS DISCOS: regenera el muro con 60 discos al azar. GÉNERO AL AZAR: filtra el
        muro por un estilo aleatorio. AÑO AL AZAR: filtra por un año. Género y año no se
        combinan. Para buscar o filtrar a voluntad, usa ARCHIVO.
      </footer>

      <FichaBar album={seleccion} onCerrar={() => setSeleccion(null)} />
    </>
  )
}
