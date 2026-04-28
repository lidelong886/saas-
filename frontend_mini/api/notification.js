// 消息通知相关API
const request = require('../utils/request')

// 获取通知列表
const getNotifications = (params) => {
  return request.get('/notification/list', params)
}

// 获取未读通知数
const getUnreadCount = () => {
  return request.get('/notification/unread-count')
}

// 标记单条已读
const markAsRead = (id) => {
  return request.put(`/notification/${id}/read`)
}

// 全部标记已读
const markAllAsRead = () => {
  return request.put('/notification/read-all')
}

module.exports = {
  getNotifications,
  getUnreadCount,
  markAsRead,
  markAllAsRead
}
