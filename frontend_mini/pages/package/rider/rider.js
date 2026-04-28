const { getRiderPackages } = require('../../../api/package')

Page({
  data: {
    packages: [],
    isLoading: true
  },

  onLoad() {
    // 检查登录状态
    const token = wx.getStorageSync('token')
    if (!token) {
      this.setData({ isLoading: false })
      wx.showModal({
        title: '需要登录',
        content: '请先登录后再查看骑手套餐',
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
      return
    }
    this.loadPackages()
  },

  onPullDownRefresh() {
    this.loadPackages().then(() => {
      wx.stopPullDownRefresh()
    })
  },

  async loadPackages() {
    try {
      this.setData({ isLoading: true })
      const res = await getRiderPackages()

      if (res.code === 200 && res.data) {
        const packages = res.data.map(item => ({
          ...item,
          recommended: item.duration_days === 90
        }))

        this.setData({ packages })
      }
    } catch (error) {
      console.error('加载骑手套餐失败:', error)
    } finally {
      this.setData({ isLoading: false })
    }
  },

  onBuyPackage(e) {
    const item = e.currentTarget.dataset.item

    const token = wx.getStorageSync('token')
    if (!token) {
      wx.showModal({
        title: '提示',
        content: '请先登录',
        success: (res) => {
          if (res.confirm) {
            wx.navigateTo({
              url: '/pages/profile/login'
            })
          }
        }
      })
      return
    }

    wx.showModal({
      title: '确认购买',
      content: `确认购买${item.name}（¥${item.price}）？`,
      success: (res) => {
        if (res.confirm) {
          this.processPurchase(item)
        }
      }
    })
  },

  async processPurchase(item) {
    wx.showLoading({ title: '处理中...' })

    try {
      wx.navigateTo({
        url: `/pages/package/detail?id=${item.id}`
      })
    } catch (error) {
      console.error('购买失败:', error)
      wx.showToast({
        title: '购买失败',
        icon: 'none'
      })
    } finally {
      wx.hideLoading()
    }
  }
})
