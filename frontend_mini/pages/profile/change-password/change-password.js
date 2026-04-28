// pages/profile/change-password.js
const request = require('../../../utils/request')

Page({
  data: {
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
  },

  onOldPasswordInput: function(e) {
    this.setData({ oldPassword: e.detail.value })
  },

  onNewPasswordInput: function(e) {
    this.setData({ newPassword: e.detail.value })
  },

  onConfirmPasswordInput: function(e) {
    this.setData({ confirmPassword: e.detail.value })
  },

  onSubmit: function() {
    const { oldPassword, newPassword, confirmPassword } = this.data

    if (!oldPassword) {
      wx.showToast({ title: '请输入原密码', icon: 'none' })
      return
    }

    if (!newPassword) {
      wx.showToast({ title: '请输入新密码', icon: 'none' })
      return
    }

    if (!/^(?=.*[A-Za-z])(?=.*\d).{8,}$/.test(newPassword)) {
      wx.showToast({ title: '密码至少8位且包含字母和数字', icon: 'none' })
      return
    }

    if (newPassword !== confirmPassword) {
      wx.showToast({ title: '两次密码不一致', icon: 'none' })
      return
    }

    if (oldPassword === newPassword) {
      wx.showToast({ title: '新密码不能与原密码相同', icon: 'none' })
      return
    }

    wx.showLoading({ title: '修改中...' })

    request.post('/user/change-password', {
      old_password: oldPassword,
      new_password: newPassword
    }).then(res => {
      wx.hideLoading()
      wx.showToast({ title: '修改成功', icon: 'success' })
      setTimeout(() => {
        wx.navigateBack()
      }, 1500)
    }).catch(err => {
      wx.hideLoading()
      const msg = (err && (err.message || err.msg)) || '修改失败'
      wx.showToast({ title: msg, icon: 'none' })
    })
  }
})
