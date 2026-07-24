import { useState, useEffect } from 'react'
import { supabase } from '../lib/supabase.js'
import { AuthCtx } from './context.js'
import { CLAVE_DESTINO, guardarDestino } from './destino.js'

// Capa de cuentas ADITIVA Y OPCIONAL. Si supabase es null (faltan las env
// vars) el Provider monta igual y sirve session=null, cargando=false: el
// árbol de React nunca se rompe y el resto de la app —muro, deriva,
// archivo, fichas, player, compartir— funciona entero sin tocar.
//
// El canje del ?code= lo hace SOLO detectSessionInUrl del cliente (PKCE);
// aquí no se canjea a mano. El Provider únicamente: (1) limpia la query de
// la URL tras el canje preservando el hash, y (2) restaura el hash de
// origen que se guardó antes de lanzar el login (vuelta al origen).

// redirectTo SIEMPRE la raíz del dominio (o localhost en dev). NUNCA una
// URL /d/:id/: los stubs hacen location.replace absoluto y se comen la
// query, matando el ?code= en silencio.
const REDIRECT = window.location.origin + '/'

export function AuthProvider({ children }) {
  const [session, setSession] = useState(null)
  // Solo hay carga real si hay cliente; sin él, resuelto de entrada.
  const [cargando, setCargando] = useState(Boolean(supabase))

  useEffect(() => {
    if (!supabase) return

    // Quita ?code=/?error= de la URL tras el canje, preservando el hash.
    const limpiarUrl = () => {
      try {
        const u = new URL(window.location.href)
        if (u.searchParams.has('code') || u.searchParams.has('error')) {
          window.history.replaceState(null, '', u.pathname + u.hash)
        }
      } catch {
        /* no-op */
      }
    }

    // Restaura el hash guardado antes de lanzar el login y borra la clave.
    const restaurarDestino = () => {
      let destino = null
      try {
        destino = localStorage.getItem(CLAVE_DESTINO)
        if (destino) localStorage.removeItem(CLAVE_DESTINO)
      } catch {
        destino = null
      }
      if (destino && destino !== window.location.hash) {
        window.location.hash = destino
      }
    }

    supabase.auth.getSession().then(({ data }) => {
      setSession(data.session)
      setCargando(false)
    })

    const { data: sub } = supabase.auth.onAuthStateChange((event, sess) => {
      setSession(sess)
      setCargando(false)
      if (event === 'SIGNED_IN') {
        limpiarUrl()
        restaurarDestino()
      }
    })

    return () => sub.subscription.unsubscribe()
  }, [])

  const entrarGoogle = async () => {
    if (!supabase) return
    guardarDestino()
    await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: { redirectTo: REDIRECT },
    })
  }

  const entrarEmail = async (email) => {
    if (!supabase) return { error: new Error('cuentas no disponibles') }
    guardarDestino()
    return supabase.auth.signInWithOtp({
      email,
      options: { emailRedirectTo: REDIRECT },
    })
  }

  const salir = async () => {
    if (!supabase) return
    await supabase.auth.signOut()
  }

  const valor = {
    session,
    cargando,
    disponible: Boolean(supabase),
    entrarGoogle,
    entrarEmail,
    salir,
  }

  return <AuthCtx.Provider value={valor}>{children}</AuthCtx.Provider>
}
