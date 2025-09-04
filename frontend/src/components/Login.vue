<template>
  <v-card class="mx-auto" max-width="400">
    <v-card-title class="text-center">Аутентификация</v-card-title>
    <v-card-text>
      <v-alert v-if="errorMessage" type="error">{{ errorMessage }}</v-alert>
      <v-text-field
        v-model="email"
        label="Email"
        type="email"
        id="email"
        name="email"
        autocomplete="email"
      ></v-text-field>
      <v-text-field
        v-model="password"
        label="Пароль"
        type="password"
        id="password"
        name="password"
        autocomplete="current-password"
      ></v-text-field>
    </v-card-text>
    <v-card-actions class="d-flex flex-column">
      <v-btn color="primary" block @click="login">Войти</v-btn>
      <v-btn color="primary" block @click="loginWithGoogle">
        <v-icon left>mdi-google</v-icon>
        Войти через Google
      </v-btn>
      <v-btn color="primary" block @click="loginWithVK">
        <v-icon left>mdi-vk</v-icon>
        Войти через VK
      </v-btn>
      <div class="text-center mt-2">
        <router-link to="/register">Зарегистрироваться</router-link> |
        <router-link to="/reset">Сбросить пароль</router-link>
      </div>
    </v-card-actions>
  </v-card>
</template>

<script>
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';
import Cookies from 'js-cookie';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export default {
  data() {
    return {
      email: '',
      password: '',
      access_token: '',
      refresh_token: '',
      errorMessage: '',
    };
  },
  setup() {
    const authStore = useAuthStore();
    const router = useRouter();
    return { authStore, router };
  },
  mounted() {
    const error = this.$route.query.error;
    if (error) {
      this.errorMessage = error;
    }
  },
  watch: {
    '$route'(to, from) {
      const error = to.query.error;
      if (error) {
        this.errorMessage = error;
      } else {
        this.errorMessage = '';
      }
    }
  },
  methods: {
    loginWithGoogle() {
      window.location.href = `${API_BASE_URL}/oauth/google`;
    },
    loginWithVK() {
      window.location.href = `${API_BASE_URL}/oauth/vk`;
    },
    async login() {
      if (!this.email) {
        this.errorMessage = 'Введите email';
        return;
      }
      if (!this.password) {
        this.errorMessage = 'Введите пароль';
        return;
      }

      this.errorMessage = '';

      try {
        const response = await this.$axios.post(`${API_BASE_URL}/auth/login`, {
          email: this.email,
          password: this.password
        });

        if (response.status === 200) {
          const accessToken = response.data.data.access_token;
          const refreshToken = response.data.data.refresh_token;

          this.authStore.setAccessToken(accessToken);

          Cookies.set('refresh_token', refreshToken, {
            // expires: 30,
            // secure: true,
            sameSite: 'Strict',
            path: '/'
          });

          await this.router.push('/');

        } else {
          this.errorMessage = 'Неверный email или пароль';
        }
      } catch (error) {
        this.errorMessage = 'Произошла ошибка при аутентификации';
      }
    }
  }
}
</script>
