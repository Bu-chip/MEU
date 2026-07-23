import { supabase } from '../lib/supabase.js'
import { useAuth } from '../auth/useAuth.js'
import './Puertas.css'

// Marca de usuario: al extremo derecho de la barra, DESPUÉS de «sobre el
// proyecto» (no es una tercera puerta). Solo se pinta si hay Supabase; sin
// cuentas la barra queda exactamente como estaba. El hueco del contador
// (nº de discos guardados) se deja preparado — sin pintar nada — para PR B.
function MarcaUsuario() {
  const { session, inicial } = useAuth()
  if (!supabase) return null

  // Con sesión, el destino final es #/coleccion (aún no existe): de momento
  // apunta a #/entrar, donde vive el botón de salir.
  const destino = '#/entrar'

  if (session) {
    return (
      <a className="marca-usuario dentro" href={destino} title="tu cuenta" aria-label="tu cuenta">
        <svg viewBox="0 0 36 36" width="24" height="24" aria-hidden="true">
          <g stroke="currentColor" strokeWidth="2.2">
            <path d="M5 12h4M5 18h4M5 24h4M27 12h4M27 18h4M27 24h4" />
          </g>
          <text
            x="18"
            y="24"
            textAnchor="middle"
            fontFamily="var(--display)"
            fontSize="18"
            fill="currentColor"
          >
            {inicial}
          </text>
        </svg>
        {/* PR B: hueco del contador de discos guardados, sin número aún. */}
      </a>
    )
  }

  return (
    <a className="marca-usuario" href="#/entrar" title="entrar" aria-label="entrar">
      <svg viewBox="0 0 36 36" width="24" height="24" aria-hidden="true">
        <g stroke="currentColor" strokeWidth="2.2">
          <path d="M5 12h4M5 18h4M5 24h4M27 12h4M27 18h4M27 24h4" />
        </g>
      </svg>
      <span className="marca-txt">ENTRAR</span>
    </a>
  )
}

// «sobre el proyecto» ya tiene destino: #/sobre (spec de la página SOBRE).
export function Puertas({ activa }) {
  return (
    <nav className="puertas">
      <a href="#/" className={`puerta ${activa === 'explorar' ? 'activa' : ''}`}>
        EXPLORAR
      </a>
      <a href="#/archivo" className={`puerta ${activa === 'archivo' ? 'activa' : ''}`}>
        ARCHIVO
      </a>
      <a href="#/sobre" className={`sobre ${activa === 'sobre' ? 'activa' : ''}`}>
        sobre el proyecto
      </a>
      <MarcaUsuario />
    </nav>
  )
}
