// API请求封装
const { formatRequestFail, formatHttpError } = require('./networkError')

class Request {
  constructor() {
    this.timeout = 45000
  }

  getBaseURL() {
    try {
      const app = getApp()
      if (app && app.globalData && app.globalData.baseUrl) {
        return app.globalData.baseUrl
      }
    } catch (e) {}
    return ''
  }

  getToken() {
    return wx.getStorageSync('token')
  }

  setToken(token) {
    wx.setStorageSync('token', token)
  }

  clearToken() {
    wx.removeStorageSync('token')
  }

  getHeaders(options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers
    }

    const token = this.getToken()
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    const app = getApp()
    const tenantId = app && app.globalData && app.globalData.tenantId
    if (tenantId != null) {
      headers['X-Tenant-ID'] = String(tenantId)
    }

    return headers
  }

  request(options) {
    return new Promise((resolve, reject) => {
      const base = this.getBaseURL()
      const path = options.url || ''
      if (!path.startsWith('http') && (!base || !/^https?:\/\//i.test(base))) {
        const tip = '未配置 apiBase，请编辑 frontend_mini/config.js'
        wx.showModal({ title: '配置错误', content: tip, showCancel: false })
        reject(new Error(tip))
        return
      }

      const url = (path.startsWith('http') ? '' : base) + path

      wx.request({
        url,
        method: options.method || 'GET',
        data: options.data || {},
        header: this.getHeaders(options),
        timeout: options.timeout || this.timeout,
        success: (res) => {
          this.handleResponse(res, resolve, reject, options)
        },
        fail: (err) => {
          this.handleError(err, reject, options)
        }
      })
    })
  }

  handleResponse(res, resolve, reject, options) {
    const { statusCode, data } = res
    const silent = options && options.silent

    if (statusCode === 200) {
      if (data && data.code === 200) {
        resolve(data)
      } else if (data && data.code === 401) {
        this.clearToken()
        wx.removeStorageSync('userInfo')
        wx.navigateTo({
          url: '/pages/profile/login'
        })
        reject(data)
      } else {
        const msg = (data && data.message) || '请求失败'
        if (!silent) {
          wx.showToast({ title: msg.length > 20 ? msg.slice(0, 20) + '…' : msg, icon: 'none', duration: 2800 })
        }
        reject(data || {})
      }
    } else if (statusCode === 401) {
      this.clearToken()
      wx.removeStorageSync('userInfo')
      wx.navigateTo({
        url: '/pages/profile/login'
      })
      reject(res)
    } else {
      const { toast, modal } = formatHttpError(statusCode, data)
      if (!silent) {
        wx.showToast({ title: toast, icon: 'none', duration: 2600 })
        if (modal) {
          setTimeout(() => {
            wx.showModal({
              title: modal.title,
              content: modal.content,
              showCancel: false,
              confirmText: '知道了'
            })
          }, 320)
        }
      }
      reject(res)
    }
  }

  handleError(err, reject, options) {
    const silent = options && options.silent
    console.error('Request fail:', err)
    if (!silent) {
      const { toast, modal } = formatRequestFail(err)
      wx.showToast({ title: toast, icon: 'none', duration: 2800 })
      if (modal) {
        setTimeout(() => {
          wx.showModal({
            title: modal.title,
            content: modal.content,
            showCancel: false,
            confirmText: '知道了'
          })
        }, 350)
      }
    }
    reject(err)
  }

  get(url, data = {}, options = {}) {
    return this.request({
      url,
      method: 'GET',
      data,
      ...options
    })
  }

  post(url, data = {}, options = {}) {
    return this.request({
      url,
      method: 'POST',
      data,
      ...options
    })
  }

  put(url, data = {}, options = {}) {
    return this.request({
      url,
      method: 'PUT',
      data,
      ...options
    })
  }

  delete(url, data = {}, options = {}) {
    return this.request({
      url,
      method: 'DELETE',
      data,
      ...options
    })
  }

  upload(url, filePath, formData = {}, options = {}) {
    return new Promise((resolve, reject) => {
      const base = this.getBaseURL()
      const uploadUrl = (url.startsWith('http') ? '' : base) + url

      wx.uploadFile({
        url: uploadUrl,
        filePath,
        name: 'file',
        formData,
        header: this.getHeaders(options),
        success: (res) => {
          try {
            const data = JSON.parse(res.data)
            if (data.code === 200) {
              resolve(data)
            } else {
              wx.showToast({
                title: data.message || '上传失败',
                icon: 'none'
              })
              reject(data)
            }
          } catch (e) {
            reject(res)
          }
        },
        fail: (err) => {
          this.handleError(err, reject, options)
        }
      })
    })
  }
}

const request = new Request()

module.exports = request
