<template>
  <div class="admin-login-page">
    <div class="login-card">
      <div class="login-header">
        <div class="logo-icon">
          <svg viewBox="0 0 32 32" fill="none" width="48" height="48">
            <rect x="2" y="6" width="12" height="20" rx="2" fill="white" opacity="0.95"/>
            <rect x="18" y="2" width="12" height="24" rx="2" fill="white" opacity="0.95"/>
          </svg>
        </div>
        <h1 class="login-title">管理后台</h1>
        <p class="login-desc">校园二手交易平台管理系统</p>
      </div>

      <el-form :model="form" :rules="rules" ref="formRef" @submit.prevent="handleLogin">
        <el-form-item prop="username">
          <el-input 
            v-model="form.username" 
            placeholder="管理员账号"
            size="large"
            prefix-icon="User"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input 
            v-model="form.password" 
            type="password"
            placeholder="密码"
            size="large"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        <el-button 
          type="primary" 
          size="large" 
          style="width: 100%; margin-top: 8px;"
          :loading="loading"
          native-type="submit"
        >
          {{ loading ? '登录中...' : '登录' }}
        </el-button>
      </el-form>

      <div class="login-footer">
        <router-link to="/home">返回用户端</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { adminLogin } from '../../api/admin'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
})

const rules = {
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const res = await adminLogin(form)
    localStorage.setItem('admin_token', res.data.token)
    localStorage.setItem('admin_user', JSON.stringify(res.data.admin))
    ElMessage.success('登录成功')
    router.push('/admin/dashboard')
  } catch (error) {
    console.error('Login failed:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.admin-login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 400px;
  background: white;
  border-radius: 24px;
  padding: 40px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo-icon {
  width: 72px;
  height: 72px;
  margin: 0 auto 20px;
  border-radius: 18px;
  background: linear-gradient(135deg, #5B8DEF, #4CC9F0);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(91,141,239,0.4);
}

.login-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--c-text);
  margin-bottom: 8px;
}

.login-desc {
  font-size: 14px;
  color: var(--c-text-muted);
}

.login-footer {
  margin-top: 24px;
  text-align: center;
}

.login-footer a {
  color: var(--c-text-muted);
  font-size: 14px;
  text-decoration: none;
  transition: color 0.2s;
}

.login-footer a:hover {
  color: var(--c-primary);
}
</style>
