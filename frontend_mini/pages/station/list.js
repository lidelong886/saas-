// pages/station/list.js
const { getNearbyStations } = require('../../api/station')

Page({
  data: {
    stations: [], // 站点列表
    filteredStations: [], // 筛选后的站点列表
    isLoading: false,
    hasMore: true,
    page: 1,
    pageSize: 20,
    latitude: null,
    longitude: null,
    searchKeyword: '', // 搜索关键词
    sortBy: 'distance', // 排序方式: distance, available, name
    filterStatus: 'all', // 筛选状态: all, active, maintenance
    showFilters: false, // 是否显示筛选面板
    lastUpdatedAt: '' // 上次更新时间
  },

  onLoad: function(options) {
    // 获取当前位置
    this.getUserLocation()

    // 如果有搜索关键词
    if (options.keyword) {
      this.setData({
        searchKeyword: options.keyword
      })
    }
  },

  onShow: function() {
    // 已有坐标则刷新；首次进入且无坐标时由 onLoad 中的 getUserLocation 触发加载
    if (this.data.latitude && this.data.longitude) {
      this.loadStations(true)
    }
  },

  // 获取用户位置
  getUserLocation: function() {
    wx.getLocation({
      type: 'gcj02',
      success: (res) => {
        this.setData({
          latitude: res.latitude,
          longitude: res.longitude
        })
        this.loadStations(true)
      },
      fail: () => {
        // 使用默认位置
        this.setData({
          latitude: 39.9042,
          longitude: 116.4074
        })
        this.loadStations(true)
      }
    })
  },

  // 加载站点列表
  loadStations: function(isRefresh = false) {
    if (this.data.isLoading) return

    if (isRefresh) {
      this.setData({
        page: 1,
        hasMore: true,
        stations: []
      })
    }

    this.setData({ isLoading: true })

    const { latitude, longitude, page, pageSize } = this.data

    getNearbyStations({
      latitude,
      longitude,
      radius: 10,
      limit: 80
    }).then(res => {
      const payload = res.data || {}
      const newStations = payload.stations || []
      const stations = isRefresh ? newStations : [...this.data.stations, ...newStations]

      this.setData({
        stations,
        filteredStations: this.filterAndSortStations(stations),
        page: page + 1,
        hasMore: false,
        isLoading: false,
        lastUpdatedAt: this.formatUpdateTime()
      })
    }).catch(err => {
      console.error('加载站点失败:', err)
      wx.showToast({
        title: '加载站点失败',
        icon: 'none'
      })
      this.setData({ isLoading: false })
    })
  },

  // 筛选和排序站点
  filterAndSortStations: function(stations) {
    let filtered = [...stations]

    // 状态筛选
    if (this.data.filterStatus !== 'all') {
      filtered = filtered.filter(station => station.status === this.data.filterStatus)
    }

    // 关键词搜索
    if (this.data.searchKeyword) {
      const keyword = this.data.searchKeyword.toLowerCase()
      filtered = filtered.filter((station) => {
        const name = (station.name || '').toLowerCase()
        const addr = (station.address || '').toLowerCase()
        return name.includes(keyword) || addr.includes(keyword)
      })
    }

    // 排序
    filtered.sort((a, b) => {
      switch (this.data.sortBy) {
        case 'distance':
          return a.distance - b.distance
        case 'available':
          return b.available_batteries - a.available_batteries
        case 'name':
          return a.name.localeCompare(b.name)
        default:
          return 0
      }
    })

    return filtered
  },

  // 搜索输入
  onSearchInput: function(e) {
    const searchKeyword = e.detail.value
    this.setData({
      searchKeyword,
      filteredStations: this.filterAndSortStations(this.data.stations)
    })
  },

  // 清空搜索
  onClearSearch: function() {
    this.setData({
      searchKeyword: '',
      filteredStations: this.filterAndSortStations(this.data.stations)
    })
  },

  // 切换筛选面板
  toggleFilters: function() {
    this.setData({
      showFilters: !this.data.showFilters
    })
  },

  // 选择排序方式
  onSortChange: function(e) {
    const sortBy = e.currentTarget.dataset.sort
    this.setData({
      sortBy,
      filteredStations: this.filterAndSortStations(this.data.stations)
    })
  },

  // 选择筛选状态
  onFilterChange: function(e) {
    const filterStatus = e.currentTarget.dataset.filter
    this.setData({
      filterStatus,
      filteredStations: this.filterAndSortStations(this.data.stations)
    })
  },

  // 站点卡片点击
  onStationTap: function(e) {
    const stationId = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/station/detail?id=${stationId}`
    })
  },

  // 导航到站点
  onNavigateTap: function(e) {
    e.stopPropagation()
    const station = e.currentTarget.dataset.station

    wx.openLocation({
      latitude: Number(station.latitude),
      longitude: Number(station.longitude),
      name: station.name,
      address: station.address,
      scale: 18
    })
  },

  // 下拉刷新
  onPullDownRefresh: function() {
    this.loadStations(true)
    wx.stopPullDownRefresh()
  },

  // 触底加载更多
  onReachBottom: function() {
    if (this.data.hasMore && !this.data.isLoading) {
      this.loadStations()
    }
  },

  // 刷新数据
  onRefresh: function() {
    this.loadStations(true)
  },

  // 格式化更新时间
  formatUpdateTime: function() {
    const now = new Date()
    const h = now.getHours().toString().padStart(2, '0')
    const m = now.getMinutes().toString().padStart(2, '0')
    return `${h}:${m} 更新`
  }
})
