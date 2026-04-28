import request from '@/utils/request'

// 获取站点列表
export function getStationList(params) {
  return request({
    url: '/admin/stations',
    method: 'get',
    params
  })
}

// 获取站点详情
export function getStationDetail(id) {
  return request({
    url: `/admin/stations/${id}`,
    method: 'get'
  })
}

// 创建站点
export function createStation(data) {
  return request({
    url: '/admin/stations',
    method: 'post',
    data
  })
}

// 更新站点
export function updateStation(id, data) {
  return request({
    url: `/admin/stations/${id}`,
    method: 'put',
    data
  })
}

// 删除站点
export function deleteStation(id) {
  return request({
    url: `/admin/stations/${id}`,
    method: 'delete'
  })
}

// 获取站点统计（已迁移至 dashboard.js，此处保留向后兼容）
export { getStationStats } from './dashboard.js'

// 地址解析为经纬度（高德）
export function geocodeAddress(params) {
  return request({
    url: '/admin/map/geocode',
    method: 'get',
    params
  })
}
