import { defineStore } from 'pinia';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: null,
    jti: null,
    user: {
      email: null,
      fullName: null,
      firstName: null,
      lastName: null,
      picture: null,
    },
    roles: [],
  }),
  actions: {
    setAccessToken(token) {
      this.accessToken = token;
    },
    setJti(jti) {
      this.jti = jti;
    },
    clearAccessToken() {
      this.accessToken = null;
      this.jti = null;
      this.user = {
        email: null,
        fullName: null,
        firstName: null,
        lastName: null,
        picture: null,
      };
      this.roles = [];
    },
    setUser(userData) {
      this.user = { ...userData }; // разворачиваем userData, чтобы избежать реактивности исходного объекта
    },
    clearUser() {
      this.user = {
        email: null,
        fullName: null,
        firstName: null,
        lastName: null,
        picture: null,
      };
      this.roles = [];
    },
    setRoles(roles) {
      this.roles = roles;
    },
    clearRoles() {
      this.roles = [];
    }
  },
});
