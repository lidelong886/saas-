const { createOrder } = require('../../api/order')

Page({
  data: {
    batteryId: null,
    packageId: null,
    packageType: 'rental',
    hours: 24,
    types: [
      { key: 'exchange', label: '换电' },
      { key: 'purchase', label: '购买电池' }
    ],
    typeIndex: 0,
    loading: false
  },

  onLoad(options) {
    if (!wx.getStorageSync('token')) {
      wx.showModal({
        title: '提示',
        content: '请先登录',
        success: (r) => {
          if (r.confirm) wx.navigateTo({ url: '/pages/profile/login' })
          else wx.navigateBack()
        }
      })
      return
    }
    const bid = options.battery_id
    const packageId = options.package_id
    const packageType = options.order_type || 'rental'
    let typeIndex = 0;
    if (packageType === 'purchase') typeIndex = 1;
    else if (packageType === 'exchange') typeIndex = 0;
    else typeIndex = 0; // Default to exchange if rental is passed

    if (!bid && !packageId) {
      wx.showToast({ title: '请从电池或套餐详情进入', icon: 'none' })
      return
    }

    this.setData({
      batteryId: bid ? parseInt(bid, 10) : null,
      packageId: packageId ? parseInt(packageId, 10) : null,
      packageType,
      typeIndex,
      hours: options.hours ? Number(options.hours) || 24 : this.data.hours
    })
  },

  onHoursChange(e) {
    this.setData({ hours: Number(e.detail.value) || 24 })
  },

  onTypeChange(e) {
    const typeIndex = Number(e.detail.value)
    const packageType = this.data.types[typeIndex].key
    this.setData({ typeIndex, packageType })
  },

  onSubmit() {
    const { batteryId, packageId, hours, types, typeIndex } = this.data
    const order_type = types[typeIndex].key

    if (!batteryId && !packageId) {
      wx.showToast({ title: '缺少下单对象', icon: 'none' })
      return
    }

    if (order_type === 'purchase' && !batteryId && !packageId) {
      wx.showToast({ title: '购买订单需选择电池或套餐', icon: 'none' })
      return
    }

    this.setData({ loading: true })
    createOrder({
      order_type,
      battery_id: batteryId,
      package_id: packageId,
      hours
    })
      .then((res) => {
        const order = res.data
        const no = order && order.order_no
        wx.showToast({ title: '创建成功', icon: 'success' })
        if (no) {
          wx.redirectTo({
            url: `/pages/order/detail?order_no=${no}`
          })
        } else {
          wx.navigateBack()
        }
      })
      .catch((err) => {
        const msg = err && err.message
        wx.showToast({ title: msg || '创建失败', icon: 'none' })
      })
      .finally(() => {
        this.setData({ loading: false })
      })
  }
})
