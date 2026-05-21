<template>
  <div class="auth-page">
    <div class="auth-bg-decor"></div>
    <div class="auth-card">
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
      <h2 class="auth-title">加入校园集市</h2>
      <p class="auth-subtitle">注册账号，开启闲置交易</p>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" size="large">
        <el-form-item label="学号" prop="student_id">
          <el-input v-model="form.student_id" placeholder="请输入学号" :prefix-icon="User" />
        </el-form-item>
        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="form.nickname" placeholder="请输入昵称" :prefix-icon="EditPen" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="至少6位" show-password
            :prefix-icon="Lock" />
        </el-form-item>
        <el-form-item label="确认密码" prop="password2">
          <el-input v-model="form.password2" type="password" placeholder="再次输入密码" show-password
            :prefix-icon="Lock" @keyup.enter="handleRegister" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" style="width:100%;height:46px;font-size:16px" :loading="loading"
            @click="handleRegister">注册</el-button>
        </el-form-item>
      </el-form>
      <p class="auth-link">已有账号？<router-link to="/login">去登录</router-link></p>
      <div class="admin-entry">
        <router-link to="/admin/login" class="admin-link">
          <svg viewBox="0 0 24 24" fill="none" width="16" height="16">
            <path d="M12 15a3 3 0 100-6 3 3 0 000 6z" fill="currentColor"/>
            <path fill-rule="evenodd" d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.32V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.32-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.32V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.32 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.32 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.32 1z" clip-rule="evenodd" fill="currentColor"/>
          </svg>
          管理员登录
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock, EditPen } from '@element-plus/icons-vue'
import { register } from '../api/auth'
import { useUserStore } from '../store'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  student_id: '',
  nickname: '',
  password: '',
  password2: '',
})

const validatePass2 = (rule, value, callback) => {
  if (value !== form.password) callback(new Error('两次输入的密码不一致'))
  else callback()
}

const rules = {
  student_id: [
    { required: true, message: '请输入学号', trigger: 'blur' },
    { min: 4, max: 20, message: '学号长度需在4-20位之间', trigger: 'blur' },
  ],
  nickname: [
    { required: true, message: '请输入昵称', trigger: 'blur' },
    { max: 50, message: '昵称不能超过50个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
  ],
  password2: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validatePass2, trigger: 'blur' },
  ],
}

async function handleRegister() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    const res = await register({
      student_id: form.student_id,
      nickname: form.nickname,
      password: form.password,
    })
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
  background: radial-gradient(circle, rgba(6,214,160,0.08) 0%, transparent 70%);
  bottom: -120px;
  left: -120px;
  pointer-events: none;
}

.auth-card {
  background: rgba(255,255,255,0.9);
  backdrop-filter: blur(20px);
  padding: 38px 40px;
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
  margin-bottom: 28px;
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

.admin-entry {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid rgba(0,0,0,0.06);
  text-align: center;
}

.admin-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--c-text-muted);
  font-size: 13px;
  transition: all 0.2s;
}

.admin-link:hover {
  color: var(--c-primary);
}
</style>
