import './Puertas.css'

// «sobre el proyecto» ya tiene destino: #/sobre (spec de la página SOBRE).
export function Puertas({ activa }) {
  return (
    <nav className="puertas">
      <a href="#/" className={`puerta ${activa === 'explorar' ? 'activa' : ''}`}>
        EXPLORAR
      </a>
      <a href="#/archivo" className={`puerta ${activa === 'archivo' ? 'activa' : ''}`}>
        ARCHIVO
      </a>
      <a href="#/sobre" className={`sobre ${activa === 'sobre' ? 'activa' : ''}`}>
        sobre el proyecto
      </a>
    </nav>
  )
}
