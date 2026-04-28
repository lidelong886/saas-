// pages/fault/list.js
const { getMyFaultReports } = require('../../api/fault')

Page({
  data: {
    reports: [],
    page: 1,
    hasMore: true,
    isLoading: false,
    statusMap: {
      pending: { text: '待处理', color: '#fa8c16' },
      processing: { text: '处理中', color: '#1890ff' },
      resolved: { text: '已解决', color: '#52c41a' },
      closed: { text: '已关闭', color: '#999' }
    },
    typeMap: {
      battery: '电池故障',
      cabinet: '柜机故障',
      station: '站点问题',
      other: '其他'
    }
  },

  onLoad() {
    this.loadReports(true)
  },

  onShow() {
    if (this.data.reports.length > 0) {
      this.loadReports(true)
    }
  },

  loadReports(isRefresh) {
    if (this.data.isLoading) return

    if (isRefresh) {
      this.setData({ page: 1, hasMore: true, reports: [] })
    }

    this.setData({ isLoading: true })

    getMyFaultReports({
      page: this.data.page,
      per_page: 20
    }).then(res => {
      const list = res.data.list || res.data.items || []
      const reports = isRefresh ? list : [...this.data.reports, ...list]
      const pagination = res.data.pagination || {}

      this.setData({
        reports,
        page: this.data.page + 1,
        hasMore: pagination.page < pagination.pages,
        isLoading: false
      })
    }).catch(() => {
      wx.showToast({ title: '加载失败', icon: 'none' })
      this.setData({ isLoading: false })
    })
  },

  onPullDownRefresh() {
    this.loadReports(true)
    wx.stopPullDownRefresh()
  },

  onReachBottom() {
    if (this.data.hasMore && !this.data.isLoading) {
      this.loadReports(false)
    }
  },

  onNewReport() {
    wx.navigateTo({ url: '/pages/fault/report' })
  }
})
