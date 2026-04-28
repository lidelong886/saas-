<template>
  <div class="page-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div>
        <h1 class="page-title">套餐管理</h1>
        <p class="page-subtitle">创建和管理电池租赁套餐</p>
      </div>
      <el-button type="primary" class="btn-primary" @click="showCreateDialog">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        新增套餐
      </el-button>
    </div>

    <!-- 搜索卡片 -->
    <div class="search-card">
      <div class="search-row">
        <div class="search-field">
          <label class="field-label">套餐名称</label>
          <el-input v-model="searchForm.name" placeholder="输入名称搜索" clearable @keyup.enter="loadPackages" class="modern-input" />
        </div>
        <div class="search-field">
          <label class="field-label">套餐类型</label>
          <el-select v-model="searchForm.package_type" placeholder="全部" clearable class="modern-select">
            <el-option label="租用套餐" value="rental" />
            <el-option label="购买套餐" value="purchase" />
            <el-option label="换电套餐" value="exchange" />
          </el-select>
        </div>
        <div class="search-field">
          <label class="field-label">状态</label>
          <el-select v-model="searchForm.is_active" placeholder="全部" clearable class="modern-select">
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </div>
        <div class="search-actions">
          <el-button type="primary" class="btn-primary" @click="loadPackages">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
            搜索
          </el-button>
          <el-button class="btn-ghost" @click="resetSearch">重置</el-button>
        </div>
      </div>
    </div>

    <!-- 数据卡片 -->
    <div class="data-card">
      <el-table :data="tableData" v-loading="loading" class="modern-table">
        <el-table-column prop="id" label="ID" width="80">
          <template #default="{ row }">
            <span class="id-badge">#{{ row.id }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="套餐名称" min-width="160">
          <template #default="{ row }">
            <div class="package-name">{{ row.name }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="package_type" label="类型" width="120">
          <template #default="{ row }">
            <span class="type-badge" :class="'type-' + row.package_type">
              {{ typeMap[row.package_type] || row.package_type }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="hours" label="时长" width="100">
          <template #default="{ row }">
            <span>{{ row.hours || '-' }}h</span>
          </template>
        </el-table-column>
        <el-table-column prop="price" label="价格" width="120">
          <template #default="{ row }">
            <span class="price-value">¥{{ (row.price || 0).toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="deposit_amount" label="押金" width="100">
          <template #default="{ row }">
            <span>¥{{ (row.deposit_amount || 0).toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="exchange_fee" label="换电费" width="100">
          <template #default="{ row }">
            <span>¥{{ (row.exchange_fee || 0).toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small" effect="light">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" min-width="160">
          <template #default="{ row }">
            <span class="time-text">{{ formatTime(row.created_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <div class="action-btns">
              <el-button type="primary" link size="small" @click="showEditDialog(row)">编辑</el-button>
              <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
            </div>
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
          @current-change="loadPackages"
          @size-change="loadPackages"
        />
      </div>
    </div>

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑套餐' : '新增套餐'"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" class="package-form">
        <el-form-item label="套餐名称" prop="name">
          <el-input v-model="form.name" placeholder="如：日租套餐" />
        </el-form-item>
        <el-form-item label="套餐类型" prop="package_type">
          <el-select v-model="form.package_type" placeholder="请选择" class="full-width">
            <el-option label="租用套餐" value="rental" />
            <el-option label="购买套餐" value="purchase" />
            <el-option label="换电套餐" value="exchange" />
          </el-select>
        </el-form-item>
        <el-form-item label="电池型号" prop="battery_model">
          <el-input v-model="form.battery_model" placeholder="如：BT-2024-PRO" />
        </el-form-item>
        <el-form-item label="时长(小时)" prop="hours">
          <el-input-number v-model="form.hours" :min="1" :max="720" /> <span class="unit">小时</span>
        </el-form-item>
        <el-form-item label="价格(元)" prop="price">
          <el-input-number v-model="form.price" :min="0" :precision="2" :max="99999" /> <span class="unit">元</span>
        </el-form-item>
        <el-form-item label="押金(元)" prop="deposit_amount">
          <el-input-number v-model="form.deposit_amount" :min="0" :precision="2" :max="99999" /> <span class="unit">元</span>
        </el-form-item>
        <el-form-item label="换电费(元)" prop="exchange_fee">
          <el-input-number v-model="form.exchange_fee" :min="0" :precision="2" :max="99999" /> <span class="unit">元</span>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="套餐说明..." />
        </el-form-item>
        <el-form-item label="启用状态">
          <el-switch v-model="form.is_active" />
          <span class="switch-label">{{ form.is_active ? '启用' : '禁用' }}</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

const loading = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref(null)
const editingId = ref(null)

const searchForm = reactive({
  name: '',
  package_type: '',
  is_active: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const form = reactive({
  name: '',
  package_type: 'rental',
  battery_model: '',
  hours: 24,
  price: 0,
  deposit_amount: 0,
  exchange_fee: 0,
  description: '',
  is_active: true
})

const rules = {
  name: [{ required: true, message: '请输入套餐名称', trigger: 'blur' }],
  package_type: [{ required: true, message: '请选择套餐类型', trigger: 'change' }],
  price: [{ required: true, message: '请输入价格', trigger: 'blur' }]
}

const typeMap = {
  rental: '租用',
  purchase: '购买',
  exchange: '换电'
}

onMounted(() => {
  loadPackages()
})

function loadPackages() {
  loading.value = true
  const params = {
    page: pagination.page,
    per_page: pagination.pageSize
  }
  if (searchForm.name) params.name = searchForm.name
  if (searchForm.package_type) params.package_type = searchForm.package_type
  if (searchForm.is_active !== '') params.is_active = searchForm.is_active

  request.get('/package/admin/list', { params })
    .then(res => {
      const data = res.data || {}
      tableData.value = data.list || data.items || []
      const p = data.pagination || {}
      pagination.total = p.total || 0
    })
    .catch(() => ElMessage.error('加载套餐列表失败'))
    .finally(() => { loading.value = false })
}

function resetSearch() {
  searchForm.name = ''
  searchForm.package_type = ''
  searchForm.is_active = ''
  pagination.page = 1
  loadPackages()
}

function showCreateDialog() {
  isEdit.value = false
  editingId.value = null
  Object.assign(form, {
    name: '',
    package_type: 'rental',
    battery_model: '',
    hours: 24,
    price: 0,
    deposit_amount: 0,
    exchange_fee: 0,
    description: '',
    is_active: true
  })
  dialogVisible.value = true
}

function showEditDialog(row) {
  isEdit.value = true
  editingId.value = row.id
  Object.assign(form, {
    name: row.name || '',
    package_type: row.package_type || 'rental',
    battery_model: row.battery_model || '',
    hours: row.hours || 24,
    price: row.price || 0,
    deposit_amount: row.deposit_amount || 0,
    exchange_fee: row.exchange_fee || 0,
    description: row.description || '',
    is_active: row.is_active !== false
  })
  dialogVisible.value = true
}

function handleSubmit() {
  formRef.value.validate(valid => {
    if (!valid) return
    submitting.value = true

    const payload = { ...form }

    const action = isEdit.value
      ? request.put(`/package/admin/${editingId.value}`, payload)
      : request.post('/package/admin', payload)

    action.then(() => {
      ElMessage.success(isEdit.value ? '套餐更新成功' : '套餐创建成功')
      dialogVisible.value = false
      loadPackages()
    }).catch(() => {
      ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
    }).finally(() => {
      submitting.value = false
    })
  })
}

function handleDelete(row) {
  ElMessageBox.confirm(`确定删除套餐「${row.name}」吗？`, '删除确认', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    request.delete(`/package/admin/${row.id}`)
      .then(() => {
        ElMessage.success('删除成功')
        loadPackages()
      })
      .catch(() => ElMessage.error('删除失败'))
  }).catch(() => {})
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
.page-header .btn-primary { display: flex; align-items: center; gap: 6px; }
.search-card { background: #fff; border-radius: 16px; padding: 20px 24px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.search-row { display: flex; flex-wrap: wrap; gap: 16px; align-items: flex-end; }
.search-field { display: flex; flex-direction: column; gap: 6px; min-width: 180px; }
.field-label { font-size: 13px; color: #64748b; font-weight: 500; }
.modern-input, .modern-select { width: 100%; }
.search-actions { display: flex; gap: 8px; align-items: flex-end; }
.btn-primary { background: linear-gradient(135deg, #6366f1, #7c3aed); border: none; color: #fff; border-radius: 8px; }
.btn-ghost { border: 1px solid #e2e8f0; color: #64748b; border-radius: 8px; background: #fff; }
.data-card { background: #fff; border-radius: 16px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.modern-table { font-size: 14px; }
.id-badge { color: #94a3b8; font-size: 13px; }
.package-name { font-weight: 600; color: #1e293b; }
.type-badge { padding: 2px 10px; border-radius: 4px; font-size: 12px; font-weight: 500; }
.type-rental { background: #eff6ff; color: #1d4ed8; }
.type-purchase { background: #f0fdf4; color: #166534; }
.type-exchange { background: #fef9c3; color: #92400e; }
.price-value { font-weight: 700; color: #ef4444; }
.time-text { color: #94a3b8; font-size: 13px; }
.action-btns { display: flex; gap: 8px; }
.pagination-wrap { display: flex; justify-content: flex-end; margin-top: 20px; }
.package-form .full-width { width: 100%; }
.unit { margin-left: 8px; color: #64748b; font-size: 14px; }
.switch-label { margin-left: 10px; font-size: 13px; color: #64748b; }
</style>
