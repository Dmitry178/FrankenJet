import axios, { AxiosResponse } from 'axios';

interface BotSettingsRequest {
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
  data: BotSettingsRequest;
}

class BotSettingsService {
  private readonly baseUrl: string = '';

  async getSettings(): Promise<AxiosResponse['data']> {
    try {
      const response = await axios.get<BotSettingsResponse>(`${this.baseUrl}/bot-settings`);
      return response.data;
    } catch (error) {
      console.error('Error fetching app settings:', error);
      throw error;
    }
  }

  async updateSettings(settings: BotSettingsRequest): Promise<AxiosResponse['data']> {
    try {
      const response = await axios.put<BotSettingsResponse>(
        `${this.baseUrl}/bot-settings`,
        settings
      );
      return response.data;
    } catch (error) {
      console.error('Error updating app settings:', error);
      throw error;
    }
  }
}

export const botSettingsService = new BotSettingsService();
