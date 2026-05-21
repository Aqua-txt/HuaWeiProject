<template>
  <div class="wanteds-page">
    <div class="page-header">
      <h1 class="page-title">求购专区</h1>
      <div class="header-actions">
        <button class="btn-back-home" @click="$router.push('/home')">
          <svg viewBox="0 0 24 24" fill="none" width="18" height="18" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M15 18l-6-6 6-6" />
          </svg>
          返回主页
        </button>
        <button class="btn-publish" @click="openPublishModal">
          <svg viewBox="0 0 24 24" fill="none" width="18" height="18" stroke="currentColor" stroke-width="2.5">
            <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          发布求购
        </button>
      </div>
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
      <button class="btn-primary" @click="openPublishModal">发布求购</button>
    </div>

    <div v-else class="wanteds-cloud-board">
      <div
        v-for="(wanted, index) in wanteds"
        :key="wanted.id"
        class="cloud-wanted-item"
        :class="[
          `cloud-size-${(index % 5) + 1}`,
          `cloud-tone-${(index % 6) + 1}`,
          `cloud-rotate-${(index % 4) + 1}`,
        ]"
      >
        <button
          v-if="isOwnWanted(wanted)"
          class="cloud-delete-btn"
          type="button"
          title="删除求购"
          @click.stop="handleDeleteWanted(wanted)"
        >
          删除
        </button>
        <div class="cloud-item-main">
          <h3 class="cloud-item-title">{{ wanted.title }}</h3>
          <div class="cloud-item-budget">{{ formatBudget(wanted) }}</div>
        </div>
        <div class="cloud-item-tags">
          <span v-if="wanted.category" class="cloud-tag">{{ wanted.category }}</span>
          <span v-if="wanted.desired_condition" class="cloud-tag">{{ wanted.desired_condition }}</span>
          <span class="cloud-tag">{{ wanted.status === '已关闭' ? '已关闭' : '求购中' }}</span>
        </div>
        <p class="cloud-item-desc">{{ trimText(wanted.description, 24) }}</p>
        <div class="cloud-item-footer">
          <span class="cloud-user">
            <el-avatar :size="22" :src="userAvatar(wanted) || undefined">{{ wanted.user_nickname?.[0] }}</el-avatar>
            {{ wanted.user_nickname || '匿名同学' }}
          </span>
          <span class="cloud-time">{{ formatDate(wanted.created_at) }}</span>
        </div>
      </div>
    </div>

  </div>

  <teleport to="body">
    <div v-if="showPublishModal" class="wanted-modal-overlay" @click="closePublishModal">
      <div class="wanted-modal-panel" @click.stop>
        <WantedFormCard @cancel="closePublishModal" @success="handlePublishSuccess" />
      </div>
    </div>
  </teleport>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import WantedFormCard from '../components/WantedFormCard.vue'
import { deleteWanted, getWanteds } from '../api/wanted'
import { useUserStore } from '../store'
import { getUploadUrl } from '../utils/url'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const wanteds = ref([])
const loading = ref(true)
const showPublishModal = computed(() => route.path === '/wanted/create')
const currentUserId = computed(() => userStore.user?.id ?? null)

const userAvatar = (wanted) => {
  return wanted?.user_avatar ? getUploadUrl(wanted.user_avatar) : ''
}

const trimText = (text, max = 10) => {
  if (!text) return ''
  return text.length > max ? `${text.slice(0, max)}...` : text
}

const formatBudget = (wanted) => `¥${wanted.budget_min} - ¥${wanted.budget_max}`
const isOwnWanted = (wanted) => currentUserId.value && wanted.user_id === currentUserId.value

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
    const res = await getWanteds()
    wanteds.value = res.data.wanteds || []
  } catch (error) {
    console.error('Failed to fetch wanteds:', error)
  } finally {
    loading.value = false
  }
}

function openPublishModal() {
  router.push('/wanted/create')
}

function closePublishModal() {
  if (showPublishModal.value) router.replace('/wanteds')
}

async function handlePublishSuccess() {
  await fetchWanteds()
  closePublishModal()
}

