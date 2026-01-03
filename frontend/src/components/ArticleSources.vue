<template>
  <v-card-text class="pb-0 pt-0">
    <v-expansion-panels flat tile>
      <v-expansion-panel>
        <v-expansion-panel-title class="pa-0 ma-0">
          <h2>
            <strong>Список источников</strong>
          </h2>
        </v-expansion-panel-title>
        <v-expansion-panel-text>
          <div class="sources-content" v-html="renderedSources"></div>
        </v-expansion-panel-text>
      </v-expansion-panel>
    </v-expansion-panels>
  </v-card-text>
</template>

<script setup>
import { computed } from 'vue';
import { marked } from 'marked';
import DOMPurify from 'dompurify';

const props = defineProps({
  sources: {
    type: String,
    required: true,
    default: '',
  },
});

const renderedSources = computed(() => {
  if (!props.sources) return '';

  const html = marked(props.sources);
  return DOMPurify.sanitize(html, {
    USE_PROFILES: { html: true },
    ADD_ATTR: ['target', 'rel'],
  });
});
</script>

<style scoped>
:deep(.v-expansion-panel-text__wrapper) {
  padding: 0 !important;
}

:deep(.v-expansion-panel-title),
:deep(.v-expansion-panel-title--active) {
  min-height: 3rem !important;
  max-height: 3rem !important;
}

.sources-content :deep(ul),
.sources-content :deep(ol) {
  padding-top: 0.5rem;
  padding-left: 1rem;
}

.sources-content :deep(li) {
  margin-bottom: 0;
}

.sources-content :deep(a) {
  font-size: 0.95rem;
}
.sources-content :deep(a:hover) {
  text-decoration: underline;
}
</style>
