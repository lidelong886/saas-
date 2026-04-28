const { getExchangeHistory } = require('../../api/exchange')

Page({
  data: {
    records: [],
    isLoading: false,
    hasMore: true,
    page: 1,
    pageSize: 20
  },

  onLoad() {
    this.checkLogin()
  },

  onShow() {
    if (wx.getStorageSync('token')) {
      this.loadRecords(true)
    }
  },

  checkLogin() {
    const token = wx.getStorageSync('token')
    if (!token) {
      wx.showModal({
        title: '提示',
        content: '请先登录',
        confirmText: '去登录',
        success: (res) => {
          if (res.confirm) {
            wx.redirectTo({
              url: '/pages/profile/login'
            })
          } else {
            wx.switchTab({
              url: '/pages/profile/profile'
            })
          }
        }
      })
    }
  },

  loadRecords(isRefresh = false) {
    if (this.data.isLoading) return

    const nextPage = isRefresh ? 1 : this.data.page
    if (!isRefresh && !this.data.hasMore) return

    if (isRefresh) {
      this.setData({
        page: 1,
        hasMore: true,
        records: []
      })
    }

    this.setData({ isLoading: true })

    getExchangeHistory({
      page: nextPage,
      per_page: this.data.pageSize
    }).then(res => {
      const payload = res.data || {}
      const list = payload.list || payload.items || []
      const newRecords = list.map(item => this.normalizeRecord(item))
      const records = isRefresh ? newRecords : this.data.records.concat(newRecords)

      this.setData({
        records,
        page: nextPage + 1,
        hasMore: newRecords.length === this.data.pageSize,
        isLoading: false
      })
    }).catch(err => {
      console.error('加载换电记录失败:', err)
      wx.showToast({ title: '加载换电记录失败', icon: 'none' })
      this.setData({ isLoading: false })
    })
  },

  normalizeRecord(item) {
    const status = item.status || 'completed'
    const oldB = item.old_battery
    const newB = item.new_battery
    const sta = item.station
    const cab = item.cabinet
    return {
      ...item,
      status,
      statusText: this.formatStatus(status),
      oldBatteryCode: item.old_battery_code || (oldB && oldB.battery_code) || item.old_battery_id || '-',
      newBatteryCode: item.new_battery_code || (newB && newB.battery_code) || item.new_battery_id || '-',
      stationName: item.station_name || (sta && sta.name) || item.station_id || '-',
      cabinetName: item.cabinet_name || (cab && cab.name) || item.cabinet_id || '-',
      exchangeFeeText: this.formatAmount(item.exchange_fee),
      exchangeTimeText: item.exchange_time || item.created_at || '-',
      recordNo: item.record_no || item.id || ''
    }
  },

  formatStatus(status) {
    const map = {
      pending: '处理中',
      completed: '已完成',
      failed: '失败'
    }
    return map[status] || status
  },

  formatAmount(amount) {
    const numeric = Number(amount || 0)
    return `¥${numeric.toFixed(2)}`
  },

  onPullDownRefresh() {
    this.loadRecords(true)
    wx.stopPullDownRefresh()
  },

  onReachBottom() {
    if (this.data.hasMore && !this.data.isLoading) {
      this.loadRecords()
    }
  },

  goToIndex() {
    wx.switchTab({ url: '/pages/index/index' })
  }
})
