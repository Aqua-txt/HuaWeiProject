<template>
  <div class="admin-reports-page">
    <h1 class="page-title">举报管理</h1>

    <div class="filters">
      <el-radio-group v-model="status" @change="fetchReports">
        <el-radio-button label="待处理">待处理</el-radio-button>
        <el-radio-button label="">全部</el-radio-button>
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

        <el-table-column label="举报人" width="140">
          <template #default="{ row }">
            <div class="user-cell">
              <span>{{ row.reporter_nickname || '未知' }}</span>
              <span class="user-sub">学号: {{ row.reporter_student_id || '-' }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="被举报商品" min-width="200">
          <template #default="{ row }">
            <div class="product-cell">
              <span>{{ row.product_title || '已删除' }}</span>
              <span class="product-sub">商品ID: {{ row.product_id }} | 卖家: {{ row.product_seller_nickname || '-' }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="report_type" label="举报类型" width="110" />
        <el-table-column label="时间" width="170">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status)" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewReport(row)">查看详情</el-button>
            <el-button
              v-if="row.status === '待处理'"
              size="small"
              type="primary"
              @click="openHandleDialog(row)"
            >
              处理
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-wrap" v-if="total > perPage">
        <el-pagination
          background
          layout="prev, pager, next"
          :total="total"
          :page-size="perPage"
          :current-page="page"
          @current-change="onPageChange"
        />
      </div>
    </div>

    <!-- Detail Dialog -->
    <el-dialog v-model="dialogVisible" title="举报详情" width="560px">
      <div v-if="selectedReport" class="report-detail">
        <div class="detail-section">
          <h4 class="section-title">举报信息</h4>
          <div class="detail-grid">
            <div class="detail-item">
              <span class="detail-label">举报编号</span>
              <span class="detail-value">#{{ selectedReport.id }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">举报类型</span>
              <el-tag size="small">{{ selectedReport.report_type }}</el-tag>
            </div>
            <div class="detail-item">
              <span class="detail-label">当前状态</span>
              <el-tag size="small" :type="statusTag(selectedReport.status)">{{ selectedReport.status }}</el-tag>
            </div>
            <div class="detail-item">
              <span class="detail-label">提交时间</span>
              <span class="detail-value">{{ formatDate(selectedReport.created_at) }}</span>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <h4 class="section-title">举报描述</h4>
          <div class="detail-content">{{ selectedReport.description }}</div>
        </div>

        <div class="detail-section">
          <h4 class="section-title">举报人</h4>
          <div class="detail-grid">
            <div class="detail-item">
              <span class="detail-label">昵称</span>
              <span class="detail-value">{{ selectedReport.reporter_nickname }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">学号</span>
              <span class="detail-value">{{ selectedReport.reporter_student_id || '-' }}</span>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <h4 class="section-title">被举报商品</h4>
          <div class="detail-grid">
            <div class="detail-item">
              <span class="detail-label">商品名称</span>
              <span class="detail-value">{{ selectedReport.product_title || '已删除' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">商品ID</span>
              <span class="detail-value">#{{ selectedReport.product_id }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">卖家</span>
              <span class="detail-value">{{ selectedReport.product_seller_nickname || '-' }}</span>
            </div>
          </div>
          <a :href="'/product/' + selectedReport.product_id" target="_blank" class="product-link-btn">
            <svg viewBox="0 0 24 24" fill="none" width="14" height="14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/>
            </svg>
            在新标签页查看商品详情
          </a>
        </div>

        <div v-if="selectedReport.status !== '待处理'" class="detail-section">
          <h4 class="section-title">处理记录</h4>
          <div class="detail-grid">
            <div class="detail-item">
              <span class="detail-label">处理时间</span>
              <span class="detail-value">{{ formatDate(selectedReport.handled_at) }}</span>
            </div>
            <div v-if="selectedReport.handler_note" class="detail-item full-width">
              <span class="detail-label">处理备注</span>
              <div class="detail-content">{{ selectedReport.handler_note }}</div>
            </div>
          </div>
        </div>
      </div>
      <template #footer v-if="selectedReport?.status === '待处理'">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="danger" @click="executeAction('reject')">驳回举报</el-button>
        <el-button type="warning" @click="executeAction('takedown')">下架商品</el-button>
      </template>
    </el-dialog>

    <!-- Handle Dialog -->
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
          <el-input v-model="handleNote" type="textarea" :rows="3" placeholder="可选，填写处理说明" />
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
const status = ref('待处理')
const page = ref(1)
const perPage = ref(20)
const total = ref(0)

const dialogVisible = ref(false)
const handleDialogVisible = ref(false)
const selectedReport = ref(null)
const handleAction = ref('takedown')
const handleNote = ref('')

function formatDate(date) {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

function statusTag(status) {
  return status === '待处理' ? 'warning' : status === '已驳回' ? 'info' : 'success'
}

async function fetchReports() {
  loading.value = true
  try {
    const res = await getAdminReports({ status: status.value, page: page.value, per_page: perPage.value })
    reports.value = res.data.reports || []
    total.value = res.data.total || 0
  } catch (error) {
    console.error('Failed to fetch reports:', error)
  } finally {
    loading.value = false
  }
}

function onPageChange(p) {
  page.value = p
  fetchReports()
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

.filters { margin-bottom: 24px; }

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

.user-cell, .product-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-sub, .product-sub {
  font-size: 12px;
  color: var(--c-text-muted);
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

/* Detail dialog */
.report-detail { padding: 4px 0; }

.detail-section {
  margin-bottom: 20px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--c-text);
  margin-bottom: 12px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--c-border);
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px 16px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.detail-item.full-width {
  grid-column: 1 / -1;
  flex-direction: column;
  align-items: flex-start;
}

.detail-label {
  font-weight: 500;
  color: var(--c-text-secondary);
  min-width: 70px;
  font-size: 13px;
}

.detail-value {
  font-size: 14px;
  color: var(--c-text);
}

.detail-content {
  padding: 10px 12px;
  background: var(--c-surface-alt);
  border-radius: 8px;
  line-height: 1.6;
  font-size: 14px;
  color: var(--c-text-secondary);
}

.product-link-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-top: 10px;
  padding: 8px 14px;
  border-radius: 8px;
  background: var(--c-primary-light);
  color: var(--c-primary);
  font-size: 13px;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.2s;
}

.product-link-btn:hover {
  background: var(--c-primary);
  color: white;
}
</style>
