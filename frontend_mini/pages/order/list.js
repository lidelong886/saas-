const { getOrders, cancelOrder } = require('../../api/order')
const { formatOrderStatus } = require('../../utils/util')

const getOrderTypeText = (order = {}) => {
  if (order.order_type === 'rental') return '租电订单'
  if (order.order_type === 'exchange') return '换电订单'
  if (order.order_type === 'purchase' && order.package_id && !order.battery_id) return '套餐购买'
  if (order.order_type === 'purchase' && order.battery_id) return '电池购买'
  return '其他订单'
}

Page({
  data: {
    orders: [],
    filteredOrders: [],
    isLoading: false,
    hasMore: true,
    page: 1,
    pageSize: 20,
    activeTab: 'all',
    tabs: [
      { key: 'all', label: '全部' },
      { key: 'active', label: '进行中' },
      { key: 'completed', label: '已完成' },
      { key: 'cancelled', label: '已取消' }
    ]
  },

  onLoad: function() {
    this.checkLogin()
  },

  onShow: function() {
    if (wx.getStorageSync('token')) {
      this.loadOrders(true)
    }
  },

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
            wx.switchTab({
              url: '/pages/index/index'
            })
          }
        }
      })
    }
  },

  loadOrders: function(isRefresh = false, tabKey) {
    if (this.data.isLoading) return

    if (isRefresh) {
      this.setData({
        page: 1,
        hasMore: true,
        orders: []
      })
    }

    this.setData({ isLoading: true })

    const { page, pageSize } = this.data
    const filterTab = tabKey != null ? tabKey : this.data.activeTab
    const params = {
      page,
      per_page: pageSize
    }

    getOrders(params).then(res => {
      const inner = res.data || {}
      const list = inner.list || inner.items || []
      const newOrders = list.map(o => ({
        ...o,
        status_text: formatOrderStatus(o.status),
        type_text: getOrderTypeText(o)
      }))
      const orders = isRefresh ? newOrders : [...this.data.orders, ...newOrders]
      const filteredOrders = this.filterOrdersByTab(orders, filterTab)

      this.setData({
        orders,
        filteredOrders,
        page: page + 1,
        hasMore: newOrders.length === pageSize,
        isLoading: false
      })
    }).catch((err) => {
      const msg = (err && (err.message || err.msg)) || '加载订单失败'
      wx.showToast({ title: msg, icon: 'none' })
      console.error('加载订单失败:', err)
      this.setData({ isLoading: false })
    })
  },

  onTabChange: function(e) {
    const activeTab = e.currentTarget.dataset.tab
    this.setData({
      activeTab,
      page: 1,
      orders: []
    })
    this.loadOrders(true, activeTab)
  },

  onOrderTap: function(e) {
    const orderNo = e.currentTarget.dataset.orderNo
    wx.navigateTo({
      url: `/pages/order/detail?order_no=${orderNo}`
    })
  },

  onCancelOrder: function(e) {
    e.stopPropagation()
    const orderNo = e.currentTarget.dataset.orderNo

    wx.showModal({
      title: '确认取消',
      content: '确定要取消这个订单吗？',
      success: (res) => {
        if (res.confirm) {
          this.doCancelOrder(orderNo)
        }
      }
    })
  },

  doCancelOrder: function(orderNo) {
    wx.showLoading({ title: '取消中...' })

    cancelOrder(orderNo).then(() => {
      wx.hideLoading()
      wx.showToast({
        title: '取消成功',
        icon: 'success'
      })
      this.loadOrders(true)
    }).catch(err => {
      wx.hideLoading()
      wx.showToast({
        title: (err && err.message) || '取消失败',
        icon: 'none'
      })
    })
  },

  onPayOrder: function(e) {
    e.stopPropagation()
    const orderNo = e.currentTarget.dataset.orderNo

    wx.navigateTo({
      url: `/pages/order/detail?order_no=${orderNo}`
    })
  },

  onReviewOrder: function(e) {
    e.stopPropagation()
    wx.showToast({ title: '功能开发中', icon: 'none' })
  },

  onPullDownRefresh: function() {
    this.loadOrders(true)
    wx.stopPullDownRefresh()
  },

  onReachBottom: function() {
    if (this.data.hasMore && !this.data.isLoading) {
      this.loadOrders()
    }
  },

  goToIndex: function() {
    wx.switchTab({ url: '/pages/index/index' })
  },

  formatTime: function(time) {
    if (!time) return ''
    const date = new Date(time)
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
  },

  filterOrdersByTab: function(orders, tabKey) {
    if (tabKey === 'all') return orders
    if (tabKey === 'completed') return orders.filter(o => o.status === 'completed')
    if (tabKey === 'cancelled') return orders.filter(o => o.status === 'cancelled' || o.status === 'refunded')
    return orders.filter(o => ['pending', 'paid', 'rented', 'returned'].includes(o.status))
  }
})
