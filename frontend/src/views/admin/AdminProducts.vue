<template>
  <div class="admin-products-page">
    <h1 class="page-title">商品管理</h1>

    <div class="filters">
      <el-input 
        v-model="search" 
        placeholder="搜索商品标题" 
        clearable 
        @input="fetchProducts"
        style="width: 300px;"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else-if="products.length === 0" class="empty-state">
      <p>暂无商品</p>
    </div>

    <div v-else class="products-table">
      <el-table :data="products" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="商品" min-width="250">
          <template #default="{ row }">
            <div class="product-cell">
              <img :src="productImage(row)" class="product-thumb" />
              <div class="product-info">
                <span class="product-title">{{ row.title }}</span>
                <span class="product-price">¥{{ row.price }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="卖家" width="120">
          <template #default="{ row }">
            {{ row.seller?.nickname || '未知' }}
          </template>
        </el-table-column>
        <el-table-column prop="category" label="分类" width="120" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '在售' : '已下架' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="发布时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewProduct(row)">查看</el-button>
            <el-button 
              size="small" 
              :type="row.status === 'active' ? 'warning' : 'success'"
              @click="toggleProduct(row)"
            >
              {{ row.status === 'active' ? '下架' : '恢复' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getAdminProducts, adminToggleProduct } from '../../api/admin'

const products = ref([])
const loading = ref(true)
const search = ref('')

const baseUrl = 'http://127.0.0.1:5000'

const productImage = (product) => {
  return product.images?.length > 0 
    ? `${baseUrl}/api/uploads/${product.images[0]}`
    : 'https://via.placeholder.com/60x60?text=No'
}

const formatDate = (date) => {
  return new Date(date).toLocaleString('zh-CN')
}

async function fetchProducts() {
  loading.value = true
  try {
    const res = await getAdminProducts({ search: search.value })
    products.value = res.data.products || []
  } catch (error) {
    console.error('Failed to fetch products:', error)
  } finally {
    loading.value = false
  }
}

function viewProduct(product) {
  window.open(`/product/${product.id}`, '_blank')
}

async function toggleProduct(product) {
  try {
    await adminToggleProduct(product.id)
    ElMessage.success(product.status === 'active' ? '已下架' : '已恢复')
    fetchProducts()
  } catch (error) {
    console.error('Failed to toggle product:', error)
  }
}

onMounted(() => {
  fetchProducts()
})
</script>

<style scoped>
.admin-products-page {
  max-width: 1200px;
  margin: 0 auto;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--c-text);
  margin-bottom: 24px;
}

.filters {
  margin-bottom: 24px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
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
  padding: 60px 20px;
  text-align: center;
  color: var(--c-text-muted);
}

.products-table {
  background: var(--c-surface);
  border-radius: 16px;
  padding: 20px;
  box-shadow: var(--c-shadow-md);
}

.product-cell {
  display: flex;
  gap: 12px;
  align-items: center;
}

.product-thumb {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 8px;
}

.product-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.product-title {
  font-weight: 600;
  color: var(--c-text);
}

.product-price {
  font-size: 14px;
  color: var(--c-accent);
  font-weight: 600;
}
</style>
