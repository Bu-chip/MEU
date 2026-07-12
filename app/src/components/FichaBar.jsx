import { useEffect } from 'react'
import { BandcampPlayer } from './BandcampPlayer.jsx'
import './FichaBar.css'

// Mini-ficha inferior de los mockups: respuesta inmediata al click en
// disco sin perder el muro ni el scroll; desde aquí, FICHA → profundiza.
// Con player small (42px) que carga al abrir; el key por disco garantiza
// que saltar de tile a tile desmonta el iframe anterior (nunca dos
// sonando a la vez). Los 27 sin album_id no muestran player ni hueco.
export function FichaBar({ album, onCerrar }) {
  useEffect(() => {
    if (!album) return
    const onKey = (e) => {
      if (e.key === 'Escape') onCerrar()
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [album, onCerrar])

  if (!album) return null

  const meta = (album.genre || '') + (album.year ? ' · ' + album.year : '')

  return (
    <div className="ficha-bar">
      <button className="cerrar" onClick={onCerrar}>
        × cerrar
      </button>
      <div>
        <div className="fa">{album.artist}</div>
        <div className="ft">{album.title}</div>
        <div className="fmeta">{meta}</div>
      </div>
      <div className="acciones">
        <a className="ir-ficha" href={`#/disco/${album.id}`}>
          FICHA →
        </a>
        {album.url && album.album_id ? (
          <a href={album.url} target="_blank" rel="noopener noreferrer">
            abrir en bandcamp ↗
          </a>
        ) : (
          // 11 borrados (url muerta) y 16 sin url: aviso honesto, nunca
          // link muerto — mismo criterio que la FICHA
          <span className="stub">
            {album.url ? 'ya no está en bandcamp' : 'sin página en bandcamp'}
          </span>
        )}
      </div>
      {album.album_id && (
        <div className="player-mini" key={album.id}>
          <BandcampPlayer albumId={album.album_id} size="small" />
        </div>
      )}
    </div>
  )
}
