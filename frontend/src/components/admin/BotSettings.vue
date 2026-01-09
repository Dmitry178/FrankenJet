<template>
  <v-container>
    <v-card>
      <v-card-title>Настройки чат-бота</v-card-title>
      <v-card-text>
        <v-tabs v-model="activeTab">
          <v-tab value="bot">Настройки бота</v-tab>
          <v-tab value="prompts">Промпты</v-tab>
          <v-tab value="rag">RAG база знаний</v-tab>
        </v-tabs>

        <v-window v-model="activeTab" class="mt-4">
          <v-window-item value="bot">
            <BotSettingsTab
              v-if="botSettingsData"
              :initial-settings="botSettingsData"
              ref="botSettingsTabRef"
            />
          </v-window-item>

          <v-window-item value="prompts">
            <PromptsSettingsTab
              v-if="promptsSettingsData"
              :initial-settings="promptsSettingsData"
              ref="promptsSettingsTabRef"
            />
          </v-window-item>

          <v-window-item value="rag">
            <RagTab />
          </v-window-item>
        </v-window>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import BotSettingsTab from './BotSettingsTab.vue';
import PromptsSettingsTab from './PromptsSettingsTab.vue';
import RagTab from './RagTab.vue';
import { useBotSettings } from '@/composables/useBotSettings';

const activeTab = ref('bot');

const { fullSettings } = useBotSettings();

// настройки табов
const botSettingsData = ref(null);
const promptsSettingsData = ref(null);

// ссылки на дочерние компоненты
const botSettingsTabRef = ref();
const promptsSettingsTabRef = ref();

// обновление данных при изменении полных настроек
watch(fullSettings, (newSettings) => {
  if (newSettings) {
    botSettingsData.value = {
      enabled: newSettings.enabled,
      model: newSettings.model,
      scope: newSettings.scope,
      feedback: newSettings.feedback,
      user_daily_tokens: newSettings.user_daily_tokens,
      total_daily_tokens: newSettings.total_daily_tokens
    };

    promptsSettingsData.value = {
      system_prompt: newSettings.system_prompt,
      rag_prompt: newSettings.rag_prompt
    };
  }
}, { immediate: true });
</script>

<style scoped>
.v-window {
  min-height: 400px;
}
</style>
