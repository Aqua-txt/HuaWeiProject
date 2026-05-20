<template>
  <div class="admin-users-page">
    <h1 class="page-title">用户管理</h1>

    <div class="filters">
      <el-input 
        v-model="search" 
        placeholder="搜索学号或昵称" 
        clearable 
        @input="fetchUsers"
        style="width: 300px;"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else-if="users.length === 0" class="empty-state">
      <p>暂无用户</p>
    </div>

    <div v-else class="users-table">
      <el-table :data="users" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="用户" min-width="200">
          <template #default="{ row }">
            <div class="user-cell">
              <el-avatar :size="40" :src="userAvatar(row)">
                {{ row.nickname?.[0] }}
              </el-avatar>
              <div class="user-info">
                <span class="user-name">{{ row.nickname }}</span>
                <span class="user-id">{{ row.student_id }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="信用分" width="120">
          <template #default="{ row }">
            <div class="credit-score">
              <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16" style="color: #F59E0B;">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
              </svg>
              <span>{{ row.credit_score?.toFixed(1) || '0.0' }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="发布数" width="100">
          <template #default="{ row }">
            {{ row.product_count || 0 }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
              {{ row.status === 'active' ? '正常' : '封禁' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="注册时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewUser(row)">查看</el-button>
            <el-button 
              size="small" 
              :type="row.status === 'active' ? 'danger' : 'success'"
              @click="toggleUser(row)"
            >
              {{ row.status === 'active' ? '封禁' : '解封' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAdminUsers, adminToggleUser } from '../../api/admin'

const users = ref([])
const loading = ref(true)
const search = ref('')

const baseUrl = 'http://127.0.0.1:5000'

const userAvatar = (user) => {
  return user.avatar ? `${baseUrl}/api/uploads/${user.avatar}` : ''
}

const formatDate = (date) => {
  return new Date(date).toLocaleString('zh-CN')
}

async function fetchUsers() {
  loading.value = true
  try {
    const res = await getAdminUsers({ search: search.value })
    users.value = res.data.users || []
  } catch (error) {
    console.error('Failed to fetch users:', error)
  } finally {
    loading.value = false
  }
}

function viewUser(user) {
  window.open(`/profile/${user.id}`, '_blank')
}

async function toggleUser(user) {
  const action = user.status === 'active' ? '封禁' : '解封'
  try {
    await ElMessageBox.confirm(
      `确定要${action}用户 "${user.nickname}" 吗?`,
      '确认操作',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    await adminToggleUser(user.id)
    ElMessage.success(`已${action}`)
    fetchUsers()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to toggle user:', error)
    }
  }
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.admin-users-page {
  max-width: 1200px;
  margin: 0 auto;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--c-text);
  margin-bottom: 24px;
}

.filters {
  margin-bottom: 24px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
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
  padding: 60px 20px;
  text-align: center;
  color: var(--c-text-muted);
}

.users-table {
  background: var(--c-surface);
  border-radius: 16px;
  padding: 20px;
  box-shadow: var(--c-shadow-md);
}

.user-cell {
  display: flex;
  gap: 12px;
  align-items: center;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.user-name {
  font-weight: 600;
  color: var(--c-text);
}

.user-id {
  font-size: 13px;
  color: var(--c-text-muted);
}

.credit-score {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
}
</style>
