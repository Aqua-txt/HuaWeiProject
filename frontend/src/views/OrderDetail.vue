<template>
  <div class="order-detail-page">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>订单详情</span>
          <el-tag :type="getStatusType(order.status)" size="large">{{ order.status }}</el-tag>
        </div>
      </template>

      <div class="order-info">
        <div class="info-row">
          <span class="label">订单号：</span>
          <span class="value">{{ order.order_no }}</span>
        </div>
        <div class="info-row">
          <span class="label">创建时间：</span>
          <span class="value">{{ formatTime(order.created_at) }}</span>
        </div>
        <div class="info-row" v-if="order.buyer_confirmed_at">
          <span class="label">确认时间：</span>
          <span class="value">{{ formatTime(order.buyer_confirmed_at) }}</span>
        </div>
      </div>

      <el-divider />

      <div class="product-section">
        <h3>商品信息</h3>
        <div class="product-card">
          <img
            :src="getImageUrl(order.product_images[0])"
            class="product-image"
            v-if="order.product_images && order.product_images.length > 0"
          />
          <div class="product-info">
            <div class="product-title">{{ order.product_title }}</div>
            <div class="product-price">¥{{ order.product_price }}</div>
          </div>
        </div>
      </div>

      <el-divider />

      <div class="amount-section">
        <div class="amount-row">
          <span>商品金额：</span>
          <span class="price">¥{{ order.product_price }}</span>
        </div>
        <div class="amount-row total">
          <span>实付款：</span>
          <span class="price">¥{{ order.amount }}</span>
        </div>
      </div>

      <el-divider />

      <div class="participants-section">
        <h3>交易双方</h3>
        <div class="participant">
          <span class="role">买家：</span>
          <span>{{ order.buyer_nickname }}</span>
        </div>
        <div class="participant">
          <span class="role">卖家：</span>
          <span>{{ order.seller_nickname }}</span>
        </div>
      </div>

      <el-divider v-if="order.refund_reason" />

      <div class="refund-section" v-if="order.refund_reason">
        <h3>退款信息</h3>
        <div class="info-row">
          <span class="label">退款原因：</span>
          <span class="value">{{ order.refund_reason }}</span>
        </div>
        <div class="info-row">
          <span class="label">退款状态：</span>
          <el-tag :type="order.refund_status === '已同意' ? 'success' : 'info'">
            {{ order.refund_status }}
          </el-tag>
        </div>
      </div>

      <div class="actions">
        <el-button @click="$router.push('/home')">
          返回主页
        </el-button>
        <el-button @click="$router.push('/orders')">
          返回我的订单
        </el-button>
        <el-button
          v-if="order.status === '待付款' && isBuyer"
          type="primary"
          @click="goToPay"
        >
          去支付
        </el-button>
        <el-button
          v-if="order.status === '待付款' && isBuyer"
          type="danger"
          plain
          @click="handleCancel"
        >
          取消订单
        </el-button>
        <el-button
          v-if="order.status === '已付款' && isBuyer"
          type="success"
          @click="handleConfirm"
        >
          确认收货
        </el-button>
        <el-button
          v-if="order.status === '已付款' && isBuyer"
          type="warning"
          @click="showRefundDialog = true"
        >
          申请退款
        </el-button>
        <el-button
          v-if="order.status === '退款中' && isSeller"
          type="success"
          @click="handleRefundRespond(true)"
        >
          同意退款
        </el-button>
        <el-button
          v-if="order.status === '退款中' && isSeller"
          type="danger"
          @click="handleRefundRespond(false)"
        >
          拒绝退款
        </el-button>
        <el-button
          v-if="order.status === '已完成' && reviewable"
          type="primary"
          @click="goToReview"
        >
          评价
        </el-button>
      </div>
    </el-card>

    <el-dialog v-model="showRefundDialog" title="申请退款" width="500px">
      <el-form>
        <el-form-item label="退款原因">
          <el-input
            v-model="refundReason"
            type="textarea"
            :rows="4"
            placeholder="请输入退款原因（至少10个字）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRefundDialog = false">取消</el-button>
        <el-button type="primary" @click="handleApplyRefund">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import { getOrder, cancelOrder, confirmReceipt, applyRefund, respondRefund } from '../api/order'
