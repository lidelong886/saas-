<template>
  <div class="order-detail">
    <div class="page-header">
      <el-button @click="$router.back()">返回</el-button>
      <h2>订单详情</h2>
    </div>
    <el-card v-loading="loading">
      <el-descriptions :column="2" border v-if="order">
        <el-descriptions-item label="订单号">{{ order.order_no }}</el-descriptions-item>
        <el-descriptions-item label="订单类型">{{ typeMap[order.order_type] }}</el-descriptions-item>
        <el-descriptions-item label="订单状态">
          <el-tag :type="statusTypeMap[order.status]">{{ statusMap[order.status] }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="用户">{{ order.user_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="电池编码">{{ order.battery_code || '-' }}</el-descriptions-item>
        <el-descriptions-item label="站点">{{ order.station_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="租用时长">{{ order.rental_hours }}小时</el-descriptions-item>
        <el-descriptions-item label="单价">¥{{ order.unit_price }}/小时</el-descriptions-item>
        <el-descriptions-item label="租用费">¥{{ order.rental_fee }}</el-descriptions-item>
        <el-descriptions-item label="押金">¥{{ order.deposit_fee }}</el-descriptions-item>
        <el-descriptions-item label="总金额">¥{{ order.total_amount }}</el-descriptions-item>
        <el-descriptions-item label="支付方式">{{ order.payment_method || '-' }}</el-descriptions-item>
        <el-descriptions-item label="下单时间">{{ order.created_at }}</el-descriptions-item>
        <el-descriptions-item label="支付时间">{{ order.payment_time || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script>
import { getOrderDetail } from '@/api/order'
import { ElMessage } from 'element-plus'
export default {
  name: 'OrderDetail',
  data() {
    return {
      loading: true, order: null,
      typeMap: { rental: '租用', purchase: '购买', exchange: '换电' },
      statusMap: { pending: '待支付', paid: '已支付', rented: '租用中', returned: '已归还', completed: '已完成', cancelled: '已取消', refunded: '已退款' },
      statusTypeMap: { pending: 'warning', paid: 'info', rented: 'primary', returned: '', completed: 'success', cancelled: 'danger', refunded: 'danger' }
    }
  },
  mounted() { this.loadOrder() },
  methods: {
    async loadOrder() {
      try {
        const res = await getOrderDetail(this.$route.params.id)
        this.order = res.data
      } catch (e) { ElMessage.error('加载失败'); this.$router.back() } finally { this.loading = false }
    }
  }
}
</script>

<style scoped>
.order-detail { padding: 20px; }
.page-header { display: flex; align-items: center; gap: 20px; margin-bottom: 20px; }
.page-header h2 { margin: 0; }
</style>
