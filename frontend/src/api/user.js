import api from './index'

export function updateProfile(formData) {
  return api.put('/api/user/profile', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function getMyProducts(params) {
  return api.get('/api/user/products', { params })
}
