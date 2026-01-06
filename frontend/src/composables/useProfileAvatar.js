import { ref } from 'vue';
import { profileAvatarService } from '@/services/profileAvatarService';
import { useAuthStore } from '@/stores/auth';
import { useSnackbar } from '@/composables/useSnackbar';

export function useProfileAvatar({ emit, updatePicture, updateRoles }) {
  const authStore = useAuthStore();
  const { showSuccess, showError } = useSnackbar();

  const showCropper = ref(false);
  const imageToCrop = ref('');
  const showConfirmDialog = ref(false);
  const cropperRef = ref(null);

  // Загрузка изображения на frontend
  const onImageChange = (e) => {
    let file;
    if (e && e.target?.files) {
      file = e.target.files[0];
    } else {
      const input = document.createElement('input');
      input.type = 'file';
      input.accept = 'image/*';
      input.onchange = (event) => {
        file = event.target.files[0];
        if (file) {
          const reader = new FileReader();
          reader.onload = (event) => {
            imageToCrop.value = event.target.result;
            showCropper.value = true;
          };
          reader.readAsDataURL(file);
        }
      };
      input.click();
      return;
    }

    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        imageToCrop.value = event.target.result;
        showCropper.value = true;
      };
      reader.readAsDataURL(file);
    }
  };

  // Обрезка изображения
  const cropImage = async (cropperInstance) => {
    if (!cropperInstance) {
      console.error('Cropper instance not provided');
      return;
    }

    try {
      const result = cropperInstance.getResult();
      if (result && result.canvas) {
        result.canvas.toBlob((blob) => {
          if (blob) {
            const croppedFile = new File([blob], 'avatar.png', { type: 'image/png' });
            handleAvatarUpload(croppedFile);
          }
          showCropper.value = false;
        }, 'image/png');
      } else {
        console.error('Не удалось получить результат кропа');
        showCropper.value = false;
      }
    } catch (e) {
      console.error('Ошибка при кропе аватара:', e);
      showCropper.value = false;
    }
  };

  // Загрузка изображения в backend
  const handleAvatarUpload = async (file) => {
    try {
      const response = await profileAvatarService.uploadAvatar(file);
      if (response.status === 'ok') {
        const newPicture = response.data?.picture;
        updatePicture(newPicture);
        authStore.setUser({
          ...authStore.user,
          picture: newPicture
        });
        emit('avatar-updated', newPicture);
        showSuccess('Аватар успешно обновлён');
      } else {
        showError('Ошибка при загрузке аватара');
      }
    } catch (e) {
      console.error('Ошибка загрузки аватара:', e);
      showError('Ошибка при загрузке аватара');
    }
  };

  const confirmRemoveAvatar = () => {
    showConfirmDialog.value = true;
  };

  // Удаление аватара
  const removeAvatar = async () => {
    try {
      const response = await profileAvatarService.deleteAvatar();
      if (response.status === 'ok') {
        updatePicture(null);
        authStore.setUser({
          ...authStore.user,
          picture: null
        });
        emit('avatar-removed');
        showSuccess('Аватар успешно удалён');
      } else {
        showError('Ошибка при удалении аватара');
      }
    } catch (e) {
      console.error('Ошибка удаления аватара:', e);
      showError('Ошибка при удалении аватара');
    } finally {
      showConfirmDialog.value = false;
    }
  };

  return {
    // Данные
    showCropper,
    imageToCrop,
    showConfirmDialog,
    cropperRef,

    // Методы
    onImageChange,
    cropImage,
    confirmRemoveAvatar,
    removeAvatar
  };
}
