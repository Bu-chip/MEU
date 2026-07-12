// Punto de millar manual: es-ES de CLDR no agrupa números de 4 cifras
// (2364 → «2364») y los mockups exigen «2.364».
export function formato(n) {
  return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, '.')
}
