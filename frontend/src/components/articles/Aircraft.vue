<template>
  <!-- Панель с характеристиками -->
  <v-card-text class="pb-0 pt-6">
    <v-expansion-panels flat tile>
      <v-expansion-panel>
        <v-expansion-panel-title class="pb-0 pt-0 pl-4 pr-4">Технические характеристики</v-expansion-panel-title>
        <v-expansion-panel-text>
          <v-table density="compact" class="spec-table">
            <thead>
              <tr>
                <th>Параметр</th>
                <th>Значение</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="spec in specs" :key="spec.originalKey">
                <td>{{ spec.key }}</td>
                <td v-html="formatValue(spec.value, spec.originalKey)"></td>
              </tr>
            </tbody>
          </v-table>
        </v-expansion-panel-text>
      </v-expansion-panel>
    </v-expansion-panels>
  </v-card-text>
</template>

<script setup>
import { useAircraft } from '@/composables/useAircraft.js';
import { toRef } from 'vue';

const props = defineProps({
  aircraft: {
    type: Object,
    required: true
  }
});

// реактивная ссылка из props
const aircraftRef = toRef(props, 'aircraft');

// хук для получения данных
const { specs, formatValue } = useAircraft(aircraftRef);
</script>

<style scoped>
:deep(.v-expansion-panel) {
  border-top: 1px solid rgb(var(--v-theme-border));
  border-bottom: 1px solid rgb(var(--v-theme-border));
}

:deep(.v-expansion-panel-text__wrapper) {
  padding: 0 !important;
}

:deep(.v-expansion-panel-title),
:deep(.v-expansion-panel-title--active) {
  min-height: 2.5rem !important;
}

.spec-table {
  table-layout: auto;
  width: 100%;
}

.spec-table th,
.spec-table td {
  padding: 8px;
  text-align: left;
  border-bottom: 1px solid rgba(var(--v-theme-border), 0.12);
  white-space: nowrap;
}

.spec-table th:first-child,
.spec-table td:first-child {
  min-width: max-content;
  overflow: hidden;
  text-overflow: ellipsis;
}

.spec-table th:last-child,
.spec-table td:last-child {
  width: 100%;
  word-break: break-all;
}

.spec-table th {
  font-weight: bold;
  background-color: rgba(var(--v-theme-border), 0.25);
}

.spec-table tbody tr:hover {
  background-color: rgba(var(--v-theme-border), 0.25);
}

@media (max-width: 768px) {
  .spec-table th,
  .spec-table td {
    padding: 6px;
    font-size: 0.9rem;
    white-space: normal;
  }

  .spec-table td:first-child {
    min-width: auto;
    width: 40%;
  }
}
</style>
