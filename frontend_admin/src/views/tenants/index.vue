<template>
  <div class="tenants">
    <div class="tenant-hero">
      <div>
        <h2>租户管理</h2>
        <p>支持后台创建租户、小程序入驻申请审核与多租户演示切换</p>
      </div>
      <el-button type="primary" plain @click="showCreateDialog">新增租户</el-button>
    </div>

    <div class="summary-grid">
      <el-card class="summary-card primary"><div class="summary-label">租户总数</div><div class="summary-value">{{ tenants.length }}</div></el-card>
      <el-card class="summary-card success"><div class="summary-label">正常租户</div><div class="summary-value">{{ activeCount }}</div></el-card>
      <el-card class="summary-card warning"><div class="summary-label">待审申请</div><div class="summary-value">{{ pendingApplications }}</div></el-card>
      <el-card class="summary-card info"><div class="summary-label">站点总数</div><div class="summary-value">{{ totalStations }}</div></el-card>
    </div>

    <el-card class="tenant-table-card" v-loading="loading">
      <template #header><div class="title">租户列表</div></template>
      <el-table :data="tenants" style="width: 100%">
        <el-table-column prop="code" label="租户编码" width="140" />
        <el-table-column prop="brand_name" label="品牌名称" width="160">
          <template #default="{ row }">{{ row.brand_name || row.name }}</template>
        </el-table-column>
        <el-table-column prop="name" label="租户名称" width="180" />
        <el-table-column prop="contact_name" label="联系人" width="120" />
        <el-table-column prop="contact_phone" label="联系电话" width="140" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }"><el-tag :type="row.status === 'active' ? 'success' : 'danger'">{{ row.status === 'active' ? '正常' : '停用' }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="user_count" label="用户数" width="90" />
        <el-table-column prop="station_count" label="站点数" width="90" />
        <el-table-column prop="battery_count" label="电池数" width="90" />
        <el-table-column prop="created_at" label="创建时间" min-width="170" />
      </el-table>
    </el-card>

    <el-card class="tenant-table-card" v-loading="applicationLoading">
      <template #header>
        <div class="table-header">
          <div class="title">小程序入驻申请</div>
          <el-button size="small" @click="loadApplications">刷新</el-button>
        </div>
      </template>
      <el-table :data="applications" style="width: 100%">
        <el-table-column prop="name" label="申请名称" min-width="160" />
        <el-table-column prop="contact_name" label="联系人" width="110" />
        <el-table-column prop="contact_phone" label="电话" width="130" />
        <el-table-column prop="city" label="城市" width="130" />
        <el-table-column prop="fund_level" label="投入规模" width="120" />
        <el-table-column prop="message" label="留言" min-width="180" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }"><el-tag :type="getApplicationTag(row.status)">{{ getApplicationStatus(row.status) }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="review_remark" label="审核备注" min-width="160" show-overflow-tooltip />
        <el-table-column label="操作" width="170" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'pending'" size="small" type="success" @click="review(row, 'approve')">通过</el-button>
            <el-button v-if="row.status === 'pending'" size="small" type="danger" plain @click="review(row, 'reject')">拒绝</el-button>
            <span v-else class="muted">已处理</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="createVisible" title="新增租户" width="520px">
      <el-form :model="createForm" label-width="96px">
        <el-form-item label="租户名称"><el-input v-model="createForm.name" placeholder="例如：蜂鸟换电" /></el-form-item>
        <el-form-item label="租户编码"><el-input v-model="createForm.code" placeholder="例如：FENGNIAO" /></el-form-item>
        <el-form-item label="品牌名称"><el-input v-model="createForm.brand_name" placeholder="小程序展示名称" /></el-form-item>
        <el-form-item label="联系人"><el-input v-model="createForm.contact_name" /></el-form-item>
        <el-form-item label="联系电话"><el-input v-model="createForm.contact_phone" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCreate">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ElMessage, ElMessageBox } from 'element-plus'
import { getTenantList, createTenant, getTenantApplications, reviewTenantApplication } from '@/api/system'

