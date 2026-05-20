<template>
  <div class="dashboard-page">
    <h1 class="page-title">数据看板</h1>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <template v-else>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #5B8DEF, #4CC9F0);">
            <svg viewBox="0 0 24 24" fill="none" width="24" height="24" stroke="white" stroke-width="2">
              <line x1="12" y1="1" x2="12" y2="23"/>
              <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
            </svg>
          </div>
          <div class="stat-info">
            <p class="stat-label">今日GMV</p>
            <h3 class="stat-value">¥{{ stats.today_gmv?.toFixed(2) || '0.00' }}</h3>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #06D6A0, #05B894);">
            <svg viewBox="0 0 24 24" fill="none" width="24" height="24" stroke="white" stroke-width="2">
              <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/>
              <line x1="3" y1="6" x2="21" y2="6"/>
            </svg>
          </div>
          <div class="stat-info">
            <p class="stat-label">今日订单</p>
            <h3 class="stat-value">{{ stats.today_orders || 0 }}</h3>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #F59E0B, #D97706);">
            <svg viewBox="0 0 24 24" fill="none" width="24" height="24" stroke="white" stroke-width="2">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
              <line x1="3" y1="9" x2="21" y2="9"/>
              <line x1="9" y1="21" x2="9" y2="9"/>
            </svg>
          </div>
          <div class="stat-info">
            <p class="stat-label">今日发布</p>
            <h3 class="stat-value">{{ stats.today_products || 0 }}</h3>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #FF6B6B, #EE5A5A);">
            <svg viewBox="0 0 24 24" fill="none" width="24" height="24" stroke="white" stroke-width="2">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
          </div>
          <div class="stat-info">
            <p class="stat-label">活跃用户</p>
            <h3 class="stat-value">{{ stats.active_users || 0 }}</h3>
          </div>
        </div>
      </div>

      <div class="charts-grid">
        <div class="chart-card">
          <h3 class="chart-title">近30天交易趋势</h3>
          <div class="chart-placeholder">
            <p style="color: var(--c-text-muted);">图表区域</p>
            <p style="font-size: 12px; color: var(--c-border); margin-top: 8px;">
              可集成 ECharts/Chart.js 展示折线图
            </p>
          </div>
        </div>

        <div class="chart-card">
          <h3 class="chart-title">商品分类分布</h3>
          <div class="chart-placeholder">
            <p style="color: var(--c-text-muted);">图表区域</p>
            <p style="font-size: 12px; color: var(--c-border); margin-top: 8px;">
              可集成饼图展示分类占比
            </p>
          </div>
        </div>
      </div>

      <div class="recent-section">
        <div class="recent-card">
          <h3 class="section-title">待处理举报</h3>
          <div v-if="stats.pending_reports === 0" class="empty-text">
            暂无待处理举报
          </div>
          <div v-else class="alert-badge">
            {{ stats.pending_reports }} 条举报待处理
          </div>
          <router-link to="/admin/reports" class="view-link">查看全部 →</router-link>
        </div>

        <div class="recent-card">
          <h3 class="section-title">交易漏斗</h3>
          <div class="funnel">
            <div class="funnel-item">
              <span class="funnel-label">浏览</span>
              <span class="funnel-value">{{ stats.funnel?.view || 0 }}</span>
            </div>
            <div class="funnel-item">
              <span class="funnel-label">咨询</span>
              <span class="funnel-value">{{ stats.funnel?.inquiry || 0 }}</span>
            </div>
            <div class="funnel-item">
              <span class="funnel-label">付款</span>
              <span class="funnel-value">{{ stats.funnel?.payment || 0 }}</span>
            </div>
            <div class="funnel-item">
              <span class="funnel-label">完成</span>
              <span class="funnel-value">{{ stats.funnel?.completed || 0 }}</span>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getAdminDashboard } from '../../api/admin'

const loading = ref(true)
const stats = ref({})

async function fetchDashboard() {
  loading.value = true
  try {
    const res = await getAdminDashboard()
    stats.value = res.data
  } catch (error) {
    console.error('Failed to fetch dashboard:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchDashboard()
})
</script>

<style scoped>
.dashboard-page {
  max-width: 1200px;
  margin: 0 auto;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--c-text);
  margin-bottom: 32px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  background: var(--c-surface);
  border-radius: 16px;
  padding: 24px;
  box-shadow: var(--c-shadow-md);
  display: flex;
  align-items: center;
  gap: 20px;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-4px);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.stat-label {
  font-size: 14px;
  color: var(--c-text-muted);
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--c-text);
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.chart-card {
  background: var(--c-surface);
  border-radius: 16px;
  padding: 24px;
  box-shadow: var(--c-shadow-md);
}

.chart-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--c-text);
  margin-bottom: 20px;
}

.chart-placeholder {
  height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: var(--c-surface-alt);
  border-radius: 12px;
}

.recent-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.recent-card {
  background: var(--c-surface);
  border-radius: 16px;
  padding: 24px;
  box-shadow: var(--c-shadow-md);
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--c-text);
  margin-bottom: 16px;
}

.empty-text {
  font-size: 14px;
  color: var(--c-text-muted);
  margin-bottom: 16px;
}

.alert-badge {
  display: inline-block;
  padding: 8px 16px;
  background: rgba(255,107,107,0.15);
  color: #FF6B6B;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 16px;
}

.view-link {
  color: var(--c-primary);
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  transition: color 0.2s;
}

.view-link:hover {
  color: var(--c-primary-dark);
}

.funnel {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.funnel-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 16px;
  background: var(--c-surface-alt);
  border-radius: 10px;
}

.funnel-label {
  font-size: 14px;
  color: var(--c-text-secondary);
}

.funnel-value {
  font-size: 16px;
  font-weight: 600;
  color: var(--c-text);
}
</style>
