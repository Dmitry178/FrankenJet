<template>
  <div class="container">
    <h2>User info:</h2>
    <div v-if="userInfo">
      <p>ID: {{ userInfo.id }}</p>
      <p>Email: {{ userInfo.email }}</p>
    </div>
    <p v-else>Загрузка информации о пользователе...</p>
    <button class="button" @click="logout">Выйти</button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      userInfo: null,
    };
  },
  mounted() {
    this.fetchUserInfo();
  },
  methods: {
    async fetchUserInfo() {
      try {
        const response = await this.$axios.get('http://localhost:8111/auth/info');

        if (response.status === 200 && response.data.status === 'ok') {
          this.userInfo = response.data.data;
        } else {
          console.error('Ошибка получения информации о пользователе:', response.status, response.data);
        }
      } catch (error) {
        console.error('Ошибка при запросе информации о пользователе:', error);
      }
    },
    async logout() {
      try {
        const response = await this.$axios.post('http://localhost:8111/auth/logout');

        if (response.status === 200) {
          window.location.href = '/login';
        } else {
          console.error('Ошибка выхода из приложения:', response.status);
        }
      } catch (error) {
        console.error('Ошибка при запросе:', error);
      }
    }
  }
}
</script>

<style scoped>
.container {
  display: flex;
  flex-direction: column;
  padding: 30px;
  height: 100vh;
  background: #f7f7f7;
}

h2 {
  margin-top: 0;
  margin-bottom: 20px;
  font-family: sans-serif;
  color: #333;
}

.button {
  background-color: #4CAF50;
  color: white;
  padding: 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  width: 150px;
  transition: background-color 0.3s ease;
}

.button:hover {
  background-color: #367c39;
}

</style>
