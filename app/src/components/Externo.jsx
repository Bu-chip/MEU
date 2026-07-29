// Flecha de «se abre fuera» en SVG, no en Unicode, por la misma razón que
// Corazon.jsx: U+2197 NORTH EAST ARROW es una de las diagonales que Unicode
// marca como Emoji=Yes, así que al no cubrirla ni Big Shoulders ni IBM Plex
// Mono la cadena de fallback de iOS la resuelve en Apple Color Emoji y sale
// azul. Las cardinales U+2190-2193 no son emoji y por eso conviven sin
// problema en el resto de la interfaz. Un SVG no puede virar nunca.
//
// Los codepoints se citan por nombre a propósito: ningún carácter con
// presentación emoji posible debe entrar en app/src, tampoco en comentarios,
// para que el grep de control siga dando cero.
//
// currentColor en stroke para heredar el color del contenedor —tinta en el
// botón de la FICHA, papel sobre el fondo de la FichaBar— y volverse lima
// en el hover. strokeLinejoin miter: esquinas duras, sin curvas.
//
// `size` admite número (px) o cadena con unidad. En la FICHA hace falta en
// em: ese botón tiene font-size fluido (clamp) y con un valor fijo la
// flecha se descolgaría del texto al cambiar el viewport.
export function Externo({ size = 14 }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      aria-hidden="true"
      style={{ verticalAlign: '-0.08em' }}
    >
      <path
        d="M3 21 21 3M11 3h10v10"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinejoin="miter"
      />
    </svg>
  )
}
