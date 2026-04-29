// pages/store/detail.js
const { purchaseBatteryCategory } = require('../../api/store')

function formatMoney(value) {
  const number = Number(value || 0)
  return Number.isFinite(number) ? number.toFixed(2).replace(/\.00$/, '') : '0'
}

Page({
  data: {
    battery: null
  },

  onLoad(options) {
    const battery = wx.getStorageSync('storeBatteryDetail') || null
    if (!battery || (options.id && String(battery.id) !== String(options.id))) {
      wx.showToast({ title: '商品信息已失效', icon: 'none' })
      setTimeout(() => wx.navigateBack(), 800)
      return
    }
    this.setData({
      battery: {
        ...battery,
        displayPrice: battery.displayPrice || formatMoney(battery.selling_price || battery.deposit_amount),
        depositDisplay: battery.depositDisplay || formatMoney(battery.deposit_amount)
      }
    })
    wx.setNavigationBarTitle({ title: '商品详情' })
  },

  goBack() {
    wx.navigateBack()
  },

  buyNow() {
    const battery = this.data.battery
    if (!battery) return

    if (!wx.getStorageSync('token')) {
      wx.showModal({
        title: '登录后购买',
        content: '购买专属电池需要先登录账号。',
        confirmText: '去登录',
        success: res => {
          if (res.confirm) wx.navigateTo({ url: '/pages/profile/login' })
        }
      })
      return
    }

    wx.showModal({
      title: '确认购买',
      content: `${battery.modelName || battery.model}\n应付 ¥${battery.displayPrice}`,
      confirmText: '立即购买',
      success: res => {
        if (!res.confirm) return
        wx.showLoading({ title: '提交订单...' })
        purchaseBatteryCategory({
          voltage_type: battery.voltageType || battery.voltage_type,
          capacity: battery.capacity
        }).then(() => {
          wx.hideLoading()
          wx.showToast({ title: '购买成功', icon: 'success' })
          setTimeout(() => wx.navigateBack(), 900)
        }).catch(err => {
          wx.hideLoading()
          const msg = (err && (err.message || err.msg)) || '购买失败'
          wx.showToast({ title: msg, icon: 'none' })
        })
      }
    })
  }
})
