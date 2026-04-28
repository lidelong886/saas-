<template>
  <div class="statistics-container">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="statistics-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ dashboard.today_orders }}</div>
            <div class="stat-label">今日订单</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">¥{{ dashboard.today_revenue }}</div>
            <div class="stat-label">今日营收</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ dashboard.battery_stats.utilization_rate }}%</div>
            <div class="stat-label">电池使用率</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ dashboard.user_stats.active_users }}</div>
            <div class="stat-label">活跃用户</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 详细统计 -->
    <el-row :gutter="20" class="detail-row">
      <!-- 订单统计 -->
      <el-col :xs="24" :md="12">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <span>订单统计</span>
            </div>
          </template>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="总订单数">{{ orderStats.total_orders }}</el-descriptions-item>
            <el-descriptions-item label="待支付">{{ orderStats.pending_orders }}</el-descriptions-item>
            <el-descriptions-item label="已支付">{{ orderStats.paid_orders }}</el-descriptions-item>
            <el-descriptions-item label="租用中">{{ orderStats.rented_orders }}</el-descriptions-item>
            <el-descriptions-item label="已完成">{{ orderStats.completed_orders }}</el-descriptions-item>
            <el-descriptions-item label="已取消">{{ orderStats.cancelled_orders }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <!-- 电池统计 -->
      <el-col :xs="24" :md="12">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <span>电池统计</span>
            </div>
          </template>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="总电池数">{{ batteryStats.total_batteries }}</el-descriptions-item>
            <el-descriptions-item label="可用">{{ batteryStats.available_batteries }}</el-descriptions-item>
            <el-descriptions-item label="租用中">{{ batteryStats.rented_batteries }}</el-descriptions-item>
            <el-descriptions-item label="维护中">{{ batteryStats.maintenance_batteries }}</el-descriptions-item>
            <el-descriptions-item label="使用率">{{ batteryStats.utilization_rate }}%</el-descriptions-item>
            <el-descriptions-item label="平均电量">{{ batteryStats.average_power_level }}%</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>

    <!-- 用户统计 -->
    <el-row :gutter="20" class="detail-row">
      <el-col :xs="24">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <span>用户统计</span>
            </div>
          </template>
          <el-descriptions :column="4" border>
            <el-descriptions-item label="总用户数">{{ userStats.total_users }}</el-descriptions-item>
            <el-descriptions-item label="活跃用户">{{ userStats.active_users }}</el-descriptions-item>
            <el-descriptions-item label="实名认证">{{ userStats.verified_users }}</el-descriptions-item>
            <el-descriptions-item label="新用户(7天)">{{ userStats.new_users }}</el-descriptions-item>
            <el-descriptions-item label="认证率">{{ userStats.verification_rate }}%</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ElMessage } from 'element-plus'
import { getDashboardStats, getOrderStats, getBatteryStats } from '@/api/dashboard'

export default {
  name: 'Statistics',
  data() {
    return {
      dashboard: {
        today_orders: 0,
        today_revenue: 0,
        battery_stats: { utilization_rate: 0 },
        user_stats: { active_users: 0 }
      },
      orderStats: {
        total_orders: 0,
        pending_orders: 0,
        paid_orders: 0,
        rented_orders: 0,
        completed_orders: 0,
        cancelled_orders: 0
      },
      batteryStats: {
        total_batteries: 0,
        available_batteries: 0,
        rented_batteries: 0,
        maintenance_batteries: 0,
        utilization_rate: 0,
        average_power_level: 0
      },
      userStats: {
        total_users: 0,
        active_users: 0,
        verified_users: 0,
        new_users: 0,
        verification_rate: 0
      }
    }
  },
  methods: {
    async loadStatistics() {
      try {
        const [dashboardRes, orderRes, batteryRes] = await Promise.all([
          getDashboardStats(),
          getOrderStats(),
          getBatteryStats()
        ])

        if (dashboardRes.code === 0 || dashboardRes.code === 200) {
          const d = dashboardRes.data
          this.dashboard = {
            today_orders: d.today_orders || 0,
            today_revenue: d.today_revenue || 0,
            battery_stats: d.battery_stats || { utilization_rate: 0 },
            user_stats: d.user_stats || { active_users: 0 }
          }
          this.userStats = d.user_stats || {
            total_users: 0,
            active_users: 0,
            verified_users: 0,
            new_users: 0,
            verification_rate: 0
          }
        }
        if (orderRes.code === 0 || orderRes.code === 200) {
          this.orderStats = orderRes.data || {
            total_orders: 0,
            pending_orders: 0,
            paid_orders: 0,
            rented_orders: 0,
            completed_orders: 0,
            cancelled_orders: 0
          }
        }
        if (batteryRes.code === 0 || batteryRes.code === 200) {
          this.batteryStats = batteryRes.data || {
            total_batteries: 0,
            available_batteries: 0,
            rented_batteries: 0,
            maintenance_batteries: 0,
            utilization_rate: 0,
            average_power_level: 0
          }
        }
      } catch (error) {
        console.error('加载统计数据失败:', error)
        ElMessage.error('加载统计数据失败')
      }
    }
  },
  mounted() {
    this.loadStatistics()
    this._timer = setInterval(() => this.loadStatistics(), 30000)
  },
  unmounted() {
    clearInterval(this._timer)
  }
}
</script>

<style lang="scss" scoped>
.statistics-container {
  padding: 20px;

  .statistics-row {
    margin-bottom: 20px;

    .stat-card {
      height: 100%;

      .stat-content {
        text-align: center;
        padding: 20px 0;

        .stat-value {
          font-size: 32px;
          font-weight: bold;
          color: #409eff;
          margin-bottom: 10px;
        }

        .stat-label {
          font-size: 14px;
          color: #606266;
        }
      }
    }
  }

  .detail-row {
    margin-bottom: 20px;

    .box-card {
      height: 100%;
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
  }
}
</style>
