import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true, // Listen on all addresses
    open: true, // Automatically open browser
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true, // Generate source maps for production
    chunkSizeWarningLimit: 1600,
  },
  resolve: {
    alias: {
      // You can add path aliases here for cleaner imports
      '@': '/src',
      '@components': '/src/components',
      '@context': '/src/context',
      '@services': '/src/services',
    }
  }
})