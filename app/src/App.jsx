import { useHashRoute } from './hooks/useHashRoute.js'
import { useArchive } from './hooks/useArchive.js'
import { Header } from './components/Header.jsx'
import { Puertas } from './components/Puertas.jsx'
import { Explorar } from './pages/Explorar.jsx'
import { Archivo } from './pages/Archivo.jsx'
import { Ficha } from './pages/Ficha.jsx'
import './App.css'

const PAGINAS = {
  explorar: Explorar,
  archivo: Archivo,
  disco: Ficha,
}

export default function App() {
  const route = useHashRoute()
  const { archive, error } = useArchive()
  const Pagina = PAGINAS[route.page]

  return (
    <>
      <Header archive={archive} size={route.page === 'explorar' ? 'grande' : 'compacta'} />
      <Puertas activa={route.page} />
      {error ? (
        <p className="error-datos">error al cargar el archivo: {error}</p>
      ) : (
        <Pagina route={route} archive={archive} />
      )}
    </>
  )
}
