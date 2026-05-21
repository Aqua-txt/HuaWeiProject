<template>
  <div class="pay-page">
    <el-card v-loading="loading">
      <template #header>
        <span>确认订单</span>
      </template>

      <div class="product-section">
        <div class="product-card">
          <img
            :src="getImageUrl(order.product_images?.[0])"
            class="product-image"
            v-if="order.product_images && order.product_images.length > 0"
          />
          <div class="product-info">
            <div class="product-title">{{ order.product_title }}</div>
            <div class="product-desc">卖家: {{ order.seller_nickname }}</div>
            <div class="product-price">¥{{ order.amount }}</div>
          </div>
        </div>
      </div>

      <el-divider />

      <div class="amount-section">
        <div class="amount-row">
          <span>商品金额：</span>
          <span class="price">¥{{ order.amount }}</span>
        </div>
        <div class="amount-row total">
          <span>支付金额：</span>
          <span class="price">¥{{ order.amount }}</span>
        </div>
      </div>

      <el-divider />

      <div class="pay-section">
        <h3>支付方式</h3>
        <el-radio-group v-model="payMethod">
          <el-radio label="wechat">
            <el-icon><Wallet /></el-icon>
            微信支付（模拟）
          </el-radio>
        </el-radio-group>
      </div>

      <div class="actions">
        <el-button @click="goBack">取消</el-button>
        <el-button type="primary" @click="handlePay" :loading="paying">
          确认支付
        </el-button>
      </div>
    </el-card>

    <el-dialog v-model="showPayDialog" title="模拟微信支付" width="400px" :close-on-click-modal="false" align-center>
      <div class="mock-pay">
        <el-icon class="pay-icon"><Wallet /></el-icon>
        <p>支付金额：<span class="amount">¥{{ order.amount }}</span></p>
        <el-input
          v-model="mockPassword"
          type="password"
          placeholder="请输入支付密码（模拟，任意即可）"
        />
      </div>
      <template #footer>
        <el-button @click="showPayDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmMockPay" :loading="paying">
          确认支付
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Wallet } from '@element-plus/icons-vue'
import { getOrder, payOrder } from '../api/order'
import { getUploadUrl } from '../utils/url'

const route = useRoute()
const router = useRouter()

const order = ref({})
const loading = ref(false)
const payMethod = ref('wechat')
const showPayDialog = ref(false)
const mockPassword = ref('')
const paying = ref(false)

const orderId = route.params.id

const getImageUrl = (filename) => {
  if (!filename) return ''
  return getUploadUrl(filename)
}

const loadOrder = async () => {
  loading.value = true
  try {
    const res = await getOrder(orderId)
    order.value = res.data
    if (res.data.status !== '待付款') {
      ElMessage.warning('订单状态已变更')
      router.push(`/order/${orderId}`)
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.back()
}

const handlePay = () => {
  showPayDialog.value = true
}

const confirmMockPay = async () => {
  if (!mockPassword.value) {
    ElMessage.warning('请输入支付密码')
    return
  }
  paying.value = true
  try {
    await payOrder(orderId)
    showPayDialog.value = false
    ElMessage.success('支付成功')
    router.push(`/order/${orderId}`)
  } catch (e) {
    console.error(e)
  } finally {
    paying.value = false
  }
}

onMounted(() => {
  loadOrder()
})
</script>

<style scoped>
.pay-page {
  min-height: calc(100vh - 120px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 20px;
  box-sizing: border-box;
}

.pay-page :deep(.el-card) {
  width: min(100%, 600px);
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

.product-desc {
  font-size: 14px;
  color: #666;
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

.pay-section h3 {
  margin-bottom: 16px;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 24px;
}

.mock-pay {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.pay-icon {
  font-size: 48px;
  color: #67c23a;
  margin-bottom: 16px;
}

.mock-pay .amount {
  font-size: 24px;
  color: #f56c6c;
  font-weight: bold;
}

.mock-pay p {
  margin: 0 0 18px;
}

.mock-pay :deep(.el-input) {
  width: 100%;
  max-width: 300px;
}
</style>
