// pages/index/index.js
const { getNearbyStations, getStations } = require('../../api/station')
const { getUserStats, getUserBalance } = require('../../api/user')
const { getBatteryInsight } = require('../../utils/batteryInsight')
const { formatDistanceKm } = require('../../utils/util')
const { pickRecommendedStation, getRecommendationReason } = require('../../utils/stationRecommendation')
const { getPackageRecommendations } = require('../../api/recommend')
const { getUserPreferences } = require('../../api/rider')
const { getCurrentTenantName } = require('../../utils/tenant')

const ALERT_CACHE_KEY = 'index_low_battery_alert'
const INDEX_REFRESH_FLAG = 'index_needs_refresh'

Page({
  data: {
    hasLogin: false,
    mode: 'normal', // 'normal' | 'delivery'
    nearbyStations: [], // 附近站点
    batteryInsight: null,
    alertIconText: '🔋',
    recommendedStation: null,
    recommendedDistanceText: '-',
    alertBannerText: '',
    latitude: null,
    longitude: null,
    hasRealLocation: false,
    recommendedPackages: [],
    userBalance: 0,
    userBalanceText: '0.00',
    userPackageStatus: '',
    tenantName: 'PowerNest 官方演示租户'
  },

  onLoad: function() {
    this.loadUserMode()
    this.checkLoginStatus()
    this.getUserLocation()
  },

  onShow: function() {
    this.checkLoginStatus()
    this.refreshTenantInfo()
    const shouldRefresh = !!wx.getStorageSync(INDEX_REFRESH_FLAG)
    if (shouldRefresh) {
      wx.removeStorageSync(INDEX_REFRESH_FLAG)
    }
    if (this.data.latitude && this.data.longitude) {
      this.loadData()
    } else if (shouldRefresh) {
      this.getUserLocation()
    }
  },

  checkLoginStatus: function() {
    const token = wx.getStorageSync('token')
    this.setData({
      hasLogin: !!token
    })
  },

  refreshTenantInfo: function() {
    this.setData({ tenantName: getCurrentTenantName() })
  },

  onSwitchTenantTap: function() {
    wx.navigateTo({ url: '/pages/profile/tenant-switch/tenant-switch' })
  },

  loadUserMode: function() {
    // 从本地存储读取用户偏好模式
    const savedMode = wx.getStorageSync('user_mode') || 'normal'
    this.setData({ mode: savedMode })

    // 如果已登录，尝试从后端获取（静默失败，因为这个接口可能未实现）
    const token = wx.getStorageSync('token')
    if (token) {
      getUserPreferences()
        .then(res => {
          const mode = (res.data && res.data.mode) || savedMode
          this.setData({ mode })
          wx.setStorageSync('user_mode', mode)
        })
        .catch(() => {
          // 静默失败，使用本地存储的值
          // 这个接口可能未实现，不影响功能
        })
    }
  },

  onModeChange: function(e) {
    const mode = e.detail.mode
    this.setData({ mode })
    // 模式切换后重新加载数据
    this.loadData()
  },

  getUserLocation: function() {
    wx.getLocation({
      type: 'gcj02',
      success: (res) => {
        this.setData({
          latitude: res.latitude,
          longitude: res.longitude,
          hasRealLocation: true
        })
        this.loadData()
      },
      fail: () => {
        this.setData({
          latitude: null,
          longitude: null,
          hasRealLocation: false
        })
        this.loadData()
      }
    })
  },

  loadData: function() {
    this.loadNearbyStations()
    if (this.data.hasLogin) {
      if (this.data.mode === 'delivery') {
        // 送单模式：加载余额和套餐状态
        this.loadUserBalance()
      } else {
        // 普通模式：加载推荐套餐
        this.loadRecommendedPackages()
      }
    }
  },

  loadUserBalance: function() {
    Promise.all([getUserBalance(), getUserStats()])
      .then(([balanceRes, statsRes]) => {
        const balanceData = balanceRes.data || {}
        const stats = statsRes.data || {}
        const balance = Number(balanceData.balance) || 0
        const currentPackage = stats.currentPackage || null

        this.setData({
          userBalance: balance,
          userBalanceText: balance.toFixed(2),
          userPackageStatus: currentPackage ? currentPackage.name : '无套餐'
        })
      })
      .catch(err => {
        console.error('加载送单状态失败:', err)
      })
  },

  loadNearbyStations: function() {
    const { latitude, longitude, hasRealLocation } = this.data
    const requestTask = hasRealLocation && latitude != null && longitude != null
      ? getNearbyStations({ latitude, longitude, radius: 5, limit: 3 })
      : getStations({ limit: 3 })

    requestTask.then(res => {
      const payload = res.data || {}
      const list = (payload.stations || []).map(station => this.enhanceStation(station))
      const recommendedStation = this.enhanceStation(pickRecommendedStation(list, this.data.batteryInsight))

      if (recommendedStation && recommendedStation.distance != null) {
        const distKm = recommendedStation.distance > 100
          ? recommendedStation.distance / 1000
          : recommendedStation.distance
        const avgSpeedKmH = 22
        recommendedStation.etaMinutes = Math.ceil((distKm / avgSpeedKmH) * 60)
      }

      this.setData({
        nearbyStations: list,
        recommendedStation,
        recommendedDistanceText: this.getRecommendedDistanceText(recommendedStation)
      })
      
      if (this.data.hasLogin) {
        this.loadStats()
      }
    }).catch(err => {
      console.error('加载站点失败:', err)
    })
  },

  loadStats: function() {
    const { nearbyStations } = this.data
    getUserStats()
      .then(res => {
        const d = res.data || {}
        const batteryInsight = d.rentedBattery ? getBatteryInsight(d.rentedBattery) : null
        const recommendedStation = pickRecommendedStation(nearbyStations, batteryInsight)

        if (recommendedStation && recommendedStation.distance != null) {
          const distKm = recommendedStation.distance > 100
            ? recommendedStation.distance / 1000
            : recommendedStation.distance
          const avgSpeedKmH = 22
          recommendedStation.etaMinutes = Math.ceil((distKm / avgSpeedKmH) * 60)
        }

        this.setData({
          batteryInsight,
          alertIconText: this.getAlertIconText(batteryInsight),
          recommendedStation,
          recommendedDistanceText: this.getRecommendedDistanceText(recommendedStation),
          alertBannerText: this.getAlertBannerText(batteryInsight, recommendedStation)
        })
      })
      .catch(err => {
        console.error('加载统计数据失败:', err)
      })
  },

  getAlertBannerText(batteryInsight, recommendedStation) {
    if (!batteryInsight) return ''
    if (batteryInsight.alertLevel === 'emergency') {
      return recommendedStation ? `电量紧急，建议立即前往 ${recommendedStation.name}` : '电量紧急，建议立即规划换电'
    }
    if (batteryInsight.alertLevel === 'warning') {
      return recommendedStation ? `电量偏低，建议优先前往 ${recommendedStation.name}` : '电量偏低，建议尽快换电'
    }
    return ''
  },

  enhanceStation(station) {
    if (!station) return null
    const next = { ...station }
    next.availableBatteryCount = Number(next.available_batteries) || 0
    next.distanceText = next.distance_text || (next.distance == null ? '' : formatDistanceKm(next.distance))
    return next
  },

  getRecommendedDistanceText(station) {
    if (!station) return ''
    return station.distance_text || (station.distance == null ? '' : formatDistanceKm(station.distance))
  },

  getAlertIconText(batteryInsight) {
    return batteryInsight && batteryInsight.alertLevel === 'emergency' ? '⚡' : '🔋'
  },

  onBatteryInsightTap() {
    wx.switchTab({
      url: '/pages/exchange/exchange/exchange'
    })
  },

  onRecommendationTap() {
    const station = this.data.recommendedStation
    if (!station) {
      this.onViewMoreStations()
      return
    }
    wx.navigateTo({ url: `/pages/station/detail?id=${station.id}` })
  },

  onNavToRecommend() {
    const recommended = this.data.recommendedStation
    if (recommended) {
      wx.openLocation({
        latitude: Number(recommended.latitude),
        longitude: Number(recommended.longitude),
        name: recommended.name || '换电站',
        address: recommended.address || '',
        scale: 18
      })
    } else {
      wx.switchTab({ url: '/pages/map/map' })
    }
  },

  onNavToStation: function(e) {
    const station = e.currentTarget.dataset.item
    wx.openLocation({
      latitude: Number(station.latitude),
      longitude: Number(station.longitude),
      name: station.name || '换电站',
      address: station.address || '',
      scale: 18
    })
  },

  onStationTap: function(e) {
    const stationId = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/station/detail?id=${stationId}`
    })
  },

  onViewMoreStations: function() {
    wx.switchTab({
      url: '/pages/map/map'
    })
  },

  onScanTap: function() {
    if (!this.data.hasLogin) {
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
      return
    }

    wx.navigateTo({
      url: '/pages/battery/scan'
    })
  },

  onPullDownRefresh: function() {
    this.loadData()
    wx.stopPullDownRefresh()
  },

  loadRecommendedPackages: function() {
    getPackageRecommendations(3)
      .then(res => {
        const packages = (res.data && res.data.packages) || []
        this.setData({ recommendedPackages: packages })
      })
      .catch(err => {
        console.error('加载推荐套餐失败:', err)
      })
  },

  onPackageTap: function(e) {
    const packageId = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/package/detail?id=${packageId}`
    })
  },

  onViewAllPackages: function() {
    wx.switchTab({
      url: '/pages/package/list'
    })
  },

  onShareAppMessage: function() {
    return {
      title: 'PowerNest 骑手极速换电',
      path: '/pages/index/index'
    }
  }
})
