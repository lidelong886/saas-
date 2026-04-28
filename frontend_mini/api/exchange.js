const request = require('../utils/request')

const getExchangeHistory = (params) => {
  return request.get('/exchange/history', params)
}

const exchangeBattery = (data) => {
  return request.post('/exchange/do', data)
}

module.exports = {
  getExchangeHistory,
  exchangeBattery
}
