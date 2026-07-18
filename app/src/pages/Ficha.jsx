import { useEffect, useState } from 'react'
import { getIndices } from '../utils/indices.js'
import { similares } from '../utils/similares.js'
import { navegar, hashArchivo } from '../hooks/useHashRoute.js'
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
// COMPARTIR entrega la URL del stub estático /d/:id/ (og:tags por disco),
// no el hash: es lo que hace que el chat pinte portada y título. Dominio
// fijo a propósito — también desde dev se comparte la URL de producción,
// que es la única con stub detrás.
const DOMINIO = 'https://mapa.queimadacircuitrecords.com'

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
  // El aviso ENLACE COPIADO guarda el id del disco copiado, no un booleano:
  // así muere solo al navegar a otra ficha, sin efecto que lo resetee.
  const [copiadoId, setCopiadoId] = useState(null)

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

  const album = getIndices(archive).byId.get(route.id)

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

  // Web Share donde exista (Safari iPad: hoja nativa del sistema); si no,
  // copiar al portapapeles con aviso efímero en el propio botón. Cancelar
  // la hoja lanza AbortError: no es un error, se traga.
  const compartir = async () => {
    const url = `${DOMINIO}/d/${album.id}/`
    if (navigator.share) {
      try {
        await navigator.share({ title: `${album.artist} — ${album.title}`, url })
      } catch {
        /* hoja cancelada */
      }
    } else {
      await navigator.clipboard.writeText(url)
      setCopiadoId(album.id)
      setTimeout(() => setCopiadoId(null), 2000)
    }
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
              {copiadoId === album.id ? 'ENLACE COPIADO' : 'COMPARTIR ↑'}
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
