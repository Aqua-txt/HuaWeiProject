<template>
  <div class="order-detail-page">
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
        <h1 class="page-title">订单详情</h1>
      </div>

      <div class="detail-grid">
        <div class="status-card">
          <div class="status-icon">
            <svg v-if="order.status === 'paid'" viewBox="0 0 24 24" fill="none" width="48" height="48" stroke="currentColor" stroke-width="1.5">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 6v6l4 2"/>
            </svg>
            <svg v-else-if="order.status === 'completed'" viewBox="0 0 24 24" fill="none" width="48" height="48" stroke="currentColor" stroke-width="1.5">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <polyline points="22,4 12,14.01 9,11.01"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" width="48" height="48" stroke="currentColor" stroke-width="1.5">
              <rect x="1" y="4" width="22" height="16" rx="2" ry="2"/>
              <line x1="1" y1="10" x2="23" y2="10"/>
            </svg>
          </div>
          <div class="status-info">
            <h2 class="status-title">{{ statusText(order.status) }}</h2>
            <p class="status-desc">{{ statusDesc(order.status) }}</p>
          </div>
        </div>

        <div class="timeline-card">
          <h3 class="card-title">订单状态</h3>
          <div class="timeline">
            <div v-for="(item, index) in timeline" :key="index" class="timeline-item">
              <div class="timeline-dot"></div>
              <div class="timeline-content">
                <div class="timeline-title">{{ item.title }}</div>
                <div class="timeline-time">{{ formatDate(item.time) }}</div>
              </div>
            </div>
          </div>
        </div>

        <div class="product-card">
          <h3 class="card-title">商品信息</h3>
          <div class="product-content">
            <img :src="productImage" :alt="order.product.title" class="product-image" />
            <div class="product-info">
              <h4 class="product-title">{{ order.product.title }}</h4>
              <p class="product-desc">{{ order.product.description }}</p>
              <p class="product-price">¥{{ order.amount.toFixed(2) }}</p>
            </div>
          </div>
        </div>

        <div class="peer-card">
          <h3 class="card-title">{{ isBuyer ? '卖家信息' : '买家信息' }}</h3>
          <div class="peer-content">
            <el-avatar :size="48" :src="peerAvatar">{{ peer?.nickname?.[0] }}</el-avatar>
            <div class="peer-info">
              <div class="peer-name">{{ peer?.nickname }}</div>
              <div class="peer-credit" v-if="peer?.credit_score">
                <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
                  <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                </svg>
                <span>信用分 {{ peer.credit_score.toFixed(1) }}</span>
              </div>
            </div>
            <button class="chat-btn" @click="goToChat">
              <svg viewBox="0 0 24 24" fill="none" width="18" height="18" stroke="currentColor" stroke-width="2">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
              </svg>
              联系TA
            </button>
          </div>
        </div>

        <div class="order-card">
          <h3 class="card-title">订单信息</h3>
          <div class="order-info">
            <div class="info-row">
              <span class="info-label">订单号</span>
              <span class="info-value">{{ order.order_no }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">创建时间</span>
              <span class="info-value">{{ formatDate(order.created_at) }}</span>
            </div>
            <div v-if="order.buyer_confirmed_at" class="info-row">
              <span class="info-label">确认收货时间</span>
              <span class="info-value">{{ formatDate(order.buyer_confirmed_at) }}</span>
            </div>
          </div>
        </div>

        <div v-if="order.refund_reason" class="refund-card">
          <h3 class="card-title">退款信息</h3>
          <div class="refund-content">
            <div class="info-row">
              <span class="info-label">退款原因</span>
              <span class="info-value">{{ order.refund_reason }}</span>
            </div>
            <div v-if="order.refund_status" class="info-row">
              <span class="info-label">退款状态</span>
              <span class="info-value">{{ order.refund_status }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="action-bar">
        <button v-if="order.status === 'paid' && isBuyer" class="btn-primary" @click="confirmDialogVisible = true">
          确认收货
        </button>
        <button v-if="order.status === 'paid' && isBuyer" class="btn-secondary" @click="refundDialogVisible = true">
          申请退款
        </button>
        <button v-if="order.status === 'refund_pending' && !isBuyer" class="btn-primary" @click="processRefund(true)">
          同意退款
        </button>
        <button v-if="order.status === 'refund_pending' && !isBuyer" class="btn-secondary" @click="processRefund(false)">
          拒绝退款
        </button>
        <button v-if="order.status === 'completed' && !order.reviewed && isBuyer" class="btn-primary" @click="goToReview">
          去评价
        </button>
      </div>
    </template>

    <el-dialog v-model="refundDialogVisible" title="申请退款" width="400px">
      <el-form>
        <el-form-item label="退款原因">
          <el-input v-model="refundReason" type="textarea" :rows="3" placeholder="请说明退款原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="refundDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitRefund">提交</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="confirmDialogVisible" title="确认收货" width="400px">
      <p style="color: var(--c-text-secondary); line-height: 1.6;">
        确认收货后,货款将打给卖家,此操作不可撤销。请确保您已当面验货无误。
      </p>
      <template #footer>
        <el-button @click="confirmDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitConfirm">确认收货</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getOrderById, confirmReceive, requestRefund, handleRefund } from '../api/order'
import { useUserStore } from '../store'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const order = ref(null)
const loading = ref(true)
const refundDialogVisible = ref(false)
const confirmDialogVisible = ref(false)
const refundReason = ref('')

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
    : 'https://via.placeholder.com/200x200?text=No+Image'
})

