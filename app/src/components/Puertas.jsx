import './Puertas.css'

// «sobre el proyecto» queda inerte igual que en los mockups congelados;
// tendrá destino cuando el diseño lo defina.
export function Puertas({ activa }) {
  return (
    <nav className="puertas">
      <a href="#/" className={`puerta ${activa === 'explorar' ? 'activa' : ''}`}>
        EXPLORAR
      </a>
      <a href="#/archivo" className={`puerta ${activa === 'archivo' ? 'activa' : ''}`}>
        ARCHIVO
      </a>
      <a href="#/" className="sobre" onClick={(e) => e.preventDefault()}>
        sobre el proyecto
      </a>
    </nav>
  )
}
