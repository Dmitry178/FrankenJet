<template>
  <v-container>
    <!-- Описание проекта -->
    <v-card>
      <v-card-title class="hidden-md-and-up">Добро пожаловать!</v-card-title>
      <v-card-title class="hidden-sm-and-down">Добро пожаловать в мир авиации!</v-card-title>
      <v-card-text>
        <p class="mb-0 mb-sm-1">
          Этот проект - ваш путеводитель по истории авиации, созданный для всех, кто увлекается крылатыми машинами и героями неба.
          Здесь вы  найдете увлекательные истории о самолетах, вертолетах, дирижаблях и множестве других летательных аппаратов.
          Узнайте о выдающихся конструкторах, легендарных производителях и  странах, которые внесли свой вклад в развитие авиации.
        </p>
      </v-card-text>
    </v-card>

    <!-- Статьи -->
    <v-card v-if="articles.length > 0">
      <v-card-title
        @click="goToArticles"
        style="cursor: pointer;"
      >
        Статьи
      </v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12" sm="12" md="6" lg="4" xl="4" v-for="article in visibleArticles" :key="article.slug">
            <v-card @click="goToArticle(article.slug)" class="article-card">
              <v-img
                v-if="article.image_url"
                :src="article.image_url"
                class="grayscale-image"
                aspect-ratio=16/9
                max-height="200"
                cover
              />
              <v-img
                v-else
                src=""
                cover
                class="airplane-svg-wrapper"
              >
                <AirplaneSVG class="airplane-svg" />
              </v-img>

              <v-card-title>{{ article.title }}</v-card-title>

              <v-card-text class="cards">
                {{ article.summary }}
              </v-card-text>

            </v-card>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Интересные факты -->
    <v-card v-if="processedFacts.length > 0">
      <v-card-title>Интересные факты</v-card-title>
      <v-card-text>
        <ul class="mb-0">
          <li v-for="(fact, index) in processedFacts" :key="index" v-html="fact"></li>
        </ul>
      </v-card-text>
    </v-card>

  </v-container>
</template>

<script>
import axios from 'axios';
import { useRouter } from 'vue-router';
import AirplaneSVG from "@/components/AirplaneSVG.vue";

export default {
  components: {
    AirplaneSVG
  },
  setup() {
    const router = useRouter();
    return { router };
  },
  data() {
    return {
      articles: [], // рандомные статьи
      facts: [], // исходные факты
      processedFacts: [], // обработанные факты (html)
    };
  },
  mounted() {
    this.fetchHomeData();
  },
  computed: {
    visibleArticles() {
      const breakpoint = this.$vuetify.display.name;
      let limit;

      if (breakpoint === 'xs' || breakpoint === 'sm') {
        limit = 1;
      } else if (breakpoint === 'md') {
        limit = 2;
      } else {
        limit = 3; // lg, xl
      }

      return this.articles.slice(0, limit);
    }
  },
  methods: {
    // обработка markdown-ссылок в HTML
    processFacts(factsArray) {
      if (!Array.isArray(factsArray)) {
        return [];
      }

      const linkRegex = /\[([^\[\]]+)\]\(([^)]+)\)/g;

      return factsArray.map(fact => {
        if (typeof fact !== 'string') {
          return fact;
        }
        return fact.replace(linkRegex, '<a href="$2">$1</a>');
      });
    },

    async fetchHomeData() {
      try {
        const response = await axios.get(`/pages/home`);
        if (response.data.status === "ok") {
          this.articles = response.data.data.articles;
          this.facts = response.data.data.facts;
          this.processedFacts = this.processFacts(this.facts);
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

    goToArticles() {
      this.router.push({ name: 'Articles' });
    },
  },
};
</script>

<style scoped>
.article-card {
  display: flex;
  flex-direction: column;
  height: 100%;
  cursor: pointer;
  transition: transform 0.2s;
}

.article-card:hover {
  transform: scale(1.02);
}

.cards.v-card-text{
  padding-bottom: 0.2rem !important;
}

.grayscale-image {
  filter: grayscale(100%);
}

</style>
