import { createApp } from 'vue';
import App from './App.vue';
import { createPinia } from 'pinia';
import { useAuthStore } from "@/stores/auth.js";
import { setupRouter } from '@/plugins/router.js';
import { setupAxios } from '@/plugins/axios.js';
import { setupProperties } from "@/plugins/properties.js";
import vuetify from '@/plugins/vuetify.js';
import '@/assets/main.css'

async function init() {
  const app = createApp(App);
  const { router } = setupRouter();
  const pinia = createPinia();

  app.use(router);
  app.use(pinia);
  app.use(vuetify);

  setupAxios();
  setupProperties(app);

  // инициализация авторизации
  const authStore = useAuthStore();
  await authStore.initAuth();

  app.mount('#app');
}

init().catch(error => {
  console.error('Failed to initialize app:', error);
});
