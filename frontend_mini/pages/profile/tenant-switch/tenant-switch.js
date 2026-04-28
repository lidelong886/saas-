const { getTenantList } = require('../../../api/tenant')
const { getTenantDisplayName, saveSelectedTenant, getSelectedTenantId } = require('../../../utils/tenant')

Page({
  data: {
    tenants: [],
    currentTenantId: 1
  },

  onLoad() {
    this.setData({ currentTenantId: getSelectedTenantId(1) })
    this.loadTenants()
  },

  loadTenants() {
    getTenantList().then(res => {
      const tenants = (res.data || []).map(item => ({
        ...item,
        displayName: getTenantDisplayName(item)
      }))
      this.setData({ tenants })
    }).catch(() => {
      wx.showToast({ title: '加载运营商失败', icon: 'none' })
    })
  },

  onTenantSwitch(e) {
    const tenantId = Number(e.currentTarget.dataset.id)
    const tenant = this.data.tenants.find(item => item.id === tenantId)
    if (!tenant) return

    saveSelectedTenant(tenant)
    this.setData({ currentTenantId: tenantId })
    wx.setStorageSync('index_needs_refresh', true)
    wx.setStorageSync('profile_needs_refresh', true)
    wx.showToast({ title: `已切换到${tenant.displayName}`, icon: 'none' })

    setTimeout(() => wx.navigateBack(), 600)
  }
})
