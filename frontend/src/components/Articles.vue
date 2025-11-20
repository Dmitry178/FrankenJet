<template>
  <v-container>
    <!-- Секции тегов -->
    <v-card class="mb-0 mb-sm-2 pt-0 pt-sm-2">
      <v-card-text>
        <div v-for="(tags, category) in allTags" :key="category" class="mb-1">
          <h5 class="text-h6 mt-1 mb-1">{{ category }}</h5>
          <div>
            <v-chip
              v-for="tag in tags"
              :key="tag"
              class="mr-2 mb-2"
              size="small"
              variant="outlined"
              :class="{ 'v-chip--selected': selectedTags.includes(tag) }"
              @click="toggleTag(tag)"
            >
              {{ tag }}
            </v-chip>
          </div>
        </div>
      </v-card-text>
    </v-card>

    <!-- Значок загрузки поверх -->
    <div v-if="loading" class="d-flex justify-center my-8" style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 1000;">
      <v-progress-circular indeterminate color="primary"></v-progress-circular>
    </div>

    <!-- Ошибка -->
    <v-alert
      v-else-if="error"
      type="error"
      variant="tonal"
      class="mb-4"
    >
      {{ error }}
    </v-alert>

    <!-- Основная карточка с результатами -->
    <v-card
      v-else-if="articles && articles.length > 0"
      class="mb-4"
    >
      <v-card-text>
        <p class="text-h6 pt-0 pt-sm-3">
          Найдено {{ articles.length }} {{ pluralize(articles.length, ['статья', 'статьи', 'статей']) }}
        </p>

        <!-- Список результатов -->
        <v-row class="pt-0">
          <v-col
            v-for="item in articles"
            :key="item.id"
            cols="12"
            class="pt-1 pb-0"
          >
            <!-- Статьи -->
            <v-card
              class="search-result-card"
              @click="() => router.push(`/articles/${item.slug}`)"
            >
              <!-- Mobile -->
              <div v-if="$vuetify.display.xs || $vuetify.display.sm">
                <v-img
                  :src="getImageUrl(item.image_url)"
                  aspect-ratio="16/9"
                  class="grayscale-image"
                  cover
                >
                </v-img>
                <v-card-title class="text-h6 pa-4">
                  {{ item.title }}
                </v-card-title>
                <v-card-text class="pa-4">
                  <div v-html="item.summary"></div>
                </v-card-text>
              </div>

              <!-- Desktop -->
              <div v-else>
                <v-row no-gutters>
                  <v-col cols="3" md="2">
                    <v-img
                      :src="getImageUrl(item.image_url)"
                      height="120"
                      class="ma-4 grayscale-image"
                      cover
                    >
                      <template #placeholder>
                        <v-img
                          src=""
                          height="120"
                          class="airplane-svg-wrapper"
                          cover
                        >
                          <AirplaneSVG class="airplane-svg" />
                        </v-img>
                      </template>
                    </v-img>
                  </v-col>
                  <v-col cols="9" md="10">
                    <v-card-title class="result-card text-h6 pa-2">
                      {{ item.title }}
                    </v-card-title>
                    <v-card-text class="result-card pa-2">
                      <div v-html="item.summary"></div>
                    </v-card-text>
                  </v-col>
                </v-row>
              </div>
            </v-card>
          </v-col>
        </v-row>

        <!-- Пагинация -->
        <div v-if="totalPages > 1" class="d-flex justify-center mt-6">
          <v-pagination
            v-model="currentPage"
            :length="totalPages"
            @update:modelValue="changePage"
          ></v-pagination>
        </div>
      </v-card-text>
    </v-card>

    <!-- Если нет данных -->
    <div v-else-if="!loading && !error && selectedTags.length > 0" class="text-center my-8">
      <p>Ничего не найдено по выбранным тегам.</p>
    </div>

    <!-- Если теги не выбраны -->
    <div v-else-if="selectedTags.length === 0" class="text-center my-8">
      <p>Выберите теги для отображения статей</p>
    </div>
  </v-container>
</template>

<script>
import { useRouter } from 'vue-router';
import { onMounted, ref } from "vue";
import { useSettingsStore } from '@/stores/settings';
import axios from 'axios';
import AirplaneSVG from "@/components/AirplaneSVG.vue";

