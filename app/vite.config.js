import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  // Post-cutover (F5): la app es el sitio y se sirve desde la raíz del
  // dominio custom (mapa.queimadacircuitrecords.com). El vanilla salió del
  // deploy; su fuente sigue en main. (Antes: base '/MEU/v2/' en convivencia.)
  base: '/',
  server: {
    port: parseInt(process.env.PORT || '5173'),
    fs: {
      // El JSON canónico vive fuera de app/ (data/, única fuente de verdad).
      allow: ['..'],
    },
  },
})
