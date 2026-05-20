<template>
  <div class="review-page">
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <template v-else-if="order">
      <div class="page-header">
        <button class="back-btn" @click="$router.back()">
          <svg viewBox="0 0 24 24" fill="none" width="20" height="20" stroke="currentColor" stroke-width="2">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          返回
        </button>
        <h1 class="page-title">评价订单</h1>
      </div>

      <div class="review-card">
        <div class="peer-section">
          <el-avatar :size="64" :src="peerAvatar">{{ peer?.nickname?.[0] }}</el-avatar>
          <div class="peer-info">
            <h2 class="peer-name">{{ peer?.nickname }}</h2>
            <p class="peer-role">交易伙伴</p>
          </div>
        </div>

        <div class="product-section">
          <img :src="productImage" :alt="order.product.title" class="product-image" />
          <div class="product-info">
            <h3 class="product-title">{{ order.product.title }}</h3>
            <p class="product-price">交易金额: ¥{{ order.amount.toFixed(2) }}</p>
          </div>
        </div>

        <el-divider />

        <div class="rating-section">
          <h3 class="section-title">为TA打分</h3>
          <p class="section-desc">您的评价将帮助其他同学了解这位交易伙伴</p>

          <div class="rating-item">
            <div class="rating-label">
              <span class="label-text">沟通态度</span>
              <span class="label-desc">回复及时,态度友好</span>
            </div>
            <div class="rating-stars">
              <button 
                v-for="i in 5" 
                :key="i"
                :class="['star-btn', { active: i <= ratings.communication }]"
                @click="ratings.communication = i"
              >
                <svg viewBox="0 0 24 24" fill="currentColor" width="28" height="28">
                  <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                </svg>
              </button>
            </div>
          </div>

          <div class="rating-item">
            <div class="rating-label">
              <span class="label-text">描述相符</span>
              <span class="label-desc">商品与描述一致</span>
            </div>
            <div class="rating-stars">
              <button 
                v-for="i in 5" 
                :key="i"
                :class="['star-btn', { active: i <= ratings.description }]"
                @click="ratings.description = i"
              >
                <svg viewBox="0 0 24 24" fill="currentColor" width="28" height="28">
                  <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                </svg>
              </button>
            </div>
          </div>

          <div class="rating-item">
            <div class="rating-label">
              <span class="label-text">交易速度</span>
              <span class="label-desc">按时赴约,效率高</span>
            </div>
            <div class="rating-stars">
              <button 
                v-for="i in 5" 
                :key="i"
                :class="['star-btn', { active: i <= ratings.speed }]"
                @click="ratings.speed = i"
              >
                <svg viewBox="0 0 24 24" fill="currentColor" width="28" height="28">
                  <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                </svg>
              </button>
            </div>
          </div>
        </div>

        <el-divider />

        <div class="comment-section">
          <h3 class="section-title">留言评价 <span class="optional">(选填)</span></h3>
          <el-input
            v-model="comment"
            type="textarea"
            :rows="4"
            placeholder="分享您的交易体验,帮助其他同学~"
            maxlength="200"
            show-word-limit
          />
        </div>

        <div class="submit-section">
          <button class="btn-submit" @click="submitReview" :disabled="submitting">
            {{ submitting ? '提交中...' : '提交评价' }}
          </button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getOrderById } from '../api/order'
import { createReview } from '../api/review'
import { useUserStore } from '../store'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const order = ref(null)
const loading = ref(true)
const submitting = ref(false)
const comment = ref('')

const ratings = reactive({
  communication: 5,
  description: 5,
  speed: 5,
})

const baseUrl = 'http://127.0.0.1:5000'

const isBuyer = computed(() => {
  return order.value?.buyer_id === userStore.user?.id
})

const peer = computed(() => {
  return isBuyer.value ? order.value?.seller : order.value?.buyer
})

const peerAvatar = computed(() => {
  const avatar = peer.value?.avatar
  return avatar ? `${baseUrl}/api/uploads/${avatar}` : ''
})

