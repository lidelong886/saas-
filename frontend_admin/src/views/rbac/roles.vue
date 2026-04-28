<template>
  <div class="roles-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>角色管理</span>
          <el-button type="primary" @click="handleAdd">新增角色</el-button>
        </div>
      </template>

      <el-table :data="roles" v-loading="loading">
        <el-table-column prop="code" label="角色编码" width="150" />
        <el-table-column prop="name" label="角色名称" width="150" />
        <el-table-column prop="scope" label="作用域" width="100">
          <template #default="{ row }">
            <el-tag :type="row.scope === 'system' ? 'danger' : 'primary'">
              {{ row.scope === 'system' ? '系统' : '租户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" />
        <el-table-column label="权限数量" width="100">
          <template #default="{ row }">
            {{ row.permissions?.length || 0 }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="primary" @click="handlePermissions(row)">配置权限</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="角色编码" prop="code">
          <el-input v-model="form.code" placeholder="请输入角色编码" />
        </el-form-item>
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="作用域" prop="scope">
          <el-select v-model="form.scope" placeholder="请选择作用域">
            <el-option label="租户" value="tenant" />
            <el-option label="系统" value="system" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="permissionDialogVisible" title="配置权限" width="700px">
      <el-transfer
        v-model="selectedPermissions"
        :data="allPermissions"
        :titles="['可选权限', '已选权限']"
        :props="{ key: 'code', label: 'name' }"
        filterable
      />
      <template #footer>
        <el-button @click="permissionDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSavePermissions" :loading="submitting">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

const loading = ref(false)
const roles = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('')
const submitting = ref(false)
const formRef = ref(null)
const form = ref({
  code: '',
  name: '',
  scope: 'tenant',
  description: ''
})

const rules = {
  code: [{ required: true, message: '请输入角色编码', trigger: 'blur' }],
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }]
}

const permissionDialogVisible = ref(false)
const allPermissions = ref([])
const selectedPermissions = ref([])
const currentRole = ref(null)

const loadRoles = async () => {
  loading.value = true
  try {
    const res = await request.get('/admin/rbac/roles')
    roles.value = res.data
  } catch (error) {
    ElMessage.error('加载角色列表失败')
  } finally {
    loading.value = false
  }
}

const loadPermissions = async () => {
  try {
    const res = await request.get('/admin/rbac/permissions')
    allPermissions.value = res.data
  } catch (error) {
    ElMessage.error('加载权限列表失败')
  }
}

const handleAdd = () => {
  dialogTitle.value = '新增角色'
  form.value = { code: '', name: '', scope: 'tenant', description: '' }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑角色'
  form.value = { ...row }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  await formRef.value.validate()
  submitting.value = true
  try {
    if (form.value.id) {
      await request.put(`/admin/rbac/roles/${form.value.id}`, form.value)
      ElMessage.success('更新成功')
    } else {
      await request.post('/admin/rbac/roles', form.value)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadRoles()
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确定要删除该角色吗？', '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await request.delete(`/admin/rbac/roles/${row.id}`)
      ElMessage.success('删除成功')
      loadRoles()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

const handlePermissions = async (row) => {
  currentRole.value = row
  await loadPermissions()
  selectedPermissions.value = row.permissions?.map(p => p.code) || []
  permissionDialogVisible.value = true
}

const handleSavePermissions = async () => {
  submitting.value = true
  try {
    await request.put(`/admin/rbac/roles/${currentRole.value.id}`, {
      permissions: selectedPermissions.value
    })
    ElMessage.success('权限配置成功')
    permissionDialogVisible.value = false
    loadRoles()
  } catch (error) {
    ElMessage.error('权限配置失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadRoles()
})
</script>

<style scoped>
.roles-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
