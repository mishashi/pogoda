import { reactive } from 'vue'
import api from '@/services/api'

export const authStore = reactive({
  user: null,
  token: null,
  isAuthenticated: false,
  role: null,

  init() {
    const savedToken = localStorage.getItem('authToken')
    const savedUser = localStorage.getItem('authUser')

    if (savedToken && savedUser) {
      this.token = savedToken
      this.user = JSON.parse(savedUser)
      this.isAuthenticated = true
      api.defaults.headers.common['Authorization'] = `Bearer ${savedToken}`
    }
  },

  async login(username, password) {
    try {
      const response = await api.post('/login', { 'name': username, 'password': password })
      const {token, role} = response.data

      this.token = token
      this.user = username
      this.role = role
      this.isAuthenticated = true

      localStorage.setItem('authToken', token)
      localStorage.setItem('userRole', this.role)
      localStorage.setItem('authUser', JSON.stringify(this.user))
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      return { success: true }
    } catch (error) {
      return { success: false, message: 'Неверный логин или пароль' }
    }
  },
  
  async register(username, email, password, invite) {
    try {
      const response = await api.post('/reg', { 'name': username, 'email': email, 'password': password, 'invite': invite})
      console.log('got')
      const {token, role} = response.data

      this.token = token
      this.user = username
      this.role = role
      this.isAuthenticated = true

      localStorage.setItem('authToken', token)
      localStorage.setItem('userRole', this.role)
      localStorage.setItem('authUser', JSON.stringify(this.user))
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      return { success: true }
    } catch (error) {
      let errorMessage = 'Unknown error'
      if (error.response) {
        const data = error.response.data
        if (data && data.error) {
          errorMessage = data.error
        } else if (data && data.message) {
          errorMessage = data.message
        } else {
          errorMessage = `Server error: ${error.response.status}`
        }
      } else if (error.request) {
        errorMessage = 'No response from server'
      } else {
        errorMessage = error.message
      }
      return { success: false, message: errorMessage }
    }
  },

  logout() {
    this.user = null
    this.token = null
    this.isAuthenticated = false

    localStorage.removeItem('authToken')
    localStorage.removeItem('authUser')
    localStorage.removeItem('userRole')
    delete api.defaults.headers.common['Authorization']
    console.log('User logged out successfully');
  }
})