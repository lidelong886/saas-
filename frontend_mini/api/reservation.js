const request = require('../utils/request')

// 创建预约
const createReservation = (data) => {
  return request.post('/rider/reservations', data)
}

// 取消预约
const cancelReservation = (id) => {
  return request.delete(`/rider/reservations/${id}`)
}

// 获取预约列表
const getReservations = (status) => {
  return request.get('/rider/reservations', { status })
}

// 获取预约详情
const getReservationDetail = (id) => {
  return request.get(`/rider/reservations/${id}`)
}

// 获取附近站点
const getNearbyStations = (params) => {
  return request.get('/rider/nearby-stations', params)
}

module.exports = {
  createReservation,
  cancelReservation,
  getReservations,
  getReservationDetail,
  getNearbyStations
}
