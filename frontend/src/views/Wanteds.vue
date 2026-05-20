<template>
  <div class="wanteds-page">
    <div class="page-header">
      <h1 class="page-title">求购专区</h1>
      <button class="btn-publish" @click="$router.push('/wanted/publish')">
        <svg viewBox="0 0 24 24" fill="none" width="18" height="18" stroke="currentColor" stroke-width="2.5">
          <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        发布求购
      </button>
    </div>

    <div class="filters">
      <el-select v-model="category" placeholder="全部分类" clearable @change="fetchWanteds">
        <el-option label="全部分类" value="" />
        <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
      </el-select>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else-if="wanteds.length === 0" class="empty-state">
      <svg viewBox="0 0 64 64" fill="none" width="80" height="80">
        <circle cx="32" cy="32" r="28" stroke="#E3E8EF" stroke-width="3" stroke-dasharray="4 4"/>
        <path d="M20 32h24M32 20v24" stroke="#98A8B8" stroke-width="3" stroke-linecap="round"/>
      </svg>
      <h3>暂无求购信息</h3>
      <p>发布您的求购,让有货的同学找到你</p>
      <button class="btn-primary" @click="$router.push('/wanted/publish')">发布求购</button>
    </div>

    <div v-else class="wanteds-grid">
      <div v-for="wanted in wanteds" :key="wanted.id" class="wanted-card" @click="goToDetail(wanted.id)">
        <div class="wanted-header">
          <el-avatar :size="36" :src="userAvatar(wanted.user)">{{ wanted.user?.nickname?.[0] }}</el-avatar>
          <div class="user-info">
            <span class="user-name">{{ wanted.user?.nickname }}</span>
            <span class="post-time">{{ formatDate(wanted.created_at) }}</span>
          </div>
          <el-tag v-if="wanted.status === 'closed'" size="small" type="info">已关闭</el-tag>
        </div>
        <h3 class="wanted-title">{{ wanted.title }}</h3>
        <p class="wanted-desc">{{ wanted.description }}</p>
        <div class="wanted-meta">
          <div class="meta-item">
            <span class="meta-label">预算</span>
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
        <div class="wanted-footer">
          <span class="response-count">{{ wanted.response_count || 0 }} 人响应</span>
          <button v-if="wanted.status === 'active'" class="btn-respond" @click.stop="openRespondDialog(wanted)">
            我有货
          </button>
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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getWanteds, respondToWanted } from '../api/wanted'
import { getMyProducts } from '../api/products'

const router = useRouter()
const wanteds = ref([])
const loading = ref(true)
const category = ref('')
const respondDialogVisible = ref(false)
const selectedWanted = ref(null)
const myProducts = ref([])

const respondForm = reactive({
  price: 0,
  message: '',
  product_id: null,
})

const baseUrl = 'http://127.0.0.1:5000'

const categories = [
  '数码电子', '图书教材', '生活用品', '服装配饰', 
  '运动户外', '美妆护肤', '食品零食', '其他'
]

const userAvatar = (user) => {
  return user?.avatar ? `${baseUrl}/api/uploads/${user.avatar}` : ''
}

const formatDate = (date) => {
  const now = new Date()
  const d = new Date(date)
  const diff = now - d
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)} 天前`
  return d.toLocaleDateString('zh-CN')
}

async function fetchWanteds() {
  loading.value = true
  try {
    const res = await getWanteds({ category: category.value })
    wanteds.value = res.data.wanteds || []
  } catch (error) {
    console.error('Failed to fetch wanteds:', error)
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

function goToDetail(id) {
  router.push(`/wanted/${id}`)
}

function openRespondDialog(wanted) {
  const token = localStorage.getItem('token')
  if (!token) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  selectedWanted.value = wanted
  respondForm.price = wanted.budget_max
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
    await respondToWanted(selectedWanted.value.id, respondForm)
    ElMessage.success('响应已发送')
    respondDialogVisible.value = false
    fetchWanteds()
  } catch (error) {
    console.error('Failed to respond:', error)
  }
}

onMounted(() => {
  fetchWanteds()
})
</script>

<style scoped>
.wanteds-page {
  max-width: 900px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--c-text);
}

.btn-publish {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
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

.btn-publish:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(91,141,239,0.4);
}

.filters {
  margin-bottom: 24px;
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

.wanteds-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.wanted-card {
  background: var(--c-surface);
  border-radius: 16px;
  padding: 20px;
  box-shadow: var(--c-shadow-md);
  cursor: pointer;
  transition: all 0.25s;
  animation: fadeInUp 0.4s ease-out;
}

.wanted-card:hover {
  transform: translateY(-4px);
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

.wanted-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.user-info {
  flex: 1;
}

.user-name {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: var(--c-text);
}

.post-time {
  font-size: 12px;
  color: var(--c-text-muted);
}

.wanted-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--c-text);
  margin-bottom: 12px;
  line-height: 1.4;
}

.wanted-desc {
  font-size: 14px;
  color: var(--c-text-secondary);
  line-height: 1.6;
  margin-bottom: 16px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.wanted-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
  padding: 12px;
  background: var(--c-surface-alt);
  border-radius: 10px;
}

.meta-item {
  flex: 1;
  min-width: 100px;
}

.meta-label {
  display: block;
  font-size: 12px;
  color: var(--c-text-muted);
  margin-bottom: 4px;
}

.meta-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--c-text);
}

.wanted-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid var(--c-border);
}

.response-count {
  font-size: 13px;
  color: var(--c-text-muted);
}

.btn-respond {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  background: var(--c-secondary);
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-respond:hover {
  background: #05B894;
  transform: translateY(-1px);
}
</style>
