<template>
  <v-container>
    <v-card class="pt-2">
      <!--  Строка поиска  -->
      <v-card-text class="pt-2">
        <v-text-field
          v-model="searchQuery"
          label="Поиск..."
          append-inner-icon="mdi-magnify"
          @click:append-inner="search"
          @keydown.enter="search"
          hide-details
          rounded="pill"
          variant="outlined"
          clearable
        ></v-text-field>
      </v-card-text>
    </v-card>

    <!-- Значок загрузки -->
    <div v-if="loading" class="d-flex justify-center my-8">
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
      v-else-if="searchResults && searchResults.results && searchResults.metadata"
      class="mb-4"
    >
      <v-card-text>
        <!-- Заголовок и категории -->
        <div class="mb-2">
          <p class="text-h6 mt-1 mt-sm-3 mb-sm-2">
            {{ formatResultText(searchResults.metadata.total_count) }} в {{ formatCategoryText(searchResults.metadata.total_categories) }}
          </p>
          <div>
            <v-chip
              v-for="category in searchResults.categories"
              :key="category"
              class="mr-2 mb-2"
              variant="outlined"
              size="small"
            >
              {{ category }}
            </v-chip>
          </div>
        </div>

        <!-- Список результатов -->
        <v-row class="pt-2">
          <v-col
            v-for="item in searchResults.results"
            :key="item.id"
            cols="12"
            class="pt-1 pb-0"
          >
            <!-- Статьи -->
            <v-card
              v-if="item.category !== 'facts'"
              class="search-result-card"
              @click="() => router.push(`/articles/${item.slug}`)"
            >
              <!-- Mobile -->
              <div v-if="$vuetify.display.xs || $vuetify.display.sm">
                <v-img
                  :src="item.image_url"
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
                      :src="item.image_url"
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

            <!-- Факты -->
            <v-card
              v-else
              class="search-result-card-fact"
              variant="tonal"
            >
              <v-card-text class="pt-2 pb-2 pl-1 pr-1">
                <v-icon color="info" class="mr-2">mdi-lightbulb-on-outline</v-icon>
                <div v-html="item.summary"></div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- Пагинация -->
        <div v-if="searchResults.metadata.total_pages > 1" class="d-flex justify-center mt-6">
          <v-pagination
            v-model="currentPage"
            :length="searchResults.metadata.total_pages"
            @update:modelValue="changePage"
          ></v-pagination>
        </div>

      </v-card-text>
    </v-card>

    <!-- Если нет данных -->
    <div v-else-if="!loading && !error" class="text-center my-8">
      <p>Ничего не найдено.</p>
    </div>
  </v-container>
</template>

<script>
import { onMounted, ref, watch } from 'vue';
import { createRouter as router, useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import DOMPurify from "dompurify";
import AirplaneSVG from "@/components/icons/AirplaneSVG.vue";

export default {
  name: 'Search',
  components: {
    AirplaneSVG
  },
  methods: { router },
  setup() {
    const route = useRoute();
    const router = useRouter();

    const searchQuery = ref('');
    const searchResults = ref(null);
    const loading = ref(false);
    const error = ref(null);
    const currentPage = ref(1);

    // функции для склонения
    const pluralize = (n, forms) => {

      // приводим к числу, если строка
      n = Math.abs(parseInt(n)) || 0;

      // остаток от деления на 100
      const mod100 = n % 100;
      // остаток от деления на 10
      const mod10 = mod100 % 10;

      if (mod100 >= 11 && mod100 <= 20) {
        return forms[2]; // для 11-20 всегда форма "много"
      }

      if (mod10 === 1) {
        return forms[0]; // один
      }

      if (mod10 >= 2 && mod10 <= 4) {
        return forms[1]; // два-четыре
      }

      return forms[2]; // пять-десять, ноль, остальное
    };

    const formatResultText = (count) => {
      const form = pluralize(count, ['результат', 'результата', 'результатов']);
      // добавляем "о" к "Найден" если count != 1
      return `Найден${count === 1 ? '' : 'о'} ${count} ${form}`;
    };

    const formatCategoryText = (count) => {
      // та же логика склонения, что и для результата
      const form = pluralize(count, ['категории', 'категориях', 'категорий']);
      return `${count} ${form}`;
    };

    const search = async () => {
      if (!searchQuery.value.trim()) {
        searchResults.value = null;
        error.value = null;
        return;
      }

      loading.value = true;
      error.value = null;

      try {
        const requestData = {
          query: searchQuery.value,
          page: currentPage.value,
          page_size: 10,
        };

        const response = await axios.post(`/search`, requestData);

        if (response.data.status === 'ok') {
          searchResults.value = response.data.data;
        } else {
          error.value = 'Ошибка при поиске';
        }
      } catch (err) {
        console.error('Search error:', err);
        error.value = 'Ошибка при выполнении запроса';
      } finally {
        loading.value = false;
      }
    };

    const changePage = async (page) => {
      currentPage.value = page;
      // обновление URL при смене страницы, без вызова push, если это первоначальная загрузка
      await router.push({
        query: {
          ...route.query,
          q: searchQuery.value,
          page: page
        }
      });
      await search();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const formatDate = (dateString) => {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    };

    onMounted(() => {
      const queryFromUrl = route.query.q;
      if (queryFromUrl) {
        // санитизация строки запроса перед присвоением
        searchQuery.value = DOMPurify.sanitize(queryFromUrl);
      }
      // устанавливаем currentPage из URL, если он есть, иначе 1
      currentPage.value = parseInt(route.query.page) || 1;
      search();
    });

    // следим за изменением currentPage в URL (например, при навигации назад/вперед)
    watch(
      () => route.query.page,
      (newPageFromUrl) => {
        const newPage = parseInt(newPageFromUrl) || 1;
        if (newPage !== currentPage.value) {
          currentPage.value = newPage;
          search();
        }
      }
    );

    return {
      router,
      searchQuery,
      searchResults,
      loading,
      error,
      currentPage,
      search,
      changePage,
      formatDate,
      formatResultText,
      formatCategoryText,
      AirplaneSVG
    };
  }
};
</script>

<style scoped>
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
  /* margin-bottom: 16px; */
}

:deep(em) {
  background-color: rgb(var(--v-theme-warning)) !important;
  padding: 2px 4px !important;
  border-radius: 3px !important;
  font-style: normal !important;
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
