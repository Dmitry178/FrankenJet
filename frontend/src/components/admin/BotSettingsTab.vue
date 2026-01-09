<template>
  <v-card>
    <v-card-text>
      <v-alert
        v-if="error"
        type="error"
        title="Ошибка"
        class="mb-4"
      >
        Не удалось загрузить настройки чат-бота.
        <div class="mt-2">
          <v-btn @click="resetForm" color="error" variant="text" size="small">
            Попробовать снова
          </v-btn>
        </div>
      </v-alert>

      <!-- Форма настроек -->
      <div v-else class="settings-content">
        <v-form @submit.prevent="saveSettings">

          <v-row>
            <v-col cols="12">
              <v-switch
                v-model="editedSettings.enabled"
                label="Активировать чат-бота"
                color="primary"
                class="mb-4"
              ></v-switch>
            </v-col>
          </v-row>

          <v-row>
            <v-col cols="12" md="6">
              <v-textarea
                v-model="editedSettings.model"
                label="Модель ИИ Gigachat"
                placeholder="Введите название модели"
                variant="outlined"
                density="comfortable"
                auto-grow
                :rows="1"
                :rules="[rules.required, rules.maxLength(32)]"
                class="mb-4"
              ></v-textarea>

              <v-textarea
                v-model="editedSettings.scope"
                label="Область применения (scope Gigachat)"
                placeholder="Введите область применения"
                variant="outlined"
                density="comfortable"
                auto-grow
                :rows="1"
                :rules="[rules.required, rules.maxLength(32)]"
                class="mb-4"
              ></v-textarea>
            </v-col>

            <v-col cols="12" md="6">
              <v-textarea
                v-model.number="editedSettings.user_daily_tokens"
                label="Ежедневный лимит токенов на пользователя"
                type="number"
                min="0"
                variant="outlined"
                density="comfortable"
                auto-grow
                :rows="1"
                :rules="[rules.required]"
                class="mb-4"
              ></v-textarea>

              <v-textarea
                v-model.number="editedSettings.total_daily_tokens"
                label="Общий ежедневный лимит токенов"
                type="number"
                min="0"
                variant="outlined"
                density="comfortable"
                auto-grow
                :rows="1"
                :rules="[rules.required]"
                class="mb-4"
              ></v-textarea>
            </v-col>
          </v-row>

          <v-row>
            <v-col cols="12">
              <v-textarea
                v-model="editedSettings.feedback"
                label="Шаблон обратной связи"
                placeholder="Введите шаблон ответа на запрос об обратной связи..."
                rows="3"
                auto-grow
                prepend-inner-icon="mdi-comment-text"
                variant="outlined"
                density="comfortable"
                :rules="[rules.required, rules.maxLength(128)]"
                class="mb-4"
              ></v-textarea>
            </v-col>
          </v-row>
        </v-form>

        <div class="d-flex gap-2 mt-6">
          <v-btn
            color="success"
            variant="elevated"
            @click="saveSettings"
            :loading="saving"
            :disabled="!formValid || !hasChanges"
          >
            <v-icon start>mdi-content-save</v-icon>
            Сохранить изменения
          </v-btn>

          <v-btn
            color="primary"
            variant="outlined"
            @click="resetForm"
            :disabled="saving || !hasChanges"
          >
            <v-icon start>mdi-reload</v-icon>
            Сбросить
          </v-btn>
        </div>

      </div>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { watch } from 'vue';
import { useBotSettingsTab } from '@/composables/useBotSettingsTab';

interface Props {
  initialSettings?: {
    enabled: boolean;
    model: string;
    scope: string;
    feedback: string;
    user_daily_tokens: number;
    total_daily_tokens: number;
  };
}

const props = defineProps<Props>();

const {
  editedSettings,
  saving,
  error,
  rules,
  hasChanges,
  formValid,
  setInitialValues,
  resetForm,
  saveSettings
} = useBotSettingsTab(props.initialSettings);

// установка начальных значений при изменении пропсов
watch(() => props.initialSettings, (newSettings) => {
  if (newSettings) {
    setInitialValues(newSettings);
  }
}, { immediate: true });

// экспорт методов для использования родительским компонентом
defineExpose({
  saveSettings,
  resetForm
});
</script>

<style scoped>
.settings-content {
  padding: 16px 0;
}

.gap-2 {
  gap: 0.5rem;
}

:deep(.v-text-field),
:deep(.v-textarea) {
  margin-bottom: 16px;
}

:deep(.v-textarea:last-child) {
  margin-bottom: 0;
}

@media (max-width: 768px) {
  .settings-content {
    padding: 8px 0;
  }

  .d-flex {
    flex-direction: column;
  }

  .d-flex > .v-btn {
    margin-bottom: 8px;
  }

  .d-flex > .v-btn:last-child {
    margin-bottom: 0;
  }
}
</style>
