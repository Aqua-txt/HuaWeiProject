<template>
  <div class="admin-users">
    <el-card>
      <template #header>
        <div class="header">
          <span>用户管理</span>
          <el-input v-model="keyword" placeholder="搜索用户（学号/昵称）" style="width: 200px" @keyup.enter="loadUsers" />
        </div>
      </template>

      <el-table :data="users" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="student_id" label="学号" width="150" />
        <el-table-column prop="nickname" label="昵称" width="150" />
        <el-table-column prop="credit_score" label="信用分" width="100">
          <template #default="{ row }">
            <el-tag :type="getCreditType(row.credit_score)" size="small">
              {{ row.credit_score }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="credit_count" label="评价数" width="100" />
        <el-table-column prop="is_banned" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_banned ? 'danger' : 'success'" size="small">
              {{ row.is_banned ? '已封禁' : '正常' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button
              v-if="!row.is_banned"
              type="danger"
              size="small"
              @click="toggleBan(row, true)"
            >
              封禁
            </el-button>
            <el-button
              v-if="row.is_banned"
              type="success"
              size="small"
              @click="toggleBan(row, false)"
            >
              解封
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-if="total > 0"
        v-model:current-page="page"
        :page-size="perPage"
        :total="total"
        layout="prev, pager, next"
        @current-change="loadUsers"
        class="pagination"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAdminUsers, toggleUserBan } from '../../api/admin'

const users = ref([])
const loading = ref(false)
const page = ref(1)
const perPage = ref(10)
const total = ref(0)
const keyword = ref('')

const getCreditType = (score) => {
  if (score >= 4.5) return 'success'
  if (score >= 3) return 'warning'
  return 'danger'
}

const formatTime = (time) => {
  if (!time) return ''
  return new Date(time).toLocaleString('zh-CN')
}

const loadUsers = async () => {
  loading.value = true
  try {
    const res = await getAdminUsers({
      page: page.value,
      per_page: perPage.value,
      keyword: keyword.value,
    })
    users.value = res.data.users
    total.value = res.data.total
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const toggleBan = async (user, isBanned) => {
  try {
    await ElMessageBox.confirm(`确认${isBanned ? '封禁' : '解封'}该用户？`, '提示', { type: 'warning' })
    await toggleUserBan(user.id, { is_banned: isBanned })
    ElMessage.success('操作成功')
    loadUsers()
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  }
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.admin-users {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>
