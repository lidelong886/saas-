// pages/station/detail.js
const { getStationDetail, getStationBatteries } = require('../../api/station')

Page({
  data: {
    stationId: null,
    station: null,
    batteries: [],
    isLoading: false
  },

  onLoad: function(options) {
    const rawId = options.id
    if (!rawId) return
    const stationId = parseInt(rawId, 10)
    if (Number.isNaN(stationId)) return
    this.setData({ stationId })
    this.loadStationDetail()
    this.loadStationBatteries()
  },

  // 加载站点详情
  loadStationDetail: function() {
    wx.showLoading({ title: '加载中...' })

    getStationDetail(this.data.stationId).then(res => {
      wx.hideLoading()
      this.setData({
        station: res.data
      })
    }).catch(err => {
      wx.hideLoading()
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      })
    })
  },

  // 加载站点电池
  loadStationBatteries: function() {
    // 不传 status，展示本站点下全部电池（含充电中等），避免筛选过严导致空白
    getStationBatteries(this.data.stationId, {
      per_page: 30,
      page: 1
    }).then(res => {
      const inner = res.data || {}
      const list = inner.list || inner.items || []
      // 将英文状态转换为中文
      const processedList = list.map(battery => ({
        ...battery,
        status_cn: this.getStatusChinese(battery.status)
      }))
      this.setData({
        batteries: processedList
      })
    }).catch((err) => {
      const msg = (err && (err.message || err.msg)) || '加载电池失败'
      wx.showToast({ title: msg, icon: 'none' })
      console.error('加载电池失败:', err)
    })
  },

  // 电池状态英文转中文
  getStatusChinese: function(status) {
    const statusMap = {
      'available': '可用',
      'rented': '租用中',
      'charging': '充电中',
      'maintenance': '维护中',
      'scrapped': '已报废'
    }
    return statusMap[status] || status
  },

  onOpenBatteryList: function() {
    const id = this.data.stationId
    if (!id) return
    wx.navigateTo({
      url: `/pages/battery/list?station_id=${id}`
    })
  },

  onBatteryTap: function(e) {
    const bid = e.currentTarget.dataset.id
    if (!bid) return
    wx.navigateTo({
      url: `/pages/battery/detail?id=${bid}`
    })
  },

  onNavigate: function() {
    const station = this.data.station
    if (!station) return
    const lat = Number(station.latitude)
    const lng = Number(station.longitude)
    if (!Number.isFinite(lat) || !Number.isFinite(lng)) {
      wx.showToast({ title: '站点坐标无效，无法导航', icon: 'none' })
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

  onFaultReport: function() {
    const station = this.data.station
    if (!station) return
    wx.navigateTo({
      url: `/pages/fault/report?station_id=${station.id}&station_name=${encodeURIComponent(station.name)}`
    })
  },

  // 下拉刷新
  onPullDownRefresh: function() {
    this.loadStationDetail()
    this.loadStationBatteries()
    wx.stopPullDownRefresh()
  }
})
