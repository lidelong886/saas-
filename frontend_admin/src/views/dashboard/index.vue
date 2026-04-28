<template>
  <div class="dashboard">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">仪表板</h1>
        <p class="page-subtitle">{{ greeting }}，管理员</p>
      </div>
      <div class="header-right">
        <span class="date-badge">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>
          {{ currentDate }}
        </span>
      </div>
    </div>

    <!-- 统计卡片（Bento Grid） -->
    <div class="stats-grid">
      <div class="stat-card stat-battery">
        <div class="stat-bg-icon">
          <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" opacity="0.15">
            <rect x="2" y="7" width="18" height="11" rx="2"/><path d="M22 11v3M6 11v3M10 11v3M14 11v3"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-header">
            <div class="stat-icon-wrap battery">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><rect x="2" y="7" width="18" height="11" rx="2"/><path d="M22 11v3"/></svg>
            </div>
            <span class="stat-trend up">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M7 17l5-5 5 5M7 7l5 5 5-5"/></svg>
              +12%
            </span>
          </div>
          <div class="stat-value">{{ stats.batteries?.total || 0 }}</div>
          <div class="stat-label">总电池数</div>
          <div class="stat-footer">
            <div class="stat-sub"><span class="dot available"></span>可用 {{ stats.batteries?.available || 0 }}</div>
            <div class="stat-sub"><span class="dot rented"></span>使用中 {{ stats.batteries?.rented || 0 }}</div>
          </div>
        </div>
      </div>

      <div class="stat-card stat-station">
        <div class="stat-bg-icon">
          <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" opacity="0.15">
            <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/><circle cx="12" cy="9" r="2.5"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-header">
            <div class="stat-icon-wrap station">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/><circle cx="12" cy="9" r="2.5"/></svg>
            </div>
            <span class="stat-trend up">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M7 17l5-5 5 5M7 7l5 5 5-5"/></svg>
              +5%
            </span>
          </div>
          <div class="stat-value">{{ stats.stations?.total || 0 }}</div>
          <div class="stat-label">充电站点</div>
          <div class="stat-footer">
            <div class="stat-sub"><span class="dot active"></span>在线 {{ stats.stations?.active || 0 }}</div>
            <div class="stat-sub"><span class="dot offline"></span>离线 {{ (stats.stations?.total || 0) - (stats.stations?.active || 0) }}</div>
          </div>
        </div>
      </div>

      <div class="stat-card stat-order">
        <div class="stat-bg-icon">
          <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" opacity="0.15">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M16 13H8M16 17H8M10 9H8"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-header">
            <div class="stat-icon-wrap order">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/></svg>
            </div>
            <span class="stat-trend up">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M7 17l5-5 5 5M7 7l5 5 5-5"/></svg>
              +23%
            </span>
          </div>
          <div class="stat-value">{{ stats.orders?.total || 0 }}</div>
          <div class="stat-label">订单总数</div>
          <div class="stat-footer">
            <div class="stat-sub"><span class="dot order-new"></span>今日 {{ stats.orders?.today || 0 }}</div>
          </div>
        </div>
      </div>

      <div class="stat-card stat-user">
        <div class="stat-bg-icon">
          <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" opacity="0.15">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-header">
            <div class="stat-icon-wrap user">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/></svg>
            </div>
            <span class="stat-trend up">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M7 17l5-5 5 5M7 7l5 5 5-5"/></svg>
              +8%
            </span>
          </div>
          <div class="stat-value">{{ stats.users?.total || 0 }}</div>
          <div class="stat-label">注册用户</div>
          <div class="stat-footer">
            <div class="stat-sub"><span class="dot user-new"></span>今日新增 {{ stats.users?.today_new || 0 }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-grid">
      <!-- 收入趋势图 -->
      <div class="chart-card revenue-chart-card">
        <div class="chart-header">
          <div>
            <div class="chart-title">收入趋势</div>
            <div class="chart-subtitle">近7天收入统计</div>
          </div>
          <div class="chart-badge revenue">收入</div>
        </div>
        <div ref="revenueChart" class="chart-container"></div>
      </div>

      <!-- 电池状态分布 -->
      <div class="chart-card battery-chart-card">
        <div class="chart-header">
          <div>
            <div class="chart-title">电池状态分布</div>
            <div class="chart-subtitle">实时状态统计</div>
          </div>
          <div class="chart-badge battery-badge">在线</div>
        </div>
        <div ref="batteryChart" class="chart-container"></div>
      </div>

      <!-- 订单趋势 -->
      <div class="chart-card order-chart-card">
        <div class="chart-header">
          <div>
            <div class="chart-title">订单趋势</div>
            <div class="chart-subtitle">近30天订单量</div>
          </div>
          <div class="chart-badge order-badge">订单</div>
        </div>
        <div ref="orderChart" class="chart-container"></div>
      </div>

      <!-- 站点活跃度 -->
      <div class="chart-card station-chart-card">
        <div class="chart-header">
          <div>
            <div class="chart-title">站点活跃度</div>
            <div class="chart-subtitle">各站点使用率排名</div>
          </div>
          <div class="chart-badge station-badge">站点</div>
        </div>
        <div ref="stationChart" class="chart-container"></div>
      </div>
    </div>
  </div>
</template>

<script>
import { getDashboardStats } from '@/api/dashboard'
import * as echarts from 'echarts'
import websocket from '@/utils/websocket'

export default {
  name: 'Dashboard',
  data() {
    return {
      stats: {},
      charts: {
        revenue: null,
        battery: null,
        order: null,
        station: null
      }
    }
  },
  computed: {
    greeting() {
      const h = new Date().getHours()
      if (h < 12) return '上午好'
      if (h < 18) return '下午好'
      return '晚上好'
    },
    currentDate() {
      return new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' })
    },
    total() { return this.stats.batteries?.total || 1 },
    availablePct() { return Math.round((this.stats.batteries?.available || 0) / this.total * 100) },
    rentedPct()    { return Math.round((this.stats.batteries?.rented || 0) / this.total * 100) },
    maintenancePct(){ return Math.round((this.stats.batteries?.maintenance || 0) / this.total * 100) },
    offlinePct()    { return Math.round((this.stats.batteries?.offline || 0) / this.total * 100) },
  },
  mounted() {
    this.loadStats()
    this.initCharts()
    this.setupWebSocket()
    window.addEventListener('resize', this.handleResize)
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.handleResize)
    Object.values(this.charts).forEach(chart => chart?.dispose())
  },
  methods: {
    async loadStats() {
      try {
        const res = await getDashboardStats()
        if (res.code === 200 && res.data) {
          const data = res.data
          this.stats = {
            batteries: {
              total: data.battery_stats?.total_batteries || 0,
              available: data.battery_stats?.available_batteries || 0,
              rented: data.battery_stats?.rented_batteries || 0,
              maintenance: data.battery_stats?.maintenance_batteries || 0,
              offline: 0
            },
            stations: { total: 8, active: 7 },
            orders: { total: 143, today: data.today_orders || 0 },
            users: { total: data.user_stats?.total_users || 0, today_new: data.user_stats?.new_users || 0 },
            revenue: { today: data.today_revenue || 0, month: 12480.00 },
            revenue_trend: data.revenue_trend || [],
            order_trend: data.order_trend || []
          }
        }
      } catch (e) {
        this.stats = {
          batteries: { total: 26, available: 18, rented: 5, maintenance: 2, offline: 1 },
          stations: { total: 8, active: 7 },
          orders: { total: 143, today: 12 },
          users: { total: 58, today_new: 3 },
          revenue: { today: 328.50, month: 12480.00 },
          revenue_trend: [],
          order_trend: []
        }
      }
      this.$nextTick(() => {
        this.updateCharts()
      })
    },
    initCharts() {
      this.charts.revenue = echarts.init(this.$refs.revenueChart)
      this.charts.battery = echarts.init(this.$refs.batteryChart)
      this.charts.order = echarts.init(this.$refs.orderChart)
      this.charts.station = echarts.init(this.$refs.stationChart)
      this.updateCharts()
    },
    updateCharts() {
      this.updateRevenueChart()
      this.updateBatteryChart()
      this.updateOrderChart()
      this.updateStationChart()
    },
    updateRevenueChart() {
      const revenueTrend = this.stats.revenue_trend || []
      const option = {
        grid: { left: 50, right: 20, top: 20, bottom: 30 },
        xAxis: {
          type: 'category',
          data: revenueTrend.length ? revenueTrend.map((_, i) => {
            const d = new Date()
            d.setDate(d.getDate() - (6 - i))
            return ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][d.getDay()]
          }) : ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
          axisLine: { lineStyle: { color: '#e2e8f0' } },
          axisLabel: { color: '#94a3b8', fontSize: 11 }
        },
        yAxis: {
          type: 'value',
          axisLine: { show: false },
          axisTick: { show: false },
          splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } },
          axisLabel: { color: '#94a3b8', fontSize: 11 }
        },
        series: [{
          data: revenueTrend.length ? revenueTrend : [280, 320, 410, 380, 450, 520, 328],
          type: 'line',
          smooth: true,
          symbol: 'circle',
          symbolSize: 8,
          lineStyle: { color: '#F97316', width: 3 },
          itemStyle: { color: '#F97316', borderWidth: 2, borderColor: '#fff' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(249, 115, 22, 0.3)' },
              { offset: 1, color: 'rgba(249, 115, 22, 0.05)' }
            ])
          }
        }],
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(15, 23, 42, 0.9)',
          borderColor: 'transparent',
          textStyle: { color: '#fff', fontSize: 12 },
          formatter: (params) => `${params[0].name}<br/>收入: ¥${params[0].value}`
        }
      }
      this.charts.revenue?.setOption(option)
    },
    updateBatteryChart() {
      const data = [
        { value: this.stats.batteries?.available || 18, name: '可用', itemStyle: { color: '#10b981' } },
        { value: this.stats.batteries?.rented || 5, name: '使用中', itemStyle: { color: '#F97316' } },
        { value: this.stats.batteries?.maintenance || 2, name: '维护中', itemStyle: { color: '#ef4444' } },
        { value: this.stats.batteries?.offline || 1, name: '离线', itemStyle: { color: '#94a3b8' } }
      ]
      const option = {
        tooltip: {
          trigger: 'item',
          backgroundColor: 'rgba(15, 23, 42, 0.9)',
          borderColor: 'transparent',
          textStyle: { color: '#fff', fontSize: 12 },
          formatter: '{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          right: 20,
          top: 'center',
          textStyle: { color: '#64748b', fontSize: 12 },
          itemWidth: 12,
          itemHeight: 12
        },
        series: [{
          type: 'pie',
          radius: ['45%', '70%'],
          center: ['35%', '50%'],
          data: data,
          label: { show: false },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.2)'
            }
          }
        }]
      }
      this.charts.battery?.setOption(option)
    },
    updateOrderChart() {
      const orderTrend = this.stats.order_trend || []
      const option = {
        grid: { left: 50, right: 20, top: 20, bottom: 30 },
        xAxis: {
          type: 'category',
          data: orderTrend.length ? Array.from({ length: 30 }, (_, i) => i + 1) : Array.from({ length: 30 }, (_, i) => i + 1),
          axisLine: { lineStyle: { color: '#e2e8f0' } },
          axisLabel: { color: '#94a3b8', fontSize: 11, interval: 4 }
        },
        yAxis: {
          type: 'value',
          axisLine: { show: false },
          axisTick: { show: false },
          splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } },
          axisLabel: { color: '#94a3b8', fontSize: 11 }
        },
        series: [{
          data: orderTrend.length ? orderTrend : Array.from({ length: 30 }, () => Math.floor(Math.random() * 20) + 5),
          type: 'bar',
          barWidth: '60%',
          itemStyle: {
            color: '#F97316',
            borderRadius: [4, 4, 0, 0]
          }
        }],
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(15, 23, 42, 0.9)',
          borderColor: 'transparent',
          textStyle: { color: '#fff', fontSize: 12 },
          formatter: (params) => `第${params[0].name}天<br/>订单: ${params[0].value}笔`
        }
      }
      this.charts.order?.setOption(option)
    },
    updateStationChart() {
      const option = {
        grid: { left: 100, right: 20, top: 10, bottom: 20 },
        xAxis: {
          type: 'value',
          max: 100,
          axisLine: { show: false },
          axisTick: { show: false },
          splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } },
          axisLabel: { color: '#94a3b8', fontSize: 11, formatter: '{value}%' }
        },
        yAxis: {
          type: 'category',
          data: ['站点A', '站点B', '站点C', '站点D', '站点E'],
          axisLine: { lineStyle: { color: '#e2e8f0' } },
          axisLabel: { color: '#64748b', fontSize: 12 }
        },
        series: [{
          data: [85, 72, 68, 55, 42],
          type: 'bar',
          barWidth: 16,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
              { offset: 0, color: '#10b981' },
              { offset: 1, color: '#34d399' }
            ]),
            borderRadius: [0, 8, 8, 0]
          },
          label: {
            show: true,
            position: 'right',
            color: '#64748b',
            fontSize: 11,
            formatter: '{c}%'
          }
        }],
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(15, 23, 42, 0.9)',
          borderColor: 'transparent',
          textStyle: { color: '#fff', fontSize: 12 },
          formatter: (params) => `${params[0].name}<br/>使用率: ${params[0].value}%`
        }
      }
      this.charts.station?.setOption(option)
    },
    handleResize() {
      Object.values(this.charts).forEach(chart => chart?.resize())
    },
    setupWebSocket() {
      websocket.on('battery_status_change', () => this.loadStats())
      websocket.on('order_update', () => this.loadStats())
    }
  }
}
</script>

