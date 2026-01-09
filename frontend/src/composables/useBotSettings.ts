import { ref, onMounted } from 'vue';
import { botSettingsService } from '@/services/botSettingsService';

interface FullBotSettings {
  enabled: boolean;
  model: string;
  scope: string;
  system_prompt: string;
  rag_prompt: string;
  feedback: string;
  user_daily_tokens: number;
  total_daily_tokens: number;
}

export function useBotSettings() {
  const fullSettings = ref<FullBotSettings | null>(null);
  const loading = ref(false);
  const error = ref(false);

  const fetchSettings = async () => {
    try {
      loading.value = true;
      error.value = false;

      const response = await botSettingsService.getSettings();

      if (response.status === "ok") {
        fullSettings.value = response.data;
      } else {
        error.value = true;
        console.error('Ошибка при получении настроек:', response);
        showError('Ошибка при загрузке настроек');
      }
    } catch (e) {
      console.error('Ошибка при загрузке настроек:', e);
      showError('Ошибка при загрузке настроек');
      error.value = true;
    } finally {
      loading.value = false;
    }
  };

  onMounted(() => {
    fetchSettings();
  });

  return {
    fullSettings,
    loading,
    error,
    fetchSettings
  };
}
