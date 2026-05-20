<template>
  <div class="messages-page">
    <div class="messages-card">
      <div class="messages-header">
        <h2>消息</h2>
        <span v-if="conversations.length" class="conv-count">{{ conversations.length }} 个对话</span>
      </div>
      <div v-if="conversations.length > 0" class="conv-list">
        <div v-for="c in conversations" :key="c.id" class="conv-item"
          @click="$router.push(`/chat/${c.id}`)">
          <div class="conv-avatar-col">
            <el-avatar :size="50" :src="getAvatarUrl(otherParty(c).avatar)" class="conv-avatar">
              <span class="avatar-text">{{ otherParty(c).nickname?.[0] }}</span>
            </el-avatar>
            <span v-if="c.unread_count > 0" class="unread-dot">{{ c.unread_count > 99 ? '99+' : c.unread_count }}</span>
          </div>
          <div class="conv-body">
            <div class="conv-top">
              <span class="conv-name">{{ otherParty(c).nickname }}</span>
              <span class="conv-time">{{ formatTime(c.last_message?.created_at || c.updated_at) }}</span>
            </div>
            <div class="conv-preview">{{ c.last_message?.content || '暂无消息' }}</div>
            <div class="conv-product">
              <svg viewBox="0 0 16 16" fill="none" width="12" height="12"><circle cx="8" cy="8" r="7" stroke="currentColor" stroke-width="1.5"/><path d="M8 4v5l3 2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
              来自：{{ c.product_title }}
            </div>
          </div>
          <div class="conv-thumb" v-if="c.product_images">
            <el-image :src="`${baseUrl}/api/uploads/${c.product_images}`" fit="cover"
              class="thumb-pic" />
          </div>
        </div>
      </div>
      <div v-else class="empty-conv">
        <svg viewBox="0 0 80 60" fill="none" width="80" height="60">
          <rect x="10" y="5" width="60" height="40" rx="8" stroke="#d0d5dd" stroke-width="2"/>
          <path d="M20 25l12 10 16-16 12 14" stroke="#d0d5dd" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <text x="40" y="68" text-anchor="middle" font-size="11" fill="#d0d5dd">暂无消息</text>
        </svg>
        <p>还没有对话，去逛逛商品吧</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useUserStore } from '../store'
import { getConversations } from '../api/chat'

const userStore = useUserStore()
const baseUrl = 'http://127.0.0.1:5000'
const conversations = ref([])

let pollTimer = null

function otherParty(c) {
  if (c.buyer_id === userStore.user?.id) {
    return { nickname: c.seller_nickname, avatar: c.seller_avatar }
  }
  return { nickname: c.buyer_nickname, avatar: c.buyer_avatar }
}

function getAvatarUrl(avatar) {
  return avatar ? `${baseUrl}/api/uploads/${avatar}` : ''
}

function formatTime(t) {
  if (!t) return ''
  const d = new Date(t)
  const now = new Date()
  const diff = now - d
  if (diff < 86400000) {
    return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }
  return d.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

async function fetchConversations() {
  try {
    const res = await getConversations()
    conversations.value = res.data.conversations
  } catch {}
}

onMounted(() => {
  fetchConversations()
  pollTimer = setInterval(fetchConversations, 5000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>

<style scoped>
.messages-page {
  max-width: 680px;
  margin: 0 auto;
  animation: fadeInUp 0.4s ease;
}

.messages-card {
  background: white;
  border-radius: 20px;
  box-shadow: 0 2px 20px rgba(26,35,50,0.04);
  border: 1px solid rgba(0,0,0,0.03);
  overflow: hidden;
  min-height: 300px;
}

.messages-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  padding: 22px 24px;
  border-bottom: 1px solid var(--c-border);
}

.messages-header h2 {
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 700;
}

.conv-count {
  font-size: 13px;
  color: var(--c-text-muted);
}

.conv-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 24px;
  cursor: pointer;
  transition: all 0.2s;
  border-bottom: 1px solid rgba(0,0,0,0.03);
}

.conv-item:hover {
  background: linear-gradient(135deg, rgba(91,141,239,0.02), rgba(6,214,160,0.02));
}

.conv-avatar-col {
  position: relative;
  flex-shrink: 0;
}

.conv-avatar {
  font-weight: 600;
}

.avatar-text {
  font-size: 18px;
  color: var(--c-primary);
}

.unread-dot {
  position: absolute;
  top: -4px;
  right: -4px;
  min-width: 20px;
  height: 20px;
  background: #FF6B6B;
  color: white;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 5px;
  box-shadow: 0 2px 6px rgba(255,107,107,0.3);
}

.conv-body {
  flex: 1;
  min-width: 0;
}

.conv-top {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.conv-name {
  font-size: 15px;
  font-weight: 600;
}

.conv-time {
  font-size: 12px;
  color: var(--c-text-muted);
  flex-shrink: 0;
}

.conv-preview {
  font-size: 13px;
  color: var(--c-text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 3px;
}

.conv-product {
  font-size: 11px;
  color: var(--c-text-muted);
  display: flex;
  align-items: center;
  gap: 4px;
}

.conv-thumb { flex-shrink: 0; }

.thumb-pic {
  width: 50px;
  height: 50px;
  border-radius: 10px;
}

.empty-conv {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  gap: 12px;
  color: var(--c-text-muted);
  font-size: 14px;
}
</style>