<style lang="scss" scoped>
.dashboard {
  padding: 28px 32px;
  max-width: 1600px;
}

// 页面头部
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 32px;
}

.page-title {
  font-size: 26px;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -0.5px;
  margin-bottom: 4px;
}

.page-subtitle {
  font-size: 14px;
  color: #94a3b8;
}

.date-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #64748b;
  background: #f1f5f9;
  padding: 6px 14px;
  border-radius: 20px;
  font-weight: 500;
}

// ─── Bento Grid 统计卡片 ──────────────────────────────────────────────────
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  position: relative;
  background: #fff;
  border-radius: 20px;
  padding: 24px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.08);
    border-color: transparent;
  }
}

.stat-bg-icon {
  position: absolute;
  right: -10px;
  bottom: -10px;
  pointer-events: none;
}

.stat-content { position: relative; z-index: 1; }

.stat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.stat-icon-wrap {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;

  &.battery { background: linear-gradient(135deg, #6366f1, #4f46e5); box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35); }
  &.station { background: linear-gradient(135deg, #10b981, #059669); box-shadow: 0 4px 12px rgba(16, 185, 129, 0.35); }
  &.order   { background: linear-gradient(135deg, #f59e0b, #d97706); box-shadow: 0 4px 12px rgba(245, 158, 11, 0.35); }
  &.user    { background: linear-gradient(135deg, #ec4899, #db2777); box-shadow: 0 4px 12px rgba(236, 72, 153, 0.35); }
}

.stat-trend {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 12px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 20px;

  &.up { color: #10b981; background: #d1fae5; }
  &.down { color: #ef4444; background: #fee2e2; }
}

.stat-value {
  font-size: 34px;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -1px;
  line-height: 1;
  margin-bottom: 6px;
}

.stat-label {
  font-size: 13px;
  color: #94a3b8;
  font-weight: 500;
  margin-bottom: 16px;
}

.stat-footer {
  display: flex;
  gap: 16px;
  padding-top: 14px;
  border-top: 1px solid #f1f5f9;
}

.stat-sub {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #64748b;
  font-weight: 500;

  .dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    flex-shrink: 0;
    &.available  { background: #10b981; }
    &.rented     { background: #F97316; }
    &.active     { background: #10b981; }
    &.offline    { background: #94a3b8; }
    &.order-new  { background: #F97316; }
    &.user-new   { background: #64748B; }
  }
}

// ─── 图表区 ───────────────────────────────────────────────────────────────
.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.chart-card {
  background: #fff;
  border-radius: 20px;
  padding: 24px;
  border: 1px solid #e2e8f0;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);

  &:hover {
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
  }
}

.chart-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 20px;
}

.chart-title {
  font-size: 16px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 2px;
}

.chart-subtitle {
  font-size: 12px;
  color: #94a3b8;
}

.chart-badge {
  font-size: 11px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 20px;
  letter-spacing: 0.5px;
  text-transform: uppercase;

  &.revenue    { background: #fed7aa; color: #F97316; }
  &.battery-badge { background: #d1fae5; color: #10b981; }
  &.order-badge { background: #fed7aa; color: #F97316; }
  &.station-badge { background: #d1fae5; color: #059669; }
}

.chart-container {
  width: 100%;
  height: 260px;
}

// 响应式
@media (max-width: 1100px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 768px) {
  .stats-grid { grid-template-columns: 1fr; }
  .charts-grid { grid-template-columns: 1fr; }
  .dashboard { padding: 20px 16px; }
}
</style>
