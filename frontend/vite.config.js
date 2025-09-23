import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import vuetify from 'vite-plugin-vuetify'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
      vue(),
      vuetify({ autoImport: true }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      'vue': 'vue/dist/vue.esm-bundler.js',
    }
  },
  optimizeDeps: {
    include: [
      'vuetify',
      'vuetify/components',
      'vuetify/directives',
    ],
  },
  build: {
    transpileDependencies: ['vuetify'],
  },
})
