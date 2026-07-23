import { useContext } from 'react'
import { AuthCtx } from './context.js'

// Inicial de la marca de usuario: primera letra en mayúscula del nombre
// (user_metadata.name) si existe, si no del email. '' si no hay usuario.
function inicialDe(user) {
  if (!user) return ''
  const fuente = user.user_metadata?.name || user.email || ''
  const ch = fuente.trim().charAt(0)
  return ch ? ch.toUpperCase() : ''
}

// Único consumidor del Context. Deriva user e inicial de la sesión para no
// duplicar estado en el Provider.
export function useAuth() {
  const ctx = useContext(AuthCtx)
  const user = ctx.session?.user ?? null
  return {
    session: ctx.session,
    user,
    inicial: inicialDe(user),
    cargando: ctx.cargando,
    disponible: ctx.disponible,
    entrarGoogle: ctx.entrarGoogle,
    entrarEmail: ctx.entrarEmail,
    salir: ctx.salir,
  }
}
