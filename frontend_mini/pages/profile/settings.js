const { getUserProfile, updateUserProfile } = require('../../api/user')

Page({
  data: {
    nickname: '',
    loading: false
  },

  onShow() {
    if (!wx.getStorageSync('token')) {
      wx.navigateTo({ url: '/pages/profile/login' })
      return
    }
    getUserProfile()
      .then((res) => {
        const u = res.data || {}
        this.setData({ nickname: u.nickname || '' })
      })
      .catch(() => {})
  },

  goToChangePassword() {
    wx.navigateTo({ url: '/pages/profile/change-password' })
  },

  goToBindPhone() {
    wx.navigateTo({ url: '/pages/profile/bind-phone' })
  },

  onNickInput(e) {
    this.setData({ nickname: e.detail.value })
  },

  onSave() {
    const { nickname } = this.data
    if (!nickname || !nickname.trim()) {
      wx.showToast({ title: '昵称不能为空', icon: 'none' })
      return
    }
    this.setData({ loading: true })
    updateUserProfile({ nickname: nickname.trim() })
      .then(() => {
        wx.showToast({ title: '已保存', icon: 'success' })
        try {
          const prev = wx.getStorageSync('userInfo') || {}
          wx.setStorageSync('userInfo', { ...prev, nickname: nickname.trim() })
        } catch (e) {}
      })
      .finally(() => {
        this.setData({ loading: false })
      })
  }
})
