import axios from 'axios';

// интерфейсы для данных статьи
interface ArticleData {
  id: number;
  slug: string;
  title: string;
  meta_title?: string;
  meta_description?: string;
  seo_keywords?: string;
  content: string;
  published_at?: string;
  created_at?: string;
  is_archived?: boolean;
  sources?: any[];
}

interface AircraftData {
  id: number;
  name: string;
  original_name?: string;
  image_url?: string;
  image_description?: string;
  // TODO: добавить другие поля
}

interface TagData {
  id: number;
  name: string;
  slug: string;
}

interface ArticleResponse {
  status: string;
  data: {
    article: ArticleData;
    aircraft?: AircraftData;
    tags?: TagData[];
  };
}

interface ArticleDetails {
  article: ArticleData;
  aircraft?: AircraftData;
  tags?: TagData[];
}

class ArticleService {
  async fetchArticle(slug: string): Promise<ArticleDetails | null> {
    try {
      const response = await axios.get<ArticleResponse>(`/articles/${slug}`);

      if (response.data.status === "ok") {
        return response.data.data;
      } else {
        console.error('Ошибка при получении данных статьи:', response.data);
        return null;
      }
    } catch (error) {
      console.error('Ошибка при загрузке данных статьи:', error);
      throw error;
    }
  }
}

export const articleService = new ArticleService();
