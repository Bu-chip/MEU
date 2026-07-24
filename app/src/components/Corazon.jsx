// Corazón de GUARDAR en SVG, no en Unicode: el carácter U+2665 tiene
// historial de virar a emoji rojo en iOS y eso rompe el sistema monocromo;
// un SVG no puede volverse emoji nunca. currentColor en fill y stroke para
// heredar el color del botón (tinta en la FICHA, papel en la FichaBar) y
// volverse lima en el hover. strokeLinejoin miter obligatorio: esquinas
// duras, sin curvas ni redondeos.
export function Corazon({ lleno, size = 14 }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      aria-hidden="true"
      style={{ verticalAlign: '-0.1em' }}
    >
      <path
        d="M12 21 3 12V6l4-3 5 4 5-4 4 3v6z"
        fill={lleno ? 'currentColor' : 'none'}
        stroke="currentColor"
        strokeWidth="2"
        strokeLinejoin="miter"
      />
    </svg>
  )
}
