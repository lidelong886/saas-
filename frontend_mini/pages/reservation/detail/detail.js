const { getReservationDetail, cancelReservation } = require('../../../api/reservation')
const { formatTime } = require('../../../utils/util')

Page({
  data: {
    reservationId: null,
    reservation: {},
    countdownClass: ''
  },

  onLoad(options) {
    if (options.id) {
      this.setData({ reservationId: options.id });
      this.loadReservationDetail();
    } else {
      wx.showToast({
        title: '预约信息缺失',
        icon: 'error'
      });
      setTimeout(() => {
        wx.navigateBack();
      }, 1500);
    }
  },

  onShow() {
    // 每次显示页面时刷新数据
    if (this.data.reservationId) {
      this.loadReservationDetail();
    }
  },

  async loadReservationDetail() {
    try {
      wx.showLoading({ title: '加载中...' });
      const res = await getReservationDetail(this.data.reservationId);

      if (res.code === 200) {
        const reservation = res.data;

        // 格式化时间
        reservation.reserved_at_formatted = formatTime(new Date(reservation.reserved_at));
        reservation.expires_at_formatted = formatTime(new Date(reservation.expires_at));
        if (reservation.completed_at) {
          reservation.completed_at_formatted = formatTime(new Date(reservation.completed_at));
        }

        // 转换时间戳为毫秒
        reservation.expires_at = new Date(reservation.expires_at).getTime();

        this.setData({ reservation });
      }
    } catch (error) {
      console.error('加载预约详情失败:', error);
      wx.showToast({
        title: '加载失败',
        icon: 'error'
      });
    } finally {
      wx.hideLoading();
    }
  },

  navigateToStation() {
    const { station } = this.data.reservation;

    wx.openLocation({
      latitude: parseFloat(station.latitude),
      longitude: parseFloat(station.longitude),
      name: station.name,
      address: station.address,
      scale: 15
    });
  },

  onWarning(e) {
    const { remaining } = e.detail;
    const minutes = Math.floor(remaining / 60000);

    // 剩余5分钟时显示警告
    if (minutes === 5) {
      this.setData({ countdownClass: 'warning' });
      wx.showModal({
        title: '预约即将到期',
        content: '您的预约还有5分钟到期，请尽快前往换电站',
        showCancel: false
      });
    }

    // 剩余2分钟时显示危险提示
    if (minutes === 2) {
      this.setData({ countdownClass: 'danger' });
      wx.showModal({
        title: '预约即将到期',
        content: '您的预约还有2分钟到期！',
        showCancel: false
      });
    }
  },

  onTimeout() {
    wx.showModal({
      title: '预约已过期',
      content: '您的预约已超时，电池已释放',
      showCancel: false,
      success: () => {
        this.loadReservationDetail();
      }
    });
  },

  cancelReservation() {
    wx.showModal({
      title: '确认取消',
      content: '确定要取消这个预约吗？',
      confirmText: '确认取消',
      confirmColor: '#FF3B30',
      success: async (res) => {
        if (res.confirm) {
          try {
            wx.showLoading({ title: '取消中...' });
            const result = await cancelReservation(this.data.reservationId);

            wx.hideLoading();

            if (result.code === 200) {
              wx.showToast({
                title: '已取消预约',
                icon: 'success'
              });

              setTimeout(() => {
                this.loadReservationDetail();
              }, 1500);
            } else {
              wx.showModal({
                title: '取消失败',
                content: result.message || '请稍后重试',
                showCancel: false
              });
            }
          } catch (error) {
            wx.hideLoading();
            console.error('取消预约失败:', error);
            wx.showModal({
              title: '取消失败',
              content: '网络错误，请稍后重试',
              showCancel: false
            });
          }
        }
      }
    });
  },

  completeReservation() {
    // 跳转到换电页面
    wx.redirectTo({
      url: `/pages/swap/swap?stationId=${this.data.reservation.station.id}&batteryId=${this.data.reservation.battery.id}&reservationId=${this.data.reservationId}`
    });
  }
});
