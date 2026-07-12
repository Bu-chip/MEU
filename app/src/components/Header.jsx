import { formato } from '../utils/formato.js'
import './Header.css'

// Contadores SIEMPRE calculados de los datos (decisión 8 de Fase 0),
// nunca hardcodeados: los mockups arrastran cifras viejas (2.396/1.069).

export function Header({ archive, size = 'grande' }) {
  const years = archive?.years ?? []
  const rango = years.length ? `${years[0]}–${years[years.length - 1]}` : '—'

  return (
    <>
      <header className={`cabecera ${size}`}>
        <div>
          <h1 className="logotype">
            MAPA EUSKADI<span className="l2">UNDERGROUND</span>
          </h1>
        </div>
        <div className="counters">
          <b>{archive ? formato(archive.albums.length) : '—'}</b> releases
          <br />
          <b>{archive ? formato(archive.artists.length) : '—'}</b> artistas
          <br />
          <b>{rango}</b> · bandcamp
        </div>
      </header>
      <p className="firma">
        la guía de <b>Queimada Circuit Records</b> a la música underground de Euskadi
      </p>
    </>
  )
}
