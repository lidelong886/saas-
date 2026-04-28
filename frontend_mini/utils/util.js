// 工具函数
const formatTime = date => {
  const year = date.getFullYear()
  const month = date.getMonth() + 1
  const day = date.getDate()
  const hour = date.getHours()
  const minute = date.getMinutes()
  const second = date.getSeconds()

  return `${[year, month, day].map(formatNumber).join('/')} ${[hour, minute, second].map(formatNumber).join(':')}`
}

const formatNumber = n => {
  n = n.toString()
  return n[1] ? n : `0${n}`
}

// 格式化距离
const formatDistance = distance => {
  if (distance < 1000) {
    return `${distance}m`
  } else {
    return `${(distance / 1000).toFixed(1)}km`
  }
}

// 格式化金额
const formatMoney = amount => {
  return `¥${amount.toFixed(2)}`
}

// 格式化时间显示
const formatTimeAgo = timestamp => {
  const now = new Date()
  const time = new Date(timestamp)
  const diff = now - time
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) {
    return '刚刚'
  } else if (minutes < 60) {
    return `${minutes}分钟前`
  } else if (hours < 24) {
    return `${hours}小时前`
  } else if (days < 30) {
    return `${days}天前`
  } else {
    return formatTime(time).split(' ')[0]
  }
}

// 格式化订单状态
const formatOrderStatus = status => {
  const statusMap = {
    pending: '待支付',
    paid: '已支付',
    rented: '租用中',
    returned: '已归还',
    completed: '已完成',
    cancelled: '已取消',
    refunded: '已退款'
  }
  return statusMap[status] || status
}

// 格式化电池状态
const formatBatteryStatus = status => {
  const statusMap = {
    available: '可使用',
    rented: '租用中',
    charging: '充电中',
    maintenance: '维修中',
    scrapped: '已报废'
  }
  return statusMap[status] || status
}

// 格式化站点状态
const formatStationStatus = status => {
  const statusMap = {
    active: '正常运营',
    maintenance: '维护中',
    inactive: '停用'
  }
  return statusMap[status] || status
}

// 获取状态样式类名
const getStatusClass = status => {
  const classMap = {
    available: 'status-available',
    in_use: 'status-in-use',
    charging: 'status-charging',
    maintenance: 'status-maintenance',
    offline: 'status-offline'
  }
  return classMap[status] || 'status-offline'
}

// 验证手机号
const validatePhone = phone => {
  const pattern = /^1[3-9]\d{9}$/
  return pattern.test(phone)
}

// 验证密码强度
const validatePassword = password => {
  if (password.length < 8) {
    return false
  }
  const hasLetter = /[a-zA-Z]/.test(password)
  const hasDigit = /\d/.test(password)
  return hasLetter && hasDigit
}

// 防抖函数
const debounce = (func, delay) => {
  let timeoutId
  return function (...args) {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => func.apply(this, args), delay)
  }
}

// 节流函数
const throttle = (func, limit) => {
  let inThrottle
  return function (...args) {
    if (!inThrottle) {
      func.apply(this, args)
      inThrottle = true
      setTimeout(() => inThrottle = false, limit)
    }
  }
}

// 计算两点间距离
const calculateDistance = (lat1, lng1, lat2, lng2) => {
  const R = 6371 // 地球半径（公里）
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLng = (lng2 - lng1) * Math.PI / 180
  const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLng / 2) * Math.sin(dLng / 2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return R * c * 1000 // 返回米
}

// 复制到剪贴板
const copyToClipboard = text => {
  wx.setClipboardData({
    data: text,
    success: () => {
      wx.showToast({
        title: '复制成功',
        icon: 'success'
      })
    },
    fail: () => {
      wx.showToast({
        title: '复制失败',
        icon: 'none'
      })
    }
  })
}

// 显示加载提示
const showLoading = (title = '加载中...') => {
  wx.showLoading({
    title,
    mask: true
  })
}

// 隐藏加载提示
const hideLoading = () => {
  wx.hideLoading()
}

// 显示成功提示
const showSuccess = (title = '操作成功') => {
  wx.showToast({
    title,
    icon: 'success',
    duration: 2000
  })
}

// 显示错误提示
const showError = (title = '操作失败') => {
  wx.showToast({
    title,
    icon: 'none',
    duration: 2000
  })
}

// 显示确认对话框
const showConfirm = (options) => {
  return new Promise((resolve, reject) => {
    wx.showModal({
      title: options.title || '提示',
      content: options.content || '',
      showCancel: true,
      cancelText: options.cancelText || '取消',
      confirmText: options.confirmText || '确定',
      success: (res) => {
        if (res.confirm) {
          resolve()
        } else {
          reject()
        }
      },
      fail: reject
    })
  })
}

// 获取当前位置
const getCurrentLocation = () => {
  return new Promise((resolve, reject) => {
    wx.getLocation({
      type: 'gcj02',
      success: resolve,
      fail: reject
    })
  })
}

// 选择位置
const chooseLocation = () => {
  return new Promise((resolve, reject) => {
    wx.chooseLocation({
      success: resolve,
      fail: reject
    })
  })
}

// 扫码
const scanCode = () => {
  return new Promise((resolve, reject) => {
    wx.scanCode({
      success: resolve,
      fail: reject
    })
  })
}

// 拨打电话
const makePhoneCall = phoneNumber => {
  wx.makePhoneCall({
    phoneNumber
  })
}

// 预览图片
const previewImage = (urls, current = 0) => {
  wx.previewImage({
    urls,
    current: urls[current] || urls[0]
  })
}

// 分享功能
const shareApp = (options = {}) => {
  return {
    title: options.title || '电池租售一体化平台',
    path: options.path || '/pages/index/index',
    imageUrl: options.imageUrl || ''
  }
}

module.exports = {
  formatTime,
  formatNumber,
  formatDistance,
  formatMoney,
  formatTimeAgo,
  formatOrderStatus,
  formatBatteryStatus,
  formatStationStatus,
  getStatusClass,
  validatePhone,
  validatePassword,
  debounce,
  throttle,
  calculateDistance,
  copyToClipboard,
  showLoading,
  hideLoading,
  showSuccess,
  showError,
  showConfirm,
  getCurrentLocation,
  chooseLocation,
  scanCode,
  makePhoneCall,
  previewImage,
  shareApp
}