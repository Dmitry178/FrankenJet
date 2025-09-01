import { createApp } from 'vue';
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router';
import axios from 'axios'
import './assets/main.css'
import App from './App.vue';

import Home from './components/Home.vue';
import Login from './components/Login.vue';
// import AuthGoogle from './components/AuthGoogle.vue';
// import AuthVK from './components/AuthVK.vue';

const routes = [
  { path: '/', component: Home, meta: { requiresAuth: true } },
  { path: '/login', component: Login },
  // { path: '/auth/google', component: AuthGoogle }
  // { path: '/auth/vk', component: AuthVK }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// createApp(App).use(router).mount('#app');

const pinia = createPinia()
const app = createApp(App);

app.config.globalProperties.$axios = axios;

app.use(pinia);

// экземпляр authStore
import { useAuthStore } from '@/stores/auth';
const authStore = useAuthStore();

// interceptor для добавления access_token в заголовок
axios.interceptors.request.use(
  (config) => {
    const accessToken = authStore.accessToken; // получаем из Pinia
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// interceptor для обработки ошибок ответов
axios.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response && error.response.status === 401) {
      // перенаправление на страницу логина, только если не находимся на ней
      if (router.currentRoute.value.path !== '/login') {
        router.push('/login');
      }

      authStore.setAccessToken(null); // очищаем токен в Pinia

      return Promise.reject(error);
    }
    return Promise.reject(error);
  }
);

// маршрутизатор
router.beforeEach(async (to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);

  if (requiresAuth) {
    const accessToken = authStore.accessToken;

    if (!accessToken) {
      // если токена нет в Pinia, перенаправляем на логин
      return next({ path: '/login' });
    }

      try {
        const response = await axios.get('http://localhost:8111/auth/info');
        app.config.globalProperties.$user = response.data;
        next();

      } catch (error) {
        if (error.response && error.response.status === 401) {
          next({ path: '/login' });
        } else {
          console.error("Ошибка при проверке авторизации:", error);
          next(false);
        }
      }
    } else {
      next();
    }
});

app.use(router);
app.mount('#app');
