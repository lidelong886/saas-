// pages/order/pay/pay.js
const { getOrderDetail, payOrder } = require('../../../api/order')
const { getUserBalance } = require('../../../api/user')

Page({
  data: {
    orderNo: '',
    order: null,
    userBalance: 0,
    selectedMethod: 'wechat',
    paying: false,
    showResult: false,
    payResult: '',
    payError: '',
    orderAmountFixed: '0.00',
    userBalanceFixed: '0.00',
    needMoreFixed: '0.00'
  },

  onLoad: function(options) {
    const orderNo = options.order_no || ''
    if (!orderNo) {
      wx.showToast({ title: '缺少订单号', icon: 'none' })
      setTimeout(() => wx.navigateBack(), 1500)
      return
    }
    this.setData({ orderNo })
    this.refresh()
  },

  onShow: function() {
    if (this.data.order) {
      this.loadUserBalanceSilent()
    }
  },

  refresh: function() {
    wx.showLoading({ title: '加载订单...' })
    Promise.all([
      getOrderDetail(this.data.orderNo),
      getUserBalance()
    ]).then(([orderRes, balanceRes]) => {
      wx.hideLoading()
      const order = orderRes.data || {}
      const balance = Number((balanceRes.data || {}).balance) || 0
      const amount = Number(order.total_amount || 0)

      this.setData({
        order,
        userBalance: balance,
        orderAmountFixed: amount.toFixed(2),
        userBalanceFixed: balance.toFixed(2),
        needMoreFixed: Math.max(0, amount - balance).toFixed(2)
      })

      if (order.status !== 'pending') {
        const map = { paid: '已支付', rented: '进行中', completed: '已完成', cancelled: '已取消' }
        wx.showModal({
          title: '订单状态异常',
          content: `当前订单为"${map[order.status] || order.status}"状态，无需支付`,
          showCancel: false,
          success: () => wx.navigateBack()
        })
        return
      }

      if (balance >= amount && amount > 0) {
        this.setData({ selectedMethod: 'balance' })
      } else {
        this.setData({ selectedMethod: 'wechat' })
      }
    }).catch(() => {
      wx.hideLoading()
      wx.showToast({ title: '加载订单失败', icon: 'none' })
      setTimeout(() => wx.navigateBack(), 1500)
    })
  },

  loadUserBalanceSilent: function() {
    return getUserBalance()
      .then(res => {
        const b = Number((res.data || {}).balance) || 0
        const orderData = (res.data || {}).order || {}
        const amount = Number(orderData.total_amount || 0)
        this.setData({
          userBalance: b,
          userBalanceFixed: b.toFixed(2),
          needMoreFixed: Math.max(0, amount - b).toFixed(2)
        })
        return b
      })
      .catch(() => 0)
  },

  selectPayment: function(e) {
    const method = e.currentTarget.dataset.method
    const isBalanceInsufficient = method === 'balance' && this.data.userBalance < Number((this.data.order || {}).total_amount || 0)
    if (isBalanceInsufficient) return
    this.setData({ selectedMethod: method })
  },

  submitPayment: function() {
    const { orderNo, order, selectedMethod, paying } = this.data

    if (paying) return
    if (!order || order.status !== 'pending') {
      wx.showToast({ title: '订单状态不允许支付', icon: 'none' })
      return
    }

    // 余额支付但余额不足 → 引导充值
    if (selectedMethod === 'balance') {
      const needed = Number(order.total_amount || 0) - this.data.userBalance
      if (needed > 0) {
        wx.showModal({
          title: '余额不足',
          content: `还需 ¥${needed.toFixed(2)}，是否前往充值？`,
          confirmText: '去充值',
          success: (res) => {
            if (res.confirm) {
              wx.navigateTo({ url: '/pages/profile/balance' })
            }
          }
        })
        return
      }
    }

    this.setData({ paying: true })

    payOrder(orderNo, { payment_method: selectedMethod })
      .then(res => {
        const result = res.data || {}

        // 余额支付由后端完成扣款与订单状态流转
        if (selectedMethod === 'balance') {
          this.showPayResult('success')
          return
        }

        // 微信/支付宝：调用微信支付
        const payParams = result.wechat_params || result.payment_params || {}
        if (payParams && payParams.timeStamp) {
          wx.requestPayment({
            ...payParams,
            success: () => this.showPayResult('success'),
            fail: (err) => {
              const msg = err && err.errMsg ? (err.errMsg.includes('cancel') ? '用户取消支付' : err.errMsg) : '支付失败'
              this.showPayResult('fail', msg)
            }
          })
        } else {
          // 毕设演示模式：后端返回演示支付结果，用于完整展示订单闭环
          this.showPayResult('success')
        }
      })
      .catch(err => {
        const msg = (err && err.message) || '支付发起失败'
        this.showPayResult('fail', msg)
      })
      .finally(() => {
        this.setData({ paying: false })
      })
  },

  showPayResult: function(result, errorMsg) {
    this.setData({
      showResult: true,
      payResult: result,
      payError: errorMsg || ''
    })
  },

  closeResult: function() {
    this.setData({ showResult: false })
    if (this.data.payResult === 'success') {
      wx.switchTab({ url: '/pages/index/index' })
    }
  },

  goToOrder: function() {
    wx.redirectTo({
      url: `/pages/order/detail?order_no=${this.data.orderNo}`
    })
  },

  retryPay: function() {
    this.setData({ showResult: false })
    this.refresh()
  }
})
