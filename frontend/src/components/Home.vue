<template>
  <v-container>
    <v-card>
      <v-card-title>User Info:</v-card-title>
      <v-card-text>
        <div v-if="userInfo">
          <p>ID: {{ userInfo.id }}</p>
          <p>Email: {{ userInfo.email }}</p>
          <p v-if="userInfo.first_name">Name: {{ userInfo.first_name }}</p>
          <v-img v-if="userInfo.picture" :src="userInfo.picture" aspect-ratio="1" max-width="200" class="user-picture"></v-img>
        </div>
        <p v-else>Ошибка загрузки информации о пользователе</p>
      </v-card-text>
      <v-card-actions>
        <v-btn color="primary" @click="logout">Выйти</v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script>
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';
import Cookies from 'js-cookie';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export default {
  data() {
    return {
      userInfo: null,
      first_name: '',
    };
  },
  mounted() {
    this.fetchUserInfo();
  },
  setup() {
    const authStore = useAuthStore();
    const router = useRouter();
    return { authStore, router };
  },
  methods: {
    async fetchUserInfo() {
      try {
        const response = await this.$axios.get(`${API_BASE_URL}/auth/info`);

        if (response.status === 200 && response.data.status === 'ok') {
          this.userInfo = response.data.data;
        } else {
          console.error('Ошибка получения информации о пользователе:', response.status, response.data);
        }
      } catch (error) {
        console.error('Ошибка при запросе информации о пользователе:', error);
      }
    },
    async logout() {
      try {
        this.authStore.setAccessToken(null);
        Cookies.remove('refresh_token', { path: '/' });
        await this.router.push('/login');
      } catch (error) {
        console.error('Ошибка при запросе:', error);
      }
    }
  }
}
</script>

<style scoped>
.user-picture {
  max-width: 200px;
  max-height: 200px;
  margin-bottom: 10px;
}
</style>
