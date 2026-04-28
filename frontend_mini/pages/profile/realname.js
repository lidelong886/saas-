const { getUserProfile, submitRealname } = require('../../api/user')

Page({
  data: {
    realName: '',
    idCardNo: '',
    realnameStatus: 'unverified',
    loading: false,
    submitting: false
  },

  onShow() {
    if (!wx.getStorageSync('token')) {
      wx.navigateTo({ url: '/pages/profile/login' })
      return
    }
    this.loadProfile()
  },

  loadProfile() {
    this.setData({ loading: true })
    getUserProfile()
      .then((res) => {
        const user = res.data || {}
        this.setData({
          realName: user.real_name || '',
          idCardNo: user.id_card_no || '',
          realnameStatus: user.realname_status || 'unverified',
          loading: false
        })
      })
      .catch(() => {
        this.setData({ loading: false })
      })
  },

  onRealNameInput(e) {
    this.setData({ realName: (e.detail.value || '').trim() })
  },

  onIdCardInput(e) {
    this.setData({ idCardNo: (e.detail.value || '').trim().toUpperCase() })
  },

  validateForm() {
    const { realName, idCardNo } = this.data
    if (!realName) {
      wx.showToast({ title: '请输入真实姓名', icon: 'none' })
      return false
    }
    if (!/^[\u4e00-\u9fa5a-zA-Z·\s]{2,30}$/.test(realName)) {
      wx.showToast({ title: '姓名格式不正确', icon: 'none' })
      return false
    }
    if (!/^(\d{15}|\d{17}[\dX])$/.test(idCardNo)) {
      wx.showToast({ title: '身份证号格式不正确', icon: 'none' })
      return false
    }
    return true
  },

  onSubmit() {
    if (!this.validateForm()) return

    const { realName, idCardNo } = this.data
    this.setData({ submitting: true })
    submitRealname({
      real_name: realName,
      id_card_no: idCardNo
    }).then((res) => {
      const user = res.data || {}
      try {
        const prev = wx.getStorageSync('userInfo') || {}
        wx.setStorageSync('userInfo', {
          ...prev,
          real_name: user.real_name,
          id_card_no: user.id_card_no,
          realname_status: user.realname_status,
          is_verified: user.is_verified
        })
      } catch (e) {}
      this.setData({
        realnameStatus: user.realname_status || 'verified'
      })
      wx.showToast({ title: '认证成功', icon: 'success' })
    }).catch((err) => {
      const msg = err && err.message
      wx.showToast({ title: msg || '认证失败', icon: 'none' })
    }).finally(() => {
      this.setData({ submitting: false })
    })
  },

  getStatusText(status) {
    const map = {
      unverified: '未认证',
      verified: '已认证',
      pending: '审核中',
      rejected: '已拒绝'
    }
    return map[status] || '未认证'
  }
})
