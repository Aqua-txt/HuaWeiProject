<template>
  <div class="orders-page">
    <div class="page-header">
      <h1 class="page-title">我的订单</h1>
      <div class="tab-group">
        <button 
          v-for="tab in tabs" 
          :key="tab.value"
          :class="['tab-btn', { active: activeTab === tab.value }]"
          @click="activeTab = tab.value"
        >
          {{ tab.label }}
          <span v-if="tab.count" class="tab-count">{{ tab.count }}</span>
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else-if="orders.length === 0" class="empty-state">
      <svg viewBox="0 0 64 64" fill="none" width="80" height="80">
        <circle cx="32" cy="32" r="28" stroke="#E3E8EF" stroke-width="3" stroke-dasharray="4 4"/>
        <path d="M20 36l8-8 8 8" stroke="#98A8B8" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
        <rect x="24" y="24" width="8" height="16" rx="2" stroke="#98A8B8" stroke-width="2"/>
      </svg>
      <h3>暂无订单</h3>
      <p>快去逛逛心仪的商品吧</p>
      <router-link to="/home">
        <button class="btn-primary">浏览商品</button>
      </router-link>
    </div>

    <div v-else class="orders-grid">
      <div v-for="order in orders" :key="order.id" class="order-card" @click="goToDetail(order.id)">
        <div class="order-header">
          <span class="order-no">订单号: {{ order.order_no }}</span>
          <span :class="['status-badge', statusClass(order.status)]">{{ statusText(order.status) }}</span>
        </div>
        <div class="order-product">
          <img :src="productImage(order.product)" :alt="order.product.title" class="product-image" />
          <div class="product-info">
            <h3 class="product-title">{{ order.product.title }}</h3>
            <p class="product-price">¥{{ order.amount.toFixed(2) }}</p>
          </div>
        </div>
        <div class="order-footer">
          <div class="order-peer">
            <span class="peer-label">{{ activeTab === 'buyer' ? '卖家' : '买家' }}:</span>
            <el-avatar :size="24" :src="peerAvatar(order)">
              {{ peerName(order)?.[0] }}
            </el-avatar>
            <span class="peer-name">{{ peerName(order) }}</span>
          </div>
          <div class="order-actions">
            <button v-if="order.status === 'paid'" class="btn-action primary" @click.stop="openConfirmDialog(order)">
              确认收货
            </button>
            <button v-if="order.status === 'paid'" class="btn-action" @click.stop="openRefundDialog(order)">
              申请退款
            </button>
            <button v-if="order.status === 'refund_pending' && activeTab === 'seller'" class="btn-action primary" @click.stop="processRefund(order, true)">
              同意退款
            </button>
            <button v-if="order.status === 'refund_pending' && activeTab === 'seller'" class="btn-action" @click.stop="processRefund(order, false)">
              拒绝退款
            </button>
            <button v-if="order.status === 'completed' && !order.reviewed" class="btn-action primary" @click.stop="goToReview(order)">
              去评价
            </button>
          </div>
        </div>
        <div class="order-time">创建于 {{ formatDate(order.created_at) }}</div>
      </div>
    </div>

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
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getOrders, confirmReceive, requestRefund, handleRefund } from '../api/order'

const router = useRouter()
const orders = ref([])
const loading = ref(true)
const activeTab = ref('buyer')
const refundDialogVisible = ref(false)
const confirmDialogVisible = ref(false)
const refundReason = ref('')
const selectedOrder = ref(null)

const tabs = [
  { label: '我买到的', value: 'buyer', count: 0 },
  { label: '我卖出的', value: 'seller', count: 0 },
]

const baseUrl = 'http://127.0.0.1:5000'

const statusText = (status) => {
  const map = {
    pending: '待付款',
    paid: '待面交',
    completed: '已完成',
    cancelled: '已取消',
    refund_pending: '退款中',
    refunded: '已退款',
  }
  return map[status] || status
}

const statusClass = (status) => {
  const map = {
    pending: 'warning',
    paid: 'primary',
    completed: 'success',
    cancelled: 'default',
    refund_pending: 'warning',
    refunded: 'default',
  }
  return map[status] || 'default'
}

const productImage = (product) => {
  return product.images?.length > 0 
    ? `${baseUrl}/api/uploads/${product.images[0]}`
    : 'https://via.placeholder.com/120x120?text=No+Image'
}

const peerName = (order) => {
  return activeTab.value === 'buyer' ? order.seller?.nickname : order.buyer?.nickname
}

const peerAvatar = (order) => {
  const avatar = activeTab.value === 'buyer' ? order.seller?.avatar : order.buyer?.avatar
  return avatar ? `${baseUrl}/api/uploads/${avatar}` : ''
}

