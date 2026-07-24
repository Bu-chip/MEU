import { useAuth } from '../auth/useAuth.js'
import { useColeccion } from './useColeccion.js'
import { navegar } from './useHashRoute.js'
import { guardarDestino } from '../auth/destino.js'

// Estado GUARDAR de un disco concreto. Calca la FORMA de useCompartir — el
// hook se llama antes de los early-returns por las reglas de hooks, `album`
// puede llegar null y alternar solo se invoca desde botones que ya renderizan
// con álbum resuelto — pero no lo reutiliza: aquél está acoplado a
// navigator.share.
//
// Sin sesión, alternar() no escribe: guarda el hash actual (mecanismo de
// vuelta al origen del PR A) y manda a #/entrar — tras entrar, el usuario
// vuelve a esta misma ficha con el botón ya operativo.
export function useGuardar(album) {
  const { session } = useAuth()
  const { ids, guardar, quitar, cargando } = useColeccion()

  const guardado = album != null && ids.has(album.id)

  const alternar = () => {
    if (!album) return
    if (!session) {
      guardarDestino()
      navegar('#/entrar')
      return
    }
    if (guardado) quitar(album.id)
    else guardar(album.id)
  }

  return { guardado, alternar, cargando }
}
