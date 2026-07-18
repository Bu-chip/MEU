import { useState } from 'react'

// Lógica de COMPARTIR común a la FICHA y al FichaBar (F6). La URL
// compartida es la del stub estático /d/:id/ (og:tags por disco), no el
// hash: es lo que hace que el chat pinte portada y título. Dominio fijo
// a propósito — también desde dev se comparte la URL de producción, que
// es la única con stub detrás.
const DOMINIO = 'https://mapa.queimadacircuitrecords.com'

// Web Share donde exista (Safari iPad: hoja nativa del sistema); si no,
// copiar al portapapeles y avisar ~2 s — cada componente pinta el aviso
// a su manera (texto ENLACE COPIADO en la FICHA, glifo ✓ en el FichaBar).
// Cancelar la hoja lanza AbortError: no es un error, se traga.
//
// El aviso guarda el id del disco copiado, no un booleano: así muere
// solo al cambiar de disco, sin efecto que lo resetee. `album` puede
// llegar null/undefined (los componentes llaman al hook antes de sus
// early-returns, por las reglas de hooks); compartir solo se invoca
// desde botones que ya renderizan con álbum resuelto.
export function useCompartir(album) {
  const [copiadoId, setCopiadoId] = useState(null)

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

  return { compartir, copiado: album != null && copiadoId === album.id }
}
