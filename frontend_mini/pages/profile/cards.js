const request = require('../../utils/request')

Page({
  data: {
    cards: [],
    activeTab: 'unused',
    loading: false
  },

  onLoad() {
    this.loadCards()
  },

  onShow() {
    this.loadCards()
  },

  switchTab(e) {
    const tab = e.currentTarget.dataset.tab
    if (this.data.activeTab === tab) return
    this.setData({ activeTab: tab, cards: [] })
    this.loadCards()
  },

  loadCards() {
    if (!wx.getStorageSync('token')) return
    this.setData({ loading: true })
    request.get('/user-package/list', { status: this.data.activeTab })
      .then(res => {
        const list = res.data || []
        const formattedList = list.map(item => ({
          ...item,
          statusText: this.formatStatus(item.status),
          activated_at: this.formatDate(item.activated_at),
          expires_at: this.formatDate(item.expires_at)
        }))
        this.setData({ cards: formattedList, loading: false })
      })
      .catch(err => {
        wx.showToast({ title: '加载失败', icon: 'none' })
        this.setData({ loading: false })
      })
  },

  formatStatus(status) {
    const map = {
      'unused': '待使用',
      'active': '使用中',
      'expired': '已过期',
      'exhausted': '已用完'
    }
    return map[status] || status
  },

  formatDate(dateStr) {
    if (!dateStr) return null
    return dateStr.replace('T', ' ').substring(0, 16)
  },

  onUseCard(e) {
    const { id, name } = e.currentTarget.dataset
    wx.showModal({
      title: '确认使用',
      content: `确定激活并使用【${name}】吗？激活后将开始计算时长权益。`,
      success: (res) => {
        if (res.confirm) {
          this.activateCard(id)
        }
      }
    })
  },

  activateCard(id) {
    wx.showLoading({ title: '激活中...' })
    request.post(`/user-package/${id}/activate`)
      .then(() => {
        wx.hideLoading()
        wx.showToast({ title: '激活成功', icon: 'success' })
        this.setData({ activeTab: 'active' })
        this.loadCards()
      })
      .catch(err => {
        wx.hideLoading()
        const msg = (err && err.message) || '激活失败'
        wx.showToast({ title: msg, icon: 'none' })
      })
  },

  goToPackages() {
    wx.switchTab({ url: '/pages/package/list' })
  }
})
