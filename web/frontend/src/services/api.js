import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  //baseURL: 'http://127.0.0.1:5000/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Автоматическая подстановка токена
api.interceptors.request.use(config => {
  const token = localStorage.getItem('authToken')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Обработка ошибок авторизации
api.interceptors.response.use(
  response => response,
  error => {
    if ((error.response?.status === 434) || (error.response?.status === 435)) {
      localStorage.removeItem('authToken')
      window.location.href = '/login'
    }
    if (error.response?.status === 436) {
      window.location.href = '/'
      alert('Forbidden')
    }
    return Promise.reject(error)
  }
)

export default api
