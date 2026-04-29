const { getBatteries } = require('../../api/battery')
const { getStations } = require('../../api/station')
const request = require('../../utils/request')

Page({
  data: {
    activeTab: 'rented', // 'rented' | 'owned'
    rentedBatteries: [],
    ownedBatteries: [],
    loading: false
  },

  onLoad(options) {
    if (!wx.getStorageSync('token')) {
      wx.showModal({
        title: '提示',
        content: '登录后可查看我的电池',
        confirmText: '去登录',
        success: (r) => {
          if (r.confirm) wx.navigateTo({ url: '/pages/profile/login' })
        }
      })
    }
  },

  onShow() {
    if (wx.getStorageSync('token')) {
      this.load()
    }
  },

  switchTab(e) {
    const tab = e.currentTarget.dataset.tab
    if (this.data.activeTab === tab) return
    this.setData({ activeTab: tab })
    this.load()
  },

  load() {
    this.setData({ loading: true })
    
    if (this.data.activeTab === 'rented') {
      // 这里的逻辑如果后端没有专门的 /my 接口，可以从用户在租信息获取，或者筛选当前用户的电池
      request.get('/user/stats').then(res => {
        const stats = res.data || {}
        this.setData({ 
          rentedBatteries: stats.rentedBattery ? [stats.rentedBattery] : [],
          loading: false 
        })
      }).catch(() => {
        this.setData({ loading: false })
      })
    } else {
      // 请求新的专属电池接口
      request.get('/battery/my').then(res => {
        const list = res.data || []
        this.setData({ ownedBatteries: list, loading: false })
      }).catch(() => {
        this.setData({ ownedBatteries: [], loading: false })
      })
    }
  },

  goToReturn() {
    // 快速归还电池
    wx.showModal({
      title: '快速归还电池',
      content: '确认要归还当前租用的电池吗？\n系统将自动结算租金并退还押金。',
      confirmText: '确认归还',
      cancelText: '取消',
      success: (res) => {
        if (res.confirm) {
          this.quickReturn()
        }
      }
    })
  },

  quickReturn() {
    const battery = this.data.rentedBatteries[0]
    if (!battery) {
      wx.showToast({ title: '没有在租电池', icon: 'none' })
      return
    }

    wx.showLoading({ title: '归还中...' })

    // 调用归还接口，默认归还到1号站点1号柜
    request.post(`/battery/${battery.id}/return`, {
      station_id: 1,
      cabinet_id: 1,
      latitude: 38.0428,
      longitude: 114.5149
    }).then(res => {
      wx.hideLoading()
      wx.showModal({
        title: '归还成功',
        content: '电池已归还，押金已退回余额',
        showCancel: false,
        success: () => {
          this.load()
        }
      })
    }).catch(err => {
      wx.hideLoading()
      const msg = err && err.message || '归还失败'
      wx.showToast({ title: msg, icon: 'none' })
    })
  },

  goToBuyBattery() {
    wx.navigateTo({ url: '/pages/store/list' })
  },

  onChargeTap(e) {
    const battery = e.currentTarget.dataset.battery
    if (!battery || !battery.id) return
    wx.showLoading({ title: '加载站点...' })
    getStations({ limit: 20 }).then(res => {
      wx.hideLoading()
      const data = res.data || {}
      const stations = data.stations || []
      const usableStations = stations.filter(item => item.status === 'active')
      if (!usableStations.length) {
        wx.showToast({ title: '暂无可用公共充电桩', icon: 'none' })
        return
      }
      wx.showActionSheet({
        itemList: usableStations.slice(0, 6).map(item => item.name),
        success: action => {
          const station = usableStations[action.tapIndex]
          this.startPublicCharge(battery.id, station.id)
        }
      })
    }).catch(() => {
      wx.hideLoading()
      wx.showToast({ title: '站点加载失败', icon: 'none' })
    })
  },

  startPublicCharge(batteryId, stationId) {
    wx.showLoading({ title: '提交充电...' })
    request.post(`/battery/my/${batteryId}/charge`, { station_id: stationId }).then(() => {
      wx.hideLoading()
      wx.showToast({ title: '已开始充电', icon: 'success' })
      this.load()
    }).catch(err => {
      wx.hideLoading()
      const msg = err && (err.message || err.msg) || '充电失败'
      wx.showToast({ title: msg, icon: 'none' })
    })
  },

  onTap(e) {
    const id = e.currentTarget.dataset.id
    if (!id) return
    wx.navigateTo({
      url: `/pages/battery/detail?id=${id}`
    })
  }
})
