import axios from 'axios';

interface Article {
  id: number;
  slug: string;
  title: string;
  summary: string;
  image_url: string;
}

interface ArticlesResponse {
  status: string;
  data: Article[];
}

interface TagsResponse {
  status: string;
  data: {
    tags: Record<string, string[]>;
  };
}

export interface ArticleItem {
  id: number;
  slug: string;
  title: string;
  summary: string;
  image_url: string;
}

class ArticlesService {
  async fetchTags(): Promise<Record<string, string[]>> {
    try {
      const response = await axios.get<TagsResponse>('/pages/articles');
      if (response.data.status === 'ok') {
        return response.data.data.tags;
      } else {
        throw new Error('Ошибка при получении тегов');
      }
    } catch (error) {
      console.error('Ошибка при загрузке тегов:', error);
      throw error;
    }
  }

  async fetchArticles(tags: string[], page: number = 1): Promise<ArticleItem[]> {
    try {
      const tagsParam = tags.join(',');
      const response = await axios.get<ArticlesResponse>(
        `/articles/list?tags=${encodeURIComponent(tagsParam)}&page=${page}`
      );

      if (response.data.status === 'ok') {
        return response.data.data;
      } else {
        throw new Error('Ошибка при загрузке статей');
      }
    } catch (error) {
      console.error('Fetch articles error:', error);
      throw new Error('Ошибка при выполнении запроса');
    }
  }
}

export const articlesService = new ArticlesService();
