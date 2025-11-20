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
import { computed } from 'vue';

const props = defineProps({
  aircraft: {
    type: Object,
    required: true
  }
});

const fieldDescriptions = {
  name: "Название",
  original_name: "Оригинальное название",
  image_description: "Описание изображения",
  aircraft_type: "Тип воздушного судна",
  aircraft_purpose: "Назначение воздушного судна",
  first_flight: "Первый полёт",
  wingspan: "Размах крыльев (м)",
  length: "Длина (м)",
  height: "Высота (м)",
  max_takeoff_weight: "Максимальный взлётный вес (кг)",
  engine_type: "Тип двигателя",
  number_of_engines: "Количество двигателей",
  max_speed: "Максимальная скорость (км/ч)",
  cruise_speed: "Крейсерская скорость (км/ч)",
  range: "Дальность полёта (км)",
  service_ceiling: "Практический потолок (м)",
  crew: "Экипаж (человек)",
  icao_designator: "Код ИКАО",
  iata_designator: "Код ИАТА",
  status: "Статус",
  year_of_manufacture: "Год начала производства",
  first_used: "Начало эксплуатации",
  last_used: "Окончание эксплуатации",
};

const specs = computed(() => {
  const specData = props.aircraft;
  const result = [];

  for (const [key, label] of Object.entries(fieldDescriptions)) {
    const value = specData[key];

    // пропуск вывода оригинального названия, если совпадает с названием
    if (key === 'original_name' && specData.name && specData.name === value) {
      continue;
    }

    if (value !== null && value !== undefined && value !== "") {
      result.push({ key: label, value, originalKey: key });
    }
  }

  return result;
});

// форматирование данных
const formatValue = (value, fieldKey) => {
  // форматирование строк в формате даты YYYY-MM-DD
  if (typeof value === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(value)) {
    const date = new Date(value);
    const year = date.getFullYear();
    const month = date.getMonth();
    const day = date.getDate();

    // если 1 января или 31 декабря — значит, это просто год (данные при добавлении в базу были неполными)
    if ((month === 0 && day === 1) || (month === 11 && day === 31)) {
      return year.toString();
    }

    // полноценная дата
    return date.toLocaleDateString('ru-RU', { year: 'numeric', month: 'long', day: 'numeric' });
  }

  // форматирование чисел
  if (typeof value === 'number') {
    // поля, которые считаются годами
    const yearFields = [
      'year_of_manufacture',
      'first_used',
      'last_used'
    ];

    // если год — возвращаем как есть
    if (yearFields.some(field => field === fieldKey)) {
      return value.toString();
    }

    // иначе — форматируем с разделением тысяч через &nbsp;
    return value.toLocaleString('ru-RU', {
      useGrouping: true,
      maximumFractionDigits: 20 // если число дробное — оставим как есть
    }).replace(/\s/g, '&nbsp;');
  }

  // иначе возвращаем как есть
  return value;
};
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
