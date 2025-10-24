<template>
  <v-container>
    <div class="article-container">
      <div class="article-content">
        <v-card v-if="article">
          <v-breadcrumbs :items="breadcrumbs"></v-breadcrumbs>
          <v-divider class="ml-7 mr-7"></v-divider>

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

          <!-- Технические характеристики воздушного судна -->
          <Aircraft :aircraft="article.aircraft" />

          <v-card-text class="pt-0">
            <div id="article-content" v-html="renderedContent"></div>
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
      </div>

      <!-- Оглавление -->
      <div v-if="toc.length > 0" class="toc-wrapper">
        <v-card
          class="toc-card"
          elevation=0
        >
          <v-card-title>Содержание</v-card-title>
          <v-card-text>
            <ul class="toc-list">
              <li
                v-for="item in toc"
                :key="item.id"
                :class="{ 'active': activeTocItem === item.id }"
                @click="scrollToSection(item.id)"
              >
                <a href="#" @click.prevent="scrollToSection(item.id)">
                  {{ item.text }}
                </a>
              </li>
            </ul>
          </v-card-text>
        </v-card>
      </div>
    </div>

    <!-- FAB -->
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
import { onMounted, onUnmounted, ref, computed, nextTick } from 'vue';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import AirplaneSVG from "@/components/AirplaneSVG.vue";
import Aircraft from '@/components/Aircraft.vue';

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

    const toc = ref([]);
    const activeTocItem = ref(null);
    let observer = null;

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

    // заголовок изображения в модалке
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

    // конвертация текста из MD в HTML
    const renderedContent = computed(() => {
      if (!article.value?.article.content) return '';

      const html = marked(article.value.article.content);
      const cleanHtml = DOMPurify.sanitize(html, {
        USE_PROFILES: { html: true },  // разрешаем HTML
        ADD_ATTR: ['target', 'rel']
      });

      const parser = new DOMParser();
      const doc = parser.parseFromString(cleanHtml, 'text/html');

      // находим заголовки и добавляем им id
      const headings = doc.querySelectorAll('h1, h2, h3, h4');
      toc.value = [
          { id: 'top', text: 'Начало', level: 1 },
      ];

      headings.forEach((el, index) => {
        const id = `heading-${index}`;
        el.id = id;
        toc.value.push({
          id,
          text: el.textContent.trim(),
          level: parseInt(el.tagName.charAt(1))
        });
      });

      const links = doc.querySelectorAll('a');
      links.forEach(link => {
        link.setAttribute('target', '_blank');
        link.setAttribute('rel', 'noopener noreferrer');
      });

      return doc.body.innerHTML;
    });

    // скроллинг к пунктам таблицы содержания
    const scrollToSection = (id) => {
      if (id === 'top') {
        window.scrollTo({
          top: 0,
          behavior: 'smooth'
        });
        activeTocItem.value = 'top';
      } else {
        const element = document.getElementById(id);
        if (element) {
          const offsetTop = element.offsetTop;
          window.scrollTo({
            top: offsetTop,
            behavior: 'smooth'
          });
        }
      }
    };

    // содержание статьи
    const initObserver = () => {
      nextTick(() => {
        const headings = document.querySelectorAll('#article-content h1, #article-content h2, #article-content h3, #article-content h4');

        toc.value = [
          { id: 'top', text: 'Начало', level: 1 },
        ];

        if (observer) {
          observer.disconnect();
        }

        observer = new IntersectionObserver(
          (entries) => {
            entries.forEach(entry => {
              if (entry.isIntersecting) {
                activeTocItem.value = entry.target.id;
              }
            });
          },
          {
            rootMargin: '-20% 0px -80% 0px'
          }
        );

        headings.forEach((el) => {
          observer.observe(el);
        });
      });
    };

    // отслеживание активного пункта оглавления
    const handleScrollActiveToc = () => {
      const scrolled = window.scrollY;

      if (scrolled < 100) {
        activeTocItem.value = 'top';
        return;
      }

      const scrolledToBottom = window.innerHeight + window.scrollY >= document.body.offsetHeight - 100;
      if (scrolledToBottom && toc.value.length > 0) {
        activeTocItem.value = toc.value[toc.value.length - 1].id;
      }
    };

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
    };

    // прокрутка страницы на начало
    const scrollToTop = () => {
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
      activeTocItem.value = 'top';
    };

    onMounted(async () => {
      // загрузка статьи
      try {
        const response = await axios.get(`/articles/${slug}`);
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

      // инициализируем observer после загрузки статьи
      await nextTick(); // ждём обновления DOM
      initObserver();

      activeTocItem.value = 'top';

      window.addEventListener('scroll', handleScroll);
      window.addEventListener('scroll', handleScrollActiveToc);
    });

    onUnmounted(() => {
      if (observer) {
        observer.disconnect();
      }
      window.removeEventListener('scroll', handleScroll);
      window.removeEventListener('scroll', handleScrollActiveToc);
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
      toc,
      scrollToSection,
      activeTocItem,
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

.article-container {
  display: flex;
  gap: 1rem;
}

.article-content {
  flex: 1;
}

.toc-wrapper {
  position: sticky;
  top: 64px; /* высота тулбара */
  height: calc(100vh - 64px);
  width: 300px;
  overflow-y: auto;
  padding: 0;
}

.toc-card {
  padding: 0;
  font-size: 1.1rem;
  font-weight: bold;
}

.toc-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.toc-list li {
  cursor: pointer;
  font-size: 0.9rem;
}

.toc-list li:hover {
  text-decoration: underline;
}

.toc-list li.active a {
  font-weight: bold;
}

.toc-list a {
  text-decoration: none;
  color: inherit;
  display: block;
  padding: 4px 0;
}

.scroll-top-btn {
  position: fixed !important;
  bottom: 23px !important;
  right: 23px !important;
  z-index: 9999;
}

@media (max-width: 768px) {
  .toc-wrapper {
    display: none !important;
  }

  .article-image {
    height: auto !important;
    margin-top: 1rem !important;
    margin-bottom: 0 !important;
  }
}
</style>
