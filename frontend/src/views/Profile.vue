<template>
  <div class="profile-page">
    <div class="profile-card">
      <div class="profile-header">
        <div class="avatar-ring">
          <el-avatar :size="80" :src="avatarUrl" class="profile-avatar">
            <span class="pfp-fallback">{{ userStore.user?.nickname?.[0] }}</span>
          </el-avatar>
        </div>
        <div class="profile-info">
          <h2>{{ userStore.user?.nickname }}</h2>
          <div class="info-tags">
            <span class="info-pill">{{ userStore.user?.student_id }}</span>
            <span class="info-pill badge">校友</span>
          </div>
        </div>
      </div>

      <div class="stats-row">
        <div class="stat-item">
          <span class="stat-value">{{ userStore.user?.phone ? '已绑定' : '未设置' }}</span>
          <span class="stat-label">手机号</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
          <span class="stat-value">{{ userStore.user?.email ? '已绑定' : '未设置' }}</span>
          <span class="stat-label">邮箱</span>
        </div>
      </div>

      <div class="menu-links">
        <button class="menu-item" @click="$router.push('/my-products')">
          <span class="menu-icon" style="background:rgba(91,141,239,0.1);color:#5B8DEF">
            <svg viewBox="0 0 24 24" fill="none" width="20" height="20" stroke="currentColor" stroke-width="2">
              <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
            </svg>
          </span>
          <span class="menu-text">我的发布</span>
          <svg viewBox="0 0 24 24" fill="none" width="16" height="16" stroke="currentColor" stroke-width="2" class="menu-arrow"><path d="M9 18l6-6-6-6"/></svg>
        </button>
        <button class="menu-item" @click="$router.push('/my-favorites')">
          <span class="menu-icon" style="background:rgba(255,159,67,0.1);color:#FF9F43">
            <svg viewBox="0 0 24 24" fill="none" width="20" height="20" stroke="currentColor" stroke-width="2">
              <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
            </svg>
          </span>
          <span class="menu-text">我的收藏</span>
          <svg viewBox="0 0 24 24" fill="none" width="16" height="16" stroke="currentColor" stroke-width="2" class="menu-arrow"><path d="M9 18l6-6-6-6"/></svg>
        </button>
        <button class="menu-item" @click="$router.push('/edit-profile')">
          <span class="menu-icon" style="background:rgba(6,214,160,0.1);color:#06D6A0">
            <svg viewBox="0 0 24 24" fill="none" width="20" height="20" stroke="currentColor" stroke-width="2">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
            </svg>
          </span>
          <span class="menu-text">编辑资料</span>
          <svg viewBox="0 0 24 24" fill="none" width="16" height="16" stroke="currentColor" stroke-width="2" class="menu-arrow"><path d="M9 18l6-6-6-6"/></svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useUserStore } from '../store'
import { getUploadUrl } from '../utils/url'

const userStore = useUserStore()

const avatarUrl = computed(() => {
  const avatar = userStore.user?.avatar
  return avatar ? getUploadUrl(avatar) : ''
})
</script>

<style scoped>
.profile-page {
  max-width: 560px;
  margin: 0 auto;
  animation: fadeInUp 0.4s ease;
}

.profile-card {
  background: white;
  border-radius: 20px;
  padding: 32px;
  box-shadow: 0 2px 20px rgba(26,35,50,0.04);
  border: 1px solid rgba(0,0,0,0.03);
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 24px;
}

.avatar-ring {
  padding: 3px;
  border-radius: 50%;
  background: linear-gradient(135deg, #5B8DEF, #06D6A0);
  flex-shrink: 0;
}

.profile-avatar {
  border: 3px solid white;
  font-weight: 700;
}

.pfp-fallback {
  font-size: 32px;
  color: var(--c-primary);
}

.profile-info h2 {
  font-family: var(--font-display);
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 8px;
}

.info-tags {
  display: flex;
  gap: 8px;
}

.info-pill {
  font-size: 12px;
  padding: 3px 10px;
  border-radius: 12px;
  background: var(--c-surface-alt);
  color: var(--c-text-secondary);
  font-weight: 500;
}

.info-pill.badge {
  background: rgba(6,214,160,0.1);
  color: var(--c-secondary);
  font-weight: 600;
}

.stats-row {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 16px 0;
  margin-bottom: 12px;
  border-top: 1px solid var(--c-border);
  border-bottom: 1px solid var(--c-border);
}

.stat-item {
  flex: 1;
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: var(--c-text);
  margin-bottom: 2px;
}

.stat-label {
  font-size: 12px;
  color: var(--c-text-muted);
}

.stat-divider {
  width: 1px;
  height: 32px;
  background: var(--c-border);
}

.menu-links {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 16px;
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: 14px;
  transition: all 0.2s;
  width: 100%;
  text-align: left;
}

.menu-item:hover {
  background: var(--c-surface-alt);
}

.menu-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.menu-text {
  flex: 1;
  font-size: 15px;
  font-weight: 600;
  color: var(--c-text);
}

.menu-arrow {
  color: var(--c-text-muted);
  flex-shrink: 0;
}
</style>
