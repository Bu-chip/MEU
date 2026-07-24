import { useState } from 'react'
import { useAuth } from '../auth/useAuth.js'
import './Entrar.css'

// Página ENTRAR: login opcional, tratada como SOBRE (sobria, tipográfica,
// sin ventanas flotantes — MEU no tiene ninguna). Dos vías sin contraseña:
// Google (botón monocromo, sin logo a color) y magic link por email.
// Con sesión abierta, la página cambia a «estás dentro» + SALIR (el botón
// de salir vive aquí, no en un menú desplegable).
export function Entrar() {
  const { session, user, entrarGoogle, entrarEmail, salir, cargando } = useAuth()
  const [email, setEmail] = useState('')
  const [enviado, setEnviado] = useState(false)
  const [enviando, setEnviando] = useState(false)
  const [errorMsg, setErrorMsg] = useState(null)

  if (cargando) {
    return (
      <main className="entrar-pagina">
        <p className="cargando">comprobando sesión…</p>
      </main>
    )
  }

  if (session) {
    const quien = user?.email || ''
    return (
      <main className="entrar-pagina">
        <h1>DENTRO</h1>
        <p>{quien}</p>
        <div className="vias">
          <button className="salir-btn" onClick={salir}>
            SALIR
          </button>
        </div>
      </main>
    )
  }

  const onMagic = async (e) => {
    e.preventDefault()
    const dir = email.trim()
    if (!dir) return
    setEnviando(true)
    setErrorMsg(null)
    const { error } = await entrarEmail(dir)
    setEnviando(false)
    if (error) setErrorMsg(error.message || 'no se pudo enviar el enlace')
    else setEnviado(true)
  }

  return (
    <main className="entrar-pagina">
      <h1>ENTRAR</h1>
      <p>
        un sitio donde guardar los discos que encuentres.
        <br />
        la cuenta no hace nada más — ni perfil, ni muro, ni recomendaciones.
      </p>

      <div className="vias">
        <button className="via-google" onClick={entrarGoogle}>
          ENTRAR CON GOOGLE
        </button>

        <div className="sep">
          <span>o</span>
        </div>

        {!enviado && (
          <form className="via-email" onSubmit={onMagic}>
            <input
              type="email"
              required
              autoComplete="email"
              placeholder="tu correo"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <button type="submit" disabled={enviando}>
              {enviando ? 'ENVIANDO…' : 'ENVIAR ENLACE'}
            </button>
          </form>
        )}

        {errorMsg && <p className="err">{errorMsg}</p>}
      </div>

      {/* Pie del campo: siempre visible. Al enviar, el formulario desaparece
          y este pie queda como confirmación, sin inventar copy nueva. */}
      <p className="nota">te llega un enlace. lo abres y estás dentro. sin contraseña.</p>
    </main>
  )
}
