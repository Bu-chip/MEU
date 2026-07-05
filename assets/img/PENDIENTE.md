# Assets pendientes (Miguel) — PIEL v0

El moodboard pide al menos un asset real hecho a mano. Estos dos ya
tienen su hueco en el código; basta con soltar el archivo aquí:

1. **`papel-escaneado.jpg`** — textura de papel real escaneada
   (no simulada en CSS). Se carga en `.paper-overlay`
   (`assets/css/styles.css`); mientras no exista, hay un ruido SVG
   de respaldo. Mejor un escaneo claro (el overlay va en
   `mix-blend-mode: multiply` sobre el papel #F2EFE8).

2. **`sello-qcr.png`** — sello / lettering QCR escaneado.
   Sustituir el placeholder tipográfico `.sello-qcr` de `index.html`
   por un `<img>` con este archivo (fondo transparente, tinta negra).
