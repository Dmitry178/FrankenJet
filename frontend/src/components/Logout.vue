<template>
  <v-menu offset="0" :close-on-content-click="false">
    <template v-slot:activator="{ props }">
      <v-btn class="ml-2" v-bind="props" icon>
        <v-icon left>mdi-account-circle</v-icon>
      </v-btn>
    </template>
    <v-card width="200">
      <v-card-title class="text-center">Профиль</v-card-title>
      <v-card-actions class="d-flex flex-column">
        <router-link to="/profile" class="v-btn v-btn--text">
          Редактировать профиль
        </router-link>
        <v-btn color="error" block @click="logout">Выйти</v-btn>
      </v-card-actions>
    </v-card>
  </v-menu>
</template>

<script>
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';
import Cookies from 'js-cookie';

export default {
  setup() {
    const authStore = useAuthStore();
    const router = useRouter();

    const logout = async () => {
      authStore.setAccessToken(null);
      Cookies.remove('refresh_token', { path: '/' });
      await router.push('/');
    };

    return { logout };
  }
};
</script>
