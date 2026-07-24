// Vuelta al origen tras el login (PR A): antes de lanzar el flujo se guarda
// el hash actual bajo esta clave y, al volver con sesión, AuthContext lo
// restaura y borra. Vive en su propio módulo para que también pueda
// dispararlo quien manda a #/entrar sin pasar por los botones de login
// (GUARDAR sin sesión, PR B).
export const CLAVE_DESTINO = 'meu:destino'

// Blindado ante localStorage no disponible (modo privado, permisos).
export function guardarDestino() {
  try {
    localStorage.setItem(CLAVE_DESTINO, window.location.hash || '')
  } catch {
    /* localStorage no disponible: la vuelta al origen degrada a no-op */
  }
}
