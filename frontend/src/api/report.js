import api from './index'

export function createReport(data) {
  return api.post('/api/reports', data)
}

export function checkReported(productId) {
  return api.get(`/api/reports/check/${productId}`)
}
