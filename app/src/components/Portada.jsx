import { useState } from 'react'
import './Portada.css'

// Portada de la FICHA (único lugar con imagen: decisión 1 de Fase 0).
// Tratamiento CSS aprobado (decisión 3): grayscale + contrast + multiply
// sobre papel — nunca foto limpia. Los null (27: 11 borrados + 16 sin
// página) y los errores de carga caen en el hueco honesto del mockup.
// La URL canónica _5 (~700px) basta para la columna de ≤420px; derivar
// otros sufijos del CDN queda pendiente de verificación en producción.
export function Portada({ album }) {
  const [rota, setRota] = useState(false)

  if (!album.cover_url || rota) {
    const titulo = album.title.length > 40 ? album.title.slice(0, 40) + '…' : album.title
    return (
      <div className="portada vacia">
        <span className="aviso">
          {album.cover_url ? 'PORTADA NO DISPONIBLE' : 'SIN PORTADA · HUECO HONESTO'}
        </span>
        <div className="ph">{titulo}</div>
      </div>
    )
  }

  return (
    <div className="portada">
      <img
        src={album.cover_url}
        alt={`Portada de ${album.title}`}
        loading="lazy"
        decoding="async"
        onError={() => setRota(true)}
      />
    </div>
  )
}
