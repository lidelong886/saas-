// 订单相关API
const request = require('../utils/request')

// 获取订单列表
const getOrders = (params) => {
  return request.get('/order/my-orders', params)
}

// 获取订单详情
const getOrderDetail = (orderNo) => {
  return request.get(`/order/${orderNo}`)
}

// 创建订单
const createOrder = (data) => {
  return request.post('/order/create', data)
}

// 取消订单
const cancelOrder = (orderNo) => {
  return request.post(`/order/${orderNo}/cancel`, {
    reason: '用户在小程序端取消订单'
  })
}

// 支付订单
const payOrder = (orderNo, data) => {
  return request.post(`/payment/pay/${orderNo}`, data)
}

// 完成/评价/统计：后端暂未提供对应接口

module.exports = {
  getOrders,
  getOrderDetail,
  createOrder,
  cancelOrder,
  payOrder
}
