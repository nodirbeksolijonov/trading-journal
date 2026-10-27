import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // Forward API calls to FastAPI so the browser sees a single origin.
    proxy: { '/api': 'http://localhost:8000' },
  },
})
