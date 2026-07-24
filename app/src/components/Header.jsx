import { formato } from '../utils/formato.js'
import './Header.css'

// Contadores SIEMPRE calculados de los datos (decisión 8 de Fase 0),
// nunca hardcodeados: los mockups arrastran cifras viejas (2.396/1.069).

export function Header({ archive }) {
  const years = archive?.years ?? []
  const rango = years.length ? `${years[0]}–${years[years.length - 1]}` : '—'

  return (
    <>
      <header className="cabecera">
        <div>
          <h1 className="logotype">
            MAPA EUSKADI<span className="l2">UNDERGROUND</span>
          </h1>
        </div>
        <div className="counters">
          {/* «sobre el proyecto» encabeza la columna en escritorio; en móvil
              se oculta y el enlace pasa a la línea de la firma. Los «·» solo
              se pintan en móvil, donde las cifras van corridas en línea. */}
          <a className="sobre-link" href="#/sobre">
            sobre el proyecto
          </a>
          <span className="dato">
            <b>{archive ? formato(archive.albums.length) : '—'}</b> releases
          </span>
          <span className="sep">·</span>
          <span className="dato">
            <b>{archive ? formato(archive.artists.length) : '—'}</b> artistas
          </span>
          <span className="sep">·</span>
          <span className="dato">
            <b>{rango}</b> · bandcamp
          </span>
        </div>
      </header>
      <p className="firma">
        <span>
          la guía de <b>Queimada Circuit Records</b> a la música underground de Euskadi
        </span>
        <a className="sobre-link firma-enlace" href="#/sobre">
          sobre el proyecto
        </a>
      </p>
    </>
  )
}
