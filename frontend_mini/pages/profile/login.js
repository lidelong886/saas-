const { login } = require('../../api/auth')

Page({
  data: {
    username: '',
    password: '',
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

  onUsernameInput(e) {
    this.setData({ username: (e.detail.value || '').trim() })
  },

  onPasswordInput(e) {
    this.setData({ password: e.detail.value || '' })
  },

  async onLoginTap() {
    const { username, password } = this.data
    const account = (username || '').trim()
    if (!account || !password) {
      wx.showToast({ title: '请输入账号和密码', icon: 'none' })
      return
    }

    this.setData({ loading: true })
    try {
      this.useDefaultTenant()
      const res = await login({ username: account, account, password })
      const resData = res.data || {}
      const token = resData.tokens && resData.tokens.access_token
      const userInfo = resData.user

      if (!token) {
        wx.showToast({ title: '登录失败：未返回token', icon: 'none' })
        return
      }

      wx.setStorageSync('token', token)
      if (userInfo) wx.setStorageSync('userInfo', userInfo)

      wx.showToast({ title: '登录成功', icon: 'success' })
      setTimeout(() => {
        wx.navigateBack()
      }, 600)
    } catch (e) {
      const msg = (e && (e.message || e.msg)) || '账号或密码错误'
      wx.showToast({ title: msg, icon: 'none' })
    } finally {
      this.setData({ loading: false })
    }
  },

  goToRegister() {
    wx.navigateTo({
      url: '/pages/profile/register'
    })
  }
})

