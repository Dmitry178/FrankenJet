<template>
  <v-container>
    <v-breadcrumbs :items="breadcrumbs"></v-breadcrumbs>

    <v-card v-if="article">
      <v-card-title class="pb-2">{{ article.article.title }}</v-card-title>

      <v-card-subtitle v-if="article.article.is_archived">В архиве</v-card-subtitle>

      <!-- Изображение -->
      <v-img
        :src="articleImage"
        height="300"
        contain
        class="article-image clickable-image"
        :style="{ maxWidth: articleImageIsDefault ? '480px' : null }"
        @click="openImageDialog"
      >
        <template v-if="articleImageIsDefault" #placeholder>
          <AirplaneSVG />
        </template>
      </v-img>

      <!-- Модальное окно -->
      <v-dialog v-model="imageDialog" max-width="900">
        <v-card>
          <v-img
            :src="articleImage"
            :alt="article.aircraft.name || 'Изображение воздушного судна'"
            max-height="80vh"
            contain
          />
          <v-card-text v-if="imageCaption.title || imageCaption.description" class="pt-2 pb-0">
            <div class="modal-image-caption">
              <h4 v-if="imageCaption.title" class="text-h6 font-weight-medium mb-1">
                {{ imageCaption.title }}
              </h4>
              <p v-if="imageCaption.description" class="text-body-2 text--secondary mb-0">
                {{ imageCaption.description }}
              </p>
            </div>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn @click="closeImageDialog" icon>
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <Aircraft :aircraft="article.aircraft" />

      <v-card-text class="pt-0">
        <p v-html="renderedContent"></p>
      </v-card-text>

      <v-card-actions>
        <v-spacer></v-spacer>
        <v-card-text>Опубликовано: {{ formattedDate }}</v-card-text>
      </v-card-actions>
    </v-card>

    <v-alert
      v-else-if="error"
      type="error"
      title="Ошибка"
    >
      Статья не найдена.
    </v-alert>

    <v-btn
      v-if="showScrollTop"
      fab
      icon
      color="secondary"
      class="scroll-top-btn"
      @click="scrollToTop"
      fixed
      bottom
      right
    >
      <v-icon>mdi-arrow-up</v-icon>
    </v-btn>

    <v-meta v-if="article" :title="article.article.meta_title" :description="article.article.meta_description" :keywords="article.article.seo_keywords"></v-meta>

  </v-container>
</template>

<script>
import axios from 'axios';
import { useRoute } from 'vue-router';
import { onMounted, onUnmounted, ref, computed } from 'vue';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import AirplaneSVG from "@/components/AirplaneSVG.vue";
import Aircraft from '@/components/Aircraft.vue';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export default {
  components: {
    AirplaneSVG,
    Aircraft,
    'v-meta': {
      props: ['title', 'description', 'keywords'],
      template: `
        <head>
          <title>{{ title }}</title>
          <meta name="description" :content="description">
          <meta name="keywords" :content="keywords">
        </head>
      `
    },
    'v-breadcrumbs': {
      props: ['items'],
      template: `
        <v-breadcrumbs :items="items">
          <template v-slot:item="{ item }">
            <v-breadcrumbs-item :href="item.href" :disabled="item.disabled">
              {{ item.title }}
            </v-breadcrumbs-item>
          </template>
        </v-breadcrumbs>
      `
    }
  },
  setup() {
    const route = useRoute();
    const slug = route.params.slug;
    const article = ref(null);
    const error = ref(false);
    const showScrollTop = ref(false);
    const scrollTimer = ref(null);

    const breadcrumbs = computed(() => [
      { title: 'Главная', href: '/' },
      { title: 'Статьи', disabled: true },
      { title: article.value?.article.title || 'Статья не найдена', disabled: true },
    ]);

    const formattedDate = computed(() => {
      const dateString = article.value?.article.published_at || article.value?.article.created_at;
      if (!dateString) return 'Дата не указана';

      const date = new Date(dateString);
      const options = { year: 'numeric', month: 'long', day: 'numeric' };
      return date.toLocaleDateString('ru-RU', options);
    });

    const articleImage = computed(() => {
      if (!article.value.article) return '';
      return article.value.aircraft.image_url;
    });

    const articleImageIsDefault = computed(() => {
      return !article.value?.aircraft.image_url;
    });

    const imageDialog = ref(false);

    const openImageDialog = () => {
      imageDialog.value = true;
    };

    const closeImageDialog = () => {
      imageDialog.value = false;
    };

    const imageCaption = computed(() => {
      const { name, original_name, image_description } = article.value.aircraft || {};
      let title = '';

      if (name && original_name && name !== original_name) {
        title = `${name} (${original_name})`;
      } else if (name) {
        title = name;
      }

      return {
        title,
        description: image_description || null
      };
    });

    const renderedContent = computed(() => {
      if (!article.value?.article.content) return '';
      const html = marked(article.value.article.content);
      const cleanHtml = DOMPurify.sanitize(html, {
        USE_PROFILES: { html: true },  // разрешаем HTML
        ADD_ATTR: ['target', 'rel']
      });

      const parser = new DOMParser();
      const doc = parser.parseFromString(cleanHtml, 'text/html');
      const links = doc.querySelectorAll('a');

      links.forEach(link => {
        link.setAttribute('target', '_blank');
        link.setAttribute('rel', 'noopener noreferrer');
      });

      return doc.body.innerHTML;
    });

    // отображение кнопки прокрутки на начало страницы
    const handleScroll = () => {
      showScrollTop.value = window.scrollY > 300;

      // сброс предыдущего таймера
      if (scrollTimer.value) {
        clearTimeout(scrollTimer.value);
      }

      // отображение кнопки при скролле > 300px
      if (window.scrollY > 300) {
        showScrollTop.value = true;
      }

      // запуск таймера на скрытие кнопки через 3 секунды
      // scrollTimer.value = setTimeout(() => {
      //   showScrollTop.value = false;
      // }, 3000);
    };

    // прокрутка страницы на начало
    const scrollToTop = () => {
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    };

    onMounted(async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/articles/${slug}`);
        if (response.data.status === "ok") {
          article.value = response.data.data;
        } else {
          error.value = true;
          console.error("Ошибка при получении данных статьи:", response.data);
        }
      } catch (e) {
        console.log(e);
        error.value = true;
        console.error("Ошибка при загрузке данных статьи:", e);
      }
    });

    onMounted(() => {
      window.addEventListener('scroll', handleScroll);
    });

    onUnmounted(() => {
      window.removeEventListener('scroll', handleScroll);
    });

    return {
      article,
      breadcrumbs,
      formattedDate,
      error,
      articleImage,
      articleImageIsDefault,
      imageDialog,
      imageCaption,
      openImageDialog,
      closeImageDialog,
      renderedContent,
      showScrollTop,
      scrollToTop,
    };
  },
};
</script>

<style scoped>
.article-image >>> img {
  object-position: left center;
}

.clickable-image {
  cursor: pointer;
}

.modal-image-caption {
  text-align: center;
  padding: 0.5rem 0 0 0;
}

.modal-image-caption h4 {
  margin: 0;
}

.modal-image-caption p {
  margin: 0;
  opacity: 0.8;
}

.v-card-actions {
  padding-top: 0;
}

@media (max-width: 768px) {
  .article-image {
    height: auto !important;
    margin-top: 1rem !important;
    margin-bottom: 0 !important;
  }
}

.scroll-top-btn {
  position: fixed !important;
  bottom: 23px !important;
  right: 23px !important;
  z-index: 9999;
}
</style>
