const request = require('../utils/request')

/**
 * 获取商城电池列表
 */
function getStoreBatteries(params) {
  return request.get('/store/list', params)
}

/**
 * 购买电池
 */
function purchaseBattery(batteryId) {
  return request.post(`/store/purchase/${batteryId}`)
}

module.exports = {
  getStoreBatteries,
  purchaseBattery
}
