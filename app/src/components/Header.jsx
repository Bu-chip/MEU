import { formato } from '../utils/formato.js'
import './Header.css'

// Contadores SIEMPRE calculados de los datos (decisión 8 de Fase 0),
// nunca hardcodeados: los mockups arrastran cifras viejas (2.396/1.069).

// `compacta`: en MAPA la cabecera cede el sitio al mapa (el elemento
// dominante de esa vista). Mantiene identidad y acceso a SOBRE, pero deja
// fuera los contadores globales y la firma, que allí competirían con los
// contadores de cobertura del propio mapa.
export function Header({ archive, compacta = false }) {
  const years = archive?.years ?? []
  const rango = years.length ? `${years[0]}–${years[years.length - 1]}` : '—'

  if (compacta) {
    return (
      <header className="cabecera compacta">
        <h1 className="logotype">
          <a href="#/">
            MAPA EUSKADI<span className="l2">UNDERGROUND</span>
          </a>
        </h1>
        <a className="sobre-link" href="#/sobre">
          sobre el proyecto
        </a>
      </header>
    )
  }

  return (
    <>
      <header className="cabecera">
        <div>
          <h1 className="logotype">
            <a href="#/">
              MAPA EUSKADI<span className="l2">UNDERGROUND</span>
            </a>
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
          la guía de{' '}
          <a
            className="qcr-link"
            href="https://queimadacircuitrecords.com"
            target="_blank"
            rel="noopener"
          >
            <b>Queimada Circuit Records</b>
          </a>{' '}
          a la música underground de Euskadi
        </span>
        <a className="sobre-link firma-enlace" href="#/sobre">
          sobre el proyecto
        </a>
      </p>
    </>
  )
}
