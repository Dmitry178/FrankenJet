<template>
  <v-responsive class="border" style="border: none">
    <v-app>
      <v-app-bar :elevation="1" app flat>
        <v-container class="d-flex align-center">
          <router-link
              to="/"
              style="text-decoration: none; color: inherit; display: flex; align-items: center;"
          >
            <v-icon icon="mdi-airplane" class="mr-1" size="x-large" color="primary"></v-icon>
            <v-toolbar-title class="font-weight-bold">Franken Jet</v-toolbar-title>
          </router-link>
          <v-spacer></v-spacer>
          <v-divider vertical></v-divider>

          <v-menu v-if="!isLoggedIn" offset="0" :close-on-content-click="false">
            <template v-slot:activator="{ props }">
              <v-btn class="ml-2" v-bind="props" icon>
                <v-icon left>mdi-login</v-icon>
              </v-btn>
            </template>
            <v-card width="300">
              <v-card-title class="text-center">Аутентификация</v-card-title>
              <v-card-text>
                <v-alert v-if="loginErrorMessage" type="error">{{ loginErrorMessage }}</v-alert>
                <v-text-field
                  v-if="settingsStore.isAuthenticatedEnabled"
                  v-model="loginEmail"
                  label="Email"
                  type="email"
                  id="email"
                  name="email"
                  autocomplete="email"
                ></v-text-field>
                <v-text-field
                  v-if="settingsStore.isAuthenticatedEnabled"
                  v-model="loginPassword"
                  label="Пароль"
                  type="password"
                  id="password"
                  name="password"
                  autocomplete="current-password"
                ></v-text-field>
              </v-card-text>
              <v-card-actions class="d-flex flex-column">
                <v-btn
                  v-if="settingsStore.isAuthenticatedEnabled"
                  color="primary"
                  block @click="login"
                >
                  Войти
                </v-btn>
                <v-btn
                  v-if="settingsStore.isGoogleOAuthEnabled"
                  color="primary"
                  block
                  @click="loginWithGoogle"
                >
                  <v-icon left>mdi-google</v-icon>
                  Войти через Google
                </v-btn>
                <v-btn
                  v-if="settingsStore.isVkOAuthEnabled"
                  color="primary"
                  block
                  @click="loginWithVK"
                >
                  <v-icon left>mdi-vk</v-icon>
                  Войти через VK
                </v-btn>
                <div class="text-center mt-2">
                  <router-link v-if="settingsStore.isRegistrationEnabled" to="/register">Зарегистрироваться</router-link>
                  <span v-if="settingsStore.isRegistrationEnabled && settingsStore.isResetPasswordEnabled"> | </span>
                  <router-link v-if="settingsStore.isResetPasswordEnabled" to="/reset">Сбросить пароль</router-link>
                </div>
              </v-card-actions>
            </v-card>
          </v-menu>

          <v-btn class="ml-2" v-else @click="logout" icon>
            <v-icon left>mdi-logout</v-icon>
          </v-btn>

        </v-container>
      </v-app-bar>

      <v-main>
        <v-container>
          <router-view></router-view>
        </v-container>
      </v-main>
    </v-app>
  </v-responsive>
</template>

<script>
import {computed, ref, onMounted} from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useSettingsStore } from '@/stores/settings';
import { useRouter } from 'vue-router';
import Cookies from 'js-cookie';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export default {
  name: 'App',
  setup() {
    const authStore = useAuthStore();
    const settingsStore = useSettingsStore();
    const router = useRouter();

    const isLoggedIn = computed(() => authStore.accessToken !== null);
    const loginEmail = ref('');
    const loginPassword = ref('');
    const loginErrorMessage = ref('');

    const logout = async () => {
      authStore.setAccessToken(null);
      Cookies.remove('refresh_token', { path: '/' });
    };

    const login = async () => {
      if (!loginEmail.value) {
        loginErrorMessage.value = 'Введите email';
        return;
      }
      if (!loginPassword.value) {
        loginErrorMessage.value = 'Введите пароль';
        return;
      }

      loginErrorMessage.value = '';

      console.log('Attempting login:', loginEmail.value, loginPassword.value);

      try {
        const response = await axios.post(`${API_BASE_URL}/auth/login`, {
          email: loginEmail.value,
          password: loginPassword.value
        });

        if (response.status === 200) {
          const accessToken = response.data.data.access_token;
          const refreshToken = response.data.data.refresh_token;

          authStore.setAccessToken(accessToken);

          Cookies.set('refresh_token', refreshToken, {
            // expires: 30,
            // secure: true,
            sameSite: 'Strict',
            path: '/'
          });

          await router.push('/');
        } else {
          loginErrorMessage.value = 'Неверный email или пароль';
        }
      } catch (error) {
        console.error('Login error:', error);
        loginErrorMessage.value = 'Произошла ошибка при аутентификации';
      }
    };

     const loginWithGoogle = () => {
      window.location.href = `${API_BASE_URL}/oauth/google`;
    };

    const loginWithVK = () => {
      window.location.href = `${API_BASE_URL}/oauth/vk`;
    };

    onMounted(() => {
      settingsStore.loadSettings();
    });

    return {
      isLoggedIn,
      logout,
      login,
      loginEmail,
      loginPassword,
      loginErrorMessage,
      loginWithGoogle,
      loginWithVK,
      settingsStore,
    };
  }
};
</script>
