<template>
  <div class="layout">
    <header class="layout-header">
      <div class="header-bg"></div>
      <div class="header-content">
        <router-link to="/home" class="logo">
          <div class="logo-icon">
            <svg viewBox="0 0 32 32" fill="none" width="26" height="26">
              <rect x="2" y="6" width="12" height="20" rx="2" fill="white" opacity="0.95"/>
              <rect x="18" y="2" width="12" height="24" rx="2" fill="white" opacity="0.95"/>
              <path d="M6 12h4M6 16h4M22 8h4M22 13h4M22 18h4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
            </svg>
          </div>
          <span class="logo-text">拾光集市</span>
        </router-link>
        <div class="header-actions">
          <template v-if="userStore.isLoggedIn">
            <el-badge :value="unreadCount" :hidden="unreadCount === 0" :max="99" class="msg-badge">
              <button class="icon-btn" @click="$router.push('/messages')" title="消息">
                <svg viewBox="0 0 24 24" fill="none" width="20" height="20" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                </svg>
              </button>
            </el-badge>
            <router-link to="/publish">
              <button class="btn-publish">
                <svg viewBox="0 0 24 24" fill="none" width="16" height="16" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
                  <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
                </svg>
                发布
              </button>
            </router-link>
            <el-dropdown trigger="click" @command="handleCommand">
              <span class="avatar-wrap">
                <el-avatar :size="34" :src="avatarUrl" class="user-avatar">
                  <span class="avatar-fallback">{{ userStore.user?.nickname?.[0] }}</span>
                </el-avatar>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">
                    <el-icon><User /></el-icon>个人中心
                  </el-dropdown-item>
                  <el-dropdown-item command="orders">
                    <el-icon><List /></el-icon>我的订单
                  </el-dropdown-item>
                  <el-dropdown-item command="myProducts">
                    <el-icon><Goods /></el-icon>我的发布
                  </el-dropdown-item>
                  <el-dropdown-item command="myFavorites">
                    <el-icon><Star /></el-icon>我的收藏
                  </el-dropdown-item>
                  <el-dropdown-item command="editProfile">
                    <el-icon><EditPen /></el-icon>编辑资料
                  </el-dropdown-item>
                  <el-dropdown-item command="logout" divided>
                    <el-icon><SwitchButton /></el-icon>退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
          <template v-else>
            <router-link to="/login"><el-button class="btn-outline">登录</el-button></router-link>
            <router-link to="/register"><el-button type="primary">注册</el-button></router-link>
          </template>
        </div>
      </div>
    </header>
    <main class="layout-main" :class="{ 'layout-main-wide': ['/wanteds', '/wanted/create', '/home'].includes($route.path) }">
      <router-view v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store'
import { getUnreadCount } from '../api/chat'
import { List } from '@element-plus/icons-vue'
import { getUploadUrl } from '../utils/url'

const router = useRouter()
const userStore = useUserStore()
const unreadCount = ref(0)


const avatarUrl = computed(() => {
  const avatar = userStore.user?.avatar
  return avatar ? getUploadUrl(avatar) : ''
})

let pollTimer = null

async function fetchUnread() {
  if (!userStore.isLoggedIn) return
  try {
    const res = await getUnreadCount()
    unreadCount.value = res.data.count
  } catch {}
}

function handleCommand(cmd) {
  const routes = {
    logout: () => { userStore.logout(); router.push('/login') },
    profile: '/profile',
    orders: '/orders',
    myProducts: '/my-products',
    myFavorites: '/my-favorites',
    editProfile: '/edit-profile',
  }
  if (cmd === 'logout') routes.logout()
  else if (routes[cmd]) router.push(routes[cmd])
}

onMounted(() => {
  fetchUnread()
  pollTimer = setInterval(fetchUnread, 5000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>

<style scoped>
.layout { min-height: 100vh; }

.layout-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255,255,255,0.82);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-bottom: 1px solid rgba(91,141,239,0.08);
}

.header-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(91,141,239,0.04) 0%, rgba(6,214,160,0.03) 100%);
  pointer-events: none;
}

.header-content {
  width: 100%;
  max-width: none;
  margin: 0;
  padding: 0 24px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
  box-sizing: border-box;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
}

.logo-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, #5B8DEF, #4CC9F0);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 2px 8px rgba(91,141,239,0.25);
}

.logo-text {
  font-family: var(--font-display);
  font-size: 19px;
  font-weight: 700;
  background: linear-gradient(135deg, #5B8DEF, #06D6A0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 0.5px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.icon-btn {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  border: none;
  background: transparent;
  color: var(--c-text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.icon-btn:hover {
  background: var(--c-primary-light);
  color: var(--c-primary);
}

.btn-publish {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 8px 18px;
  border: none;
  border-radius: 24px;
  background: linear-gradient(135deg, #5B8DEF, #4CC9F0);
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s;
  box-shadow: 0 2px 10px rgba(91,141,239,0.3);
}

.btn-publish:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 18px rgba(91,141,239,0.4);
}

.btn-publish:active { transform: translateY(0); }

.avatar-wrap { cursor: pointer; }

.user-avatar {
  border: 2px solid transparent;
  background: linear-gradient(white, white) padding-box,
              linear-gradient(135deg, #5B8DEF, #06D6A0) border-box;
  transition: transform 0.2s;
}

.user-avatar:hover { transform: scale(1.05); }

.avatar-fallback {
  font-size: 14px;
  font-weight: 600;
  color: var(--c-primary);
}

.btn-outline {
  border: 1.5px solid var(--c-border) !important;
  background: transparent !important;
  color: var(--c-text) !important;
}

.btn-outline:hover {
  border-color: var(--c-primary) !important;
  color: var(--c-primary) !important;
}

.msg-badge :deep(.el-badge__content) {
  background: var(--c-accent);
  border: 2px solid white;
}

.layout-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 28px 24px;
  position: relative;
  z-index: 1;
  overflow-x: clip;
}

.layout-main-wide {
  max-width: min(1680px, calc(100vw - 16px));
  padding-left: 8px;
  padding-right: 8px;
}

/* Page transition */
.page-enter-active {
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}
.page-leave-active {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}
.page-enter-from {
  opacity: 0;
  transform: translateY(12px);
}
.page-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
