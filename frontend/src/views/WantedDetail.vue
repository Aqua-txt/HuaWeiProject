<template>
  <div class="wanted-detail-page">
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <template v-else-if="wanted">
      <div class="page-header">
        <button class="back-btn" @click="$router.back()">
          <svg viewBox="0 0 24 24" fill="none" width="20" height="20" stroke="currentColor" stroke-width="2">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          返回
        </button>
        <h1 class="page-title">求购详情</h1>
      </div>

      <div class="detail-card">
        <div class="wanted-header">
          <el-avatar :size="48" :src="userAvatar">{{ wanted.user?.nickname?.[0] }}</el-avatar>
          <div class="user-info">
            <span class="user-name">{{ wanted.user?.nickname }}</span>
            <span class="post-time">{{ formatDate(wanted.created_at) }}</span>
          </div>
          <el-tag v-if="wanted.status === 'closed'" type="info">已关闭</el-tag>
        </div>

        <h2 class="wanted-title">{{ wanted.title }}</h2>
        <p class="wanted-desc">{{ wanted.description }}</p>

        <div class="wanted-meta">
          <div class="meta-item">
            <span class="meta-label">预算范围</span>
            <span class="meta-value">¥{{ wanted.budget_min }} - ¥{{ wanted.budget_max }}</span>
          </div>
          <div v-if="wanted.category" class="meta-item">
            <span class="meta-label">分类</span>
            <span class="meta-value">{{ wanted.category }}</span>
          </div>
          <div v-if="wanted.desired_condition" class="meta-item">
            <span class="meta-label">期望成色</span>
            <span class="meta-value">{{ wanted.desired_condition }}</span>
          </div>
        </div>

        <div class="action-section">
          <button v-if="wanted.status === 'active'" class="btn-primary" @click="openRespondDialog">
            我有货,响应求购
          </button>
        </div>
      </div>

      <div v-if="responses.length > 0" class="responses-section">
        <h3 class="section-title">响应记录</h3>
        <div class="responses-list">
          <div v-for="response in responses" :key="response.id" class="response-item">
            <div class="response-header">
              <el-avatar :size="36" :src="responderAvatar(response)">{{ response.responder?.nickname?.[0] }}</el-avatar>
              <span class="responder-name">{{ response.responder?.nickname }}</span>
              <span class="response-time">{{ formatDate(response.created_at) }}</span>
            </div>
            <div class="response-content">
              <div class="response-price">报价: ¥{{ response.price_offer }}</div>
              <p class="response-message">{{ response.message }}</p>
              <div v-if="response.product" class="response-product">
                <span>关联商品: </span>
                <router-link :to="`/product/${response.product.id}`">{{ response.product.title }}</router-link>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="relatedProducts.length > 0" class="related-section">
        <h3 class="section-title">相关在售商品</h3>
        <div class="related-grid">
          <div 
            v-for="product in relatedProducts" 
            :key="product.id" 
            class="related-card"
            @click="$router.push(`/product/${product.id}`)"
          >
            <img :src="productImage(product)" class="related-image" />
            <div class="related-info">
              <h4 class="related-title">{{ product.title }}</h4>
              <p class="related-price">¥{{ product.price }}</p>
            </div>
          </div>
        </div>
      </div>

      <el-dialog v-model="respondDialogVisible" title="响应求购" width="500px">
        <el-form :model="respondForm" label-width="80px">
          <el-form-item label="报价">
            <el-input-number v-model="respondForm.price" :min="0" :precision="2" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="留言">
            <el-input v-model="respondForm.message" type="textarea" :rows="3" placeholder="介绍一下您的东西~" />
          </el-form-item>
          <el-form-item label="关联商品">
            <el-select v-model="respondForm.product_id" placeholder="可选,关联您的在售商品" clearable style="width: 100%;">
              <el-option v-for="p in myProducts" :key="p.id" :label="p.title" :value="p.id" />
            </el-select>
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="respondDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitRespond">提交响应</el-button>
        </template>
      </el-dialog>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getWantedById, respondToWanted } from '../api/wanted'
import { getMyProducts } from '../api/products'

const route = useRoute()
const router = useRouter()
const wanted = ref(null)
const responses = ref([])
const relatedProducts = ref([])
const loading = ref(true)
const respondDialogVisible = ref(false)
const myProducts = ref([])

const respondForm = reactive({
  price: 0,
  message: '',
  product_id: null,
})

