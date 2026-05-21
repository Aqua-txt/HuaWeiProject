<template>
  <div class="admin-products">
    <el-card>
      <template #header>
        <div class="header">
          <span>商品管理</span>
          <div>
            <el-input v-model="keyword" placeholder="搜索商品" style="width: 200px; margin-right: 10px" @keyup.enter="loadProducts" />
            <el-select v-model="statusFilter" placeholder="状态" clearable @change="loadProducts" style="width: 120px">
              <el-option label="上架" value="上架" />
              <el-option label="已下架" value="已下架" />
            </el-select>
          </div>
        </div>
      </template>

      <el-table :data="products" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="标题" />
        <el-table-column prop="seller_nickname" label="卖家" width="120" />
        <el-table-column prop="category" label="分类" width="100" />
        <el-table-column prop="price" label="价格" width="100">
          <template #default="{ row }">
            ¥{{ row.price }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === '上架' ? 'success' : 'info'" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button
              v-if="row.status === '上架'"
              type="warning"
              size="small"
              @click="toggleStatus(row, '已下架')"
            >
              下架
            </el-button>
            <el-button
              v-if="row.status === '已下架'"
              type="success"
              size="small"
              @click="toggleStatus(row, '上架')"
            >
              上架
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
        @current-change="loadProducts"
        class="pagination"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAdminProducts, updateAdminProductStatus } from '../../api/admin'

const products = ref([])
const loading = ref(false)
const page = ref(1)
const perPage = ref(10)
const total = ref(0)
const keyword = ref('')
const statusFilter = ref('')

const formatTime = (time) => {
  if (!time) return ''
  return new Date(time).toLocaleString('zh-CN')
}

const loadProducts = async () => {
  loading.value = true
  try {
    const res = await getAdminProducts({
      page: page.value,
      per_page: perPage.value,
      keyword: keyword.value,
      status: statusFilter.value,
    })
    products.value = res.data.products
    total.value = res.data.total
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const toggleStatus = async (product, newStatus) => {
  try {
    await ElMessageBox.confirm(`确认${newStatus === '已下架' ? '下架' : '上架'}该商品？`, '提示', { type: 'warning' })
    await updateAdminProductStatus(product.id, { status: newStatus })
    ElMessage.success('操作成功')
    loadProducts()
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  }
}

onMounted(() => {
  loadProducts()
})
</script>

<style scoped>
.admin-products {
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
