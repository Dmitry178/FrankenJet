<template>
  <v-container>
    <v-card>
      <v-card-title>Профиль пользователя</v-card-title>
      <v-card-text>
        <!-- Состояние загрузки -->
        <div v-if="loading" class="text-center py-8">
          <v-progress-circular
            indeterminate
            color="primary"
          ></v-progress-circular>
          <div class="mt-4">Загрузка профиля...</div>
        </div>

        <!-- Состояние ошибки -->
        <v-alert
          v-else-if="error"
          type="error"
          title="Ошибка"
          class="mb-4"
        >
          Не удалось загрузить профиль пользователя.
          <div class="mt-2">
            <v-btn @click="fetchProfile" color="error" variant="text" size="small">
              Попробовать снова
            </v-btn>
          </div>
        </v-alert>

        <!-- Данные профиля -->
        <div v-else-if="profile" class="profile-content">
          <v-row>
            <v-col cols="12" md="3" class="text-center">
              <ProfileAvatar
                :picture="profile.picture"
                :roles="profile.roles"
              />
            </v-col>

            <!-- Информация о пользователе -->
            <v-col cols="12" md="9">
              <v-list>
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon>mdi-email</v-icon>
                  </template>
                  <v-list-item-subtitle>Login/email</v-list-item-subtitle>
                  <v-list-item-title>{{ profile.email }}</v-list-item-title>
                </v-list-item>

                <v-divider></v-divider>

                <!-- Полное имя -->
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon>mdi-account</v-icon>
                  </template>
                  <v-list-item-subtitle>Полное имя</v-list-item-subtitle>
                  <v-list-item-title :class="{ 'text-grey': !isEditing && !editedProfile.full_name }">
                    <template v-if="!isEditing">
                      {{ editedProfile.full_name || 'Не указано' }}
                    </template>
                    <template v-else>
                      <v-text-field
                        v-model="editedProfile.full_name"
                        placeholder="Введите полное имя"
                        density="compact"
                        hide-details
                        variant="underlined"
                        :rules="[rules.maxLength(64)]"
                      ></v-text-field>
                    </template>
                  </v-list-item-title>
                </v-list-item>

                <v-divider></v-divider>

                <!-- Имя -->
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon>mdi-account-outline</v-icon>
                  </template>
                  <v-list-item-subtitle>Имя</v-list-item-subtitle>
                  <v-list-item-title :class="{ 'text-grey': !isEditing && !editedProfile.first_name }">
                    <template v-if="!isEditing">
                      {{ editedProfile.first_name || 'Не указано' }}
                    </template>
                    <template v-else>
                      <v-text-field
                        v-model="editedProfile.first_name"
                        placeholder="Введите имя"
                        density="compact"
                        hide-details
                        variant="underlined"
                        :rules="[rules.maxLength(64)]"
                      ></v-text-field>
                    </template>
                  </v-list-item-title>
                </v-list-item>

                <v-divider></v-divider>

                <!-- Фамилия -->
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon>mdi-account-outline</v-icon>
                  </template>
                  <v-list-item-subtitle>Фамилия</v-list-item-subtitle>
                  <v-list-item-title :class="{ 'text-grey': !isEditing && !editedProfile.last_name }">
                    <template v-if="!isEditing">
                      {{ editedProfile.last_name || 'Не указано' }}
                    </template>
                    <template v-else>
                      <v-text-field
                        v-model="editedProfile.last_name"
                        placeholder="Введите фамилию"
                        density="compact"
                        hide-details
                        variant="underlined"
                        :rules="[rules.maxLength(64)]"
                      ></v-text-field>
                    </template>
                  </v-list-item-title>
                </v-list-item>

                <v-divider></v-divider>

                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon>mdi-calendar</v-icon>
                  </template>
                  <v-list-item-subtitle>Дата регистрации</v-list-item-subtitle>
                  <v-list-item-title class="text-grey">
                    {{ formatDate(profile.created_at) }}
                  </v-list-item-title>
                </v-list-item>

                <v-divider></v-divider>

                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon>mdi-update</v-icon>
                  </template>
                  <v-list-item-subtitle>Последнее обновление</v-list-item-subtitle>
                  <v-list-item-title class="text-grey">
                    {{ formatDate(profile.updated_at) }}
                  </v-list-item-title>
                </v-list-item>
              </v-list>

              <!-- Действия с профилем -->
              <div class="mt-6">
                <template v-if="!isEditing">
                  <v-btn
                    color="primary"
                    variant="outlined"
                    @click="startEditing"
                    class="mr-2"
                  >
                    <v-icon start>mdi-pencil</v-icon>
                    Редактировать профиль
                  </v-btn>
                </template>
                <template v-else>
                  <v-btn
                    color="success"
                    variant="outlined"
                    @click="saveProfile"
                    class="mr-2"
                    :loading="saving"
                    :disabled="!formValid || !hasChanges"
                  >
                    <v-icon start>mdi-content-save</v-icon>
                    Сохранить
                  </v-btn>

                  <v-btn
                    color="error"
                    variant="outlined"
                    @click="cancelEditing"
                    class="mr-2"
                    :disabled="saving"
                  >
                    <v-icon start>mdi-close</v-icon>
                    Отменить
                  </v-btn>
                </template>
              </div>

            </v-col>
          </v-row>
        </div>
      </v-card-text>
    </v-card>

  </v-container>
</template>

<script>
import { ref } from "vue";
import { useProfile } from '@/composables/useProfile';
import ProfileAvatar from '@/components/profile/ProfileAvatar.vue';

export default {
  components: {
    ProfileAvatar
  },
  setup() {
    // Данные и методы из composable
    const {
      profile,
      editedProfile,
      loading,
      saving,
      error,
      isEditing,
      rules,
      hasChanges,
      formValid,
      formatDate,
      fetchProfile,
      startEditing,
      cancelEditing,
      saveProfile,
    } = useProfile();

    const cropperRef = ref(null);

    return {
      profile,
      editedProfile,
      loading,
      saving,
      error,
      isEditing,
      rules,
      hasChanges,
      formValid,
      formatDate,
      fetchProfile,
      startEditing,
      cancelEditing,
      saveProfile,
    };
  }
};
</script>

<style scoped>
.profile-content {
  padding: 16px 0;
}

.v-progress-circular {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

:deep(.v-text-field) {
  max-width: 300px;
}

:deep(.v-text-field .v-field__input) {
  padding-top: 0;
  padding-bottom: 0;
}

.text-grey {
  opacity: 0.95;
}

@media (max-width: 768px) {
  .profile-content {
    padding: 8px 0;
  }

  .v-list-item {
    padding-left: 0;
    padding-right: 0;
  }
}
</style>
