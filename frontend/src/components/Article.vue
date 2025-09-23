<template>
  <v-container>
    <v-breadcrumbs :items="breadcrumbs"></v-breadcrumbs>

    <v-card v-if="article">
      <v-card-title>{{ article.title }}</v-card-title>

      <v-card-subtitle v-if="article.is_archived">В архиве</v-card-subtitle>

      <v-img
        :src="articleImage"
        height="300"
        cover
        class="article-image"
        :style="{ maxWidth: articleImageIsDefault ? '400px' : null }"
      ></v-img>

      <v-card-text>
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

    <v-meta v-if="article" :title="article.meta_title" :description="article.meta_description" :keywords="article.seo_keywords"></v-meta>
  </v-container>
</template>

<script>
import axios from 'axios';
import { useRoute } from 'vue-router';
import { onMounted, ref, computed, getCurrentInstance } from 'vue';
import { marked } from 'marked';
import DOMPurify from 'dompurify';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export default {
  components: {
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
    const internalInstance = getCurrentInstance();

    const breadcrumbs = computed(() => [
      { title: 'Главная', href: '/' },
      { title: 'Статьи', disabled: true },
      { title: article.value?.title || 'Статья не найдена', disabled: true },
    ]);

    const formattedDate = computed(() => {
      const dateString = article.value?.published_at || article.value?.created_at;
      if (!dateString) return 'Дата не указана';

      const date = new Date(dateString);
      const options = { year: 'numeric', month: 'long', day: 'numeric' };
      return date.toLocaleDateString('ru-RU', options);
    });

    const articleImage = computed(() => {
      if (!article.value) return '';
      return article.value.image_url ? article.value.image_url : internalInstance.appContext.config.globalProperties.$defaultImage;
    });

    const articleImageIsDefault = computed(() => {
      return !article.value?.image_url;
    });

    const renderedContent = computed(() => {
      if (!article.value?.content) return '';
      const html = marked(article.value.content);
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

    return {
      article,
      breadcrumbs,
      formattedDate,
      error,
      articleImage,
      articleImageIsDefault,
      renderedContent,
    };
  },
};
</script>

<style scoped>
.article-image {
  margin: 16px;
}
</style>
