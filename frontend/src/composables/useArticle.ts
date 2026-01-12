import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import { articleService } from '@/services/articleService';

export interface TocItem {
  id: string;
  text: string;
  level: number;
}

export interface ImageCaption {
  title: string;
  description: string | null;
  alt: string;
}

export function useArticle() {
  const route = useRoute();
  const router = useRouter();
  const slug = route.params.slug as string;

  const article = ref<any>(null);
  const error = ref(false);
  const toc = ref<TocItem[]>([]);
  const activeTocItem = ref<string | null>(null);
  let observer: IntersectionObserver | null = null;

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
    return article.value.aircraft?.image_url || '';
  });

  const articleImageIsDefault = computed(() => {
    return !article.value?.aircraft?.image_url;
  });

  const imageDialog = ref(false);

  const openImageDialog = () => {
    imageDialog.value = true;
  };

  const imageCaption = computed<ImageCaption>(() => {
    const { name, original_name, image_description } = article.value?.aircraft || {};
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

  const setTagAndNavigate = (tag: any) => {
    localStorage.setItem('articles_selected_tags', JSON.stringify([tag]));
    localStorage.setItem('articles_current_page', '1');
    router.push('/articles');
  };

  const renderedContent = computed(() => {
    if (!article.value?.article?.content) return '';

    const html = marked(article.value.article.content);
    const cleanHtml = DOMPurify.sanitize(html, {
      USE_PROFILES: { html: true },
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
        text: el.textContent?.trim() || '',
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

  const scrollToSection = (id: string) => {
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

        let scrollEndHandler = () => {
          activeTocItem.value = id;
          window.removeEventListener('scrollend', scrollEndHandler);
        };

        window.addEventListener('scrollend', scrollEndHandler);
      }
    }
  };

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

  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
    activeTocItem.value = 'top';
  };

  onMounted(async () => {
    try {
      const articleData = await articleService.fetchArticle(slug);
      if (articleData) {
        article.value = articleData;
      } else {
        error.value = true;
      }
    } catch (e) {
      console.error('Ошибка при загрузке данных статьи:', e);
      error.value = true;
    }

    await nextTick();
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
}
