<template>
  <v-app>
    <!-- Тулбар -->
    <v-app-bar app flat>
      <router-link
          to="/"
          style="text-decoration: none; color: inherit; display: flex; align-items: center;"
      >
        <v-icon icon="mdi-airplane" class="mr-1" size="x-large" color="primary"></v-icon>
        <v-toolbar-title class="font-weight-bold">Franken Jet</v-toolbar-title>
      </router-link>

      <!--  Строка поиска  -->
      <v-text-field
        v-if="!isSearchRoute"
        v-model="searchQuery"
        label="Поиск..."
        append-inner-icon="mdi-magnify"
        @click:append-inner="search"
        @keydown.enter="search"
        class="ml-4 hidden-sm-and-down"
        style="max-width: 300px;"
        hide-details
        rounded="pill"
        variant="outlined"
        clearable
      ></v-text-field>

      <v-spacer></v-spacer>

      <v-btn icon @click="toggleTheme" class="mr-2">
        <v-icon>{{ themeIcon }}</v-icon>
      </v-btn>

      <v-divider vertical></v-divider>

      <Login v-if="!isLoggedIn" />
      <Logout v-else />
    </v-app-bar>

    <!-- Основной контент -->
    <v-main>
      <router-view></router-view>
    </v-main>
  </v-app>
</template>

<script>

import { computed, onMounted, ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useSettingsStore } from '@/stores/settings';
import { useRouter, useRoute } from 'vue-router';
import { useTheme } from 'vuetify';
import { displayAsciiArt } from '@/plugins/console.js';
import vuetifyConfig from '@/vuetify.config.js';
import Login from '@/components/Login.vue';
import Logout from '@/components/Logout.vue';

export default {
  name: 'App',
  components: {
    Login,
    Logout,
  },
  setup() {
    const authStore = useAuthStore();
    const settingsStore = useSettingsStore();
    const router = useRouter();
    const route = useRoute();
    const theme = useTheme();

    const isLoggedIn = computed(() => authStore.accessToken !== null);
    const searchQuery = ref('');

    // true, если текущий маршрут - /search
    const isSearchRoute = computed(() => route.path === '/search');

    const search = () => {
      router.push({ path: "/search", query: { q: searchQuery.value } });
    };

    // получаем названия тем из vuetify.config
    const themeNames = Object.keys(vuetifyConfig.theme.themes);
    const currentThemeIndex = ref(0);

    // загружаем тему из localStorage
    const savedTheme = localStorage.getItem('selectedTheme');
    if (savedTheme && themeNames.includes(savedTheme)) {
      theme.change(savedTheme);
      currentThemeIndex.value = themeNames.indexOf(savedTheme);
    }
    else {
      // тема не установлена в localStorage, проверяем, что системная тема - dark
      if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
        const matchedThemeName = themeNames.find(name => name.toLowerCase().includes('dark'));
        const matchedIndex = themeNames.indexOf(matchedThemeName);
        if (matchedIndex !== -1) {
          localStorage.setItem('selectedTheme', matchedThemeName);
          currentThemeIndex.value = matchedIndex;
          theme.change(savedTheme);
        }
      }
    }

    const themeIcon = computed(() => {
      // индекс следующей темы
      const nextIndex = (currentThemeIndex.value + 1) % themeNames.length;
      const nextThemeName = themeNames[nextIndex];

      if (nextThemeName==='dark') {
        return 'mdi-weather-night';
      } else if (nextThemeName==='light') {
        return 'mdi-weather-sunny';
      } else {
        return 'mdi-palette';
      }
    });

    // переключение на следующую тему
    const toggleTheme = () => {
      currentThemeIndex.value = (currentThemeIndex.value + 1) % themeNames.length;
      const nextTheme = themeNames[currentThemeIndex.value];
      theme.change(nextTheme);
      localStorage.setItem('selectedTheme', nextTheme);
    };

    onMounted(() => {
      settingsStore.loadSettings();
      displayAsciiArt();
    });

    return {
      isLoggedIn,
      isSearchRoute,
      settingsStore,
      searchQuery,
      search,
      themeIcon,
      toggleTheme,
    };
  }
};
</script>
