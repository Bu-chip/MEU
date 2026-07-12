import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  // Convivencia (F1–F4): la app vive en /MEU/v2/ mientras el sitio vanilla
  // sigue en /MEU/. El cutover de F5 cambia esta base.
  base: '/MEU/v2/',
  server: {
    port: parseInt(process.env.PORT || '5173'),
    fs: {
      // El JSON canónico vive fuera de app/ (data/, única fuente de verdad).
      allow: ['..'],
    },
  },
})
