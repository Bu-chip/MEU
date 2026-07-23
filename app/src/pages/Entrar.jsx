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
    const quien = user?.user_metadata?.name || user?.email || 'tu cuenta'
    return (
      <main className="entrar-pagina">
        <h1>ESTÁS DENTRO</h1>
        <p>
          Sesión iniciada como <b>{quien}</b>.
        </p>
        <p className="nota">
          Tu colección de discos aparecerá aquí próximamente. De momento el acceso no cambia
          nada de lo que ya podías hacer sin cuenta.
        </p>
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
        Guardar discos en una colección personal es opcional. El mapa, el archivo y las fichas
        funcionan igual sin cuenta — esto solo añade una estantería tuya encima.
      </p>

      <div className="vias">
        <button className="via-google" onClick={entrarGoogle}>
          ENTRAR CON GOOGLE
        </button>

        <div className="sep">
          <span>o con tu correo</span>
        </div>

        {enviado ? (
          <p className="enviado">
            Enlace enviado. Revisa tu correo <b>{email}</b> y abre el enlace de acceso en este
            mismo dispositivo.
          </p>
        ) : (
          <form className="via-email" onSubmit={onMagic}>
            <input
              type="email"
              required
              autoComplete="email"
              placeholder="tu@correo.com"
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

      <p className="nota">
        Sin contraseñas: entras con un enlace de un solo uso o con Google. No perfilamos ni
        vendemos nada.
      </p>
    </main>
  )
}
