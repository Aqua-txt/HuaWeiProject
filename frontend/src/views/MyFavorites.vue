<template>
  <div class="favorites-page">
    <div class="section-card">
      <div class="section-header">
        <router-link to="/home" class="home-link">
          <el-button type="primary" round size="small">回到主页</el-button>
        </router-link>
        <h2>我的收藏</h2>
      </div>
      <div v-if="products.length > 0" class="product-grid">
        <article v-for="(p, i) in products" :key="p.id" class="product-card"
          :style="{ animationDelay: `${i * 0.05}s` }"
          @click="openFavoriteProduct(p.id)">
          <div class="card-img">
            <el-image :src="getImageUrl(p.images[0])" fit="cover" class="card-image">
              <template #error>
                <div class="img-fb">
                  <svg viewBox="0 0 32 32" fill="none" width="32" height="32">
                    <rect x="4" y="6" width="24" height="20" rx="3" stroke="#c0c4cc" stroke-width="1.5"/>
                    <circle cx="11" cy="13" r="2" stroke="#c0c4cc" stroke-width="1.5"/>
                    <path d="M4 22l8-8 6 6 4-4 6 6" stroke="#c0c4cc" stroke-width="1.5" stroke-linejoin="round"/>
                  </svg>
                </div>
              </template>
            </el-image>
            <span class="card-price">&yen;{{ p.price }}</span>
            <span class="fav-indicator">
              <svg viewBox="0 0 16 16" width="12" height="12" fill="#FF6B6B">
                <path d="M8 14l-4.94 2.6L4 10.68.66 7.42l4.86-.7L8 1.62l2.48 5.1 4.86.7L12 10.68l1.06 5.92z"/>
              </svg>
            </span>
          </div>
          <div class="card-body">
            <h3 class="card-title">{{ p.title }}</h3>
            <div class="card-meta">
              <span class="meta-tag">{{ p.category }}</span>
              <span>{{ p.condition }}</span>
            </div>
          </div>
        </article>
      </div>
      <div v-else class="empty-state">
        <svg viewBox="0 0 80 60" fill="none" width="80" height="60">
          <path d="M40 5C25 5 12 18 12 30s13 20 28 20c5 0 10-1 14-3l14 5-4-13c2-3 3-6 3-9 0-12-12-25-27-25z" stroke="#d0d5dd" stroke-width="2"/>
          <text x="40" y="70" text-anchor="middle" font-size="11" fill="#d0d5dd">还没有收藏的商品</text>
        </svg>
        <p>去首页逛逛吧</p>
        <router-link to="/home"><el-button type="primary" round size="small">发现好物</el-button></router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getFavorites } from '../api/products'
import { getUploadUrl } from '../utils/url'

const router = useRouter()
const products = ref([])

function getImageUrl(img) {
  return img ? getUploadUrl(img) : ''
}

async function fetchFavorites() {
  try {
    const res = await getFavorites({ per_page: 50 })
    products.value = res.data.products
  } catch {}
}

function openFavoriteProduct(productId) {
  router.push({
    path: '/home',
    query: { product: String(productId) },
  })
}

onMounted(() => { fetchFavorites() })
</script>

<style scoped>
.favorites-page {
  max-width: 920px;
  margin: 0 auto;
  padding-top: 24px;
  animation: fadeInUp 0.4s ease;
}

.section-card {
  background: white;
  border-radius: 20px;
  padding: 24px;
  margin-top: 12px;
  box-shadow: 0 2px 20px rgba(26,35,50,0.04);
  border: 1px solid rgba(0,0,0,0.03);
}

.section-header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 20px;
}

.home-link {
  flex-shrink: 0;
  text-decoration: none;
}

.section-card h2 {
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 700;
  margin: 0;
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
@media (max-width: 900px) { .product-grid { grid-template-columns: repeat(3, 1fr); } }
@media (max-width: 600px) { .product-grid { grid-template-columns: repeat(2, 1fr); } }

.product-card {
  background: white;
  border-radius: 14px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid var(--c-border);
  animation: fadeInUp 0.4s ease both;
}

.product-card:hover {
  box-shadow: 0 6px 24px rgba(91,141,239,0.1);
  transform: translateY(-3px);
  border-color: rgba(91,141,239,0.15);
}

.card-img {
  position: relative;
  height: 160px;
  background: var(--c-surface-alt);
}

.card-image { width: 100%; height: 100%; }

.img-fb {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f8fafc, #eef2f7);
}

.card-price {
  position: absolute;
  bottom: 8px;
  left: 8px;
  background: rgba(26,35,50,0.78);
  backdrop-filter: blur(8px);
  color: white;
  padding: 2px 10px;
  border-radius: 14px;
  font-size: 14px;
  font-weight: 700;
}

.fav-indicator {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(255,255,255,0.85);
  backdrop-filter: blur(8px);
  width: 26px;
  height: 26px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-body { padding: 12px; }

.card-title {
  font-size: 14px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 6px;
}

.card-meta {
  font-size: 12px;
  color: var(--c-text-muted);
  display: flex;
  gap: 8px;
  align-items: center;
}

.meta-tag {
  background: var(--c-primary-light);
  color: var(--c-primary);
  padding: 1px 7px;
  border-radius: 6px;
  font-weight: 500;
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

@media (max-width: 600px) {
  .favorites-page {
    padding-top: 16px;
  }

  .section-card {
    margin-top: 8px;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>
