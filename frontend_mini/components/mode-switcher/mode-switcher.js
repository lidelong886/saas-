// components/mode-switcher/mode-switcher.js
const { updateUserPreferences } = require('../../api/rider')

Component({
  properties: {
    mode: {
      type: String,
      value: 'normal'
    }
  },

  data: {
    currentMode: 'normal'
  },

  lifetimes: {
    attached() {
      this.setData({
        currentMode: this.properties.mode
      })
    }
  },

  observers: {
    'mode': function(newMode) {
      this.setData({
        currentMode: newMode
      })
    }
  },

  methods: {
    onSwitchMode(e) {
      const mode = e.currentTarget.dataset.mode
      if (mode === this.data.currentMode) return

      this.setData({ currentMode: mode })

      // 保存到本地存储
      wx.setStorageSync('user_mode', mode)

      // 保存到后端（静默失败）
      const token = wx.getStorageSync('token')
      if (token) {
        updateUserPreferences({ mode }).catch(err => {
          console.error('保存用户偏好失败:', err)
        })
      }

      // 触发父组件事件
      this.triggerEvent('change', { mode })

      // 提示用户
      wx.showToast({
        title: mode === 'delivery' ? '已切换到送单模式' : '已切换到普通模式',
        icon: 'none',
        duration: 1500
      })
    }
  }
})