export default {
  name: 'Articles',
  components: {
    AirplaneSVG
  },
  setup() {
    const router = useRouter();
    const settingsStore = useSettingsStore();

    const allTags = ref({});
    const selectedTags = ref([]);
    const articles = ref([]);
    const loading = ref(false);
    const error = ref(null);
    const currentPage = ref(1);
    const totalPages = ref(1);

    // константы для ключей localStorage
    const STORAGE_KEYS = {
      SELECTED_TAGS: 'articles_selected_tags',
      CURRENT_PAGE: 'articles_current_page'
    };

    // функция для получения полного URL изображения
    const getImageUrl = (imagePath) => {
      const baseUrl = settingsStore.settings.urls?.images || '';
      if (baseUrl && imagePath) {
        return `${baseUrl}${imagePath.startsWith('/') ? '' : '/'}${imagePath}`;
      }
      return imagePath;
    };

    // функции для склонения
    const pluralize = (n, forms) => {
      n = Math.abs(parseInt(n)) || 0;
      const mod100 = n % 100;
      const mod10 = mod100 % 10;

      if (mod100 >= 11 && mod100 <= 20) {
        return forms[2];
      }

      if (mod10 === 1) {
        return forms[0];
      }

      if (mod10 >= 2 && mod10 <= 4) {
        return forms[1];
      }

      return forms[2];
    };

    // сохранение тегов в localStorage
    const saveSelectedTagsToStorage = () => {
      try {
        localStorage.setItem(STORAGE_KEYS.SELECTED_TAGS, JSON.stringify(selectedTags.value));
      } catch (e) {
        console.warn('Ошибка сохранения выбранных тегов в localStorage:', e);
      }
    };

    // восстановление тегов из localStorage
    const loadSelectedTagsFromStorage = () => {
      try {
        const stored = localStorage.getItem(STORAGE_KEYS.SELECTED_TAGS);
        if (stored) {
          const parsed = JSON.parse(stored);
          if (Array.isArray(parsed)) {
            selectedTags.value = parsed;
          }
        }
      } catch (e) {
        console.warn('Ошибка загрузки выбранных тегов из localStorage:', e);
        selectedTags.value = [];
      }
    };

    // сохранение номера страницы в localStorage
    const saveCurrentPageToStorage = () => {
      try {
        localStorage.setItem(STORAGE_KEYS.CURRENT_PAGE, currentPage.value.toString());
      } catch (e) {
        console.warn('Ошибка сохранения номера текущей страницы в localStorage:', e);
      }
    };

    // восстановление номера страницы из localStorage
    const loadCurrentPageFromStorage = () => {
      try {
        const stored = localStorage.getItem(STORAGE_KEYS.CURRENT_PAGE);
        if (stored) {
          const parsed = parseInt(stored, 10);
          if (!isNaN(parsed) && parsed > 0) {
            currentPage.value = parsed;
          }
        }
      } catch (e) {
        console.warn('Ошибка чтение номера текущей страницы из localStorage:', e);
        currentPage.value = 1;
      }
    };

    const fetchTags = async () => {
      try {
        const response = await axios.get('/pages/articles');
        if (response.data.status === 'ok') {
          allTags.value = response.data.data.tags;
        } else {
          console.error('Ошибка при получении тегов:', response.data);
        }
      } catch (error) {
        console.error('Ошибка при загрузке тегов:', error);
      }
    };

    const fetchArticles = async () => {
      if (selectedTags.value.length === 0) {
        articles.value = [];
        return;
      }

      loading.value = true;
      error.value = null;

      try {
        const tagsParam = selectedTags.value.join(',');
        const response = await axios.get(`/articles/list?tags=${encodeURIComponent(tagsParam)}&page=${currentPage.value}`);

        if (response.data.status === 'ok') {
          articles.value = response.data.data;
        } else {
          error.value = 'Ошибка при загрузке статей';
        }
      } catch (err) {
        console.error('Fetch articles error:', err);
        error.value = 'Ошибка при выполнении запроса';
      } finally {
        loading.value = false;
      }
    };

    const toggleTag = async (tag) => {
      const index = selectedTags.value.indexOf(tag);
      if (index > -1) {
        selectedTags.value.splice(index, 1);
      } else {
        selectedTags.value.push(tag);
      }
      currentPage.value = 1; // сброс на первую страницу при изменении тегов

      saveSelectedTagsToStorage();
      saveCurrentPageToStorage();

      // сохраняем текущую позицию прокрутки
      const scrollPosition = window.scrollY;

      // вызываем fetchArticles асинхронно, чтобы не блокировать UI
      await fetchArticles();

      // восстанавливаем позицию прокрутки
      window.scrollTo({ top: scrollPosition, behavior: 'auto' }); // 'auto' для мгновенного возврата
    };

    const changePage = async (page) => {
      currentPage.value = page;
      // для смены страницы оставляем прокрутку к началу
      window.scrollTo({ top: 0, behavior: 'smooth' });
      await fetchArticles();
    };

    onMounted(async () => {
      // загрузка тегов
      await fetchTags();
      // восстановление состояния из localStorage
      loadSelectedTagsFromStorage();
      loadCurrentPageFromStorage();
      // загрузка статей
      if (selectedTags.value.length > 0) {
        await fetchArticles();
      }
    });

    return {
      router,
      allTags,
      selectedTags,
      articles,
      getImageUrl,
      loading,
      error,
      currentPage,
      totalPages,
      pluralize,
      fetchTags,
      fetchArticles,
      toggleTag,
      changePage,
      AirplaneSVG
    };
  },
};
</script>

<style scoped>
.search-card {
  margin: 16px 0;
}

.search-result-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.search-result-card:hover {
  transform: scale(1.005);
  text-decoration: none;
}

.grayscale-image {
  filter: grayscale(100%);
}

.search-result-card-fact {
  cursor: default;
}

.search-result-card-fact:hover {
  transform: none;
  background-color: inherit;
}

.search-result-card,
.search-result-card-fact {
  margin-bottom: 16px;
}

:deep(em) {
  background-color: rgb(var(--v-theme-warning)) !important;
  padding: 2px 4px !important;
  border-radius: 3px !important;
  font-style: normal !important;
}

.v-chip--selected {
  background-color: rgb(var(--v-theme-primary));
  color: white;
}

@media (min-width: 768px) {
  .result-card.v-card-title{
    padding-left: 0 !important;
    padding-bottom: 0 !important;
    margin-left: 0 !important;
  }

  .result-card.v-card-text{
    padding-left: 0 !important;
    padding-bottom: 1rem !important;
    margin-left: 0 !important;
  }
}

@media (max-width: 768px) {
  .search-result-card {
    flex-direction: column;
  }
}
</style>
