import { useState, useMemo } from 'react'
import { getIndices } from '../utils/indices.js'
import { shuffle, muroLibre, alAzarDistinto, TAM_MURO } from '../utils/azar.js'
import { FichaBar } from '../components/FichaBar.jsx'
import './Explorar.css'

// Spec congelada: design/meu-explorar-v8-deriva.html. Muro tipográfico
// (sin portadas, decisión 1), tres mandos de deriva, mini-ficha inferior
// como destino del click. El estado del muro es efímero: no va a la URL.

// Rotación de variantes tipográficas del mockup, por posición en el muro.
const VARIANTES = [
  'v-inicial', 'v-negra', 'v-titulo', 'v-inicial',
  'v-split', 'v-negra', 'v-inicial', 'v-titulo',
]

function Tile({ album, variante, onAbrir }) {
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
            variante={VARIANTES[i % VARIANTES.length]}
            onAbrir={() => setSeleccion(album)}
          />
        ))}
      </div>

      <footer className="pie">
        tres verbos, cero cajones: MÁS DISCOS rehace el muro con azar del archivo entero
        (variedad de géneros garantizada) · GÉNERO AL AZAR te deja caer en un estilo que
        no has elegido — dungeon synth, horror disco, poky… — y AÑO AL AZAR en un año
        entre {years[0]} y {years[years.length - 1]} (a veces con 3 discos: eso también
        es el archivo); el nombre o el año preside el muro; repetir = caer en otro; × =
        deriva libre; género y año no se combinan — combinar es filtrar, y filtrar es de
        la otra puerta · aquí no se elige ni se busca: para eso está la otra puerta
      </footer>

      <FichaBar album={seleccion} onCerrar={() => setSeleccion(null)} />
    </>
  )
}
