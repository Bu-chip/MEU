import { useEffect, useReducer } from 'react'
import { supabase } from '../lib/supabase.js'
import { useAuth } from '../auth/useAuth.js'

// Colección del usuario como Set de ids del JSON canónico (el campo `id`,
// clave estable del archivo — NO el album_id de Bandcamp, que es cosa del
// player y falta en 15 discos). Singleton de módulo al estilo de useArchive:
// una carga por sesión compartida por todos los componentes, así el botón de
// la FICHA y el contador de la cabecera ven el mismo Set y se mueven a la
// vez. Sin sesión (o sin Supabase): Set vacío y ni una llamada a la red.

let ids = new Set()
let cargando = false
let cargadaPara = null // user.id de la colección en memoria
const oyentes = new Set()

function emitir() {
  oyentes.forEach((fn) => fn())
}

// Carga (o vacía) la colección según la sesión. Idempotente: mismo user →
// no-op; user nuevo → recarga; sin user → Set vacío sin tocar la red.
function sincronizar(user) {
  if (!supabase || !user) {
    if (cargadaPara !== null) {
      cargadaPara = null
      ids = new Set()
      cargando = false
      emitir()
    }
    return
  }
  if (cargadaPara === user.id) return
  cargadaPara = user.id
  cargando = true
  emitir()
  supabase
    .from('saved_albums')
    .select('disco_id')
    .eq('user_id', user.id)
    .then(({ data, error }) => {
      if (cargadaPara !== user.id) return // la sesión cambió mientras cargaba
      cargando = false
      if (!error && data) ids = new Set(data.map((r) => r.disco_id))
      emitir()
    })
}

// Escrituras optimistas: el Set cambia al instante y, si Supabase falla, se
// revierte SOLO ese id (no un snapshot completo: otras escrituras en vuelo
// no se pierden). El unique (user_id, disco_id) convierte el insert
// duplicado en error 23505 — ya estaba guardado, no es fallo.
async function insertar(user, discoId) {
  if (!supabase || !user || ids.has(discoId)) return
  ids = new Set(ids).add(discoId)
  emitir()
  const { error } = await supabase
    .from('saved_albums')
    .insert({ user_id: user.id, disco_id: discoId })
  if (error && error.code !== '23505') {
    ids = new Set(ids)
    ids.delete(discoId)
    emitir()
  }
}

async function borrar(user, discoId) {
  if (!supabase || !user || !ids.has(discoId)) return
  ids = new Set(ids)
  ids.delete(discoId)
  emitir()
  const { error } = await supabase
    .from('saved_albums')
    .delete()
    .eq('user_id', user.id)
    .eq('disco_id', discoId)
  if (error) {
    ids = new Set(ids).add(discoId)
    emitir()
  }
}

export function useColeccion() {
  const { user } = useAuth()
  // El estado vive en el módulo; el reducer solo fuerza el re-render cuando
  // emitir() avisa (los Sets se reasignan con identidad nueva a cada cambio).
  const [, refrescar] = useReducer((n) => n + 1, 0)

  useEffect(() => {
    oyentes.add(refrescar)
    return () => oyentes.delete(refrescar)
  }, [])

  useEffect(() => {
    sincronizar(user)
  }, [user])

  return {
    ids,
    cargando,
    guardar: (discoId) => insertar(user, discoId),
    quitar: (discoId) => borrar(user, discoId),
  }
}
