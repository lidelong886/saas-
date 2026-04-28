const { getPackageDetail } = require('../../api/package')

Page({
  data: {
    packageInfo: null,
    loading: true,
    id: null
  },

  onLoad(options) {
    const id = options.id
    if (!id) {
      wx.showToast({ title: '参数错误', icon: 'none' })
      this.setData({ loading: false })
      return
    }
    this.setData({ id })
    this.fetch(id)
  },

  fetch(id) {
    this.setData({ loading: true })
    getPackageDetail(id)
      .then((res) => {
        this.setData({
          packageInfo: this.normalizePackage(res.data || {}),
          loading: false
        })
      })
      .catch((err) => {
        console.error('加载套餐详情失败:', err)
        this.setData({ packageInfo: null, loading: false })
      })
  },

  normalizePackage(item) {
    const packageType = item.package_type || 'rental'
    return {
      ...item,
      packageTypeText: this.formatType(packageType),
      priceText: this.formatMoney(item.price),
      depositText: this.formatMoney(item.deposit_amount),
      exchangeFeeText: this.formatMoney(item.exchange_fee),
      durationText: item.hours ? `${item.hours}小时` : '按套餐配置'
    }
  },

  formatType(type) {
    const map = {
      rental: '租用套餐',
      purchase: '购买套餐',
      exchange: '换电套餐'
    }
    return map[type] || type
  },

  formatMoney(value) {
    return `¥${Number(value || 0).toFixed(2)}`
  },

  onCreateOrder() {
    const info = this.data.packageInfo
    if (!info) return

    if (!wx.getStorageSync('token')) {
      wx.showModal({
        title: '提示',
        content: '请先登录后再下单',
        confirmText: '去登录',
        success: (res) => {
          if (res.confirm) {
            wx.navigateTo({ url: '/pages/profile/login' })
          }
        }
      })
      return
    }



    if (info.package_type === 'exchange') {
      wx.showModal({
        title: '换电套餐',
        content: '购买后即可享受相应的换电权益。',
        showCancel: false
      })
    }

    // 对于购买套餐，统一使用 purchase 订单类型，不需要选电池
    wx.navigateTo({
      url: `/pages/order/create?package_id=${info.id}&order_type=purchase&hours=${info.hours || 24}`
    })
  }
})
