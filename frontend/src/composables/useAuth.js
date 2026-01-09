import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useSettingsStore } from '@/stores/settings';
import { useSnackbar } from '@/composables/useSnackbar';
import { loginWithEmailAndPassword, loginWithGoogle, loginWithVK } from '@/services/authService.js';

export const useAuth = () => {
  const authStore = useAuthStore();
  const settingsStore = useSettingsStore();
  const router = useRouter();
  const { showError } = useSnackbar();

  const loginEmail = ref('');
  const loginPassword = ref('');

  const login = async () => {
    if (!loginEmail.value) {
      showError('Введите email');
      return;
    }
    if (!loginPassword.value) {
      showError('Введите пароль');
      return;
    }

    try {
      await loginWithEmailAndPassword(loginEmail.value, loginPassword.value);
      await router.push('/');
    } catch (error) {
      console.error('Login error:', error);
      showError('Произошла ошибка при аутентификации');
    }
  };

  return {
    login,
    loginEmail,
    loginPassword,
    settingsStore,
    authStore,
    loginWithGoogle,
    loginWithVK,
  };
};
