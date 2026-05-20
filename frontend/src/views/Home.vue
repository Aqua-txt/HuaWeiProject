<template>
  <div class="home">
    <!-- Hero / Search -->
    <div class="search-hero">
      <div class="search-glow"></div>
      <h1 class="hero-title">发现身边的<span class="highlight">好物</span></h1>
      <p class="hero-sub">教材、数码、生活用品 — 在校园集市找到你需要的</p>
      <div class="search-box">
        <el-input v-model="keyword" placeholder="搜索商品..." size="large" clearable
          :prefix-icon="Search" @keyup.enter="doSearch" @clear="doSearch"
          class="search-input" />
      </div>
    </div>

    <!-- Filters -->
    <div class="filter-bar">
      <div class="filter-cats">
        <button v-for="cat in categories" :key="cat.value"
          class="cat-chip" :class="{ active: category === cat.value }"
          @click="category = cat.value; doSearch()">
          <span class="cat-emoji">{{ cat.emoji }}</span>
          {{ cat.label }}
        </button>
      </div>
      <el-select v-model="sort" style="width:168px" @change="doSearch" class="sort-select">
        <el-option label="最新发布" value="latest" />
        <el-option label="价格从低到高" value="price_asc" />
        <el-option label="价格从高到低" value="price_desc" />
      </el-select>
    </div>

    <!-- Product Grid -->
    <div v-if="products.length > 0" class="product-grid">
      <article v-for="(p, i) in products" :key="p.id" class="product-card"
        :style="{ animationDelay: `${i * 0.04}s` }"
        @click="$router.push(`/product/${p.id}`)">
        <div class="card-img">
          <el-image :src="getImageUrl(p.images[0])" fit="cover" class="card-image">
            <template #error>
              <div class="img-placeholder">
                <svg viewBox="0 0 48 48" fill="none" width="48" height="48">
                  <rect x="6" y="10" width="36" height="28" rx="4" stroke="#c0c4cc" stroke-width="2"/>
                  <circle cx="16" cy="20" r="3" stroke="#c0c4cc" stroke-width="2"/>
                  <path d="M6 32l10-10 8 8 6-6 12 12" stroke="#c0c4cc" stroke-width="2" stroke-linejoin="round"/>
                </svg>
              </div>
            </template>
          </el-image>
          <span class="card-price">&yen;{{ p.price }}</span>
          <span class="card-category-tag">{{ p.category }}</span>
        </div>
        <div class="card-body">
          <h3 class="card-title">{{ p.title }}</h3>
          <div class="card-meta">
            <span class="meta-condition">{{ p.condition }}</span>
          </div>
          <div class="card-footer">
            <span class="card-seller">
              <el-avatar :size="22" :src="getAvatarUrl(p.seller_avatar)" />
              {{ p.seller_nickname }}
            </span>
            <span class="card-time">{{ formatTime(p.created_at) }}</span>
          </div>
        </div>
      </article>
    </div>

    <!-- Empty -->
    <div v-else class="empty-state">
      <div class="empty-illustration">
        <svg viewBox="0 0 120 100" fill="none" width="120" height="100">
          <rect x="20" y="10" width="80" height="60" rx="8" stroke="#c0c4cc" stroke-width="2" stroke-dasharray="6 4"/>
          <circle cx="48" cy="40" r="10" stroke="#c0c4cc" stroke-width="2"/>
          <path d="M68 50l8-8 6 6 10-10" stroke="#c0c4cc" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <text x="60" y="92" text-anchor="middle" font-size="12" fill="#c0c4cc">{{ keyword ? '未找到相关商品' : '还没有商品' }}</text>
        </svg>
      </div>
      <p class="empty-text">{{ keyword ? '换个关键词试试吧' : '快来发布第一个商品吧' }}</p>
      <router-link to="/publish" v-if="!keyword">
        <el-button type="primary" size="large" round>发布商品</el-button>
      </router-link>
    </div>

    <!-- Pagination -->
    <div v-if="total > perPage" class="pagination-wrap">
      <el-pagination background layout="prev, pager, next" :total="total"
        :page-size="perPage" :current-page="page" @current-change="onPageChange" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { getProducts } from '../api/products'

const baseUrl = 'http://127.0.0.1:5000'

const products = ref([])
const keyword = ref('')
const category = ref('')
const sort = ref('latest')
const page = ref(1)
const perPage = ref(12)
const total = ref(0)

const categories = [
  { value: '', label: '全部', emoji: '🏠' },
  { value: '教材', label: '教材', emoji: '📚' },
  { value: '数码', label: '数码', emoji: '💻' },
  { value: '生活', label: '生活', emoji: '🏠' },
  { value: '其他', label: '其他', emoji: '📦' },
]

function getImageUrl(img) {
  return img ? `${baseUrl}/api/uploads/${img}` : ''
}

function getAvatarUrl(avatar) {
  return avatar ? `${baseUrl}/api/uploads/${avatar}` : ''
}

