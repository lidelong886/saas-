<template>
  <div class="battery-edit">
    <div class="page-header">
      <el-button @click="$router.back()">返回</el-button>
      <h2>编辑电池</h2>
    </div>
    <el-card v-loading="pageLoading">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="电池编码">
          <el-input v-model="form.battery_code" disabled />
        </el-form-item>
        <el-form-item label="电池型号" prop="model">
          <el-input v-model="form.model" />
        </el-form-item>
        <el-form-item label="容量(mAh)">
          <el-input-number v-model="form.capacity" :min="1000" style="width: 100%" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option label="可用" value="available" />
            <el-option label="租用中" value="rented" />
            <el-option label="充电中" value="charging" />
            <el-option label="维护中" value="maintenance" />
          </el-select>
        </el-form-item>
        <el-form-item label="电量(%)">
          <el-slider v-model="form.power_level" :min="0" :max="100" show-input />
        </el-form-item>
        <el-form-item v-if="tenantList.length" label="所属运营商">
          <el-select v-model="form.tenant_id" placeholder="请选择运营商" style="width: 100%" filterable @change="handleTenantChange">
            <el-option
              v-for="tenant in tenantList"
              :key="tenant.id"
              :label="tenant.name"
              :value="tenant.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="所属站点">
          <el-select v-model="form.current_station_id" placeholder="请选择站点" style="width: 100%" filterable>
            <el-option
              v-for="station in stationList"
              :key="station.id"
              :label="station.name"
              :value="station.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitForm" :loading="loading">保存</el-button>
          <el-button @click="$router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { getBatteryDetail, updateBattery } from '@/api/battery'
import { getStationList } from '@/api/station'
import { getTenantList } from '@/api/system'
import { ElMessage } from 'element-plus'
export default {
  name: 'BatteryEdit',
  data() {
    return {
      pageLoading: true, loading: false,
      tenantList: [],
      stationList: [],
      form: { battery_code: '', model: '', capacity: 10000, voltage_type: '60V', status: 'available', power_level: 100, tenant_id: 1, selling_price: null, current_station_id: null },
      rules: { model: [{ required: true, message: '请输入电池型号', trigger: 'blur' }] }
    }
  },
  methods: {
    async loadTenants() {
      try {
        const res = await getTenantList()
        this.tenantList = res.data || []
      } catch (e) { this.tenantList = [] }
    },
    async loadStations() {
      try {
        const params = { per_page: 999 }
        if (this.form.tenant_id) params.tenant_id = this.form.tenant_id
        const res = await getStationList(params)
        this.stationList = res.data?.list || []
      } catch (e) { /* ignore */ }
    },
    handleTenantChange() {
      this.form.current_station_id = null
      this.loadStations()
    },
    async loadBattery() {
      try {
        const res = await getBatteryDetail(this.$route.params.id)
        this.form = res.data
        if (!this.form.voltage_type) this.form.voltage_type = this.form.model && this.form.model.includes('72V') ? '72V' : '60V'
        if (this.form.selling_price != null) this.form.selling_price = Number(this.form.selling_price)
        if (this.form.current_station_id === undefined) this.form.current_station_id = null
        this.loadStations()
      } catch (e) { ElMessage.error('加载失败'); this.$router.back() } finally { this.pageLoading = false }
    },
    async submitForm() {
      try {
        await this.$refs.formRef.validate()
        this.loading = true
        const data = { ...this.form }
        if (!data.current_station_id) delete data.current_station_id
        await updateBattery(this.$route.params.id, data)
        ElMessage.success('保存成功')
        this.$router.push('/batteries')
      } catch (e) {
        if (e !== false) ElMessage.error('保存失败')
      } finally {
        this.loading = false
      }
    }
  },
  async mounted() { await this.loadTenants(); this.loadBattery() }
}
</script>

<style scoped>
.battery-edit { padding: 20px; }
.page-header { display: flex; align-items: center; gap: 20px; margin-bottom: 20px; }
.page-header h2 { margin: 0; }
</style>
