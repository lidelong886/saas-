<template>
  <div class="page-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div>
        <h1 class="page-title">用户管理</h1>
        <p class="page-subtitle">管理所有注册用户</p>
      </div>
      <el-button type="primary" class="btn-primary" @click="showCreateDialog">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        新增用户
      </el-button>
    </div>

    <!-- 搜索卡片 -->
    <div class="search-card">
      <div class="search-row">
        <div class="search-field">
          <label class="field-label">关键词</label>
          <el-input
            v-model="searchForm.keyword"
            placeholder="用户名 / 手机号 / 邮箱"
            clearable
            @keyup.enter="loadUsers"
            class="modern-input"
          >
            <template #prefix>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
            </template>
          </el-input>
        </div>
        <div class="search-actions">
          <el-button type="primary" class="btn-primary" @click="loadUsers">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
            搜索
          </el-button>
          <el-button class="btn-ghost" @click="resetSearch">重置</el-button>
        </div>
      </div>
    </div>

    <!-- 用户列表 -->
    <div class="data-card">
      <el-table :data="users" v-loading="loading" class="modern-table">
        <el-table-column prop="id" label="ID" width="80">
          <template #default="{ row }">
            <span class="user-id">#{{ row.id }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="username" label="用户" min-width="160">
          <template #default="{ row }">
            <div class="user-cell">
              <div class="user-avatar-lg">{{ (row.nickname || row.username || 'U').charAt(0).toUpperCase() }}</div>
              <div class="user-detail">
                <div class="username">{{ row.nickname || row.username }}</div>
                <div class="user-sub">{{ row.username }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="手机号" width="140">
          <template #default="{ row }">
            <span class="phone-text">{{ row.phone || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="email" label="邮箱" min-width="200">
          <template #default="{ row }">
            <span class="email-text">{{ row.email || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="is_rider" label="骑手" width="80">
          <template #default="{ row }">
            <span class="badge" :class="row.is_rider ? 'rider' : 'normal'">
              {{ row.is_rider ? '骑手' : '普通' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="balance" label="余额" width="110">
          <template #default="{ row }">
            <span class="balance">¥{{ parseFloat(row.balance || 0).toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="90">
          <template #default="{ row }">
            <span class="badge" :class="row.is_active ? 'active' : 'banned'">
              {{ row.is_active ? '正常' : '禁用' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" min-width="160">
          <template #default="{ row }">
            <span class="date-text">{{ row.created_at ? new Date(row.created_at).toLocaleDateString('zh-CN', { year:'numeric', month:'2-digit', day:'2-digit' }) : '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <div class="action-row">
              <el-button size="small" text type="primary" class="action-btn" @click="showEditDialog(row)">编辑</el-button>
              <el-button size="small" text :class="row.is_active ? 'danger-text' : 'success-text'" @click="toggleStatus(row)">
                {{ row.is_active ? '禁用' : '启用' }}
              </el-button>
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
          @size-change="loadUsers"
          @current-change="loadUsers"
        />
      </div>
    </div>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑用户' : '新增用户'" width="500px" class="modern-dialog">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px" class="dialog-form">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!isEdit">
          <el-input v-model="form.password" type="password" show-password placeholder="请输入密码" />
        </el-form-item>
        <el-form-item label="昵称">
          <el-input v-model="form.nickname" placeholder="请输入昵称" />
        </el-form-item>
        <el-form-item label="骑手">
          <el-switch v-model="form.is_rider" active-text="是" inactive-text="否" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button class="btn-ghost" @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" class="btn-primary" @click="submitForm" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { getUserList, createUser, updateUser, deleteUser, toggleUserStatus } from '@/api/user'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'Users',
  data() {
    return {
      loading: false,
      submitting: false,
      users: [],
      searchForm: { keyword: '' },
      pagination: { page: 1, per_page: 20, total: 0 },
      dialogVisible: false,
      isEdit: false,
      currentUserId: null,
      form: { username: '', phone: '', email: '', password: '', nickname: '', is_rider: false },
      rules: {
        username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
        phone: [{ required: true, message: '请输入手机号', trigger: 'blur' }],
        email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }],
        password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
      }
    }
  },
  mounted() { this.loadUsers() },
  methods: {
    async loadUsers() {
      this.loading = true
      try {
        const res = await getUserList({
          page: this.pagination.page,
          per_page: this.pagination.per_page,
          keyword: this.searchForm.keyword
        })
        this.users = res.data?.list || []
        this.pagination.total = res.data?.pagination?.total || 0
      } catch (error) {
        console.error('加载用户列表失败:', error)
      } finally {
        this.loading = false
      }
    },
    resetSearch() {
      this.searchForm.keyword = ''
      this.pagination.page = 1
      this.loadUsers()
    },
    showCreateDialog() {
      this.isEdit = false
      this.form = { username: '', phone: '', email: '', password: '', nickname: '', is_rider: false }
      this.dialogVisible = true
    },
    showEditDialog(row) {
      this.isEdit = true
      this.currentUserId = row.id
      this.form = { ...row }
      this.dialogVisible = true
    },
    async submitForm() {
      try {
        await this.$refs.formRef.validate()
        this.submitting = true
        if (this.isEdit) {
          await updateUser(this.currentUserId, this.form)
          ElMessage.success('更新成功')
        } else {
          await createUser(this.form)
          ElMessage.success('创建成功')
        }
        this.dialogVisible = false
        this.loadUsers()
      } catch {}
      finally { this.submitting = false }
    },
    async toggleStatus(row) {
      try {
        await toggleUserStatus(row.id, !row.is_active)
        ElMessage.success(row.is_active ? '已禁用' : '已启用')
        this.loadUsers()
      } catch {}
    },
    handleDelete(row) {
      ElMessageBox.confirm(`确定删除用户"${row.username}"吗？`, '提示', { type: 'warning' })
        .then(async () => {
          await deleteUser(row.id)
          ElMessage.success('删除成功')
          this.loadUsers()
        }).catch(() => {})
    }
  }
}
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
}

.search-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 260px;
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

.user-id { font-size: 12px; color: #94a3b8; font-weight: 600; }

.user-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar-lg {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  color: #fff;
  font-size: 15px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.user-detail {
  .username { font-size: 14px; font-weight: 600; color: #0f172a; }
  .user-sub { font-size: 12px; color: #94a3b8; margin-top: 2px; }
}

.phone-text, .email-text { font-size: 13px; color: #334155; }
.badge {
  font-size: 12px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 20px;
  display: inline-block;
  &.active   { background: #d1fae5; color: #059669; }
  &.banned   { background: #fee2e2; color: #dc2626; }
  &.rider    { background: #ede9fe; color: #7c3aed; }
  &.normal   { background: #f1f5f9; color: #64748b; }
}
.balance { font-size: 14px; font-weight: 700; color: #0f172a; }
.date-text { font-size: 13px; color: #64748b; }

.action-row {
  display: flex;
  gap: 4px;
  align-items: center;
}

.action-btn { font-size: 13px; font-weight: 600; padding: 4px 8px; border-radius: 8px; }
.danger-text { color: #ef4444 !important; font-size: 13px; font-weight: 600; }
.success-text { color: #10b981 !important; font-size: 13px; font-weight: 600; }

.pagination-wrap {
  padding: 16px 20px;
  border-top: 1px solid #f1f5f9;
  display: flex;
  justify-content: flex-end;
}

.dialog-form {
  :deep(.el-form-item__label) { font-weight: 600; color: #334155; }
}
</style>
