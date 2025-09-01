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

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

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

// перевыпуск токенов
async function refreshAccessToken() {
  const refreshToken = getCookie('refresh_token');

  if (!refreshToken) {
    return false;
  }

  try {
    const refreshResponse = await axios.post('http://localhost:8111/auth/refresh', {}, {
      headers: {
        'Authorization': `Bearer ${refreshToken}`
      }
    });

    if (refreshResponse.data.status === 'ok') {
      const newAccessToken = refreshResponse.data.data.access_token;
      const newRefreshToken = refreshResponse.data.data.refresh_token;

      // обновление токенов
      authStore.setAccessToken(newAccessToken);
      document.cookie = `refresh_token=${newRefreshToken}; path=/; max-age=3600; secure; httponly`;

      return true;
    } else {
      authStore.setAccessToken(null);
      document.cookie = "refresh_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC;";
      return false;
    }
  } catch (error) {
    authStore.setAccessToken(null);
    document.cookie = "refresh_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC;";
    return false;
  }
}

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
  async (error) => {
    if (error.response && error.response.status === 401) {
      const originalRequest = error.config;

      // Проверяем, не пытались ли мы уже обновить токен
      if (!originalRequest._retry) {
        originalRequest._retry = true;

        const success = await refreshAccessToken();

        if (success) {
          // Повторяем оригинальный запрос с новым токеном
          originalRequest.headers.Authorization = `Bearer ${authStore.accessToken}`;
          return axios(originalRequest); // Повторяем запрос
        } else {
          // Если обновление токена не удалось, перенаправляем на логин
          if (router.currentRoute.value.path !== '/login') {
            router.push('/login');
          }
          return Promise.reject(error);
        }
      }
    }
    return Promise.reject(error);
  }
);

// маршрутизатор
router.beforeEach(async (to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);

  if (requiresAuth) {
    let accessToken = authStore.accessToken;

    // если access-токена нет в Pinia
    if (!accessToken) {
      const success = await refreshAccessToken();
      if (success) {
        accessToken = authStore.accessToken;
      } else {
        // если не удалось обновить, на логин
        return next({ path: '/login' });
      }
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
