import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [tailwindcss(),react()],
  server: {
    proxy: {
      '/api/forecast': 'http://localhost:8001',
      '/forecasts': 'http://localhost:8001',
      '/historical': 'http://localhost:8001',
      '/skus': 'http://localhost:8001',
      '/auth': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        secure: false,
    },
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets'
  }
})
