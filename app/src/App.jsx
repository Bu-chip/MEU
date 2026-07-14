import { useHashRoute } from './hooks/useHashRoute.js'
import { useArchive } from './hooks/useArchive.js'
import { Header } from './components/Header.jsx'
import { Puertas } from './components/Puertas.jsx'
import { Explorar } from './pages/Explorar.jsx'
import { Archivo } from './pages/Archivo.jsx'
import { Ficha } from './pages/Ficha.jsx'
import { Sobre } from './pages/Sobre.jsx'
import './App.css'

const PAGINAS = {
  explorar: Explorar,
  archivo: Archivo,
  sobre: Sobre,
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

  const Pagina = PAGINAS[route.page]
  return (
    <>
      <Header archive={archive} size={route.page === 'explorar' ? 'grande' : 'compacta'} />
      <Puertas activa={route.page} />
      <Pagina route={route} archive={archive} />
    </>
  )
}
