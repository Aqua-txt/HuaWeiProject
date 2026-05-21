<template>
  <div class="admin-reports-page">
    <h1 class="page-title">举报管理</h1>

    <div class="filters">
      <el-radio-group v-model="status" @change="fetchReports">
        <el-radio-button label="pending">待处理</el-radio-button>
        <el-radio-button label="handled">已处理</el-radio-button>
      </el-radio-group>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else-if="reports.length === 0" class="empty-state">
      <p>暂无举报记录</p>
    </div>

    <div v-else class="reports-table">
      <el-table :data="reports" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="举报人" width="120">
          <template #default="{ row }">
            {{ row.reporter?.nickname || '未知' }}
          </template>
        </el-table-column>
        <el-table-column label="被举报商品" min-width="200">
          <template #default="{ row }">
            <div class="product-cell">
              <span>{{ row.product?.title || '已删除' }}</span>
              <span class="product-id">ID: {{ row.product_id }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="report_type" label="类型" width="120" />
        <el-table-column label="时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'pending' ? 'warning' : 'success'">
              {{ row.status === 'pending' ? '待处理' : '已处理' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewReport(row)">查看</el-button>
            <el-button 
              v-if="row.status === 'pending'" 
              size="small" 
              type="primary" 
              @click="openHandleDialog(row)"
            >
              处理
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialogVisible" title="举报详情" width="600px">
      <div v-if="selectedReport" class="report-detail">
        <div class="detail-row">
          <span class="detail-label">举报人:</span>
          <span>{{ selectedReport.reporter?.nickname }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">被举报商品:</span>
          <span>{{ selectedReport.product?.title }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">举报类型:</span>
          <el-tag>{{ selectedReport.report_type }}</el-tag>
        </div>
        <div class="detail-row">
          <span class="detail-label">举报描述:</span>
        </div>
        <div class="detail-content">
          {{ selectedReport.description }}
        </div>
        <div v-if="selectedReport.status === 'handled'" class="detail-row">
          <span class="detail-label">处理结果:</span>
          <el-tag type="success">已处理</el-tag>
        </div>
        <div v-if="selectedReport.handler_note" class="detail-row">
          <span class="detail-label">处理备注:</span>
        </div>
        <div v-if="selectedReport.handler_note" class="detail-content">
          {{ selectedReport.handler_note }}
        </div>
      </div>
      <template #footer v-if="selectedReport?.status === 'pending'">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="danger" @click="executeAction('reject')">驳回举报</el-button>
        <el-button type="warning" @click="executeAction('takedown')">下架商品</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="handleDialogVisible" title="处理举报" width="500px">
      <el-form>
        <el-form-item label="处理操作">
          <el-select v-model="handleAction" style="width: 100%;">
            <el-option label="下架商品" value="takedown" />
            <el-option label="驳回举报" value="reject" />
            <el-option label="封禁用户" value="ban" />
          </el-select>
        </el-form-item>
        <el-form-item label="处理备注">
          <el-input v-model="handleNote" type="textarea" :rows="3" placeholder="可选,填写处理说明" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="handleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitHandle">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getAdminReports, handleReport } from '../../api/admin'

const reports = ref([])
const loading = ref(true)
const status = ref('pending')
const dialogVisible = ref(false)
const handleDialogVisible = ref(false)
const selectedReport = ref(null)
const handleAction = ref('takedown')
const handleNote = ref('')

const formatDate = (date) => {
  return new Date(date).toLocaleString('zh-CN')
}

async function fetchReports() {
  loading.value = true
  try {
    const res = await getAdminReports({ status: status.value })
    reports.value = (res.data.reports || []).map(report => ({
      ...report,
      status: report.status === 'pending' ? 'pending' : 'handled'
    }))
  } catch (error) {
    console.error('Failed to fetch reports:', error)
  } finally {
    loading.value = false
  }
}

function viewReport(report) {
  selectedReport.value = report
  dialogVisible.value = true
}

function openHandleDialog(report) {
  selectedReport.value = report
  handleAction.value = 'takedown'
  handleNote.value = ''
  handleDialogVisible.value = true
}

async function submitHandle() {
  try {
    await handleReport(selectedReport.value.id, {
      action: handleAction.value,
      note: handleNote.value,
    })
    ElMessage.success('处理成功')
    handleDialogVisible.value = false
    dialogVisible.value = false
    fetchReports()
  } catch (error) {
    console.error('Failed to handle report:', error)
  }
}

function executeAction(action) {
  handleAction.value = action
  handleNote.value = ''
  submitHandle()
}

onMounted(() => {
  fetchReports()
})
</script>

<style scoped>
.admin-reports-page {
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

.reports-table {
  background: var(--c-surface);
  border-radius: 16px;
  padding: 20px;
  box-shadow: var(--c-shadow-md);
}

.product-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.product-id {
  font-size: 12px;
  color: var(--c-text-muted);
}

.report-detail {
  padding: 20px 0;
}

.detail-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.detail-label {
  font-weight: 600;
  color: var(--c-text-secondary);
  min-width: 100px;
}

.detail-content {
  padding: 12px;
  background: var(--c-surface-alt);
  border-radius: 8px;
  margin-bottom: 16px;
  line-height: 1.6;
}
</style>
