<template>
  <v-menu offset="0" :close-on-content-click="false">
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
</template>

<script>
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useSettingsStore } from '@/stores/settings';
import { useRouter } from 'vue-router';
import Cookies from 'js-cookie';
import axios from 'axios';

export default {
  name: 'Login',
  setup() {
    const authStore = useAuthStore();
    const settingsStore = useSettingsStore();
    const router = useRouter();

    const loginEmail = ref('');
    const loginPassword = ref('');
    const loginErrorMessage = ref('');

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

      try {
        const response = await axios.post(`/auth/login`, {
          email: loginEmail.value,
          password: loginPassword.value
        });

        if (response.status === 200) {
          const accessToken = response.data.data.tokens.access_token;
          authStore.setAccessToken(accessToken);

          const refreshToken = response.data.data.tokens.refresh_token;
          Cookies.set('refresh_token', refreshToken, {
            // expires: 30,
            // secure: true,
            sameSite: 'Strict',
            path: '/'
          });

          const userData = {
            email: response.data.data.user.email,
            fullName: response.data.data.user.full_name,
            firstName: response.data.data.user.first_name,
            lastName: response.data.data.user.last_name,
            picture: response.data.data.user.picture,
          };
          authStore.setUser(userData);

          const roles = response.data.data.roles;
          authStore.setRoles(roles);

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
      window.location.href = `/oauth/google`;
    };

    const loginWithVK = () => {
      window.location.href = `/oauth/vk`;
    };

    return {
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
