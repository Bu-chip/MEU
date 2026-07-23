import { createContext } from 'react'

// El objeto Context vive solo, sin componentes ni hooks, para que ni
// AuthContext.jsx (solo el Provider) ni useAuth.js (solo el hook) tengan
// que exportar nada extra y disparar react-refresh/only-export-components.
// Valores por defecto = degradación limpia si algún consumidor quedara
// fuera del Provider (no debería: <App/> va envuelto en main.jsx).
export const AuthCtx = createContext({
  session: null,
  cargando: false,
  disponible: false,
  entrarGoogle: async () => {},
  entrarEmail: async () => ({ error: null }),
  salir: async () => {},
})
