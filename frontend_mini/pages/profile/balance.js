const { getUserBalance, recharge, getWalletTransactions } = require('../../api/user')

Page({
  data: {
    balance: 0,
    points: 0,
    balanceText: '0.00',
    records: [],
    weekExpense: '0.00',
    weekIncome: '0.00',
    amountPick: 100,
    customAmount: '',
    loading: false
  },

  onShow() {
    if (!wx.getStorageSync('token')) {
      wx.showModal({
        title: '提示',
        content: '请先登录后查看余额',
        confirmText: '去登录',
        success: (r) => {
          if (r.confirm) wx.navigateTo({ url: '/pages/profile/login' })
          else wx.navigateBack()
        }
      })
      return
    }
    this.refresh()
  },

  refresh() {
    getUserBalance()
      .then((res) => {
        const d = res.data || {}
        const b = Number(d.balance) || 0
        this.setData({
          balance: b,
          points: d.points || 0,
          balanceText: b.toFixed(2)
        })
      })
      .catch(() => {
        wx.showToast({ title: '加载余额失败', icon: 'none' })
      })

    getWalletTransactions({ page: 1, per_page: 100 })
      .then((res) => {
        const inner = res.data || {}
        const list = inner.list || inner.items || []

        // 计算本周收支
        const weekStart = new Date()
        weekStart.setDate(weekStart.getDate() - weekStart.getDay())
        weekStart.setHours(0, 0, 0, 0)

        let weekExpense = 0
        let weekIncome = 0

        list.forEach(record => {
          const recordDate = new Date(record.created_at)
          if (recordDate >= weekStart) {
            if (record.direction === 'expense') {
              weekExpense += parseFloat(record.amount) || 0
            } else if (record.direction === 'income') {
              weekIncome += parseFloat(record.amount) || 0
            }
          }
        })

        this.setData({
          weekExpense: weekExpense.toFixed(2),
          weekIncome: weekIncome.toFixed(2),
          records: list.slice(0, 10).map(item => this.normalizeRecord(item))
        })
      })
      .catch(() => {
        wx.showToast({ title: '加载明细失败', icon: 'none' })
        this.setData({ records: [] })
      })
  },

  normalizeRecord(item) {
    const direction = item.direction === 'expense' ? '-' : '+'
    const typeMap = {
      recharge: '余额充值',
      pay: '余额支付',
      refund: '退款返还',
      adjustment: '余额调整'
    }

    return {
      ...item,
      displayTitle: typeMap[item.transaction_type] || '钱包变动',
      displayAmount: `${direction}¥${Number(item.amount || 0).toFixed(2)}`,
      displayTime: item.created_at || '',
      displayRemark: item.remarks || ''
    }
  },

  pickAmount(e) {
    const v = Number(e.currentTarget.dataset.v)
    this.setData({ amountPick: v, customAmount: '' })
  },

  onCustomInput(e) {
    this.setData({ customAmount: e.detail.value, amountPick: 0 })
  },

  onRecharge() {
    let amt = this.data.amountPick
    if (this.data.customAmount) {
      amt = parseFloat(this.data.customAmount)
    }
    if (!amt || amt <= 0) {
      wx.showToast({ title: '请输入有效金额', icon: 'none' })
      return
    }

    this.setData({ loading: true })
    recharge({ amount: amt })
      .then((res) => {
        const d = res.data || {}
        const b = Number(d.balance) || 0
        this.setData({
          balance: b,
          points: d.points || 0,
          balanceText: b.toFixed(2),
          loading: false
        })
        wx.showToast({ title: '充值成功', icon: 'success' })
        this.refresh()
      })
      .catch(() => {
        this.setData({ loading: false })
        wx.showToast({ title: '充值失败，请重试', icon: 'none' })
      })
  }
})
