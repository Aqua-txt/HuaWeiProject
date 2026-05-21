<template>
  <div class="orders-page">
    <el-tabs v-model="activeTab" @tab-change="handleTabChange">
      <el-tab-pane label="我买到的" name="buyer"></el-tab-pane>
      <el-tab-pane label="我卖出的" name="seller"></el-tab-pane>
    </el-tabs>

    <el-card v-loading="loading" class="orders-card">
      <div v-if="orders.length === 0" class="empty-state">
        <el-empty description="暂无订单"></el-empty>
      </div>
      <div v-else class="order-list">
        <div v-for="order in orders" :key="order.id" class="order-item" @click="goToOrder(order.id)">
          <div class="order-header">
            <span class="order-no">订单号: {{ order.order_no }}</span>
            <el-tag :type="getStatusType(order.status)">{{ order.status }}</el-tag>
          </div>
          <div class="order-body">
            <img
              :src="getImageUrl(order.product_images[0])"
              class="product-image"
              v-if="order.product_images && order.product_images.length > 0"
            />
            <div class="product-info">
              <div class="product-title">{{ order.product_title }}</div>
              <div class="product-price">¥{{ order.amount }}</div>
              <div class="order-time">{{ formatTime(order.created_at) }}</div>
            </div>
          </div>
          <div class="order-actions">
            <el-button
              v-if="order.status === '待付款'"
              type="primary"
              size="small"
              @click.stop="goToPay(order)"
            >
              去支付
            </el-button>
            <el-button
              v-if="order.status === '待付款' && activeTab === 'buyer'"
              type="danger"
              size="small"
              plain
              @click.stop="handleCancel(order)"
            >
              取消订单
            </el-button>
            <el-button
              v-if="order.status === '已付款' && activeTab === 'buyer'"
              type="success"
              size="small"
              @click.stop="handleConfirm(order)"
            >
              确认收货
            </el-button>
            <el-button
              v-if="order.status === '已完成' && isOrderReviewable(order.id)"
              type="primary"
              size="small"
              @click.stop="goToReview(order)"
            >
              评价
            </el-button>
          </div>
        </div>
      </div>

      <el-pagination
        v-if="total > 0"
        v-model:current-page="page"
        :page-size="perPage"
        :total="total"
        layout="prev, pager, next"
        @current-change="loadOrders"
        class="pagination"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import { getOrders, cancelOrder, confirmReceipt } from '../api/order'
import { checkReviewable } from '../api/review'
import { getUploadUrl } from '../utils/url'

const router = useRouter()
const activeTab = ref('buyer')
const orders = ref([])
const loading = ref(false)
const page = ref(1)
const perPage = ref(10)
const total = ref(0)
const reviewableMap = ref({})

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

const loadOrders = async () => {
  loading.value = true
  try {
    const res = await getOrders({
      role: activeTab.value,
      page: page.value,
      per_page: perPage.value,
    })
    orders.value = res.data.orders
    total.value = res.data.total
    await loadReviewableStates()
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const loadReviewableStates = async () => {
  const completedOrders = orders.value.filter(order => order.status === '已完成')
  const nextMap = {}

  await Promise.all(
    completedOrders.map(async (order) => {
      try {
        const res = await checkReviewable(order.id)
        nextMap[order.id] = Boolean(res.data.reviewable)
      } catch (e) {
        console.error(e)
        nextMap[order.id] = false
      }
    })
  )

  reviewableMap.value = nextMap
}

const isOrderReviewable = (orderId) => {
  return Boolean(reviewableMap.value[orderId])
}

const handleTabChange = () => {
  page.value = 1
  loadOrders()
}

const goToOrder = (orderId) => {
  router.push(`/order/${orderId}`)
}

const goToPay = (order) => {
  router.push(`/pay/${order.id}`)
}

const handleConfirm = async (order) => {
  try {
    await ElMessageBox.confirm(
      '确认收货后将打款给卖家，不可撤销，是否确认？',
      '确认收货',
      { type: 'warning' }
    )
    await confirmReceipt(order.id)
    ElMessage.success('确认收货成功')
    loadOrders()
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  }
}

const handleCancel = async (order) => {
  try {
    await ElMessageBox.confirm(
      '取消订单后，商品会重新上架，是否继续？',
      '取消订单',
      { type: 'warning' }
    )
    await cancelOrder(order.id)
    ElMessage.success('订单已取消，商品已重新上架')
    loadOrders()
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  }
}

const goToReview = (order) => {
  router.push(`/review/${order.id}`)
}

onMounted(() => {
  loadOrders()
})
</script>

<style scoped>
.orders-page {
  max-width: 900px;
  margin: 20px auto;
  padding: 0 20px;
}

.orders-card {
  margin-top: 20px;
}

.order-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.order-item {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.order-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.1);
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.order-no {
  font-size: 14px;
  color: #666;
}

.order-body {
  display: flex;
  gap: 16px;
}

.product-image {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: 8px;
}

.product-info {
  flex: 1;
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

.order-time {
  font-size: 12px;
  color: #999;
  margin-top: 8px;
}

.order-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 12px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.empty-state {
  padding: 40px 0;
}
</style>
