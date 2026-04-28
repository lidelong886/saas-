<template>
  <div class="station-create">
    <div class="page-header">
      <div>
        <div class="page-title">新增站点</div>
        <div class="page-subtitle">填写站点基础信息，支持根据地址自动定位经纬度</div>
      </div>
      <el-button @click="$router.back()" class="btn-back">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
        返回
      </el-button>
    </div>

    <div class="form-card">
      <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
        <div class="form-section">
          <div class="section-title">基础信息</div>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="站点名称" prop="name">
                <el-input v-model="form.name" placeholder="请输入站点名称" class="modern-input" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="站点类型">
                <el-select v-model="form.type" placeholder="选择站点类型" class="modern-input" style="width: 100%">
                  <el-option label="街头站点" value="street" />
                  <el-option label="商场站点" value="mall" />
                  <el-option label="办公楼站点" value="office" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item v-if="tenantList.length" label="所属运营商">
            <el-select v-model="form.tenant_id" placeholder="请选择运营商" class="modern-input" style="width: 100%" filterable>
              <el-option
                v-for="tenant in tenantList"
                :key="tenant.id"
                :label="tenant.name"
                :value="tenant.id"
              />
            </el-select>
          </el-form-item>
        </div>

        <div class="form-section">
          <div class="section-title">地址与定位</div>
          <el-form-item label="详细地址" prop="address">
            <el-input
              v-model="form.address"
              type="textarea"
              :rows="3"
              placeholder="请输入详细地址，例如：北京市海淀区中关村大街1号"
              class="modern-textarea"
            />
          </el-form-item>
          <div class="locate-action">
            <el-button
              type="primary"
              :loading="locating"
              @click="handleLocate"
              class="btn-locate"
            >
              <svg v-if="!locating" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="3"/></svg>
              {{ locating ? '定位中...' : '自动定位' }}
            </el-button>
            <span class="locate-tip">根据地址自动填充经纬度，定位结果可手动微调</span>
          </div>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="纬度" prop="latitude">
                <el-input-number
                  v-model="form.latitude"
                  :precision="6"
                  :step="0.000001"
                  controls-position="right"
                  class="modern-number"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="经度" prop="longitude">
                <el-input-number
                  v-model="form.longitude"
                  :precision="6"
                  :step="0.000001"
                  controls-position="right"
                  class="modern-number"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <div class="form-footer">
          <el-button type="primary" @click="submitForm" :loading="loading" class="btn-submit">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
            创建站点
          </el-button>
          <el-button @click="$router.back()" class="btn-cancel">取消</el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script>
import { ElMessage } from 'element-plus'
import { createStation } from '@/api/station'
import { getTenantList } from '@/api/system'
import stationLocateMixin from './station-locate-mixin.js'

export default {
  name: 'StationCreate',
  mixins: [stationLocateMixin],
  data() {
    return {
      loading: false,
      tenantList: [],
      form: {
        name: '',
        type: 'street',
        tenant_id: 1,
        address: '',
        latitude: 39.9042,
        longitude: 116.4074
      },
      rules: {
        name: [{ required: true, message: '请输入站点名称', trigger: 'blur' }],
        address: [{ required: true, message: '请输入详细地址', trigger: 'blur' }]
      }
    }
  },
  mounted() {
    this.loadTenants()
  },
  methods: {
    async loadTenants() {
      try {
        const res = await getTenantList()
        this.tenantList = res.data || []
        if (this.tenantList.length && !this.form.tenant_id) {
          this.form.tenant_id = this.tenantList[0].id
        }
      } catch (e) {
        this.tenantList = []
      }
    },
    handleLocate() {
      this.handleLocateByAddress(this.form.address)
    },
    async submitForm() {
      try {
        await this.$refs.formRef.validate()
      } catch {
        return
      }
      this.loading = true
      try {
        await createStation(this.form)
        ElMessage.success('站点创建成功')
        this.$router.push('/stations')
      } catch (e) {
        ElMessage.error('创建失败')
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.station-create {
  padding: 28px 32px;
  max-width: 1000px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding: 28px 32px;
  border-radius: 20px;
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  color: #fff;
}
.page-title {
  font-size: 26px;
  font-weight: 800;
  letter-spacing: -0.3px;
  margin-bottom: 6px;
}
.page-subtitle {
  font-size: 14px;
  opacity: 0.92;
}
.btn-back {
  background: rgba(255,255,255,0.15);
  border: 1px solid rgba(255,255,255,0.3);
  color: #fff;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  &:hover {
    background: rgba(255,255,255,0.25);
    border-color: rgba(255,255,255,0.4);
  }
}

.form-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  padding: 32px;
  box-shadow: 0 10px 24px rgba(15,23,42,0.06);
}

.form-section {
  margin-bottom: 32px;
  &:last-of-type {
    margin-bottom: 0;
  }
}
.section-title {
  font-size: 16px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 2px solid #f1f5f9;
}

:deep(.el-form-item__label) {
  font-size: 13px;
  font-weight: 600;
  color: #64748b;
  margin-bottom: 8px;
}

:deep(.el-input__wrapper),
:deep(.el-textarea__inner) {
  border-radius: 10px;
  box-shadow: 0 0 0 1px #e2e8f0 !important;
  background: #f8fafc;
  padding: 10px 14px;
  &:hover {
    box-shadow: 0 0 0 1px #cbd5e1 !important;
  }
}
:deep(.el-input__wrapper.is-focus),
:deep(.el-textarea__inner:focus) {
  box-shadow: 0 0 0 2px rgba(99,102,241,0.2) !important;
}

:deep(.el-input-number) {
  .el-input__wrapper {
    padding: 0 12px;
  }
}

.locate-action {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}
.btn-locate {
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  border: none;
  border-radius: 10px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  box-shadow: 0 2px 8px rgba(99,102,241,0.3);
  &:hover {
    box-shadow: 0 4px 12px rgba(99,102,241,0.4);
    transform: translateY(-1px);
  }
}
.locate-tip {
  font-size: 12px;
  color: #94a3b8;
}

.form-footer {
  display: flex;
  gap: 12px;
  padding-top: 24px;
  border-top: 1px solid #f1f5f9;
}
.btn-submit {
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  border: none;
  border-radius: 10px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  box-shadow: 0 2px 8px rgba(99,102,241,0.3);
  &:hover {
    box-shadow: 0 4px 12px rgba(99,102,241,0.4);
    transform: translateY(-1px);
  }
}
.btn-cancel {
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  &:hover {
    border-color: #cbd5e1;
    background: #f8fafc;
  }
}
</style>
