import { useEffect } from 'react'
import './FichaBar.css'

// Mini-ficha inferior de los mockups: respuesta inmediata al click en
// disco sin perder el muro ni el scroll; desde aquí, FICHA → profundiza.
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
        {album.url ? (
          <a href={album.url} target="_blank" rel="noopener noreferrer">
            abrir en bandcamp ↗
          </a>
        ) : (
          <span className="stub">sin página en bandcamp</span>
        )}
      </div>
    </div>
  )
}