export default {
  name: 'Tenants',
  data() {
    return {
      loading: false,
      applicationLoading: false,
      tenants: [],
      applications: [],
      createVisible: false,
      createForm: { name: '', code: '', brand_name: '', contact_name: '', contact_phone: '' }
    }
  },
  computed: {
    activeCount() { return this.tenants.filter(item => item.status === 'active').length },
    totalStations() { return this.tenants.reduce((sum, item) => sum + Number(item.station_count || 0), 0) },
    pendingApplications() { return this.applications.filter(item => item.status === 'pending').length }
  },
  mounted() {
    this.loadTenants()
    this.loadApplications()
  },
  methods: {
    async loadTenants() {
      this.loading = true
      try {
        const res = await getTenantList()
        this.tenants = res.data || []
      } catch (error) {
        ElMessage.error('加载租户列表失败')
      } finally {
        this.loading = false
      }
    },
    async loadApplications() {
      this.applicationLoading = true
      try {
        const res = await getTenantApplications()
        this.applications = res.data || []
      } catch (error) {
        ElMessage.error('加载入驻申请失败')
      } finally {
        this.applicationLoading = false
      }
    },
    showCreateDialog() {
      this.createForm = { name: '', code: '', brand_name: '', contact_name: '', contact_phone: '' }
      this.createVisible = true
    },
    async submitCreate() {
      if (!this.createForm.name || !this.createForm.code) return ElMessage.warning('请填写租户名称和编码')
      try {
        await createTenant(this.createForm)
        ElMessage.success('租户创建成功')
        this.createVisible = false
        this.loadTenants()
      } catch (error) {
        ElMessage.error('创建失败：' + (error.response?.data?.message || error.message))
      }
    },
    async review(row, action) {
      const label = action === 'approve' ? '通过并创建租户' : '拒绝'
      try {
        await ElMessageBox.confirm(`确认${label}“${row.name}”？处理结果会通过通知发送给小程序用户。`, '审核确认', { type: action === 'approve' ? 'success' : 'warning' })
        await reviewTenantApplication(row.id, { action, remark: action === 'approve' ? '欢迎加入 PowerNest 平台' : '资料暂不完整，请补充后再提交' })
        ElMessage.success('审核完成')
        this.loadApplications()
        this.loadTenants()
      } catch (error) {
        if (error !== 'cancel') ElMessage.error('审核失败：' + (error.response?.data?.message || error.message))
      }
    },
    getApplicationStatus(status) {
      return { pending: '待审核', approved: '已通过', rejected: '已拒绝' }[status] || status
    },
    getApplicationTag(status) {
      return { pending: 'warning', approved: 'success', rejected: 'danger' }[status] || 'info'
    }
  }
}
</script>

<style lang="scss" scoped>
.tenants { padding: 20px; }
.tenant-hero { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding: 24px 28px; border-radius: 20px; background: linear-gradient(135deg, #1d4ed8 0%, #3b82f6 60%, #60a5fa 100%); color: #fff; box-shadow: 0 18px 40px rgba(59, 130, 246, 0.2); }
.tenant-hero h2 { margin: 0; font-size: 24px; font-weight: 700; }
.tenant-hero p { margin: 8px 0 0; opacity: 0.92; }
.summary-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; margin-bottom: 20px; }
.summary-card { border: none; border-radius: 16px; color: #fff; }
.summary-card.primary { background: linear-gradient(135deg, #0ea5e9, #2563eb); }
.summary-card.success { background: linear-gradient(135deg, #10b981, #059669); }
.summary-card.warning { background: linear-gradient(135deg, #f59e0b, #d97706); }
.summary-card.info { background: linear-gradient(135deg, #8b5cf6, #6d28d9); }
.summary-label { font-size: 13px; opacity: 0.9; }
.summary-value { margin-top: 10px; font-size: 30px; font-weight: 800; }
.tenant-table-card { margin-bottom: 20px; border-radius: 16px; overflow: hidden; }
.table-header { display: flex; justify-content: space-between; align-items: center; }
.title { font-size: 18px; font-weight: 700; color: #0f172a; }
.muted { color: #94a3b8; font-size: 13px; }
</style>
