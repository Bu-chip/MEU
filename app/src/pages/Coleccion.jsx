import { useState, useEffect, useMemo } from 'react'
import { useAuth } from '../auth/useAuth.js'
import { useColeccion } from '../hooks/useColeccion.js'
import { useVistos } from '../hooks/useVistos.js'
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
  const { session, cargando: cargandoSesion, salir, nombre, inicial } = useAuth()
  const { orden, quitar, cargando } = useColeccion()
  const { ids: vistos } = useVistos()
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

  const total = archive.albums.length

  return (
    <main className="coleccion-pagina">
      <header className="coleccion-cab">
        {/* Fila superior equilibrada: el titular a un lado y el bloque de
            cuenta al otro. El bloque agrupa quién eres (nombre de Google si
            lo hay, si no la inicial — nunca el email) sobre SALIR, alineado a
            la derecha; antes iban sueltos (nombre arriba-izquierda, SALIR
            arriba-derecha) y quedaban descolocados en iPad y móvil. */}
        <div className="cab-fila">
          <h1>COLECCIÓN</h1>
          <div className="cuenta-barra">
            <span className="cuenta-quien">{nombre || inicial}</span>
            <button className="salir" onClick={salir}>
              SALIR
            </button>
          </div>
        </div>
        {/* Dos ejes independientes: guardar es intención (guardados, lima);
            haber pasado por un disco es recorrido (vistos, tinta). Cifras
            siempre calculadas del dato, con el punto de millar de la cabecera. */}
        <p className="escala guardados">
          <b>{formato(discos.length)}</b> / {formato(total)} guardados
        </p>
        <p className="escala vistos">
          <b>{formato(vistos.size)}</b> / {formato(total)} vistos
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

      {/* SALIR se subió a la barra de cuenta de la cabecera (antes vivía aquí
          al pie): cerrar sesión es una opción básica y debe descubrirse sin
          bajar hasta el final del muro. Al salir, el efecto de arriba manda a
          #/entrar. */}
      <FichaBar album={seleccion} onCerrar={() => setSeleccion(null)} />
    </main>
  )
}
