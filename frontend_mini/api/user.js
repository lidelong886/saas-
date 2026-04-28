// 用户相关API
const request = require('../utils/request')

const getUserProfile = () => {
  return request.get('/user/profile')
}

const updateUserProfile = (data) => {
  return request.put('/user/profile', data)
}

const getUserStats = () => {
  return request.get('/user/stats')
}

const getUserBalance = () => {
  return request.get('/user/balance')
}

const recharge = (data) => {
  return request.post('/user/recharge', data)
}

const getWalletTransactions = (params) => {
  return request.get('/user/wallet/transactions', params)
}

const submitRealname = (data) => {
  return request.put('/user/profile', data)
}

module.exports = {
  getUserProfile,
  updateUserProfile,
  getUserStats,
  getUserBalance,
  recharge,
  getWalletTransactions,
  submitRealname
}
