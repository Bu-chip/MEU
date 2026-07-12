// Capa de alias de tags — SOLO búsqueda (decisión 6 de Fase 0).
//
// Política conservadora:
// - Solo grafías distintas del MISMO lexema presentes en los datos
//   (ortografía, separadores, acrónimos de la propia expresión).
// - Nada de fusiones entre familias lingüísticas o léxicas.
// - jungle queda FUERA del grupo dnb (género con entidad propia).
// - Los compuestos (liquid dnb, crust punk, …) no se aliasan: la búsqueda
//   por subcadena ya los encuentra.
// - Esta capa jamás muta data/ ni los conteos: cada tag conserva su cuenta
//   real en facetas y fichas.
//
// Excluidos deliberadamente tras revisar los 2.090 tags:
//   «punk?» (estilización intencional del artista, no errata de «punk»),
//   «metal; punk» (artefacto ≠ metalpunk),
//   «rhythmic noise» / «rhythm and noise» (variación morfológica, no gráfica).

export const GRUPOS_ALIAS = [
  ['drum & bass', 'drum and bass', 'drum n bass', 'dnb', 'd&b'],
  ['rock & roll', 'rock and roll', "rock'n'roll"],
  ['rhythm & blues', 'rhythm and blues', 'r&b'],
  ['hardcore', 'hxc'],
  ['new orleans', 'neworleans⚜️'],
]
