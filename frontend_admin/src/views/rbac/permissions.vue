<template>
  <div class="permissions-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>权限管理</span>
          <el-button type="primary" @click="handleAdd">新增权限</el-button>
        </div>
      </template>

      <el-table :data="permissions" v-loading="loading">
        <el-table-column prop="code" label="权限编码" width="200" />
        <el-table-column prop="name" label="权限名称" width="150" />
        <el-table-column prop="module" label="模块" width="120" />
        <el-table-column prop="action" label="操作" width="120" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="权限编码" prop="code">
          <el-input v-model="form.code" placeholder="如: user:create" />
        </el-form-item>
        <el-form-item label="权限名称" prop="name">
          <el-input v-model="form.name" placeholder="如: 创建用户" />
        </el-form-item>
        <el-form-item label="模块" prop="module">
          <el-input v-model="form.module" placeholder="如: user" />
        </el-form-item>
        <el-form-item label="操作" prop="action">
          <el-select v-model="form.action" placeholder="请选择操作">
            <el-option label="查看" value="view" />
            <el-option label="创建" value="create" />
            <el-option label="编辑" value="edit" />
            <el-option label="删除" value="delete" />
            <el-option label="导出" value="export" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

const loading = ref(false)
const permissions = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('')
const submitting = ref(false)
const formRef = ref(null)
const form = ref({
  code: '',
  name: '',
  module: '',
  action: '',
  description: ''
})

const rules = {
  code: [{ required: true, message: '请输入权限编码', trigger: 'blur' }],
  name: [{ required: true, message: '请输入权限名称', trigger: 'blur' }],
  module: [{ required: true, message: '请输入模块', trigger: 'blur' }],
  action: [{ required: true, message: '请选择操作', trigger: 'change' }]
}

const loadPermissions = async () => {
  loading.value = true
  try {
    const res = await request.get('/admin/rbac/permissions')
    permissions.value = res.data
  } catch (error) {
    ElMessage.error('加载权限列表失败')
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  dialogTitle.value = '新增权限'
  form.value = { code: '', name: '', module: '', action: '', description: '' }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑权限'
  form.value = { ...row }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  await formRef.value.validate()
  submitting.value = true
  try {
    if (form.value.id) {
      await request.put(`/admin/rbac/permissions/${form.value.id}`, form.value)
      ElMessage.success('更新成功')
    } else {
      await request.post('/admin/rbac/permissions', form.value)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadPermissions()
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确定要删除该权限吗？', '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await request.delete(`/admin/rbac/permissions/${row.id}`)
      ElMessage.success('删除成功')
      loadPermissions()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

onMounted(() => {
  loadPermissions()
})
</script>

<style scoped>
.permissions-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
