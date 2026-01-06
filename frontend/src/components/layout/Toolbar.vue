<template>
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

    <Auth
      v-if="!isLoggedIn && $vuetify.display.mdAndUp"
    />
    <UserMenu v-else-if="$vuetify.display.mdAndUp" />

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
      <v-toolbar-title class="text-h6 font-weight-bold"></v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn icon @click="drawer = false">
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
</template>

<script>
import { useToolbar } from '@/composables/useToolbar';
import Auth from '@/components/menus/Auth.vue';
import UserMenu from '@/components/menus/UserMenu.vue';

export default {
  name: 'Toolbar',
  components: {
    Auth,
    UserMenu,
  },
  setup() {
    const {
      isLoggedIn,
      isSearchRoute,
      isChatBotAvailable,
      searchQuery,
      drawer,
      themeIcon,
      search,
      toggleTheme,
    } = useToolbar();

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
  },
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
