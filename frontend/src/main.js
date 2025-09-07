import { createApp } from 'vue';
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router';
import axios from 'axios'
// import './assets/main.css'
import App from './App.vue';
import vuetify from './plugins/vuetify';

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

// экземпляр authStore
import { useAuthStore } from '@/stores/auth';
import Cookies from "js-cookie";
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
      const newAccessToken = refreshResponse.data.data.tokens.access_token;
      authStore.setAccessToken(newAccessToken);

      const newRefreshToken = refreshResponse.data.data.tokens.refresh_token;
      // document.cookie = `refresh_token=${newRefreshToken}; path=/; max-age=3600; secure; httponly`;
      Cookies.set('refresh_token', newRefreshToken, {
        // expires: 30,
        // secure: true,
        sameSite: 'Strict',
        path: '/'
      });

      const userData = {
        email: refreshResponse.data.data.user.email,
        fullName: refreshResponse.data.data.user.full_name,
        firstName: refreshResponse.data.data.user.first_name,
        lastName: refreshResponse.data.data.user.last_name,
        picture: refreshResponse.data.data.user.picture,
      };
      authStore.setUser(userData);

      const roles = refreshResponse.data.data.roles;
      authStore.setRoles(roles);

      return true;

    } else {
      authStore.setAccessToken(null);
      Cookies.remove('refresh_token');
      return false;
    }

  } catch (error) {
    authStore.setAccessToken(null);
    Cookies.remove('refresh_token');
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

router.beforeEach(async (to, from, next) => {
    const requiresAuth = to.matched.some(record => record.meta.requiresAuth);

    if (requiresAuth) {
        // маршрут требует авторизацию
        if (!authStore.accessToken) {
            // нет access токена, перенаправляем на главную страницу
            next('/');
        } else {
            // access токен есть, пропускаем
            next();
        }
    } else {
        // маршрут не требует авторизацию, пропускаем
        next();
    }
});

// app.mount('#app');

(async () => {
    if (!authStore.accessToken && Cookies.get('refresh_token')) {
        await refreshAccessToken();
    }
    app.mount('#app');
})();
