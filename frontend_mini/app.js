//app.js
const config = require('./config')
const { DEFAULT_TENANT_NAME, getCurrentTenantName } = require('./utils/tenant')

App({
  onLaunch: function () {
    var logs = wx.getStorageSync('logs') || []
    logs.unshift(Date.now())
    wx.setStorageSync('logs', logs)

    wx.login({
      success: res => {
        this.globalData.code = res.code
      }
    })

    const selectedTenantId = wx.getStorageSync('selectedTenantId')
    if (selectedTenantId) {
      this.globalData.tenantId = Number(selectedTenantId) || config.tenantId
    }
    this.globalData.tenantName = getCurrentTenantName(DEFAULT_TENANT_NAME)
  },

  // 步骤7：记录每次打开时间，供低电量提醒频率控制使用
  onShow: function () {
    this.globalData.lastShowTimestamp = Date.now()
  },

  globalData: {
    userInfo: null,
    token: null,
    code: null,
    baseUrl: config.apiBase,
    tenantId: config.tenantId,
    tenantName: DEFAULT_TENANT_NAME,
    lastShowTimestamp: 0
  }
})