const productImage = computed(() => {
  const images = order.value?.product?.images
  return images?.length > 0 
    ? `${baseUrl}/api/uploads/${images[0]}`
    : 'https://via.placeholder.com/120x120?text=No+Image'
})

async function fetchOrder() {
  loading.value = true
  try {
    const res = await getOrderById(route.params.id)
    order.value = res.data.order
  } catch (error) {
    console.error('Failed to fetch order:', error)
  } finally {
    loading.value = false
  }
}

async function submitReview() {
  if (ratings.communication === 0 || ratings.description === 0 || ratings.speed === 0) {
    ElMessage.warning('请完成所有评分项')
    return
  }

  submitting.value = true
  try {
    const revieweeId = isBuyer.value ? order.value.seller_id : order.value.buyer_id
    await createReview({
      order_id: order.value.id,
      reviewee_id: revieweeId,
      communication_score: ratings.communication,
      description_score: ratings.description,
      speed_score: ratings.speed,
      comment: comment.value,
    })
    ElMessage.success('评价提交成功')
    router.push('/orders')
  } catch (error) {
    console.error('Failed to submit review:', error)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchOrder()
})
</script>

<style scoped>
.review-page {
  max-width: 600px;
  margin: 0 auto;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: var(--c-text-muted);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--c-border);
  border-top-color: var(--c-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  border: none;
  border-radius: 10px;
  background: var(--c-surface);
  color: var(--c-text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: var(--c-shadow-sm);
}

.back-btn:hover {
  background: var(--c-surface-alt);
  color: var(--c-text);
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--c-text);
}

.review-card {
  background: var(--c-surface);
  border-radius: 20px;
  padding: 32px;
  box-shadow: var(--c-shadow-lg);
}

.peer-section {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 24px;
}

.peer-info {
  flex: 1;
}

.peer-name {
  font-size: 20px;
  font-weight: 700;
  color: var(--c-text);
  margin-bottom: 6px;
}

.peer-role {
  font-size: 14px;
  color: var(--c-text-muted);
}

.product-section {
  display: flex;
  gap: 16px;
  padding: 20px;
  background: var(--c-surface-alt);
  border-radius: 12px;
  margin-bottom: 24px;
}

.product-image {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 10px;
}

.product-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.product-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--c-text);
  margin-bottom: 8px;
}

.product-price {
  font-size: 14px;
  color: var(--c-text-secondary);
}

.rating-section,
.comment-section {
  margin: 24px 0;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--c-text);
  margin-bottom: 8px;
}

.section-desc {
  font-size: 14px;
  color: var(--c-text-muted);
  margin-bottom: 24px;
}

.optional {
  font-size: 14px;
  font-weight: 400;
  color: var(--c-text-muted);
}

.rating-item {
  margin-bottom: 24px;
}

.rating-label {
  margin-bottom: 12px;
}

.label-text {
  display: block;
  font-size: 15px;
  font-weight: 600;
  color: var(--c-text);
  margin-bottom: 4px;
}

.label-desc {
  font-size: 13px;
  color: var(--c-text-muted);
}

.rating-stars {
  display: flex;
  gap: 8px;
}

.star-btn {
  width: 40px;
  height: 40px;
  border: none;
  background: transparent;
  color: var(--c-border);
  cursor: pointer;
  transition: all 0.2s;
  padding: 0;
}

.star-btn:hover {
  transform: scale(1.1);
}

.star-btn.active {
  color: #F59E0B;
  animation: starPop 0.3s ease-out;
}

@keyframes starPop {
  0% { transform: scale(1); }
  50% { transform: scale(1.2); }
  100% { transform: scale(1); }
}

.submit-section {
  margin-top: 32px;
  text-align: center;
}

.btn-submit {
  padding: 16px 48px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--c-primary), #4CC9F0);
  color: white;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s;
  box-shadow: 0 4px 16px rgba(91,141,239,0.3);
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(91,141,239,0.4);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
