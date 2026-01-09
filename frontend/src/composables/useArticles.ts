import { ref, onMounted } from 'vue';
import { articlesService, type ArticleItem } from '@/services/articlesService';

export const useArticles = () => {
  const allTags = ref<Record<string, string[]>>({});
  const selectedTags = ref<string[]>([]);
  const articles = ref<ArticleItem[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const currentPage = ref(1);
  const totalPages = ref(1);

  // константы для ключей localStorage
  const STORAGE_KEYS = {
    SELECTED_TAGS: 'articles_selected_tags',
    CURRENT_PAGE: 'articles_current_page'
  };

  // функции для склонения
  const pluralize = (n: number, forms: [string, string, string]): string => {
    n = Math.abs(parseInt(n.toString())) || 0;
    const mod100 = n % 100;
    const mod10 = mod100 % 10;

    if (mod100 >= 11 && mod100 <= 20) {
      return forms[2];
    }

    if (mod10 === 1) {
      return forms[0];
    }

    if (mod10 >= 2 && mod10 <= 4) {
      return forms[1];
    }

    return forms[2];
  };

  // сохранение тегов в localStorage
  const saveSelectedTagsToStorage = (): void => {
    try {
      localStorage.setItem(STORAGE_KEYS.SELECTED_TAGS, JSON.stringify(selectedTags.value));
    } catch (e) {
      console.warn('Ошибка сохранения выбранных тегов в localStorage:', e);
    }
  };

  // восстановление тегов из localStorage
  const loadSelectedTagsFromStorage = (): void => {
    try {
      const stored = localStorage.getItem(STORAGE_KEYS.SELECTED_TAGS);
      if (stored) {
        const parsed = JSON.parse(stored);
        if (Array.isArray(parsed)) {
          selectedTags.value = parsed;
        }
      }
    } catch (e) {
      console.warn('Ошибка загрузки выбранных тегов из localStorage:', e);
      selectedTags.value = [];
    }
  };

  // сохранение номера страницы в localStorage
  const saveCurrentPageToStorage = (): void => {
    try {
      localStorage.setItem(STORAGE_KEYS.CURRENT_PAGE, currentPage.value.toString());
    } catch (e) {
      console.warn('Ошибка сохранения номера текущей страницы в localStorage:', e);
    }
  };

  // восстановление номера страницы из localStorage
  const loadCurrentPageFromStorage = (): void => {
    try {
      const stored = localStorage.getItem(STORAGE_KEYS.CURRENT_PAGE);
      if (stored) {
        const parsed = parseInt(stored, 10);
        if (!isNaN(parsed) && parsed > 0) {
          currentPage.value = parsed;
        }
      }
    } catch (e) {
      console.warn('Ошибка чтение номера текущей страницы из localStorage:', e);
      currentPage.value = 1;
    }
  };

  const fetchTags = async (): Promise<void> => {
    try {
      allTags.value = await articlesService.fetchTags();
    } catch (error) {
      console.error('Ошибка при загрузке тегов:', error);
    }
  };

  const fetchArticles = async (): Promise<void> => {
    if (selectedTags.value.length === 0) {
      articles.value = [];
      return;
    }

    loading.value = true;
    error.value = null;

    try {
      articles.value = await articlesService.fetchArticles(selectedTags.value, currentPage.value);
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Ошибка при выполнении запроса';
    } finally {
      loading.value = false;
    }
  };

  const toggleTag = async (tag: string): Promise<void> => {
    const index = selectedTags.value.indexOf(tag);
    if (index > -1) {
      selectedTags.value.splice(index, 1);
    } else {
      selectedTags.value.push(tag);
    }
    currentPage.value = 1; // сброс на первую страницу при изменении тегов

    saveSelectedTagsToStorage();
    saveCurrentPageToStorage();

    // сохраняем текущую позицию прокрутки
    const scrollPosition = window.scrollY;

    // вызываем fetchArticles асинхронно, чтобы не блокировать UI
    await fetchArticles();

    // восстанавливаем позицию прокрутки
    window.scrollTo({ top: scrollPosition, behavior: 'auto' }); // 'auto' для мгновенного возврата
  };

  const changePage = async (page: number): Promise<void> => {
    currentPage.value = page;
    // для смены страницы оставляем прокрутку к началу
    window.scrollTo({ top: 0, behavior: 'smooth' });
    await fetchArticles();
  };

  const initialize = async (): Promise<void> => {
    // загрузка тегов
    await fetchTags();
    // восстановление состояния из localStorage
    loadSelectedTagsFromStorage();
    loadCurrentPageFromStorage();
    // загрузка статей
    if (selectedTags.value.length > 0) {
      await fetchArticles();
    }
  };

  return {
    allTags,
    selectedTags,
    articles,
    loading,
    error,
    currentPage,
    totalPages,
    pluralize,
    fetchTags,
    fetchArticles,
    toggleTag,
    changePage,
    initialize
  };
};
