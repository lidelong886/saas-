// pages/fault/report.js
const { submitFaultReport } = require('../../api/fault')
const { getUserProfile } = require('../../api/user')

Page({
  data: {
    faultTypes: [
      { value: 'battery', label: '电池故障' },
      { value: 'cabinet', label: '柜机故障' },
      { value: 'station', label: '站点问题' },
      { value: 'other', label: '其他' }
    ],
    selectedType: '',
    description: '',
    images: [],
    stationId: null,
    stationName: '',
    contactPhone: '',
    submitting: false
  },

  onLoad(options) {
    if (options.station_id) {
      this.setData({
        stationId: parseInt(options.station_id),
        stationName: options.station_name || ''
      })
    }
    this.loadUserPhone()
  },

  loadUserPhone() {
    getUserProfile().then(res => {
      const phone = (res.data || {}).phone || ''
      if (phone) {
        this.setData({ contactPhone: phone })
      }
    }).catch(() => {})
  },

  onSelectType(e) {
    this.setData({ selectedType: e.currentTarget.dataset.type })
  },

  onDescInput(e) {
    this.setData({ description: e.detail.value })
  },

  onPhoneInput(e) {
    this.setData({ contactPhone: e.detail.value })
  },

  onChooseImage() {
    if (this.data.images.length >= 3) {
      wx.showToast({ title: '最多上传3张图片', icon: 'none' })
      return
    }
    wx.chooseMedia({
      count: 3 - this.data.images.length,
      mediaType: ['image'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        const newImages = res.tempFiles.map(f => f.tempFilePath)
        this.setData({
          images: [...this.data.images, ...newImages]
        })
      }
    })
  },

  onRemoveImage(e) {
    const idx = e.currentTarget.dataset.index
    const images = [...this.data.images]
    images.splice(idx, 1)
    this.setData({ images })
  },

  onSubmit() {
    const { selectedType, description, images, stationId, contactPhone } = this.data

    if (!selectedType) {
      wx.showToast({ title: '请选择故障类型', icon: 'none' })
      return
    }
    if (!description || description.trim().length < 10) {
      wx.showToast({ title: '故障描述至少10个字', icon: 'none' })
      return
    }

    this.setData({ submitting: true })

    submitFaultReport({
      fault_type: selectedType,
      description: description.trim(),
      images: images,
      station_id: stationId,
      contact_phone: contactPhone
    }).then(res => {
      const reportNo = (res.data || {}).report_no || ''
      wx.showModal({
        title: '报修提交成功',
        content: `工单号：${reportNo}\n我们将尽快处理您的报修`,
        showCancel: false,
        success: () => {
          wx.navigateBack()
        }
      })
    }).catch(err => {
      wx.showToast({ title: '提交失败，请重试', icon: 'none' })
    }).finally(() => {
      this.setData({ submitting: false })
    })
  }
})
