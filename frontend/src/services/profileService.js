import axios from 'axios';

const BASE_URL = '/users';

export const profileService = {
  // Получить профиль
  getProfile: async () => {
    const response = await axios.get(`${BASE_URL}/profile`);
    return response.data;
  },

  // Обновить профиль
  updateProfile: async (data) => {
    const response = await axios.put(`${BASE_URL}/profile`, data);
    return response.data;
  }
};
