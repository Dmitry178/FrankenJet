import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from "@/stores/auth.js";
import Home from '../components/Home.vue';
import Login from '../components/Login.vue';
import AuthGoogle from '../components/LoginGoogle.vue';
import Register from '../components/Register.vue';
import ResetPassword from '../components/ResetPassword.vue';
import Article from '../components/Article.vue';
import Search from '../components/Search.vue';

const routes = [
  { path: '/', component: Home, name: 'Home' },
  { path: '/login', component: Login, name: 'Login' },
  { path: '/auth/google', component: AuthGoogle },
  { path: '/register', component: Register, name: 'Register' },
  { path: '/reset', component: ResetPassword, name: 'ResetPassword' },
  { path: '/articles/:slug', component: Article, name: 'Article' },
  { path: '/search', component: Search, name: 'Search' },
];

export function setupRouter() {
  const router = createRouter({
    history: createWebHistory(),
    routes,
  });

  router.beforeEach((to, from, next) => {
    const requiresAuth = to.matched.some(record => record.meta?.requiresAuth);

    if (requiresAuth) {
      const authStore = useAuthStore();
      if (!authStore.accessToken) {
        next('/');
      } else {
        next();
      }
    } else {
      next();
    }
  });

  return { router };
}
