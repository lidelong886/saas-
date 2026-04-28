// pages/battery/scan.js
const { scanBattery, rentBattery } = require('../../api/battery')

Page({
  data: {
    batteryInfo: null,
    isScanning: false,
    hasScanned: false
  },

  onLoad: function() {
    this.checkLogin()
  },

  onShow: function() {
    // 每次显示页面时重置状态
    this.setData({
      batteryInfo: null,
      hasScanned: false
    })
  },

  // 检查登录
  checkLogin: function() {
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
            wx.navigateBack()
          }
        }
      })
    }
  },

  // 扫码
  onScanTap: function() {
    if (this.data.isScanning) return

    wx.scanCode({
      onlyFromCamera: true,
      scanType: ['qrCode', 'barCode'],
      success: (res) => {
        const code = res.result
        this.handleScanResult(code)
      },
      fail: (err) => {
        console.error('扫码失败:', err)
        wx.showToast({
          title: '扫码失败',
          icon: 'none'
        })
      }
    })
  },

  // 处理扫码结果
  handleScanResult: function(code) {
    this.setData({ isScanning: true })
    wx.showLoading({ title: '识别中...' })

    scanBattery(code).then(res => {
      wx.hideLoading()
      const batteryInfo = res.data
      
      this.setData({
        batteryInfo,
        hasScanned: true,
        isScanning: false
      })

      // 检查电池状态
      if (batteryInfo.status !== 'available') {
        wx.showModal({
          title: '提示',
          content: '该电池当前不可用',
          showCancel: false
        })
      }
    }).catch(err => {
      wx.hideLoading()
      this.setData({ isScanning: false })
      
      const msg = (err && (err.message || err.msg)) || '无法识别该二维码'
      wx.showModal({
        title: '识别失败',
        content: msg,
        showCancel: false
      })
    })
  },

  // 确认租用
  onConfirmRent: function() {
    const battery = this.data.batteryInfo
    if (!battery) return

    if (battery.status !== 'available') {
      wx.showToast({
        title: '该电池不可用',
        icon: 'none'
      })
      return
    }

    this.rentBattery(battery.id)
  },

  // 租用电池
  rentBattery: function(batteryId) {
    wx.showLoading({ title: '处理中...' })

    rentBattery({
      battery_id: batteryId
    }).then(res => {
      wx.hideLoading()

      const order = res.data || {}
      const isFreeRent = Number(order.total_amount || 0) === 0

      if (isFreeRent) {
        wx.showModal({
          title: '租用成功',
          content: `已使用套餐完成租电${order.order_no ? `（${order.order_no}）` : ''}，无需支付，可直接使用电池。`,
          showCancel: false,
          success: () => {
            wx.navigateBack()
          }
        })
        return
      }

      wx.showModal({
        title: '订单创建成功',
        content: `租电订单已创建${order.order_no ? `（${order.order_no}）` : ''}，请先完成支付后再使用电池。`,
        confirmText: '去支付',
        cancelText: '稍后支付',
        success: (modalRes) => {
          if (modalRes.confirm && order.order_no) {
            wx.redirectTo({
              url: `/pages/order/detail?order_no=${order.order_no}`
            })
          } else {
            wx.navigateBack()
          }
        }
      })
    }).catch(err => {
      wx.hideLoading()

      const msg = (err && (err.message || err.msg)) || '租用失败，请重试'
      wx.showModal({
        title: '租用失败',
        content: msg,
        showCancel: false
      })
    })
  },

  // 查看电池详情
  onViewDetail: function() {
    const battery = this.data.batteryInfo
    if (!battery) return

    wx.navigateTo({
      url: `/pages/battery/detail?id=${battery.id}`
    })
  },

  // 重新扫码
  onRescan: function() {
    this.setData({
      batteryInfo: null,
      hasScanned: false
    })
    this.onScanTap()
  }
})
