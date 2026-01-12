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

    <VMeta v-if="article"
      :title="article.article.meta_title"
      :description="article.article.meta_description"
      :keywords="article.article.seo_keywords">
    </VMeta>

  </v-container>
</template>

<script setup lang="ts">
import { useArticle } from '@/composables/useArticle';
import VMeta from '@/components/common/VMeta.vue';
import AirplaneSVG from "@/components/icons/AirplaneSVG.vue";
import Aircraft from '@/components/articles/Aircraft.vue';
import ArticleSources from '@/components/articles/ArticleSources.vue';
import ArticleImageModal from '@/components/articles/ArticleImageModal.vue';
import ArticleTagsList from '@/components/articles/ArticleTagsList.vue';
import ArticleTableOfContents from '@/components/articles/ArticleTOC.vue';

const {
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
  scrollToTop,
  openImageDialog,
  setTagAndNavigate,
  scrollToSection,
} = useArticle();
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
