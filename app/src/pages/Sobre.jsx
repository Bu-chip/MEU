import './Sobre.css'

// Página SOBRE: texto fijo del proyecto, spec cerrada (copy literal).
// Columna de lectura contenida, mismo criterio que la columna de datos
// de la FICHA. Único uso de lima: el enlace a QCR.
export function Sobre() {
  return (
    <main className="sobre-pagina">
      <h1>SOBRE</h1>
      <p>
        El MEU es la guía personal de Queimada Circuit Records a la música underground de
        Euskal Herria en Bandcamp. Un archivo hecho a mano, disco a disco.
      </p>
      <h2>Cómo funciona</h2>
      <p>
        No hay algoritmo, ni cuentas, ni nada que te vigile. Solo un catálogo curado con
        criterio maximalista: ante la duda, un disco entra; solo queda fuera lo clarísimamente
        ajeno a la escena. Cada ficha apunta a Bandcamp — la idea es que escuches, y si algo te
        gusta, lo compres ahí y apoyes a quien lo hace.
      </p>
      <h2>Qué no es</h2>
      <p>
        No es una tienda, ni un recomendador, ni vende nada. No te perfila. Es una guía, no un
        filtro de calidad.
      </p>
      <h2>Quién</h2>
      <p>
        Detrás está QCR, sello experimental afincado en Bilbao, y el trabajo de comisariado de
        una sola persona. El catálogo es un archivo vivo: crece cada mes con discos nuevos que
        se descubren en Bandcamp y se revisan a mano antes de entrar.
      </p>
      <p className="qcr">
        <a href="https://queimadacircuitrecords.com" target="_blank" rel="noreferrer">
          queimadacircuitrecords.com
        </a>
      </p>
    </main>
  )
}
