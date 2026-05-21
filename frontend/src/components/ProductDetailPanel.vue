<template>
  <div class="product-detail" :class="{ 'is-modal': modal }" v-loading="loading">
    <div class="detail-scroll" :class="{ 'with-bottom-bar': hasBottomBar }">
      <template v-if="product && !notFound">
        <div class="image-carousel">
          <div
            class="carousel-track"
            :style="{ transform: `translateX(-${currentIndex * 100}%)` }"
            @touchstart="onTouchStart"
            @touchmove="onTouchMove"
            @touchend="onTouchEnd"
          >
            <div v-for="(img, i) in product.images" :key="i" class="carousel-slide">
              <el-image :src="getImageUrl(img)" fit="cover" class="slide-image">
                <template #error>
                  <div class="slide-placeholder">
                    <svg viewBox="0 0 80 80" fill="none" width="80" height="80">
                      <rect x="10" y="16" width="60" height="48" rx="6" stroke="#ccc" stroke-width="2" />
                      <circle cx="28" cy="34" r="6" stroke="#ccc" stroke-width="2" />
                      <path d="M10 56l18-18 14 14 10-10 18 18" stroke="#ccc" stroke-width="2" stroke-linejoin="round" />
                    </svg>
                  </div>
                </template>
              </el-image>
            </div>
          </div>

          <button class="carousel-back" @click="handleClose">
            <svg viewBox="0 0 24 24" fill="none" width="22" height="22" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M19 12H5M12 19l-7-7 7-7" />
            </svg>
          </button>

          <div v-if="product.images.length > 1" class="carousel-dots">
            <span
              v-for="(_, i) in product.images"
              :key="i"
              class="dot"
              :class="{ active: currentIndex === i }"
              @click="currentIndex = i"
            ></span>
          </div>

          <div v-if="product.images.length > 1" class="carousel-counter">
            {{ currentIndex + 1 }} / {{ product.images.length }}
          </div>

          <div v-if="product.is_favorited" class="carousel-fav-badge">
            <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14">
              <path d="M10 17l-6.18 3.25L5 13.35.82 9.28l6.07-.88L10 2.7l3.11 5.7 6.07.88L16 13.35l1.18 6.9z" />
            </svg>
            已收藏
          </div>
        </div>

        <div class="content-card">
          <div class="author-bar">
            <div class="author-info">
              <el-avatar :size="44" :src="product.seller_avatar ? getImageUrl(product.seller_avatar) : undefined" class="author-avatar">
                {{ product.seller_nickname?.[0] }}
              </el-avatar>
              <div class="author-text">
                <div class="author-name">{{ product.seller_nickname }}</div>
                <div class="author-meta">
                  <span class="author-badge">认证校友</span>
                  <span v-if="product.seller_credit_score > 0" class="author-credit">
                    <svg viewBox="0 0 16 16" fill="none" width="12" height="12">
                      <path d="M8 1l2 4 4.5.5-3.2 3 .9 4.5L8 11.5 4.8 13l.9-4.5-3.2-3L7 5l1-4z" fill="#FFD166" stroke="#FFD166" stroke-width="1" />
                    </svg>
                    {{ product.seller_credit_score.toFixed(1) }}
                  </span>
                </div>
              </div>
            </div>
            <button v-if="!isOwner" class="author-contact-btn" @click="contactSeller" :disabled="!userStore.isLoggedIn">
              <svg viewBox="0 0 20 20" fill="none" width="16" height="16" stroke="currentColor" stroke-width="1.8" stroke-linecap="round">
                <path d="M18 2L10 10M18 2l-6 16-2-8-8-2 16-6z" />
              </svg>
              私信
            </button>
          </div>

          <h1 class="product-title">{{ product.title }}</h1>
          <div class="price-row">
            <span class="price">&yen;{{ product.price }}</span>
            <span v-if="product.original_price && product.original_price > product.price" class="original-price">&yen;{{ product.original_price }}</span>
          </div>

          <div class="tag-row">
            <span class="tag tag-cat">{{ product.category }}</span>
            <span class="tag tag-cond">{{ product.condition }}</span>
            <span class="tag tag-time">
              <svg viewBox="0 0 16 16" fill="none" width="12" height="12">
                <circle cx="8" cy="8" r="7" stroke="currentColor" stroke-width="1.5" />
                <path d="M8 4v5l3 2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
              </svg>
              {{ formatDate(product.created_at) }}
            </span>
          </div>

          <div class="desc-section" v-if="product.description">
            <p class="desc-text">{{ product.description }}</p>
          </div>

          <div v-if="isOwner" class="owner-actions">
            <el-button :icon="Edit" round @click="router.push(`/edit-product/${product.id}`)">编辑商品</el-button>
            <el-button v-if="product.status === '上架'" type="warning" round @click="changeStatus('已下架')">下架</el-button>
            <el-button v-else type="success" round @click="changeStatus('上架')">重新上架</el-button>
          </div>
        </div>
      </template>

      <div v-else-if="notFound" class="off-shelf">
        <el-result icon="warning" title="商品已下架" sub-title="该商品可能已被卖家下架或删除">
          <template #extra>
            <el-button type="primary" @click="handleClose">返回首页</el-button>
          </template>
        </el-result>
      </div>
    </div>

    <div v-if="hasBottomBar" class="bottom-bar" :class="{ 'inside-modal': modal }">
      <div class="bottom-bar-inner">
        <button class="bottom-icon-btn" :class="{ active: product.is_favorited }" @click="toggleFav" :disabled="!userStore.isLoggedIn">
          <svg viewBox="0 0 20 20" fill="none" width="22" height="22" stroke="currentColor" stroke-width="1.8">
            <path
              d="M10 17l-6.18 3.25L5 13.35.82 9.28l6.07-.88L10 2.7l3.11 5.7 6.07.88L16 13.35l1.18 6.9z"
              :fill="product.is_favorited ? 'currentColor' : 'none'"
            />
          </svg>
          <span>{{ product.is_favorited ? '已收藏' : '收藏' }}</span>
        </button>
        <button class="bottom-icon-btn" @click="showReportDialog = true" :disabled="!userStore.isLoggedIn">
          <svg viewBox="0 0 20 20" fill="none" width="20" height="20" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M10 18a8 8 0 1 0 0-16 8 8 0 0 0 0 16Z" />
            <path d="M10 6v4" />
            <circle cx="10" cy="13" r="0.5" fill="currentColor" />
          </svg>
          <span>举报</span>
        </button>
        <button class="bottom-btn-contact" @click="contactSeller" :disabled="!userStore.isLoggedIn">联系卖家</button>
        <button class="bottom-btn-buy" @click="handleBuy" :disabled="!userStore.isLoggedIn" :style="{ opacity: userStore.isLoggedIn ? 1 : 0.5 }">立即购买</button>
      </div>
    </div>

    <el-dialog v-model="showReportDialog" title="举报商品" width="480px">
      <el-form :model="reportForm" label-width="80px">
        <el-form-item label="举报类型">
          <el-select v-model="reportForm.report_type" placeholder="选择类型">
            <el-option label="虚假信息" value="虚假信息" />
            <el-option label="违规商品" value="违规商品" />
            <el-option label="诈骗行为" value="诈骗行为" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="举报描述">
          <el-input v-model="reportForm.description" type="textarea" :rows="4" placeholder="请描述举报原因（至少10个字）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showReportDialog = false">取消</el-button>
        <el-button type="primary" @click="handleReport" :loading="reporting">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Edit } from '@element-plus/icons-vue'
