// 电池相关API
const request = require('../utils/request')

// 获取电池列表
const getBatteries = (params) => {
  // 小程序端展示可用电池：后端提供 /battery/available
  return request.get('/battery/available', params)
}

// 获取电池详情
const getBatteryDetail = (batteryId) => {
  return request.get(`/battery/${batteryId}`)
}

// 扫描电池二维码
const scanBattery = (batteryCode) => {
  return request.get(`/battery/scan/${encodeURIComponent(batteryCode)}`)
}

const getCurrentPackage = () => {
  return request.get('/user/stats', {}, { silent: true }).then(res => {
    const stats = res.data || {}
    return stats.currentPackage || null
  }).catch(() => null)
}

// 租用电池
const rentBattery = async (data) => {
  const batteryId = data.battery_id
  const currentPackage = await getCurrentPackage()
  const payload = {
    ...data,
    hours: currentPackage ? 1 : 24
  }
  return request.post(`/battery/${batteryId}/rent`, payload)
}

// 归还电池
const returnBattery = (data) => {
  const batteryId = data.battery_id
  return request.post(`/battery/${batteryId}/return`, data)
}

module.exports = {
  getBatteries,
  getBatteryDetail,
  scanBattery,
  rentBattery,
  returnBattery
}

