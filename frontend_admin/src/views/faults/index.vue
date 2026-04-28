<template>
  <div class="page-container">
    <div class="page-header">
      <div>
        <h1 class="page-title">故障报修管理</h1>
        <p class="page-subtitle">查看和处理用户提交的故障报修</p>
      </div>
    </div>

    <div class="search-card">
      <div class="search-row">
        <div class="search-field">
          <label class="field-label">工单号</label>
          <el-input
            v-model="searchForm.report_no"
            placeholder="输入工单号搜索"
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
          <label class="field-label">故障类型</label>
          <el-select v-model="searchForm.fault_type" placeholder="选择类型" clearable class="modern-select">
            <el-option label="电池故障" value="battery" />
            <el-option label="柜机故障" value="cabinet" />
            <el-option label="站点问题" value="station" />
            <el-option label="其他" value="other" />
          </el-select>
        </div>
        <div class="search-field">
          <label class="field-label">处理状态</label>
          <el-select v-model="searchForm.status" placeholder="选择状态" clearable class="modern-select">
            <el-option label="待处理" value="pending" />
            <el-option label="处理中" value="processing" />
            <el-option label="已完成" value="resolved" />
            <el-option label="已关闭" value="closed" />
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

    <div class="data-card">
      <el-table :data="tableData" v-loading="loading" class="modern-table">
        <el-table-column prop="report_no" label="工单号" min-width="160">
          <template #default="{ row }">
            <div class="report-no">{{ row.report_no }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="fault_type" label="故障类型" width="110">
          <template #default="{ row }">
            <span class="type-badge" :class="`type-${row.fault_type}`">{{ getFaultTypeLabel(row.fault_type) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="故障描述" min-width="200">
          <template #default="{ row }">
            <div class="description-text">{{ row.description }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="user_id" label="报修人" width="100">
          <template #default="{ row }">
            <div class="user-cell">
              <div class="user-avatar-sm">U</div>
              <span>#{{ row.user_id }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="contact_phone" label="联系电话" width="120">
          <template #default="{ row }">
            <span class="phone-text">{{ row.contact_phone }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <span class="status-badge" :class="`status-${row.status}`">{{ getStatusLabel(row.status) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="提交时间" min-width="160">
          <template #default="{ row }">
            <span class="date-text">{{ formatDate(row.created_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <div class="action-row">
              <el-button size="small" text type="primary" class="action-btn" @click="handleDetail(row)">详情</el-button>
              <el-button size="small" text class="action-btn success-text" @click="handleProcess(row)" v-if="row.status === 'pending'">处理</el-button>
              <el-button size="small" text class="action-btn warning-text" @click="handleResolve(row)" v-if="row.status === 'processing'">完成</el-button>
            </div>
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
          @change="loadFaultReports"
        />
      </div>
    </div>

    <el-dialog v-model="detailVisible" title="报修详情" width="600px">
      <div v-if="currentReport" class="detail-content">
        <div class="detail-row">
          <span class="detail-label">工单号:</span>
          <span class="detail-value">{{ currentReport.report_no }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">故障类型:</span>
          <span class="detail-value">{{ getFaultTypeLabel(currentReport.fault_type) }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">故障描述:</span>
          <span class="detail-value">{{ currentReport.description }}</span>
        </div>
        <div class="detail-row" v-if="currentReport.images && currentReport.images.length">
          <span class="detail-label">故障图片:</span>
          <div class="image-list">
            <el-image
              v-for="(img, idx) in currentReport.images"
              :key="idx"
              :src="img"
              :preview-src-list="currentReport.images"
              fit="cover"
              class="fault-image"
            />
          </div>
        </div>
        <div class="detail-row">
          <span class="detail-label">联系电话:</span>
          <span class="detail-value">{{ currentReport.contact_phone }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">状态:</span>
          <span class="status-badge" :class="currentReport.status">{{ getStatusLabel(currentReport.status) }}</span>
        </div>
        <div class="detail-row" v-if="currentReport.admin_remarks">
          <span class="detail-label">管理员备注:</span>
          <span class="detail-value">{{ currentReport.admin_remarks }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">提交时间:</span>
          <span class="detail-value">{{ formatDate(currentReport.created_at) }}</span>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="processVisible" title="处理报修" width="500px">
      <el-form :model="processForm" label-width="100px">
        <el-form-item label="处理状态">
          <el-select v-model="processForm.status" placeholder="选择状态">
            <el-option label="处理中" value="processing" />
            <el-option label="已完成" value="resolved" />
            <el-option label="已关闭" value="closed" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="processForm.admin_remarks"
            type="textarea"
            :rows="4"
            placeholder="请输入处理备注"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="processVisible = false">取消</el-button>
        <el-button type="primary" @click="submitProcess">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from '@/utils/request'

const loading = ref(false)
const tableData = ref([])
const detailVisible = ref(false)
const processVisible = ref(false)
const currentReport = ref(null)

const searchForm = reactive({
  report_no: '',
  fault_type: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  per_page: 20,
  total: 0
})

const processForm = reactive({
  status: '',
  admin_remarks: ''
})

const loadFaultReports = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.per_page,
      ...searchForm
    }
    const res = await axios.get('/admin/fault-reports', { params })
    tableData.value = res.data.list || []
    pagination.total = res.data.pagination?.total || 0
  } catch (error) {
    ElMessage.error('加载失败: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadFaultReports()
}

const handleReset = () => {
  searchForm.report_no = ''
  searchForm.fault_type = ''
  searchForm.status = ''
  handleSearch()
}

const handleDetail = (row) => {
  currentReport.value = row
  detailVisible.value = true
}

const handleProcess = (row) => {
  currentReport.value = row
  processForm.status = 'processing'
  processForm.admin_remarks = ''
  processVisible.value = true
}

const handleResolve = (row) => {
  currentReport.value = row
  processForm.status = 'resolved'
  processForm.admin_remarks = ''
  processVisible.value = true
}

const submitProcess = async () => {
  try {
    await axios.put(`/admin/fault-reports/${currentReport.value.id}`, processForm)
    ElMessage.success('处理成功')
    processVisible.value = false
    loadFaultReports()
  } catch (error) {
    ElMessage.error('处理失败: ' + (error.response?.data?.message || error.message))
  }
}

const getFaultTypeLabel = (type) => {
  const map = {
    battery: '电池故障',
    cabinet: '柜机故障',
    station: '站点问题',
    other: '其他'
  }
  return map[type] || type
}

const getStatusLabel = (status) => {
  const map = {
    pending: '待处理',
    processing: '处理中',
    resolved: '已完成',
    closed: '已关闭'
  }
  return map[status] || status
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

onMounted(() => {
  loadFaultReports()
})
</script>

<style lang="scss" scoped>
.page-container { padding: 28px 32px; }

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

.page-subtitle { font-size: 14px; color: #94a3b8; }

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

.search-actions { display: flex; gap: 10px; align-items: center; flex-shrink: 0; }

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

  :deep(.el-table__row:hover td) { background: #f8fafc !important; }
}

.report-no {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 12px;
  color: #334155;
  background: #f1f5f9;
  padding: 3px 8px;
  border-radius: 6px;
  display: inline-block;
}

.description-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #64748b;
  font-size: 13px;
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

.phone-text { color: #64748b; font-size: 13px; }

.type-badge {
  font-size: 12px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 20px;
  display: inline-block;
  &.type-battery { background: #fef3c7; color: #d97706; }
  &.type-cabinet { background: #dbeafe; color: #2563eb; }
  &.type-station { background: #fce7f3; color: #db2777; }
  &.type-other { background: #f3f4f6; color: #6b7280; }
}

.status-badge {
  font-size: 12px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 20px;
  display: inline-block;
  &.status-pending { background: #fef3c7; color: #d97706; }
  &.status-processing { background: #dbeafe; color: #3b82f6; }
  &.status-resolved { background: #d1fae5; color: #059669; }
  &.status-closed { background: #f3f4f6; color: #6b7280; }
}

.date-text { font-size: 13px; color: #64748b; }

.action-row { display: flex; gap: 4px; align-items: center; }

.action-btn { font-size: 13px; font-weight: 600; padding: 4px 8px; border-radius: 8px; }

.success-text { color: #10b981 !important; }
.warning-text { color: #f59e0b !important; }

.pagination-wrap {
  padding: 16px 20px;
  border-top: 1px solid #f1f5f9;
  display: flex;
  justify-content: flex-end;
}

.detail-content {
  padding: 20px 0;
}

.detail-row {
  display: flex;
  margin-bottom: 16px;
  align-items: flex-start;
}

.detail-label {
  width: 100px;
  color: #64748b;
  font-size: 14px;
  flex-shrink: 0;
}

.detail-value {
  flex: 1;
  color: #1e293b;
  font-size: 14px;
}

.image-list {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.fault-image {
  width: 100px;
  height: 100px;
  border-radius: 8px;
  cursor: pointer;
}
</style>
