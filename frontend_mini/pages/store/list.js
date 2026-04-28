// pages/store/list.js
const { getStoreBatteries, purchaseBattery } = require('../../api/store')

Page({
  data: {
    batteries: [],
    page: 1,
    hasMore: true,
    isLoading: false
  },

  onLoad: function() {
    this.loadBatteries()
  },

  loadBatteries: function() {
    if (this.data.isLoading || !this.data.hasMore) return

    this.setData({ isLoading: true })
    wx.showLoading({ title: '加载中...' })

    getStoreBatteries({
      page: this.data.page,
      per_page: 20
    }).then(res => {
      const data = res.data || {}
      const list = data.list || data.items || []

      this.setData({
        batteries: this.data.page === 1 ? list : [...this.data.batteries, ...list],
        hasMore: list.length >= 20,
        page: this.data.page + 1,
        isLoading: false
      })
      wx.hideLoading()
    }).catch(err => {
      wx.hideLoading()
      wx.showToast({ title: '加载失败', icon: 'none' })
      this.setData({ isLoading: false })
    })
  },

  onBatteryTap: function(e) {
    const battery = e.currentTarget.dataset.battery
    wx.showModal({
      title: battery.model,
      content: `电池编号: ${battery.battery_code}\n容量: ${battery.capacity}mAh\n电量: ${battery.power_level}%\n售价: ¥${battery.selling_price || battery.deposit_amount}`,
      showCancel: false
    })
  },

  onPurchaseTap: function(e) {
    const battery = e.currentTarget.dataset.battery

    wx.showModal({
      title: '确认购买',
      content: `确定购买 ${battery.model} 吗？\n价格：¥${battery.selling_price || battery.deposit_amount}`,
      success: (res) => {
        if (res.confirm) {
          this.purchaseBattery(battery.id)
        }
      }
    })
  },

  purchaseBattery: function(batteryId) {
    wx.showLoading({ title: '购买中...' })

    purchaseBattery(batteryId).then(res => {
      wx.hideLoading()
      wx.showToast({ title: '购买成功', icon: 'success' })
      setTimeout(() => {
        this.setData({ page: 1, hasMore: true })
        this.loadBatteries()
      }, 1500)
    }).catch(err => {
      wx.hideLoading()
      const msg = (err && (err.message || err.msg)) || '购买失败'
      wx.showToast({ title: msg, icon: 'none' })
    })
  },

  onReachBottom: function() {
    this.loadBatteries()
  },

  onPullDownRefresh: function() {
    this.setData({ page: 1, hasMore: true })
    this.loadBatteries()
    wx.stopPullDownRefresh()
  }
})
