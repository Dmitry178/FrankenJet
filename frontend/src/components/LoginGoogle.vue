<template>
  <div class="container">
    <p>Обработка аутентификации</p>
  </div>
</template>

<script>

import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';
import Cookies from 'js-cookie';

export default {
  setup() {
    const authStore = useAuthStore();
    const router = useRouter();

    return { authStore, router };
  },

  mounted() {
    this.handleGoogleCallback();
  },

  methods: {
    async handleGoogleCallback() {
      const queryParams = new URLSearchParams(window.location.search);
      const code = queryParams.get('code');
      const state = queryParams.get('state');

      if (code && state) {
        try {
          const response = await this.$axios.post(`/oauth/google/redirect`, { code, state });

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
            console.error('Ошибка аутентификации Google:', response.status);
            await this.router.push({path: '/login', query: {error: 'Ошибка аутентификации Google.'}});
          }
        } catch (error) {
          console.error('Ошибка при запросе к oauth/google/redirect:', error);
          await this.router.push({path: '/login', query: {error: 'Произошла ошибка при аутентификации Google.'}});
        }
      } else {
        console.error('Нет параметров code или state в URL.');
        await this.router.push({
          path: '/login',
          query: {error: 'Отсутствуют необходимые параметры для аутентификации Google.'}
        });
      }
    },
  },
};
</script>

<style scoped>
.container {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 20px;
  min-height: 100vh;
  font-family: 'Inter', sans-serif;
}
</style>
