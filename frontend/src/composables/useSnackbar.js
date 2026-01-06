import { reactive } from 'vue';

// Глобальное состояние уведомлений
const snackbarState = reactive({
  show: false,
  message: '',
  color: 'success',
  timeout: 2000
});

export function useSnackbar() {
  const showSnackbar = (message, color = 'success', timeout = 3000) => {
    snackbarState.show = true;
    snackbarState.message = message;
    snackbarState.color = color;
    snackbarState.timeout = timeout;
  };

  const showSuccess = (message, timeout = 3000) => {
    showSnackbar(message, 'success', timeout);
  };

  const showError = (message, timeout = 3000) => {
    showSnackbar(message, 'error', timeout);
  };

  const showInfo = (message, timeout = 3000) => {
    showSnackbar(message, 'info', timeout);
  };

  const showWarning = (message, timeout = 3000) => {
    showSnackbar(message, 'warning', timeout);
  };

  return {
    snackbarState,
    showSnackbar,
    showSuccess,
    showError,
    showInfo,
    showWarning
  };
}

export { snackbarState };
