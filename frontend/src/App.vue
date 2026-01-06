<template>
  <v-app>
    <Toolbar />

    <!-- Основной контент -->
    <v-main>
      <router-view></router-view>

      <!-- FAB над чат-ботом -->
      <ScrollTopFAB v-if="isChatBotAvailable" :isFinalPosition="false" />

      <!-- Чат-бот -->
      <ChatBot v-if="isChatBotAvailable" />

      <!-- FAB на месте чат-бота -->
      <ScrollTopFAB v-else :isFinalPosition="true" />

    </v-main>
    <Snackbar />
  </v-app>
</template>

<script>
import { computed, onMounted } from 'vue';
import { useSettingsStore } from '@/stores/settings';
import { displayAsciiArt } from '@/plugins/console.js';
import Toolbar from '@/components/layout/Toolbar.vue';
import Snackbar from '@/components/layout/Snackbar.vue';
import ChatBot from '@/components/ChatBot.vue';
import ScrollTopFAB from '@/components/layout/ScrollTopFAB.vue';

export default {
  name: 'App',
  components: {
    Toolbar,
    ChatBot,
    Snackbar,
    ScrollTopFAB,
  },
  setup() {
    const settingsStore = useSettingsStore();

    const isChatBotAvailable = computed(() => settingsStore.isChatBotAvailable);

    onMounted(() => {
      settingsStore.loadSettings();
      displayAsciiArt();
    });

    return {
      isChatBotAvailable,
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
</style>
