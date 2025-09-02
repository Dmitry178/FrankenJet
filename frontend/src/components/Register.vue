<template>
  <div class="container">
    <div class="auth-form">
      <h2>Регистрация</h2>

      <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>

      <div class="form-inputs">
        <input type="email" placeholder="Email" class="input-field" v-model="email" autocomplete="email" />
        <input type="password" placeholder="Пароль" class="input-field" v-model="password" autocomplete="new-password" />
      </div>

      <p>На указанный email придет ссылка подтверждения</p>

      <button class="enter-button" @click="register">Зарегистрироваться</button>
    </div>
  </div>
</template>

<script>

import { ref } from 'vue';
import { useRouter } from 'vue-router';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export default {
  setup() {
    const email = ref('');
    const password = ref('');
    const errorMessage = ref('');
    const router = useRouter();

    const register = async () => {
      if (!email.value) {
        errorMessage.value = 'Введите email';
        return;
      }
      if (!password.value) {
        errorMessage.value = 'Введите пароль';
        return;
      }

      errorMessage.value = '';

      try {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            email: email.value,
            password: password.value
          })
        });

        if (response.ok) {
          alert('Регистрация прошла успешно, подтвердите email, перейдя по ссылке в письме');
          await router.push('/login');
        } else {
          const errorData = await response.json();
          errorMessage.value = errorData.message || 'Ошибка при регистрации';
          console.error('Ошибка при регистрации:', errorData);
        }
      } catch (error) {
        errorMessage.value = 'Произошла ошибка при регистрации';
        console.error('Ошибка при запросе:', error);
      }
    };

    return {
      email,
      password,
      errorMessage,
      register,
      router
    };
  }
};
</script>

<style scoped>

.container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: #f7f7f7;
  text-align: center;
}

.auth-form {
  background-color: #fff;
  border-radius: 12px;
  padding: 40px 30px 45px 30px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  width: 300px;
}

h2 {
  margin-top: 0;
  margin-bottom: 20px;
  font-family: sans-serif;
  color: #333;
}

.button {
  display: flex;
  align-items: center;
  gap: 10px;
  background-color: #ffffff;
  color: #555;
  border: 1px solid #ddd;
  border-radius: 10px;
  padding: 8px 25px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.button:hover {
  background-color: #f7f7f7;
}

.form-inputs {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
}

.input-field {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 16px;
}

.enter-button {
  background-color: #4CAF50;
  color: white;
  padding: 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s ease;
}

.enter-button:hover {
  background-color: #367c39;
}

.button-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  background-color: #ffffff;
  color: #555;
  border: 1px solid #ddd;
  border-radius: 10px;
  padding: 8px 25px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  width: 100%;
  height: 48px;
}

.error-message {
  color: red;
  margin-bottom: 10px;
}
</style>
