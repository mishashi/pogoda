<template>
  <div class="container mt-4">
    <div class="row justify-content-center">
      <div class="col-md-10">
        <div class="card">
          <div class="card-header">
            <h5>Статистика погоды</h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="loadGraph">
              <div class="row">
                <div class="col-md-5 mb-3">
                <label class="form-label">Тип графика</label>
                <select class="form-select" v-model="selectedType" required>
                  <option disabled value="">Выберите тип</option>
                  <option value="maxtemp-boxplot">Maxtemp Boxplot</option>
                  <option value="maxtemp-rmse">Maxtemp RMSE</option>
                </select>
              </div>

              <div class="col-md-6 mb-3">
                <label class="form-label">Город</label>
                <select class="form-select" v-model="selectedCity" required>
                  <option disabled value="">Выберите город</option>
                  <option v-for="city in cities" :key="city" :value="city">
                    {{ city }}
                  </option>
                </select>
              </div>
            </div>
              <button type="submit" class="btn btn-primary w-100" :disabled="loading">
                {{ loading ? 'Загрузка...' : 'Показать график' }}
              </button>
            </form>

            <div v-if="error" class="alert alert-danger mt-3">
              {{ error }}
            </div>

            <div v-if="graphUrl" class="mt-4 text-center">
              <img :src="graphUrl" alt="График статистики" class="img-fluid">
            </div>
            <div> Maxtemp RMSE - зависмость среднеквадратичной ошибки прогноза температуры от срока предсказаний
            <br> Maxtemp Boxplot - распределние ошибок предсказания температуры</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'

export default {
  name: 'StatView',
  data() {
    return {
      cities: [],      
      selectedType: '',
      selectedCity: '',
      loading: false,
      error: null,
      graphUrl: null
    }
  },
  mounted() {
    this.fetchCities()
  },
  methods: {

    async fetchCities() {
      try {
        const response = await api.get('/cities')
        const data = response.data
        this.cities = Array.isArray(data) ? data : (data.cities || [])
        if (this.cities.length === 0) {
          this.error = 'Список городов пуст'
        }
	this.cities.push('all')
      } catch (err) {
        this.error = 'Ошибка загрузки городов: ' + this.getErrorMessage(err)
      }
    },

    async loadGraph() {
      if (!this.selectedType || !this.selectedCity) {
        this.error = 'Выберите тип графика и город'
        return
      }

      this.loading = true
      this.error = null
      this.graphUrl = null

      try {
        const response = await api.get('/stat', {
          params: {
            type: this.selectedType,
            city: this.selectedCity
          }
        })

        const data = response.data
        if (!data.graph_url) {
          throw new Error('Сервер не вернул URL графика')
        }
        const unique = Date.now()
        this.graphUrl = `/graphs/${data.graph_url}?nocache=${unique}`
      } catch (err) {
        this.error = this.getErrorMessage(err)
      } finally {
        this.loading = false
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
</style>