const timeline = computed(() => {
  if (!order.value) return []
  const items = [
    { title: '订单创建', time: order.value.created_at },
  ]
  if (order.value.status !== 'pending') {
    items.push({ title: '付款成功', time: order.value.paid_at || order.value.created_at })
  }
  if (order.value.status === 'completed') {
    items.push({ title: '确认收货', time: order.value.buyer_confirmed_at })
  }
  if (order.value.status === 'refunded') {
    items.push({ title: '退款完成', time: order.value.updated_at })
  }
  return items
})

const statusText = (status) => {
  const map = {
    pending: '待付款',
    paid: '待面交',
    completed: '交易完成',
    cancelled: '已取消',
    refund_pending: '退款处理中',
    refunded: '已退款',
  }
  return map[status] || status
}

const statusDesc = (status) => {
  const map = {
    pending: '请尽快完成支付',
    paid: '请与对方约定面交时间和地点',
    completed: '交易已完成,快去评价吧',
    cancelled: '订单已取消',
    refund_pending: '退款申请处理中',
    refunded: '退款已完成,款项已原路返回',
  }
  return map[status] || ''
}

const formatDate = (date) => {
  return new Date(date).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

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

function goToChat() {
  const peerId = isBuyer.value ? order.value.seller_id : order.value.buyer_id
  router.push(`/chat/${peerId}`)
}

function goToReview() {
  router.push(`/orders/${order.value.id}/review`)
}

async function submitConfirm() {
  try {
    await confirmReceive(order.value.id)
    ElMessage.success('确认收货成功')
    confirmDialogVisible.value = false
    fetchOrder()
  } catch (error) {
    console.error('Failed to confirm:', error)
  }
}

async function submitRefund() {
  if (!refundReason.value.trim()) {
    ElMessage.warning('请填写退款原因')
    return
  }
  try {
    await requestRefund(order.value.id, { reason: refundReason.value })
    ElMessage.success('退款申请已提交')
    refundDialogVisible.value = false
    fetchOrder()
  } catch (error) {
    console.error('Failed to request refund:', error)
  }
}

async function processRefund(agree) {
  try {
    await handleRefund(order.value.id, { agree })
    ElMessage.success(agree ? '已同意退款' : '已拒绝退款')
    fetchOrder()
  } catch (error) {
    console.error('Failed to handle refund:', error)
  }
}

onMounted(() => {
  fetchOrder()
})
</script>

<style scoped>
.order-detail-page {
  max-width: 800px;
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

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--c-text);
  margin-bottom: 16px;
}

.status-card {
  grid-column: 1 / -1;
  background: var(--c-surface);
  border-radius: 20px;
  padding: 32px;
  box-shadow: var(--c-shadow-md);
  display: flex;
  align-items: center;
  gap: 24px;
}

.status-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: var(--c-primary-light);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--c-primary);
}

.status-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--c-text);
  margin-bottom: 8px;
}

.status-desc {
  font-size: 15px;
  color: var(--c-text-secondary);
}

.timeline-card,
.product-card,
.peer-card,
.order-card,
.refund-card {
  background: var(--c-surface);
  border-radius: 16px;
  padding: 20px;
  box-shadow: var(--c-shadow-md);
}

.timeline {
  position: relative;
  padding-left: 24px;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 6px;
  top: 8px;
  bottom: 8px;
  width: 2px;
  background: var(--c-border);
}

.timeline-item {
  position: relative;
  padding-bottom: 20px;
}

.timeline-item:last-child {
  padding-bottom: 0;
}

.timeline-dot {
  position: absolute;
  left: -20px;
  top: 6px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--c-primary);
  border: 2px solid white;
  box-shadow: 0 0 0 2px var(--c-primary);
}

.timeline-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--c-text);
  margin-bottom: 4px;
}

.timeline-time {
  font-size: 13px;
  color: var(--c-text-muted);
}

.product-content {
  display: flex;
  gap: 16px;
}

.product-image {
  width: 120px;
  height: 120px;
  object-fit: cover;
  border-radius: 12px;
  background: var(--c-surface-alt);
}

.product-info {
  flex: 1;
}

.product-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--c-text);
  margin-bottom: 8px;
}

.product-desc {
  font-size: 14px;
  color: var(--c-text-secondary);
  margin-bottom: 12px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.product-price {
  font-size: 20px;
  font-weight: 700;
  color: var(--c-accent);
}

.peer-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.peer-info {
  flex: 1;
}

.peer-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--c-text);
  margin-bottom: 6px;
}

.peer-credit {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #F59E0B;
}

.chat-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  border: none;
  border-radius: 10px;
  background: var(--c-primary-light);
  color: var(--c-primary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.chat-btn:hover {
  background: var(--c-primary);
  color: white;
}

.order-info,
.refund-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--c-border);
}

.info-row:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.info-label {
  font-size: 14px;
  color: var(--c-text-muted);
}

.info-value {
  font-size: 14px;
  font-weight: 500;
  color: var(--c-text);
}

.action-bar {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding: 24px;
  background: var(--c-surface);
  border-radius: 16px;
  box-shadow: var(--c-shadow-md);
}

.btn-primary {
  padding: 14px 32px;
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

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(91,141,239,0.4);
}

.btn-secondary {
  padding: 14px 32px;
  border: 2px solid var(--c-border);
  border-radius: 12px;
  background: transparent;
  color: var(--c-text);
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s;
}

.btn-secondary:hover {
  border-color: var(--c-primary);
  color: var(--c-primary);
}
</style>
