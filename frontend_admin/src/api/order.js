import request from '@/utils/request'

// 获取订单列表
export function getOrderList(params) {
  return request({
    url: '/admin/orders',
    method: 'get',
    params
  })
}

// 获取订单详情
export function getOrderDetail(id) {
  return request({
    url: `/admin/orders/${id}`,
    method: 'get'
  })
}

// 更新订单状态
export function updateOrderStatus(id, status) {
  return request({
    url: `/admin/orders/${id}/status`,
    method: 'put',
    data: { status }
  })
}

// 取消订单
export function cancelOrder(id, reason) {
  return request({
    url: `/admin/orders/${id}/cancel`,
    method: 'post',
    data: { reason }
  })
}

// 退款订单
export function refundOrder(id, reason) {
  return request({
    url: `/admin/orders/${id}/refund`,
    method: 'post',
    data: { reason }
  })
}
