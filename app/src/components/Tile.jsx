import { useState } from 'react'
import { Corazon } from './Corazon.jsx'
import { miniatura } from '../utils/portadas.js'
import './Tile.css'

// Tile del muro, extraído de Explorar.jsx al compartirse con COLECCIÓN:
// mismas variantes (spec meu-explorar-v8-deriva), mismo tratamiento .tratada
// de las portadas y mismo hueco honesto —sustituta tipográfica— para los
// discos sin cover o con la imagen rota.

// Sustitutas tipográficas para los discos sin cover_url (27) o con la
// imagen rota: estables por disco para que regenerar el muro no baile.
const RESERVAS = ['v-inicial', 'v-negra', 'v-titulo', 'v-split']

export function Tile({ album, variante, onAbrir, quitar }) {
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
      {/* Corazón de quitar (solo COLECCIÓN): esquina superior derecha, donde
          no pisa ni la etiqueta de artista (abajo) ni el cuerpo de las
          variantes tipográficas. Va tras .meta y con z-index para seguir
          clicable con el encendido lima del hover. */}
      {quitar && (
        <button
          className="tile-quitar"
          onClick={(e) => {
            e.stopPropagation()
            quitar()
          }}
          aria-label="quitar de la colección"
          title="quitar de la colección"
        >
          <Corazon lleno size={12} />
        </button>
      )}
    </div>
  )
}
