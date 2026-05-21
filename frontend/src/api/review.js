import api from './index'

export function createReview(data) {
  return api.post('/api/reviews', data)
}

export function getReviews(params) {
  return api.get('/api/reviews', { params })
}

export function getReview(reviewId) {
  return api.get(`/api/reviews/${reviewId}`)
}

export function checkReviewable(orderId) {
  return api.get(`/api/orders/${orderId}/reviewable`)
}
