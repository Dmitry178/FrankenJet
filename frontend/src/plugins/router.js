import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from "@/stores/auth.js";
import { useSettingsStore } from "@/stores/settings.js";
import Home from '@/components/Home.vue';
import AuthGoogle from '@/components/auth/LoginGoogle.vue';
import Register from '@/components/Register.vue';
import ResetPassword from '@/components/ResetPassword.vue';
import Profile from '@/components/profile/Profile.vue';
import Articles from '@/components/articles/Articles.vue';
import Article from '@/components/Article.vue';
import Search from '@/components/Search.vue';
import BotSettings from "@/components/admin/BotSettings.vue";

const routes = [
  {
    path: '/',
    component: Home,
    name: 'Home'
  },
  {
    path: '/auth/google',
    component: AuthGoogle,
    meta: {
      requiresAuth: false,
      requiresEnabled: 'isGoogleOAuthEnabled',
    }
  },
  {
    path: '/register',
    component: Register,
    name: 'Register',
    meta: {
      requiresAuth: false,
      requiresEnabled: 'isRegistrationEnabled'
    }
  },
  {
    path: '/reset',
    component: ResetPassword,
    name: 'ResetPassword',
    meta: {
      requiresAuth: false,
      requiresEnabled: 'isResetPasswordEnabled'
    }
  },
  {
    path: '/profile',
    component: Profile,
    name: 'Profile',
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/articles',
    component: Articles,
    name: 'Articles'
  },
  {
    path: '/articles/:slug',
    component: Article,
    name: 'Article'
  },
  {
    path: '/search',
    component: Search,
    name: 'Search'
  },
  {
    path: '/settings',
    component: BotSettings,
    name: 'BotSettings',
    meta: {
      requiresAuth: true
    }
  },
];

export function setupRouter() {
  const router = createRouter({
    history: createWebHistory(),
    routes,
  });

  router.beforeEach(async (to, from, next) => {
    // проверка доступов
    const settingsStore = useSettingsStore();
    if (!settingsStore.loading && !settingsStore.hasError) {
      await settingsStore.loadSettings();
    }
    const requiresEnabled = to.meta?.requiresEnabled;
    if (requiresEnabled && !settingsStore[requiresEnabled]) {
      next('/');
      return;
    }

    // проверка аутентификации
    const requiresAuth = to.matched.some(record => record.meta?.requiresAuth);
    if (requiresAuth) {
      const authStore = useAuthStore();
      if (!authStore.accessToken) {
        next('/');
        return;
      }
    }
    next();
  });

  return { router };
}
