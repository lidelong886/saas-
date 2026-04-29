const { register } = require('../../api/auth')

Page({
  data: {
    phone: '',
    username: '',
    password: '',
    confirmPassword: '',
    loading: false
  },

  onLoad() {
    this.useDefaultTenant()
  },

  useDefaultTenant() {
    const app = getApp()
    if (app && app.globalData) {
      app.globalData.tenantId = 1
    }
    wx.setStorageSync('selectedTenantId', 1)
  },

  onPhoneInput(e) {
    this.setData({ phone: e.detail.value || '' })
  },

  onUsernameInput(e) {
    this.setData({ username: (e.detail.value || '').trim() })
  },

  onPasswordInput(e) {
    this.setData({ password: e.detail.value || '' })
  },

  onConfirmPasswordInput(e) {
    this.setData({ confirmPassword: e.detail.value || '' })
  },

  async onRegisterTap() {
    const { phone, username, password, confirmPassword } = this.data

    if (!phone || phone.length !== 11) {
      wx.showToast({ title: '请输入正确的11位手机号', icon: 'none' })
      return
    }

    if (!username) {
      wx.showToast({ title: '请输入用户名', icon: 'none' })
      return
    }

    if (!password) {
      wx.showToast({ title: '请输入密码', icon: 'none' })
      return
    }

    if (!/^(?=.*[A-Za-z])(?=.*\d).{8,}$/.test(password)) {
      wx.showToast({ title: '密码至少8位且包含字母和数字', icon: 'none' })
      return
    }

    if (password !== confirmPassword) {
      wx.showToast({ title: '两次输入的密码不一致', icon: 'none' })
      return
    }

    this.setData({ loading: true })
    try {
      this.useDefaultTenant()
      const res = await register({ 
        username, 
        password,
        phone 
      })
      
      const resData = res.data || {}
      const token = resData.tokens && resData.tokens.access_token
      const userInfo = resData.user

      if (token) {
        wx.setStorageSync('token', token)
        if (userInfo) wx.setStorageSync('userInfo', userInfo)
      }

      wx.showToast({ title: '注册成功', icon: 'success' })
      setTimeout(() => {
        // 如果是从其他页面来的，返回上一页；否则去首页
        if (getCurrentPages().length > 1) {
          // 由于可能是从登录页跳过来的，我们想直接回到最初的页面
          wx.navigateBack({ delta: 2 }).catch(() => {
            wx.navigateBack()
          })
        } else {
          wx.switchTab({ url: '/pages/index/index' })
        }
      }, 1000)
    } catch (e) {
      const msg = (e && (e.message || e.msg)) || '注册失败'
      wx.showToast({ title: msg, icon: 'none' })
    } finally {
      this.setData({ loading: false })
    }
  },

  goToLogin() {
    wx.navigateBack()
  }
})
