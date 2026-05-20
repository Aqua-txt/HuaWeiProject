<template>
  <div class="chat-page">
    <!-- Header -->
    <div class="chat-header">
      <button class="btn-back" @click="$router.back()">
        <svg viewBox="0 0 24 24" fill="none" width="20" height="20" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
      </button>
      <el-avatar :size="38" :src="getAvatarUrl(partnerAvatar)" class="partner-avatar">
        <span class="avatar-fb">{{ partnerName?.[0] }}</span>
      </el-avatar>
      <div class="partner-info">
        <span class="partner-name">{{ partnerName }}</span>
        <span class="partner-product">{{ conv?.product_title }}</span>
      </div>
    </div>

    <!-- Messages -->
    <div class="chat-messages" ref="msgContainer">
      <div v-if="messages.length === 0 && !loading" class="chat-empty">
        <div class="empty-bubble">
          <svg viewBox="0 0 48 48" fill="none" width="48" height="48">
            <circle cx="24" cy="24" r="22" stroke="#d0d5dd" stroke-width="1.5" stroke-dasharray="4 4"/>
            <path d="M16 22h16M16 28h10" stroke="#d0d5dd" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
          <p>发送第一条消息，开始交流吧</p>
        </div>
      </div>
      <div v-for="msg in messages" :key="msg.id"
        class="msg-row" :class="{ 'msg-mine': msg.sender_id === userStore.user?.id }">
        <div class="msg-bubble" :class="{ mine: msg.sender_id === userStore.user?.id }">
          <div class="msg-text">{{ msg.content }}</div>
          <div class="msg-time">{{ formatTime(msg.created_at) }}</div>
        </div>
      </div>
    </div>

    <!-- Input -->
    <div class="chat-input">
      <div class="input-wrap">
        <textarea v-model="inputText" placeholder="输入消息..." rows="1"
          @keydown.enter.exact.prevent="handleSend" :disabled="sending"
          @input="autoResize" ref="inputRef"
          class="msg-textarea"></textarea>
        <button class="btn-send" :class="{ ready: inputText.trim() }"
          @click="handleSend" :disabled="!inputText.trim() || sending">
          <svg viewBox="0 0 24 24" fill="none" width="20" height="20" stroke="currentColor" stroke-width="2" stroke-linecap="round">
            <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { getMessages, sendMessage } from '../api/chat'
import { useUserStore } from '../store'

const route = useRoute()
const userStore = useUserStore()
const baseUrl = 'http://127.0.0.1:5000'

const conv = ref(null)
const messages = ref([])
const inputText = ref('')
const loading = ref(false)
const sending = ref(false)
const msgContainer = ref(null)
const inputRef = ref(null)

let pollTimer = null
let lastMsgId = 0

const partnerName = computed(() => {
  if (!conv.value) return ''
  return userStore.user?.id === conv.value.buyer_id
    ? conv.value.seller_nickname
    : conv.value.buyer_nickname
})

const partnerAvatar = computed(() => {
  if (!conv.value) return ''
  return userStore.user?.id === conv.value.buyer_id
    ? conv.value.seller_avatar
    : conv.value.buyer_avatar
})

function getAvatarUrl(avatar) {
  return avatar ? `${baseUrl}/api/uploads/${avatar}` : ''
}

function formatTime(t) {
  if (!t) return ''
  return new Date(t).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

function scrollToBottom() {
  nextTick(() => {
    const el = msgContainer.value
    if (el) el.scrollTop = el.scrollHeight
  })
}

function autoResize() {
  const el = inputRef.value
  if (el) {
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 120) + 'px'
  }
}

function updateLastId() {
  if (messages.value.length > 0) {
    lastMsgId = messages.value[messages.value.length - 1].id
  }
}

async function fetchMessages() {
  loading.value = true
  try {
    const res = await getMessages(route.params.id)
    messages.value = res.data.messages
    updateLastId()
    conv.value = { ...res.data, id: parseInt(route.params.id) }
    scrollToBottom()
  } catch {} finally {
    loading.value = false
  }
}

async function pollNewMessages() {
  if (!conv.value) return
  try {
    const res = await getMessages(route.params.id, { after_id: lastMsgId })
    const newMsgs = res.data.messages
    if (newMsgs.length > 0) {
      // Keep only messages not already in the list (dedup by id)
      const existingIds = new Set(messages.value.map(m => m.id))
      const trulyNew = newMsgs.filter(m => !existingIds.has(m.id))
      if (trulyNew.length > 0) {
        messages.value.push(...trulyNew)
        updateLastId()
        scrollToBottom()
      }
    }
  } catch {}
}

