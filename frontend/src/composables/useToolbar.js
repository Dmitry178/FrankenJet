import { computed, ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useSettingsStore } from '@/stores/settings';
import { useRouter, useRoute } from 'vue-router';
import { useTheme } from 'vuetify';
import vuetifyConfig from '@/vuetify.config.js';

export function useToolbar() {
  const authStore = useAuthStore();
  const settingsStore = useSettingsStore();
  const router = useRouter();
  const route = useRoute();
  const theme = useTheme();

  const isLoggedIn = computed(() => authStore.accessToken !== null);
  const isSearchRoute = computed(() => route.path === '/search');
  const isChatBotAvailable = computed(() => settingsStore.isChatBotAvailable);

  const searchQuery = ref('');
  const drawer = ref(false);

  // Темы
  const themeNames = Object.keys(vuetifyConfig.theme.themes);
  const currentThemeIndex = ref(0);

  // Загрузка темы из localStorage
  const savedTheme = localStorage.getItem('selectedTheme');
  if (savedTheme && themeNames.includes(savedTheme)) {
    theme.change(savedTheme);
    currentThemeIndex.value = themeNames.indexOf(savedTheme);
  } else {
    // Установка темы по умолчанию (если не выбрана)
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      const matchedThemeName = themeNames.find(name => name.toLowerCase().includes('dark'));
      if (matchedThemeName) {
        const matchedIndex = themeNames.indexOf(matchedThemeName);
        localStorage.setItem('selectedTheme', matchedThemeName);
        currentThemeIndex.value = matchedIndex;
        theme.change(matchedThemeName); // исправлено: было theme.change(savedTheme)
      }
    }
  }

  const themeIcon = computed(() => {
    const nextIndex = (currentThemeIndex.value + 1) % themeNames.length;
    const nextThemeName = themeNames[nextIndex];

    if (nextThemeName === 'dark') {
      return 'mdi-weather-night';
    } else if (nextThemeName === 'light') {
      return 'mdi-weather-sunny';
    } else {
      return 'mdi-palette';
    }
  });

  const search = () => {
    router.push({ path: "/search", query: { q: searchQuery.value } });
    drawer.value = false;
  };

  const toggleTheme = () => {
    currentThemeIndex.value = (currentThemeIndex.value + 1) % themeNames.length;
    const nextTheme = themeNames[currentThemeIndex.value];
    theme.change(nextTheme);
    localStorage.setItem('selectedTheme', nextTheme);
  };

  return {
    isLoggedIn,
    isSearchRoute,
    isChatBotAvailable,
    searchQuery,
    drawer,
    themeIcon,
    search,
    toggleTheme,
  };
}
