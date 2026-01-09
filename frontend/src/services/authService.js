import axios from 'axios';
import Cookies from 'js-cookie';
import { useAuthStore } from '@/stores/auth';

export const loginWithEmailAndPassword = async (email, password) => {
  const response = await axios.post(`/auth/login`, {
    email,
    password
  });

  if (response.status === 200) {
    const { access_token, refresh_token } = response.data.data.tokens;
    const userData = response.data.data.user;
    const roles = response.data.data.roles;

    const authStore = useAuthStore();
    authStore.setAccessToken(access_token);
    authStore.setUser({
      email: userData.email,
      fullName: userData.full_name,
      firstName: userData.first_name,
      lastName: userData.last_name,
      picture: userData.picture,
    });
    authStore.setRoles(roles);

    Cookies.set('refresh_token', refresh_token, {
      sameSite: 'Strict',
      path: '/'
    });

    return { success: true };
  } else {
    throw new Error('Invalid credentials');
  }
};

export const loginWithGoogle = () => {
  window.location.href = `/oauth/google`;
};

export const loginWithVK = () => {
  window.location.href = `/oauth/vk`;
};
