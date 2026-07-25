import { useEffect, useReducer } from 'react'
import { supabase } from '../lib/supabase.js'
import { useAuth } from '../auth/useAuth.js'

// VISTOS: el segundo eje de la colección (decisión Notion, PR D). Guardar es
// intención (saved_albums, lima); haber pasado por un disco es recorrido
// (seen_albums, tinta). Se llama VISTOS, no ESCUCHADOS: el play del embed de
// Bandcamp no es detectable (H3 muerta, solo emite `playerinited`), así que
// «visto = abrir la ficha» — misma lógica del hueco honesto.
//
// Clon de useColeccion: singleton de módulo, una carga por sesión compartida.
// Aquí basta un Set de ids (pertenencia O(1) para el futuro filtro «ya visto»
// y cardinalidad para el contador); no hay `orden` porque VISTOS no pinta muro.
// Sin sesión (o sin Supabase): Set vacío y ni una llamada a la red.

let ids = new Set()
let cargando = false
let cargadaPara = null // user.id del set en memoria
const oyentes = new Set()

function emitir() {
  oyentes.forEach((fn) => fn())
}

// Carga (o vacía) los vistos según la sesión. Idempotente: mismo user → no-op;
// user nuevo → recarga; sin user → Set vacío sin tocar la red.
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
    .from('seen_albums')
    .select('disco_id')
    .eq('user_id', user.id)
    .then(({ data, error }) => {
      if (cargadaPara !== user.id) return // la sesión cambió mientras cargaba
      cargando = false
      if (!error && data) ids = new Set(data.map((r) => r.disco_id))
      emitir()
    })
}

// Marca un disco como visto (upsert al montar la FICHA). Optimista: el Set
// crece al instante; el unique (user_id, disco_id) convierte el insert
// duplicado en error 23505 —ya estaba visto, no es fallo— y cualquier otro
// error revierte solo ese id. Si ya está en el Set, no toca la red.
async function marcar(user, discoId) {
  if (!supabase || !user || ids.has(discoId)) return
  ids = new Set(ids).add(discoId)
  emitir()
  const { error } = await supabase
    .from('seen_albums')
    .insert({ user_id: user.id, disco_id: discoId })
  if (error && error.code !== '23505') {
    ids = new Set(ids)
    ids.delete(discoId)
    emitir()
  }
}

export function useVistos() {
  const { user } = useAuth()
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
    marcar: (discoId) => marcar(user, discoId),
  }
}
