<template>
  <div class="edit-profile-page">
    <div class="edit-card">
      <button class="back-btn" @click="$router.back()" title="返回">
        <svg viewBox="0 0 24 24" fill="none" width="18" height="18" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
      </button>
      <h2>编辑资料</h2>
      <el-form ref="formRef" :model="form" label-position="top" size="large">
        <el-form-item label="头像">
          <div class="avatar-section">
            <el-upload :auto-upload="false" :show-file-list="false"
              :before-upload="beforeAvatar" @change="onAvatarChange" accept="image/*">
              <div class="avatar-edit-wrap">
                <el-avatar :size="88" :src="avatarPreview || avatarUrl" class="edit-avatar">
                  <span class="avatar-text">{{ userStore.user?.nickname?.[0] }}</span>
                </el-avatar>
                <div class="avatar-overlay">
                  <svg viewBox="0 0 24 24" fill="none" width="22" height="22" stroke="white" stroke-width="2">
                    <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
                    <circle cx="12" cy="13" r="4"/>
                  </svg>
                </div>
              </div>
            </el-upload>
            <p class="avatar-hint">点击更换头像</p>
          </div>
        </el-form-item>

        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="form.nickname" maxlength="50" show-word-limit placeholder="你的昵称" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="form.phone" placeholder="选填" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" placeholder="选填" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="saving" @click="handleSave"
            style="width:100%;height:46px;font-size:15px;border-radius:14px">
            保存修改
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../store'
import { updateProfile } from '../api/user'
import { getUploadUrl } from '../utils/url'

const router = useRouter()
const userStore = useUserStore()
const saving = ref(false)
const formRef = ref(null)
const avatarFile = ref(null)
const avatarPreview = ref('')

const avatarUrl = computed(() => {
  const avatar = userStore.user?.avatar
  return avatar ? getUploadUrl(avatar) : ''
})

const form = reactive({ nickname: '', phone: '', email: '' })

function beforeAvatar(file) {
  if (file.size > 5 * 1024 * 1024) { ElMessage.error('图片不能超过5MB'); return false }
  return false
}

function onAvatarChange(file) {
  avatarFile.value = file.raw
  const reader = new FileReader()
  reader.onload = (e) => { avatarPreview.value = e.target.result }
  reader.readAsDataURL(file.raw)
}

async function handleSave() {
  saving.value = true
  try {
    const fd = new FormData()
    if (form.nickname) fd.append('nickname', form.nickname)
    if (form.phone) fd.append('phone', form.phone)
    if (form.email) fd.append('email', form.email)
    if (avatarFile.value) fd.append('avatar', avatarFile.value)
    const res = await updateProfile(fd)
    userStore.updateUser(res.data.user)
    ElMessage.success('资料已更新')
    router.back()
  } catch {} finally { saving.value = false }
}

onMounted(() => {
  const u = userStore.user
  if (u) {
    form.nickname = u.nickname || ''
    form.phone = u.phone || ''
    form.email = u.email || ''
  }
})
</script>

<style scoped>
.edit-profile-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  box-sizing: border-box;
  animation: fadeInUp 0.4s ease;
}

.edit-card {
  background: white;
  width: min(100%, 500px);
  border-radius: 20px;
  padding: 32px;
  box-shadow: 0 2px 20px rgba(26,35,50,0.04);
  border: 1px solid rgba(0,0,0,0.03);
  position: relative;
}

.edit-card :deep(.back-btn) {
  position: absolute;
  top: 30px;
  left: 30px;
  margin-right: 0;
}

.edit-card h2 {
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 700;
  padding-left: 72px;
  min-height: 38px;
  display: flex;
  align-items: center;
  margin-bottom: 28px;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.avatar-edit-wrap {
  position: relative;
  cursor: pointer;
  border-radius: 50%;
}

.edit-avatar {
  border: 3px solid var(--c-border);
  font-weight: 700;
  transition: border-color 0.2s;
}

.avatar-edit-wrap:hover .edit-avatar {
  border-color: var(--c-primary);
}

.avatar-overlay {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: rgba(91,141,239,0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.25s;
}

.avatar-edit-wrap:hover .avatar-overlay {
  opacity: 1;
}

.avatar-text {
  font-size: 36px;
  color: var(--c-primary);
}

.avatar-hint {
  font-size: 12px;
  color: var(--c-primary);
  margin-top: 8px;
}
</style>
