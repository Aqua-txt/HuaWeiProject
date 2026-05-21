import axios from 'axios'
import { API_BASE_URL } from '../utils/url'
import { ElMessage } from 'element-plus'

const adminApi = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
})

adminApi.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

adminApi.interceptors.response.use(
  (res) => {
    if (res.data?.message && res.config.method !== 'get') {
      ElMessage.success(res.data.message)
    }
    return res.data
  },
  (err) => {
    const msg =
      err.code === 'ERR_NETWORK'
        ? '无法连接后端服务，请先启动 backend/app.py'
        : err.response?.data?.message || '网络异常，请稍后重试'
    ElMessage.error(msg)
    if (err.response?.status === 401) {
      localStorage.removeItem('admin_token')
      localStorage.removeItem('admin_user')
      window.location.href = '/admin/login'
    }
    return Promise.reject(err)
  }
)

export function adminLogin(data) {
  return adminApi.post('/api/admin/login', data)
}

export function initAdmin(data) {
  return adminApi.post('/api/admin/init', data)
}

export function getAdminReports(params) {
  return adminApi.get('/api/admin/reports', { params })
}

export function getAdminReport(reportId) {
  return adminApi.get(`/api/admin/reports/${reportId}`)
}

export function handleReport(reportId, data) {
  return adminApi.post(`/api/admin/reports/${reportId}/handle`, data)
}

export function getAdminProducts(params) {
  return adminApi.get('/api/admin/products', { params })
}

export function updateAdminProductStatus(productId, data) {
  return adminApi.put(`/api/admin/products/${productId}/status`, data)
}

export function getAdminUsers(params) {
  return adminApi.get('/api/admin/users', { params })
}

export function toggleUserBan(userId, data) {
  return adminApi.put(`/api/admin/users/${userId}/ban`, data)
}

export function getDashboard() {
  return adminApi.get('/api/admin/dashboard')
}