async function handleDeleteWanted(wanted) {
  try {
    await ElMessageBox.confirm(`确认删除“${wanted.title}”吗？`, '删除求购', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
    await deleteWanted(wanted.id)
    wanteds.value = wanteds.value.filter((item) => item.id !== wanted.id)
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') console.error('Failed to delete wanted:', error)
  }
}

watch(showPublishModal, (visible) => {
  document.body.style.overflow = visible ? 'hidden' : ''
}, { immediate: true })

onMounted(() => {
  fetchWanteds()
})

onUnmounted(() => {
  document.body.style.overflow = ''
})
</script>

<style scoped>
.wanteds-page {
  width: 100%;
  max-width: none;
  margin: 0;
  overflow-x: hidden;
  box-sizing: border-box;
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

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-back-home {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border: 1.5px solid var(--c-border);
  border-radius: 12px;
  background: white;
  color: var(--c-text);
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s;
}

.btn-back-home:hover {
  border-color: var(--c-primary);
  color: var(--c-primary);
  background: var(--c-primary-light);
  transform: translateY(-2px);
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

.wanteds-cloud-board {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  grid-auto-flow: dense;
  align-items: start;
  gap: 18px 20px;
  width: 100%;
  padding: 34px 32px;
  min-height: 520px;
  border-radius: 26px;
  background:
    radial-gradient(circle at top, rgba(91, 141, 239, 0.08), transparent 36%),
    linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
  border: 1px solid rgba(137, 149, 169, 0.18);
  box-shadow: var(--c-shadow-md);
  overflow: hidden;
  box-sizing: border-box;
}

.cloud-wanted-item {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 14px 16px 16px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.88);
  border: 1px solid rgba(255, 255, 255, 0.65);
  box-shadow: 0 8px 24px rgba(40, 60, 120, 0.08);
  backdrop-filter: blur(8px);
  animation: fadeInUp 0.4s ease-out;
  transition: transform 0.22s ease, box-shadow 0.22s ease;
  width: 100%;
  max-width: none;
  min-width: 0;
  box-sizing: border-box;
}

.cloud-delete-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 5px 10px;
  border: none;
  border-radius: 999px;
  background: rgba(255, 107, 107, 0.12);
  color: var(--c-accent);
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.cloud-delete-btn:hover {
  background: var(--c-accent);
  color: white;
}

.cloud-wanted-item:hover {
  transform: translateY(-3px) scale(1.02);
  box-shadow: 0 12px 30px rgba(40, 60, 120, 0.12);
}

.cloud-item-main {
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 8px;
  padding-right: 48px;
}

.cloud-item-title {
  margin: 0;
  font-weight: 800;
  line-height: 1.15;
  color: var(--c-text);
  word-break: break-word;
}

.cloud-item-budget {
  font-weight: 700;
  white-space: nowrap;
}

.cloud-item-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.cloud-tag {
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.66);
  font-size: 12px;
  font-weight: 600;
  color: var(--c-text-secondary);
}

.cloud-item-desc {
  margin: 0;
  font-size: 12px;
  line-height: 1.45;
  color: var(--c-text-secondary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.cloud-item-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.cloud-user {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
  font-size: 12px;
  font-weight: 600;
  color: var(--c-text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cloud-time {
  flex-shrink: 0;
  font-size: 12px;
  color: var(--c-text-muted);
}

.cloud-size-1,
.cloud-size-2 {
  grid-column: span 2;
}

.cloud-size-1 .cloud-item-title {
  font-size: 30px;
}

.cloud-size-1 .cloud-item-budget {
  font-size: 18px;
  color: #2d6cdf;
}

.cloud-size-2 .cloud-item-title {
  font-size: 24px;
}

.cloud-size-2 .cloud-item-budget {
  font-size: 16px;
  color: #3aa76d;
}

.cloud-size-3 .cloud-item-title {
  font-size: 20px;
}

.cloud-size-3 .cloud-item-budget {
  font-size: 15px;
  color: #cb7d21;
}

.cloud-size-4 .cloud-item-title {
  font-size: 17px;
}

.cloud-size-4 .cloud-item-budget {
  font-size: 14px;
  color: #8b66d9;
}

.cloud-size-5 .cloud-item-title {
  font-size: 15px;
}

.cloud-size-5 .cloud-item-budget {
  font-size: 13px;
  color: #d35f56;
}

.cloud-tone-1 {
  background: linear-gradient(135deg, rgba(237, 246, 255, 0.98), rgba(255, 255, 255, 0.9));
}

.cloud-tone-2 {
  background: linear-gradient(135deg, rgba(241, 255, 246, 0.98), rgba(255, 255, 255, 0.9));
}

.cloud-tone-3 {
  background: linear-gradient(135deg, rgba(255, 247, 236, 0.98), rgba(255, 255, 255, 0.9));
}

.cloud-tone-4 {
  background: linear-gradient(135deg, rgba(248, 242, 255, 0.98), rgba(255, 255, 255, 0.9));
}

.cloud-tone-5 {
  background: linear-gradient(135deg, rgba(255, 241, 242, 0.98), rgba(255, 255, 255, 0.9));
}

.cloud-tone-6 {
  background: linear-gradient(135deg, rgba(238, 253, 253, 0.98), rgba(255, 255, 255, 0.9));
}

.cloud-rotate-1 {
  transform: rotate(-2deg);
}

.cloud-rotate-2 {
  transform: rotate(1.5deg);
}

.cloud-rotate-3 {
  transform: rotate(-1deg);
}

.cloud-rotate-4 {
  transform: rotate(2deg);
}

.wanted-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1200;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: rgba(17, 24, 39, 0.42);
  backdrop-filter: blur(4px);
}

.wanted-modal-panel {
  width: min(100%, 680px);
  max-height: 92vh;
  overflow-y: auto;
  border-radius: 24px;
}

@media (max-width: 768px) {
  .wanteds-page {
    width: 100%;
  }

  .wanteds-cloud-board {
    padding: 18px 14px;
    gap: 14px;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }

  .wanted-modal-overlay {
    padding: 12px;
  }

  .cloud-wanted-item,
  .cloud-size-1,
  .cloud-size-2,
  .cloud-size-3,
  .cloud-size-4,
  .cloud-size-5 {
    grid-column: span 1;
    width: 100%;
  }
}

</style>
