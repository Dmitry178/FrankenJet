import { ref, computed } from 'vue';
import { botSettingsService } from '@/services/botSettingsService';
import { useSnackbar } from '@/composables/useSnackbar';

interface PromptsSettings {
  system_prompt: string;
  rag_prompt: string;
}

export function usePromptsSettingsTab(initialSettings?: PromptsSettings) {
  const { showSuccess, showError } = useSnackbar();

  const settings = ref<PromptsSettings | null>(initialSettings || null);
  const editedSettings = ref<PromptsSettings>({
    system_prompt: '',
    rag_prompt: ''
  });

  const saving = ref(false);
  const error = ref<string | null>(null);

  // правила валидации
  const rules = {
    required: (value: string) => {
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
      editedSettings.value.system_prompt !== settings.value.system_prompt ||
      editedSettings.value.rag_prompt !== settings.value.rag_prompt
    );
  });

  // валидность формы
  const formValid = computed(() => {
    return editedSettings.value.system_prompt.trim() !== '' &&
           editedSettings.value.rag_prompt.trim() !== '';
  });

  // установка начальных значений
  const setInitialValues = (newSettings: PromptsSettings) => {
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
        ...editedSettings.value
      };

      const response: any = await botSettingsService.updatePromptsSettings(payload);

      if (response.status === "ok") {
        settings.value = { ...payload };
        editedSettings.value = { ...payload };
        showSuccess('Промпты успешно обновлены');
      } else {
        console.error("Ошибка при сохранении промптов:", response);
          showError('Ошибка при сохранении промптов');
      }
    } catch (e) {
      console.error('Ошибка при сохранении промптов:', e);
      showError('Ошибка при сохранении промптов');
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
