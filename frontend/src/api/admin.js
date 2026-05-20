import api from './index'

export function adminLogin(data) {
  return api.post('/admin/login', data)
}

export function getAdminDashboard() {
  return api.get('/admin/dashboard')
}

export function getAdminReports(params) {
  return api.get('/admin/reports', { params })
}

export function handleReport(id, data) {
  return api.post(`/admin/reports/${id}/handle`, data)
}

export function getAdminProducts(params) {
  return api.get('/admin/products', { params })
}

export function adminToggleProduct(id) {
  return api.post(`/admin/products/${id}/toggle`)
}

export function getAdminUsers(params) {
  return api.get('/admin/users', { params })
}

export function adminToggleUser(id) {
  return api.post(`/admin/users/${id}/toggle`)
}
