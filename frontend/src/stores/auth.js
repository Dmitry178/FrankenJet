import { defineStore } from 'pinia';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: localStorage.getItem('accessToken') || null
  }),
  actions: {
    setAccessToken(token) {
      this.accessToken = token;
      if (token) {
          localStorage.setItem('accessToken', token);
      } else {
          localStorage.removeItem('accessToken');
      }
    },
    clearAccessToken() {
      this.accessToken = null;
      localStorage.removeItem('accessToken');
    }
  },
});