const formatDate = (date) => {
  return new Date(date).toLocaleString('zh-CN', {
    month: 'numeric',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

async function fetchOrders() {
  loading.value = true
  try {
    const res = await getOrders({ type: activeTab.value })
    orders.value = res.data.orders || []
  } catch (error) {
    console.error('Failed to fetch orders:', error)
  } finally {
    loading.value = false
  }
}

function goToDetail(id) {
  router.push(`/orders/${id}`)
}

function goToReview(order) {
  router.push(`/orders/${order.id}/review`)
}

function openConfirmDialog(order) {
  selectedOrder.value = order
  confirmDialogVisible.value = true
}

async function submitConfirm() {
  try {
    await confirmReceive(selectedOrder.value.id)
    ElMessage.success('确认收货成功')
    confirmDialogVisible.value = false
    fetchOrders()
  } catch (error) {
    console.error('Failed to confirm:', error)
  }
}

function openRefundDialog(order) {
  selectedOrder.value = order
  refundDialogVisible.value = true
  refundReason.value = ''
}

async function submitRefund() {
  if (!refundReason.value.trim()) {
    ElMessage.warning('请填写退款原因')
    return
  }
  try {
    await requestRefund(selectedOrder.value.id, { reason: refundReason.value })
    ElMessage.success('退款申请已提交')
    refundDialogVisible.value = false
    fetchOrders()
  } catch (error) {
    console.error('Failed to request refund:', error)
  }
}

async function processRefund(order, agree) {
  try {
    await handleRefund(order.id, { agree })
    ElMessage.success(agree ? '已同意退款' : '已拒绝退款')
    fetchOrders()
  } catch (error) {
    console.error('Failed to handle refund:', error)
  }
}

onMounted(() => {
  fetchOrders()
})

watch(activeTab, () => {
  fetchOrders()
})
</script>

<style scoped>
.orders-page {
  max-width: 900px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--c-text);
  margin-bottom: 20px;
}

.tab-group {
  display: flex;
  gap: 8px;
  background: var(--c-surface);
  padding: 6px;
  border-radius: 12px;
  box-shadow: var(--c-shadow-sm);
}

.tab-btn {
  flex: 1;
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: var(--c-text-secondary);
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.25s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.tab-btn.active {
  background: var(--c-primary);
  color: white;
  box-shadow: 0 2px 8px rgba(91,141,239,0.3);
}

.tab-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  background: rgba(255,255,255,0.25);
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
}

.tab-btn:not(.active) .tab-count {
  background: var(--c-primary-light);
  color: var(--c-primary);
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

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  background: var(--c-surface);
  border-radius: 20px;
  box-shadow: var(--c-shadow-md);
}

.empty-state h3 {
  margin-top: 20px;
  font-size: 20px;
  font-weight: 600;
  color: var(--c-text);
}

.empty-state p {
  margin-top: 8px;
  color: var(--c-text-muted);
  font-size: 14px;
}

.btn-primary {
  margin-top: 24px;
  padding: 12px 28px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--c-primary), #4CC9F0);
  color: white;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s;
  box-shadow: 0 4px 16px rgba(91,141,239,0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(91,141,239,0.4);
}

.orders-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.order-card {
  background: var(--c-surface);
  border-radius: 16px;
  padding: 20px;
  box-shadow: var(--c-shadow-md);
  cursor: pointer;
  transition: all 0.25s;
  animation: fadeInUp 0.4s ease-out;
}

.order-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--c-shadow-lg);
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(16px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.order-no {
  font-size: 13px;
  color: var(--c-text-muted);
  font-family: 'Courier New', monospace;
}

.status-badge {
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
}

.status-badge.primary {
  background: var(--c-primary-light);
  color: var(--c-primary);
}

.status-badge.success {
  background: rgba(6,214,160,0.15);
  color: #059669;
}

.status-badge.warning {
  background: rgba(255,159,67,0.15);
  color: #E67E22;
}

.status-badge.default {
  background: var(--c-surface-alt);
  color: var(--c-text-muted);
}

.order-product {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.product-image {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: 12px;
  background: var(--c-surface-alt);
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
  line-height: 1.4;
}

.product-price {
  font-size: 20px;
  font-weight: 700;
  color: var(--c-accent);
}

.order-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid var(--c-border);
}

.order-peer {
  display: flex;
  align-items: center;
  gap: 8px;
}

.peer-label {
  font-size: 13px;
  color: var(--c-text-muted);
}

.peer-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--c-text);
}

.order-actions {
  display: flex;
  gap: 8px;
}

.btn-action {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  background: var(--c-surface-alt);
  color: var(--c-text-secondary);
}

.btn-action:hover {
  background: var(--c-border);
}

.btn-action.primary {
  background: var(--c-primary);
  color: white;
}

.btn-action.primary:hover {
  background: var(--c-primary-dark);
}

.order-time {
  margin-top: 12px;
  font-size: 12px;
  color: var(--c-text-muted);
}
</style>