import { getProduct, toggleFavorite, updateProductStatus } from '../api/products'
import { createConversation } from '../api/chat'
import { createOrder } from '../api/order'
import { createReport } from '../api/report'
import { useUserStore } from '../store'
import { getUploadUrl } from '../utils/url'
import { useRouter } from 'vue-router'

const props = defineProps({
  productId: {
    type: [String, Number],
    required: true,
  },
  modal: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['close'])

const router = useRouter()
const userStore = useUserStore()

const product = ref(null)
const loading = ref(false)
const notFound = ref(false)
const currentIndex = ref(0)
const showReportDialog = ref(false)
const reporting = ref(false)
const reportForm = ref({ report_type: '其他', description: '' })

const isOwner = computed(() => userStore.user?.id === product.value?.seller_id)
const hasBottomBar = computed(() => Boolean(!isOwner.value && product.value && !notFound.value))

const getImageUrl = (filename) => (filename ? getUploadUrl(filename) : '')

function handleClose() {
  if (props.modal) emit('close')
  else router.back()
}

function formatDate(t) {
  if (!t) return ''
  const d = new Date(t)
  const now = new Date()
  const diff = now - d
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`
  return d.toLocaleDateString('zh-CN')
}

let touchStartX = 0
let touchDeltaX = 0

function onTouchStart(e) {
  touchStartX = e.touches[0].clientX
}

function onTouchMove(e) {
  touchDeltaX = e.touches[0].clientX - touchStartX
}

function onTouchEnd() {
  const imgs = product.value?.images
  if (!imgs?.length) return
  if (touchDeltaX < -40 && currentIndex.value < imgs.length - 1) currentIndex.value += 1
  else if (touchDeltaX > 40 && currentIndex.value > 0) currentIndex.value -= 1
  touchDeltaX = 0
}

async function fetchProduct() {
  if (!props.productId) return
  loading.value = true
  notFound.value = false
  currentIndex.value = 0
  product.value = null
  try {
    const res = await getProduct(props.productId)
    if (res.data.status !== '上架') {
      notFound.value = true
      return
    }
    product.value = res.data
  } catch {
    notFound.value = true
  } finally {
    loading.value = false
  }
}

async function contactSeller() {
  if (!userStore.isLoggedIn) {
    router.push('/login')
    return
  }
  try {
    const res = await createConversation({ product_id: product.value.id, seller_id: product.value.seller_id })
    router.push(`/chat/${res.data.id}`)
  } catch {}
}

async function toggleFav() {
  if (!userStore.isLoggedIn) {
    router.push('/login')
    return
  }
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

async function handleBuy() {
  if (!userStore.isLoggedIn) {
    router.push('/login')
    return
  }
  try {
    const res = await createOrder({ product_id: product.value.id })
    router.push(`/pay/${res.data.id}`)
  } catch (e) {
    console.error(e)
  }
}

async function handleReport() {
  if (reportForm.value.description.length < 10) {
    ElMessage.warning('举报描述至少10个字')
    return
  }
  reporting.value = true
  try {
    await createReport({
      product_id: product.value.id,
      report_type: reportForm.value.report_type,
      description: reportForm.value.description,
    })
    showReportDialog.value = false
    reportForm.value = { report_type: '其他', description: '' }
    ElMessage.success('举报提交成功')
  } catch (e) {
    console.error(e)
  } finally {
    reporting.value = false
  }
}

watch(() => props.productId, fetchProduct, { immediate: true })
</script>

<style scoped>
.product-detail {
  max-width: 640px;
  margin: 0 auto;
  padding-bottom: 80px;
}

.detail-scroll.with-bottom-bar {
  padding-bottom: 0;
}

.product-detail.is-modal {
  position: relative;
  max-width: none;
  width: 100%;
  height: 100%;
  margin: 0;
  padding-bottom: 0;
  display: flex;
  flex-direction: column;
  background: white;
  overflow: hidden;
}

.product-detail.is-modal .detail-scroll {
  flex: 1;
  overflow-y: auto;
  padding-bottom: 88px;
}

.image-carousel {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  background: #f5f6f8;
  margin-bottom: 16px;
}

.product-detail.is-modal .image-carousel {
  border-radius: 0;
}

.carousel-track {
  display: flex;
  overflow: hidden;
  width: 100%;
  aspect-ratio: 1 / 1;
  transition: transform 0.35s cubic-bezier(0.25, 0.8, 0.25, 1.2);
}

.carousel-slide {
  flex: 0 0 100%;
  width: 100%;
}

.slide-image {
  width: 100%;
  height: 100%;
}

.slide-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f8fafc, #eef2f7);
  min-height: 360px;
}

.carousel-back {
  position: absolute;
  top: 12px;
  left: 12px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
  color: #333;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.2s;
  z-index: 2;
}

.carousel-back:hover {
  background: white;
  transform: scale(1.05);
}

.carousel-dots {
  position: absolute;
  bottom: 14px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 6px;
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: all 0.25s;
}

.dot.active {
  width: 18px;
  border-radius: 3px;
  background: white;
}

.carousel-counter {
  position: absolute;
  bottom: 12px;
  right: 12px;
  background: rgba(0, 0, 0, 0.45);
  color: white;
  font-size: 12px;
  padding: 2px 10px;
  border-radius: 12px;
  backdrop-filter: blur(8px);
}

.carousel-fav-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(255, 107, 107, 0.9);
  backdrop-filter: blur(8px);
  color: white;
  padding: 4px 10px;
  border-radius: 14px;
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
  box-shadow: 0 2px 8px rgba(255, 107, 107, 0.3);
}

.content-card {
  background: white;
  border-radius: 16px;
  padding: 20px 24px;
  margin-bottom: 16px;
}

.product-detail.is-modal .content-card {
  margin: 0;
  border-radius: 0;
}

.author-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.author-avatar {
  border: 2px solid #f0f0f0;
  cursor: pointer;
}

.author-name {
  font-size: 15px;
  font-weight: 600;
  color: #222;
}

.author-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 2px;
}

.author-badge {
  font-size: 11px;
  color: #06d6a0;
  background: rgba(6, 214, 160, 0.08);
  padding: 1px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.author-credit {
  font-size: 11px;
  color: #b8860b;
  display: flex;
  align-items: center;
  gap: 2px;
}

.author-contact-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 7px 16px;
  border: 1px solid #e2e2e2;
  border-radius: 20px;
  background: white;
  color: #555;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.author-contact-btn:hover {
  border-color: #5b8def;
  color: #5b8def;
  background: rgba(91, 141, 239, 0.04);
}

.author-contact-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.product-title {
  font-size: 20px;
  font-weight: 700;
  color: #222;
  line-height: 1.4;
  margin-bottom: 12px;
  letter-spacing: -0.2px;
}

.price-row {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 14px;
}

.price {
  font-size: 28px;
  font-weight: 800;
  color: #ff2442;
  letter-spacing: -0.5px;
}

.original-price {
  font-size: 14px;
  color: #999;
  text-decoration: line-through;
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 18px;
}

.tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 5px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 500;
}

.tag-cat {
  background: rgba(91, 141, 239, 0.08);
  color: #5b8def;
}

.tag-cond {
  background: #f5f6f8;
  color: #666;
}

.tag-time {
  background: #f5f6f8;
  color: #999;
}

.desc-section {
  padding-top: 14px;
  border-top: 1px solid #f0f0f0;
}

.desc-text {
  font-size: 15px;
  line-height: 1.75;
  color: #444;
  white-space: pre-wrap;
  word-break: break-word;
}

.owner-actions {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  gap: 10px;
}

.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  border-top: 1px solid #f0f0f0;
  padding: 10px 16px;
  padding-bottom: max(10px, env(safe-area-inset-bottom));
  z-index: 50;
  box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.04);
}

.bottom-bar.inside-modal {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 0 0 24px 24px;
}

.bottom-bar-inner {
  max-width: 640px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 8px;
}

.product-detail.is-modal .bottom-bar-inner {
  max-width: none;
}

.bottom-icon-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 6px 12px;
  border: none;
  background: transparent;
  color: #888;
  font-size: 11px;
  cursor: pointer;
  transition: color 0.2s;
  flex-shrink: 0;
}

.bottom-icon-btn:hover {
  color: #555;
}

.bottom-icon-btn.active {
  color: #ff2442;
}

.bottom-icon-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.bottom-btn-contact {
  flex: 1;
  padding: 11px 0;
  border: 1px solid #5b8def;
  border-radius: 24px;
  background: white;
  color: #5b8def;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.bottom-btn-contact:hover {
  background: rgba(91, 141, 239, 0.04);
}

.bottom-btn-contact:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.bottom-btn-buy {
  flex: 1;
  padding: 11px 0;
  border: none;
  border-radius: 24px;
  background: linear-gradient(135deg, #ff2442, #ff6b6b);
  color: white;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 10px rgba(255, 36, 66, 0.2);
}

.bottom-btn-buy:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(255, 36, 66, 0.3);
}

.bottom-btn-buy:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.off-shelf {
  padding: 80px 0;
  text-align: center;
}

@media (max-width: 900px) {
  .product-detail.is-modal .content-card {
    padding: 18px 18px 12px;
  }
}
</style>
