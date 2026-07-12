import './BandcampPlayer.css'

// Player embebido oficial de Bandcamp. Enmienda a la decisión 2 de Fase 0:
// carga automática (sin click-para-cargar) en sus dos formatos —
//   large → FICHA: tracklist, artwork fuera (la portada tratada ya preside)
//   small → mini-ficha: barra de 42px
// bgcol papel y linkcol lima en ambos. item_type «a» va implícito en la
// clave album=. Con album_id null (27 discos) no renderiza nada: el hueco
// lo gestiona quien llama. Quien renderiza debe pasar key={album.id} para
// que el cambio de disco desmonte el iframe anterior (nunca dos sonando).
export function BandcampPlayer({ albumId, size = 'large' }) {
  if (!albumId) return null

  const params =
    size === 'small'
      ? '/size=small/bgcol=F2EFE8/linkcol=A3E635/transparent=true/'
      : '/size=large/bgcol=F2EFE8/linkcol=A3E635/tracklist=true/artwork=none/transparent=true/'

  return (
    <iframe
      className={`player-bandcamp ${size}`}
      title="Player de Bandcamp"
      src={`https://bandcamp.com/EmbeddedPlayer/album=${albumId}${params}`}
    />
  )
}
