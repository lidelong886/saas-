const { getPaymentRecords } = require('../../api/payment')

Page({
  data: {
    records: [],
    loading: false,
    page: 1,
    hasMore: true
  },

  onLoad() {
    this.checkLogin()
    this.loadRecords()
  },

  checkLogin() {
    if (!wx.getStorageSync('token')) {
      wx.showModal({
        title: '提示',
        content: '请先登录',
        success: (res) => {
          if (res.confirm) {
            wx.navigateTo({ url: '/pages/profile/login' })
          } else {
            wx.navigateBack()
          }
        }
      })
    }
  },

  loadRecords() {
    if (this.data.loading || !this.data.hasMore) return

    this.setData({ loading: true })

    getPaymentRecords({
      page: this.data.page,
      per_page: 20
    })
      .then(res => {
        const newRecords = res.data || []
        const hasMore = res.pagination?.has_next || false

        this.setData({
          records: [...this.data.records, ...newRecords],
          hasMore,
          page: this.data.page + 1
        })
      })
      .catch(err => {
        console.error('加载支付记录失败:', err)
        wx.showToast({ title: '加载失败', icon: 'none' })
      })
      .finally(() => {
        this.setData({ loading: false })
      })
  },

  onRecordTap(e) {
    const record = e.currentTarget.dataset.item
    wx.showModal({
      title: '支付详情',
      content: `支付单号: ${record.payment_no}\n金额: ¥${record.amount}\n状态: ${this.getStatusText(record.status)}\n时间: ${record.created_at}`,
      showCancel: false
    })
  },

  getStatusText(status) {
    const map = {
      pending: '待支付',
      paid: '已支付',
      failed: '支付失败',
      refunded: '已退款'
    }
    return map[status] || status
  },

  getTypeText(type) {
    const map = {
      order: '订单支付',
      recharge: '账户充值',
      package: '套餐购买'
    }
    return map[type] || type
  },

  onPullDownRefresh() {
    this.setData({
      records: [],
      page: 1,
      hasMore: true
    })
    this.loadRecords()
    wx.stopPullDownRefresh()
  },

  onReachBottom() {
    this.loadRecords()
  }
})
