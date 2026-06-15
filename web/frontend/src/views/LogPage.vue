<template>
  <div class="container mt-4">
    <h1 class="mb-4">Логи пользователей</h1>

    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3 align-items-end">
          <div class="col-md-4">
            <label for="userFilter" class="form-label">Пользователь (ID или имя)</label>
            <input
              id="userFilter"
              v-model="filters.user"
              type="text"
              class="form-control"
              placeholder=""
              @keyup.enter="applyFilters"
            />
          </div>

          <div class="col-md-4">
            <label for="typeFilter" class="form-label">Тип события</label>
            <input
              id="typeFilter"
              v-model="filters.type"
              type="text"
              class="form-control"
              placeholder="Login, Registration, ..."
              @keyup.enter="applyFilters"
            />
          </div>

          <div class="col-md-2">
            <div class="d-flex gap-2">
              <button
                class="btn btn-primary w-100"
                @click="applyFilters"
                :disabled="loading"
              >
                Применить
              </button>
              <button
                class="btn btn-secondary w-100"
                @click="resetFilters"
                :disabled="loading"
              >
                Сбросить
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
     <div>
      <label>
         <input type="checkbox" v-model="nosystem" @change="applyFilters">
         Скрыть системные логи
      </label>
    </div>
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Загрузка...</span>
      </div>
    </div>

    <div v-else-if="error" class="alert alert-danger" role="alert">
      {{ error }}
    </div>

    <div v-else-if="logs.length === 0" class="alert alert-info" role="alert">
      Нет логов по заданным критериям.
    </div>

    <div v-else class="table-responsive">
      <table class="table table-striped table-hover">
        <thead class="table-dark">
          <tr>
            <th>Время</th>
            <th>Пользователь</th>
            <th>Тип</th>
            <th>Сообщение</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(log, idx) in logs" :key="idx">
            <td>{{ formatTimestamp(log.timestamp) }}</td>
            <td>{{ log.user || '–' }}</td>
            <td>{{ log.type }}</td>
            <td>{{ log.message }}</td>
          </tr>
        </tbody>
      </table>
    </div>

  <div v-if="totalPages > 1" class="d-flex justify-content-between align-items-center mt-4">
      <div>
        Показано {{ (currentPage - 1) * perPage + 1 }} – {{ Math.min(currentPage * perPage, total) }} из {{ total }}
      </div>
      <div>
        <button class="btn btn-sm btn-outline-primary me-2" :disabled="currentPage === 1" @click="goToPage(currentPage - 1)">
          &larr; Назад
        </button>
        <span v-for="p in displayedPages" :key="p" class="mx-1">
          <button v-if="p === currentPage" class="btn btn-sm btn-primary">{{ p }}</button>
          <button v-else class="btn btn-sm btn-outline-secondary" @click="goToPage(p)">{{ p }}</button>
        </span>
        <button class="btn btn-sm btn-outline-primary ms-2" :disabled="currentPage === totalPages" @click="goToPage(currentPage + 1)">
          Вперёд &rarr;
        </button>
      </div>
      <div>
        <select v-model="perPage" @change="resetAndFetch" class="form-select form-select-sm w-auto">
          <option :value="20">20 на странице</option>
          <option :value="50">50 на странице</option>
          <option :value="100">100 на странице</option>
        </select>
      </div>
    </div>
  </div>

</template>

<script>
import { ref, onMounted, computed } from 'vue'
import api from '@/services/api'

export default {
  name: 'LogPage',
  setup() {
    const logs = ref([])
    const loading = ref(false)
    const error = ref(null)

    const filters = ref({
      user: '',
      type: ''
    })

    const nosystem = ref(false)

    const currentPage = ref(1)
    const perPage = ref(50)
    const total = ref(0)
    const totalPages = ref(1)

    const fetchLogs = async () => {
      loading.value = true
      error.value = null
      try {
        const params = {
          page: currentPage.value,
          per_page: perPage.value
        }
        if (filters.value.user.trim()) params.user = filters.value.user.trim()
        if (filters.value.type.trim()) params.type = filters.value.type.trim()
        if (nosystem.value) params.nosystem = 'true'

        const response = await api.get('/logs', { params })
        logs.value = response.data.logs || []
        total.value = response.data.total || 0
        totalPages.value = response.data.pages || 1
        currentPage.value = response.data.page || 1
      } catch (err) {
        console.error(err)
        error.value = err.response?.data?.error || 'Ошибка загрузки логов'
        logs.value = []
      } finally {
        loading.value = false
      }
    }

    const applyFilters = () => {
      currentPage.value = 1
      fetchLogs()
    }

    const resetFilters = () => {
      filters.value.user = ''
      filters.value.type = ''
      currentPage.value = 1
      fetchLogs()
    }

    const resetAndFetch = () => {
      currentPage.value = 1
      fetchLogs()
    }

    const goToPage = (page) => {
      if (page < 1 || page > totalPages.value) return
      currentPage.value = page
      fetchLogs()
    }

    const formatTimestamp = (isoString) => {
      if (!isoString) return ''
      const date = new Date(isoString)
      return date.toLocaleString()
    }

    const displayedPages = computed(() => {
      const delta = 2
      let start = currentPage.value - delta
      let end = currentPage.value + delta
      if (start < 1) {
        start = 1
        end = Math.min(totalPages.value, start + 4)
      }
      if (end > totalPages.value) {
        end = totalPages.value
        start = Math.max(1, end - 4)
      }
      const pages = []
      for (let i = start; i <= end; i++) pages.push(i)
      return pages
    })

    onMounted(() => {
      fetchLogs()
    })

    return {
      logs,
      loading,
      error,
      filters,
      nosystem,
      currentPage,
      perPage,
      total,
      totalPages,
      displayedPages,
      resetAndFetch,
      goToPage,
      applyFilters,  
  resetFilters,      
      formatTimestamp,   
  fetchLogs
    }
  }
}
</script>

<style scoped>
.container {
  max-width: 1400px;
}
</style>
