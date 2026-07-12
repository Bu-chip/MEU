import './EnObras.css'

// Placeholder temporal del esqueleto F1: cada puerta se abre en su fase.
// F2 (EXPLORAR), F3 (ARCHIVO) y F4 (FICHA) sustituyen este bloque.
export function EnObras({ puerta, fase }) {
  return (
    <section className="en-obras">
      <p className="que">{puerta}</p>
      <p className="cuando">
        esta puerta se abre en la <b>fase {fase}</b> de la migración · mientras
        tanto, el archivo completo sigue vivo en{' '}
        <a href="https://bu-chip.github.io/MEU/">bu-chip.github.io/MEU</a>
      </p>
    </section>
  )
}
