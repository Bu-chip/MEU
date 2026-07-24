import { supabase } from '../lib/supabase.js'
import { useAuth } from '../auth/useAuth.js'
import './Puertas.css'

// Marca de usuario: sola al extremo derecho de la barra (no es una tercera
// puerta). Solo se pinta si hay Supabase; sin cuentas la barra queda con
// EXPLORAR · ARCHIVO y nada a la derecha. El hueco del contador (nº de
// discos guardados) se deja preparado — sin pintar nada — para PR B.
function MarcaUsuario() {
  const { session, inicial } = useAuth()
  if (!supabase) return null

  // Con sesión, el destino final es #/coleccion (aún no existe): de momento
  // apunta a #/entrar, donde vive el botón de salir.
  const destino = '#/entrar'

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
        {/* PR B: hueco del contador de discos guardados, sin número aún. */}
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
