import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    host: true,
    port: 5173,
    strictPort: true,
    watch: { usePolling: true }, // this may decrease the performance, so later i may set an interval
    headers: {
      "Cross-Origin-Opener-Policy": "same-origin-allow-popups"
    }
  },
})
