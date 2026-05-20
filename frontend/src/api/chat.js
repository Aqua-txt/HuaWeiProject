import api from './index'

export function getConversations() {
  return api.get('/api/conversations')
}

export function createConversation(data) {
  return api.post('/api/conversations', data)
}

export function getMessages(convId, params) {
  return api.get(`/api/conversations/${convId}/messages`, { params })
}

export function sendMessage(convId, data) {
  return api.post(`/api/conversations/${convId}/messages`, data)
}

export function getUnreadCount() {
  return api.get('/api/unread-count')
}
