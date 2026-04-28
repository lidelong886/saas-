// 认证相关API
const request = require('../utils/request')

// 用户注册
const register = (data) => {
  return request.post('/auth/register', data)
}

// 用户登录
const login = (data) => {
  return request.post('/auth/login', data)
}

// 发送短信验证码
const sendSms = (data) => {
  return request.post('/auth/send-sms', data)
}

// 刷新token
const refreshToken = () => {
  return request.post('/auth/refresh-token')
}

// 用户登出
const logout = () => {
  return request.post('/auth/logout')
}

// 用户重置密码
const resetPassword = (data) => {
  return request.post('/auth/reset-password', data)
}

module.exports = {
  register,
  login,
  sendSms,
  refreshToken,
  logout,
  resetPassword
}

