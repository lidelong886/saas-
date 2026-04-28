<template>
  <div class="battery-create">
    <div class="page-header">
      <el-button @click="$router.back()">返回</el-button>
      <h2>新增电池</h2>
    </div>
    <el-card>
      <el-form :model="formData" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="电池型号" prop="model">
          <el-input v-model="formData.model" />
        </el-form-item>
        <el-form-item label="容量(mAh)" prop="capacity">
          <el-input-number v-model="formData.capacity" :min="1000" :max="50000" style="width: 100%" />
        </el-form-item>
        <el-form-item label="电池类型">
          <el-select v-model="formData.battery_type" style="width: 100%">
            <el-option label="锂离子电池" value="lithium_ion" />
            <el-option label="锂聚合物电池" value="lithium_polymer" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="tenantList.length" label="所属运营商">
          <el-select v-model="formData.tenant_id" placeholder="请选择运营商" style="width: 100%" filterable @change="handleTenantChange">
            <el-option
              v-for="tenant in tenantList"
              :key="tenant.id"
              :label="tenant.name"
              :value="tenant.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="所属站点" prop="current_station_id">
          <el-select v-model="formData.current_station_id" placeholder="请选择站点" style="width: 100%" filterable>
            <el-option
              v-for="station in stationList"
              :key="station.id"
              :label="station.name"
              :value="station.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="租用单价">
          <el-input-number v-model="formData.rental_price_per_hour" :precision="2" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="押金金额">
          <el-input-number v-model="formData.deposit_amount" :precision="2" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitForm" :loading="loading">创建</el-button>
          <el-button @click="$router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { createBattery } from '@/api/battery'
import { getStationList } from '@/api/station'
import { getTenantList } from '@/api/system'
import { ElMessage } from 'element-plus'
export default {
  name: 'BatteryCreate',
  data() {
    return {
      loading: false,
      tenantList: [],
      stationList: [],
      formData: {
        tenant_id: 1,
        model: '',
        capacity: 10000,
        battery_type: 'lithium_ion',
        current_station_id: null,
        rental_price_per_hour: 0.5,
        deposit_amount: 50
      },
      rules: {
        model: [{ required: true, message: '请输入电池型号', trigger: 'blur' }],
        capacity: [{ required: true, message: '请输入容量', trigger: 'blur' }]
      }
    }
  },
  methods: {
    async loadTenants() {
      try {
        const res = await getTenantList()
        this.tenantList = res.data || []
        if (this.tenantList.length) {
          this.formData.tenant_id = this.tenantList[0].id
        }
      } catch (e) {
        this.tenantList = []
      }
    },
    async loadStations() {
      try {
        const params = { per_page: 999 }
        if (this.formData.tenant_id) params.tenant_id = this.formData.tenant_id
        const res = await getStationList(params)
        this.stationList = res.data?.list || []
      } catch (e) {
        // ignore
      }
    },
    handleTenantChange() {
      this.formData.current_station_id = null
      this.loadStations()
    },
    async submitForm() {
      try {
        await this.$refs.formRef.validate()
        this.loading = true
        // 只传递有值的字段，避免传 null 给后端
        const data = { ...this.formData }
        if (!data.current_station_id) delete data.current_station_id
        await createBattery(data)
        ElMessage.success('创建成功')
        this.$router.push('/batteries')
      } catch (e) {
        if (e !== false) ElMessage.error('创建失败')
      } finally {
        this.loading = false
      }
    }
  },
  async mounted() {
    await this.loadTenants()
    this.loadStations()
  }
}
</script>

<style scoped>
.battery-create { padding: 20px; }
.page-header { display: flex; align-items: center; gap: 20px; margin-bottom: 20px; }
.page-header h2 { margin: 0; }
</style>
