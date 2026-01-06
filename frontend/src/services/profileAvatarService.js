import axios from 'axios';

const BASE_URL = '/users';

export const profileAvatarService = {
  // Загрузить аватар
  uploadAvatar: async (file) => {
    const formData = new FormData();
    formData.append('avatar', file);
    const response = await axios.post(`${BASE_URL}/avatar`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },

  // Удалить аватар
  deleteAvatar: async () => {
    const response = await axios.delete(`${BASE_URL}/avatar`);
    return response.data;
  }
};
