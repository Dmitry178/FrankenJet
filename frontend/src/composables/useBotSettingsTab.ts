import { ref, computed } from 'vue';
import { botSettingsService } from '@/services/botSettingsService';
import { useSnackbar } from '@/composables/useSnackbar';

interface BotSettings {
  enabled: boolean;
  model: string;
  scope: string;
  feedback: string;
  user_daily_tokens: number;
  total_daily_tokens: number;
}

export function useBotSettingsTab(initialSettings?: BotSettings) {
  const { showSuccess, showError } = useSnackbar();

  const settings = ref<BotSettings | null>(initialSettings || null);
  const editedSettings = ref<BotSettings>({
    enabled: false,
    model: '',
    scope: '',
    feedback: '',
    user_daily_tokens: 0,
    total_daily_tokens: 0
  });

  const saving = ref(false);
  const error = ref<string | null>(null);

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
      editedSettings.value.feedback !== settings.value.feedback ||
      editedSettings.value.user_daily_tokens !== settings.value.user_daily_tokens ||
      editedSettings.value.total_daily_tokens !== settings.value.total_daily_tokens
    );
  });

  // валидность формы
  const formValid = computed(() => {
    return editedSettings.value.model.trim() !== '' &&
           editedSettings.value.scope.trim() !== '' &&
           editedSettings.value.feedback.trim() !== '' &&
           editedSettings.value.user_daily_tokens >= 0 &&
           editedSettings.value.total_daily_tokens >= 0;
  });

  // установка начальных значений
  const setInitialValues = (newSettings: BotSettings) => {
    settings.value = { ...newSettings };
    editedSettings.value = { ...newSettings };
  };

  // сброс формы к исходным значениям
  const resetForm = () => {
    if (settings.value) {
      editedSettings.value = { ...settings.value };
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

      const response: any = await botSettingsService.updateBotSettings(payload);

      if (response.status === "ok") {
        settings.value = { ...payload };
        editedSettings.value = { ...payload };
        showSuccess('Настройки бота успешно обновлены');
      } else {
        console.error('Ошибка при сохранении настроек бота:', response);
        showError('Ошибка при сохранении настроек бота');
      }
    } catch (e) {
      console.error('Ошибка при сохранении настроек бота:', e);
      showError('Ошибка при сохранении настроек бота');
    } finally {
      saving.value = false;
    }
  };

  return {
    editedSettings,
    saving,
    error,
    rules,
    hasChanges,
    formValid,
    setInitialValues,
    resetForm,
    saveSettings
  };
}
