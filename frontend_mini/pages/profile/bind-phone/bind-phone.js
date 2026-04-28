// pages/profile/bind-phone.js
const request = require('../../../utils/request')

Page({
  data: {
    phone: '',
    code: '',
    countdown: 0,
    canSendCode: true
  },

  onPhoneInput: function(e) {
    this.setData({ phone: e.detail.value })
  },

  onCodeInput: function(e) {
    this.setData({ code: e.detail.value })
  },

  onSendCode: function() {
    const { phone, canSendCode } = this.data

    if (!canSendCode) return

    if (!phone) {
      wx.showToast({ title: '请输入手机号', icon: 'none' })
      return
    }

    if (!/^1[3-9]\d{9}$/.test(phone)) {
      wx.showToast({ title: '手机号格式不正确', icon: 'none' })
      return
    }

    wx.showLoading({ title: '发送中...' })

    request.post('/auth/send-code', { phone }).then(res => {
      wx.hideLoading()
      wx.showToast({ title: '验证码已发送', icon: 'success' })
      this.startCountdown()
    }).catch(err => {
      wx.hideLoading()
      const msg = (err && (err.message || err.msg)) || '发送失败'
      wx.showToast({ title: msg, icon: 'none' })
    })
  },

  startCountdown: function() {
    this.setData({ countdown: 60, canSendCode: false })
    const timer = setInterval(() => {
      const countdown = this.data.countdown - 1
      if (countdown <= 0) {
        clearInterval(timer)
        this.setData({ countdown: 0, canSendCode: true })
      } else {
        this.setData({ countdown })
      }
    }, 1000)
  },

  onSubmit: function() {
    const { phone, code } = this.data

    if (!phone) {
      wx.showToast({ title: '请输入手机号', icon: 'none' })
      return
    }

    if (!/^1[3-9]\d{9}$/.test(phone)) {
      wx.showToast({ title: '手机号格式不正确', icon: 'none' })
      return
    }

    if (!code) {
      wx.showToast({ title: '请输入验证码', icon: 'none' })
      return
    }

    wx.showLoading({ title: '绑定中...' })

    request.post('/user/bind-phone', {
      phone,
      code
    }).then(res => {
      wx.hideLoading()
      wx.showToast({ title: '绑定成功', icon: 'success' })
      setTimeout(() => {
        wx.navigateBack()
      }, 1500)
    }).catch(err => {
      wx.hideLoading()
      const msg = (err && (err.message || err.msg)) || '绑定失败'
      wx.showToast({ title: msg, icon: 'none' })
    })
  }
})
