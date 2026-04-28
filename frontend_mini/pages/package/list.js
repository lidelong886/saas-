const { getPackages } = require('../../api/package')
const { getPackageRecommendations } = require('../../api/recommend')

Page({
  data: {
    packages: [],
    recommendedPackages: [],
    isLoading: false,
    hasMore: true,
    page: 1,
    pageSize: 20
  },

  onShow() {
    this.loadPackages(true)
    this.loadRecommendations()
  },

  loadRecommendations() {
    // 只有登录用户才加载推荐（或者根据后端逻辑也支持未登录热门推荐）
    if (wx.getStorageSync('token')) {
      getPackageRecommendations(5).then(res => {
        const list = res.data && res.data.packages ? res.data.packages : []
        const newPackages = list.map(item => this.normalizePackage(item))
        this.setData({
          recommendedPackages: newPackages
        })
      }).catch(err => {
        console.error('加载推荐套餐失败:', err)
      })
    } else {
      // 未登录可以清空，或者调用热门推荐
      this.setData({ recommendedPackages: [] })
    }
  },

  loadPackages(isRefresh = false) {
    if (this.data.isLoading) return

    const nextPage = isRefresh ? 1 : this.data.page
    if (!isRefresh && !this.data.hasMore) return

    if (isRefresh) {
      this.setData({
        packages: [],
        page: 1,
        hasMore: true
      })
    }

    this.setData({ isLoading: true })

    getPackages({
      page: nextPage,
      per_page: this.data.pageSize,
      active_only: true
    }).then((res) => {
      const payload = res.data || {}
      const list = payload.list || payload.items || []
      const newPackages = list.map(item => this.normalizePackage(item))
      const packages = isRefresh ? newPackages : this.data.packages.concat(newPackages)

      this.setData({
        packages,
        page: nextPage + 1,
        hasMore: newPackages.length === this.data.pageSize,
        isLoading: false
      })
    }).catch((err) => {
      console.error('加载套餐失败:', err)
      this.setData({ isLoading: false })
    })
  },

  normalizePackage(item) {
    const packageType = item.package_type || 'rental'
    return {
      ...item,
      packageTypeText: this.formatType(packageType),
      priceText: this.formatMoney(item.price),
      depositText: this.formatMoney(item.deposit_amount),
      exchangeFeeText: this.formatMoney(item.exchange_fee),
      durationText: item.hours ? `${item.hours}小时` : '按套餐配置'
    }
  },

  formatType(type) {
    const map = {
      rental: '租用套餐',
      purchase: '购买套餐',
      exchange: '换电套餐'
    }
    return map[type] || type
  },

  formatMoney(value) {
    return `¥${Number(value || 0).toFixed(2)}`
  },

  onBuyTap(e) {
    const item = e.currentTarget.dataset.item
    if (!item || !item.id) return

    if (!wx.getStorageSync('token')) {
      wx.showModal({
        title: '提示',
        content: '请先登录后再购买',
        confirmText: '去登录',
        success: (res) => {
          if (res.confirm) wx.navigateTo({ url: '/pages/profile/login' })
        }
      })
      return
    }

    wx.showLoading({ title: '创建订单中...' })
    const { createOrder } = require('../../api/order')
    createOrder({
      order_type: 'purchase',
      package_id: item.id,
      hours: item.hours || 24
    }).then(res => {
      wx.hideLoading()
      const order = res.data
      const no = order && order.order_no
      if (no) {
        wx.navigateTo({
          url: `/pages/order/detail?order_no=${no}`
        })
      }
    }).catch(err => {
      wx.hideLoading()
      const msg = err && err.message
      wx.showToast({ title: msg || '下单失败', icon: 'none' })
    })
  },

  onPullDownRefresh() {
    this.loadPackages(true)
    this.loadRecommendations()
    wx.stopPullDownRefresh()
  },

  onReachBottom() {
    if (this.data.hasMore && !this.data.isLoading) {
      this.loadPackages()
    }
  },

  goToIndex() {
    wx.switchTab({ url: '/pages/index/index' })
  },

  onRiderPackageTap() {
    wx.navigateTo({
      url: '/pages/package/rider/rider'
    })
  }
})
