// Lógica de la deriva de EXPLORAR, trasplantada del mockup congelado
// (design/meu-explorar-v8-deriva.html) con el esquema real de campos.

export const TAM_MURO = 60

export function shuffle(lista) {
  const copia = [...lista]
  for (let i = copia.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[copia[i], copia[j]] = [copia[j], copia[i]]
  }
  return copia
}

// Muro de deriva libre con variedad garantizada: ronda por género grueso
// (hasta 2 al azar por género) y relleno al azar del archivo entero,
// sin repetir disco. A diferencia del mockup, deduplica DURANTE el
// relleno para que el muro tenga siempre los 60 que promete el mando.
export function muroLibre(albums, n = TAM_MURO) {
  const porGenero = {}
  for (const album of albums) {
    const g = album.genre || '—'
    ;(porGenero[g] = porGenero[g] || []).push(album)
  }

  const vistos = new Set()
  const unicos = []
  const anota = (album) => {
    if (!vistos.has(album.id)) {
      vistos.add(album.id)
      unicos.push(album)
    }
  }

  for (const lista of Object.values(porGenero)) {
    const k = Math.min(2, lista.length)
    for (let i = 0; i < k; i++) {
      anota(lista[Math.floor(Math.random() * lista.length)])
    }
  }
  while (unicos.length < n && unicos.length < albums.length) {
    anota(albums[Math.floor(Math.random() * albums.length)])
  }

  return shuffle(unicos).slice(0, n)
}

// Elige una opción distinta de la actual (repetir mando = caer en otro).
export function alAzarDistinto(opciones, actual) {
  if (opciones.length < 2) return opciones[0]
  let elegido
  do {
    elegido = opciones[Math.floor(Math.random() * opciones.length)]
  } while (elegido === actual)
  return elegido
}