async function handleSend() {
  const content = inputText.value.trim()
  if (!content) return
  sending.value = true
  try {
    const res = await sendMessage(route.params.id, { content })
    inputText.value = ''
    messages.value.push(res.data)
    updateLastId()
    if (inputRef.value) inputRef.value.style.height = 'auto'
    scrollToBottom()
  } catch {} finally {
    sending.value = false
  }
}

onMounted(async () => {
  await fetchMessages()
  pollTimer = setInterval(pollNewMessages, 3000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>

<style scoped>
.chat-page {
  max-width: 700px;
  margin: 0 auto;
  background: white;
  border-radius: 20px;
  box-shadow: 0 2px 20px rgba(26,35,50,0.04);
  border: 1px solid rgba(0,0,0,0.03);
  display: flex;
  flex-direction: column;
  height: calc(100vh - 112px);
  overflow: hidden;
  animation: fadeInUp 0.4s ease;
}

/* Header */
.chat-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  border-bottom: 1px solid var(--c-border);
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(12px);
}

.btn-back {
  width: 36px;
  height: 36px;
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

.btn-back:hover { background: var(--c-primary-light); color: var(--c-primary); }

.partner-avatar { flex-shrink: 0; }

.avatar-fb {
  font-size: 16px;
  font-weight: 600;
  color: var(--c-primary);
}

.partner-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.partner-name {
  font-size: 15px;
  font-weight: 600;
}

.partner-product {
  font-size: 12px;
  color: var(--c-text-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Messages area */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background:
    radial-gradient(circle at 20% 30%, rgba(91,141,239,0.02) 0%, transparent 50%),
    radial-gradient(circle at 80% 70%, rgba(6,214,160,0.02) 0%, transparent 50%),
    #fafbfc;
}

.chat-empty {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-bubble {
  text-align: center;
  color: var(--c-text-muted);
}

.empty-bubble p {
  margin-top: 12px;
  font-size: 14px;
}

.msg-row {
  display: flex;
  margin-bottom: 14px;
  animation: fadeInUp 0.3s ease;
}

.msg-mine { justify-content: flex-end; }

.msg-bubble {
  max-width: 68%;
  padding: 12px 16px;
  border-radius: 18px;
  background: white;
  box-shadow: 0 1px 3px rgba(26,35,50,0.06);
  border: 1px solid rgba(0,0,0,0.04);
}

.msg-bubble.mine {
  background: linear-gradient(135deg, #5B8DEF, #4A7BDB);
  color: white;
  border: none;
  border-bottom-right-radius: 6px;
  box-shadow: 0 2px 10px rgba(91,141,239,0.2);
}

.msg-bubble:not(.mine) {
  border-bottom-left-radius: 6px;
}

.msg-text {
  font-size: 14px;
  line-height: 1.55;
  word-break: break-word;
}

.msg-time {
  font-size: 10px;
  margin-top: 5px;
  opacity: 0.5;
  text-align: right;
}

.msg-bubble.mine .msg-time { color: rgba(255,255,255,0.7); }
.msg-bubble:not(.mine) .msg-time { color: var(--c-text-muted); }

/* Input */
.chat-input {
  padding: 14px 20px;
  border-top: 1px solid var(--c-border);
  background: white;
}

.input-wrap {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  background: var(--c-surface-alt);
  border-radius: 24px;
  padding: 8px 8px 8px 18px;
  transition: all 0.25s;
  border: 1.5px solid transparent;
}

.input-wrap:focus-within {
  border-color: var(--c-primary);
  background: white;
  box-shadow: 0 0 0 4px rgba(91,141,239,0.06);
}

.msg-textarea {
  flex: 1;
  border: none;
  background: transparent;
  outline: none;
  resize: none;
  font-size: 14px;
  line-height: 1.5;
  font-family: var(--font-body);
  color: var(--c-text);
  padding: 4px 0;
  max-height: 120px;
}

.msg-textarea::placeholder { color: var(--c-text-muted); }

.btn-send {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: var(--c-border);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.25s;
  flex-shrink: 0;
}

.btn-send.ready {
  background: linear-gradient(135deg, #5B8DEF, #4CC9F0);
  box-shadow: 0 2px 8px rgba(91,141,239,0.3);
}

.btn-send.ready:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 14px rgba(91,141,239,0.4);
}

.btn-send:disabled { cursor: not-allowed; }
</style>
