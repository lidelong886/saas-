// 站点相关API
const request = require('../utils/request')

// ???????????????????
const getStations = (params = {}) => {
  return request.get('/station/public-list', params)
}

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

