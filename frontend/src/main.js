import { createApp } from 'vue';
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router';
import axios from 'axios'
// import './assets/main.css'
import App from './App.vue';

import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';
import 'vuetify/styles';
import '@mdi/font/css/materialdesignicons.css';
import { createVuetify } from 'vuetify';

import Home from './components/Home.vue';
import Login from './components/Login.vue';
import AuthGoogle from './components/LoginGoogle.vue';
// import AuthVK from './components/LoginVK.vue';
import Register from './components/Register.vue';
import ResetPassword from './components/ResetPassword.vue';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

// цветовая схема (#CDAB8F)
const lightTheme = {
  dark: false,
  colors: {
    primary: '#CDAB8F',
    secondary: '#E8D5C4',
    accent: '#A1887F',
    error: '#B00020',
    info: '#2196F3',
    success: '#4CAF50',
    warning: '#FB8C00',
    background: '#F8F5F0',
    surface: '#FFFDF5',
  }
}

const vuetify = createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'lightTheme',
    themes: {
      lightTheme,
    }
  }
});

// ???
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

const routes = [
  { path: '/', component: Home, name: 'Home' },
  { path: '/login', component: Login, name: 'Login' },
  { path: '/auth/google', component: AuthGoogle },
  // { path: '/auth/vk', component: AuthVK },
  // { path: '/profile', component: Profile, name: 'Profile', meta: { requiresAuth: true } },
  { path: '/register', component: Register, name: 'Register' },
  { path: '/reset', component: ResetPassword, name: 'ResetPassword' },
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
app.use(router);
app.use(vuetify);

// экземпляр authStore (???)
import { useAuthStore } from '@/stores/auth';
const authStore = useAuthStore();

// перевыпуск токенов
async function refreshAccessToken() {
  const refreshToken = getCookie('refresh_token');

  if (!refreshToken) {
    return false;
  }

  try {
    const refreshResponse = await axios.post(`${API_BASE_URL}/auth/refresh`, {}, {
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

      // проверка попытки обновления токена
      if (!originalRequest._retry) {
        originalRequest._retry = true;

        const success = await refreshAccessToken();

        if (success) {
          // повтор оригинального запроса с новым токеном
          originalRequest.headers.Authorization = `Bearer ${authStore.accessToken}`;
          return axios(originalRequest); // повтор запроса
        } else {
          // если обновление токена не удалось, пробрасываем ошибку дальше
          return Promise.reject(error);
        }
      }
    }
    return Promise.reject(error);
  }
);

// маршрутизатор (???)
/*
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

    // если токен есть (или был успешно обновлен), делаем запрос к /auth/info
    try {
      const response = await axios.get(`${API_BASE_URL}/auth/info`);
      app.config.globalProperties.$user = response.data;
      next();

    } catch (error) {
      // перенаправление на /login, если запрос /auth/info вернул 401 и interceptor не смог обновить токен
      if (error.response && error.response.status === 401) {
        return next({ path: '/login' });
      } else {
        console.error("Ошибка при проверке авторизации:", error);
        next(false);
      }
    }

  } else {
    next();
  }
});
 */

router.beforeEach(async (to, from, next) => {
    const requiresAuth = to.matched.some(record => record.meta.requiresAuth);

    if (requiresAuth) {
        // маршрут требует авторизацию
        if (!authStore.accessToken) {
            // нет access токена, перенаправляем на страницу логина
            next('/login');
        } else {
            // access токен есть, пропускаем
            next();
        }
    } else {
        // маршрут не требует авторизацию, пропускаем
        next();
    }
});

// app.use(router);
app.mount('#app');
