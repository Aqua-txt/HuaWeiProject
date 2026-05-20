<template>
  <div class="product-detail" v-loading="loading">
    <template v-if="product && !notFound">
      <div class="detail-breadcrumb">
        <router-link to="/home" class="bread-link">首页</router-link>
        <span class="bread-sep">/</span>
        <span class="bread-current">{{ product.title }}</span>
      </div>

      <div class="detail-top">
        <div class="image-section">
          <div class="main-image-wrap">
            <el-image :src="currentImage" fit="cover" class="main-image">
              <template #error>
                <div class="img-placeholder">
                  <svg viewBox="0 0 80 80" fill="none" width="80" height="80">
                    <rect x="10" y="16" width="60" height="48" rx="6" stroke="#d0d5dd" stroke-width="2"/>
                    <circle cx="28" cy="34" r="6" stroke="#d0d5dd" stroke-width="2"/>
                    <path d="M10 56l18-18 14 14 10-10 18 18" stroke="#d0d5dd" stroke-width="2" stroke-linejoin="round"/>
                  </svg>
                </div>
              </template>
            </el-image>
            <div v-if="product.is_favorited" class="fav-badge">
              <span class="fav-dot"></span>已收藏
            </div>
          </div>
          <div v-if="product.images && product.images.length > 1" class="thumb-strip">
            <button v-for="(img, i) in product.images" :key="i"
              class="thumb-btn" :class="{ active: currentIndex === i }"
              @click="currentIndex = i">
              <el-image :src="`${baseUrl}/api/uploads/${img}`" fit="cover" class="thumb-img" />
            </button>
          </div>
        </div>

        <div class="info-section">
          <div class="info-tags">
            <span class="info-tag cat">{{ product.category }}</span>
            <span class="info-tag cond">{{ product.condition }}</span>
          </div>
          <h1 class="product-title">{{ product.title }}</h1>
          <div class="product-price">
            <span class="price-symbol">&yen;</span>
            <span class="price-value">{{ product.price }}</span>
          </div>

          <div class="product-desc" v-if="product.description">
            <h4 class="desc-label">商品描述</h4>
            <p class="desc-text">{{ product.description }}</p>
          </div>

          <div class="product-meta-row">
            <span class="meta-pill">
              <svg viewBox="0 0 16 16" fill="none" width="14" height="14"><circle cx="8" cy="8" r="7" stroke="currentColor" stroke-width="1.5"/><path d="M8 4v5l3 2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
              {{ formatDate(product.created_at) }}
            </span>
          </div>

          <div class="seller-card">
            <div class="seller-profile">
              <el-avatar :size="52" :src="getAvatarUrl(product.seller_avatar)" class="seller-avatar" />
              <div class="seller-text">
                <div class="seller-name">{{ product.seller_nickname }}</div>
                <div class="seller-badges">
                  <span class="seller-badge">认证校友</span>
                  <span v-if="sellerCredit" class="credit-badge">
                    <svg viewBox="0 0 24 24" fill="currentColor" width="14" height="14">
                      <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                    </svg>
                    {{ sellerCredit.toFixed(1) }}
                  </span>
                </div>
              </div>
            </div>

            <div class="seller-actions" v-if="!isOwner">
              <button class="btn-buy" @click="handleBuy" :disabled="!userStore.isLoggedIn || product.status !== '上架'">
                <svg viewBox="0 0 24 24" fill="none" width="18" height="18" stroke="currentColor" stroke-width="2">
                  <circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/>
                  <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>
                </svg>
                立即购买
              </button>
              <button class="btn-contact" @click="contactSeller" :disabled="!userStore.isLoggedIn">
                <svg viewBox="0 0 20 20" fill="none" width="18" height="18" stroke="currentColor" stroke-width="1.8" stroke-linecap="round">
                  <path d="M18 2L10 10M18 2l-6 16-2-8-8-2 16-6z"/>
                </svg>
                联系卖家
              </button>
              <button class="btn-fav" :class="{ favorited: product.is_favorited }"
                @click="toggleFav" :disabled="!userStore.isLoggedIn">
                <svg viewBox="0 0 20 20" fill="none" width="18" height="18" stroke="currentColor" stroke-width="1.8">
                  <path d="M10 17l-6.18 3.25L5 13.35.82 9.28l6.07-.88L10 2.7l3.11 5.7 6.07.88L16 13.35l1.18 6.9z"
                    :fill="product.is_favorited ? 'currentColor' : 'none'"/>
                </svg>
                {{ product.is_favorited ? '已收藏' : '收藏' }}
              </button>
            </div>
            <div class="seller-actions" v-else>
              <el-button :icon="Edit" round @click="$router.push(`/edit-product/${product.id}`)">编辑</el-button>
              <el-button v-if="product.status === '上架'" type="warning" round @click="changeStatus('已下架')">下架</el-button>
              <el-button v-else type="success" round @click="changeStatus('上架')">重新上架</el-button>
            </div>
          </div>

          <div v-if="!isOwner && userStore.isLoggedIn" class="report-section">
            <button class="btn-report" @click="openReportDialog">
              <svg viewBox="0 0 24 24" fill="none" width="16" height="16" stroke="currentColor" stroke-width="2">
                <path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/>
                <line x1="4" y1="22" x2="4" y2="15"/>
              </svg>
              举报商品
            </button>
          </div>
        </div>
      </div>
    </template>

    <div v-else-if="notFound" class="off-shelf">
      <el-result icon="warning" title="商品已下架" sub-title="该商品可能已被卖家下架或删除">
        <template #extra>
          <router-link to="/home"><el-button type="primary">返回首页</el-button></router-link>
        </template>
      </el-result>
    </div>

    <el-dialog v-model="reportDialogVisible" title="举报商品" width="500px">
      <el-form :model="reportForm" :rules="reportRules" ref="reportFormRef">
        <el-form-item label="举报类型" prop="report_type">
          <el-select v-model="reportForm.report_type" placeholder="请选择" style="width: 100%;">
            <el-option label="虚假信息" value="虚假信息" />
            <el-option label="违规商品" value="违规商品" />
            <el-option label="诈骗行为" value="诈骗行为" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="举报描述" prop="description">
          <el-input v-model="reportForm.description" type="textarea" :rows="3" placeholder="请详细描述问题(至少10字)" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reportDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitReport">提交举报</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="payDialogVisible" title="确认订单" width="500px">
      <div class="pay-order-summary">
        <div class="pay-product">
          <img :src="currentImage" class="pay-product-image" />
          <div class="pay-product-info">
            <h4>{{ product?.title }}</h4>
            <p class="pay-price">¥{{ product?.price }}</p>
          </div>
        </div>
        <el-divider />
        <div class="pay-seller">
          <span>卖家: {{ product?.seller_nickname }}</span>
        </div>
        <div class="pay-note">
          <p>付款后请与卖家约定面交时间和地点,当面验货后确认收货。</p>
        </div>
      </div>
      <template #footer>
        <el-button @click="payDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="processPayment" :loading="paying">
          {{ paying ? '支付中...' : `确认支付 ¥${product?.price}` }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Edit } from '@element-plus/icons-vue'
