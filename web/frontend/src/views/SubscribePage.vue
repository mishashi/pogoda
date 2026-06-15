<template>
  <div class="container mt-4">
    <div class="row justify-content-center">
      <div class="col-md-11">
        <!-- Карточка подписок -->
        <div class="card mb-4">
          <div class="card-header">
            <h5>Мои подписки на города</h5>
          </div>
          <div class="card-body">
            <div v-if="loading" class="text-center">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Загрузка...</span>
              </div>
            </div>
            <div v-else-if="error" class="alert alert-danger">
              {{ error }}
            </div>
            <div v-else>
              <div v-if="subscriptions.length === 0" class="text-muted">
                Вы пока не подписаны ни на один город.
              </div>
              <div v-else class="row">
                <div class="col-md-6 mb-3" v-for="city in subscriptions" :key="city">
                  <div class="card h-100">
                    <div class="card-body d-flex justify-content-between align-items-center">
                      <span>{{ city }}</span>
                      <button 
                        class="btn btn-sm btn-outline-danger" 
                        @click="unsubscribe(city)"
                        :disabled="actionLoading === city"
                      >
                        {{ actionLoading === city ? '...' : 'Отписаться' }}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <h5>Подписаться на новый город</h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="subscribe">
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label class="form-label">Город</label>
                    <select class="form-select" v-model="selectedCity" required>
                    <option disabled value="">Выберите город</option>
                    <option v-for="city in availableCities" :key="city" :value="city">
                        {{ city }}
                    </option>
                    </select>
                </div>
                <div class="col-md-6 mb-3">
                    <label class="form-label">Вариант подписки</label>
                    <select class="form-select" v-model="subscriptionOption">
                    <option value="daily8">Каждый день в 8:50</option>
                    </select>
                </div>
            </div>
              <button type="submit" class="btn btn-primary w-100" :disabled="actionLoading === 'subscribe'">
                {{ actionLoading === 'subscribe' ? 'Подписка...' : 'Подписаться' }}
              </button>
            </form>
            <div v-if="subscribeError" class="alert alert-danger mt-3">
              {{ subscribeError }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'

export default {
  name: 'SubscriptionsView',
  data() {
    return {
      subscriptions: [],
      allCities: [],       
      selectedCity: '',   
      subscriptionOption: 'daily8', 
      loading: true,     
      actionLoading: null,   
      error: null,          
      subscribeError: null   
    }
  },
  computed: {
    availableCities() {
      return this.allCities.filter(city => !this.subscriptions.includes(city))
    }
  },
  mounted() {
    this.fetchData()
  },
  methods: {
    async fetchData() {
      this.loading = true
      this.error = null
      try {
        const citiesResponse = await api.get('/cities')
        const citiesData = citiesResponse.data
        this.allCities = Array.isArray(citiesData) ? citiesData : (citiesData.cities || [])

        const subsResponse = await api.get('/subscribe')
        this.subscriptions = subsResponse.data.subscriptions || []
      } catch (err) {
        this.error = 'Ошибка загрузки данных: ' + this.getErrorMessage(err)
      } finally {
        this.loading = false
      }
    },

    async subscribe() {
      if (!this.selectedCity) {
        this.subscribeError = 'Выберите город'
        return
      }
      this.subscribeError = null
      this.actionLoading = 'subscribe'

      try {
        const payload = {
          city: this.selectedCity
          // option: this.subscriptionOption 
        }
        const response = await api.post('/subscribe', payload)
        this.subscriptions = response.data.subscriptions || []
        this.selectedCity = '' 
      } catch (err) {
        this.subscribeError = this.getErrorMessage(err)
      } finally {
        this.actionLoading = null
      }
    },

    async unsubscribe(city) {
      if (!city) return
      this.actionLoading = city

      try {
        const response = await api.delete('/subscribe', { data: { city: city } })
        this.subscriptions = response.data.subscriptions || []
      } catch (err) {
        this.error = this.getErrorMessage(err)
        setTimeout(() => { this.error = null }, 3000)
      } finally {
        this.actionLoading = null
      }
    },

    getErrorMessage(err) {
      if (err.response?.data?.error) {
        return err.response.data.error
      }
      if (err.message) {
        return err.message
      }
      return 'Неизвестная ошибка'
    }
  }
}
</script>

<style scoped>
.card-header h5 {
  margin: 0;
}
</style>
