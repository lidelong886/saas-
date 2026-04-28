<template>
  <div class="page-container">
    <div class="page-header">
      <div>
        <h1 class="page-title">消息通知管理</h1>
        <p class="page-subtitle">查看和管理系统消息通知</p>
      </div>
      <el-button type="primary" class="btn-primary" @click="handleSendNotification">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M5 12l7-7 7 7"/></svg>
        发送通知
      </el-button>
    </div>

    <div class="search-card">
      <div class="search-row">
        <div class="search-field">
          <label class="field-label">通知类型</label>
          <el-select v-model="searchForm.noti_type" placeholder="选择类型" clearable class="modern-select">
            <el-option label="订单通知" value="order" />
            <el-option label="换电通知" value="exchange" />
            <el-option label="系统公告" value="system" />
            <el-option label="报修反馈" value="fault" />
          </el-select>
        </div>
        <div class="search-field">
          <label class="field-label">用户ID</label>
          <el-input
            v-model="searchForm.user_id"
            placeholder="输入用户ID"
            clearable
            @keyup.enter="handleSearch"
            class="modern-input"
          />
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
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="noti_type" label="类型" width="110">
          <template #default="{ row }">
            <span class="type-badge" :class="`type-${row.noti_type}`">{{ getTypeLabel(row.noti_type) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="180">
          <template #default="{ row }">
            <div class="title-text">{{ row.title }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="content" label="内容" min-width="250">
          <template #default="{ row }">
            <div class="content-text">{{ row.content }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="user_id" label="接收用户" width="100">
          <template #default="{ row }">
            <div class="user-cell">
              <div class="user-avatar-sm">U</div>
              <span>#{{ row.user_id }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="is_read" label="状态" width="90">
          <template #default="{ row }">
            <span class="status-badge" :class="row.is_read ? 'status-read' : 'status-unread'">
              {{ row.is_read ? '已读' : '未读' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="发送时间" min-width="160">
          <template #default="{ row }">
            <span class="date-text">{{ formatDate(row.created_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <div class="action-row">
              <el-button size="small" text type="primary" class="action-btn" @click="handleDetail(row)">详情</el-button>
              <el-button size="small" text type="danger" class="action-btn" @click="handleDelete(row)">删除</el-button>
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
          @change="loadNotifications"
        />
      </div>
    </div>

    <el-dialog v-model="detailVisible" title="通知详情" width="600px">
      <div v-if="currentNotification" class="detail-content">
        <div class="detail-row">
          <span class="detail-label">ID:</span>
          <span class="detail-value">{{ currentNotification.id }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">类型:</span>
          <span class="detail-value">{{ getTypeLabel(currentNotification.noti_type) }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">标题:</span>
          <span class="detail-value">{{ currentNotification.title }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">内容:</span>
          <span class="detail-value">{{ currentNotification.content }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">接收用户:</span>
          <span class="detail-value">#{{ currentNotification.user_id }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">状态:</span>
          <span class="status-badge" :class="currentNotification.is_read ? 'status-read' : 'status-unread'">
            {{ currentNotification.is_read ? '已读' : '未读' }}
          </span>
        </div>
        <div class="detail-row">
          <span class="detail-label">发送时间:</span>
          <span class="detail-value">{{ formatDate(currentNotification.created_at) }}</span>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="sendVisible" title="发送通知" width="600px">
      <el-form :model="sendForm" label-width="100px">
        <el-form-item label="通知类型">
          <el-select v-model="sendForm.noti_type" placeholder="选择类型">
            <el-option label="订单通知" value="order" />
            <el-option label="换电通知" value="exchange" />
            <el-option label="系统公告" value="system" />
            <el-option label="报修反馈" value="fault" />
          </el-select>
        </el-form-item>
        <el-form-item label="接收用户">
          <el-input v-model="sendForm.user_id" placeholder="输入用户ID，留空则发送给所有用户" />
        </el-form-item>
        <el-form-item label="标题">
          <el-input v-model="sendForm.title" placeholder="请输入通知标题" maxlength="100" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input
            v-model="sendForm.content"
            type="textarea"
            :rows="4"
            placeholder="请输入通知内容"
            maxlength="500"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="sendVisible = false">取消</el-button>
        <el-button type="primary" @click="submitSend">发送</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from '@/utils/request'

const loading = ref(false)
const tableData = ref([])
const detailVisible = ref(false)
const sendVisible = ref(false)
const currentNotification = ref(null)

const searchForm = reactive({
  noti_type: '',
  user_id: ''
})

const pagination = reactive({
  page: 1,
  per_page: 20,
  total: 0
})

const sendForm = reactive({
  noti_type: 'system',
  user_id: '',
  title: '',
  content: ''
})

const loadNotifications = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.per_page,
      ...searchForm
    }
    const res = await axios.get('/admin/notifications', { params })
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
  loadNotifications()
}

const handleReset = () => {
  searchForm.noti_type = ''
  searchForm.user_id = ''
  handleSearch()
}

const handleDetail = (row) => {
  currentNotification.value = row
  detailVisible.value = true
}

const handleSendNotification = () => {
  sendForm.noti_type = 'system'
  sendForm.user_id = ''
  sendForm.title = ''
  sendForm.content = ''
  sendVisible.value = true
}

const submitSend = async () => {
  if (!sendForm.title || !sendForm.content) {
    ElMessage.warning('请填写标题和内容')
    return
  }

  try {
    await axios.post('/admin/notifications', sendForm)
    ElMessage.success('发送成功')
    sendVisible.value = false
    loadNotifications()
  } catch (error) {
    ElMessage.error('发送失败: ' + (error.response?.data?.message || error.message))
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除这条通知吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await axios.delete(`/admin/notifications/${row.id}`)
    ElMessage.success('删除成功')
    loadNotifications()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + (error.response?.data?.message || error.message))
    }
  }
}

const getTypeLabel = (type) => {
  const map = {
    order: '订单通知',
    exchange: '换电通知',
    system: '系统公告',
    fault: '报修反馈'
  }
  return map[type] || type
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

onMounted(() => {
  loadNotifications()
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

.title-text {
  font-weight: 600;
  color: #0f172a;
  font-size: 14px;
}

.content-text {
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

.type-badge {
  font-size: 12px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 20px;
  display: inline-block;
  &.type-order { background: #dbeafe; color: #2563eb; }
  &.type-exchange { background: #d1fae5; color: #059669; }
  &.type-system { background: #fef3c7; color: #d97706; }
  &.type-fault { background: #fce7f3; color: #db2777; }
}

.status-badge {
  font-size: 12px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 20px;
  display: inline-block;
  &.status-read { background: #d1fae5; color: #059669; }
  &.status-unread { background: #fef3c7; color: #d97706; }
}

.date-text { font-size: 13px; color: #64748b; }

.action-row { display: flex; gap: 4px; align-items: center; }

.action-btn { font-size: 13px; font-weight: 600; padding: 4px 8px; border-radius: 8px; }

.danger-text { color: #ef4444 !important; }

.pagination-wrap {
  padding: 16px 20px;
  border-top: 1px solid #f1f5f9;
  display: flex;
  justify-content: flex-end;
}

.detail-content { padding: 20px 0; }

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
</style>
