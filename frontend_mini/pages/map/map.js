// pages/map/map.js
const { getNearbyStations, getStations } = require('../../api/station')

function toNum(v) {
  const n = Number(v)
  return Number.isFinite(n) ? n : NaN
}

Page({
  data: {
    latitude: 38.0428,
    longitude: 114.5149,
    markers: [],
    stations: [],
    selectedStation: null,
    showStationDetail: false,
    userLocation: null,
    scale: 14,
    isLoading: false,
    searchRadius: 15000,
    locationEnabled: false,
    searchKeyword: '',
    showPrivacyAuthorization: false
  },

  onLoad: function () {
    this._privacyResolve = null
    this._showingLocationGuide = false
    this.registerMapPrivacyListener()
    if (typeof wx.requirePrivacyAuthorize === 'function') {
      wx.requirePrivacyAuthorize({
        success: () => this.checkLocationPermission(),
        fail: () => this.checkLocationPermission()
      })
    } else {
      this.checkLocationPermission()
    }
  },

  /** 微信要求：用户须点击带 agreePrivacyAuthorization 的 button 后才能 resolve，不能用 Modal */
  registerMapPrivacyListener: function () {
    if (typeof wx.onNeedPrivacyAuthorization !== 'function') return
    wx.onNeedPrivacyAuthorization((resolve) => {
      this._privacyResolve = resolve
      this.setData({ showPrivacyAuthorization: true })
    })
  },

  onAgreePrivacyAuthorization: function () {
    if (typeof this._privacyResolve === 'function') {
      this._privacyResolve({ buttonId: 'agree-btn', event: 'agree' })
      this._privacyResolve = null
    }
    this.setData({ showPrivacyAuthorization: false })
  },

  onRejectPrivacyAuthorization: function () {
    if (typeof this._privacyResolve === 'function') {
      this._privacyResolve({ event: 'disagree' })
      this._privacyResolve = null
    }
    this.setData({ showPrivacyAuthorization: false })
    wx.showToast({ title: '未同意将无法使用定位', icon: 'none' })
  },

  onReady: function () {
    this.ensureMapContext()
    if (this.data.locationEnabled && this.data.userLocation) {
      this.moveMapToUser()
    }
  },

  onShow: function () {
    wx.getSetting({
      success: (res) => {
        const granted = res.authSetting['scope.userLocation']
        if (granted === true) {
          if (!this.data.locationEnabled) {
            // 从设置页返回后权限刚被允许，重新定位后再加载站点
            this.setData({ locationEnabled: true })
            this.getUserLocation()           // getUserLocation 成功后会自行调用 loadNearbyStations
            return
          }
        }
        // 已有坐标则直接刷新；首次进入且未授权时不发请求（坐标为默认值石家庄）
        if (this.data.userLocation) {
          this.loadNearbyStations()
        }
      },
      fail: () => {
        if (this.data.userLocation) {
          this.loadNearbyStations()
        }
      }
    })
  },

  /** Map 为原生组件，需尽早拿到 context；部分时机 onReady 较晚，这里可兜底创建 */
  ensureMapContext: function () {
    if (!this.mapContext) {
      this.mapContext = wx.createMapContext('map')
    }
    return this.mapContext
  },

  moveMapToUser: function () {
    const ctx = this.ensureMapContext()
    if (!ctx) return
    wx.nextTick(() => {
      ctx.moveToLocation({
        success: () => {},
        fail: () => {}
      })
    })
  },

  checkLocationPermission: function () {
    wx.getSetting({
      success: (res) => {
        if (res.authSetting['scope.userLocation'] === true) {
          this.setData({ locationEnabled: true })
          this.getUserLocation()
        } else if (res.authSetting['scope.userLocation'] === false) {
          this.setData({ locationEnabled: false })
          this.showLocationGuideModal()
        } else {
          this.setData({ locationEnabled: false })
          this.requestLocationPermission()
        }
      },
      fail: () => {
        this.setData({ locationEnabled: false })
        // getSetting 异常时直接尝试定位，由系统/隐私弹窗处理
        this.getUserLocation()
      }
    })
  },

  showLocationGuideModal: function () {
    if (this._showingLocationGuide) return
    this._showingLocationGuide = true
    wx.showModal({
      title: '需要定位权限',
      content:
        '用于在地图上显示您的位置和附近换电站。请点击「去设置」→ 打开「位置信息」。\n\n也可使用顶部搜索条在地图上手动选点。',
      confirmText: '去设置',
      cancelText: '暂不',
      success: (r) => {
        if (r.confirm) {
          wx.openSetting({
            success: (res) => {
              if (res.authSetting['scope.userLocation'] === true) {
                this.setData({ locationEnabled: true })
                this.getUserLocation({ showHud: true })
              }
            },
            complete: () => {
              this._showingLocationGuide = false
            }
          })
          return
        }
        this._showingLocationGuide = false
      },
      fail: () => {
        this._showingLocationGuide = false
      }
    })
  },

  requestLocationPermission: function () {
    wx.authorize({
      scope: 'scope.userLocation',
      success: () => {
        this.setData({ locationEnabled: true })
        this.getUserLocation({ showHud: true })
      },
      fail: (err) => {
        const msg = (err && err.errMsg) || ''
        if (msg.indexOf('auth deny') !== -1 || msg.indexOf('auth denied') !== -1) {
          this.showLocationGuideModal()
        }
        this.loadNearbyStations()
      }
    })
  },

  /**
   * @param {{ showHud?: boolean }} opts showHud 为 true 时显示「定位中」（用于用户点击「定位」）
   */
  getUserLocation: function (opts) {
    const showHud = !!(opts && opts.showHud)
    const finishFail = (err) => {
      if (showHud) wx.hideLoading()
      const msg = (err && err.errMsg) || ''
      if (
        msg.indexOf('auth deny') !== -1 ||
        msg.indexOf('privacy') !== -1 ||
        msg.indexOf('Privacy') !== -1
      ) {
        this.setData({ locationEnabled: false })
        this.showLocationGuideModal()
      } else {
        wx.showToast({
          title: '定位失败，请打开系统定位与微信位置权限',
          icon: 'none',
          duration: 2800
        })
      }
      this.loadNearbyStations()
    }

    const finishSuccess = (res) => {
      if (showHud) wx.hideLoading()
      const lat = res.latitude
      const lng = res.longitude
      this.setData(
        {
          latitude: lat,
          longitude: lng,
          userLocation: { latitude: lat, longitude: lng },
          searchKeyword: '',
          locationEnabled: true,
          scale: 16
        },
        () => {
          this.moveMapToUser()
          this.loadNearbyStations()
        }
      )
    }

    const tryLocate = (useHigh) => {
      const opt = {
        type: 'gcj02',
        success: finishSuccess,
        fail: (err) => {
          if (useHigh) {
            tryLocate(false)
            return
          }
          console.error('Map getLocation failed:', err)
          wx.showToast({ title: '定位失败，请检查手机定位开关', icon: 'none' })
          finishFail(err)
        }
      }
      if (useHigh) {
        opt.isHighAccuracy = true
        opt.highAccuracyExpireTime = 5000
      }
      wx.getLocation(opt)
    }

    if (showHud) wx.showLoading({ title: '定位中…', mask: true })
    tryLocate(true)
  },

  onChooseSearchArea: function () {
    const run = () => {
      // 必须先检查权限，如果没有权限先请求权限
      wx.getSetting({
        success: (res) => {
          if (!res.authSetting['scope.userLocation']) {
            wx.authorize({
              scope: 'scope.userLocation',
              success: () => {
                this.openChooseLocation()
              },
              fail: () => {
                this.showLocationGuideModal()
              }
            })
          } else {
            this.openChooseLocation()
          }
        }
      })
    }
    if (typeof wx.requirePrivacyAuthorize === 'function') {
      wx.requirePrivacyAuthorize({
        success: () => run(),
        fail: () => run()
      })
    } else {
      run()
    }
  },

  openChooseLocation: function () {
    wx.chooseLocation({
      success: (res) => {
        const lat = res.latitude
        const lng = res.longitude
        const name = res.name || ''
        const addr = res.address || ''
        this.setData({
          latitude: lat,
          longitude: lng,
          locationEnabled: true,
          searchKeyword: name || addr || '已选位置',
          selectedStation: null,
          showStationDetail: false,
          scale: 15
        })
        this.loadNearbyStations()
      },
      fail: (err) => {
        console.error('chooseLocation API failed:', err)
        if(err.errMsg && err.errMsg.indexOf('cancel') === -1) {
            wx.showModal({
                title: '位置调用失败',
                content: err.errMsg || '未知错误',
                showCancel: false
            })
        }
      }
    })
  },

  loadNearbyStations: function () {
    if (this.data.isLoading) return

    this.setData({ isLoading: true })
    wx.showLoading({ title: '加载站点…', mask: false })

    const { latitude, longitude, searchRadius, userLocation } = this.data
    const lat = toNum(latitude)
    const lng = toNum(longitude)
    const hasRealLocation = !!userLocation && !Number.isNaN(lat) && !Number.isNaN(lng)
    const requestTask = hasRealLocation
      ? getNearbyStations({
        latitude: lat,
        longitude: lng,
        radius: Math.max(1, Math.ceil(searchRadius / 1000)),
        limit: 50
      })
      : getStations({ limit: 50 })

    requestTask
      .then((res) => {
        const payload = res.data || {}
        const stations = payload.stations || []
        this.setData({
          stations,
          smartRecommend: stations[0] || null,
          markers: this.createMarkers(stations),
          isLoading: false
        })
        wx.hideLoading()
      })
      .catch((err) => {
        const msg = (err && (err.message || err.msg)) || '加载站点失败'
        wx.showToast({ title: msg, icon: 'none' })
        this.setData({ isLoading: false })
        wx.hideLoading()
      })
  },

  createMarkers: function (stations) {
    return stations
      .map((station) => {
        const lat = toNum(station.latitude)
        const lng = toNum(station.longitude)
        if (Number.isNaN(lat) || Number.isNaN(lng)) return null

        // 步骤10：根据健康状态选择标注颜色
        let bgColor = '#0d9488'  // 默认绿色（电池充足）
        if (station.health_status === 'empty') {
          bgColor = '#9ca3af'     // 灰色（无电池）
        } else if (station.health_status === 'low') {
          bgColor = '#f59e0b'     // 黄色（电池紧张）
        } else if (station.health_status === 'maintenance') {
          bgColor = '#ef4444'     // 红色（维护中）
        }

        return {
          id: station.id,
          latitude: lat,
          longitude: lng,
          title: station.name,
          iconPath: '/images/marker.png',
          width: 1,
          height: 1,
          alpha: 0,
          // 仿小哈换电风格，使用 callout 直接常驻显示可用电池数
          customCallout: {
            display: 'ALWAYS',
            anchorY: 0,
            anchorX: 0,
            bgColor: bgColor,
            content: String(station.available_batteries || 0)
          }
        }
      })
      .filter(Boolean)
  },

  onCalloutTap: function(e) {
    const markerId =
      e.detail && e.detail.markerId !== undefined && e.detail.markerId !== null
        ? e.detail.markerId
        : e.markerId
    const station = this.data.stations.find((s) => s.id === markerId)
    if (station) {
      this.showStationDetail(station)
    }
  },

  onMarkerTap: function (e) {
    const markerId =
      e.detail && e.detail.markerId !== undefined && e.detail.markerId !== null
        ? e.detail.markerId
        : e.markerId
    const station = this.data.stations.find((s) => s.id === markerId)
    if (station) {
      this.showStationDetail(station)
    }
  },

  showStationDetail: function (station) {
    const lat = toNum(station.latitude)
    const lng = toNum(station.longitude)
    if (Number.isNaN(lat) || Number.isNaN(lng)) {
      wx.showToast({ title: '站点坐标无效', icon: 'none' })
      return
    }
    this.setData({
      selectedStation: station,
      showStationDetail: true,
      latitude: lat,
      longitude: lng,
      scale: 16
    })
  },

  hideStationDetail: function () {
    this.setData({
      showStationDetail: false,
      selectedStation: null
    })
  },

  navigateToStation: function () {
    const station = this.data.selectedStation
    if (!station) return
    const lat = toNum(station.latitude)
    const lng = toNum(station.longitude)
    if (Number.isNaN(lat) || Number.isNaN(lng)) {
      wx.showToast({ title: '无法导航：坐标无效', icon: 'none' })
      return
    }
    wx.openLocation({
      latitude: lat,
      longitude: lng,
      name: station.name || '换电站',
      address: station.address || '',
      scale: 18
    })
  },

  viewStationDetail: function () {
    const station = this.data.selectedStation
    if (!station) return
    wx.navigateTo({
      url: `/pages/station/detail?id=${station.id}`
    })
  },

  onRegionChange: function (e) {
    if (e.type === 'end' && e.causedBy === 'drag') {
      const ctx = this.ensureMapContext()
      if (!ctx) return
      ctx.getCenterLocation({
        success: (res) => {
          this.setData({
            latitude: res.latitude,
            longitude: res.longitude
          })
        }
      })
    }
  },

  relocateUser: function () {
    this.ensureMapContext()
    const runAfterPrivacy = () => {
      wx.getSetting({
        success: (res) => {
          const loc = res.authSetting['scope.userLocation']
          if (loc === true) {
            this.setData({ locationEnabled: true })
            this.getUserLocation({ showHud: true })
          } else if (loc === false) {
            wx.openSetting({
              success: (settingRes) => {
                if (settingRes.authSetting['scope.userLocation'] === true) {
                  this.setData({ locationEnabled: true })
                  this.getUserLocation({ showHud: true })
                } else {
                  this.showLocationGuideModal()
                }
              },
              fail: () => {
                this.showLocationGuideModal()
              }
            })
          } else {
            this.requestLocationPermission()
          }
        },
        fail: () => {
          this.getUserLocation({ showHud: true })
        }
      })
    }
    if (typeof wx.requirePrivacyAuthorize === 'function') {
      wx.requirePrivacyAuthorize({
        success: () => runAfterPrivacy(),
        fail: () => runAfterPrivacy()
      })
    } else {
      runAfterPrivacy()
    }
  },

  onRefresh: function () {
    const ctx = this.ensureMapContext()
    if (ctx) {
      ctx.getCenterLocation({
        success: (res) => {
          this.setData(
            {
              latitude: res.latitude,
              longitude: res.longitude
            },
            () => this.loadNearbyStations()
          )
        },
        fail: () => this.loadNearbyStations()
      })
    } else {
      this.loadNearbyStations()
    }
  },

  onShareAppMessage: function () {
    return {
      title: '智慧换电 - 地图找站',
      path: '/pages/map/map'
    }
  }
})
