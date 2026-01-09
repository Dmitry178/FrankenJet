<template>
  <v-card>
    <v-card-text>
      <v-alert
        v-if="error"
        type="error"
        title="Ошибка"
        class="mb-4"
      >
        Не удалось загрузить настройки промптов.
        <div class="mt-2">
          <v-btn @click="resetForm" color="error" variant="text" size="small">
            Попробовать снова
          </v-btn>
        </div>
      </v-alert>

      <!-- Форма настроек промптов -->
      <div v-else class="prompts-content">
        <v-form @submit.prevent="saveSettings">

          <v-row>
            <v-col cols="12">
              <v-textarea
                v-model="editedSettings.system_prompt"
                label="Системный промпт"
                placeholder="Введите системный промт для чат-бота..."
                rows="6"
                auto-grow
                prepend-inner-icon="mdi-script-text"
                variant="outlined"
                density="comfortable"
                :rules="[rules.required, rules.maxLength(3000)]"
                class="mb-4"
              ></v-textarea>

              <v-textarea
                v-model="editedSettings.rag_prompt"
                label="RAG промпт"
                placeholder="Введите промт для поиска по документам..."
                rows="4"
                auto-grow
                prepend-inner-icon="mdi-file-search"
                variant="outlined"
                density="comfortable"
                :rules="[rules.required, rules.maxLength(2000)]"
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
            class="no-shadow"
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
import { usePromptsSettingsTab } from '@/composables/usePromptsSettingsTab';

interface Props {
  initialSettings?: {
    system_prompt: string;
    rag_prompt: string;
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
} = usePromptsSettingsTab(props.initialSettings);

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
.prompts-content {
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

.no-shadow {
  box-shadow: none !important;
}

.no-shadow:hover {
  box-shadow: none !important;
}

@media (max-width: 768px) {
  .prompts-content {
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
