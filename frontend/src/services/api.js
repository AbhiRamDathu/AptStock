import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: BASE_URL,
})

export const uploadSales = (formData) =>
  api.post('/upload/sales', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })

export const listSKUs = () =>
  api.get('/skus')

export const getForecast = (skus, store) =>
  api.post('/forecast/multi', { skus, store })

export const getHistorical = (skus, store, from, to) =>
  api.post('/historical', { skus, store, from, to })

export default api
