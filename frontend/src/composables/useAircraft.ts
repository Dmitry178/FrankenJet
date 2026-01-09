/**
 * @typedef {import('vue').Ref} Ref
 */

import { computed } from 'vue';

// интерфейс для воздушного судна
interface Aircraft {
  name?: string;
  original_name?: string;
  image_description?: string;
  aircraft_type?: string;
  aircraft_purpose?: string;
  first_flight?: string | number;
  wingspan?: number;
  length?: number;
  height?: number;
  max_takeoff_weight?: number;
  engine_type?: string;
  number_of_engines?: number;
  max_speed?: number;
  cruise_speed?: number;
  range?: number;
  service_ceiling?: number;
  crew?: number;
  icao_designator?: string;
  iata_designator?: string;
  status?: string;
  year_of_manufacture?: number;
  first_used?: number;
  last_used?: number;
  [key: string]: any; // для возможности доступа к другим полям
}

// описания полей
const FIELD_DESCRIPTIONS = {
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

// поля, которые считаются годами
const YEAR_FIELDS = [
  'year_of_manufacture',
  'first_used',
  'last_used'
];

type YearField = typeof YEAR_FIELDS[number]; // 'year_of_manufacture' | 'first_used' | 'last_used'

/**
 * Форматирование значения в зависимости от типа поля
 * @param {any} value - Значение
 * @param {string} fieldKey - Ключ поля
 * @returns {string} - Отформатированное значение
 */
const formatValue = (value, fieldKey): string => {
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
    // если год — возвращаем как есть
    if (YEAR_FIELDS.some(field => field === fieldKey)) {
      return value.toString();
    }

    // иначе - форматируем с разделением тысяч через &nbsp;
    return value.toLocaleString('ru-RU', {
      useGrouping: true,
      maximumFractionDigits: 20 // если число дробное — оставим как есть
    }).replace(/\s/g, '&nbsp;');
  }

  // иначе возвращаем как есть
  return String(value);
};

// тип возвращаемого значения хука
interface UseAircraftReturn {
  specs: ComputedRef<SpecItem[]>;
  formatValue: (value: any, fieldKey: string) => string;
}

/**
 * Хук для работы с данными воздушного судна
 * @param {Ref<Object>} aircraft - Реактивная ссылка на объект с данными воздушного судна
 * @returns {Object} - Объект с вычисленными значениями
 */
export function useAircraft(aircraft): UseAircraftReturn {
  // вычисляемые технические характеристики
  const specs = computed(() => {
    const specData = aircraft.value || {};
    const result = [];

    for (const [key, label] of Object.entries(FIELD_DESCRIPTIONS)) {
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

  return {
    specs,
    formatValue
  };
}
