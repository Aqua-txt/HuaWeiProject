import api from './index'

export function getWanteds(params) {
  return api.get('/api/wanteds', { params })
}

export function getWantedById(id) {
  return api.get(`/api/wanteds/${id}`)
}

export function createWanted(data) {
  return api.post('/api/wanteds', data)
}

export function updateWanted(id, data) {
  return api.put(`/api/wanteds/${id}`, data)
}

export function deleteWanted(id) {
  return api.delete(`/api/wanteds/${id}`)
}

export function respondToWanted(id, data) {
  return api.post(`/api/wanteds/${id}/respond`, data)
}

export function getMyWanteds(params) {
  return api.get('/api/wanteds/my', { params })
}
