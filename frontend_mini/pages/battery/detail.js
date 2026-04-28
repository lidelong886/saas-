const { getBatteryDetail, rentBattery } = require('../../api/battery')

Page({
  data: {
    battery: null,
    loading: true
  },

  onLoad(options) {
    if (options.id) {
      this.loadDetail(options.id)
    } else {
      wx.showToast({ title: '缺少电池ID', icon: 'none' })
      setTimeout(() => wx.navigateBack(), 1500)
    }
  },

  loadDetail(id) {
    this.setData({ loading: true })
    getBatteryDetail(id).then(res => {
      this.setData({ battery: res.data, loading: false })
    }).catch(err => {
      wx.showToast({ title: '加载失败', icon: 'none' })
      this.setData({ loading: false })
    })
  },

  goCreateOrder() {
    const battery = this.data.battery
    if (!battery || !battery.id) return

    if (!wx.getStorageSync('token')) {
      wx.showModal({
        title: '提示',
        content: '请先登录后再租用电池',
        confirmText: '去登录',
        success: (res) => {
          if (res.confirm) wx.navigateTo({ url: '/pages/profile/login' })
        }
      })
      return
    }

    wx.showLoading({ title: '创建订单中...' })
    rentBattery({
      battery_id: battery.id,
      hours: 24
    }).then(res => {
      wx.hideLoading()
      const order = res.data
      const order_no = order && order.order_no
      if (order_no) {
        wx.navigateTo({
          url: `/pages/order/detail?order_no=${order_no}`
        })
      }
    }).catch(err => {
      wx.hideLoading()
      const msg = err && err.message
      wx.showToast({ title: msg || '创建订单失败', icon: 'none' })
    })
  }
})
