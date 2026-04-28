<template>
  <div class="page-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div>
        <h1 class="page-title">电池管理</h1>
        <p class="page-subtitle">统一查看电池状态、健康度与设备分布</p>
      </div>
      <el-button type="primary" class="btn-primary" @click="handleCreate">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        添加电池
      </el-button>
    </div>

    <!-- 统计卡片 Bento 网格 -->
    <div class="bento-grid">
      <div class="bento-card bento-total">
        <div class="bento-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="1" y="6" width="18" height="12" rx="2"/><line x1="23" y1="10" x2="23" y2="14"/></svg>
        </div>
        <div class="bento-value">{{ pagination.total }}</div>
        <div class="bento-label">电池总数</div>
      </div>
      <div class="bento-card bento-available">
        <div class="bento-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
        </div>
        <div class="bento-value">{{ statusSummary.available }}</div>
        <div class="bento-label">可用电池</div>
      </div>
      <div class="bento-card bento-rented">
        <div class="bento-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        </div>
        <div class="bento-value">{{ statusSummary.rented }}</div>
        <div class="bento-label">租用中</div>
      </div>
      <div class="bento-card bento-maintenance">
        <div class="bento-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
        </div>
        <div class="bento-value">{{ statusSummary.maintenance + statusSummary.scrapped }}</div>
        <div class="bento-label">维护 / 异常</div>
      </div>
    </div>

    <!-- 搜索卡片 -->
    <div class="search-card">
      <div class="search-row">
        <div class="search-field">
          <label class="field-label">电池编码</label>
          <el-input
            v-model="searchForm.battery_code"
            placeholder="输入编码搜索"
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
          <label class="field-label">状态</label>
          <el-select v-model="searchForm.status" placeholder="选择状态" clearable class="modern-select">
            <el-option label="可用" value="available" />
            <el-option label="租用中" value="rented" />
            <el-option label="维护中" value="maintenance" />
            <el-option label="报废" value="scrapped" />
          </el-select>
        </div>
        <div class="search-field">
          <label class="field-label">站点</label>
          <el-select v-model="searchForm.station_id" placeholder="选择站点" clearable filterable class="modern-select">
            <el-option
              v-for="station in stationList"
              :key="station.id"
              :label="station.name"
              :value="station.id"
            />
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

    <!-- 数据表格 -->
    <div class="data-card">
      <el-table :data="tableData" v-loading="loading" class="modern-table">
        <el-table-column prop="id" label="ID" width="80">
          <template #default="{ row }">
            <span class="row-id">#{{ row.id }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="battery_code" label="电池编码" min-width="160">
          <template #default="{ row }">
            <span class="battery-code">{{ row.battery_code }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="model" label="型号" min-width="140" />
        <el-table-column label="所属运营商" min-width="130">
          <template #default="{ row }">
            <el-tag type="success" effect="plain">{{ row.tenant_name || '默认运营商' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="power_level" label="电量" width="140">
          <template #default="{ row }">
            <div class="power-wrap">
              <el-progress
                :percentage="Number(row.power_level) || 0"
                :status="getPowerStatus(row.power_level)"
                :stroke-width="8"
              />
              <span class="power-text">{{ Number(row.power_level) || 0 }}%</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="110">
          <template #default="{ row }">
            <span class="badge" :class="row.status">{{ getStatusLabel(row.status) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="voltage" label="电压" width="90">
          <template #default="{ row }">
            <span class="meta-text">{{ row.voltage != null ? row.voltage + 'V' : '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="temperature" label="温度" width="90">
          <template #default="{ row }">
            <span class="meta-text" :class="Number(row.temperature) >= 45 ? 'temp-warn' : ''">
              {{ row.temperature != null ? row.temperature + '°C' : '-' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="所属站点" min-width="150">
          <template #default="{ row }">
            <span class="meta-text">{{ row.current_station_name || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="售价" width="100">
          <template #default="{ row }">
            <span class="price-text">{{ row.selling_price ? '¥' + parseFloat(row.selling_price).toFixed(2) : '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="健康" min-width="130">
          <template #default="{ row }">
            <span class="health-badge" :class="getHealthClass(row)">
              {{ getHealthText(row) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <div class="action-row">
              <el-button size="small" text type="primary" class="action-btn" @click="handleEdit(row)">编辑</el-button>
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
          @change="loadBatteries"
        />
      </div>
    </div>

    <!-- 新增 / 编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="520px" class="modern-dialog">
      <el-form :model="formData" :rules="rules" ref="formRef" label-width="90px" class="dialog-form">
        <el-form-item label="电池编码" prop="battery_code">
          <el-input v-model="formData.battery_code" placeholder="请输入电池编码" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="型号" prop="model">
          <el-input v-model="formData.model" placeholder="请输入电池型号" />
        </el-form-item>
        <el-form-item label="容量(mAh)" prop="capacity">
          <el-input-number v-model="formData.capacity" :min="1000" :max="50000" style="width:100%" />
        </el-form-item>
        <el-form-item label="电量(%)" prop="power_level">
          <el-input-number v-model="formData.power_level" :min="0" :max="100" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="formData.status" placeholder="请选择状态" style="width:100%">
            <el-option label="可用" value="available" />
            <el-option label="租用中" value="rented" />
            <el-option label="维护中" value="maintenance" />
            <el-option label="报废" value="scrapped" />
          </el-select>
        </el-form-item>
        <el-form-item label="电压(V)" prop="voltage">
          <el-input-number v-model="formData.voltage" :step="0.1" style="width:100%" />
        </el-form-item>
        <el-form-item label="温度(°C)" prop="temperature">
          <el-input-number v-model="formData.temperature" :step="0.1" style="width:100%" />
        </el-form-item>
        <el-form-item v-if="tenantList.length" label="所属运营商">
          <el-select v-model="formData.tenant_id" placeholder="请选择运营商" style="width:100%" filterable @change="handleTenantChange">
            <el-option
              v-for="tenant in tenantList"
              :key="tenant.id"
              :label="tenant.name"
              :value="tenant.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="租用单价(时)" prop="rental_price_per_hour">
          <el-input-number v-model="formData.rental_price_per_hour" :min="0" :precision="2" :step="0.1" style="width:100%">
            <template #prefix>¥</template>
          </el-input-number>
        </el-form-item>
        <el-form-item label="电池押金" prop="deposit_amount">
          <el-input-number v-model="formData.deposit_amount" :min="0" :precision="2" :step="10" style="width:100%">
            <template #prefix>¥</template>
          </el-input-number>
        </el-form-item>
        <el-form-item label="售卖价格" prop="selling_price">
          <el-input-number v-model="formData.selling_price" :min="0" :precision="2" :step="100" style="width:100%" placeholder="留空则使用押金作为售价">
            <template #prefix>¥</template>
          </el-input-number>
        </el-form-item>
        <el-form-item label="所属站点" prop="current_station_id">
          <el-select v-model="formData.current_station_id" placeholder="请选择站点" style="width:100%" filterable>
            <el-option
              v-for="station in stationList"
              :key="station.id"
              :label="station.name"
              :value="station.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button class="btn-ghost" @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" class="btn-primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ElMessage, ElMessageBox } from 'element-plus'
import { getBatteryList, createBattery, updateBattery, deleteBattery } from '@/api/battery'
import { getStationList } from '@/api/station'
import { getTenantList } from '@/api/system'

export default {
  name: 'BatteryIndex',
  data() {
    return {
      tableData: [],
      loading: false,
      submitting: false,
      dialogVisible: false,
      isEdit: false,
      tenantList: [],
      stationList: [],
      searchForm: {
        battery_code: '',
        status: '',
        station_id: ''
      },
      formData: {
        tenant_id: 1,
        battery_code: '',
        model: '',
        capacity: 10000,
        power_level: 100,
        status: 'available',
        voltage: 0,
        temperature: 0,
        current_station_id: null,
        rental_price_per_hour: 0.5,
        deposit_amount: 50,
        selling_price: null
      },
      rules: {
        battery_code: [{ required: true, message: '电池编码不能为空', trigger: 'blur' }],
        model: [{ required: true, message: '型号不能为空', trigger: 'blur' }],
        capacity: [{ required: true, message: '容量不能为空', trigger: 'blur' }],
        power_level: [{ required: true, message: '电量不能为空', trigger: 'blur' }],
        status: [{ required: true, message: '状态不能为空', trigger: 'change' }]
      },
      pagination: {
        page: 1,
        per_page: 20,
        total: 0
      },
      statusSummary: {
        available: 0,
        rented: 0,
        maintenance: 0,
        scrapped: 0
      }
    }
  },
  computed: {
    dialogTitle() {
      return this.isEdit ? '编辑电池' : '添加电池'
    }
  },
  async mounted() { await this.loadTenants(); this.loadBatteries(); this.loadStations() },
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
        if (this.formData.tenant_id) params.tenant_id = this.formData.tenant_id
        const res = await getStationList(params)
        this.stationList = res.data?.list || []
      } catch (e) { /* ignore */ }
    },
    handleTenantChange() {
      this.formData.current_station_id = null
      this.loadStations()
    },
    async loadBatteries() {
      this.loading = true
      try {
        const params = {
          page: this.pagination.page,
          per_page: this.pagination.per_page
        }
        if (this.searchForm.battery_code) params.keyword = this.searchForm.battery_code
        if (this.searchForm.status) params.status = this.searchForm.status
        if (this.searchForm.station_id) params.station_id = this.searchForm.station_id

        const response = await getBatteryList(params)
        if (response.code === 0 || response.code === 200) {
          this.tableData = response.data.list || []
          this.pagination.total = response.data.pagination?.total || 0
          this.statusSummary = this.tableData.reduce((acc, item) => {
            const key = item.status || 'unknown'
            if (acc[key] !== undefined) acc[key] += 1
            return acc
          }, { available: 0, rented: 0, maintenance: 0, scrapped: 0 })
        }
      } catch (error) {
        ElMessage.error('加载电池列表失败')
      } finally {
        this.loading = false
      }
    },
    handleSearch() { this.pagination.page = 1; this.loadBatteries() },
    handleReset() {
      this.searchForm = { battery_code: '', status: '', station_id: '' }
      this.pagination.page = 1
      this.loadBatteries()
    },
    handleCreate() {
      this.isEdit = false
      this.formData = {
        tenant_id: this.tenantList[0]?.id || 1,
        battery_code: '', model: '', capacity: 10000, power_level: 100,
        status: 'available', voltage: 0, temperature: 0,
        rental_price_per_hour: 0.50, deposit_amount: 50.00, selling_price: null,
        current_station_id: null
      }
      this.loadStations()
      this.dialogVisible = true
    },
    handleEdit(row) {
      this.isEdit = true
      this.formData = { ...row }
      this.loadStations()
      // 设置默认回显值，并转换数字类型
      if (this.formData.rental_price_per_hour === undefined || this.formData.rental_price_per_hour === null) {
        this.formData.rental_price_per_hour = 0.50
      } else {
        this.formData.rental_price_per_hour = parseFloat(this.formData.rental_price_per_hour)
      }
      if (this.formData.deposit_amount === undefined || this.formData.deposit_amount === null) {
        this.formData.deposit_amount = 50.00
      } else {
        this.formData.deposit_amount = parseFloat(this.formData.deposit_amount)
      }
      if (this.formData.selling_price === undefined || this.formData.selling_price === null) {
        this.formData.selling_price = null
      } else {
        this.formData.selling_price = parseFloat(this.formData.selling_price)
      }
      this.dialogVisible = true
    },
    async handleSubmit() {
      try {
        await this.$refs.formRef.validate()
        this.submitting = true
        if (this.isEdit) {
          await updateBattery(this.formData.id, this.formData)
          ElMessage.success('编辑成功')
        } else {
          await createBattery(this.formData)
          ElMessage.success('创建成功')
        }
        this.dialogVisible = false
        this.loadBatteries()
      } catch {} finally { this.submitting = false }
    },
    handleDelete(row) {
      ElMessageBox.confirm(`确定删除电池"${row.battery_code}"吗？`, '提示', { type: 'warning' })
        .then(async () => {
          await deleteBattery(row.id)
          ElMessage.success('删除成功')
          this.loadBatteries()
        }).catch(() => {})
    },
    getStatusLabel(status) {
      return { available: '可用', rented: '租用中', maintenance: '维护中', scrapped: '报废' }[status] || status
    },
    getPowerStatus(powerLevel) {
      const v = Number(powerLevel) || 0
      if (v < 20) return 'exception'
      if (v < 50) return 'warning'
      return 'success'
    },
    getHealthText(row) {
      const power = Number(row.power_level) || 0
      const temp = Number(row.temperature) || 0
      if (row.status === 'scrapped') return '建议更换'
      if (row.status === 'maintenance') return '待检修'
      if (temp >= 45) return '温度偏高'
      if (power < 20) return '电量过低'
      return '运行正常'
    },
    getHealthClass(row) {
      const t = this.getHealthText(row)
      if (t === '运行正常') return 'health-ok'
      if (t === '电量过低' || t === '温度偏高') return 'health-warn'
      return 'health-bad'
    }
  }
}
</script>

<style lang="scss" scoped>
.page-container { padding: 28px 32px; }

/* ── 头部 ──────────────────────────────────────── */
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

/* ── 按钮 ──────────────────────────────────────── */
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
  cursor: pointer;
  transition: all 0.2s;
  &:hover { background: #f8fafc; color: #334155; }
}

/* ── Bento 统计 ─────────────────────────────────── */
.bento-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.bento-card {
  background: #fff;
  border-radius: 20px;
  padding: 24px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 20rpx rgba(0,0,0,0.06);
  transition: all 0.2s;
  cursor: default;

  &:hover { transform: translateY(-2px); box-shadow: 0 8px 30rpx rgba(0,0,0,0.1); }
}

.bento-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 14px;
}

.bento-total .bento-icon { background: #f1f5f9; color: #64748B; }
.bento-available .bento-icon { background: #d1fae5; color: #10b981; }
.bento-rented .bento-icon { background: #fed7aa; color: #F97316; }
.bento-maintenance .bento-icon { background: #fee2e2; color: #ef4444; }

.bento-value {
  font-size: 30px;
  font-weight: 800;
  color: #0f172a;
  line-height: 1;
  margin-bottom: 6px;
}

.bento-label {
  font-size: 12px;
  color: #94a3b8;
  font-weight: 500;
}

/* ── 搜索卡片 ─────────────────────────────────── */
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
    transition: all 0.2s;
    &:hover { box-shadow: 0 0 0 1px #cbd5e1; }
    &.is-focus { box-shadow: 0 0 0 2px rgba(249,115,22,0.2) !important; }
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

.search-actions {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-shrink: 0;
}

/* ── 数据卡片 ─────────────────────────────────── */
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

.row-id { font-size: 12px; color: #94a3b8; font-weight: 600; }

.battery-code {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 12px;
  background: #f1f5f9;
  color: #334155;
  padding: 3px 8px;
  border-radius: 6px;
}

.power-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
  :deep(.el-progress) { flex: 1; }
  :deep(.el-progress-bar__outer) { border-radius: 4px; }
}

.power-text {
  font-size: 12px;
  font-weight: 700;
  color: #0f172a;
  min-width: 34px;
  text-align: right;
}

.badge {
  font-size: 12px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 20px;
  display: inline-block;
  &.available { background: #d1fae5; color: #059669; }
  &.rented    { background: #fed7aa; color: #F97316; }
  &.maintenance { background: #fee2e2; color: #dc2626; }
  &.scrapped  { background: #f1f5f9; color: #64748b; }
}

.meta-text { font-size: 13px; color: #64748b; }
.temp-warn { color: #ef4444 !important; font-weight: 600; }

.price-text {
  font-size: 13px;
  font-weight: 600;
  color: #0f172a;
}

.health-badge {
  font-size: 12px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 20px;
  display: inline-block;
  &.health-ok  { background: #d1fae5; color: #059669; }
  &.health-warn { background: #fef3c7; color: #d97706; }
  &.health-bad { background: #fee2e2; color: #dc2626; }
}

.action-row { display: flex; gap: 4px; align-items: center; }
.action-btn { font-size: 13px; font-weight: 600; padding: 4px 8px; border-radius: 8px; cursor: pointer; transition: all 0.2s; }

.pagination-wrap {
  padding: 16px 20px;
  border-top: 1px solid #f1f5f9;
  display: flex;
  justify-content: flex-end;
}

/* ── 对话框 ─────────────────────────────────── */
.dialog-form {
  :deep(.el-form-item__label) { font-weight: 600; color: #334155; }
}

@media (max-width: 1100px) {
  .bento-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 768px) {
  .bento-grid { grid-template-columns: repeat(2, 1fr); }
  .page-container { padding: 20px 16px; }
}
</style>
