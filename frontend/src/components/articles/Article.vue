<template>
  <v-container>
    <div class="article-container">
      <div class="article-content">
        <v-card v-if="article">
          <v-breadcrumbs :items="breadcrumbs"></v-breadcrumbs>
          <v-divider class="ml-7 mr-7"></v-divider>

          <v-card-title class="pb-2">{{ article.article.title }}</v-card-title>

          <v-card-subtitle v-if="article.article.is_archived">Статья в архиве</v-card-subtitle>

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
          <ArticleImageModal
            v-model="imageDialog"
            :src="articleImage"
            :alt="imageCaption.alt"
            :caption-title="imageCaption.title"
            :caption-description="imageCaption.description"
          />

          <!-- Технические характеристики воздушного судна -->
          <Aircraft :aircraft="article.aircraft" />

          <!-- Статья -->
          <v-card-text class="pt-0">
            <div id="article-content" v-html="renderedContent"></div>
          </v-card-text>

          <!-- Список источников -->
          <ArticleSources v-if="article.article.sources" :sources="article.article.sources" />

          <!-- Список тегов -->
          <v-card-text class="pt-0">
            <ArticleTagsList
              :tags="article.tags"
              @tag-click="setTagAndNavigate"
            />
          </v-card-text>

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
      <ArticleTableOfContents
        :items="toc"
        :active-id="activeTocItem"
        @item-click="scrollToSection"
      />
    </div>

    <v-meta v-if="article" :title="article.article.meta_title" :description="article.article.meta_description" :keywords="article.article.seo_keywords"></v-meta>

  </v-container>
</template>

<script>
import axios from 'axios';
import { useRoute, useRouter } from 'vue-router';
import { onMounted, onUnmounted, ref, computed, nextTick } from 'vue';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import AirplaneSVG from "@/components/icons/AirplaneSVG.vue";
import Aircraft from '@/components/articles/Aircraft.vue';
import ArticleSources from '@/components/articles/ArticleSources.vue';
import ArticleImageModal from '@/components/articles/ArticleImageModal.vue';
import ArticleTagsList from '@/components/articles/ArticleTagsList.vue';
import ArticleTableOfContents from '@/components/articles/ArticleTOC.vue';

export default {
  name: 'Article',
  components: {
    AirplaneSVG,
    Aircraft,
    ArticleSources,
    ArticleImageModal,
    ArticleTagsList,
    ArticleTableOfContents,
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
    const router = useRouter();
    const slug = route.params.slug;
    const article = ref(null);
    const error = ref(false);

    const toc = ref([]);
    const activeTocItem = ref(null);
    let observer = null;

    const breadcrumbs = computed(() => [
      { title: 'Главная', href: '/' },
      { title: 'Статьи', href: '/articles' },
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
      if (!article.value?.article) return '';
      return article.value.aircraft.image_url;
    });

    const articleImageIsDefault = computed(() => {
      return !article.value?.aircraft.image_url;
    });

    const imageDialog = ref(false);

    const openImageDialog = () => {
      imageDialog.value = true;
    };

    // заголовок изображения в модалке
    const imageCaption = computed(() => {
      const { name, original_name, image_description } = article.value.aircraft || {};
      let title = '';
      let alt = 'Изображение воздушного судна';

      if (name && original_name && name !== original_name) {
        title = `${name} (${original_name})`;
        alt = `${name} (${original_name})`;
      } else if (name) {
        title = name;
        alt = name;
      }

      return {
        title,
        description: image_description || null,
        alt,
      };
    });

    // запись выбранного тега в localStorage и переход на /articles
    const setTagAndNavigate = (tag) => {
      localStorage.setItem('articles_selected_tags', JSON.stringify([tag]));
      localStorage.setItem('articles_current_page', '1');
      router.push('/articles');
    };

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
          // позиция элемента
          const offsetTop = element.offsetTop;

          // плавный скролл
          window.scrollTo({
            top: offsetTop,
            behavior: 'smooth'
          });

          // ожидание завершения скролла
          let scrollEndHandler = () => {
            activeTocItem.value = id; // активный пункт
            // убираем обработчик, чтобы он не срабатывал повторно
            window.removeEventListener('scrollend', scrollEndHandler);
          };

          // добавляем заново обработчик события scrollend
          window.addEventListener('scrollend', scrollEndHandler);
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
      await nextTick();  // ждём обновления DOM
      initObserver();

      activeTocItem.value = 'top';

      window.addEventListener('scroll', handleScrollActiveToc);
    });

    onUnmounted(() => {
      if (observer) {
        observer.disconnect();
      }
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
      renderedContent,
      toc,
      activeTocItem,
      openImageDialog,
      setTagAndNavigate,
      scrollToTop,
      scrollToSection,
    };
  },
};
</script>

<style scoped>
.article-image :deep(img) {
  object-position: left center;
}

.clickable-image {
  cursor: pointer;
}

.article-container {
  display: flex;
  gap: 1rem;
}

.article-content {
  flex: 1;
}

@media (min-width: 768px) {
  .v-card-title {
    padding-bottom: 0.15rem !important;
  }

  .v-card-title,
  .v-card-text {
    padding-left: 1.25rem !important;
    padding-right: 1.25rem !important;
  }
}

@media (max-width: 768px) {
  .v-card-title {
    padding-bottom: 0 !important;
  }

  .v-card-text {
    padding-top: 0 !important;
  }

  .article-image {
    height: auto !important;
    margin-top: 0.5rem !important;
    margin-bottom: 1rem !important;
  }
}
</style>