import { checkReviewable } from '../api/review'
import { useUserStore } from '../store'
import { getUploadUrl } from '../utils/url'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const order = ref({})
const loading = ref(false)
const showRefundDialog = ref(false)
const refundReason = ref('')
const reviewable = ref(false)

const orderId = route.params.id

const isBuyer = computed(() => order.value.buyer_id === userStore.user?.id)
const isSeller = computed(() => order.value.seller_id === userStore.user?.id)

const getStatusType = (status) => {
  const map = {
    '待付款': 'warning',
    '已取消': 'info',
    '已付款': 'primary',
    '已完成': 'success',
    '退款中': 'info',
    '已退款': 'danger',
    '管理员仲裁': 'danger',
  }
  return map[status] || 'info'
}

const getImageUrl = (filename) => {
  if (!filename) return ''
  return getUploadUrl(filename)
}

const formatTime = (time) => {
  if (!time) return ''
  return new Date(time).toLocaleString('zh-CN')
}

const loadOrder = async () => {
  loading.value = true
  try {
    const res = await getOrder(orderId)
    order.value = res.data
    if (res.data.status === '已完成') {
      await loadReviewableState()
    } else {
      reviewable.value = false
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const loadReviewableState = async () => {
  try {
    const res = await checkReviewable(orderId)
    reviewable.value = Boolean(res.data.reviewable)
  } catch (e) {
    console.error(e)
    reviewable.value = false
  }
}

const goToPay = () => {
  router.push(`/pay/${orderId}`)
}

const handleCancel = async () => {
  try {
    await ElMessageBox.confirm(
      '取消订单后，商品会重新上架，是否继续？',
      '取消订单',
      { type: 'warning' }
    )
    await cancelOrder(orderId)
    ElMessage.success('订单已取消，商品已重新上架')
    loadOrder()
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  }
}

const handleConfirm = async () => {
  try {
    await ElMessageBox.confirm(
      '确认收货后将打款给卖家，不可撤销，是否确认？',
      '确认收货',
      { type: 'warning' }
    )
    await confirmReceipt(orderId)
    ElMessage.success('确认收货成功')
    loadOrder()
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  }
}

const handleApplyRefund = async () => {
  if (refundReason.value.length < 10) {
    ElMessage.warning('退款原因至少10个字')
    return
  }
  try {
    await applyRefund(orderId, { reason: refundReason.value })
    showRefundDialog.value = false
    refundReason.value = ''
    loadOrder()
  } catch (e) {
    console.error(e)
  }
}

const handleRefundRespond = async (agree) => {
  try {
    await ElMessageBox.confirm(
      agree ? '同意退款后款项将退回买家，是否确认？' : '拒绝退款后将进入管理员仲裁，是否确认？',
      agree ? '同意退款' : '拒绝退款',
      { type: 'warning' }
    )
    await respondRefund(orderId, { agree, note: '' })
    loadOrder()
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  }
}

const goToReview = () => {
  router.push(`/review/${orderId}`)
}

onMounted(() => {
  loadOrder()
})
</script>

<style scoped>
.order-detail-page {
  min-height: calc(100vh - 120px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 20px;
  box-sizing: border-box;
}

.order-detail-page :deep(.el-card) {
  width: min(100%, 700px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.order-info {
  padding: 10px 0;
}

.info-row {
  margin-bottom: 12px;
}

.label {
  color: #666;
  margin-right: 8px;
}

.value {
  color: #333;
}

.product-section h3,
.participants-section h3,
.refund-section h3 {
  margin-bottom: 16px;
}

.product-card {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: #f5f5f5;
  border-radius: 8px;
}

.product-image {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: 8px;
}

.product-title {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 8px;
}

.product-price {
  font-size: 18px;
  color: #f56c6c;
  font-weight: bold;
}

.amount-section {
  padding: 10px 0;
}

.amount-row {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 8px;
}

.amount-row.total {
  font-size: 18px;
  font-weight: bold;
}

.price {
  color: #f56c6c;
  margin-left: 8px;
}

.participant {
  margin-bottom: 8px;
}

.role {
  color: #666;
  margin-right: 8px;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 24px;
}
</style>
