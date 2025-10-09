import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Port dla aplikacji frontend (React)
    port: 5173, 
    // Konfiguracja proxy do przekierowywania zapytań API na Backend FastAPI
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000', // Adres, na którym działa Twój FastAPI
        changeOrigin: true, // Zmieniamy nagłówek 'Origin'
        rewrite: (path) => path.replace(/^\/api/, ''), // Usuwamy /api z żądania
      },
    },
  },
})