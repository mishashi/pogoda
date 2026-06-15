<template>
  <div class="container mt-4">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            <h5>Вход в систему</h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="login">
              <div class="mb-3">
                <label class="form-label">Имя пользователя или email</label>
                <input 
                  type="text" 
                  class="form-control" 
                  v-model="username"
                  required
                >
              </div>
              <div class="mb-3">
                <label class="form-label">Пароль</label>
                <input 
                  type="password" 
                  class="form-control" 
                  v-model="password"
                  required
                >
              </div>
              <button type="submit" class="btn btn-primary w-100" :disabled="loading">
                {{ loading ? 'Вход...' : 'Войти' }}
              </button>
            </form>
            <br>
            <router-link :to="`/register`" class="btn btn-secondary">
              Зарегистрироваться
            </router-link>
            <div v-if="error" class="alert alert-danger mt-3">
              {{ error }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { authStore } from '@/stores/auth'

export default {
  name: 'LoginView',
  data() {
    return {
      username: '',
      password: '',
      loading: false,
      error: null
    }
  },
  methods: {
    async login() {
      this.loading = true
      this.error = null

      const result = await authStore.login(this.username, this.password)

      if (result.success) {
        location.href = '/'
      } else {
        this.error = result.message
      }

      this.loading = false
    }
  }
}
</script>