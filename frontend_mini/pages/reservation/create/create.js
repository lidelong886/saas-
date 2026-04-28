const { createReservation } = require('../../../api/reservation')
const { getStationDetail, getStationBatteries } = require('../../../api/station')

Page({
  data: {
    stationId: null,
    station: {},
    batteries: [],
    selectedBatteryId: null,
    selectedDuration: 30, // 默认30分钟
    durations: [
      { value: 15, label: '15分钟', desc: '适合就在附近' },
      { value: 30, label: '30分钟', desc: '推荐' },
      { value: 45, label: '45分钟', desc: '路程较远' }
    ],
    cancelCount: 3, // 本月剩余免费取消次数
    reserveUntil: '',
    canConfirm: false
  },

  onLoad(options) {
    if (options.stationId) {
      this.setData({ stationId: options.stationId });
      this.loadStationData();
      this.loadBatteries();
    } else {
      wx.showToast({
        title: '站点信息缺失',
        icon: 'error'
      });
      setTimeout(() => {
        wx.navigateBack();
      }, 1500);
    }
  },

  async loadStationData() {
    try {
      wx.showLoading({ title: '加载中...' });
      const res = await getStationDetail(this.data.stationId);

      if (res.code === 200) {
        this.setData({
          station: res.data,
          cancelCount: res.data.user_cancel_count || 3
        });
        this.updateReserveUntil();
      }
    } catch (error) {
      console.error('加载站点信息失败:', error);
      wx.showToast({
        title: '加载失败',
        icon: 'error'
      });
    } finally {
      wx.hideLoading();
    }
  },

  async loadBatteries() {
    try {
      const res = await getStationBatteries(this.data.stationId);

      if (res.code === 200) {
        // 只显示可用的电池（电量>20%，健康度>70%）
        const availableBatteries = res.data.filter(b =>
          b.status === 'available' && b.charge > 20 && b.health > 70
        );

        this.setData({ batteries: availableBatteries });
      }
    } catch (error) {
      console.error('加载电池列表失败:', error);
    }
  },

  selectBattery(e) {
    const batteryId = e.currentTarget.dataset.id;
    this.setData({
      selectedBatteryId: batteryId,
      canConfirm: true
    });
  },

  selectDuration(e) {
    const duration = e.currentTarget.dataset.value;
    this.setData({ selectedDuration: duration });
    this.updateReserveUntil();
  },

  updateReserveUntil() {
    const now = new Date();
    const reserveTime = new Date(now.getTime() + this.data.selectedDuration * 60 * 1000);
    const hours = String(reserveTime.getHours()).padStart(2, '0');
    const minutes = String(reserveTime.getMinutes()).padStart(2, '0');

    this.setData({
      reserveUntil: `${hours}:${minutes}`
    });
  },

  async confirmReservation() {
    if (!this.data.canConfirm) return;

    try {
      wx.showLoading({ title: '预约中...' });

      const res = await createReservation({
        station_id: this.data.stationId,
        battery_id: this.data.selectedBatteryId,
        duration_minutes: this.data.selectedDuration
      });

      wx.hideLoading();

      if (res.code === 200) {
        wx.showToast({
          title: '预约成功',
          icon: 'success'
        });

        // 跳转到预约详情页
        setTimeout(() => {
          wx.redirectTo({
            url: `/pages/reservation/detail/detail?id=${res.data.id}`
          });
        }, 1500);
      } else {
        wx.showModal({
          title: '预约失败',
          content: res.message || '请稍后重试',
          showCancel: false
        });
      }
    } catch (error) {
      wx.hideLoading();
      console.error('预约失败:', error);

      wx.showModal({
        title: '预约失败',
        content: error.message || '网络错误，请稍后重试',
        showCancel: false
      });
    }
  }
});
