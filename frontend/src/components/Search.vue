<template>
  <v-container>
    <v-card class="search-card mb-4">
      <!--  Строка поиска  -->
      <v-card-text>
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
        <div class="mb-4">
          <p class="text-h6">
            Найдено {{ searchResults.metadata.total_count }} результатов в {{ searchResults.metadata.total_categories }} категориях
          </p>
          <div class="mt-2">
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
              :to="`/articles/${item.slug}`"
              class="search-result-card"
              hover
            >
              <v-row no-gutters>
                <v-col cols="3" md="2">
                  <v-img
                    :src="item.image_url"
                    height="120"
                    cover
                    class="ma-4 grayscale-image"
                  >
                    <template #placeholder>
                      <div class="d-flex align-center justify-center fill-height">
                        <v-icon>mdi-image-off</v-icon>
                      </div>
                    </template>
                  </v-img>
                </v-col>
                <v-col cols="9" md="10">
                  <v-card-title class="text-h6 pa-2">
                    {{ item.title }}
                  </v-card-title>
                  <v-card-text class="pa-2">
                    {{ item.summary }}
                  </v-card-text>
                </v-col>
              </v-row>
            </v-card>

            <!-- Факты -->
            <v-card
              v-else
              class="search-result-card-fact"
              variant="tonal"
            >
              <v-card-text class="pt-2 pb-2 pl-1 pr-1">
                <v-icon color="info" class="mr-2">mdi-lightbulb-on-outline</v-icon>
                {{ item.summary }}
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

    <!-- Если нет данных, но и не загружается — показываем пустое состояние -->
    <div v-else-if="!loading && !error" class="text-center my-8">
      <p>Ничего не найдено.</p>
    </div>
  </v-container>
</template>

<script>
import {onMounted, ref, watch} from 'vue';
import {useRoute, useRouter} from 'vue-router';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export default {
  name: 'Search',
  setup() {
    const route = useRoute();
    const router = useRouter();

    const searchQuery = ref('');
    const searchResults = ref(null);
    const loading = ref(false);
    const error = ref(null);
    const currentPage = ref(1);

    const search = async () => {
      if (!searchQuery.value.trim()) {
        searchResults.value = null;
        error.value = null;
        return;
      }

      loading.value = true;
      error.value = null;

      try {
        const response = await axios.get(`${API_BASE_URL}/search`, {
          params: {
            q: searchQuery.value,
            page: currentPage.value,
            limit: 10
          }
        });

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
      const query = route.query.q;
      if (query) {
        searchQuery.value = query;
      }
      // устанавливаем currentPage из URL, если он есть, иначе 1
      currentPage.value = parseInt(route.query.page) || 1;
      search();
    });

    /*
    // следим за набором текста в строке поиска
    watch(searchQuery, (newQuery) => {
      if (newQuery !== route.query.q) {
        const newQueryParams = {
          ...route.query,
          q: newQuery || undefined, // если пустой, удаляем параметр
          page: newQuery ? 1 : undefined // если новый запрос, сбрасываем на страницу 1, иначе удаляем page
        };
        if (newQuery) {
          newQueryParams.page = 1; // всегда сбрасываем на первую страницу при новом поиске
          currentPage.value = 1; // синхронизируем локальное состояние
        }
        router.replace({ query: newQueryParams });
        if (newQuery) {
          search();
        } else {
          // очищаем результаты, если запрос пустой
          searchResults.value = null;
          error.value = null;
        }
      }
    });
    */

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

    /*
    // следим за изменением searchQuery в URL (например, при навигации назад/вперед или вводе в адресной строке)
    watch(
      () => route.query.q,
      (newQueryFromUrl) => {
        if (newQueryFromUrl !== searchQuery.value) {
          searchQuery.value = newQueryFromUrl || '';
          // Если в URL есть новый запрос, сбрасываем на 1 страницу, если не указана другая
          currentPage.value = parseInt(route.query.page) || 1;
          if (newQueryFromUrl) {
            search();
          } else {
            searchResults.value = null;
            error.value = null;
          }
        }
      }
    );
    */

    return {
      searchQuery,
      searchResults,
      loading,
      error,
      currentPage,
      search,
      changePage,
      formatDate
    };
  }
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

@media (max-width: 768px) {
  .search-result-card {
    flex-direction: column;
  }
}
</style>
