// pages/profile/tenant.js
const { submitTenantApplication } = require('../../api/tenant')

Page({
  data: {
    formData: {
      name: '',
      contactName: '',
      phone: '',
      city: '',
      message: ''
    },
    fundOptions: ['10万以下', '10-50万', '50-100万', '100万以上'],
    fundIndex: -1,
    loading: false,
    submitted: false
  },

  onLoad() {
    this.checkLoginStatus()
  },

  checkLoginStatus() {
    const token = wx.getStorageSync('token')
    if (!token) {
      wx.showModal({
        title: '提示',
        content: '请先登录后再申请',
        confirmText: '去登录',
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

  onFundChange(e) {
    this.setData({
      fundIndex: e.detail.value
    })
  },

  onSubmit(e) {
    const data = e.detail.value
    const { name, contactName, phone, city, message } = data
    const fundLevel = this.data.fundIndex === -1 ? '' : this.data.fundOptions[this.data.fundIndex]

    if (!name) return wx.showToast({ title: '请输入公司/个人名称', icon: 'none' })
    if (!contactName) return wx.showToast({ title: '请输入联系人姓名', icon: 'none' })
    if (!phone || phone.length !== 11) return wx.showToast({ title: '请输入正确的手机号', icon: 'none' })
    if (!city) return wx.showToast({ title: '请输入意向城市', icon: 'none' })
    if (!fundLevel) return wx.showToast({ title: '请选择预计投入资金', icon: 'none' })

    this.setData({ loading: true })

    wx.showLoading({ title: '提交中...' })

    submitTenantApplication({
      name,
      contact_name: contactName,
      contact_phone: phone,
      city,
      fund_level: fundLevel,
      message
    }).then(() => {
      wx.hideLoading()
      this.setData({
        loading: false,
        submitted: true
      })
      wx.showToast({ title: '申请已提交', icon: 'success' })
    }).catch(() => {
      wx.hideLoading()
      this.setData({ loading: false })
    })
  },

  goBack() {
    wx.navigateBack()
  }
})
