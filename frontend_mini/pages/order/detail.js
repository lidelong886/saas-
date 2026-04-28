// pages/order/detail.js
const { getOrderDetail, payOrder, cancelOrder } = require('../../api/order')
const { refundOrder } = require('../../api/payment')
const { getNearbyStations } = require('../../api/station')
const { returnBattery } = require('../../api/battery')
const { formatOrderStatus, getCurrentLocation } = require('../../utils/util')

const getOrderTypeText = (order = {}) => {
  if (order.order_type === 'rental') return '租电订单'
  if (order.order_type === 'exchange') return '换电订单'
  if (order.order_type === 'purchase' && order.package_id && !order.battery_id) return '套餐购买'
  if (order.order_type === 'purchase' && order.battery_id) return '电池购买'
  return '其他订单'
}

Page({
  data: {
    orderNo: '',
    order: null,
    paying: false,
    cancelling: false,
    returning: false,
    refunding: false,
    statusText: '',
    typeText: '',
    stations: []
  },

  onLoad: function(options) {
    const orderNo = options.order_no || ''
    if (!orderNo) {
      wx.showToast({ title: '缺少订单号', icon: 'none' })
      return
    }
    this.setData({ orderNo })
    this.refresh()
    // loadStations() 已由 refresh() 末尾调用，此处不再重复
  },

  isValidCoordinatePair: function(lat, lng) {
    if (!Number.isFinite(lat) || !Number.isFinite(lng)) return false
    if (lat === 0 && lng === 0) return false
    if (lat < -90 || lat > 90) return false
    if (lng < -180 || lng > 180) return false
    return true
  },

  getOrderCoordinates: function(order) {
    const lat = Number(order.pickup_latitude || order.return_latitude)
    const lng = Number(order.pickup_longitude || order.return_longitude)
    if (!this.isValidCoordinatePair(lat, lng)) return null
    return { latitude: lat, longitude: lng }
  },

  resolveStationCoordinates: function(order) {
    const orderCoordinates = this.getOrderCoordinates(order)
    if (orderCoordinates) {
      return Promise.resolve(orderCoordinates)
    }

    return getCurrentLocation().then(res => ({
      latitude: Number(res.latitude),
      longitude: Number(res.longitude)
    })).then(coords => {
      if (!this.isValidCoordinatePair(coords.latitude, coords.longitude)) {
        return Promise.reject(new Error('定位坐标无效'))
      }
      return coords
    })
  },

  loadStations: function() {
    const order = this.data.order || {}
    this.resolveStationCoordinates(order).then(({ latitude, longitude }) => {
      return getNearbyStations({ latitude, longitude, radius: 10, limit: 10 })
    }).then(res => {
      const list = (res.data || {}).stations || []
      this.setData({ stations: list })
    }).catch(() => {
      this.setData({ stations: [] })
      wx.showToast({ title: '暂无可用定位，无法加载附近站点', icon: 'none' })
    })
  },

  refresh: function() {
    const { orderNo } = this.data
    wx.showLoading({ title: '加载中...' })
    getOrderDetail(orderNo).then(res => {
      wx.hideLoading()
      const order = res.data || {}
      this.setData({
        order,
        statusText: formatOrderStatus(order.status),
        typeText: getOrderTypeText(order)
      })
      this.loadStations()
    }).catch(() => {
      wx.hideLoading()
      wx.showToast({ title: '加载订单失败', icon: 'none' })
      this.setData({ order: null })
    })
  },

  onPay: function() {
    const { orderNo } = this.data
    this.setData({ paying: true })
    payOrder(orderNo, { payment_method: 'wechat' }).then(() => {
      // 支付成功后判断如果是购买套餐，则提示去卡券页
      const isPackagePurchase = this.data.order && this.data.order.order_type === 'purchase' && this.data.order.package_id;
      
      if (isPackagePurchase) {
        wx.showModal({
          title: '购买成功',
          content: '套餐已存入卡券包，可立即使用或稍后使用',
          confirmText: '立即使用',
          cancelText: '稍后使用',
          success: (res) => {
            if (res.confirm) {
              wx.navigateTo({ url: '/pages/profile/cards' })
            } else {
              this.refresh()
            }
          }
        })
      } else {
        wx.showToast({ title: '支付成功', icon: 'success' })
        this.refresh()
      }
    }).catch(err => {
      const msg = err && err.message
      wx.showToast({ title: msg || '支付失败', icon: 'none' })
    }).finally(() => {
      this.setData({ paying: false })
    })
  },

  // 跳转支付页面
  goToPay: function() {
    wx.navigateTo({
      url: `/pages/order/pay/pay?order_no=${this.data.orderNo}`
    })
  },

  // 取消订单
  onCancel: function() {
    const { orderNo } = this.data
    this.setData({ cancelling: true })
    cancelOrder(orderNo).then(() => {
      wx.showToast({ title: '已取消', icon: 'success' })
      this.refresh()
    }).catch(() => {
      wx.showToast({ title: '取消失败', icon: 'none' })
    }).finally(() => {
      this.setData({ cancelling: false })
    })
  },

  onRefund: function() {
    const { order } = this.data
    if (!order) return

    const isRentalOrder = order.order_type === 'rental'
    if (isRentalOrder) {
      wx.showToast({ title: '租电订单请在完成归还后再处理售后', icon: 'none' })
      return
    }

    const refundableStatuses = ['paid', 'returned', 'completed']
    if (!refundableStatuses.includes(order.status)) {
      wx.showToast({ title: '当前状态不可退款', icon: 'none' })
      return
    }

    wx.showModal({
      title: '申请退款',
      content: `确认申请退款 ¥${order.total_amount || 0} 吗？`,
      success: (res) => {
        if (res.confirm) {
          this.doRefund(order)
        }
      }
    })
  },

  doRefund: function(order) {
    this.setData({ refunding: true })
    refundOrder({
      order_no: order.order_no,
      refund_amount: Number(order.total_amount || 0),
      reason: '用户在小程序端申请退款'
    }).then(() => {
      wx.showToast({ title: '退款申请已提交', icon: 'success' })
      this.refresh()
    }).catch(err => {
      const msg = err && err.message
      wx.showToast({ title: msg || '退款申请失败', icon: 'none' })
    }).finally(() => {
      this.setData({ refunding: false })
    })
  },

  onReturnBattery: function() {
    const { order, stations } = this.data
    if (!order || !order.battery_id) {
      wx.showToast({ title: '缺少电池信息', icon: 'none' })
      return
    }

    const stationList = (stations || []).filter(s => s && s.id && s.name)
    if (stationList.length === 0) {
      wx.showToast({ title: '暂无站点可选，正在重新获取定位', icon: 'none' })
      this.loadStations()
      return
    }

    wx.showActionSheet({
      itemList: stationList.map(s => s.name),
      success: (res) => {
        const station = stationList[res.tapIndex]
        this.doReturnBattery(order.battery_id, station.id)
      }
    })
  },

  doReturnBattery: function(batteryId, stationId) {
    // 模拟扫码电柜交互
    wx.scanCode({
      success: () => {
        wx.showLoading({ title: '连接电柜...' })
        setTimeout(() => {
          wx.hideLoading()
          wx.showModal({
            title: '归还电池',
            content: '已为您打开 5号空仓，请放入电池并关好仓门',
            confirmText: '已放入',
            showCancel: false,
            success: (res) => {
              if (res.confirm) {
                wx.showLoading({ title: '检测中...' })
                setTimeout(() => {
                  wx.hideLoading()
                  this.setData({ returning: true })
                  wx.getLocation({
                    type: 'gcj02',
                    success: (locRes) => {
                      const payload = {
                        battery_id: batteryId,
                        station_id: stationId,
                        latitude: locRes.latitude,
                        longitude: locRes.longitude
                      }
                      this._callReturnApi(payload)
                    },
                    fail: () => {
                      const payload = { battery_id: batteryId, station_id: stationId }
                      this._callReturnApi(payload)
                    }
                  })
                }, 1000)
              }
            }
          })
        }, 800)
      },
      fail: () => {
        wx.showToast({ title: '请先扫描电柜二维码', icon: 'none' })
      }
    })
  },

  _callReturnApi: function(payload) {
    returnBattery(payload).then(() => {
      wx.showToast({ title: '归还成功', icon: 'success' })
      this.refresh()
    }).catch(err => {
      const msg = err && err.message
      wx.showToast({ title: msg || '归还失败', icon: 'none' })
    }).finally(() => {
      this.setData({ returning: false })
    })
  }
})
