import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'
import LoginPage from '../views/LoginPage.vue'
import RegisterPage from '../views/RegisterPage.vue'
import StatPage from '../views/StatPage.vue'
import SubscribePage from '../views/SubscribePage.vue'
import LogPage from '../views/LogPage.vue'

const routes = [
  {path: '/login', component: LoginPage},
  {path: '/', component: HomePage, meta: {requiresAuth: true}},
  {path: '/stat', component: StatPage, meta: {requiresAuth: true}},
  {path: '/subscribes', component: SubscribePage, meta: {requiresAuth: true}},
  {path: '/logs', component: LogPage, meta: {requiresAuth: true, requiresAdmin: true}},
  {path: '/register', component: RegisterPage},
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('authToken')
  const userRole = localStorage.getItem('userRole')

  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.meta.requiresAdmin && userRole === 'USER') {
    next('/') 
  } else {
    next()
  }
})

export default router