import { getProduct, toggleFavorite, updateProductStatus } from '../api/products'
import { createConversation } from '../api/chat'
import { createOrder, mockPayment } from '../api/order'
import { createReport, checkReported } from '../api/report'
import { useUserStore } from '../store'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const baseUrl = 'http://127.0.0.1:5000'

const product = ref(null)
const loading = ref(false)
const notFound = ref(false)
const currentIndex = ref(0)
const reportDialogVisible = ref(false)
const payDialogVisible = ref(false)
const paying = ref(false)
const reportFormRef = ref(null)
const sellerCredit = ref(0)

const reportForm = reactive({
  report_type: '',
  description: '',
})

const reportRules = {
  report_type: [{ required: true, message: '请选择举报类型', trigger: 'change' }],
  description: [
    { required: true, message: '请填写举报描述', trigger: 'blur' },
    { min: 10, message: '描述至少10个字符', trigger: 'blur' },
  ],
}

const currentImage = computed(() => {
  if (!product.value?.images?.length) return ''
  return `${baseUrl}/api/uploads/${product.value.images[currentIndex.value]}`
})

const isOwner = computed(() => {
  return userStore.user?.id === product.value?.seller_id
})

function getAvatarUrl(avatar) {
  return avatar ? `${baseUrl}/api/uploads/${avatar}` : ''
}

