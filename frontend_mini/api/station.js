// 站点相关API
const request = require('../utils/request')

// 获取站点列表 (小程序端默认获取附近的所有可用站点，后端 /station/list 是 admin 专属)
const getStations = (params) => {
  // 如果没有传经纬度，默认使用北京天安门作为兜底，防止后端报 400 错误
  const requestParams = {
    latitude: 39.9042,
    longitude: 116.4074,
    radius: 50,
    ...params
  }
  return request.get('/station/nearby', requestParams)
}

// 获取站点详情
const getStationDetail = (stationId) => {
  return request.get(`/station/${stationId}`)
}

// 获取附近站点
const getNearbyStations = (params) => {
  return request.get('/station/nearby', params)
}

// 获取站点电池列表
const getStationBatteries = (stationId, params) => {
  return request.get('/battery/available', {
    station_id: stationId,
    ...params
  })
}

// 获取站点柜子列表
const getStationCabinets = (stationId, params) => {
  return request.get(`/station/${stationId}/cabinets`, params)
}

// 获取柜子详情
const getCabinetDetail = (cabinetId) => {
  return request.get(`/station/cabinet/${cabinetId}`)
}

module.exports = {
  getStations,
  getStationDetail,
  getNearbyStations,
  getStationBatteries,
  getStationCabinets,
  getCabinetDetail
}

