<template>
  <div class="page-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div>
        <h1 class="page-title">订单管理</h1>
        <p class="page-subtitle">查看和管理所有租赁订单</p>
      </div>
    </div>

    <!-- 搜索卡片 -->
    <div class="search-card">
      <div class="search-row">
        <div class="search-field">
          <label class="field-label">订单号</label>
          <el-input
            v-model="searchForm.order_no"
            placeholder="输入订单号搜索"
            clearable
            @keyup.enter="handleSearch"
            class="modern-input"
          >
            <template #prefix>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
            </template>
          </el-input>
        </div>
        <div class="search-field">
          <label class="field-label">订单状态</label>
          <el-select v-model="searchForm.status" placeholder="选择状态" clearable class="modern-select">
            <el-option label="待支付" value="pending" />
            <el-option label="已支付" value="paid" />
            <el-option label="租用中" value="rented" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </div>
        <div class="search-actions">
          <el-button type="primary" class="btn-primary" @click="handleSearch">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
            搜索
          </el-button>
          <el-button class="btn-ghost" @click="handleReset">重置</el-button>
        </div>
      </div>
    </div>

    <!-- 订单列表 -->
    <div class="data-card">
      <el-table :data="tableData" v-loading="loading" class="modern-table">
        <el-table-column prop="order_no" label="订单号" min-width="180">
          <template #default="{ row }">
            <div class="order-no">{{ row.order_no }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="user_id" label="用户" width="100">
          <template #default="{ row }">
            <div class="user-cell">
              <div class="user-avatar-sm">U</div>
              <span>#{{ row.user_id }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="order_type" label="类型" width="90">
          <template #default="{ row }">
            <span class="type-badge" :class="row.order_type">{{ getOrderTypeLabel(row.order_type) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="total_amount" label="金额" width="110">
          <template #default="{ row }">
            <span class="amount">¥{{ parseFloat(row.total_amount || 0).toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="110">
          <template #default="{ row }">
            <span class="status-badge" :class="row.status">{{ getStatusLabel(row.status) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" min-width="160">
          <template #default="{ row }">
            <span class="date-text">{{ formatDate(row.created_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="90" fixed="right">
          <template #default="{ row }">
            <el-button size="small" text type="primary" class="action-btn" @click="handleDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.per_page"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next"
          @change="loadOrders"
        />
      </div>
    </div>

    <!-- 订单详情 -->
    <el-dialog v-model="detailVisible" title="订单详情" width="560px" class="modern-dialog">
      <el-descriptions :column="2" border v-if="detailData">
        <el-descriptions-item label="订单号"><span class="mono">{{ detailData.order_no }}</span></el-descriptions-item>
        <el-descriptions-item label="用户ID">{{ detailData.user_id }}</el-descriptions-item>
        <el-descriptions-item label="订单类型">
          <span class="type-badge" :class="detailData.order_type">{{ getOrderTypeLabel(detailData.order_type) }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <span class="status-badge" :class="detailData.status">{{ getStatusLabel(detailData.status) }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="总金额"><span class="amount">¥{{ parseFloat(detailData.total_amount || 0).toFixed(2) }}</span></el-descriptions-item>
        <el-descriptions-item label="支付方式">{{ detailData.payment_method || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDate(detailData.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="支付时间">{{ formatDate(detailData.payment_time) || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script>
import { ElMessage } from 'element-plus'
import { getOrderList } from '@/api/order'

export default {
  name: 'OrderIndex',
  data() {
    return {
      tableData: [],
      loading: false,
      detailVisible: false,
      detailData: null,
      searchForm: {
        order_no: '',
        status: ''
      },
      pagination: {
        page: 1,
        per_page: 20,
        total: 0
      }
    }
  },
  methods: {
    async loadOrders() {
      this.loading = true
      try {
        const params = {
          page: this.pagination.page,
          per_page: this.pagination.per_page
        }
        if (this.searchForm.status) {
          params.status = this.searchForm.status
        }
        if (this.searchForm.order_no) {
          params.keyword = this.searchForm.order_no
        }

        const response = await getOrderList(params)
        if (response.code === 0 || response.code === 200) {
          this.tableData = response.data.list || []
          this.pagination.total = response.data.pagination?.total || 0
        }
      } catch (error) {
        ElMessage.error('加载订单列表失败')
      } finally {
        this.loading = false
      }
    },
    handleSearch() {
      this.pagination.page = 1
      this.loadOrders()
    },
    handleReset() {
      this.searchForm = { order_no: '', status: '' }
      this.pagination.page = 1
      this.loadOrders()
    },
    handleDetail(row) {
      this.detailData = row
      this.detailVisible = true
    },
    getStatusType(status) {
      const typeMap = {
        pending: 'warning',
        paid: 'info',
        rented: 'primary',
        completed: 'success',
        cancelled: 'danger'
      }
      return typeMap[status] || 'info'
    },
    getStatusLabel(status) {
      const labelMap = {
        pending: '待支付',
        paid: '已支付',
        rented: '租用中',
        completed: '已完成',
        cancelled: '已取消'
      }
      return labelMap[status] || status
    },
    getOrderTypeLabel(type) {
      const labelMap = {
        rental: '租赁',
        purchase: '购买',
        exchange: '换电'
      }
      return labelMap[type] || type
    },
    formatDate(date) {
      if (!date) return '-'
      return new Date(date).toLocaleString('zh-CN')
    }
  },
  mounted() {
    this.loadOrders()
  }
}
</script>

<style lang="scss" scoped>
.page-container {
  padding: 28px 32px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 28px;
}

.page-title {
  font-size: 24px;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -0.3px;
  margin-bottom: 4px;
}

.page-subtitle {
  font-size: 14px;
  color: #94a3b8;
}

.search-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 20px 24px;
  margin-bottom: 20px;
}

.search-row {
  display: flex;
  align-items: flex-end;
  gap: 16px;
  flex-wrap: wrap;
}

.search-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 180px;
  flex: 1;
}

.field-label {
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.modern-input {
  :deep(.el-input__wrapper) {
    border-radius: 10px;
    box-shadow: 0 0 0 1px #e2e8f0;
    background: #f8fafc;
    padding: 10px 14px;
    &:hover { box-shadow: 0 0 0 1px #cbd5e1; }
    &.is-focus { box-shadow: 0 0 0 2px rgba(99,102,241,0.2) !important; }
  }
}

.modern-select {
  :deep(.el-input__wrapper) {
    border-radius: 10px;
    box-shadow: 0 0 0 1px #e2e8f0;
    background: #f8fafc;
    &:hover { box-shadow: 0 0 0 1px #cbd5e1; }
  }
}

.search-actions {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-shrink: 0;
}

.btn-primary {
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  border: none;
  border-radius: 10px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  box-shadow: 0 2px 8px rgba(99,102,241,0.3);
  &:hover { box-shadow: 0 4px 12px rgba(99,102,241,0.4); transform: translateY(-1px); }
}

.btn-ghost {
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  color: #64748b;
  background: #fff;
  &:hover { background: #f8fafc; color: #334155; }
}

.data-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  overflow: hidden;
}

.modern-table {
  :deep(.el-table__header th) {
    background: #f8fafc;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #64748b;
    font-weight: 700;
    padding: 14px 16px;
  }

  :deep(.el-table__body td) {
    padding: 14px 16px;
    border-bottom: 1px solid #f1f5f9;
  }

  :deep(.el-table__row:hover td) {
    background: #f8fafc !important;
  }
}

.order-no {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 12px;
  color: #334155;
  background: #f1f5f9;
  padding: 3px 8px;
  border-radius: 6px;
  display: inline-block;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  .user-avatar-sm {
    width: 26px;
    height: 26px;
    border-radius: 50%;
    background: linear-gradient(135deg, #6366f1, #4f46e5);
    color: #fff;
    font-size: 11px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  span { font-size: 13px; color: #64748b; }
}

.type-badge {
  font-size: 12px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 20px;
  display: inline-block;
  &.rental { background: #dbeafe; color: #3b82f6; }
  &.purchase { background: #d1fae5; color: #10b981; }
  &.exchange { background: #fef3c7; color: #f59e0b; }
}

.amount {
  font-weight: 700;
  color: #0f172a;
  font-size: 14px;
}

.status-badge {
  font-size: 12px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 20px;
  display: inline-block;
  &.pending { background: #fef3c7; color: #d97706; }
  &.paid { background: #dbeafe; color: #3b82f6; }
  &.rented { background: #ede9fe; color: #7c3aed; }
  &.completed { background: #d1fae5; color: #059669; }
  &.cancelled { background: #fee2e2; color: #dc2626; }
}

.date-text { font-size: 13px; color: #64748b; }

.action-btn {
  font-size: 13px;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 8px;
}

.pagination-wrap {
  padding: 16px 20px;
  border-top: 1px solid #f1f5f9;
  display: flex;
  justify-content: flex-end;
}

.mono { font-family: monospace; font-size: 12px; }
</style>
