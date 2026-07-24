import { useHashRoute } from './hooks/useHashRoute.js'
import { useArchive } from './hooks/useArchive.js'
import { supabase } from './lib/supabase.js'
import { Header } from './components/Header.jsx'
import { Puertas } from './components/Puertas.jsx'
import { Explorar } from './pages/Explorar.jsx'
import { Archivo } from './pages/Archivo.jsx'
import { Ficha } from './pages/Ficha.jsx'
import { Sobre } from './pages/Sobre.jsx'
import { Entrar } from './pages/Entrar.jsx'
import './App.css'

const PAGINAS = {
  explorar: Explorar,
  archivo: Archivo,
  sobre: Sobre,
  entrar: Entrar,
}

export default function App() {
  const route = useHashRoute()
  const { archive, error } = useArchive()

  if (error) {
    return <p className="error-datos">error al cargar el archivo: {error}</p>
  }

  // La FICHA no lleva header ni puertas: abre con su barra de retorno
  // (spec meu-ficha-v1).
  if (route.page === 'disco') {
    return <Ficha route={route} archive={archive} />
  }

  // #/entrar solo existe si hay Supabase: sin cuentas cae en EXPLORAR, sin
  // ruta muerta ni página vacía (degradación limpia).
  const page = route.page === 'entrar' && !supabase ? 'explorar' : route.page
  const Pagina = PAGINAS[page]
  return (
    <>
      <Header archive={archive} />
      <Puertas activa={page} />
      <Pagina route={route} archive={archive} />
    </>
  )
}
