import api from './index'

export function createOrder(data) {
  return api.post('/api/orders', data)
}

export function payOrder(orderId) {
  return api.post(`/api/orders/${orderId}/pay`)
}

export function cancelOrder(orderId) {
  return api.post(`/api/orders/${orderId}/cancel`)
}

export function confirmReceipt(orderId) {
  return api.post(`/api/orders/${orderId}/confirm`)
}

export function applyRefund(orderId, data) {
  return api.post(`/api/orders/${orderId}/refund`, data)
}

export function respondRefund(orderId, data) {
  return api.post(`/api/orders/${orderId}/refund/respond`, data)
}

export function getOrders(params) {
  return api.get('/api/orders', { params })
}

export function getOrder(orderId) {
  return api.get(`/api/orders/${orderId}`)
}
