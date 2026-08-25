import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  // The landing page's public animations are served by this single Vite app.
  publicDir: '../landing-react/public',
  server: {
    port: 5173,
    strictPort: true,
  },
})
