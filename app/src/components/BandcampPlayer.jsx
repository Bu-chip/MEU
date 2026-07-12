import { useState } from 'react'
import './BandcampPlayer.css'

// Player embebido oficial de Bandcamp (decisión 2 de Fase 0): size=large
// con tracklist, click-para-cargar (no se llama a bandcamp.com hasta que
// el usuario lo pide), bgcol papel y linkcol lima, artwork fuera porque
// la portada tratada ya preside la ficha. item_type «a» va implícito en
// la clave album=. Quien renderiza debe pasar key={album.id} para que el
// estado de carga se reinicie al cambiar de disco.
export function BandcampPlayer({ albumId }) {
  const [cargado, setCargado] = useState(false)

  if (!albumId) return null

  if (!cargado) {
    return (
      <button className="player-cargar" onClick={() => setCargado(true)}>
        ▶ CARGAR PLAYER
        <span className="sub">se conecta a bandcamp.com al pulsar</span>
      </button>
    )
  }

  const src =
    `https://bandcamp.com/EmbeddedPlayer/album=${albumId}` +
    '/size=large/bgcol=F2EFE8/linkcol=A3E635/tracklist=true/artwork=none/transparent=true/'

  return <iframe className="player-bandcamp" title="Player de Bandcamp" src={src} loading="lazy" />
}
