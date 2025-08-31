<template>
  <div class="container">
    <div class="auth-form">
      <h2>Аутентификация</h2>

      <div class="form-inputs">
        <input type="email" placeholder="Email" class="input-field" v-model="email"/>
        <input type="password" placeholder="Пароль" class="input-field" v-model="password"/>
        <button class="enter-button" @click="login">Войти</button>
      </div>

      <div class="button-container">
        <button class="button google-button" @click="loginWithGoogle">
          <img src="../assets/google.webp" alt="" width="32"/>
          Войти через Google
        </button>
        <button class="button vk-button" @click="loginWithVK">
          <img src="../assets/vk.jpg" alt="" width="20"/>
          Войти через VK
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      email: '',
      password: ''
    };
  },
  methods: {
    loginWithGoogle() {
      window.location.href = 'http://localhost:8111/oauth/google';
    },
    loginWithVK() {
      window.location.href = 'http://localhost:8111/oauth/vk';
    },
    async login() {
      try {
        const response = await this.$axios.post('http://localhost:8111/auth/login', {
          email: this.email,
          password: this.password
        });

        if (response.status === 200) {
          window.location.href = '/';
        } else {
          console.error('Ошибка аутентификации:', response.status);
          alert('Неверный email или пароль.');
        }
      } catch (error) {
        console.error('Ошибка при запросе:', error);
        alert('Произошла ошибка при аутентификации.');
      }
    }
  }
}
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
  //box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
  //box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: all 0.2s ease;
  width: 100%;
  height: 48px;
}

.button:hover {
  //box-shadow: 0 4px 5px rgba(0,0,0,0.2);
}

</style>
