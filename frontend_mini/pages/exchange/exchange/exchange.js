// pages/exchange/exchange/exchange.js
const { getUserStats } = require('../../../api/user')
const { getNearbyStations, getStations } = require('../../../api/station')
const { getStationBatteries } = require('../../../api/station')
const { rentBattery, returnBattery } = require('../../../api/battery')
const { exchangeBattery } = require('../../../api/exchange')
const { getBatteryInsight } = require('../../../utils/batteryInsight')
const { pickRecommendedStation } = require('../../../utils/stationRecommendation')

const INDEX_REFRESH_FLAG = 'index_needs_refresh'
const PROFILE_REFRESH_FLAG = 'profile_needs_refresh'

Page({
  data: {
    step: 0,           // 0=租电  1=选站  2=选电池  3=确认
    // Step 0 / Rent
    rentConfirming: false,
    rentSelectedStation: null,
    rentSelectedBattery: null,
    // Step 1
    stations: [],
    stationLoading: false,
    selectedStation: null,
    // Step 2
    availableBatteries: [],
    batteryLoading: false,
    selectedBattery: null,
    // Step 3
    currentBattery: null,
    exchangeFee: 0,
    confirming: false,
    // Shared
    loading: false,
    latitude: null,
    longitude: null,
    hasRealLocation: false,
    error: '',
    exchangeError: '',
    canExchange: false,
    batteryInsight: null,
    recommendedStation: null
  },

  onLoad() {
    // 不要在这里 checkLogin，因为小程序生命周期问题可能导致卡死或白屏
    // this.checkLogin()
  },

  onShow() {
    // 先检查登录状态
    if (!this.checkLogin()) {
      return
    }
    this.initData()
  },

  checkLogin() {
    const token = wx.getStorageSync('token')
    if (!token) {
      wx.showModal({
        title: '需要登录',
        content: '请先登录后再使用换电功能',
        confirmText: '去登录',
        cancelText: '取消',
        success: (res) => {
          if (res.confirm) {
            wx.navigateTo({
              url: '/pages/profile/login'
            })
          }
        }
      })
      return false
    }
    return true
  },

  initData() {
    this.getLocation()
  },

  resetExchangeState() {
    this.setData({
      confirming: false,
      rentConfirming: false,
      canExchange: false,
      step: 0,
      selectedStation: null,
      selectedBattery: null,
      rentSelectedStation: null,
      rentSelectedBattery: null,
      currentBattery: null,
      availableBatteries: [],
      stations: [],
      batteryInsight: null,
      recommendedStation: null,
      exchangeError: '',
      error: '',
      exchangeFee: 0
    })
  },

  markRefreshFlags() {
    wx.setStorageSync(INDEX_REFRESH_FLAG, 1)
    wx.setStorageSync(PROFILE_REFRESH_FLAG, 1)
  },

  refreshAfterExchange(result = {}) {
    const newBattery = result.new_battery || null
    this.resetExchangeState()

    if (newBattery) {
      this.setData({
        currentBattery: newBattery,
        batteryInsight: getBatteryInsight(newBattery),
        canExchange: true,
        exchangeFee: Number(result.exchange_fee || 0)
      })
    }

    this.markRefreshFlags()
    this.initData()
  },

  getLocation() {
    wx.showLoading({ title: '获取位置...' })
    wx.getLocation({
      type: 'gcj02',
      success: (res) => {
        this.setData({
          latitude: res.latitude,
          longitude: res.longitude,
          hasRealLocation: true
        })
        this.loadCurrentBattery()
      },
      fail: () => {
        wx.hideLoading()
        wx.showToast({ title: '定位失败，已隐藏距离信息', icon: 'none' })
        this.setData({
          latitude: null,
          longitude: null,
          hasRealLocation: false
        })
        this.loadCurrentBattery()
      }
    })
  },

  // Step 1: 获取当前租用电池
  loadCurrentBattery() {
    wx.showLoading({ title: '加载中...' })
    getUserStats()
      .then(res => {
        wx.hideLoading()
        const stats = res.data || {}
        const rentedBattery = stats.rentedBattery || null

        if (!rentedBattery) {
          this.setData({
            error: '',
            exchangeError: '您当前没有正在租用的电池，可直接在本页租用一块电池',
            canExchange: false,
            currentBattery: null,
            batteryInsight: null,
            selectedStation: null,
            selectedBattery: null,
            rentSelectedStation: null,
            rentSelectedBattery: null,
            availableBatteries: [],
            step: 0
          })
          this.loadNearbyStations()
          return
        }

        this.setData({
          error: '',
          exchangeError: '',
          canExchange: true,
          step: 1,
          currentBattery: rentedBattery,
          batteryInsight: getBatteryInsight(rentedBattery)
        })
        this.loadNearbyStations()
      })
      .catch(() => {
        wx.hideLoading()
        this.setData({
          error: '加载当前租用电池失败，请重新进入页面或重新登录',
          exchangeError: '当前无法确认租用电池状态，已禁止换电操作',
          canExchange: false,
          step: 0,
          currentBattery: null,
          batteryInsight: null,
          selectedStation: null,
          selectedBattery: null,
          rentSelectedStation: null,
          rentSelectedBattery: null,
          availableBatteries: []
        })
        this.loadNearbyStations()
      })
  },

  // Step 1: 加载附近站点
  loadNearbyStations() {
    const { latitude, longitude, hasRealLocation } = this.data
    this.setData({ stationLoading: true })

    const requestTask = hasRealLocation && latitude != null && longitude != null
      ? getNearbyStations({ latitude, longitude, radius: 10, limit: 20 })
      : getStations({ limit: 20 })

    requestTask
      .then(res => {
        const stations = (res.data || {}).stations || []
        console.log('加载到的站点:', stations)
        const recommended = pickRecommendedStation(stations, this.data.batteryInsight)
        this.setData({
          stations,
          stationLoading: false,
          error: stations.length === 0 ? '附近暂无换电站点' : '',
          recommendedStation: recommended
        })
      })
      .catch((err) => {
        console.error('加载站点失败:', err)
        this.setData({
          stationLoading: false,
          error: '加载站点失败，请点击重新加载'
        })
      })
  },

  // 选择租用站点
  onStationSelectForRent(e) {
    const station = e.currentTarget.dataset.station
    this.setData({
      rentSelectedStation: station,
      rentSelectedBattery: null
    })
    wx.showToast({
      title: `已选择 ${station.name}`,
      icon: 'none'
    })
  },

  // 选择站点
  onStationSelect(e) {
    if (!this.data.canExchange || !this.data.currentBattery) {
      wx.showToast({ title: '当前没有可换的在租电池', icon: 'none' })
      return
    }
    const station = e.currentTarget.dataset.station
    this.setData({
      selectedStation: station,
      step: 2,
      availableBatteries: [],
      selectedBattery: null
    })
    this.loadStationBatteries(station.id)
  },

  // 返回上一步
  onBackStep() {
    const step = this.data.step
    if (step === 2) {
      this.setData({
        step: 1,
        availableBatteries: [],
        selectedBattery: null
      })
    } else if (step === 3) {
      this.setData({ step: 2 })
    }
  },

  // 直接归还
  onDirectReturn() {
    const battery = this.data.currentBattery
    if (!battery) {
      wx.showToast({ title: '当前没有可归还的电池', icon: 'none' })
      return
    }

    wx.showModal({
      title: '直接归还电池',
      content: '确认直接归还当前电池吗？归还后本次租用将结束，如需继续使用可重新租用。',
      confirmText: '确认归还',
      success: (res) => {
        if (!res.confirm) return

        wx.showLoading({ title: '归还中...' })
        returnBattery({
          battery_id: battery.id,
          station_id: (this.data.selectedStation && this.data.selectedStation.id) || 1,
          cabinet_id: battery.current_cabinet_id || 1,
          latitude: this.data.latitude,
          longitude: this.data.longitude
        })
          .then(() => {
            wx.hideLoading()
            wx.showModal({
              title: '归还成功',
              content: '电池已成功归还，您现在可以重新租用电池。',
              showCancel: false,
              success: () => {
                this.resetExchangeState()
                this.initData()
                this.markRefreshFlags()
              }
            })
          })
          .catch(err => {
            wx.hideLoading()
            wx.showModal({
              title: '归还失败',
              content: (err && err.message) || '归还失败，请重试',
              showCancel: false
            })
          })
      }
    })
  },

  // Step 2: 加载站点可用电池
  loadStationBatteries(stationId) {
    this.setData({ batteryLoading: true, error: '' })

    getStationBatteries(stationId, { limit: 20 })
      .then(res => {
        const inner = res.data || {}
        const list = inner.list || inner.items || []
        // 过滤掉当前正在租用的电池
        const currentId = (this.data.currentBattery && this.data.currentBattery.id) || null
        const available = list.filter(b => b.id !== currentId)
        this.setData({
          availableBatteries: available,
          batteryLoading: false,
          error: available.length === 0 ? '该站点暂无可用电池' : ''
        })
      })
      .catch(() => {
        this.setData({
          batteryLoading: false,
          error: '加载电池失败'
        })
      })
  },

  // 选择电池
  onBatterySelect(e) {
    const battery = e.currentTarget.dataset.battery
    this.setData({
      selectedBattery: battery,
      step: 3
    })
  },

  // 刷新电池列表
  onRefreshBatteries() {
    const station = this.data.selectedStation
    if (station) {
      this.loadStationBatteries(station.id)
    }
  },

  // 快速租用
  onQuickRent() {
    const station = this.data.rentSelectedStation || this.data.recommendedStation || this.data.stations[0]
    if (!station) {
      wx.showToast({ title: '暂无可租用站点', icon: 'none' })
      return
    }

    if ((station.available_batteries || 0) <= 0) {
      wx.showToast({ title: '该站点暂无可租电池', icon: 'none' })
      return
    }

    if (this.data.rentConfirming) return

    wx.showModal({
      title: '快速租用电池',
      content: `确认从“${station.name}”租用一块电池吗？系统将自动分配一块满电电池。`,
      confirmText: '确认租用',
      success: (res) => {
        if (!res.confirm) return

        this.setData({ rentConfirming: true })
        wx.showLoading({ title: '租用中...' })

        getStationBatteries(station.id, { limit: 20 })
          .then(resBatteries => {
            const inner = resBatteries.data || {}
            const list = inner.list || inner.items || []
            const battery = list[0]

            if (!battery) {
              throw new Error('该站点暂无可租用电池')
            }

            return rentBattery({
              battery_id: battery.id,
              station_id: station.id,
              cabinet_id: battery.current_cabinet_id || 1,
              latitude: this.data.latitude,
              longitude: this.data.longitude
            })
          })
          .then(resOrder => {
            wx.hideLoading()
            const order = resOrder.data || {}
            const isFreeRent = Number(order.total_amount || 0) === 0
            this.setData({ rentConfirming: false })

            if (isFreeRent) {
              wx.showModal({
                title: '租用成功',
                content: `已使用套餐完成租电${order.order_no ? `（${order.order_no}）` : ''}，无需支付，可直接取用电池。`,
                showCancel: false,
                success: () => {
                  this.markRefreshFlags()
                  this.initData()
                }
              })
              return
            }

            wx.showModal({
              title: '订单创建成功',
              content: `已为您创建租电订单${order.order_no ? `（${order.order_no}）` : ''}，请先完成支付后再取用电池。`,
              confirmText: '去支付',
              cancelText: '稍后支付',
              success: (modalRes) => {
                this.markRefreshFlags()
                if (order.order_no && modalRes.confirm) {
                  wx.navigateTo({
                    url: `/pages/order/detail?order_no=${order.order_no}`
                  })
                  return
                }
                this.initData()
              }
            })
          })
          .catch(err => {
            wx.hideLoading()
            this.setData({ rentConfirming: false })
            wx.showModal({
              title: '租用失败',
              content: (err && (err.message || (err.data && err.data.message))) || '租用失败，请重试',
              showCancel: false
            })
          })
      }
    })
  },

  // Step 3: 确认换电
  onConfirmExchange() {
    const { currentBattery, selectedBattery, selectedStation, confirming, canExchange } = this.data
    if (confirming) return

    if (!canExchange || !currentBattery) {
      wx.showToast({ title: '当前没有可换的在租电池', icon: 'none' })
      return
    }

    if (!selectedBattery || !selectedStation) {
      wx.showToast({ title: '数据不完整，无法换电', icon: 'none' })
      return
    }

    // 毕设演示模式：一键模拟换电柜交互流程，跳过真实的物理扫码
    wx.showModal({
      title: '操作提示 (毕设演示)',
      content: '系统将跳过扫码环节，直接模拟换电柜开门交互流程',
      confirmText: '开始换电',
      cancelText: '取消',
      success: (resScan) => {
        if (resScan.confirm) {
          wx.showLoading({ title: '正在连接电柜...' })
          setTimeout(() => {
            wx.hideLoading()
            wx.showModal({
              title: '电柜交互',
              content: '请将空电池放入 3号仓，并关好仓门',
              confirmText: '已放入',
              showCancel: false,
              success: (res) => {
                if (res.confirm) {
                  wx.showLoading({ title: '检测电池中...' })
                  setTimeout(() => {
                    wx.hideLoading()
                    wx.showModal({
                      title: '仓门已弹开',
                      content: '请从 8号仓 取出满电电池',
                      confirmText: '已取出',
                      showCancel: false,
                      success: (res2) => {
                        if (res2.confirm) {
                          this.doExchange()
                        }
                      }
                    })
                  }, 1500)
                }
              }
            })
          }, 1000)
        }
      }
    })
  },

  doExchange() {
    const { currentBattery, selectedBattery, selectedStation, canExchange } = this.data
    if (!canExchange || !currentBattery) {
      wx.showToast({ title: '当前没有可换的在租电池', icon: 'none' })
      return
    }
    this.setData({ confirming: true, exchangeError: '' })

    wx.showLoading({ title: '换电中...' })

    exchangeBattery({
      old_battery_id: currentBattery.id,
      new_battery_id: selectedBattery.id,
      station_id: selectedStation.id,
      cabinet_id: selectedBattery.current_cabinet_id || 1,
      latitude: this.data.latitude,
      longitude: this.data.longitude
    })
      .then(res => {
        wx.hideLoading()
        const result = res.data || {}
        const nextBatteryCode = (result.new_battery && result.new_battery.battery_code) || selectedBattery.battery_code
        wx.showModal({
          title: '换电成功',
          content: `已用 ${currentBattery.battery_code} 换取新电池 ${nextBatteryCode}，费用 ¥${(result.exchange_fee || 0).toFixed(2)}`,
          showCancel: false,
          success: () => {
            this.refreshAfterExchange(result)
          }
        })
      })
      .catch(err => {
        wx.hideLoading()
        const msg = (err && err.message) || '换电失败，请重试'
        wx.showModal({
          title: '换电失败',
          content: msg,
          showCancel: false
        })
        this.setData({ confirming: false, exchangeError: msg })
      })
  },

  goToRecommended() {
    const station = this.data.recommendedStation
    if (!station) return
    this.setData({
      selectedStation: station,
      step: 2,
      availableBatteries: [],
      selectedBattery: null
    })
    this.loadStationBatteries(station.id)
  }
})
