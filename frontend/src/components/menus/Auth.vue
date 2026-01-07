<template>
  <v-menu offset="0" :close-on-content-click="false">
    <template v-slot:activator="{ props }">
      <v-btn class="ml-2" v-bind="props" icon>
        <v-icon left>mdi-login</v-icon>
      </v-btn>
    </template>
    <v-card width="300">
      <v-card-title class="text-center">Аутентификация</v-card-title>

      <v-card-text>
        <v-text-field
          v-if="settingsStore.isAuthenticatedEnabled"
          v-model="loginEmail"
          label="Email"
          type="email"
          id="email"
          name="email"
          autocomplete="email"
        ></v-text-field>

        <v-text-field
          v-if="settingsStore.isAuthenticatedEnabled"
          v-model="loginPassword"
          label="Пароль"
          type="password"
          id="password"
          name="password"
          autocomplete="current-password"
        ></v-text-field>

        <v-btn
          v-if="settingsStore.isAuthenticatedEnabled"
          block @click="login"
          elevation="0"
          :style="{
            'background-color': 'rgb(var(--v-theme-background))',
            'border': '1px solid rgba(var(--v-theme-border), 0.75)'
          }"
        >
          Войти
        </v-btn>

        <v-btn
          v-if="settingsStore.isGoogleOAuthEnabled"
          color="primary"
          block
          @click="loginWithGoogle"
        >
          <v-icon left>mdi-google</v-icon>
          Войти через Google
        </v-btn>

        <v-btn
          v-if="settingsStore.isVkOAuthEnabled"
          color="primary"
          block
          @click="loginWithVK"
        >
          <v-icon left>mdi-vk</v-icon>
          Войти через VK
        </v-btn>

        <div class="text-center mt-2">
          <router-link v-if="settingsStore.isRegistrationEnabled" to="/register">Зарегистрироваться</router-link>
          <span v-if="settingsStore.isRegistrationEnabled && settingsStore.isResetPasswordEnabled"> | </span>
          <router-link v-if="settingsStore.isResetPasswordEnabled" to="/reset">Сбросить пароль</router-link>
        </div>
      </v-card-text>

    </v-card>
  </v-menu>
</template>

<script>
import { useAuth } from '@/composables/useAuth';

export default {
  name: 'Auth',
  setup() {
    const {
      login,
      loginEmail,
      loginPassword,
      settingsStore,
      loginWithGoogle,
      loginWithVK
    } = useAuth();

    return {
      login,
      loginEmail,
      loginPassword,
      settingsStore,
      loginWithGoogle,
      loginWithVK
    };
  }
};
</script>
