import { ref, computed, onMounted } from 'vue';
import { profileService } from '@/services/profileService';
import { useAuthStore } from '@/stores/auth';
import { useSnackbar } from '@/composables/useSnackbar';

export function useProfile() {
  const authStore = useAuthStore();

  // Методы уведомлений
  const { showSuccess, showError, showInfo, showWarning } = useSnackbar();

  // Состояния
  const profile = ref(null);
  const editedProfile = ref({});
  const loading = ref(true);
  const saving = ref(false);
  const error = ref(false);
  const isEditing = ref(false);

  // Правила валидации
  const rules = {
    maxLength: (max) => (value) => {
      if (!value) return true;
      return value.length <= max || `Максимальная длина: ${max} символов`;
    }
  };

  // Форматирование даты
  const formatDate = (dateString) => {
    if (!dateString) return 'Не указано';
    const date = new Date(dateString);
    const options = {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    };
    return date.toLocaleDateString('ru-RU', options);
  };

  // Проверка изменений
  const hasChanges = computed(() => {
    if (!profile.value) return false;
    return (
      editedProfile.value.full_name !== profile.value.full_name ||
      editedProfile.value.first_name !== profile.value.first_name ||
      editedProfile.value.last_name !== profile.value.last_name
    );
  });

  // Валидность формы
  const formValid = computed(() => {
    return true;
  });

  // Загрузка профиля
  const fetchProfile = async () => {
    try {
      loading.value = true;
      error.value = false;

      const response = await profileService.getProfile();

      if (response.status === "ok") {
        profile.value = response.data;
        editedProfile.value = {
          full_name: profile.value.full_name || '',
          first_name: profile.value.first_name || '',
          last_name: profile.value.last_name || ''
        };
      } else {
        error.value = true;
        console.error("Ошибка при получении профиля:", response);
      }
    } catch (e) {
      console.error("Ошибка при загрузке профиля:", e);
      error.value = true;
    } finally {
      loading.value = false;
    }
  };

  // Начало редактирования
  const startEditing = () => {
    isEditing.value = true;
  };

  // Отмена редактирования
  const cancelEditing = () => {
    editedProfile.value = {
      full_name: profile.value.full_name || '',
      first_name: profile.value.first_name || '',
      last_name: profile.value.last_name || ''
    };
    isEditing.value = false;
  };

  // Сохранение профиля
  const saveProfile = async () => {
    if (!formValid.value || !hasChanges.value) return;

    try {
      saving.value = true;

      const response = await profileService.updateProfile({
        full_name: editedProfile.value.full_name || null,
        first_name: editedProfile.value.first_name || null,
        last_name: editedProfile.value.last_name || null
      });

      if (response.status === "ok") {
        profile.value = {
          ...profile.value,
          full_name: editedProfile.value.full_name,
          first_name: editedProfile.value.first_name,
          last_name: editedProfile.value.last_name,
          updated_at: new Date().toISOString()
        };

        authStore.setUser({
          ...authStore.user,
          fullName: editedProfile.value.full_name,
          firstName: editedProfile.value.first_name,
          lastName: editedProfile.value.last_name
        });

        isEditing.value = false;
        showSuccess('Профиль успешно обновлен');
        await fetchProfile(); // актуализация
      } else {
        showError('Ошибка при сохранении профиля');
        console.error("Ошибка при сохранении профиля:", response);
      }
    } catch (e) {
      console.error("Ошибка при сохранении профиля:", e);
      showError('Ошибка при сохранении профиля');
    } finally {
      saving.value = false;
    }
  };

  // Инициализация
  onMounted(() => {
    fetchProfile();
  });

  return {
    // Данные
    profile,
    editedProfile,
    loading,
    saving,
    error,
    isEditing,
    rules,
    hasChanges,
    formValid,

    // Методы
    formatDate,
    fetchProfile,
    startEditing,
    cancelEditing,
    saveProfile
  };
}
