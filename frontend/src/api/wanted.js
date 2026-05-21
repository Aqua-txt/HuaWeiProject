import api from './index'

export function createWanted(data) {
  return api.post('/api/wanteds', data)
}

export function getWanteds(params) {
  return api.get('/api/wanteds', { params })
}

export function getWanted(wantedId) {
  return api.get(`/api/wanteds/${wantedId}`)
}

export function updateWanted(wantedId, data) {
  return api.put(`/api/wanteds/${wantedId}`, data)
}

export function deleteWanted(wantedId) {
  return api.delete(`/api/wanteds/${wantedId}`)
}

export function createWantedResponse(wantedId, data) {
  return api.post(`/api/wanteds/${wantedId}/responses`, data)
}

export function getWantedResponses(wantedId) {
  return api.get(`/api/wanteds/${wantedId}/responses`)
}
