import { defineStore } from 'pinia'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export const useSettingsStore = defineStore('settings', {
  state: () => ({
    settings: {
      auth_methods: {
        authentication: false,
        registration: false,
        reset_password: false,
        oauth2_google: false,
        oauth2_vk: false
      }
    },
    loading: false,
    error: null
  }),

  getters: {
    isAuthenticatedEnabled: (state) => state.settings.auth_methods.authentication,
    isRegistrationEnabled: (state) => state.settings.auth_methods.registration,
    isResetPasswordEnabled: (state) => state.settings.auth_methods.reset_password,
    isGoogleOAuthEnabled: (state) => state.settings.auth_methods.oauth2_google,
    isVkOAuthEnabled: (state) => state.settings.auth_methods.oauth2_vk,
    isLoading: (state) => state.loading,
    hasError: (state) => state.error
  },

  actions: {
    async loadSettings() {
      this.loading = false;
      this.error = null;
      try {
        const response = await axios.get(`${API_BASE_URL}/settings`);
        this.settings = response.data;
        this.loading = true;
      } catch (error) {
        console.error("Error loading settings:", error);
        this.error = error;
      }
    }
  }
})
