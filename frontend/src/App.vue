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

          <Login v-if="!isLoggedIn" />
          <Logout v-else />

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
import Login from './components/Login.vue';
import Logout from './components/Logout.vue';
import { computed, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useSettingsStore } from '@/stores/settings';

export default {
  name: 'App',
  components: {
    Login,
    Logout,
  },
  setup() {
    const authStore = useAuthStore();
    const settingsStore = useSettingsStore();

    const isLoggedIn = computed(() => authStore.accessToken !== null);

    onMounted(() => {
      settingsStore.loadSettings();
    });

    return {
      isLoggedIn,
      settingsStore,
    };
  }
};
</script>