const baseUrl = 'http://127.0.0.1:5000'

const userAvatar = computed(() => {
  return wanted.value?.user?.avatar ? `${baseUrl}/api/uploads/${wanted.value.user.avatar}` : ''
})

const responderAvatar = (response) => {
  return response.responder?.avatar ? `${baseUrl}/api/uploads/${response.responder.avatar}` : ''
}

const productImage = (product) => {
  return product.images?.length > 0 
    ? `${baseUrl}/api/uploads/${product.images[0]}`
    : 'https://via.placeholder.com/120x120?text=No+Image'
}

const formatDate = (date) => {
  return new Date(date).toLocaleString('zh-CN', {
    month: 'numeric',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

async function fetchWanted() {
  loading.value = true
  try {
    const res = await getWantedById(route.params.id)
    wanted.value = res.data.wanted
    responses.value = res.data.responses || []
    relatedProducts.value = res.data.related_products || []
  } catch (error) {
    console.error('Failed to fetch wanted:', error)
  } finally {
    loading.value = false
  }
}

async function fetchMyProducts() {
  try {
    const res = await getMyProducts()
    myProducts.value = res.data.products || []
  } catch (error) {
    console.error('Failed to fetch my products:', error)
  }
}

function openRespondDialog() {
  const token = localStorage.getItem('token')
  if (!token) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  respondForm.price = wanted.value.budget_max
  respondForm.message = ''
  respondForm.product_id = null
  respondDialogVisible.value = true
  fetchMyProducts()
}

async function submitRespond() {
  if (!respondForm.message.trim()) {
    ElMessage.warning('请填写留言')
    return
  }
  try {
    await respondToWanted(wanted.value.id, respondForm)
    ElMessage.success('响应已发送')
    respondDialogVisible.value = false
    fetchWanted()
  } catch (error) {
    console.error('Failed to respond:', error)
  }
}

onMounted(() => {
  fetchWanted()
})
</script>

<style scoped>
.wanted-detail-page {
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

.detail-card {
  background: var(--c-surface);
  border-radius: 20px;
  padding: 32px;
  box-shadow: var(--c-shadow-lg);
  margin-bottom: 32px;
}

.wanted-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.user-info {
  flex: 1;
}

.user-name {
  display: block;
  font-size: 16px;
  font-weight: 600;
  color: var(--c-text);
}

.post-time {
  font-size: 13px;
  color: var(--c-text-muted);
}

.wanted-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--c-text);
  margin-bottom: 16px;
  line-height: 1.4;
}

.wanted-desc {
  font-size: 15px;
  color: var(--c-text-secondary);
  line-height: 1.8;
  margin-bottom: 24px;
}

.wanted-meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  padding: 20px;
  background: var(--c-surface-alt);
  border-radius: 12px;
  margin-bottom: 24px;
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.meta-label {
  font-size: 13px;
  color: var(--c-text-muted);
}

.meta-value {
  font-size: 16px;
  font-weight: 600;
  color: var(--c-text);
}

.action-section {
  display: flex;
  justify-content: center;
  padding-top: 16px;
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

.responses-section,
.related-section {
  margin-bottom: 32px;
}

.section-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--c-text);
  margin-bottom: 20px;
}

.responses-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.response-item {
  background: var(--c-surface);
  border-radius: 16px;
  padding: 20px;
  box-shadow: var(--c-shadow-md);
}

.response-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.responder-name {
  flex: 1;
  font-weight: 600;
  color: var(--c-text);
}

.response-time {
  font-size: 13px;
  color: var(--c-text-muted);
}

.response-content {
  padding-left: 48px;
}

.response-price {
  font-size: 18px;
  font-weight: 700;
  color: var(--c-accent);
  margin-bottom: 12px;
}

.response-message {
  font-size: 14px;
  color: var(--c-text-secondary);
  line-height: 1.6;
  margin-bottom: 12px;
}

.response-product {
  font-size: 14px;
  color: var(--c-text-muted);
}

.response-product a {
  color: var(--c-primary);
  font-weight: 500;
}

.related-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.related-card {
  background: var(--c-surface);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: var(--c-shadow-sm);
}

.related-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--c-shadow-md);
}

.related-image {
  width: 100%;
  height: 120px;
  object-fit: cover;
}

.related-info {
  padding: 12px;
}

.related-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--c-text);
  margin-bottom: 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.related-price {
  font-size: 16px;
  font-weight: 700;
  color: var(--c-accent);
}
</style>
