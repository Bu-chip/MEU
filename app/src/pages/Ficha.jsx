import { useEffect } from 'react'
import { getIndices } from '../utils/indices.js'
import { similares } from '../utils/similares.js'
import { navegar, hashArchivo } from '../hooks/useHashRoute.js'
import { useCompartir } from '../hooks/useCompartir.js'
import { Portada } from '../components/Portada.jsx'
import { BandcampPlayer } from '../components/BandcampPlayer.jsx'
import './Ficha.css'

// Spec congelada: design/meu-ficha-v1.html + extensiones de Fase 0
// (decisión 2 enmendada: el player carga automáticamente al entrar), tags
// clicables que aterrizan en #/archivo?tag=…, similares al vuelo.
// Sin header ni puertas: la ficha abre con su barra de retorno (mockup).
//
// Las tres poblaciones del archivo, distinguibles por los datos:
//   ok      → url y album_id presentes: ESCUCHAR + player
//   borrado → album_id null con url presente (11): aviso honesto,
//             sin link muerto ni player
//   sinurl  → url null (16): ficha documental, sin ESCUCHAR ni player
//
// COMPARTIR: lógica y racional en hooks/useCompartir.js (compartida con
// el FichaBar); aquí el aviso del fallback es el texto ENLACE COPIADO.

function Retorno() {
  return (
    <div className="retorno">
      <a href="#/">← EXPLORAR</a>
      <a href="#/archivo">← ARCHIVO</a>
      <span className="marca">MAPA EUSKADI UNDERGROUND · QCR</span>
    </div>
  )
}

export function Ficha({ route, archive }) {
  // El álbum se resuelve antes de los early-returns porque el hook de
  // compartir (reglas de hooks) debe llamarse incondicionalmente.
  const album = archive ? getIndices(archive).byId.get(route.id) : null
  const { compartir, copiado } = useCompartir(album)

  useEffect(() => {
    window.scrollTo(0, 0)
  }, [route.id])

  if (!archive) {
    return (
      <>
        <Retorno />
        <p className="cargando">cargando archivo…</p>
      </>
    )
  }

  if (!album) {
    return (
      <>
        <Retorno />
        <div className="no-encontrado">
          <p className="que">REGISTRO NO ENCONTRADO</p>
          <p className="cuando">
            el id {route.id} no existe en el archivo (los huecos en la numeración son bajas
            históricas) · vuelve a <a href="#/">EXPLORAR</a> o al <a href="#/archivo">ARCHIVO</a>
          </p>
        </div>
      </>
    )
  }

  const poblacion = album.url ? (album.album_id ? 'ok' : 'borrado') : 'sinurl'
  const sims = similares(archive.albums, album)

  const otroAzar = () => {
    let otro
    do {
      otro = archive.albums[Math.floor(Math.random() * archive.albums.length)]
    } while (otro.id === album.id)
    navegar(`#/disco/${otro.id}`)
  }

  return (
    <>
      <Retorno />

      <div className="cuerpo">
        <Portada key={album.id} album={album} />
        <div className="datos">
          <h1 className="art">{album.artist}</h1>
          <div className="tit">{album.title}</div>
          <div className="metaline">
            <span className="m">
              AÑO <b>{album.year || 's/f'}</b>
            </span>
            <span className="m">
              GÉNERO <b>{album.genre || '—'}</b>
            </span>
            <span className="m">
              FUENTE <b>bandcamp</b>
            </span>
          </div>
          <div className="tags">
            {album.tags.map((tag) => (
              <a key={tag} href={hashArchivo({ tag })}>
                {tag}
              </a>
            ))}
          </div>
          <div className="acciones">
            {poblacion === 'ok' && (
              <a className="principal" href={album.url} target="_blank" rel="noopener noreferrer">
                ESCUCHAR EN BANDCAMP ↗
              </a>
            )}
            {poblacion === 'borrado' && (
              <span className="principal ausente">YA NO ESTÁ EN BANDCAMP</span>
            )}
            {poblacion === 'sinurl' && (
              <span className="principal ausente">SIN PÁGINA EN BANDCAMP · FICHA DOCUMENTAL</span>
            )}
            <button className="azar" onClick={otroAzar}>
              OTRO AL AZAR ⟳
            </button>
            <button className="compartir" onClick={compartir}>
              {copiado ? 'ENLACE COPIADO' : 'COMPARTIR ↑'}
            </button>
          </div>
          {poblacion === 'ok' && (
            <div className="player">
              <BandcampPlayer key={album.id} albumId={album.album_id} />
            </div>
          )}
        </div>
      </div>

      <div className="similares">
        <h2>
          CERCA DE ESTE <span className="c">por tags compartidos</span>
        </h2>
        {sims.length === 0 && (
          <p className="solo">nada cerca: este disco está solo en su esquina del archivo</p>
        )}
        {sims.map(([otro, ov]) => (
          <div className="sim" key={otro.id} onClick={() => navegar(`#/disco/${otro.id}`)}>
            <span className="y">{otro.year || 's/f'}</span>
            <span className="ar">{otro.artist}</span>
            <span className="ti">{otro.title}</span>
            <span className="ge">{otro.genre || '—'}</span>
            <span className="ov">
              {ov} {ov === 1 ? 'tag' : 'tags'}
            </span>
          </div>
        ))}
      </div>

      <footer className="pie">
        Toca un tag para filtrar ARCHIVO por él. OTRO AL AZAR abre otra ficha cualquiera.
        Si el disco no tiene portada en Bandcamp, se muestra un hueco en su lugar.
      </footer>
    </>
  )
}