function formatTime(t) {
  if (!t) return ''
  const d = new Date(t)
  const now = new Date()
  const diff = now - d
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`
  return d.toLocaleDateString()
}

async function fetchProducts() {
  try {
    const res = await getProducts({
      page: page.value,
      per_page: perPage.value,
      keyword: keyword.value,
      category: category.value,
      sort: sort.value,
    })
    products.value = res.data.products
    total.value = res.data.total
  } catch {}
}

function doSearch() {
  page.value = 1
  fetchProducts()
}

function onPageChange(p) {
  page.value = p
  fetchProducts()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(() => { fetchProducts() })
</script>

<style scoped>
/* Hero */
.search-hero {
  text-align: center;
  padding: 32px 0 24px;
  position: relative;
}

.search-glow {
  position: absolute;
  width: 300px;
  height: 300px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(91,141,239,0.08) 0%, transparent 70%);
  top: -80px;
  left: 50%;
  transform: translateX(-50%);
  pointer-events: none;
}

.hero-title {
  font-family: var(--font-display);
  font-size: 32px;
  font-weight: 800;
  color: var(--c-text);
  margin-bottom: 8px;
  letter-spacing: -0.5px;
}

.hero-title .highlight {
  background: linear-gradient(135deg, #5B8DEF, #06D6A0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-sub {
  font-size: 15px;
  color: var(--c-text-muted);
  margin-bottom: 24px;
}

.search-box {
  max-width: 520px;
  margin: 0 auto;
}

.search-input :deep(.el-input__wrapper) {
  border-radius: 28px !important;
  padding: 6px 18px;
  background: white;
  box-shadow: 0 2px 16px rgba(91,141,239,0.08) !important;
  border: 2px solid transparent;
  transition: all 0.3s;
}

.search-input :deep(.el-input__wrapper:hover) {
  border-color: rgba(91,141,239,0.2);
  box-shadow: 0 4px 20px rgba(91,141,239,0.12) !important;
}

.search-input :deep(.el-input.is-focus .el-input__wrapper) {
  border-color: var(--c-primary) !important;
  box-shadow: 0 4px 24px rgba(91,141,239,0.18) !important;
}

/* Filter bar */
.filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-cats {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.cat-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 8px 18px;
  border-radius: 24px;
  border: 1.5px solid var(--c-border);
  background: white;
  color: var(--c-text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.25s;
}

.cat-chip:hover {
  border-color: var(--c-primary);
  color: var(--c-primary);
  background: var(--c-primary-light);
}

.cat-chip.active {
  background: var(--c-primary);
  border-color: var(--c-primary);
  color: white;
  box-shadow: 0 2px 10px rgba(91,141,239,0.25);
}

.cat-emoji { font-size: 15px; }

.sort-select :deep(.el-input__wrapper) {
  border-radius: 24px !important;
}

/* Product Grid */
.product-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 18px;
}

@media (max-width: 1000px) { .product-grid { grid-template-columns: repeat(3, 1fr); } }
@media (max-width: 700px) { .product-grid { grid-template-columns: repeat(2, 1fr); } }

.product-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 1px 4px rgba(26,35,50,0.04);
  border: 1px solid rgba(0,0,0,0.04);
  animation: fadeInUp 0.5s ease both;
}

.product-card:hover {
  box-shadow: 0 8px 30px rgba(91,141,239,0.1);
  transform: translateY(-4px);
  border-color: rgba(91,141,239,0.1);
}

.card-img {
  position: relative;
  width: 100%;
  height: 200px;
  background: #f0f4f8;
}

.card-image {
  width: 100%;
  height: 100%;
}

.img-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f8fafc, #eef2f7);
}

.card-price {
  position: absolute;
  bottom: 10px;
  left: 10px;
  background: rgba(26,35,50,0.78);
  backdrop-filter: blur(8px);
  color: white;
  padding: 3px 12px;
  border-radius: 16px;
  font-size: 15px;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.card-category-tag {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(255,255,255,0.88);
  backdrop-filter: blur(8px);
  color: var(--c-primary);
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}

.card-body {
  padding: 14px;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--c-text);
}

.card-meta {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
}

.meta-condition {
  font-size: 11px;
  color: var(--c-text-muted);
  background: var(--c-surface-alt);
  padding: 2px 8px;
  border-radius: 6px;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-seller {
  font-size: 12px;
  color: var(--c-text-secondary);
  display: flex;
  align-items: center;
  gap: 5px;
}

.card-time {
  font-size: 11px;
  color: var(--c-text-muted);
}

/* Empty */
.empty-state {
  text-align: center;
  padding: 80px 20px;
}

.empty-illustration { margin-bottom: 16px; }

.empty-text {
  font-size: 15px;
  color: var(--c-text-muted);
  margin-bottom: 24px;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 32px;
  padding-bottom: 20px;
}
</style>
