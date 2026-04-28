import request from '@/utils/request'

// 用户登录
export function login(data) {
  return request({
    url: '/admin-auth/login',
    method: 'post',
    data: {
      username: data.username,
      password: data.password
    }
  })
}

// 用户登出
export function logout() {
  return request({
    url: '/admin-auth/logout',
    method: 'post'
  })
}

// 获取用户信息
export function getUserInfo() {
  return request({
    url: '/admin-auth/me',
    method: 'get'
  })
}

// 刷新token
export function refreshToken() {
  return request({
    url: '/auth/refresh-token',
    method: 'post'
  })
}

// 发送短信验证码
export function sendSmsCode(data) {
  return request({
    url: '/auth/send-sms',
    method: 'post',
    data
  })
}

// 重置密码
export function resetPassword(data) {
  return request({
    url: '/auth/reset-password',
    method: 'post',
    data
  })
}
