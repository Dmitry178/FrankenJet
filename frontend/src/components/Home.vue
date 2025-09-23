<template>
  <v-container>
    <!-- Описание проекта -->
    <v-card class="mb-4">
      <v-card-title>Добро пожаловать в мир авиации!</v-card-title>
      <v-card-text>
        <p>
          Этот проект - ваш путеводитель по истории авиации, созданный для всех, кто увлекается крылатыми машинами и героями неба.
          Здесь вы  найдете увлекательные истории о самолетах, вертолетах, дирижаблях и множестве других летательных аппаратов.
          Узнайте о выдающихся конструкторах, легендарных производителях и  странах, которые внесли свой вклад в развитие авиации.
        </p>
      </v-card-text>
    </v-card>

    <!-- Статьи -->
    <v-card class="mb-4" v-if="articles.length > 0">
      <v-card-title>Статьи</v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12" sm="6" md="4" lg="3" v-for="article in articles" :key="article.slug">
            <v-card @click="goToArticle(article.slug)" class="article-card">
              <v-img
                :src="articleImage(article)"
                height="200"
                cover
              ></v-img>
              <v-card-title>{{ article.title }}</v-card-title>
              <v-card-text>
                {{ article.summary }}
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Интересные факты -->
    <v-card class="mb-4" v-if="facts.length > 0">
      <v-card-title>Интересные факты</v-card-title>
      <v-card-text>
        <ul>
          <li v-for="(fact, index) in facts" :key="index">{{ fact }}</li>
        </ul>
      </v-card-text>
    </v-card>

  </v-container>
</template>

<script>
import axios from 'axios';
import { inject } from "vue";
import { useRouter } from 'vue-router';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export default {
  components: {

  },
  setup() {
    const router = useRouter();
    return { router };
  },
  data() {
    return {
      articles: [],
      facts: [],
    };
  },
  mounted() {
    this.fetchHomeData();
  },
  methods: {
    articleImage(article) {
      return article.thumbnail_url ? article.thumbnail_url : this.$defaultImage;
    },
    async fetchHomeData() {
      try {
        const response = await axios.get(`${API_BASE_URL}/pages/home`);
        if (response.data.status === "ok") {
          this.articles = response.data.data.articles;
          this.facts = response.data.data.facts;
        } else {
          console.error("Ошибка при получении данных с бэкенда:", response.data);
        }
      } catch (error) {
        console.error("Ошибка при загрузке данных главной страницы:", error);
      }
    },
    goToArticle(slug) {
      this.router.push({ path: `/articles/${slug}` });
    },
  },
};
</script>

<style scoped>
.article-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.article-card:hover {
  transform: scale(1.02);
}
</style>
