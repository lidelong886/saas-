<template>
  <div class="page-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div>
        <h1 class="page-title">换电记录</h1>
        <p class="page-subtitle">查看所有换电订单记录</p>
      </div>
    </div>

    <!-- 搜索卡片 -->
    <div class="search-card">
      <div class="search-row">
        <div class="search-field">
          <label class="field-label">订单号</label>
          <el-input v-model="searchForm.order_no" placeholder="输入订单号" clearable @keyup.enter="loadRecords" class="modern-input" />
        </div>
        <div class="search-field">
          <label class="field-label">用户名</label>
          <el-input v-model="searchForm.user_name" placeholder="输入用户名" clearable @keyup.enter="loadRecords" class="modern-input" />
        </div>
        <div class="search-field">
          <label class="field-label">订单状态</label>
          <el-select v-model="searchForm.status" placeholder="全部" clearable class="modern-select">
            <el-option label="待支付" value="pending" />
            <el-option label="已支付" value="paid" />
            <el-option label="进行中" value="rented" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
            <el-option label="已退款" value="refunded" />
          </el-select>
        </div>
        <div class="search-actions">
          <el-button type="primary" class="btn-primary" @click="loadRecords">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
            搜索
          </el-button>
          <el-button class="btn-ghost" @click="resetSearch">重置</el-button>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stat-cards">
      <div class="stat-card">
        <div class="stat-num">{{ statTotal }}</div>
        <div class="stat-label">总换电数</div>
      </div>
      <div class="stat-card">
        <div class="stat-num">{{ statCompleted }}</div>
        <div class="stat-label">已完成</div>
      </div>
      <div class="stat-card">
        <div class="stat-num">{{ statPending }}</div>
        <div class="stat-label">待处理</div>
      </div>
      <div class="stat-card">
        <div class="stat-num">{{ statRevenue }}</div>
        <div class="stat-label">总营收(元)</div>
      </div>
    </div>

    <!-- 数据卡片 -->
    <div class="data-card">
      <el-table :data="tableData" v-loading="loading" class="modern-table">
        <el-table-column prop="order_no" label="订单号" min-width="200">
          <template #default="{ row }">
            <div class="order-no-cell">{{ row.order_no }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="user_name" label="用户" width="120">
          <template #default="{ row }">
            <div class="user-cell">
              <div class="user-avatar-sm">{{ (row.user_name || 'U')[0].toUpperCase() }}</div>
              <span>{{ row.user_name || '用户#' + row.user_id }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="station_name" label="站点" min-width="160">
          <template #default="{ row }">
            <span>{{ row.station_name || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="battery_code" label="电池" width="140">
          <template #default="{ row }">
            <span class="battery-code">{{ row.battery_code || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="exchange_fee" label="换电费" width="100">
          <template #default="{ row }">
            <span class="fee-value">¥{{ Number(row.exchange_fee || 0).toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="payment_method" label="支付方式" width="100">
          <template #default="{ row }">
            <span class="pay-method">{{ methodMap[row.payment_method] || row.payment_method || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="source" label="来源" width="100">
          <template #default="{ row }">
            <span class="source-tag" :class="'source-' + row.source">{{ sourceMap[row.source] || row.source || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small" effect="light">
              {{ statusMap[row.status] || row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" min-width="170">
          <template #default="{ row }">
            <span class="time-text">{{ formatTime(row.created_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @current-change="loadRecords"
          @size-change="loadRecords"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const loading = ref(false)
const tableData = ref([])

const searchForm = reactive({
  order_no: '',
  user_name: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const statTotal = ref(0)
const statCompleted = ref(0)
const statPending = ref(0)
const statRevenue = ref('0.00')

const statusMap = {
  pending: '待支付',
  paid: '已支付',
  rented: '进行中',
  completed: '已完成',
  cancelled: '已取消',
  refunded: '已退款'
}

const statusTypeMap = {
  pending: 'warning',
  paid: 'success',
  rented: 'primary',
  completed: 'info',
  cancelled: 'danger',
  refunded: 'info'
}

const methodMap = {
  wechat: '微信',
  alipay: '支付宝',
  balance: '余额'
}

const sourceMap = {
  miniapp: '小程序',
  admin: '管理后台',
  api: 'API'
}

function statusType(s) { return statusTypeMap[s] || '' }

onMounted(() => { loadRecords() })

function loadRecords() {
  loading.value = true
  const params = {
    page: pagination.page,
    per_page: pagination.pageSize,
    order_type: 'exchange'
  }
  if (searchForm.order_no) params.order_no = searchForm.order_no
  if (searchForm.user_name) params.user_name = searchForm.user_name
  if (searchForm.status) params.status = searchForm.status

  request.get('/admin/orders', { params })
    .then(res => {
      const data = res.data || {}
      tableData.value = (data.list || data.items || [])
      const p = data.pagination || {}
      pagination.total = p.total || 0

      // 统计
      statTotal.value = p.total || tableData.value.length
      statCompleted.value = tableData.value.filter(r => r.status === 'completed').length
      statPending.value = tableData.value.filter(r => ['pending', 'paid', 'rented'].includes(r.status)).length
      const totalRevenue = tableData.value.reduce((s, r) => s + Number(r.exchange_fee || 0), 0)
      statRevenue.value = totalRevenue.toFixed(2)
    })
    .catch(() => ElMessage.error('加载换电记录失败'))
    .finally(() => { loading.value = false })
}

function resetSearch() {
  searchForm.order_no = ''
  searchForm.user_name = ''
  searchForm.status = ''
  pagination.page = 1
  loadRecords()
}

function viewDetail(row) {
  ElMessage.info(`订单号：${row.order_no}，该功能由订单详情页提供`)
}

function formatTime(time) {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN', { hour12: false })
}
</script>

<style scoped>
.page-container { padding: 24px; min-height: 100vh; background: #f5f7fa; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; }
.page-title { font-size: 24px; font-weight: 700; color: #1e293b; margin: 0 0 4px; }
.page-subtitle { font-size: 14px; color: #64748b; margin: 0; }
.search-card { background: #fff; border-radius: 16px; padding: 20px 24px; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.search-row { display: flex; flex-wrap: wrap; gap: 16px; align-items: flex-end; }
.search-field { display: flex; flex-direction: column; gap: 6px; min-width: 180px; }
.field-label { font-size: 13px; color: #64748b; font-weight: 500; }
.modern-input, .modern-select { width: 100%; }
.search-actions { display: flex; gap: 8px; align-items: flex-end; }
.btn-primary { background: linear-gradient(135deg, #6366f1, #7c3aed); border: none; color: #fff; border-radius: 8px; display: flex; align-items: center; gap: 6px; }
.btn-ghost { border: 1px solid #e2e8f0; color: #64748b; border-radius: 8px; background: #fff; }
.stat-cards { display: flex; gap: 16px; margin-bottom: 16px; }
.stat-card { flex: 1; background: #fff; border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.06); cursor: default; transition: all 0.2s; }
.stat-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.stat-num { font-size: 28px; font-weight: 700; color: #1e293b; }
.stat-label { font-size: 13px; color: #64748b; margin-top: 4px; }
.data-card { background: #fff; border-radius: 16px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.modern-table { font-size: 14px; }
.order-no-cell { font-size: 12px; color: #64748b; letter-spacing: 0.5px; }
.user-cell { display: flex; align-items: center; gap: 8px; }
.user-avatar-sm { width: 28px; height: 28px; border-radius: 50%; background: #64748B; color: #fff; font-size: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.battery-code { font-weight: 600; color: #1e293b; }
.fee-value { font-weight: 700; color: #ef4444; }
.pay-method { color: #64748b; font-size: 13px; }
.source-tag { padding: 2px 8px; border-radius: 4px; font-size: 12px; }
.source-miniapp { background: #f0fdf4; color: #166534; }
.source-admin { background: #eff6ff; color: #1d4ed8; }
.source-api { background: #fef9c3; color: #92400e; }
.time-text { color: #94a3b8; font-size: 12px; }
.pagination-wrap { display: flex; justify-content: flex-end; margin-top: 20px; }
</style>
