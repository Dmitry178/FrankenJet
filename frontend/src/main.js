import { createApp } from 'vue';
import App from './App.vue';
import { createPinia } from 'pinia';
import { useAuthStore } from "@/stores/auth.js";
import { useChatStore } from "@/stores/chat.js";
import { setupRouter } from '@/plugins/router.js';
import { setupAxios } from '@/plugins/axios.js';
import { setupProperties } from "@/plugins/properties.js";
import vuetify from '@/plugins/vuetify.js';
import '@/assets/main.css'

async function init() {
  const app = createApp(App);
  const { router } = setupRouter();
  const pinia = createPinia();
  pinia.use(({ store }) => {
    const originalConsoleLog = console.log
    console.log = (...args) => {
      if (
        args.length === 1 &&
        typeof args[0] === 'string' &&
        args[0].includes('websocket') &&
        args[0].includes('store installed')
      ) {
        return
      }
      originalConsoleLog(...args)
    }
  })

  app.use(router);
  app.use(pinia);
  app.use(vuetify);

  setupAxios();
  setupProperties(app);

  // инициализация авторизации
  const authStore = useAuthStore();
  await authStore.initAuth();

  // инициализация чата
  const chatStore = useChatStore();
  chatStore.initializeChatId();

  app.mount('#app');
}

init().catch(error => {
  console.error('Failed to initialize app:', error);
});
