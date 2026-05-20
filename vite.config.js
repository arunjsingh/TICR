import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite' // 👈 Added Tailwind Import
import path from 'path'

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss() // 👈 Added Tailwind Plugin Engine
  ],
  resolve: {
    alias: {
      // Creates a shortcut so you can import components cleanly
      '@': path.resolve(__dirname, './app/UI'),
    },
  },
  server: {
    port: 3000, // Frontend development server port
    proxy: {
      // Routes frontend network calls to your Python application
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
})
