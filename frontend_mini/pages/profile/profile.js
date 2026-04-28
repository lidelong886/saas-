// pages/profile/profile.js
const request = require('../../utils/request')
const { showDemoNetworkHelp } = require('../../utils/networkError')
const { getUnreadCount } = require('../../api/notification')
const { getCurrentTenantName } = require('../../utils/tenant')

const PROFILE_REFRESH_FLAG = 'profile_needs_refresh'

Page({
  data: {
    apiBase: '',
    apiBaseShort: '',
    userInfo: null,
    hasLogin: false,
    balance: 0,
    unreadCount: 0,
    tenantInfo: null,
    tenantName: 'PowerNest 官方演示租户',
    stats: {
      rentedBattery: null,
      currentPackage: null
    },
    menuItems: [
      { id: 1, title: '我的余额', path: '/pages/profile/balance', needLogin: true },
      { id: 2, title: '我的订单', path: '/pages/order/list', needLogin: true },
      { id: 3, title: '换电记录', path: '/pages/exchange/history', needLogin: true },
      { id: 4, title: '我的卡券', path: '/pages/profile/cards', needLogin: true },
      { id: 5, title: '我的电池', path: '/pages/battery/list', needLogin: true },
      { id: 6, title: '实名认证', path: '/pages/profile/realname', needLogin: true },
      { id: 7, title: '账户充值', path: '/pages/payment/recharge', needLogin: true },
      { id: 8, title: '支付记录', path: '/pages/payment/records', needLogin: true },
      { id: 9, title: '设置', path: '/pages/profile/settings', needLogin: false },
      { id: 10, title: '联系客服', path: '', needLogin: false },
      { id: 11, title: '帮助中心', path: '', needLogin: false }
    ],
    avatarPlaceholderText: '访'
  },

  onLoad: function() {
    this.checkLoginStatus()
  },

  onShow: function() {
    this.refreshApiBase()
    this.refreshTenantInfo()
    this.checkLoginStatus()
    const shouldRefresh = !!wx.getStorageSync(PROFILE_REFRESH_FLAG)
    if (shouldRefresh) {
      wx.removeStorageSync(PROFILE_REFRESH_FLAG)
    }
    if (this.data.hasLogin) {
      this.loadUserData()
      this.loadUnreadCount()
    }
  },

  refreshApiBase: function() {
    try {
      const appInst = getApp()
      const u = (appInst && appInst.globalData && appInst.globalData.baseUrl) || ''
      const short = u.length > 40 ? u.slice(0, 38) + '…' : u
      this.setData({ apiBase: u, apiBaseShort: short || '未配置' })
    } catch (e) {
      this.setData({ apiBase: '', apiBaseShort: '读取失败' })
    }
  },

  refreshTenantInfo: function() {
    this.setData({ tenantName: getCurrentTenantName() })
  },

  getAvatarPlaceholderText: function(userInfo) {
    const name = (userInfo && userInfo.username) ? String(userInfo.username) : '用户'
    return name.charAt(0)
  },

  onApiHelpTap: function() {
    showDemoNetworkHelp(this.data.apiBase)
  },

  checkLoginStatus: function() {
    const token = wx.getStorageSync('token')
    const userInfo = wx.getStorageSync('userInfo')
    
    this.setData({
      hasLogin: !!token,
      userInfo: userInfo,
      avatarPlaceholderText: token ? this.getAvatarPlaceholderText(userInfo) : '访'
    })
  },

  loadUserData: function() {
    this.loadUserInfo()
    this.loadUserStats()
  },

  loadUserInfo: function() {
    request.get('/user/profile').then(res => {
      const userInfo = res.data || {}
      this.setData({
        userInfo,
        balance: userInfo.balance || 0,
        avatarPlaceholderText: this.getAvatarPlaceholderText(userInfo),
        tenantInfo: userInfo.tenant_info || null
      })
      wx.setStorageSync('userInfo', userInfo)
    }).catch(err => console.error('加载用户信息失败:', err))
  },

  loadUserStats: function() {
    request.get('/user/stats').then(res => {
      const stats = res.data || {}
      this.setData({
        stats: {
          currentPackage: stats.currentPackage || null,
          rentedBattery: stats.rentedBattery || null
        }
      })
    }).catch(err => console.error('加载统计失败:', err))
  },

  goToTenant() {
    wx.navigateTo({ url: "/pages/profile/tenant" })
  },

  goToTenantSwitch() {
    wx.navigateTo({ url: '/pages/profile/tenant-switch/tenant-switch' })
  },

  goToBalance: function() {
    if (!this.data.hasLogin) return this.showLoginTip()
    wx.navigateTo({ url: '/pages/profile/balance' })
  },

  onLoginTap: function() {
    wx.navigateTo({ url: '/pages/profile/login' })
  },

  onMenuItemTap: function(e) {
    const item = e.currentTarget.dataset.item
    if (!item) return;
    
    if (item.needLogin && !this.data.hasLogin) {
      this.showLoginTip()
      return
    }

    if (item.id === 10) { // 联系客服
      this.contactService()
      return
    }

    if (item.id === 11) { // 帮助中心
      wx.showModal({
        title: '帮助中心',
        content: '1. 首页极简版专为骑手打造，扫大按钮直达取电\n2. 可在【我的卡券】中激活购买的套餐\n3. 如果有任何问题可随时联系客服',
        showCancel: false
      })
      return
    }

    if (item.path) {
      wx.navigateTo({ url: item.path })
    }
  },

  contactService: function() {
    wx.showModal({
      title: '联系客服',
      content: '客服电话: 400-123-4567\n工作时间: 9:00-18:00',
      showCancel: true,
      confirmText: '拨打电话',
      success: (res) => {
        if (res.confirm) {
          wx.makePhoneCall({ phoneNumber: '4001234567' })
        }
      }
    })
  },

  showLoginTip: function() {
    wx.showModal({
      title: '提示',
      content: '请先登录后再使用此功能',
      confirmText: '去登录',
      success: (res) => {
        if (res.confirm) {
          wx.navigateTo({ url: '/pages/profile/login' })
        }
      }
    })
  },

  onLogout: function() {
    wx.showModal({
      title: '确认退出',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          this.logout()
        }
      }
    })
  },

  logout: function() {
    wx.showLoading({ title: '退出中...' })

    const clearLocal = () => {
      wx.hideLoading()
      wx.removeStorageSync('token')
      wx.removeStorageSync('userInfo')

      this.setData({
        hasLogin: false,
        userInfo: null,
        avatarPlaceholderText: '访',
        balance: 0,
        stats: {
          currentPackage: null,
          rentedBattery: null
        }
      })

      wx.showToast({ title: '已退出登录', icon: 'success' })
    }

    request.post('/auth/logout').then(() => clearLocal()).catch(() => clearLocal())
  },

  onPullDownRefresh: function() {
    if (this.data.hasLogin) {
      this.loadUserData()
      this.loadUnreadCount()
    }
    wx.stopPullDownRefresh()
  },

  loadUnreadCount: function() {
    getUnreadCount().then(res => {
      this.setData({ unreadCount: (res.data || {}).count || 0 })
    }).catch(() => {})
  },

  goToNotifications: function() {
    if (!this.data.hasLogin) {
      wx.navigateTo({ url: '/pages/profile/login' })
      return
    }
    wx.navigateTo({ url: '/pages/notification/list' })
  },

  goToFaultList: function() {
    if (!this.data.hasLogin) {
      wx.navigateTo({ url: '/pages/profile/login' })
      return
    }
    wx.navigateTo({ url: '/pages/fault/list' })
  },

  goToStore: function() {
    wx.navigateTo({ url: '/pages/store/list' })
  }
})
