<template>
  <div class="my-products-page">
    <div class="section-card">
      <div class="section-header">
        <button class="back-btn" @click="$router.back()" title="返回">
          <svg viewBox="0 0 24 24" fill="none" width="18" height="18" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
        </button>
        <h2>我的发布</h2>
        <el-tabs v-model="activeTab" @tab-change="fetchProducts" class="status-tabs">
          <el-tab-pane name="上架">
            <template #label><span class="tab-dot dot-active"></span>在售</template>
          </el-tab-pane>
          <el-tab-pane name="已下架">
            <template #label><span class="tab-dot dot-off"></span>已下架</template>
          </el-tab-pane>
        </el-tabs>
      </div>

      <div v-if="products.length > 0" class="product-list">
        <div v-for="p in products" :key="p.id" class="product-row"
          @click="$router.push(`/product/${p.id}`)">
          <div class="row-img">
            <el-image :src="getImageUrl(p.images[0])" fit="cover" class="row-thumb">
              <template #error>
                <div class="row-thumb-fb">
                  <svg viewBox="0 0 32 32" fill="none" width="28" height="28">
                    <rect x="4" y="6" width="24" height="20" rx="3" stroke="#c0c4cc" stroke-width="1.5"/>
                    <circle cx="11" cy="13" r="2" stroke="#c0c4cc" stroke-width="1.5"/>
                    <path d="M4 22l8-8 6 6 4-4 6 6" stroke="#c0c4cc" stroke-width="1.5" stroke-linejoin="round"/>
                  </svg>
                </div>
              </template>
            </el-image>
            <span class="row-status" :class="p.status === '上架' ? 'on' : 'off'">
              {{ p.status === '上架' ? '在售' : '已下架' }}
            </span>
          </div>
          <div class="row-info">
            <div class="row-title">{{ p.title }}</div>
            <div class="row-meta">
              <span class="row-price">&yen;{{ p.price }}</span>
              <span class="meta-sep">·</span>
              <span>{{ p.category }}</span>
              <span class="meta-sep">·</span>
              <span>{{ p.condition }}</span>
              <span class="meta-sep">·</span>
              <span>{{ formatDate(p.created_at) }}</span>
            </div>
          </div>
          <div class="row-actions" @click.stop>
            <el-button size="small" round @click="$router.push(`/edit-product/${p.id}`)">编辑</el-button>
            <el-button v-if="p.status === '上架'" size="small" type="warning" round @click="changeStatus(p, '已下架')">
              下架
            </el-button>
            <el-button v-else size="small" type="success" round @click="changeStatus(p, '上架')">
              重新上架
            </el-button>
          </div>
        </div>
      </div>

      <div v-else class="empty-state">
        <svg viewBox="0 0 80 60" fill="none" width="80" height="60">
          <rect x="15" y="8" width="50" height="40" rx="8" stroke="#d0d5dd" stroke-width="2"/>
          <line x1="28" y1="28" x2="52" y2="28" stroke="#d0d5dd" stroke-width="2" stroke-linecap="round"/>
          <line x1="32" y1="34" x2="48" y2="34" stroke="#d0d5dd" stroke-width="2" stroke-linecap="round"/>
          <text x="40" y="68" text-anchor="middle" font-size="11" fill="#d0d5dd">暂无商品</text>
        </svg>
        <p>还没有发布过商品</p>
        <router-link to="/publish"><el-button type="primary" round size="small">去发布</el-button></router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getMyProducts } from '../api/user'
import { updateProductStatus } from '../api/products'
import { ElMessage } from 'element-plus'
import { getUploadUrl } from '../utils/url'

const products = ref([])
const activeTab = ref('上架')

function getImageUrl(img) {
  return img ? getUploadUrl(img) : ''
}

function formatDate(t) {
  if (!t) return ''
  return new Date(t).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

async function fetchProducts() {
  try {
    const res = await getMyProducts({ status: activeTab.value })
    products.value = res.data.products
  } catch {}
}

async function changeStatus(p, status) {
  try {
    await updateProductStatus(p.id, status)
    ElMessage.success(status === '已下架' ? '已下架' : '已重新上架')
    fetchProducts()
  } catch {}
}

onMounted(() => { fetchProducts() })
</script>

<style scoped>
.my-products-page {
  max-width: 760px;
  margin: 24px auto 0;
  animation: fadeInUp 0.4s ease;
}

.section-card {
  background: white;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 2px 20px rgba(26,35,50,0.04);
  border: 1px solid rgba(0,0,0,0.03);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.section-header h2 {
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 700;
}

.tab-dot {
  display: inline-block;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  margin-right: 5px;
}
.dot-active { background: var(--c-secondary); }
.dot-off { background: var(--c-text-muted); }

.product-row {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 0;
  border-bottom: 1px solid rgba(0,0,0,0.04);
  cursor: pointer;
  transition: background 0.2s;
}

.product-row:hover { background: var(--c-surface-alt); border-radius: 12px; padding-left: 8px; padding-right: 8px; }

.row-img { position: relative; flex-shrink: 0; }

.row-thumb {
  width: 80px;
  height: 80px;
  border-radius: 12px;
}

.row-thumb-fb {
  width: 80px;
  height: 80px;
  background: var(--c-surface-alt);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.row-status {
  position: absolute;
  bottom: 4px;
  left: 4px;
  font-size: 10px;
  font-weight: 600;
  padding: 1px 7px;
  border-radius: 8px;
}

.row-status.on { background: rgba(6,214,160,0.15); color: var(--c-secondary); }
.row-status.off { background: rgba(0,0,0,0.05); color: var(--c-text-muted); }

.row-info { flex: 1; min-width: 0; }

.row-title {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.row-meta {
  font-size: 13px;
  color: var(--c-text-muted);
  display: flex;
  align-items: center;
  gap: 2px;
  flex-wrap: wrap;
}

.row-price {
  color: #FF6B6B;
  font-weight: 600;
}

.meta-sep { margin: 0 2px; }

.row-actions {
  flex-shrink: 0;
  display: flex;
  gap: 6px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 40px 20px;
  color: var(--c-text-muted);
  font-size: 14px;
}
</style>
