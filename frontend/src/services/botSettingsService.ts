import axios, { AxiosResponse } from 'axios';

interface BotSettingsRequest {
  enabled: boolean;
  model: string;
  scope: string;
  feedback: string;
  user_daily_tokens: number;
  total_daily_tokens: number;
}

interface PromptsSettingsRequest {
  system_prompt: string;
  rag_prompt: string;
}

interface FullBotSettingsRequest {
  enabled: boolean;
  model: string;
  scope: string;
  system_prompt: string;
  rag_prompt: string;
  feedback: string;
  user_daily_tokens: number;
  total_daily_tokens: number;
}

interface BotSettingsResponse {
  status: string;
  data: FullBotSettingsRequest;
}

class BotSettingsService {
  private readonly baseUrl: string = '';

  async getSettings(): Promise<AxiosResponse['data']> {
    try {
      const response = await axios.get<BotSettingsResponse>(`${this.baseUrl}/bot-settings`);
      return response.data;
    } catch (error) {
      console.error('Ошибка получения настроек:', error);
      throw error;
    }
  }

  async updateBotSettings(settings: BotSettingsRequest): Promise<AxiosResponse['data']> {
    try {
      const response = await axios.patch<BotSettingsResponse>(
        `${this.baseUrl}/bot-settings`,
        settings
      );
      return response.data;
    } catch (error) {
      console.error('Ошибка обновления настроек бота:', error);
      throw error;
    }
  }

  async updatePromptsSettings(settings: PromptsSettingsRequest): Promise<AxiosResponse['data']> {
    try {
      const response = await axios.patch<BotSettingsResponse>(
        `${this.baseUrl}/bot-settings`,
        settings
      );
      return response.data;
    } catch (error) {
      console.error('Ошибка обновления промптов:', error);
      throw error;
    }
  }

  async updateSettings(settings: Partial<FullBotSettingsRequest>): Promise<AxiosResponse['data']> {
    try {
      const response = await axios.patch<BotSettingsResponse>(
        `${this.baseUrl}/bot-settings`,
        settings
      );
      return response.data;
    } catch (error) {
      console.error('Ошибка обновления настроек:', error);
      throw error;
    }
  }
}

export const botSettingsService = new BotSettingsService();
