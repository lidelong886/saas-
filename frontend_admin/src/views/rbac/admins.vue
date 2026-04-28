<template>
  <div class="admins-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>管理员管理</span>
          <el-button type="primary" @click="handleAdd">新增管理员</el-button>
        </div>
      </template>

      <el-table :data="admins" v-loading="loading">
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="nickname" label="昵称" width="150" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="email" label="邮箱" width="200" />
        <el-table-column label="超级管理员" width="120">
          <template #default="{ row }">
            <el-tag :type="row.is_super_admin ? 'danger' : 'info'">
              {{ row.is_super_admin ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="角色" width="200">
          <template #default="{ row }">
            <el-tag v-for="role in row.roles" :key="role.id" size="small" style="margin-right: 5px">
              {{ role.name }}
            </el-tag>
          </template>
        </el-table-column>
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
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="form.nickname" placeholder="请输入昵称" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" />
          <span style="color: #999; font-size: 12px">编辑时留空表示不修改密码</span>
        </el-form-item>
        <el-form-item label="超级管理员">
          <el-switch v-model="form.is_super_admin" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.is_active" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.roles" multiple placeholder="请选择角色">
            <el-option
              v-for="role in allRoles"
              :key="role.code"
              :label="role.name"
              :value="role.code"
            />
          </el-select>
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
const admins = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('')
const submitting = ref(false)
const formRef = ref(null)
const allRoles = ref([])
const form = ref({
  username: '',
  nickname: '',
  phone: '',
  email: '',
  password: '',
  is_super_admin: false,
  is_active: true,
  roles: []
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入手机号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const loadAdmins = async () => {
  loading.value = true
  try {
    const res = await request.get('/admin/rbac/admins')
    admins.value = res.data
  } catch (error) {
    ElMessage.error('加载管理员列表失败')
  } finally {
    loading.value = false
  }
}

const loadRoles = async () => {
  try {
    const res = await request.get('/admin/rbac/roles')
    allRoles.value = res.data
  } catch (error) {
    ElMessage.error('加载角色列表失败')
  }
}

const handleAdd = async () => {
  await loadRoles()
  dialogTitle.value = '新增管理员'
  form.value = {
    username: '',
    nickname: '',
    phone: '',
    email: '',
    password: '',
    is_super_admin: false,
    is_active: true,
    roles: []
  }
  dialogVisible.value = true
}

const handleEdit = async (row) => {
  await loadRoles()
  dialogTitle.value = '编辑管理员'
  form.value = {
    ...row,
    password: '',
    roles: row.roles?.map(r => r.code) || []
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  await formRef.value.validate()
  submitting.value = true
  try {
    const data = { ...form.value }
    if (form.value.id && !data.password) {
      delete data.password
    }

    if (form.value.id) {
      await request.put(`/admin/rbac/admins/${form.value.id}`, data)
      ElMessage.success('更新成功')
    } else {
      await request.post('/admin/rbac/admins', data)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadAdmins()
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确定要删除该管理员吗？', '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await request.delete(`/admin/rbac/admins/${row.id}`)
      ElMessage.success('删除成功')
      loadAdmins()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

onMounted(() => {
  loadAdmins()
})
</script>

<style scoped>
.admins-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
