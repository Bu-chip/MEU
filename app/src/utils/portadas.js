// Escalera de sufijos del CDN de Bandcamp, ya verificada: _3=100px,
// _7=160, _9=210, _2=350, _5=700. El JSON trae la canónica _5 (700px,
// la usa la FICHA); para las tiles del muro basta _2 — 350px cubre un
// tile de ~160px a 2x de densidad sin cargar la grande.
export function miniatura(coverUrl) {
  return coverUrl.replace(/_5(\.\w+)$/, '_2$1')
}
