const request = require('../utils/request')

const getPaymentRecords = (params) => {
  return request.get('/payment/records', params)
}

const refundOrder = (orderNo) => {
  return request.post(`/order/${orderNo}/refund`)
}

module.exports = {
  getPaymentRecords,
  refundOrder
}
