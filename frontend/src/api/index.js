import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: 'http://127.0.0.1:5000',
  timeout: 10000,
})

api.interceptors.request.use((config) => {
  const isAdminRequest = config.url?.startsWith('/admin')
  const token = isAdminRequest 
    ? localStorage.getItem('admin_token') 
    : localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => {
    if (res.data?.message && res.config.method !== 'get') {
      ElMessage.success(res.data.message)
    }
    return res.data
  },
  (err) => {
    const msg = err.response?.data?.message || '网络异常，请稍后重试'
    ElMessage.error(msg)
    if (err.response?.status === 401) {
      const isAdminRequest = err.config?.url?.startsWith('/admin')
      if (isAdminRequest) {
        localStorage.removeItem('admin_token')
        localStorage.removeItem('admin_user')
        if (window.location.pathname !== '/admin/login') {
          window.location.href = '/admin/login'
        }
      } else {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        window.location.href = '/login'
      }
    }
    return Promise.reject(err)
  }
)

export default api
