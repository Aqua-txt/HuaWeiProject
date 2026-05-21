import api from './index'

export function getProducts(params) {
  return api.get('/api/products', { params })
}

export function getProduct(id) {
  return api.get(`/api/products/${id}`)
}

export function createProduct(formData) {
  return api.post('/api/products', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function updateProduct(id, formData) {
  return api.put(`/api/products/${id}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function updateProductStatus(id, status) {
  return api.put(`/api/products/${id}/status`, { status })
}

export function toggleFavorite(id) {
  return api.post(`/api/products/${id}/favorite`)
}

export function getFavorites(params) {
  return api.get('/api/favorites', { params })
}
