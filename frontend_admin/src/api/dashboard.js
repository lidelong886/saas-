import request from '@/utils/request'

// 获取仪表板统计数据
export function getDashboardStats() {
  return request({
    url: '/statistics/dashboard',
    method: 'get'
  })
}

// 获取营收统计
export function getRevenueStats(params) {
  return request({
    url: '/statistics/revenue',
    method: 'get',
    params
  })
}

// 获取订单统计
export function getOrderStats(params) {
  return request({
    url: '/statistics/orders',
    method: 'get',
    params
  })
}

// 获取电池统计
export function getBatteryStats(params) {
  return request({
    url: '/statistics/batteries',
    method: 'get',
    params
  })
}

// 获取站点统计
export function getStationStats(params) {
  return request({
    url: '/statistics/stations',
    method: 'get',
    params
  })
}

// 系统设置（实际定义在 system.js，此处 re-export 保持向后兼容）
export { getSettings, updateSettings } from './system.js'
