const DEFAULT_TENANT_NAME = 'PowerNest 官方演示租户'

function getTenantDisplayName(tenant) {
  if (!tenant) return DEFAULT_TENANT_NAME
  return tenant.brand_name || tenant.name || DEFAULT_TENANT_NAME
}

function getSelectedTenantId(defaultId) {
  const stored = wx.getStorageSync('selectedTenantId')
  return Number(stored) || defaultId || 1
}

function getCurrentTenantName(defaultName) {
  const tenant = wx.getStorageSync('selectedTenant')
  return getTenantDisplayName(tenant) || defaultName || DEFAULT_TENANT_NAME
}

function saveSelectedTenant(tenant) {
  if (!tenant) return
  wx.setStorageSync('selectedTenantId', tenant.id)
  wx.setStorageSync('selectedTenant', tenant)
  const app = getApp()
  if (app && app.globalData) {
    app.globalData.tenantId = tenant.id
    app.globalData.tenantName = getTenantDisplayName(tenant)
  }
}

module.exports = {
  DEFAULT_TENANT_NAME,
  getTenantDisplayName,
  getSelectedTenantId,
  getCurrentTenantName,
  saveSelectedTenant
}