function formatDate(t) {
  if (!t) return ''
  return new Date(t).toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit',
  })
}

async function fetchProduct() {
  loading.value = true
  try {
    const res = await getProduct(route.params.id)
    if (res.data.status !== '上架') notFound.value = true
    product.value = res.data
    sellerCredit.value = res.data.seller_credit_score || 0
  } catch {
    notFound.value = true
  } finally {
    loading.value = false
  }
}

async function contactSeller() {
  if (!userStore.isLoggedIn) { router.push('/login'); return }
  try {
    const res = await createConversation({
      product_id: product.value.id,
      seller_id: product.value.seller_id,
    })
    router.push(`/chat/${res.data.id}`)
  } catch {}
}

async function toggleFav() {
  if (!userStore.isLoggedIn) { router.push('/login'); return }
  try {
    const res = await toggleFavorite(product.value.id)
    product.value.is_favorited = res.data.is_favorited
  } catch {}
}

async function changeStatus(status) {
  try {
    await updateProductStatus(product.value.id, status)
    product.value.status = status
    ElMessage.success(status === '已下架' ? '商品已下架' : '商品已重新上架')
  } catch {}
}

function handleBuy() {
  if (!userStore.isLoggedIn) {
    router.push('/login')
    return
  }
  payDialogVisible.value = true
}

async function processPayment() {
  paying.value = true
  try {
    const orderRes = await createOrder({
      product_id: product.value.id,
      seller_id: product.value.seller_id,
      amount: product.value.price,
    })
    const orderId = orderRes.data.order_id
    
    await mockPayment({
      order_id: orderId,
      amount: product.value.price,
    })
    
    ElMessage.success('支付成功')
    payDialogVisible.value = false
    router.push(`/orders/${orderId}`)
  } catch (error) {
    console.error('Payment failed:', error)
  } finally {
    paying.value = false
  }
}

async function openReportDialog() {
  try {
    const res = await checkReported(product.value.id)
    if (res.data.reported) {
      ElMessage.warning('您已举报过该商品')
      return
    }
    reportForm.report_type = ''
    reportForm.description = ''
    reportDialogVisible.value = true
  } catch (error) {
    console.error('Failed to check report:', error)
  }
}

async function submitReport() {
  const valid = await reportFormRef.value.validate().catch(() => false)
  if (!valid) return
  
  try {
    await createReport({
      product_id: product.value.id,
      report_type: reportForm.report_type,
      description: reportForm.description,
    })
    ElMessage.success('举报已提交')
    reportDialogVisible.value = false
  } catch (error) {
    console.error('Failed to submit report:', error)
  }
}

onMounted(() => { fetchProduct() })
</script>

<style scoped>
.product-detail {
  animation: fadeInUp 0.45s ease;
}

.detail-breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
  font-size: 13px;
}

.bread-link { color: var(--c-text-muted); }
.bread-link:hover { color: var(--c-primary); }
.bread-sep { color: var(--c-border); }
.bread-current { color: var(--c-text); font-weight: 500; }

.detail-top {
  display: flex;
  gap: 36px;
  background: white;
  border-radius: 20px;
  padding: 28px;
  box-shadow: 0 2px 16px rgba(26,35,50,0.04);
  border: 1px solid rgba(0,0,0,0.03);
}

@media (max-width: 768px) { .detail-top { flex-direction: column; } }

.image-section { flex: 1; min-width: 0; }

.main-image-wrap {
  position: relative;
  border-radius: 14px;
  overflow: hidden;
  background: #f5f7fa;
}

.main-image { width: 100%; height: 400px; }

.img-placeholder {
  width: 100%;
  height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f8fafc, #eef2f7);
}

.fav-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  background: rgba(255,107,107,0.12);
  color: #FF6B6B;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 5px;
  backdrop-filter: blur(8px);
}

.fav-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #FF6B6B;
}

.thumb-strip {
  display: flex;
  gap: 8px;
  margin-top: 14px;
}

.thumb-btn {
  width: 64px;
  height: 64px;
  border-radius: 10px;
  overflow: hidden;
  border: 2px solid transparent;
  cursor: pointer;
  padding: 0;
  background: none;
  transition: all 0.2s;
}

