<template>
  <div class="profile-avatar-container d-flex flex-column align-center">
    <!-- Контейнер аватара и кнопок действий -->
    <div class="avatar-and-actions d-flex align-center justify-center mb-4">
      <!-- Аватар -->
      <v-avatar size="160" color="grey-lighten-3" class="mb-4">
        <v-img
          v-if="currentPicture"
          :src="currentPicture"
          alt="Аватар пользователя"
          @load="onImageLoad"
          @error="onImageError"
        ></v-img>
        <v-icon v-else size="64" color="grey-darken-2">
          mdi-account-circle
        </v-icon>
      </v-avatar>

      <!-- Кнопки управления аватаром -->
      <div class="avatar-actions d-flex flex-column">
        <!-- Изменение аватара -->
        <v-btn
          variant="text"
          size="small"
          @click="onImageChange(null)"
          icon="mdi-camera"
          title="Изменить аватар"
          class="mb-1"
        ></v-btn>

        <!-- Удаление аватара -->
        <v-btn
          :disabled="!currentPicture"
          variant="text"
          size="small"
          color="error"
          @click="confirmRemoveAvatar"
          icon="mdi-delete"
          :title="currentPicture ? 'Удалить аватар' : 'Аватар отсутствует'"
        ></v-btn>
      </div>
    </div>

    <!-- Роли -->
    <div class="roles-container mb-4">
      <v-chip
        v-for="role in roles"
        :key="role"
        color="primary"
        variant="outlined"
        class="mr-1 mb-1"
        size="small"
      >
        {{ role }}
      </v-chip>
    </div>

    <!-- Диалог кропа -->
    <v-dialog v-model="showCropper" max-width="800">
      <v-card v-if="showCropper">
        <v-card-title>Редактировать аватар</v-card-title>
        <v-card-text>
          <vue-cropper
            ref="cropperRef"
            :src="imageToCrop"
            :view-mode="2"
            :stencil-component="RectangleStencil"
            :stencil-props="{ aspectRatio: 1 }"
            :zoomable="true"
            :movable="true"
            :rotatable="false"
            :scalable="true"
            class="cropper"
          />
        </v-card-text>
        <v-card-actions>
          <v-btn @click="showCropper = false">Отмена</v-btn>
          <v-btn color="primary" @click="cropImage(cropperRef)">Сохранить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Подтверждение удаления -->
    <v-dialog v-model="showConfirmDialog" max-width="400">
      <v-card>
        <v-card-title>Подтверждение</v-card-title>
        <v-card-text>
          Вы уверены, что хотите удалить аватар?
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="showConfirmDialog = false">Отмена</v-btn>
          <v-btn color="error" @click="removeAvatar">Удалить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { ref } from 'vue';
import { useProfileAvatar } from '@/composables/useProfileAvatar';
import { Cropper as VueCropper } from 'vue-advanced-cropper';
import 'vue-advanced-cropper/dist/style.css';

export default {
  name: 'ProfileAvatar',
  components: {
    VueCropper
  },
  props: {
    picture: {
      type: String,
      default: null
    },
    roles: {
      type: Array,
      default: () => []
    }
  },
  emits: ['avatar-updated', 'avatar-removed'],
  setup(props, { emit }) {
    const currentPicture = ref(props.picture);
    const roles = ref(props.roles);

    const {
      showCropper,
      imageToCrop,
      showConfirmDialog,
      cropperRef,
      onImageChange,
      cropImage,
      confirmRemoveAvatar,
      removeAvatar,
      RectangleStencil
    } = useProfileAvatar({
      emit,
      updatePicture: (newPicture) => {
        currentPicture.value = newPicture;
      },
      updateRoles: (newRoles) => {
        roles.value = newRoles;
      }
    });

    const onImageLoad = () => {
      // console.log('Image loaded');
    };

    const onImageError = () => {
      // console.log('Image failed to load');
    };

    return {
      currentPicture,
      roles,
      showCropper,
      imageToCrop,
      showConfirmDialog,
      cropperRef,
      onImageLoad,
      onImageError,
      onImageChange,
      cropImage,
      confirmRemoveAvatar,
      removeAvatar,
      RectangleStencil
    };
  }
};
</script>

<style scoped>
.profile-avatar-container {
  width: 100%;
}

.avatar-and-actions {
  width: 100%;
}

.roles-container {
  width: 100%;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
}

.cropper {
  height: 400px;
  width: 100%;
}

/* Мобильная адаптация */
@media (max-width: 768px) {
  .avatar-and-actions {
    flex-direction: column;
  }

  .avatar-actions {
    flex-direction: row;
    justify-content: center;
    margin-top: 8px;
  }

  .avatar-actions .v-btn {
    margin: 0 4px;
  }

  .roles-container {
    justify-content: center;
  }
}
</style>
