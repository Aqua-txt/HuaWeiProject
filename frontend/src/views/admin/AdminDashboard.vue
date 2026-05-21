<template>
  <div class="admin-dashboard">
    <!-- Overview: Today -->
    <el-row :gutter="20" class="overview">
      <el-col :span="8">
        <el-card shadow="hover" class="overview-card">
          <div class="stat">
            <div class="stat-value">{{ overview.today_orders ?? '-' }}</div>
            <div class="stat-label">今日订单</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="overview-card">
          <div class="stat">
            <div class="stat-value">{{ overview.today_products ?? '-' }}</div>
            <div class="stat-label">今日发布</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="overview-card">
          <div class="stat">
            <div class="stat-value">{{ overview.today_users ?? '-' }}</div>
            <div class="stat-label">今日新增用户</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Overview: Totals -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="6">
        <el-card shadow="hover" class="overview-card total-card">
          <div class="stat">
            <div class="stat-value total">{{ overview.total_products ?? '-' }}</div>
            <div class="stat-label">商品总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="overview-card total-card">
          <div class="stat">
            <div class="stat-value total">{{ overview.total_users ?? '-' }}</div>
            <div class="stat-label">用户总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="overview-card total-card">
          <div class="stat">
            <div class="stat-value total">{{ overview.total_orders ?? '-' }}</div>
            <div class="stat-label">订单总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="overview-card total-card">
          <div class="stat">
            <div class="stat-value total">{{ overview.paid_orders ?? '-' }}</div>
            <div class="stat-label">已付款 / 已完成 {{ overview.completed_orders != null ? overview.completed_orders : '' }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Charts -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="16">
        <el-card>
          <template #header><span>近30天趋势</span></template>
          <div class="trend-chart" v-if="trend.length">
            <div class="chart-bars">
              <div class="bar-group" v-for="(d, i) in trend" :key="i">
                <div class="bars-row">
                  <div class="bar products-bar" :style="{ height: barHeight(d.products, maxTrend) + 'px' }" :title="d.products + '件'"></div>
                  <div class="bar orders-bar" :style="{ height: barHeight(d.orders, maxTrend) + 'px' }" :title="d.orders + '单'"></div>
                  <div class="bar users-bar" :style="{ height: barHeight(d.users, maxTrend) + 'px' }" :title="d.users + '人'"></div>
                </div>
                <div class="bar-date">{{ d.date }}</div>
              </div>
            </div>
            <div class="chart-legend">
              <span><span class="dot" style="background:#5B8DEF"></span>发布</span>
              <span><span class="dot" style="background:#06D6A0"></span>订单</span>
              <span><span class="dot" style="background:#FFD166"></span>用户</span>
            </div>
          </div>
          <div v-else class="chart-empty">暂无数据</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header><span>商品分类分布</span></template>
          <div class="category-chart" v-if="categoryDistribution.length">
            <div class="cat-bar-wrap" v-for="c in categoryDistribution" :key="c.category">
              <span class="cat-label">{{ c.category }}</span>
              <div class="cat-bar-track">
                <div class="cat-bar-fill" :style="{ width: barPercent(c.count, maxCat) + '%' }"></div>
              </div>
              <span class="cat-count">{{ c.count }}</span>
            </div>
          </div>
          <div v-else class="chart-empty">暂无数据</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getDashboard } from '../../api/admin'

const overview = ref({})
const trend = ref([])
const categoryDistribution = ref([])

const maxTrend = computed(() => {
  let max = 1
  for (const d of trend.value) {
    max = Math.max(max, d.products, d.orders, d.users)
  }
  return max
})

const maxCat = computed(() => {
  let max = 1
  for (const c of categoryDistribution.value) {
    max = Math.max(max, c.count)
  }
  return max
})

function barHeight(val, max) {
  return Math.max(2, (val / max) * 200)
}

function barPercent(val, max) {
  return Math.round((val / max) * 100)
}

async function loadDashboard() {
  try {
    const res = await getDashboard()
    overview.value = res.data.overview
    trend.value = res.data.trend
    categoryDistribution.value = res.data.category_distribution
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  const token = localStorage.getItem('admin_token')
  if (!token) {
    window.location.href = '/admin/login'
    return
  }
  loadDashboard()
})
</script>

<style scoped>
.admin-dashboard { padding: 20px; }

.overview-card { text-align: center; }

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #409eff;
}

.stat-value.total {
  color: #333;
  font-size: 24px;
}

.stat-label {
  font-size: 13px;
  color: #999;
  margin-top: 6px;
}

/* Trend chart */
.trend-chart { padding: 8px 0; }

.chart-bars {
  display: flex;
  align-items: flex-end;
  gap: 2px;
  height: 220px;
  padding-bottom: 4px;
  overflow-x: auto;
}

.bar-group {
  flex: 1;
  min-width: 14px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  height: 100%;
}

.bars-row {
  display: flex;
  gap: 1px;
  align-items: flex-end;
  height: 200px;
  width: 100%;
  justify-content: center;
}

.bar {
  width: 3px;
  border-radius: 1px;
  min-height: 1px;
  transition: opacity 0.2s;
}
.bar:hover { opacity: 0.7; }

.products-bar { background: #5B8DEF; }
.orders-bar { background: #06D6A0; }
.users-bar { background: #FFD166; }

.bar-date {
  font-size: 10px;
  color: #999;
  margin-top: 4px;
  white-space: nowrap;
  transform: rotate(-45deg);
  transform-origin: center;
  width: 0;
}

.chart-legend {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 16px;
  font-size: 12px;
  color: #666;
}
.chart-legend .dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 2px;
  margin-right: 4px;
  vertical-align: middle;
}

/* Category chart */
.category-chart { padding: 10px 0; }

.cat-bar-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.cat-label {
  width: 44px;
  font-size: 13px;
  color: #333;
  text-align: right;
}

.cat-bar-track {
  flex: 1;
  height: 22px;
  background: #f0f4f8;
  border-radius: 11px;
  overflow: hidden;
}

.cat-bar-fill {
  height: 100%;
  background: linear-gradient(135deg, #5B8DEF, #4CC9F0);
  border-radius: 11px;
  transition: width 0.5s ease;
  min-width: 4px;
}

.cat-count {
  width: 36px;
  font-size: 13px;
  color: #666;
  font-weight: 600;
}

.chart-empty {
  height: 220px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 14px;
}

.total-card .stat-label {
  font-size: 12px;
}
</style>
