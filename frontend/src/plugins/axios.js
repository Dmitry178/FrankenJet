import axios from 'axios';
import { useAuthStore } from '@/stores/auth';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export function setupAxios() {
  axios.defaults.baseURL = API_BASE_URL;

  const authStore = useAuthStore();

  // Request interceptor
  axios.interceptors.request.use(
    (config) => {
      if (authStore.accessToken) {
        config.headers.Authorization = `Bearer ${authStore.accessToken}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  // Response interceptor
  axios.interceptors.response.use(
    (response) => response,
    async (error) => {
      if (error.response?.status === 401) {
        const originalRequest = error.config;

        if (!originalRequest._retry) {
          originalRequest._retry = true;

          const success = await authStore.refreshToken();
          if (success) {
            originalRequest.headers.Authorization = `Bearer ${authStore.accessToken}`;
            return axios(originalRequest);
          } else {
            return Promise.reject(error);
          }
        }
      }
      return Promise.reject(error);
    }
  );
}
