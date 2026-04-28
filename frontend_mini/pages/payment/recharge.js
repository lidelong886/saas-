const request = require('../../utils/request')

Page({
  data: {
    presetAmounts: [50, 100, 200, 500],
    customAmount: '',
    selectedAmount: 0,
    loading: false
  },

  onLoad() {
    this.checkLogin()
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

  onPresetTap(e) {
    const amount = e.currentTarget.dataset.amount
    this.setData({
      selectedAmount: amount,
      customAmount: ''
    })
  },

  onCustomInput(e) {
    const value = parseFloat(e.detail.value) || 0
    this.setData({
      customAmount: e.detail.value,
      selectedAmount: value
    })
  },

  onRecharge() {
    const { selectedAmount } = this.data

    if (!selectedAmount || selectedAmount <= 0) {
      wx.showToast({ title: '请输入充值金额', icon: 'none' })
      return
    }

    if (selectedAmount < 10) {
      wx.showToast({ title: '最低充值10元', icon: 'none' })
      return
    }

    if (selectedAmount > 10000) {
      wx.showToast({ title: '单次最多充值10000元', icon: 'none' })
      return
    }

    this.setData({ loading: true })

    request.post('/payment/recharge', {
      amount: selectedAmount,
      payment_method: 'wechat'
    })
      .then(res => {
        const paymentData = res.data

        // 毕设演示模式：通过后端演示回调完成充值闭环
        if (paymentData.payment_no) {
          return request.post(`/payment/recharge/${paymentData.payment_no}/complete`)
        }

        // 接入真实商户号后调用微信支付
        return wx.requestPayment({
          timeStamp: paymentData.timeStamp,
          nonceStr: paymentData.nonceStr,
          package: paymentData.package,
          signType: paymentData.signType,
          paySign: paymentData.paySign
        })
      })
      .then(() => {
        wx.showToast({ title: '充值成功', icon: 'success' })
        setTimeout(() => {
          wx.navigateBack()
        }, 1500)
      })
      .catch(err => {
        console.error('充值失败:', err)
        wx.showToast({
          title: err.message || '充值失败',
          icon: 'none'
        })
      })
      .finally(() => {
        this.setData({ loading: false })
      })
  }
})
