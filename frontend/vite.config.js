import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [tailwindcss(),react()],
  server: {
    proxy: {
      '/upload-and-process': 'http://localhost:8001',
      '/generate_forecasts_with_real_data': 'http://localhost:8001',
      '/historical': 'http://localhost:8001',
      '/skus': 'http://localhost:8001'
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets'
  }
})
