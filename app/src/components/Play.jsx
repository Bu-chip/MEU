// Triángulo de reproducción en SVG, no en Unicode, hermano de Corazon.jsx
// y Externo.jsx: U+25B6 BLACK RIGHT-POINTING TRIANGLE es la base del emoji
// de play (Emoji=Yes) y en iOS cae en Apple Color Emoji exactamente igual
// que la flecha, multiplicado por los 60 tiles del muro. Los triangulitos
// de orden de ARCHIVO (U+25B4 y U+25BE) no están en el set emoji y se
// quedan como están.
//
// Macizo y sin stroke: el glifo que sustituye es un triángulo relleno, y
// un stroke sobre el relleno solo lo engordaría. El triángulo ya es
// angular por definición, así que no hay nada que redondear. currentColor
// para heredar tinta o papel según la variante de tile.
export function Play({ size = 12 }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      aria-hidden="true"
      style={{ verticalAlign: '-0.08em' }}
    >
      <path d="M5 3 21 12 5 21z" fill="currentColor" />
    </svg>
  )
}
