import { defineStore } from 'pinia';
import axios from 'axios';
import Cookies from 'js-cookie';
import { jwtDecode } from 'jwt-decode';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

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
      this.user = { ...userData };
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
    },

    // метод для инициализации авторизации
    async initAuth() {
      if (!this.accessToken && Cookies.get('refresh_token')) {
        await this.refreshToken();
      }
    },

    // метод для обновления токена
    async refreshToken() {
      const refreshToken = this.getCookie('refresh_token');
      if (!refreshToken) return false;

      try {
        const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {}, {
          headers: { 'Authorization': `Bearer ${refreshToken}` }
        });

        if (response.data.status === 'ok') {
          const tokens = response.data.data.tokens;
          this.setAccessToken(tokens.access_token);

          const newRefreshToken = tokens.refresh_token;
          try {
            const payload = jwtDecode(newRefreshToken);
            this.setJti(payload.jti);
          } catch (e) {
            console.error('Failed to decode refresh token:', e);
          }

          Cookies.set('refresh_token', newRefreshToken, { sameSite: 'Strict', path: '/' });

          const userData = response.data.data.user;
          this.setUser({
            email: userData.email,
            fullName: userData.full_name,
            firstName: userData.first_name,
            lastName: userData.last_name,
            picture: userData.picture,
          });

          this.setRoles(response.data.data.roles);
          return true;
        } else {
          this.logout();
          return false;
        }
      } catch (error) {
        this.logout();
        return false;
      }
    },

    logout() {
      this.clearAccessToken();
      Cookies.remove('refresh_token');
    },

    getCookie(name) {
      const value = `; ${document.cookie}`;
      const parts = value.split(`; ${name}=`);
      if (parts.length === 2) return parts.pop().split(';').shift();
    }
  },
});
