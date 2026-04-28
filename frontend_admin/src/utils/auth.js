import Cookies from 'js-cookie'

const TokenKey = 'Admin-Token'

export function getToken() {
  return Cookies.get(TokenKey)
}

export function setToken(token) {
  return Cookies.set(TokenKey, token, { expires: 7 }) // 7天过期
}

export function removeToken() {
  return Cookies.remove(TokenKey)
}

// 检查是否有权限
export function hasPermission(permission) {
  const permissions = JSON.parse(localStorage.getItem('permissions') || '[]')
  return permissions.includes(permission)
}

// 检查是否有角色
export function hasRole(role) {
  const roles = JSON.parse(localStorage.getItem('roles') || '[]')
  return roles.includes(role)
}

// 检查是否是管理员
export function isAdmin() {
  return hasRole('admin') || hasRole('super_admin')
}

// 检查是否登录
export function isLoggedIn() {
  return !!getToken()
}
