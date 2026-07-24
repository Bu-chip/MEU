import { useState, useEffect, useMemo } from 'react'
import { useAuth } from '../auth/useAuth.js'
import { useColeccion } from '../hooks/useColeccion.js'
import { reemplazar } from '../hooks/useHashRoute.js'
import { formato } from '../utils/formato.js'
import { Tile } from '../components/Tile.jsx'
import { FichaBar } from '../components/FichaBar.jsx'
import './Coleccion.css'

// COLECCIÓN: los guardados del usuario como muro, con el mismo tile de
// EXPLORAR en v-portada (la sustituta tipográfica cubre los discos sin
// cover). Orden: guardado más reciente primero (el `orden` de useColeccion).
// Sin corte de 60: aquí se pintan todos. Cada tile lleva su corazón lleno
// para quitar sin pasar por la ficha; el singleton de useColeccion hace que
// desaparezca del muro y baje el contador en el acto. El click en el tile
// abre la misma mini-ficha inferior que en EXPLORAR.
export function Coleccion({ archive }) {
  const { session, cargando: cargandoSesion, salir } = useAuth()
  const { orden, quitar, cargando } = useColeccion()
  const [seleccion, setSeleccion] = useState(null)

  // Página con dueño: sin sesión, a #/entrar. Con replace, no con navegar:
  // atrás no debe devolver a una colección que no se puede ver.
  useEffect(() => {
    if (!cargandoSesion && !session) reemplazar('#/entrar')
  }, [cargandoSesion, session])

  const porId = useMemo(
    () => (archive ? new Map(archive.albums.map((a) => [a.id, a])) : null),
    [archive]
  )

  if (!archive || cargandoSesion || (session && cargando)) {
    return <p className="cargando">cargando colección…</p>
  }
  if (!session) return null // redirigiendo a #/entrar

  // Ids huérfanos (guardados que ya no están en el JSON) se omiten sin
  // romper: el contador cuenta lo que el muro enseña.
  const discos = orden.map((id) => porId.get(id)).filter(Boolean)

  return (
    <main className="coleccion-pagina">
      <header className="coleccion-cab">
        <h1>COLECCIÓN</h1>
        <p className="escala">
          {formato(discos.length)} / {formato(archive.albums.length)} discos
        </p>
      </header>

      {discos.length === 0 ? (
        <div className="coleccion-vacia">
          <p>todavía no has guardado ningún disco.</p>
          <p>guárdalos desde su ficha, con el corazón.</p>
        </div>
      ) : (
        <div className="grid">
          {discos.map((album) => (
            <Tile
              key={album.id}
              album={album}
              variante="v-portada"
              onAbrir={() => setSeleccion(album)}
              quitar={() => quitar(album.id)}
            />
          ))}
        </div>
      )}

      {/* SALIR vive aquí (antes en #/entrar): al pie, discreto, en mono.
          Al cerrar sesión el efecto de arriba ya manda a #/entrar. */}
      <footer className="coleccion-pie">
        <button className="salir" onClick={salir}>
          SALIR
        </button>
      </footer>

      <FichaBar album={seleccion} onCerrar={() => setSeleccion(null)} />
    </main>
  )
}
