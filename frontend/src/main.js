import { createApp } from 'vue';
import { createRouter, createWebHistory } from 'vue-router';
import axios from 'axios'
import './assets/main.css'
import App from './App.vue';

import Home from './components/Home.vue';
import Login from './components/Login.vue';
// import AuthGoogle from './components/AuthGoogle.vue';
// import AuthVK from './components/AuthVK.vue';

const routes = [
    { path: '/', component: Home, meta: { requiresAuth: true } },
    { path: '/login', component: Login },
    // { path: '/auth/google', component: AuthGoogle }
    // { path: '/auth/vk', component: AuthVK }
];

const router = createRouter({
    history: createWebHistory(),
    routes
});

// createApp(App).use(router).mount('#app');

const app = createApp(App);
app.config.globalProperties.$axios = axios;

// Проверка, нужна ли авторизация для маршрута
router.beforeEach(async (to, from, next) => {
    const requiresAuth = to.matched.some(record => record.meta.requiresAuth);

    if (requiresAuth) {
        try {
            const response = await axios.get('/auth/info');
            app.config.globalProperties.$user = response.data;
            next();

        } catch (error) {
            if (error.response && error.response.status === 401) {
                next({ path: '/login' });
            } else {
                console.error("Ошибка при проверке авторизации:", error);
                next(false);
            }
        }
    } else {
        next();
    }
});

axios.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response && error.response.status === 401) {
      router.push('/login');
      // if (error.config.url !== 'http://localhost:8111/auth/login') {
      //   router.push('/login');
      // }
      return Promise.reject(error);
    }
    return Promise.reject(error);
  }
);

app.use(router);
app.mount('#app');
