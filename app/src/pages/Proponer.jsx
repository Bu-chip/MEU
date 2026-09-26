import { useState } from 'react'
import './Proponer.css'

// Página PROPONER: cualquiera puede sugerir un disco, un grupo o un sello
// de Bandcamp. Sin backend: el formulario envía por debajo a un Google
// Form (buzón privado) y el robot de scripts/proposals.py convierte las
// respuestas en un PR de candidatos que Miguel revisa. Nada entra solo.
//
// El Form de Google no lo ve nadie: solo importa que sus campos (entry.*)
// existan. Si se cambia el Form, cambian estos ids.
const FORM_ACTION =
  'https://docs.google.com/forms/d/e/1FAIpQLScqQ19gyjEdpqk-oaZYkVDtyKiei_ELdO7mnhFMb_-mA_BQtQ/formResponse'
const CAMPOS = {
  url: 'entry.1358002423',
  lugar: 'entry.585327343',
  sello: 'entry.1363706201',
  relacionados: 'entry.1754998920',
  comentario: 'entry.1338744787',
}

// Solo Bandcamp: una ficha de disco, la portada de un grupo o de un sello.
// Los dominios propios (p. ej. queimadacircuitrecords.com) también son
// Bandcamp, pero no se pueden distinguir aquí; el robot los descarta y los
// lista para revisión manual.
const BANDCAMP_RE = /^https?:\/\/[a-z0-9-]+\.bandcamp\.com(\/|$)/i

export function Proponer() {
  const [url, setUrl] = useState('')
  const [estado, setEstado] = useState('idle') // idle | enviando | ok | error
  const [error, setError] = useState(null)

  async function onSubmit(e) {
    e.preventDefault()
    const form = e.currentTarget
    const datos = new FormData(form)
    // Campo trampa: invisible para personas; los bots lo rellenan.
    if (datos.get('web')) {
      setEstado('ok')
      return
    }
    const limpia = url.trim()
    if (!BANDCAMP_RE.test(limpia)) {
      setError('tiene que ser un enlace de bandcamp.com')
      return
    }
    setError(null)
    setEstado('enviando')
    const cuerpo = new URLSearchParams()
    cuerpo.set(CAMPOS.url, limpia)
    for (const campo of ['lugar', 'sello', 'relacionados', 'comentario']) {
      const v = String(datos.get(campo) ?? '').trim()
      if (v) cuerpo.set(CAMPOS[campo], v)
    }
    try {
      // no-cors: Google no responde con CORS, así que la respuesta es opaca.
      // Si la red va, el envío llega; el único fallo detectable es de red.
      await fetch(FORM_ACTION, { method: 'POST', mode: 'no-cors', body: cuerpo })
      setEstado('ok')
    } catch {
      setEstado('error')
    }
  }

  if (estado === 'ok') {
    return (
      <main className="proponer-pagina">
        <h1>PROPONER</h1>
        <p className="enviado">
          Recibido. Las propuestas se revisan a mano, una a una, antes de entrar
          en el archivo; puede tardar unas semanas. Eskerrik asko.
        </p>
        <p>
          <a className="otra" href="#/proponer" onClick={() => { setUrl(''); setEstado('idle') }}>
            proponer otro
          </a>
        </p>
      </main>
    )
  }

  return (
    <main className="proponer-pagina">
      <h1>PROPONER</h1>
      <p>
        ¿Falta un disco, un grupo o un sello de Euskal Herria? Pega su enlace de
        Bandcamp. Con la portada de un grupo o de un sello vale: el robot recorre
        toda su discografía. Solo el enlace es obligatorio; lo demás ayuda a
        situarlo.
      </p>

      <form className="propuesta" onSubmit={onSubmit} autoComplete="off">
        <label>
          <span>enlace de bandcamp</span>
          <input
            type="url"
            name="url"
            required
            inputMode="url"
            placeholder="https://grupo.bandcamp.com/album/…"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
          />
        </label>
        <label>
          <span>de dónde es (pueblo o ciudad)</span>
          <input type="text" name="lugar" placeholder="Bilbo, Iruñea, Gasteiz…" />
        </label>
        <label>
          <span>sello o colectivo</span>
          <input type="text" name="sello" />
        </label>
        <label>
          <span>otros grupos o sellos que deberían estar</span>
          <textarea name="relacionados" rows={3} placeholder="nombres o enlaces, uno por línea" />
        </label>
        <label>
          <span>comentario</span>
          <textarea name="comentario" rows={3} />
        </label>
        {/* Honeypot: fuera de la vista y del tabulador. */}
        <label className="trampa" aria-hidden="true">
          <span>web</span>
          <input type="text" name="web" tabIndex={-1} autoComplete="off" />
        </label>

        {error && <p className="err">{error}</p>}
        {estado === 'error' && (
          <p className="err">no se ha podido enviar; comprueba la conexión y vuelve a intentarlo</p>
        )}
        <button type="submit" disabled={estado === 'enviando'}>
          {estado === 'enviando' ? 'ENVIANDO…' : 'ENVIAR'}
        </button>
      </form>

      <p className="pie-form">
        No se guarda quién envía. Cada propuesta pasa por una revisión humana:
        ante la duda un disco entra, pero nada entra sin mirarlo.
      </p>
    </main>
  )
}
