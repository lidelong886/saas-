import request from '@/utils/request'

// 获取电池列表
export function getBatteryList(params) {
  return request({
    url: '/admin/batteries',
    method: 'get',
    params
  })
}

// 获取电池详情
export function getBatteryDetail(id) {
  return request({
    url: `/admin/batteries/${id}`,
    method: 'get'
  })
}

// 创建电池
export function createBattery(data) {
  return request({
    url: '/admin/batteries',
    method: 'post',
    data
  })
}

// 更新电池
export function updateBattery(id, data) {
  return request({
    url: `/admin/batteries/${id}`,
    method: 'put',
    data
  })
}

// 删除电池
export function deleteBattery(id) {
  return request({
    url: `/admin/batteries/${id}`,
    method: 'delete'
  })
}

// 获取电池统计（已迁移至 dashboard.js，此处保留向后兼容）
export { getBatteryStats } from './dashboard.js'
