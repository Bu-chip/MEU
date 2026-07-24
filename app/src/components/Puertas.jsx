import { supabase } from '../lib/supabase.js'
import { useAuth } from '../auth/useAuth.js'
import { useColeccion } from '../hooks/useColeccion.js'
import { formato } from '../utils/formato.js'
import './Puertas.css'

// Marca de usuario: sola al extremo derecho de la barra (no es una tercera
// puerta). Solo se pinta si hay Supabase; sin cuentas la barra queda con
// EXPLORAR · ARCHIVO y nada a la derecha. Con sesión lleva al lado el
// contador de discos guardados (PR B).
function MarcaUsuario() {
  const { session, inicial } = useAuth()
  const { ids } = useColeccion()
  if (!supabase) return null

  // Con sesión, la marca lleva a la colección (SALIR también vive allí).
  const destino = '#/coleccion'

  // Zócalo = tres piezas en flex (patitas · inicial · patitas): el hueco lo
  // fija el CSS (gap), idéntico para cualquier inicial, sin depender del
  // ancho del glifo.
  const patitas = (
    <svg viewBox="0 0 5 36" width="4" height="24" aria-hidden="true">
      <path d="M0 12h5M0 18h5M0 24h5" stroke="currentColor" strokeWidth="2.2" />
    </svg>
  )

  if (session) {
    return (
      <a className="marca-usuario dentro" href={destino} title="tu cuenta" aria-label="tu cuenta">
        <span className="marca-chip">
          {patitas}
          <span className="marca-inicial">{inicial}</span>
          {patitas}
        </span>
        {/* El contador nace con el primer disco (con cero no se pinta) y se
            mueve en vivo al guardar/quitar vía el singleton de useColeccion.
            Sin capar: punto de millar como el 7.568 de la cabecera. */}
        {ids.size > 0 && <span className="marca-cuenta">{formato(ids.size)}</span>}
      </a>
    )
  }

  return (
    <a className="marca-usuario" href="#/entrar" title="entrar" aria-label="entrar">
      <span className="marca-chip">
        {patitas}
        {patitas}
      </span>
      <span className="marca-txt">ENTRAR</span>
    </a>
  )
}

export function Puertas({ activa }) {
  return (
    <nav className="puertas">
      <a href="#/" className={`puerta ${activa === 'explorar' ? 'activa' : ''}`}>
        EXPLORAR
      </a>
      <a href="#/archivo" className={`puerta ${activa === 'archivo' ? 'activa' : ''}`}>
        ARCHIVO
      </a>
      <MarcaUsuario />
    </nav>
  )
}
