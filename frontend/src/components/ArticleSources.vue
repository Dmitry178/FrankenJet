<template>
  <v-card-text class="pb-0 pt-0">
    <v-expansion-panels flat tile>
      <v-expansion-panel>
        <v-expansion-panel-title class="pb-0 pt-0 pl-4 pr-4">
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
  padding: 0.5rem 0 0 0 !important;
}

:deep(.v-expansion-panel-title),
:deep(.v-expansion-panel-title--active) {
  min-height: 2.5rem !important;
}

.sources-content >>> ul,
.sources-content >>> ol {
  padding-left: 1rem;
}

.sources-content >>> li {
  margin-bottom: 0.1rem;
}

.sources-content >>> a:hover {
  text-decoration: underline;
}
</style>
