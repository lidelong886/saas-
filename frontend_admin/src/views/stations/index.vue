<template>
  <div class="station-container">
    <!-- 搜索和操作栏 -->
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>站点管理</span>
          <el-button type="primary" @click="handleCreate">新增站点</el-button>
        </div>
      </template>

      <!-- 搜索表单 -->
      <el-form :model="searchForm" label-width="100px" class="search-form">
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :md="6">
            <el-form-item label="站点名称">
              <el-input v-model="searchForm.name" placeholder="请输入站点名称" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-col>
        </el-row>
      </el-form>

      <!-- 站点列表 -->
      <el-table :data="tableData" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="站点名称" />
        <el-table-column label="所属运营商" min-width="130">
          <template #default="{ row }">
            <el-tag type="success" effect="plain">{{ row.tenant_name || '默认运营商' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="address" label="地址" min-width="200" />
        <el-table-column label="联系电话" width="140">
          <template #default="{ row }">
            <span>{{ row.phone || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="坐标" width="150">
          <template #default="{ row }">
            <span>{{ row.latitude }}, {{ row.longitude }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <div class="table-actions">
              <el-button size="small" type="primary" plain @click="handleEdit(row)">编辑</el-button>
              <el-button size="small" type="danger" plain @click="handleDelete(row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.per_page"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 20px; text-align: right"
        @change="loadStations"
      />
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form :model="formData" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item v-if="tenantList.length" label="所属运营商">
          <el-select v-model="formData.tenant_id" placeholder="请选择运营商" style="width:100%" filterable>
            <el-option
              v-for="tenant in tenantList"
              :key="tenant.id"
              :label="tenant.name"
              :value="tenant.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="站点名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入站点名称" />
        </el-form-item>
        <el-form-item label="地址" prop="address">
          <el-input v-model="formData.address" placeholder="请输入站点地址" />
          <div class="geo-actions">
            <el-button type="primary" plain size="small" :loading="locating" @click="handleLocateByAddress(formData.address)">按地址自动定位</el-button>
            <span class="geo-tip">输入地址后自动获取经纬度，也可手动修改</span>
          </div>
        </el-form-item>
        <el-form-item label="纬度" prop="latitude">
          <el-input-number v-model="formData.latitude" :min="-90" :max="90" :step="0.0001" />
        </el-form-item>
        <el-form-item label="经度" prop="longitude">
          <el-input-number v-model="formData.longitude" :min="-180" :max="180" :step="0.0001" />
        </el-form-item>
        <el-form-item label="联系电话" prop="phone">
          <el-input v-model="formData.phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="营业时间" prop="business_hours">
          <el-input v-model="formData.business_hours" placeholder="例如: 08:00-22:00" />
        </el-form-item>
        <el-form-item label="容量" prop="capacity">
          <el-input-number v-model="formData.capacity" :min="1" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ElMessage, ElMessageBox } from 'element-plus'
import { getStationList, createStation, updateStation, deleteStation } from '@/api/station'
import { getTenantList } from '@/api/system'
import stationLocateMixin from './station-locate-mixin.js'

export default {
  name: 'StationIndex',
  mixins: [stationLocateMixin],
  data() {
    return {
      tableData: [],
      tenantList: [],
      loading: false,
      dialogVisible: false,
      isEdit: false,
      searchForm: {
        name: ''
      },
      formData: {
        tenant_id: 1,
        name: '',
        address: '',
        latitude: 0,
        longitude: 0,
        phone: '',
        business_hours: '',
        capacity: 0
      },
      rules: {
        name: [{ required: true, message: '站点名称不能为空', trigger: 'blur' }],
        address: [{ required: true, message: '地址不能为空', trigger: 'blur' }],
        latitude: [{ required: true, message: '纬度不能为空', trigger: 'blur' }],
        longitude: [{ required: true, message: '经度不能为空', trigger: 'blur' }]
      },
      pagination: {
        page: 1,
        per_page: 20,
        total: 0
      }
    }
  },
  computed: {
    dialogTitle() {
      return this.isEdit ? '编辑站点' : '新增站点'
    }
  },
  methods: {
    async loadTenants() {
      try {
        const response = await getTenantList()
        this.tenantList = response.data || []
      } catch (error) {
        this.tenantList = []
      }
    },
    async loadStations() {
      this.loading = true
      try {
        const params = {
          page: this.pagination.page,
          per_page: this.pagination.per_page
        }
        if (this.searchForm.name) {
          params.keyword = this.searchForm.name
        }

        const response = await getStationList(params)
        if (response.code === 0 || response.code === 200) {
          this.tableData = response.data.list || []
          this.pagination.total = response.data.pagination?.total || 0
        }
      } catch (error) {
        ElMessage.error('加载站点列表失败')
      } finally {
        this.loading = false
      }
    },
    handleSearch() {
      this.pagination.page = 1
      this.loadStations()
    },
    handleReset() {
      this.searchForm.name = ''
      this.pagination.page = 1
      this.loadStations()
    },
    handleCreate() {
      this.isEdit = false
      this.formData = {
        tenant_id: this.tenantList[0]?.id || 1,
        name: '',
        address: '',
        latitude: 0,
        longitude: 0,
        phone: '',
        business_hours: '',
        capacity: 0
      }
      this.dialogVisible = true
    },
    handleEdit(row) {
      this.isEdit = true
      this.formData = { ...row }
      this.dialogVisible = true
    },
    async handleDelete(row) {
      try {
        await ElMessageBox.confirm('确定删除该站点吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })

        await deleteStation(row.id)
        ElMessage.success('删除成功')
        this.loadStations()
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('删除失败')
        }
      }
    },
    async handleSubmit() {
      let valid = false
      try {
        valid = await this.$refs.formRef.validate()
      } catch (_) {
        return
      }
      if (!valid) return
      try {
        if (this.isEdit) {
          await updateStation(this.formData.id, this.formData)
          ElMessage.success('编辑成功')
        } else {
          await createStation(this.formData)
          ElMessage.success('创建成功')
        }

        this.dialogVisible = false
        this.loadStations()
      } catch (error) {
        // errors already surfaced via API; cancel is no-op
      }
    }
  },
  mounted() {
    this.loadTenants()
    this.loadStations()
  }
}
</script>

<style lang="scss" scoped>
.station-container {
  padding: 20px;

  .box-card {
    margin-bottom: 20px;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .search-form {
    margin-bottom: 20px;
  }

  .table-actions {
    display: flex;
    gap: 8px;
    align-items: center;
    flex-wrap: nowrap;
  }

  .geo-actions {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 10px;
    flex-wrap: wrap;
  }

  .geo-tip {
    color: #64748b;
    font-size: 12px;
  }
}
</style>
