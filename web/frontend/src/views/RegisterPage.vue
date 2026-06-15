<template>
  <div class="container mt-4">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            <h5>Регистрация</h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="register">
              <div class="mb-3">
                <label class="form-label">Имя пользователя</label>
                <input 
                  type="text" 
                  class="form-control" 
                  v-model="username"
                  required
                >
              </div>
              <div class="mb-3">
                <label class="form-label">Email</label>
                <input 
                  type="text" 
                  class="form-control" 
                  v-model="email"
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
              <div class="mb-3">
                <input type="checkbox" v-model = "admin">Я админ!
                <div v-if = 'admin'>
                    <div class="mb-3">
                    <label class="form-label">Введи пароль админа</label>
                    <input 
                    type="password" 
                    class="form-control" 
                    v-model="invite"
                    required
                    >
                </div>
              </div>
              </div>
              <button type="submit" class="btn btn-primary w-100" :disabled="loading">
                {{ loading ? 'Регистрация...' : 'Зарегистрироваться' }}
              </button>
            </form>

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
  name: 'RegisterView',
  data() {
    return {
      username: '',
      email: '',
      password: '',
      loading: false,
      error: null,
      admin: false,
      invite: '',
    }
  },
  methods: {
    async register() {
      this.loading = true
      this.error = null

      const result = await authStore.register(this.username, this.email, this.password, this.invite)

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