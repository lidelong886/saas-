// 骑手相关API
const request = require('../utils/request')

// 获取附近站点（骑手模式）
const getNearbyStations = (lat, lng, radius = 5, limit = 3) => {
  return request.get('/rider/nearby-stations', {
    latitude: lat,
    longitude: lng,
    radius,
    limit
  })
}

// 快速换电（骑手套餐自动判断）
const quickSwap = (code) => {
  return request.post('/exchange/quick-swap', { code })
}

// 更新用户偏好设置
const updateUserPreferences = (preferences) => {
  return request.put('/user/preferences', preferences)
}

// 获取用户偏好设置
const getUserPreferences = () => {
  return request.get('/user/preferences', {}, { silent: true })
}

module.exports = {
  getNearbyStations,
  quickSwap,
  updateUserPreferences,
  getUserPreferences
}
