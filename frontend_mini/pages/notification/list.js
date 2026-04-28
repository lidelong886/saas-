// pages/notification/list.js
const { getNotifications, getUnreadCount, markAsRead, markAllAsRead } = require('../../api/notification')

Page({
  data: {
    notifications: [],
    page: 1,
    hasMore: true,
    isLoading: false,
    unreadCount: 0,
    typeIcons: {
      order: '/images/icon-order-noti.png',
      exchange: '/images/icon-exchange-noti.png',
      system: '/images/icon-system-noti.png',
      fault: '/images/icon-fault-noti.png'
    },
    typeLabels: {
      order: '订单通知',
      exchange: '换电通知',
      system: '系统公告',
      fault: '报修反馈'
    }
  },

  onLoad() {
    this.loadNotifications(true)
  },

  onShow() {
    this.loadUnreadCount()
  },

  loadNotifications(isRefresh) {
    if (this.data.isLoading) return

    if (isRefresh) {
      this.setData({ page: 1, hasMore: true, notifications: [] })
    }

    this.setData({ isLoading: true })

    getNotifications({
      page: this.data.page,
      per_page: 20
    }).then(res => {
      const list = res.data.list || res.data.items || []
      const notifications = isRefresh ? list : [...this.data.notifications, ...list]
      const pagination = res.data.pagination || {}

      this.setData({
        notifications,
        page: this.data.page + 1,
        hasMore: pagination.page < pagination.pages,
        isLoading: false
      })
    }).catch(() => {
      wx.showToast({ title: '加载失败', icon: 'none' })
      this.setData({ isLoading: false })
    })
  },

  loadUnreadCount() {
    getUnreadCount().then(res => {
      this.setData({ unreadCount: (res.data || {}).count || 0 })
    }).catch(() => {})
  },

  onNotificationTap(e) {
    const item = e.currentTarget.dataset.item

    // 标记已读
    if (!item.is_read) {
      markAsRead(item.id).then(() => {
        const notifications = this.data.notifications.map(n =>
          n.id === item.id ? { ...n, is_read: true } : n
        )
        this.setData({
          notifications,
          unreadCount: Math.max(0, this.data.unreadCount - 1)
        })
      }).catch(() => {})
    }

    // 跳转到关联页面
    if (item.link_type === 'order' && item.link_id) {
      wx.navigateTo({ url: `/pages/order/detail?order_no=${item.link_id}` })
    } else if (item.link_type === 'exchange' && item.link_id) {
      wx.navigateTo({ url: '/pages/exchange/history' })
    } else if (item.link_type === 'fault' && item.link_id) {
      wx.navigateTo({ url: '/pages/fault/list' })
    }
  },

  onMarkAllRead() {
    if (this.data.unreadCount === 0) return

    markAllAsRead().then(() => {
      const notifications = this.data.notifications.map(n => ({ ...n, is_read: true }))
      this.setData({ notifications, unreadCount: 0 })
      wx.showToast({ title: '已全部标记已读', icon: 'success' })
    }).catch(() => {
      wx.showToast({ title: '操作失败', icon: 'none' })
    })
  },

  onPullDownRefresh() {
    this.loadNotifications(true)
    this.loadUnreadCount()
    wx.stopPullDownRefresh()
  },

  onReachBottom() {
    if (this.data.hasMore && !this.data.isLoading) {
      this.loadNotifications(false)
    }
  }
})
