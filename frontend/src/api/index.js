import axios from 'axios'
import { API_BASE_URL } from '../utils/url'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
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
    const msg =
      err.code === 'ERR_NETWORK'
        ? '无法连接后端服务，请先启动 backend/app.py'
        : err.response?.data?.message || '网络异常，请稍后重试'
    ElMessage.error(msg)
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default api
