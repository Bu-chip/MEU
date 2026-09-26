import { useHashRoute } from './hooks/useHashRoute.js'
import { useArchive } from './hooks/useArchive.js'
import { supabase } from './lib/supabase.js'
import { Header } from './components/Header.jsx'
import { Puertas } from './components/Puertas.jsx'
import { Explorar } from './pages/Explorar.jsx'
import { Archivo } from './pages/Archivo.jsx'
import { Mapa } from './pages/Mapa.jsx'
import { Ficha } from './pages/Ficha.jsx'
import { Sobre } from './pages/Sobre.jsx'
import { Proponer } from './pages/Proponer.jsx'
import { Entrar } from './pages/Entrar.jsx'
import { Coleccion } from './pages/Coleccion.jsx'
import './App.css'

const PAGINAS = {
  explorar: Explorar,
  archivo: Archivo,
  mapa: Mapa,
  sobre: Sobre,
  proponer: Proponer,
  entrar: Entrar,
  coleccion: Coleccion,
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

  // #/entrar y #/coleccion solo existen si hay Supabase: sin cuentas caen en
  // EXPLORAR, sin ruta muerta ni página vacía (degradación limpia).
  const rutaCuentas = route.page === 'entrar' || route.page === 'coleccion'
  const page = rutaCuentas && !supabase ? 'explorar' : route.page
  const Pagina = PAGINAS[page]
  return (
    <>
      {/* MAPA usa la cabecera compacta: el mapa manda en esa vista. */}
      <Header archive={archive} compacta={page === 'mapa'} />
      <Puertas activa={page} />
      <Pagina route={route} archive={archive} />
    </>
  )
}
