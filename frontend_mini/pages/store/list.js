// pages/store/list.js
const { getStoreBatteries, purchaseBatteryCategory } = require('../../api/store')

function toNumber(value, fallback = 0) {
  const number = Number(value)
  return Number.isFinite(number) ? number : fallback
}

function formatMoney(value) {
  const number = toNumber(value, 0)
  return number.toFixed(2).replace(/\.00$/, '')
}

function inferVoltage(item) {
  if (item.voltage_type) return item.voltage_type
  const model = item.model || ''
  const match = model.match(/(48|60|72)V/i)
  return match ? `${match[1]}V` : '60V'
}

function normalizeBattery(item, index) {
  const capacity = toNumber(item.capacity, 0)
  const powerLevel = Math.max(0, Math.min(100, toNumber(item.power_level, 0)))
  const price = item.selling_price || item.deposit_amount || 0
  const voltage = inferVoltage(item)
  const stock = toNumber(item.stock, 0)
  const sellingPoint = stock > 8 ? '热销现货' : stock > 0 ? '少量现货' : '暂时售罄'

  return {
    ...item,
    id: item.category_id || item.id || `${voltage}-${capacity}`,
    categoryId: item.category_id || item.id || `${voltage}-${capacity}`,
    voltageType: voltage,
    priceValue: toNumber(price, 0),
    displayPrice: formatMoney(price),
    depositDisplay: formatMoney(item.deposit_amount || 0),
    capacityDisplay: item.capacity_label || (capacity >= 1000 ? `${Math.round(capacity / 1000)}Ah` : `${capacity}mAh`),
    powerLevel,
    stock,
    avgPowerLevel: toNumber(item.avg_power_level, powerLevel),
    modelName: item.model || `${voltage} ${capacity >= 1000 ? Math.round(capacity / 1000) + 'Ah' : capacity + 'mAh'} 智能锂电池`,
    batteryCode: `${voltage}-${capacity >= 1000 ? Math.round(capacity / 1000) + 'Ah' : capacity + 'mAh'}`,
    stationName: '购买后系统自动分配同规格电池',
    sellingPoint,
    warrantyText: '24个月质保',
    serviceText: '公共充电桩低价充电',
    isFeatured: index === 0
  }
}

