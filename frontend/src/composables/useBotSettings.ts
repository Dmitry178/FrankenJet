import { ref, computed, onMounted } from 'vue';
import { botSettingsService } from '@/services/botSettingsService';
import { useSnackbar } from '@/composables/useSnackbar';

interface BotSettings {
  enabled: boolean;
  model: string;
  scope: string;
  system_prompt: string;
  rag_prompt: string;
  feedback: string;
  user_daily_tokens: number;
  total_daily_tokens: number;
}

interface EditedBotSettings extends Omit<BotSettings, 'user_daily_tokens' | 'total_daily_tokens'> {
  user_daily_tokens: number;
  total_daily_tokens: number;
}

export function useBotSettings() {
  // методы уведомлений
  const { showSuccess, showError, showInfo, showWarning } = useSnackbar();

  // состояния
  const settings = ref<BotSettings | null>(null);
  const editedSettings = ref<EditedBotSettings>({
    enabled: false,
    model: '',
    scope: '',
    system_prompt: '',
    rag_prompt: '',
    feedback: '',
    user_daily_tokens: 10000,
    total_daily_tokens: 50000
  });

  const saving = ref(false);
  const error = ref(false);

  // правила валидации
  const rules = {
    required: (value: string | number) => {
      if (value === null || value === undefined || value === '') return 'Обязательное поле';
      if (typeof value === 'string' && value.trim() === '') return 'Обязательное поле';
      return true;
    },
    maxLength: (max: number) => (value: string) => {
      if (!value) return true;
      return value.length <= max || `Максимальная длина: ${max} символов`;
    }
  };

  // проверка изменений
  const hasChanges = computed(() => {
    if (!settings.value) return false;

    return (
      editedSettings.value.enabled !== settings.value.enabled ||
      editedSettings.value.model !== settings.value.model ||
      editedSettings.value.scope !== settings.value.scope ||
      editedSettings.value.system_prompt !== settings.value.system_prompt ||
      editedSettings.value.rag_prompt !== settings.value.rag_prompt ||
      editedSettings.value.feedback !== settings.value.feedback ||
      editedSettings.value.user_daily_tokens !== settings.value.user_daily_tokens ||
      editedSettings.value.total_daily_tokens !== settings.value.total_daily_tokens
    );
  });

  // валидность формы
  const formValid = computed(() => {
    // проверка обязательных полей
    return editedSettings.value.model.trim() !== '' &&
           editedSettings.value.scope.trim() !== '' &&
           editedSettings.value.user_daily_tokens >= 0 &&
           editedSettings.value.total_daily_tokens >= 0;
  });

  // загрузка настроек
  const fetchSettings = async () => {
    try {
      error.value = false;

      const response = await botSettingsService.getSettings();

      if (response.status === "ok") {
        settings.value = response.data;
        editedSettings.value = {
          ...response.data,
          user_daily_tokens: response.data.user_daily_tokens,
          total_daily_tokens: response.data.total_daily_tokens
        };
      } else {
        error.value = true;
        console.error("Ошибка при получении настроек:", response);
      }
    } catch (e) {
      console.error("Ошибка при загрузке настроек:", e);
      error.value = true;
      showError('Ошибка при загрузке настроек приложения');
    }
  };

  // сброс формы к исходным значениям
  const resetForm = () => {
    if (settings.value) {
      editedSettings.value = {
        ...settings.value,
        user_daily_tokens: settings.value.user_daily_tokens,
        total_daily_tokens: settings.value.total_daily_tokens
      };
    }
  };

  // сохранение настроек
  const saveSettings = async () => {
    if (!formValid.value || !hasChanges.value) return;

    try {
      saving.value = true;

      const payload = {
        ...editedSettings.value,
        user_daily_tokens: parseInt(String(editedSettings.value.user_daily_tokens)),
        total_daily_tokens: parseInt(String(editedSettings.value.total_daily_tokens))
      };

      const response: any = await botSettingsService.updateSettings(payload);

      if (response.status === "ok") {
        settings.value = {
          ...payload,
          user_daily_tokens: payload.user_daily_tokens,
          total_daily_tokens: payload.total_daily_tokens
        };

        showSuccess('Настройки приложения успешно обновлены');
      } else {
        showError('Ошибка при сохранении настроек');
        console.error("Ошибка при сохранении настроек:", response);
      }
    } catch (e) {
      console.error("Ошибка при сохранении настроек:", e);
      showError('Ошибка при сохранении настроек приложения');
    } finally {
      saving.value = false;
    }
  };

  // инициализация
  onMounted(() => {
    fetchSettings();
  });

  return {
    // данные
    settings,
    editedSettings,
    saving,
    error,
    rules,
    hasChanges,
    formValid,

    // методы
    fetchSettings,
    resetForm,
    saveSettings
  };
}
