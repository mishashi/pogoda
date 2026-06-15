<script>
import { RouterLink, RouterView } from 'vue-router'
import { authStore } from '@/stores/auth'
import { reactive } from 'vue';

export default {
  name: 'App',
  data() {
    return {
      userdata: reactive({
      username: localStorage.getItem('authUser') || '',
      role: localStorage.getItem('userRole') || ''
    }),
      error: null
    }
  },
  created() {
    authStore.init()
    window.addEventListener('storage', (event) => {
      if (event.key === 'authUser') {
          this.userdata.username = event.newValue || ''; 
      }
      if (event.key === 'userRole') {
          this.userdata.role = event.newValue || ''; 
      }
});
  },
  methods: {
    logout() {
      authStore.logout()
      location.href = '/login'
    }, checkerror () {
      if (localStorage.getItem('error')) {
              this.error = localStorage.getItem('error')
              localStorage.removeItem('error')
              return true; 
      }
      return false; 
    }
  }
  
}
</script>

<template>
  <header>
    <nav class="navbar">
      <div class="nav-container">
        <RouterLink class="logo" to="/">
          Анализатор погоды
        </RouterLink>

        <div v-if="userdata.role">
        <div class="nav-links">
          <RouterLink to="/">Главная</RouterLink>
          <RouterLink to="/stat">📊 Статистика</RouterLink>
          <RouterLink to="/subscribes">🔔 Подписки</RouterLink>
          <RouterLink v-if="userdata.role !== 'USER'" to="/logs">📜 Логи</RouterLink>
        </div>
        </div>
        <div class="user-info">
          <span class="user-badge">Вы: {{ userdata.username }} | Ваша роль: {{ userdata.role }}</span>
          <button class="logout-btn" @click="logout">Выйти</button>
        </div>
      </div>
    </nav>

    <div v-if="error" class="error-message">
      {{ error }}
      <button class="close-error" @click="error = null">✖</button>
    </div>
  </header>

  <main class="main-content">
    <RouterView />
  </main>
</template>


<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.navbar {
  background: linear-gradient(135deg, #a5bbe4 0%, #a5bbe4 100%);
  padding: 0.8rem 2rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.nav-container {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.logo {
  font-size: 1.6rem;
  font-weight: bold;
  color: white;
  text-decoration: none;
  letter-spacing: 1px;
  transition: transform 0.2s;
}

.logo:hover {
  transform: scale(1.02);
}

.nav-links {
  display: flex;
  gap: 1.8rem;
  align-items: center;
  flex-wrap: wrap;
}

.nav-links a {
  color: #f0f0f0;
  text-decoration: none;
  font-weight: 500;
  padding: 0.4rem 0;
  transition: all 0.2s;
  border-bottom: 2px solid transparent;
}

.nav-links a:hover {
  color: #ffd966;
  transform: translateY(-2px);
}

.nav-links a.router-link-active {
  border-bottom-color: #ffc107;
  color: #ffc107;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-badge {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(4px);
  padding: 0.4rem 1rem;
  border-radius: 40px;
  color: white;
  font-size: 0.9rem;
  font-weight: 500;
}

.logout-btn {
  background: transparent;
  border: 2px solid rgba(255, 255, 255, 0.6);
  color: white;
  padding: 0.4rem 1rem;
  border-radius: 40px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.logout-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: white;
  transform: scale(1.02);
}

.error-message {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background: #dc3545;
  color: white;
  padding: 0.8rem 1.2rem;
  border-radius: 12px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 500;
  z-index: 1000;
  backdrop-filter: blur(8px);
  animation: slideIn 0.3s ease;
}

.close-error {
  background: none;
  border: none;
  color: white;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0 4px;
  opacity: 0.8;
  transition: opacity 0.2s;
}

.close-error:hover {
  opacity: 1;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.main-content {
  max-width: 1400px;
  margin: 2rem auto;
  padding: 0 1.5rem;
}

/* Адаптив для мобильных */
@media (max-width: 850px) {
  .nav-container {
    flex-direction: column;
    align-items: stretch;
  }
  .nav-links {
    justify-content: center;
  }
  .user-info {
    justify-content: center;
  }
}
</style>
