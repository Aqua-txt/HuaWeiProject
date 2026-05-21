import api from './index'

export function createReport(data) {
  return api.post('/api/reports', data)
}

export function getReports(params) {
  return api.get('/api/reports', { params })
}

export function getReport(reportId) {
  return api.get(`/api/reports/${reportId}`)
}
