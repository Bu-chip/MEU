import { useEffect } from 'react'
import './FichaBar.css'

// Mini-ficha inferior de los mockups: destino provisional del click en
// disco hasta que F4 traiga la FICHA completa (#/disco/:id).
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
        {album.url ? (
          <a href={album.url} target="_blank" rel="noopener noreferrer">
            abrir en bandcamp ↗
          </a>
        ) : (
          <span className="stub">sin página en bandcamp</span>
        )}
        <span className="stub">ficha completa → fase 4</span>
      </div>
    </div>
  )
}
