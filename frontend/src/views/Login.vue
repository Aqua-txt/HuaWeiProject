<template>
  <div class="auth-page">
    <div class="auth-bg-decor"></div>
    <div class="auth-card">
      <button class="auth-back-btn" @click="$router.back()" title="返回">
        <svg viewBox="0 0 24 24" fill="none" width="20" height="20" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
      </button>
      <div class="auth-brand">
        <div class="brand-icon">
          <svg viewBox="0 0 32 32" fill="none" width="28" height="28">
            <rect x="2" y="6" width="12" height="20" rx="2" fill="white" opacity="0.95"/>
            <rect x="18" y="2" width="12" height="24" rx="2" fill="white" opacity="0.95"/>
            <path d="M6 12h4M6 16h4M22 8h4M22 13h4M22 18h4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
          </svg>
        </div>
        <span class="brand-name">校园集市</span>
      </div>
      <h2 class="auth-title">欢迎回来</h2>
      <p class="auth-subtitle">登录你的账号，继续校园交易</p>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" size="large">
        <el-form-item label="学号" prop="student_id">
          <el-input v-model="form.student_id" placeholder="请输入学号" :prefix-icon="User" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password
            :prefix-icon="Lock" @keyup.enter="handleLogin" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" style="width:100%;height:46px;font-size:16px" :loading="loading" @click="handleLogin">
            登录
          </el-button>
        </el-form-item>
      </el-form>
      <p class="auth-link">还没有账号？<router-link to="/register">立即注册</router-link></p>
      <div class="auth-divider">
        <span>或</span>
      </div>
      <router-link to="/admin/login" class="admin-entry-link">
        <svg viewBox="0 0 24 24" fill="none" width="16" height="16" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z"/>
          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1Z"/>
        </svg>
        管理员登录
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock } from '@element-plus/icons-vue'
import { login } from '../api/auth'
import { useUserStore } from '../store'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({ student_id: '', password: '' })

const rules = {
  student_id: [{ required: true, message: '请输入学号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    const res = await login(form)
    userStore.setAuth(res.data.token, res.data.user)
    router.push('/home')
  } catch {} finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  background: linear-gradient(160deg, #EEF2FF 0%, #E8F8F5 40%, #FFF8F0 100%);
}

.auth-bg-decor {
  position: absolute;
  width: 500px;
  height: 500px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(91,141,239,0.08) 0%, transparent 70%);
  top: -120px;
  right: -120px;
  pointer-events: none;
}

.auth-card {
  position: relative;
  background: rgba(255,255,255,0.9);
  backdrop-filter: blur(20px);
  padding: 44px 40px;
  border-radius: 24px;
  width: 420px;
  box-shadow:
    0 4px 24px rgba(91,141,239,0.06),
    0 12px 48px rgba(0,0,0,0.04);
  border: 1px solid rgba(91,141,239,0.06);
  position: relative;
  z-index: 1;
  animation: fadeInScale 0.5s ease;
}

.auth-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: center;
  margin-bottom: 8px;
}

.brand-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: linear-gradient(135deg, #5B8DEF, #4CC9F0);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 12px rgba(91,141,239,0.3);
}

.brand-name {
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, #5B8DEF, #06D6A0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.auth-title {
  text-align: center;
  margin: 16px 0 4px;
  font-size: 26px;
  font-weight: 700;
  color: var(--c-text);
}

.auth-subtitle {
  text-align: center;
  font-size: 14px;
  color: var(--c-text-muted);
  margin-bottom: 32px;
}

.auth-link {
  text-align: center;
  font-size: 14px;
  color: var(--c-text-muted);
  margin-top: 8px;
}

.auth-link a {
  color: var(--c-primary);
  font-weight: 600;
}

.auth-link a:hover { text-decoration: underline; }

.auth-divider {
  display: flex;
  align-items: center;
  margin-top: 20px;
}

.auth-divider::before,
.auth-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--c-border);
}

.auth-divider span {
  padding: 0 12px;
  font-size: 12px;
  color: var(--c-text-muted);
}

.admin-entry-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 100%;
  padding: 10px 0;
  margin-top: 12px;
  border-radius: 12px;
  border: 1px dashed var(--c-border);
  background: transparent;
  color: var(--c-text-muted);
  font-size: 14px;
  text-decoration: none;
  transition: all 0.25s;
}

.admin-entry-link:hover {
  background: rgba(30,41,59,0.04);
  color: var(--c-text-secondary);
  border-color: var(--c-text-muted);
}
</style>
