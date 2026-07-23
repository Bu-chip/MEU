// Cliente Supabase único de todo el MEU (calco del que corre en el hermano
// genre-explorer). La capa de cuentas es ADITIVA Y OPCIONAL: si faltan las
// env vars, este módulo exporta `null` en vez de lanzar, y toda la app —
// muro, deriva, archivo, fichas, player, compartir — sigue funcionando sin
// tocar. Quien lo consume comprueba el null (ver auth/AuthContext.jsx).
//
// Solo la clave anon/publishable, pública por diseño (RLS protege los datos
// en el servidor); NUNCA la service_role.
import { createClient } from '@supabase/supabase-js'

const url = import.meta.env.VITE_SUPABASE_URL
const anonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

// Sin cualquiera de las dos → null. La app entera degrada limpio.
export const supabase =
  url && anonKey
    ? createClient(url, anonKey, {
        auth: {
          flowType: 'pkce',
          persistSession: true,
          autoRefreshToken: true,
          detectSessionInUrl: true,
        },
      })
    : null
