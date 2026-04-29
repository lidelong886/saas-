import request from '@/utils/request'

export function getTenantList() {
  return request({
    url: '/admin/rbac/tenants',
    method: 'get'
  })
}

export function createTenant(data) {
  return request({
    url: '/admin/rbac/tenants',
    method: 'post',
    data
  })
}

export function updateTenant(id, data) {
  return request({
    url: `/admin/rbac/tenants/${id}`,
    method: 'put',
    data
  })
}

export function deleteTenant(id) {
  return request({
    url: `/admin/rbac/tenants/${id}`,
    method: 'delete'
  })
}

export function getTenantApplications(params) {
  return request({
    url: '/admin/rbac/tenant-applications',
    method: 'get',
    params
  })
}

export function reviewTenantApplication(id, data) {
  return request({
    url: `/admin/rbac/tenant-applications/${id}/review`,
    method: 'post',
    data
  })
}

export function getOperationLogs(params) {
  return request({
    url: '/admin/logs',
    method: 'get',
    params
  })
}

// 系统设置
export function getSettings() {
  return request({
    url: '/admin/settings',
    method: 'get'
  })
}

export function updateSettings(data) {
  return request({
    url: '/admin/settings',
    method: 'put',
    data
  })
}
