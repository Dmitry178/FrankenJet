<template>
  <v-app>
    <!-- Toolbar -->
    <v-app-bar app flat>
      <router-link
          to="/"
          style="text-decoration: none; color: inherit; display: flex; align-items: center;"
          :class="{
            'pl-2': $vuetify.display.smAndDown,
            'pl-0': $vuetify.display.mdAndUp
          }"
      >
        <v-icon icon="mdi-airplane" class="mr-2 mr-sm-1" size="x-large" color="primary"></v-icon>
        <v-toolbar-title class="font-weight-bold">Franken Jet</v-toolbar-title>
      </router-link>

      <!-- Search (desktop) -->
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

      <v-btn
        v-if="$vuetify.display.mdAndUp"
        :to="{ name: 'Home' }"
        variant="text"
        class="mr-2"
      >
        Главная
      </v-btn>

      <v-btn
        v-if="$vuetify.display.mdAndUp"
        :to="{ name: 'Articles' }"
        variant="text"
        class="mr-2"
      >
        Статьи
      </v-btn>

      <v-btn
        v-if="$vuetify.display.mdAndUp"
        icon
        @click="toggleTheme"
        class="mr-2"
      >
        <v-icon>{{ themeIcon }}</v-icon>
      </v-btn>

      <v-divider vertical></v-divider>

      <Login
        v-if="!isLoggedIn && $vuetify.display.mdAndUp"
      />
      <Logout v-else-if="$vuetify.display.mdAndUp" />

      <v-btn
        v-if="$vuetify.display.smAndDown"
        icon
        @click="drawer = true"
        class="mx-0"
      >
        <v-icon>mdi-menu</v-icon>
      </v-btn>

    </v-app-bar>

    <!-- Drawer (mobile) -->
    <v-overlay
      v-model="drawer"
      width="100%"
      class="bg-surface"
      :scrim="false"
      @click:outside="drawer = false"
    >

      <v-toolbar flat class="px-0">
        <v-toolbar-title class="text-h6 font-weight-bold">
        </v-toolbar-title>
        <v-spacer></v-spacer>
        <v-btn
          icon
          @click="drawer = false"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-toolbar>

      <v-divider class="drawer"></v-divider>

      <!-- Search (mobile) -->
      <v-list-item>
        <v-text-field
          v-model="searchQuery"
          label="Поиск..."
          append-inner-icon="mdi-magnify"
          @click:append-inner="search"
          @keydown.enter="search"
          hide-details
          rounded="pill"
          variant="outlined"
          clearable
          density="compact"
          class="mt-2"
        ></v-text-field>
      </v-list-item>

      <v-divider class="drawer"></v-divider>

      <!-- Menu (mobile) -->
      <v-btn
      block
      rounded="0"
      variant="text"
      class="py-6"
      :to="{ name: 'Home' }"
      @click="drawer = false"
      >
        Главная
      </v-btn>

      <v-divider class="drawer"></v-divider>

      <v-btn
      block
      rounded="0"
      variant="text"
      class="py-6"
      :to="{ name: 'Articles' }"
      @click="drawer = false"
      >
        Статьи
      </v-btn>

      <v-divider class="drawer"></v-divider>

      <!-- Theme -->
      <v-btn
      block
      rounded="0"
      variant="text"
      class="py-6"
      @click="toggleTheme"
      >
        Тема
        <v-icon end>{{ themeIcon }}</v-icon>
      </v-btn>

      <v-divider class="drawer"></v-divider>

      <!-- Login / Logout -->
      <v-btn
        v-if="!isLoggedIn"
        block
        rounded="0"
        variant="text"
        @click="drawer = false"
        class="py-6"
      >
        Вход
        <v-icon end>mdi-login</v-icon>
      </v-btn>
      <v-btn
        v-else
        block
        rounded="0"
        variant="text"
        @click="drawer = false"
        class="py-6"
      >
        Выход
        <v-icon end>mdi-logout</v-icon>
      </v-btn>
    </v-overlay>

    <!-- Основной контент -->
    <v-main>
      <router-view></router-view>

      <!-- FAB -->
      <v-btn
        v-if="showScrollTop"
        fab
        icon
        color="secondary"
        class="scroll-top-btn"
        @click="scrollToTop"
        fixed
        bottom
        right
      >
        <v-icon>mdi-arrow-up</v-icon>
      </v-btn>
    </v-main>
  </v-app>
</template>

<script>

import {computed, onMounted, onUnmounted, ref} from 'vue';
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
      drawer.value = false; // закрываем меню после поиска
    };

    // FAB (Floating Action Button)
    const showScrollTop = ref(false);
    const scrollTimer = ref(null);

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

    // управление состоянием Drawer
    const drawer = ref(false);

    // отображение кнопки прокрутки на начало страницы
    const handleScroll = () => {
      showScrollTop.value = window.scrollY > 300;

      // сброс предыдущего таймера
      if (scrollTimer.value) {
        clearTimeout(scrollTimer.value);
      }

      // отображение кнопки при скролле > 300px
      if (window.scrollY > 300) {
        showScrollTop.value = true;
      }
    };

    // прокрутка страницы на начало
    const scrollToTop = () => {
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
      // activeTocItem.value = 'top';
    };

    onMounted(() => {
      settingsStore.loadSettings();
      displayAsciiArt();

      window.addEventListener('scroll', handleScroll);
    });

    onUnmounted(() => {
      window.removeEventListener('scroll', handleScroll);
    });

    return {
      isLoggedIn,
      isSearchRoute,
      settingsStore,
      searchQuery,
      search,
      themeIcon,
      toggleTheme,
      drawer,
      showScrollTop,
      scrollToTop,
    };
  }
};
</script>

<style scoped>
.v-btn--variant-text:hover {
  text-decoration: none;
  color: inherit;
}

.v-btn--variant-text:hover::before {
  opacity: 0;
}

.drawer.v-divider {
  margin: 0 !important;
  padding: 0 !important;
}

:deep(.v-breadcrumbs-item--link) {
  font-size: 0.85rem !important;
}

.v-overlay .v-btn--variant-text:hover {
  text-decoration: none;
  color: inherit;
}

.v-overlay .v-btn--variant-text:hover::before {
  opacity: 0;
}

.scroll-top-btn {
  position: fixed !important;
  bottom: 23px !important;
  right: 23px !important;
  z-index: 9999;
}
</style>
