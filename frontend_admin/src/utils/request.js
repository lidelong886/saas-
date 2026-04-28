import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import store from '@/store'
import { getToken } from '@/utils/auth'

// 创建axios实例
const service = axios.create({
  baseURL: process.env.VUE_APP_BASE_API || '/api/v1', // API的基础URL
  timeout: 30000, // 请求超时时间
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    // 添加认证token
    const token = getToken()
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    // 租户ID由后端从JWT claims中读取，前端不再手动设置
    // （保留 X-Tenant-ID 仅用于非JWT认证的公开接口，由后端 before_request 决定是否采纳）
    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// 防止 401 弹窗重复触发
let _isHandlingAuth = false

// 触发统一登录失效处理的内部函数
function handleAuthExpiry() {
  if (_isHandlingAuth) return
  _isHandlingAuth = true
  ElMessageBox.confirm('登录已过期，请重新登录', '提示', {
    confirmButtonText: '重新登录',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    store.dispatch('user/logout').then(() => { location.reload() })
  }).catch(() => {
    store.dispatch('user/fedLogout').then(() => { location.reload() })
  }).finally(() => { _isHandlingAuth = false })
}

// 响应拦截器 - 成功路径
service.interceptors.response.use(
  response => {
    const res = response.data
    if (res.code === 200 || res.code === 0) {
      return res
    }
    // 业务层 401：直接拒绝，不弹窗（HTTP层统一处理）
    if (res.code === 401) {
      return Promise.reject(new Error(res.message || '登录已过期'))
    }
    // 403 权限不足
    if (res.code === 403) {
      ElMessage({ message: res.message || '权限不足', type: 'warning', duration: 3000 })
      return Promise.reject(new Error(res.message || '权限不足'))
    }
    // 其他业务错误
    ElMessage({ message: res.message || '请求失败', type: 'error', duration: 5000 })
    return Promise.reject(new Error(res.message || '请求失败'))
  },

  // 响应拦截器 - 错误路径
  error => {
    console.error('Response error:', error)
    const { response } = error

    if (response) {
      const { status, data } = response

      if (status === 401) {
        // 统一处理，两处 401 只弹一次
        handleAuthExpiry()
        return Promise.reject(error)
      }

      if (status === 422) {
        // JWT 验证失败：取消不跳转
        ElMessageBox.confirm('登录已过期，请重新登录', '提示', {
          confirmButtonText: '重新登录',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          store.dispatch('user/fedLogout').then(() => { window.location.href = '/login' })
        }).catch(() => {
          // 取消操作：留在当前页，不跳转
        })
        return Promise.reject(error)
      }

      if (status === 403) {
        ElMessage({ message: data?.message || '权限不足', type: 'warning', duration: 3000 })
        return Promise.reject(error)
      }
      if (status === 404) {
        ElMessage({ message: data?.message || '资源不存在', type: 'warning', duration: 3000 })
        return Promise.reject(error)
      }
      if (status === 500) {
        ElMessage({ message: data?.message || '服务器内部错误', type: 'error', duration: 5000 })
        return Promise.reject(error)
      }
      ElMessage({ message: data?.message || `请求失败 (${status})`, type: 'error', duration: 5000 })
      return Promise.reject(error)
    }

    // 网络层错误
    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      ElMessage({ message: '请求超时，请检查网络连接', type: 'error', duration: 5000 })
    } else {
      ElMessage({ message: '网络错误，请检查网络连接', type: 'error', duration: 5000 })
    }
    return Promise.reject(error)
  }
)

export default service
