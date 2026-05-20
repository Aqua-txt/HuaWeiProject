import api from './index'

export function createOrder(data) {
  return api.post('/api/orders', data)
}

export function getOrders(params) {
  return api.get('/api/orders', { params })
}

export function getOrderById(id) {
  return api.get(`/api/orders/${id}`)
}

export function confirmReceive(id) {
  return api.post(`/api/orders/${id}/confirm`)
}

export function requestRefund(id, data) {
  return api.post(`/api/orders/${id}/refund`, data)
}

export function handleRefund(id, data) {
  return api.post(`/api/orders/${id}/handle-refund`, data)
}

export function mockPayment(data) {
  return api.post('/api/pay/mock-wechat-pay', data)
}