.thumb-btn.active {
  border-color: var(--c-primary);
  box-shadow: 0 0 0 3px rgba(91,141,239,0.15);
}

.thumb-img { width: 100%; height: 100%; }

.info-section { flex: 1.1; min-width: 280px; }

.info-tags {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.info-tag {
  font-size: 12px;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 8px;
}

.info-tag.cat {
  background: linear-gradient(135deg, rgba(91,141,239,0.1), rgba(91,141,239,0.05));
  color: var(--c-primary);
}

.info-tag.cond {
  background: var(--c-surface-alt);
  color: var(--c-text-secondary);
}

.product-title {
  font-family: var(--font-display);
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 16px;
  line-height: 1.35;
}

.product-price {
  display: flex;
  align-items: baseline;
  margin-bottom: 20px;
}

.price-symbol {
  font-size: 18px;
  color: #FF6B6B;
  font-weight: 700;
  margin-right: 2px;
}

.price-value {
  font-size: 36px;
  color: #FF6B6B;
  font-weight: 800;
  line-height: 1;
  letter-spacing: -1px;
}

.product-desc {
  margin-bottom: 20px;
  padding: 16px;
  background: var(--c-surface-alt);
  border-radius: 12px;
}

.desc-label {
  font-size: 12px;
  color: var(--c-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.8px;
  margin-bottom: 8px;
}

.desc-text {
  font-size: 14px;
  line-height: 1.7;
  color: var(--c-text-secondary);
  white-space: pre-wrap;
}

.product-meta-row {
  margin-bottom: 24px;
}

.meta-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: var(--c-text-muted);
}

.seller-card {
  border-top: 1px solid var(--c-border);
  padding-top: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 14px;
}

.seller-profile {
  display: flex;
  align-items: center;
  gap: 12px;
}

.seller-avatar { flex-shrink: 0; }

.seller-name {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 6px;
}

.seller-badges {
  display: flex;
  gap: 8px;
}

.seller-badge {
  font-size: 11px;
  color: var(--c-secondary);
  background: rgba(6,214,160,0.1);
  padding: 2px 8px;
  border-radius: 8px;
  font-weight: 600;
}

.credit-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #F59E0B;
  font-weight: 600;
}

.seller-actions { display: flex; gap: 10px; flex-wrap: wrap; }

.btn-buy {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 22px;
  border: none;
  border-radius: 28px;
  background: linear-gradient(135deg, #FF6B6B, #EE5A5A);
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s;
  box-shadow: 0 2px 12px rgba(255,107,107,0.3);
}

.btn-buy:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 20px rgba(255,107,107,0.4);
}

.btn-buy:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.btn-contact {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 22px;
  border: none;
  border-radius: 28px;
  background: linear-gradient(135deg, #5B8DEF, #4CC9F0);
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s;
  box-shadow: 0 2px 12px rgba(91,141,239,0.25);
}

.btn-contact:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 20px rgba(91,141,239,0.35);
}

.btn-contact:active { transform: translateY(0); }
.btn-contact:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-fav {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 10px 18px;
  border: 1.5px solid var(--c-border);
  border-radius: 28px;
  background: white;
  color: var(--c-text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.25s;
}

.btn-fav:hover { border-color: #FF6B6B; color: #FF6B6B; }
.btn-fav.favorited { border-color: #FF6B6B; color: #FF6B6B; background: rgba(255,107,107,0.04); }
.btn-fav:disabled { opacity: 0.5; cursor: not-allowed; }

.report-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px dashed var(--c-border);
}

.btn-report {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: none;
  background: transparent;
  color: var(--c-text-muted);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-report:hover {
  color: var(--c-accent);
}

.off-shelf { padding: 60px 0; }

.pay-order-summary {
  padding: 8px 0;
}

.pay-product {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.pay-product-image {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 10px;
}

.pay-product-info h4 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
}

.pay-price {
  font-size: 18px;
  font-weight: 700;
  color: #FF6B6B;
}

.pay-seller {
  font-size: 14px;
  color: var(--c-text-secondary);
  margin-bottom: 16px;
}

.pay-note {
  padding: 12px;
  background: rgba(91,141,239,0.05);
  border-radius: 8px;
  font-size: 13px;
  color: var(--c-text-secondary);
  line-height: 1.6;
}
</style>
