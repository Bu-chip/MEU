import { useEffect } from 'react'
import { BandcampPlayer } from './BandcampPlayer.jsx'
import { Corazon } from './Corazon.jsx'
import { useCompartir } from '../hooks/useCompartir.js'
import { useGuardar } from '../hooks/useGuardar.js'
import { supabase } from '../lib/supabase.js'
import './FichaBar.css'

// Mini-ficha inferior de los mockups: respuesta inmediata al click en
// disco sin perder el muro ni el scroll; desde aquí, FICHA → profundiza.
// Con player small (42px) que carga al abrir; el key por disco garantiza
// que saltar de tile a tile desmonta el iframe anterior (nunca dos
// sonando a la vez). Los 27 sin album_id no muestran player ni hueco.
export function FichaBar({ album, onCerrar }) {
  const { compartir, copiado } = useCompartir(album)
  const { guardado, alternar } = useGuardar(album)

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

  // El modificador con-player abre la columna central del grid: sin
  // album_id la fila ni siquiera reserva el espacio del player.
  return (
    <div className={`ficha-bar${album.album_id ? ' con-player' : ''}`}>
      <button className="cerrar" onClick={onCerrar}>
        × cerrar
      </button>
      <div>
        <div className="fa">{album.artist}</div>
        <div className="ft">{album.title}</div>
        <div className="fmeta">{meta}</div>
      </div>
      {album.album_id && (
        <div className="player-mini" key={album.id}>
          <BandcampPlayer albumId={album.album_id} size="small" />
        </div>
      )}
      <div className="acciones">
        {/* Compartir compacto: mismo useCompartir que la FICHA; el aviso
            del fallback aquí es el swap de glifo ↑ → ✓ (U+2713, sin
            variante emoji, monocromo garantizado). Clase propia
            compartir-mini: esta columna también se llama .acciones y la
            regla .acciones button.compartir de Ficha.css la alcanzaría. */}
        <div className="fila-acciones">
          <button className="compartir-mini" onClick={compartir} aria-label="compartir" title="compartir">
            {copiado ? '✓' : '↑'}
          </button>
          {/* Guardar compacto: solo el corazón (aquí compartir también es
              solo glifo), mismo useGuardar que la FICHA — el singleton de
              useColeccion mantiene ambos botones en el mismo estado. Sobre
              el fondo tinta de la barra hereda papel vía currentColor. */}
          {supabase && (
            <button
              className="guardar-mini"
              onClick={alternar}
              aria-label={guardado ? 'guardado' : 'guardar'}
              title={guardado ? 'guardado' : 'guardar'}
            >
              <Corazon lleno={guardado} />
            </button>
          )}
          <a className="ir-ficha" href={`#/disco/${album.id}`}>
            FICHA →
          </a>
        </div>
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
    </div>
  )
}
