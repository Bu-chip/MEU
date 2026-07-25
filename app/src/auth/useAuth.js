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

// Nombre visible del usuario: SOLO el que trae el proveedor (Google rellena
// user_metadata.name / full_name). NUNCA el email — la cautela del Notion es
// que el correo no aparezca en ninguna parte de la interfaz. Con magic link no
// hay nombre, así que devuelve null y quien lo pinte cae en la inicial.
function nombreDe(user) {
  if (!user) return null
  const nombre = user.user_metadata?.name || user.user_metadata?.full_name || ''
  return nombre.trim() || null
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
    nombre: nombreDe(user),
    cargando: ctx.cargando,
    disponible: ctx.disponible,
    entrarGoogle: ctx.entrarGoogle,
    entrarEmail: ctx.entrarEmail,
    salir: ctx.salir,
  }
}
