import axios from 'axios';
import { useAuthStore } from '@/stores/auth.js';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function getCookie(name) {
  let value = "; " + document.cookie;
  let parts = value.split("; " + name + "=");
  if (parts.length === 2) return parts.pop().split(";").shift();
}

export function setupAxios() {
  axios.defaults.baseURL = API_BASE_URL;

  // Request interceptor
  axios.interceptors.request.use(
    (config) => {
      // получаем актуальный экземпляр store внутри interceptor
      const authStore = useAuthStore();

      // добавление заголовка Authorization, если есть токен авторизации
      if (authStore.accessToken) {
        config.headers.Authorization = `Bearer ${authStore.accessToken}`;
      }

      // извлечение CSRF-токена из cookie и добавление его в заголовки
      const csrfToken = getCookie('csrf-token');
      if (csrfToken && ['POST', 'PUT', 'PATCH', 'DELETE'].includes(config.method?.toUpperCase())) {
        config.headers['X-CSRF-Token'] = csrfToken;
      }

      return config;
    },
    (error) => Promise.reject(error)
  );

  // Response interceptor
  axios.interceptors.response.use(
    (response) => response,
    async (error) => {
      // обработка ошибки 401 (аутентификация, обновление токена)
      if (error.response?.status === 401) {
        const originalRequest = error.config;

        if (!originalRequest._retry) {
          originalRequest._retry = true;

          const authStore = useAuthStore();
          const success = await authStore.refreshToken();
          if (success) {
            originalRequest.headers.Authorization = `Bearer ${authStore.accessToken}`;
            return axios(originalRequest);
          } else {
            const authStoreForLogout = useAuthStore();
            authStoreForLogout.logout();
            return Promise.reject(error);
          }
        }
      }

      // обработка ошибки 412 (CSRF)
      if (error.response?.status === 412) {

      }

      return Promise.reject(error);
    }
  );
}
