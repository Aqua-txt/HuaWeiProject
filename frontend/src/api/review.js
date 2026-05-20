import api from './index'

export function createReview(data) {
  return api.post('/api/reviews', data)
}

export function getReviewsByUser(userId, params) {
  return api.get(`/api/reviews/user/${userId}`, { params })
}

export function getMyReviews(params) {
  return api.get('/api/reviews/my', { params })
}

export function checkReviewed(orderId) {
  return api.get(`/api/reviews/check/${orderId}`)
}