Page({
  data: {
    batteries: [],
    filteredBatteries: [],
    page: 1,
    hasMore: true,
    isLoading: false,
    keyword: '',
    activeVoltage: 'all',
    activePrice: 'all',
    sortMode: 'recommend',
    voltageTabs: [
      { key: 'all', label: '全部' },
      { key: '60V', label: '60V' },
      { key: '72V', label: '72V' }
    ],
    priceTabs: [
      { key: 'all', label: '全部' },
      { key: '0-1000', label: '1000以下', min: 0, max: 1000 },
      { key: '1000-2000', label: '1000-2000', min: 1000, max: 2000 },
      { key: '2000+', label: '2000以上', min: 2000 }
    ],
    sortTabs: [
      { key: 'recommend', label: '推荐' },
      { key: 'priceAsc', label: '价格升序' },
      { key: 'priceDesc', label: '价格降序' },
      { key: 'powerDesc', label: '交付电量' }
    ]
  },

  onLoad() {
    wx.setNavigationBarTitle({ title: '电池商城' })
    this.loadBatteries(true)
  },

  normalizeList(list) {
    return (list || []).map((item, index) => normalizeBattery(item, index))
  },

  getListFromResponse(res) {
    const data = res.data || {}
    if (Array.isArray(data)) return data
    return data.list || data.items || data.records || []
  },

  getHasMore(res, list) {
    const data = res.data || {}
    const pagination = data.pagination || data
    if (pagination.pages && pagination.page) return pagination.page < pagination.pages
    if (typeof pagination.total === 'number' && pagination.per_page) {
      return this.data.page * pagination.per_page < pagination.total
    }
    return list.length >= 20
  },

  getActivePriceRange() {
    const priceTabs = Array.isArray(this.data.priceTabs) ? this.data.priceTabs : []
    return priceTabs.find(item => item.key === this.data.activePrice) || priceTabs[0] || { key: 'all' }
  },

  buildStoreParams(page) {
    const range = this.getActivePriceRange()
    const params = { page, per_page: 20, sort: this.data.sortMode }
    if (this.data.activeVoltage !== 'all') params.voltage_type = this.data.activeVoltage
    if (range.min != null) params.price_min = range.min
    if (range.max != null) params.price_max = range.max
    return params
  },

  loadBatteries(refresh = false) {
    if (this.data.isLoading) return
    if (!refresh && !this.data.hasMore) return

    const page = refresh ? 1 : this.data.page
    this.setData({ isLoading: true })
    if (refresh) wx.showLoading({ title: '加载商城...' })

    getStoreBatteries(this.buildStoreParams(page)).then(res => {
      const list = this.normalizeList(this.getListFromResponse(res))
      const batteries = refresh ? list : this.data.batteries.concat(list)
      this.setData({
        batteries,
        page: page + 1,
        hasMore: this.getHasMore(res, list),
        isLoading: false
      })
      this.applyFilters()
    }).catch(() => {
      this.setData({ isLoading: false })
      wx.showToast({ title: '商城加载失败', icon: 'none' })
    }).finally(() => {
      wx.hideLoading()
      wx.stopPullDownRefresh()
    })
  },

  applyFilters() {
    const keyword = (this.data.keyword || '').trim().toLowerCase()
    const range = this.getActivePriceRange()
    let list = this.data.batteries.filter(item => {
      const matchVoltage = this.data.activeVoltage === 'all' || item.voltageType === this.data.activeVoltage
      const matchPriceMin = range.min == null || item.priceValue >= range.min
      const matchPriceMax = range.max == null || item.priceValue < range.max
      const text = `${item.modelName} ${item.voltageType} ${item.capacityDisplay}`.toLowerCase()
      return matchVoltage && matchPriceMin && matchPriceMax && (!keyword || text.includes(keyword))
    })

    if (this.data.sortMode === 'priceAsc') {
      list = list.slice().sort((a, b) => a.priceValue - b.priceValue)
    } else if (this.data.sortMode === 'priceDesc') {
      list = list.slice().sort((a, b) => b.priceValue - a.priceValue)
    } else if (this.data.sortMode === 'powerDesc') {
      list = list.slice().sort((a, b) => b.powerLevel - a.powerLevel)
    }

    this.setData({ filteredBatteries: list })
  },

  onSearchInput(e) {
    this.setData({ keyword: e.detail.value || '' })
    this.applyFilters()
  },

  clearSearch() {
    this.setData({ keyword: '' })
    this.applyFilters()
  },

  switchVoltage(e) {
    this.setData({ activeVoltage: e.currentTarget.dataset.key, page: 1, hasMore: true, batteries: [] })
    this.loadBatteries(true)
  },

  switchPrice(e) {
    this.setData({ activePrice: e.currentTarget.dataset.key, page: 1, hasMore: true, batteries: [] })
    this.loadBatteries(true)
  },

  switchSort(e) {
    this.setData({ sortMode: e.currentTarget.dataset.key, page: 1, hasMore: true, batteries: [] })
    this.loadBatteries(true)
  },

  onBatteryTap(e) {
    const battery = e.currentTarget.dataset.battery
    wx.setStorageSync('storeBatteryDetail', battery)
    wx.navigateTo({ url: `/pages/store/detail?id=${battery.categoryId}` })
  },

  onPurchaseTap(e) {
    const battery = e.currentTarget.dataset.battery
    if (!wx.getStorageSync('token')) {
      wx.showModal({
        title: '登录后购买',
        content: '购买专属电池需要先登录账号。',
        confirmText: '去登录',
        success: res => {
          if (res.confirm) wx.navigateTo({ url: '/pages/profile/login' })
        }
      })
      return
    }

    wx.showModal({
      title: '确认购买',
      content: `${battery.modelName}\n${battery.capacityDisplay} · ${battery.voltageType} · 库存 ${battery.stock} 件\n应付 ¥${battery.displayPrice}`,
      confirmText: '立即购买',
      success: res => {
        if (res.confirm) this.purchaseBattery(battery)
      }
    })
  },

  purchaseBattery(battery) {
    wx.showLoading({ title: '提交订单...' })
    purchaseBatteryCategory({
      voltage_type: battery.voltageType,
      capacity: battery.capacity
    }).then(() => {
      wx.hideLoading()
      wx.showToast({ title: '购买成功', icon: 'success' })
      setTimeout(() => this.loadBatteries(true), 900)
    }).catch(err => {
      wx.hideLoading()
      const msg = (err && (err.message || err.msg)) || '购买失败'
      wx.showToast({ title: msg, icon: 'none' })
    })
  },

  onReachBottom() {
    this.loadBatteries(false)
  },

  onPullDownRefresh() {
    this.loadBatteries(true)
  }
})
